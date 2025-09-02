from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator
from typing import List, Optional
import os
import motor.motor_asyncio
import asyncio
from datetime import datetime, timedelta
import requests
import uuid
import aiofiles
from dotenv import load_dotenv
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from PIL import Image, ImageOps
import io
import tempfile
import subprocess
import mimetypes
from pathlib import Path
import time
import sys
import ftplib
import shutil

# Load environment variables
load_dotenv()

# === CONFIGURATION DIRECTORIES - CORRECTED FOR LINUX ===
UPLOAD_DIR = "/app/backend/uploads"
DOWNLOAD_DIR = os.path.join(UPLOAD_DIR, "downloaded")
OPTIMIZED_DIR = os.path.join(UPLOAD_DIR, "optimized")
PROCESSED_DIR = os.path.join(UPLOAD_DIR, "processed")
WORDPRESS_UPLOADS_DIR = "/app/backend/wordpress/uploads/"

# Ensure directories exist
def ensure_upload_directories():
    """Create required directories automatically"""
    directories = [UPLOAD_DIR, DOWNLOAD_DIR, OPTIMIZED_DIR, PROCESSED_DIR, WORDPRESS_UPLOADS_DIR]
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Directory created/verified: {directory}")
        except Exception as e:
            print(f"❌ Error creating directory {directory}: {e}")
            raise

# Create directories at startup
ensure_upload_directories()

# === FASTAPI APP INITIALIZATION ===
app = FastAPI(title="Meta Publishing Platform - Fixed")

# Configuration flags
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
FORCE_FTP = os.getenv("FORCE_FTP", "false").lower() == "true"

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log requests for debugging"""
    if request.url.path == "/api/webhook":
        method = request.method
        print(f"🌐 Webhook request: {method} {request.url}")
    
    response = await call_next(request)
    return response

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS requests for CORS"""
    return {"message": "OK"}

# === DATABASE SETUP ===
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.meta_posts

# === FACEBOOK/META CONFIGURATION ===
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
FACEBOOK_GRAPH_URL = os.getenv("FACEBOOK_GRAPH_URL", "https://graph.facebook.com/v18.0")

# === FTP CONFIGURATION ===
FTP_HOST = os.getenv("FTP_HOST", "logicamp.org")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER", "logi")
FTP_PASSWORD = os.getenv("FTP_PASSWORD", "logi")
FTP_DIRECTORY = os.getenv("FTP_DIRECTORY", "/wordpress/uploads/")
FTP_BASE_URL = os.getenv("FTP_BASE_URL", "https://logicamp.org/wordpress/uploads/")

# === PYDANTIC MODELS ===
class PostCreate(BaseModel):
    content: str
    media_urls: Optional[List[str]] = []
    platform: str = "facebook"  # facebook, instagram, both
    page_id: Optional[str] = None
    
    @validator('platform')
    def validate_platform(cls, v):
        if v not in ['facebook', 'instagram', 'both']:
            raise ValueError('Platform must be facebook, instagram, or both')
        return v

class PostResponse(BaseModel):
    id: str
    content: str
    media_urls: List[str]
    platform: str
    status: str
    created_at: datetime
    facebook_post_id: Optional[str] = None
    instagram_post_id: Optional[str] = None

# === UTILITY FUNCTIONS ===
def log_media(message: str, level: str = "INFO"):
    """Structured logging for media operations"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "CONVERSION": "🔄"}
    icon = icons.get(level.upper(), "📁")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [Media] {message}")

async def upload_to_ftp_simple(local_file_path: str, original_filename: str = None) -> tuple:
    """Simple FTP upload with date structure"""
    try:
        log_media(f"Starting FTP upload: {local_file_path}", "INFO")
        
        if not os.path.exists(local_file_path):
            return False, None, "Local file not found"
        
        # Create date structure (YYYY/MM/DD)
        now = datetime.now()
        date_path = f"{now.year:04d}/{now.month:02d}/{now.day:02d}"
        
        # Generate unique filename
        timestamp = int(now.timestamp())
        unique_id = uuid.uuid4().hex[:8]
        
        if original_filename:
            name, ext = os.path.splitext(original_filename)
            filename = f"{timestamp}_{unique_id}_{name[:30]}{ext}"
        else:
            _, ext = os.path.splitext(local_file_path)
            filename = f"media_{timestamp}_{unique_id}{ext}"
        
        # Clean filename for FTP
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Final URL
        https_url = f"{FTP_BASE_URL.rstrip('/')}/{date_path}/{filename}"
        
        if DRY_RUN:
            log_media("DRY_RUN: FTP upload simulated", "INFO")
            return True, https_url, None
        
        # FTP upload
        try:
            ftp = ftplib.FTP()
            ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
            ftp.login(FTP_USER, FTP_PASSWORD)
            
            # Navigate to directory and create date structure
            ftp.cwd(FTP_DIRECTORY)
            
            # Create year directory
            try:
                ftp.cwd(f"{now.year:04d}")
            except ftplib.error_perm:
                ftp.mkd(f"{now.year:04d}")
                ftp.cwd(f"{now.year:04d}")
            
            # Create month directory
            try:
                ftp.cwd(f"{now.month:02d}")
            except ftplib.error_perm:
                ftp.mkd(f"{now.month:02d}")
                ftp.cwd(f"{now.month:02d}")
            
            # Create day directory
            try:
                ftp.cwd(f"{now.day:02d}")
            except ftplib.error_perm:
                ftp.mkd(f"{now.day:02d}")
                ftp.cwd(f"{now.day:02d}")
            
            # Upload file
            with open(local_file_path, 'rb') as file:
                ftp.storbinary(f'STOR {filename}', file)
            
            ftp.quit()
            log_media(f"FTP upload successful: {https_url}", "SUCCESS")
            return True, https_url, None
            
        except Exception as ftp_error:
            log_media(f"FTP upload failed: {str(ftp_error)}", "ERROR")
            return False, None, str(ftp_error)
            
    except Exception as e:
        log_media(f"General FTP error: {str(e)}", "ERROR")
        return False, None, str(e)

async def convert_image_for_social(input_path: str) -> tuple:
    """Convert image to social media optimal format"""
    try:
        log_media(f"Converting image: {input_path}", "CONVERSION")
        
        if not os.path.exists(input_path):
            return False, None, "Input file not found"
        
        # Generate output path
        unique_id = uuid.uuid4().hex[:8]
        timestamp = int(datetime.utcnow().timestamp())
        output_path = os.path.join(OPTIMIZED_DIR, f"social_{timestamp}_{unique_id}.jpg")
        
        # Convert with PIL
        with Image.open(input_path) as img:
            # Fix EXIF orientation
            processed_img = ImageOps.exif_transpose(img)
            
            # Resize if too large (max 1080x1080 for Instagram)
            max_size = 1080
            if processed_img.width > max_size or processed_img.height > max_size:
                processed_img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                log_media(f"Resized to: {processed_img.size}", "INFO")
            
            # Convert to RGB if needed
            if processed_img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', processed_img.size, (255, 255, 255))
                if processed_img.mode in ('RGBA', 'LA'):
                    rgb_img.paste(processed_img, mask=processed_img.split()[-1])
                else:
                    rgb_img.paste(processed_img)
                processed_img = rgb_img
            elif processed_img.mode != 'RGB':
                processed_img = processed_img.convert('RGB')
            
            # Save optimized JPEG
            processed_img.save(output_path, 'JPEG', quality=85, optimize=True)
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            log_media(f"Conversion successful: {file_size:.2f}MB", "SUCCESS")
            return True, output_path, None
        else:
            return False, None, "Output file not created"
            
    except Exception as e:
        log_media(f"Image conversion error: {str(e)}", "ERROR")
        return False, None, str(e)

# === API ENDPOINTS ===
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "directories": {
            "upload": os.path.exists(UPLOAD_DIR),
            "download": os.path.exists(DOWNLOAD_DIR),
            "optimized": os.path.exists(OPTIMIZED_DIR),
            "processed": os.path.exists(PROCESSED_DIR)
        }
    }

@app.post("/api/posts", response_model=PostResponse)
async def create_post(post: PostCreate):
    """Create a new social media post"""
    try:
        log_media(f"Creating post for platform: {post.platform}", "INFO")
        
        # Generate post ID
        post_id = str(uuid.uuid4())
        
        # Process media URLs if provided
        processed_media = []
        if post.media_urls:
            for media_url in post.media_urls:
                log_media(f"Processing media: {media_url}", "INFO")
                # For now, just validate URLs
                if media_url.startswith(('http://', 'https://', '/')):
                    processed_media.append(media_url)
                else:
                    log_media(f"Invalid media URL: {media_url}", "WARNING")
        
        # Create post document
        post_doc = {
            "_id": post_id,
            "content": post.content,
            "media_urls": processed_media,
            "platform": post.platform,
            "status": "created",
            "created_at": datetime.utcnow(),
            "facebook_post_id": None,
            "instagram_post_id": None
        }
        
        # Save to database
        await db.posts.insert_one(post_doc)
        
        log_media(f"Post created successfully: {post_id}", "SUCCESS")
        
        return PostResponse(**post_doc)
        
    except Exception as e:
        log_media(f"Error creating post: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/posts")
async def get_posts(skip: int = 0, limit: int = 10):
    """Get list of posts"""
    try:
        cursor = db.posts.find().skip(skip).limit(limit).sort("created_at", -1)
        posts = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for post in posts:
            post["id"] = post["_id"]
            del post["_id"]
        
        return {"posts": posts, "total": len(posts)}
        
    except Exception as e:
        log_media(f"Error fetching posts: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a media file"""
    try:
        log_media(f"Uploading file: {file.filename}", "INFO")
        
        # Generate unique filename
        unique_id = uuid.uuid4().hex[:8]
        timestamp = int(datetime.utcnow().timestamp())
        filename = f"upload_{timestamp}_{unique_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Check if it's an image and convert if needed
        if file.content_type and file.content_type.startswith('image/'):
            success, converted_path, error = await convert_image_for_social(file_path)
            if success:
                # Upload converted image to FTP
                ftp_success, ftp_url, ftp_error = await upload_to_ftp_simple(converted_path, filename)
                if ftp_success:
                    # Clean up local files
                    try:
                        os.unlink(file_path)
                        os.unlink(converted_path)
                    except:
                        pass
                    
                    log_media(f"File uploaded and processed: {ftp_url}", "SUCCESS")
                    return {"url": ftp_url, "filename": filename, "processed": True}
        
        # For non-images or if conversion failed, upload original
        ftp_success, ftp_url, ftp_error = await upload_to_ftp_simple(file_path, filename)
        if ftp_success:
            try:
                os.unlink(file_path)
            except:
                pass
            
            return {"url": ftp_url, "filename": filename, "processed": False}
        else:
            raise HTTPException(status_code=500, detail=f"FTP upload failed: {ftp_error}")
            
    except Exception as e:
        log_media(f"Upload error: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/webhook")
async def webhook_handler(request: Request):
    """Handle webhooks from external services"""
    try:
        # Get request body
        body = await request.body()
        
        # Log webhook received
        log_media("Webhook received", "INFO")
        
        # Return success response
        return {"status": "received", "timestamp": datetime.utcnow()}
        
    except Exception as e:
        log_media(f"Webhook error: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

# === STARTUP EVENT ===
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🚀 Meta Publishing Platform - Fixed Version Starting...")
    print(f"📁 Upload directory: {UPLOAD_DIR}")
    print(f"🌐 FTP Host: {FTP_HOST}")
    print(f"🔧 DRY_RUN mode: {DRY_RUN}")
    print("✅ Application started successfully!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)