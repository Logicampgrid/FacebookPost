from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
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
from contextlib import asynccontextmanager
from pyngrok import ngrok, conf
import threading
import signal

# Load environment variables
load_dotenv()

# === NGROK CONFIGURATION ===
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")  # Optional for basic usage
ENABLE_NGROK = os.getenv("ENABLE_NGROK", "true").lower() == "true"
NGROK_TUNNEL = None
NGROK_URL = None

# === CONFIGURATION DIRECTORIES - CORRECTED FOR LINUX ===
UPLOAD_DIR = "/app/backend/uploads"
DOWNLOAD_DIR = os.path.join(UPLOAD_DIR, "downloaded")
OPTIMIZED_DIR = os.path.join(UPLOAD_DIR, "optimized")
PROCESSED_DIR = os.path.join(UPLOAD_DIR, "processed")
WORDPRESS_UPLOADS_DIR = "/app/backend/wordpress/uploads/"

# === FRONTEND BUILD DIRECTORY ===
FRONTEND_BUILD_DIR = "/app/frontend/build"

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

def ensure_frontend_build():
    """Check if frontend build exists"""
    if os.path.exists(FRONTEND_BUILD_DIR):
        print(f"✅ Frontend build found: {FRONTEND_BUILD_DIR}")
        return True
    else:
        print(f"⚠️ Frontend build not found: {FRONTEND_BUILD_DIR}")
        return False

# Create directories at startup
ensure_upload_directories()
frontend_build_available = ensure_frontend_build()

# === NGROK FUNCTIONS ===
def start_ngrok_tunnel():
    """Start ngrok tunnel and save URL to file"""
    global NGROK_TUNNEL, NGROK_URL
    
    if not ENABLE_NGROK:
        print("🔧 Ngrok is disabled (ENABLE_NGROK=false)")
        return None
        
    try:
        # First try with subprocess for free ngrok
        print("🚀 Starting ngrok tunnel on port 8001...")
        
        # Kill any existing ngrok processes
        try:
            subprocess.run(["pkill", "-f", "ngrok"], capture_output=True)
        except:
            pass
        
        # Start ngrok with subprocess in background
        ngrok_process = subprocess.Popen(
            ["ngrok", "http", "8001", "--log=stdout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give ngrok time to start
        time.sleep(3)
        
        # Get ngrok URL via API
        try:
            response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                tunnels = response.json()
                if tunnels.get('tunnels'):
                    public_url = tunnels['tunnels'][0]['public_url']
                    NGROK_URL = public_url
                    print(f"🌐 Ngrok tunnel active: {NGROK_URL}")
                    
                    # Save URL to file for frontend access
                    ngrok_url_file = "/app/backend/ngrok_url.txt"
                    with open(ngrok_url_file, "w") as f:
                        f.write(NGROK_URL)
                    print(f"💾 Ngrok URL saved to: {ngrok_url_file}")
                    
                    # Also save to frontend .env file
                    try:
                        frontend_env_path = "/app/frontend/.env"
                        if os.path.exists(frontend_env_path):
                            # Read current .env
                            with open(frontend_env_path, "r") as f:
                                lines = f.readlines()
                            
                            # Update REACT_APP_BACKEND_URL
                            updated_lines = []
                            backend_url_updated = False
                            for line in lines:
                                if line.startswith("REACT_APP_BACKEND_URL="):
                                    updated_lines.append(f"REACT_APP_BACKEND_URL={NGROK_URL}\n")
                                    backend_url_updated = True
                                else:
                                    updated_lines.append(line)
                            
                            # If REACT_APP_BACKEND_URL doesn't exist, add it
                            if not backend_url_updated:
                                updated_lines.append(f"REACT_APP_BACKEND_URL={NGROK_URL}\n")
                            
                            # Write back to file
                            with open(frontend_env_path, "w") as f:
                                f.writelines(updated_lines)
                            print(f"✅ Frontend .env updated with ngrok URL: {NGROK_URL}")
                        
                    except Exception as e:
                        print(f"⚠️ Warning: Could not update frontend .env: {e}")
                    
                    return NGROK_URL
                else:
                    print("❌ No tunnels found in ngrok API response")
            else:
                print(f"❌ Ngrok API returned status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to ngrok API: {e}")
        
        # If API method failed, try pyngrok as fallback
        try:
            print("🔄 Trying pyngrok as fallback...")
            if NGROK_AUTH_TOKEN:
                ngrok.set_auth_token(NGROK_AUTH_TOKEN)
                print("🔑 Ngrok auth token configured")
            
            NGROK_TUNNEL = ngrok.connect(8001)
            NGROK_URL = NGROK_TUNNEL.public_url
            print(f"🌐 Ngrok tunnel active via pyngrok: {NGROK_URL}")
            return NGROK_URL
        except Exception as pyngrok_error:
            print(f"❌ Pyngrok also failed: {pyngrok_error}")
        
        return None
        
    except Exception as e:
        print(f"❌ Failed to start ngrok tunnel: {e}")
        print("🔧 Continuing without ngrok - backend will be available locally only")
        return None

def stop_ngrok_tunnel():
    """Stop ngrok tunnel"""
    global NGROK_TUNNEL
    if NGROK_TUNNEL:
        try:
            ngrok.disconnect(NGROK_TUNNEL.public_url)
            print("🛑 Ngrok tunnel stopped")
        except Exception as e:
            print(f"⚠️ Error stopping ngrok tunnel: {e}")
        finally:
            NGROK_TUNNEL = None

# === LIFESPAN CONTEXT MANAGER ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan events - startup and shutdown"""
    # Startup
    print("🚀 Meta Publishing Platform - Ngrok Integration Starting...")
    print(f"📁 Upload directory: {UPLOAD_DIR}")
    print(f"🌐 FTP Host: {os.getenv('FTP_HOST', 'logicamp.org')}")
    print(f"🔧 DRY_RUN mode: {os.getenv('DRY_RUN', 'false')}")
    
    # Start ngrok tunnel in background thread
    if ENABLE_NGROK:
        ngrok_thread = threading.Thread(target=start_ngrok_tunnel, daemon=True)
        ngrok_thread.start()
        # Give ngrok a moment to start
        await asyncio.sleep(2)
    
    print("✅ Application started successfully!")
    
    yield  # This is where the application runs
    
    # Shutdown
    print("🛑 Shutting down application...")
    if ENABLE_NGROK:
        stop_ngrok_tunnel()
    print("✅ Application shutdown complete!")

# === FASTAPI APP INITIALIZATION ===
app = FastAPI(
    title="Meta Publishing Platform - Ngrok Integration",
    lifespan=lifespan
)

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

# === STATIC FILES CONFIGURATION ===
# Mount static files if frontend build is available
if frontend_build_available:
    # Mount static assets (CSS, JS, images, etc.)
    app.mount("/static", StaticFiles(directory=f"{FRONTEND_BUILD_DIR}/static"), name="static")
    print("✅ Frontend static files mounted at /static")
else:
    print("⚠️ Frontend build not available, static files not mounted")

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

# === CONFIGURATION BOUTIQUES MULTI-PLATFORM ===
PUBLICATION_TEST_MODE = os.getenv("PUBLICATION_TEST_MODE", "true").lower() == "true"

# Dictionnaire statique pour les configurations par défaut
STORES = {
    "logicantiq": {
        "fb_page_id": os.getenv("FB_PAGE_ID_LOGICANTIQ"),
        "ig_user_id": os.getenv("IG_USER_ID_LOGICANTIQ"),
        "access_token": os.getenv("FB_ACCESS_TOKEN_LOGICANTIQ")
    },
    "logicampoutdoor": {
        "fb_page_id": os.getenv("FB_PAGE_ID_LOGICAMPOUTDOOR"),
        "ig_user_id": os.getenv("IG_USER_ID_LOGICAMPOUTDOOR"),
        "access_token": os.getenv("FB_ACCESS_TOKEN_LOGICAMPOUTDOOR")
    },
    "bergerblancsuisse": {
        "fb_page_id": os.getenv("FB_PAGE_ID_BERGER"),
        "ig_user_id": os.getenv("IG_USER_ID_BERGER"),
        "access_token": os.getenv("FB_ACCESS_TOKEN_BERGER")
    },
    "gizmobbs": {
        "fb_page_id": os.getenv("FB_PAGE_ID_GIZMO"),
        "ig_user_id": os.getenv("IG_USER_ID_GIZMO"),
        "access_token": os.getenv("FB_ACCESS_TOKEN_GIZMO")
    }
}

# Dictionnaire dynamique pour les tokens récupérés via authentification
TOKENS = {
    "logicantiq": {},
    "logicampoutdoor": {},
    "bergerblancsuisse": {},
    "gizmobbs": {}
}

def get_store_config(store: str) -> dict:
    """Récupère la configuration d'un store (tokens dynamiques prioritaires sur statiques)"""
    if store not in STORES:
        raise ValueError(f"Store inconnu: {store}")
    
    # Commencer avec la configuration statique
    config = STORES[store].copy()
    
    # Surcharger avec les tokens dynamiques si disponibles
    if store in TOKENS and TOKENS[store]:
        dynamic_config = TOKENS[store]
        if dynamic_config.get("access_token"):
            config["access_token"] = dynamic_config["access_token"]
        if dynamic_config.get("fb_page_id"):
            config["fb_page_id"] = dynamic_config["fb_page_id"]
        if dynamic_config.get("ig_user_id"):
            config["ig_user_id"] = dynamic_config["ig_user_id"]
    
    return config

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

class PublishRequest(BaseModel):
    store: str
    message: str
    product_url: str
    image_url: Optional[str] = None
    platforms: List[str] = ["facebook", "instagram"]  # Par défaut les deux
    
    @validator('store')
    def validate_store(cls, v):
        if v not in STORES:
            raise ValueError(f'Store must be one of: {list(STORES.keys())}')
        return v
    
    @validator('platforms')
    def validate_platforms(cls, v):
        valid_platforms = ["facebook", "instagram"]
        for platform in v:
            if platform not in valid_platforms:
                raise ValueError(f'Platform must be one of: {valid_platforms}')
        return v

class PublishResponse(BaseModel):
    success: bool
    store: str
    platforms: List[str]
    facebook_result: Optional[dict] = None
    instagram_result: Optional[dict] = None
    errors: List[str] = []
    test_mode: bool = False

class FacebookAuthRequest(BaseModel):
    code: str
    store: str
    redirect_uri: str

class FacebookAuthResponse(BaseModel):
    success: bool
    store: str
    access_token: Optional[str] = None
    fb_page_id: Optional[str] = None
    ig_user_id: Optional[str] = None
    error: Optional[str] = None

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

# === FONCTIONS DE PUBLICATION MULTI-PLATEFORME ===
def log_publish(message: str, level: str = "INFO"):
    """Logging spécialisé pour les publications"""
    icons = {"INFO": "📢", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
    icon = icons.get(level.upper(), "📢")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [PUBLISH] {message}")

async def extract_image_from_url(url: str) -> Optional[str]:
    """Extrait l'image principale d'une URL via Open Graph"""
    try:
        log_publish(f"Extraction image depuis: {url}", "INFO")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Chercher l'image Open Graph
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            image_url = og_image['content']
            
            # Convertir URL relative en absolue si nécessaire
            if image_url.startswith('/'):
                from urllib.parse import urljoin
                image_url = urljoin(url, image_url)
            
            log_publish(f"Image extraite: {image_url}", "SUCCESS")
            return image_url
        
        # Fallback: chercher la première image
        img_tag = soup.find('img')
        if img_tag and img_tag.get('src'):
            image_url = img_tag['src']
            if image_url.startswith('/'):
                from urllib.parse import urljoin
                image_url = urljoin(url, image_url)
            
            log_publish(f"Image fallback: {image_url}", "INFO")
            return image_url
        
        log_publish("Aucune image trouvée", "WARNING")
        return None
        
    except Exception as e:
        log_publish(f"Erreur extraction image: {str(e)}", "ERROR")
        return None

async def post_to_facebook(store: str, message: str, product_url: str) -> dict:
    """Publie un post sur la page Facebook correspondante"""
    try:
        log_publish(f"Publication Facebook pour {store}", "INFO")
        
        if store not in STORES:
            raise ValueError(f"Store inconnu: {store}")
        
        creds = get_store_config(store)
        
        if not creds["fb_page_id"] or not creds["access_token"]:
            raise ValueError(f"Configuration Facebook manquante pour {store}")
        
        # Mode test : simulation
        if PUBLICATION_TEST_MODE:
            log_publish(f"MODE TEST - Publication Facebook simulée pour {store}", "TEST")
            return {
                "id": f"test_fb_post_{uuid.uuid4().hex[:8]}",
                "message": message,
                "link": product_url,
                "test_mode": True
            }
        
        # Publication réelle
        url = f"{FACEBOOK_GRAPH_URL}/{creds['fb_page_id']}/feed"
        payload = {
            "message": message,
            "link": product_url,
            "access_token": creds["access_token"]
        }
        
        log_publish(f"Requête Facebook: POST {url}", "INFO")
        response = requests.post(url, data=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if "id" not in data:
            raise Exception(f"Réponse Facebook invalide: {data}")
        
        log_publish(f"Publication Facebook réussie: {data['id']}", "SUCCESS")
        return data
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Erreur HTTP Facebook: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_msg += f" - {error_data}"
            except:
                error_msg += f" - Status: {e.response.status_code}"
        log_publish(error_msg, "ERROR")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Erreur Facebook: {str(e)}"
        log_publish(error_msg, "ERROR")
        raise Exception(error_msg)

async def post_to_instagram(store: str, message: str, product_url: str, image_url: str) -> dict:
    """Publie une image avec légende sur Instagram (processus en 2 étapes)"""
    try:
        log_publish(f"Publication Instagram pour {store}", "INFO")
        
        if store not in STORES:
            raise ValueError(f"Store inconnu: {store}")
        
        creds = get_store_config(store)
        
        if not creds["ig_user_id"] or not creds["access_token"]:
            raise ValueError(f"Configuration Instagram manquante pour {store}")
        
        if not image_url:
            raise ValueError("Image URL requise pour Instagram")
        
        # Mode test : simulation
        if PUBLICATION_TEST_MODE:
            log_publish(f"MODE TEST - Publication Instagram simulée pour {store}", "TEST")
            return {
                "id": f"test_ig_post_{uuid.uuid4().hex[:8]}",
                "caption": f"{message}\n\n{product_url}",
                "image_url": image_url,
                "test_mode": True
            }
        
        ig_user_id = creds["ig_user_id"]
        access_token = creds["access_token"]
        
        # Étape 1 : Créer le conteneur média
        log_publish("Étape 1/2 - Création conteneur média Instagram", "INFO")
        create_url = f"{FACEBOOK_GRAPH_URL}/{ig_user_id}/media"
        
        create_payload = {
            "image_url": image_url,
            "caption": f"{message}\n\n{product_url}",
            "access_token": access_token
        }
        
        create_response = requests.post(create_url, data=create_payload, timeout=30)
        create_response.raise_for_status()
        
        media_data = create_response.json()
        
        if "id" not in media_data:
            raise Exception(f"Erreur création conteneur Instagram: {media_data}")
        
        creation_id = media_data["id"]
        log_publish(f"Conteneur créé: {creation_id}", "SUCCESS")
        
        # Étape 2 : Publier le média
        log_publish("Étape 2/2 - Publication du média Instagram", "INFO")
        publish_url = f"{FACEBOOK_GRAPH_URL}/{ig_user_id}/media_publish"
        
        publish_payload = {
            "creation_id": creation_id,
            "access_token": access_token
        }
        
        publish_response = requests.post(publish_url, data=publish_payload, timeout=30)
        publish_response.raise_for_status()
        
        publish_data = publish_response.json()
        
        if "id" not in publish_data:
            raise Exception(f"Erreur publication Instagram: {publish_data}")
        
        log_publish(f"Publication Instagram réussie: {publish_data['id']}", "SUCCESS")
        
        # Retourner les données combinées
        return {
            "id": publish_data["id"],
            "creation_id": creation_id,
            "caption": f"{message}\n\n{product_url}",
            "image_url": image_url
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Erreur HTTP Instagram: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_msg += f" - {error_data}"
            except:
                error_msg += f" - Status: {e.response.status_code}"
        log_publish(error_msg, "ERROR")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Erreur Instagram: {str(e)}"
        log_publish(error_msg, "ERROR")
        raise Exception(error_msg)

async def publish_post(store: str, message: str, product_url: str, image_url: Optional[str] = None, platforms: List[str] = ["facebook", "instagram"]) -> dict:
    """Fonction principale pour publier sur Facebook et/ou Instagram"""
    try:
        log_publish(f"Début publication multi-plateforme pour {store} sur {platforms}", "INFO")
        
        if store not in STORES:
            raise ValueError(f"Store inconnu: {store}")
        
        results = {
            "success": False,
            "store": store,
            "platforms": platforms,
            "facebook_result": None,
            "instagram_result": None,
            "errors": [],
            "test_mode": PUBLICATION_TEST_MODE
        }
        
        # Extraire l'image si pas fournie et Instagram requis
        if "instagram" in platforms and not image_url:
            log_publish("Extraction automatique de l'image pour Instagram", "INFO")
            image_url = await extract_image_from_url(product_url)
            if not image_url:
                results["errors"].append("Impossible d'extraire une image pour Instagram")
        
        # Publication Facebook
        if "facebook" in platforms:
            try:
                fb_result = await post_to_facebook(store, message, product_url)
                results["facebook_result"] = fb_result
                log_publish("Publication Facebook terminée", "SUCCESS")
            except Exception as e:
                error_msg = f"Échec Facebook: {str(e)}"
                results["errors"].append(error_msg)
                log_publish(error_msg, "ERROR")
        
        # Publication Instagram
        if "instagram" in platforms:
            try:
                if not image_url:
                    raise Exception("Image requise pour Instagram")
                
                ig_result = await post_to_instagram(store, message, product_url, image_url)
                results["instagram_result"] = ig_result
                log_publish("Publication Instagram terminée", "SUCCESS")
            except Exception as e:
                error_msg = f"Échec Instagram: {str(e)}"
                results["errors"].append(error_msg)
                log_publish(error_msg, "ERROR")
        
        # Déterminer le succès global
        success_count = 0
        if "facebook" in platforms and results["facebook_result"]:
            success_count += 1
        if "instagram" in platforms and results["instagram_result"]:
            success_count += 1
        
        results["success"] = success_count > 0 and len(results["errors"]) == 0
        
        if results["success"]:
            log_publish(f"Publication multi-plateforme réussie pour {store}", "SUCCESS")
        else:
            log_publish(f"Publication partiellement échouée pour {store}: {results['errors']}", "WARNING")
        
        return results
        
    except Exception as e:
        error_msg = f"Erreur générale publication: {str(e)}"
        log_publish(error_msg, "ERROR")
        return {
            "success": False,
            "store": store,
            "platforms": platforms,
            "facebook_result": None,
            "instagram_result": None,
            "errors": [error_msg],
            "test_mode": PUBLICATION_TEST_MODE
        }

# === FONCTIONS D'AUTHENTIFICATION FACEBOOK ===
def log_auth(message: str, level: str = "INFO"):
    """Logging spécialisé pour l'authentification"""
    icons = {"INFO": "🔐", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    icon = icons.get(level.upper(), "🔐")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [AUTH] {message}")

async def exchange_facebook_code(code: str, redirect_uri: str) -> dict:
    """Échange un code d'autorisation Facebook contre un access token"""
    try:
        log_auth(f"Échange du code d'autorisation Facebook", "INFO")
        
        if not FACEBOOK_APP_ID or not FACEBOOK_APP_SECRET:
            raise Exception("Configuration Facebook manquante (APP_ID ou APP_SECRET)")
        
        # Étape 1: Échanger le code contre un access token
        token_url = f"{FACEBOOK_GRAPH_URL}/oauth/access_token"
        token_params = {
            'client_id': FACEBOOK_APP_ID,
            'client_secret': FACEBOOK_APP_SECRET,
            'redirect_uri': redirect_uri,
            'code': code
        }
        
        log_auth("Requête d'échange de token...", "INFO")
        response = requests.get(token_url, params=token_params, timeout=30)
        response.raise_for_status()
        
        token_data = response.json()
        
        if "access_token" not in token_data:
            raise Exception(f"Token non reçu: {token_data}")
        
        access_token = token_data["access_token"]
        log_auth("Access token reçu avec succès", "SUCCESS")
        
        # Étape 2: Obtenir les informations utilisateur et ses pages
        user_url = f"{FACEBOOK_GRAPH_URL}/me"
        user_params = {
            'access_token': access_token,
            'fields': 'id,name,accounts'
        }
        
        user_response = requests.get(user_url, params=user_params, timeout=30)
        user_response.raise_for_status()
        user_data = user_response.json()
        
        log_auth(f"Utilisateur: {user_data.get('name', 'Inconnu')}", "INFO")
        
        # Étape 3: Obtenir les pages gérées par l'utilisateur
        pages_url = f"{FACEBOOK_GRAPH_URL}/me/accounts"
        pages_params = {
            'access_token': access_token,
            'fields': 'id,name,access_token,instagram_business_account'
        }
        
        pages_response = requests.get(pages_url, params=pages_params, timeout=30)
        pages_response.raise_for_status()
        pages_data = pages_response.json()
        
        pages = pages_data.get('data', [])
        log_auth(f"Trouvé {len(pages)} page(s) gérée(s)", "INFO")
        
        result = {
            "user_access_token": access_token,
            "user_id": user_data.get('id'),
            "user_name": user_data.get('name'),
            "pages": []
        }
        
        # Traiter chaque page
        for page in pages:
            page_info = {
                "page_id": page.get('id'),
                "page_name": page.get('name'),
                "page_access_token": page.get('access_token'),
                "instagram_business_account": None
            }
            
            # Vérifier si la page a un compte Instagram Business connecté
            if 'instagram_business_account' in page:
                ig_account = page['instagram_business_account']
                if ig_account:
                    page_info["instagram_business_account"] = ig_account.get('id')
                    log_auth(f"Page '{page.get('name')}' a un compte Instagram: {ig_account.get('id')}", "INFO")
                else:
                    log_auth(f"Page '{page.get('name')}' n'a pas de compte Instagram", "WARNING")
            
            result["pages"].append(page_info)
        
        log_auth("Authentification Facebook réussie", "SUCCESS")
        return result
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Erreur HTTP lors de l'authentification: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_msg += f" - {error_data}"
            except:
                error_msg += f" - Status: {e.response.status_code}"
        log_auth(error_msg, "ERROR")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Erreur authentification: {str(e)}"
        log_auth(error_msg, "ERROR")
        raise Exception(error_msg)

def save_store_tokens(store: str, page_id: str, page_access_token: str, ig_user_id: str = None):
    """Sauvegarde les tokens d'un store dans le dictionnaire TOKENS"""
    global TOKENS
    
    log_auth(f"Sauvegarde tokens pour {store}", "INFO")
    
    TOKENS[store] = {
        "fb_page_id": page_id,
        "access_token": page_access_token,
        "ig_user_id": ig_user_id,
        "updated_at": datetime.utcnow()
    }
    
    log_auth(f"Tokens sauvegardés: Page={page_id}, Instagram={ig_user_id}", "SUCCESS")

# === API ENDPOINTS ===
@app.get("/api/health")
async def health_check():
    """Health check endpoint with ngrok info and store configurations"""
    # Vérifier la configuration des stores
    store_status = {}
    for store_name, config in STORES.items():
        store_status[store_name] = {
            "fb_page_id": bool(config.get("fb_page_id")),
            "ig_user_id": bool(config.get("ig_user_id")),
            "access_token": bool(config.get("access_token"))
        }
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "publication": {
            "test_mode": PUBLICATION_TEST_MODE,
            "stores_configured": len([s for s in store_status.values() if all(s.values())]),
            "total_stores": len(STORES)
        },
        "stores": store_status,
        "ngrok": {
            "enabled": ENABLE_NGROK,
            "url": NGROK_URL,
            "tunnel_active": NGROK_TUNNEL is not None
        },
        "directories": {
            "upload": os.path.exists(UPLOAD_DIR),
            "download": os.path.exists(DOWNLOAD_DIR),
            "optimized": os.path.exists(OPTIMIZED_DIR),
            "processed": os.path.exists(PROCESSED_DIR)
        }
    }

@app.get("/api/ngrok-info")
async def get_ngrok_info():
    """Get current ngrok tunnel information"""
    return {
        "enabled": ENABLE_NGROK,
        "url": NGROK_URL,
        "tunnel_active": NGROK_TUNNEL is not None,
        "public_url": NGROK_URL if NGROK_TUNNEL else None
    }

@app.get("/api/stores")
async def get_stores():
    """Obtenir la liste des stores configurés"""
    stores_info = {}
    for store_name, config in STORES.items():
        stores_info[store_name] = {
            "name": store_name,
            "facebook_configured": bool(config.get("fb_page_id") and config.get("access_token")),
            "instagram_configured": bool(config.get("ig_user_id") and config.get("access_token")),
            "fb_page_id": config.get("fb_page_id", "Non configuré"),
            "ig_user_id": config.get("ig_user_id", "Non configuré")
        }
    
    return {
        "stores": stores_info,
        "test_mode": PUBLICATION_TEST_MODE,
        "total_stores": len(STORES)
    }

@app.get("/api/publications")
async def get_publications(skip: int = 0, limit: int = 20, store: Optional[str] = None):
    """Obtenir l'historique des publications"""
    try:
        # Construire le filtre
        filter_query = {}
        if store:
            if store not in STORES:
                raise HTTPException(status_code=400, detail=f"Store '{store}' inconnu")
            filter_query["store"] = store
        
        # Récupérer les publications
        cursor = db.publications.find(filter_query).skip(skip).limit(limit).sort("created_at", -1)
        publications = await cursor.to_list(length=limit)
        
        # Convertir pour la réponse
        for pub in publications:
            pub["id"] = pub["_id"]
            del pub["_id"]
        
        # Compter le total
        total = await db.publications.count_documents(filter_query)
        
        return {
            "publications": publications,
            "total": total,
            "skip": skip,
            "limit": limit,
            "store_filter": store
        }
        
    except Exception as e:
        log_publish(f"Erreur récupération publications: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/test-config")
async def test_store_configuration(store: str):
    """Tester la configuration d'un store sans publier"""
    try:
        if store not in STORES:
            raise HTTPException(status_code=400, detail=f"Store '{store}' inconnu")
        
        config = STORES[store]
        results = {
            "store": store,
            "facebook_test": None,
            "instagram_test": None,
            "errors": []
        }
        
        # Test Facebook
        if config.get("fb_page_id") and config.get("access_token"):
            try:
                url = f"{FACEBOOK_GRAPH_URL}/{config['fb_page_id']}"
                params = {"access_token": config["access_token"]}
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    results["facebook_test"] = {
                        "success": True,
                        "page_name": data.get("name", "Inconnu"),
                        "page_id": data.get("id")
                    }
                else:
                    results["facebook_test"] = {
                        "success": False,
                        "error": f"Status {response.status_code}"
                    }
                    results["errors"].append(f"Facebook API error: {response.status_code}")
            except Exception as e:
                results["facebook_test"] = {"success": False, "error": str(e)}
                results["errors"].append(f"Facebook test error: {str(e)}")
        else:
            results["errors"].append("Configuration Facebook incomplète")
        
        # Test Instagram
        if config.get("ig_user_id") and config.get("access_token"):
            try:
                url = f"{FACEBOOK_GRAPH_URL}/{config['ig_user_id']}"
                params = {"fields": "account_type,username", "access_token": config["access_token"]}
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    results["instagram_test"] = {
                        "success": True,
                        "username": data.get("username", "Inconnu"),
                        "account_type": data.get("account_type", "Inconnu"),
                        "user_id": data.get("id")
                    }
                else:
                    results["instagram_test"] = {
                        "success": False,
                        "error": f"Status {response.status_code}"
                    }
                    results["errors"].append(f"Instagram API error: {response.status_code}")
            except Exception as e:
                results["instagram_test"] = {"success": False, "error": str(e)}
                results["errors"].append(f"Instagram test error: {str(e)}")
        else:
            results["errors"].append("Configuration Instagram incomplète")
        
        return results
        
    except Exception as e:
        log_publish(f"Erreur test configuration: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

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
        
        # Convert for response
        post_doc["id"] = post_doc["_id"]
        del post_doc["_id"]
        
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

@app.post("/api/publish", response_model=PublishResponse)
async def publish_to_social_media(request: PublishRequest):
    """Endpoint principal pour publier sur Facebook et/ou Instagram"""
    try:
        log_publish(f"Nouvelle demande de publication: {request.store} -> {request.platforms}", "INFO")
        
        # Validation des paramètres
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Le message ne peut pas être vide")
        
        if not request.product_url.strip():
            raise HTTPException(status_code=400, detail="L'URL du produit ne peut pas être vide")
        
        # Vérifier que le store existe
        if request.store not in STORES:
            available_stores = list(STORES.keys())
            raise HTTPException(
                status_code=400, 
                detail=f"Store '{request.store}' inconnu. Stores disponibles: {available_stores}"
            )
        
        # Vérifier la configuration du store
        store_config = get_store_config(request.store)
        missing_config = []
        
        if "facebook" in request.platforms:
            if not store_config.get("fb_page_id"):
                missing_config.append("fb_page_id")
            if not store_config.get("access_token"):
                missing_config.append("access_token")
        
        if "instagram" in request.platforms:
            if not store_config.get("ig_user_id"):
                missing_config.append("ig_user_id")
            if not store_config.get("access_token"):
                missing_config.append("access_token")
        
        if missing_config:
            raise HTTPException(
                status_code=500, 
                detail=f"Configuration manquante pour {request.store}: {missing_config}"
            )
        
        # Effectuer la publication
        result = await publish_post(
            store=request.store,
            message=request.message,
            product_url=request.product_url,
            image_url=request.image_url,
            platforms=request.platforms
        )
        
        # Sauvegarder en base de données pour historique
        try:
            post_doc = {
                "_id": str(uuid.uuid4()),
                "store": request.store,
                "message": request.message,
                "product_url": request.product_url,
                "image_url": request.image_url,
                "platforms": request.platforms,
                "result": result,
                "created_at": datetime.utcnow(),
                "test_mode": PUBLICATION_TEST_MODE
            }
            await db.publications.insert_one(post_doc)
            log_publish("Publication sauvegardée en base", "INFO")
        except Exception as db_error:
            log_publish(f"Erreur sauvegarde DB: {str(db_error)}", "WARNING")
        
        # Retourner le résultat
        return PublishResponse(**result)
        
    except HTTPException:
        # Re-lancer les HTTPException sans les wrapper
        raise
    except Exception as e:
        error_msg = f"Erreur interne publication: {str(e)}"
        log_publish(error_msg, "ERROR")
        raise HTTPException(status_code=500, detail=error_msg)

# === FONCTION HELPER POUR PARSING FLEXIBLE ===
async def parse_code_state_request(request: Request) -> dict:
    """Parse les données de requête dans plusieurs formats"""
    content_type = request.headers.get("content-type", "").lower()
    
    # Variables pour stocker les données
    code = None
    state = None
    store = "default"
    redirect_uri = ""
    
    if "application/json" in content_type:
        # Format JSON: {"code": "...", "state": "..."}
        try:
            json_data = await request.json()
            code = json_data.get("code")
            state = json_data.get("state")
            store = json_data.get("store", "default")
            redirect_uri = json_data.get("redirect_uri", "")
            log_auth("Données reçues en JSON", "INFO")
        except Exception as e:
            log_auth(f"Erreur parsing JSON: {e}", "ERROR")
            raise HTTPException(status_code=400, detail="Format JSON invalide")
            
    elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        # Format form-data: code=...&state=...
        try:
            form_data = await request.form()
            code = form_data.get("code")
            state = form_data.get("state")
            store = form_data.get("store", "default")
            redirect_uri = form_data.get("redirect_uri", "")
            log_auth("Données reçues en form-data", "INFO")
        except Exception as e:
            log_auth(f"Erreur parsing form-data: {e}", "ERROR")
            raise HTTPException(status_code=400, detail="Format form-data invalide")
    else:
        # Fallback: essayer les deux formats
        try:
            # Essayer JSON d'abord
            json_data = await request.json()
            code = json_data.get("code")
            state = json_data.get("state")
            store = json_data.get("store", "default")
            redirect_uri = json_data.get("redirect_uri", "")
            log_auth("Données reçues en JSON (fallback)", "INFO")
        except:
            try:
                # Essayer form-data ensuite
                form_data = await request.form()
                code = form_data.get("code")
                state = form_data.get("state")
                store = form_data.get("store", "default")
                redirect_uri = form_data.get("redirect_uri", "")
                log_auth("Données reçues en form-data (fallback)", "INFO")
            except Exception as e:
                log_auth(f"Impossible de parser les données: {e}", "ERROR")
                raise HTTPException(
                    status_code=400, 
                    detail="Format de données non supporté. Utilisez JSON ou form-data"
                )
    
    # Validation des paramètres requis
    if not code:
        raise HTTPException(status_code=400, detail="Paramètre 'code' requis")
    if not state:
        raise HTTPException(status_code=400, detail="Paramètre 'state' requis")
    
    return {
        "code": code,
        "state": state,
        "store": store,
        "redirect_uri": redirect_uri
    }

@app.post("/api/auth/facebook/exchange-code")
async def exchange_facebook_code_endpoint(request: Request):
    """Échange un code d'autorisation Facebook - Accepte JSON et form-data et retourne access_token"""
    try:
        # Parser les données selon le format
        data = await parse_code_state_request(request)
        
        log_auth(f"Code exchange reçu - Store: {data['store']}, Code: {data['code'][:10]}..., State: {data['state']}", "INFO")
        
        # Si pas de redirect_uri fourni, utiliser une valeur par défaut
        redirect_uri = data.get('redirect_uri') or "http://localhost:3000/auth/callback"
        
        # VALIDATION: Configuration Facebook requise
        if not FACEBOOK_APP_ID or not FACEBOOK_APP_SECRET:
            log_auth("Configuration Facebook manquante", "WARNING")
            return {
                "success": False,
                "error": "Configuration Facebook manquante (FACEBOOK_APP_ID ou FACEBOOK_APP_SECRET)",
                "test_mode": True,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            # VRAIE AUTHENTIFICATION FACEBOOK
            auth_result = await exchange_facebook_code(data['code'], redirect_uri)
            
            # Chercher une page appropriée pour ce store
            pages = auth_result.get("pages", [])
            if not pages:
                return {
                    "success": False,
                    "error": "Aucune page Facebook trouvée pour cet utilisateur",
                    "user_info": {
                        "user_id": auth_result.get("user_id"),
                        "user_name": auth_result.get("user_name")
                    },
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Prendre la première page disponible
            selected_page = pages[0]
            page_id = selected_page["page_id"]
            page_access_token = selected_page["page_access_token"]
            ig_user_id = selected_page.get("instagram_business_account")
            
            # Sauvegarder les tokens pour ce store si ce n'est pas "default"
            if data['store'] != "default" and data['store'] in STORES:
                save_store_tokens(data['store'], page_id, page_access_token, ig_user_id)
                log_auth(f"Tokens sauvegardés pour le store: {data['store']}", "SUCCESS")
            
            # SUCCÈS - Retourner l'access token
            return {
                "success": True,
                "message": "Authentification Facebook réussie",
                "access_token": page_access_token,
                "fb_page_id": page_id,
                "ig_user_id": ig_user_id,
                "store": data['store'],
                "user_info": {
                    "user_id": auth_result.get("user_id"),
                    "user_name": auth_result.get("user_name"),
                    "total_pages": len(pages)
                },
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as facebook_error:
            # Erreur lors de l'échange Facebook
            log_auth(f"Erreur échange Facebook: {str(facebook_error)}", "ERROR")
            return {
                "success": False,
                "error": f"Erreur Facebook OAuth: {str(facebook_error)}",
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
        
    except HTTPException:
        # Re-lancer les HTTPException sans les wrapper
        raise
    except Exception as e:
        error_msg = f"Erreur exchange-code: {str(e)}"
        log_auth(error_msg, "ERROR")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/auth/facebook/exchange-code-legacy", response_model=FacebookAuthResponse)
async def exchange_facebook_code_legacy(request: FacebookAuthRequest):
    """Ancien endpoint pour compatibilité (utilise store et redirect_uri)"""
    try:
        log_auth(f"Demande d'authentification legacy pour le store: {request.store}", "INFO")
        
        # Vérifier que le store existe
        if request.store not in STORES:
            available_stores = list(STORES.keys())
            raise HTTPException(
                status_code=400,
                detail=f"Store '{request.store}' inconnu. Stores disponibles: {available_stores}"
            )
        
        # Échanger le code contre les tokens
        auth_result = await exchange_facebook_code(request.code, request.redirect_uri)
        
        # Chercher une page appropriée pour ce store
        pages = auth_result.get("pages", [])
        if not pages:
            return FacebookAuthResponse(
                success=False,
                store=request.store,
                error="Aucune page Facebook trouvée pour cet utilisateur"
            )
        
        # Pour l'instant, prendre la première page disponible
        # TODO: Améliorer la logique de sélection de page
        selected_page = pages[0]
        
        page_id = selected_page["page_id"]
        page_access_token = selected_page["page_access_token"]
        ig_user_id = selected_page.get("instagram_business_account")
        
        # Sauvegarder les tokens pour ce store
        save_store_tokens(request.store, page_id, page_access_token, ig_user_id)
        
        log_auth(f"Authentification legacy réussie pour {request.store}", "SUCCESS")
        
        return FacebookAuthResponse(
            success=True,
            store=request.store,
            access_token=page_access_token,
            fb_page_id=page_id,
            ig_user_id=ig_user_id
        )
        
    except HTTPException:
        # Re-lancer les HTTPException sans les wrapper
        raise
    except Exception as e:
        error_msg = f"Erreur authentification Facebook legacy: {str(e)}"
        log_auth(error_msg, "ERROR")
        return FacebookAuthResponse(
            success=False,
            store=request.store,
            error=error_msg
        )

@app.get("/api/webhook")
async def webhook_verify(request: Request):
    """Handle Facebook webhook verification (GET request)"""
    try:
        # ===== CORRECTION 1: Amélioration de la récupération des paramètres =====
        # Récupération plus robuste des paramètres de requête Facebook
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token") 
        challenge = request.query_params.get("hub.challenge")
        
        # ===== CORRECTION 2: Configuration du token de vérification =====
        # Token de vérification depuis .env (doit correspondre au script GUI Windows)
        VERIFY_TOKEN = os.getenv("FACEBOOK_VERIFY_TOKEN", "mon_token_secret_webhook")
        
        # ===== CORRECTION 3: Logging détaillé pour debug =====
        print(f"🔍 [WEBHOOK DEBUG] Paramètres reçus:")
        print(f"    - hub.mode: '{mode}'")
        print(f"    - hub.verify_token: '{token}'") 
        print(f"    - hub.challenge: '{challenge}'")
        print(f"    - Token attendu: '{VERIFY_TOKEN}'")
        print(f"    - URL complète: {request.url}")
        
        # ===== CORRECTION 4: Validation stricte des paramètres requis =====
        if not mode or not token or not challenge:
            log_media("Paramètres manquants dans la requête webhook", "ERROR")
            print(f"❌ Paramètres manquants: mode={mode}, token={token}, challenge={challenge}")
            raise HTTPException(
                status_code=400, 
                detail="Paramètres hub.mode, hub.verify_token et hub.challenge requis"
            )
        
        # ===== CORRECTION 5: Vérification exacte des conditions Facebook =====
        if mode == "subscribe" and token == VERIFY_TOKEN:
            log_media("✅ Webhook verification successful!", "SUCCESS")
            print(f"✅ Vérification réussie - Renvoi du challenge: '{challenge}'")
            
            # ===== CORRECTION 6: Réponse en format texte plain pour Facebook =====
            # Facebook attend une réponse texte directe, pas JSON
            return PlainTextResponse(content=str(challenge), status_code=200)
        else:
            # ===== CORRECTION 7: Messages d'erreur détaillés pour debug =====
            error_msg = f"Vérification échouée - Mode: '{mode}' vs 'subscribe', Token: '{token}' vs '{VERIFY_TOKEN}'"
            log_media(error_msg, "ERROR")
            print(f"❌ {error_msg}")
            raise HTTPException(status_code=403, detail="Token de vérification invalide")
            
    except HTTPException:
        # Re-lancer les HTTPException sans les wrapper
        raise
    except Exception as e:
        # ===== CORRECTION 8: Gestion d'erreur robuste =====
        error_detail = f"Erreur interne webhook: {str(e)}"
        log_media(error_detail, "ERROR")
        print(f"❌ Exception webhook: {e}")
        raise HTTPException(status_code=500, detail=error_detail)

@app.post("/api/webhook")
async def webhook_handler(request: Request):
    """Handle Facebook webhook events (POST request) - Support JSON et fichiers binaires"""
    try:
        # Get request body
        body = await request.body()
        
        # Vérifier le Content-Type pour déterminer le traitement
        content_type = request.headers.get("content-type", "").lower()
        log_media(f"Webhook Content-Type: {content_type}", "INFO")
        
        # Si c'est du JSON, traiter normalement
        if "application/json" in content_type or "text/" in content_type:
            try:
                webhook_data = json.loads(body.decode('utf-8'))
                log_media(f"Webhook JSON reçu: {json.dumps(webhook_data, indent=2)}", "INFO")
                
                # Process Facebook webhook data
                if webhook_data.get("object") == "page":
                    entries = webhook_data.get("entry", [])
                    for entry in entries:
                        # Handle page messages
                        if "messaging" in entry:
                            for messaging_event in entry["messaging"]:
                                sender_id = messaging_event.get("sender", {}).get("id")
                                message = messaging_event.get("message", {})
                                
                                if message:
                                    log_media(f"Message from {sender_id}: {message.get('text', 'No text')}", "INFO")
                                    
                                    # Handle attachments (images, videos, etc.)
                                    if "attachments" in message:
                                        for attachment in message["attachments"]:
                                            attachment_type = attachment.get("type")
                                            payload = attachment.get("payload", {})
                                            url = payload.get("url")
                                            log_media(f"Attachment received: {attachment_type} - {url}", "INFO")
                        
                        # Handle page feed changes
                        if "changes" in entry:
                            for change in entry["changes"]:
                                field = change.get("field")
                                value = change.get("value", {})
                                log_media(f"Page change: {field} - {value}", "INFO")
            
            except json.JSONDecodeError:
                log_media("Erreur de décodage JSON, traitement comme données binaires", "WARNING")
                # Si ce n'est pas du JSON valide, traiter comme binaire
                await handle_binary_webhook_data(body, content_type)
        
        # Si c'est des données binaires (images, vidéos, etc.)
        elif any(binary_type in content_type for binary_type in ["image/", "video/", "audio/", "application/octet-stream", "multipart/"]):
            log_media(f"Données binaires reçues: {len(body)} bytes", "INFO")
            await handle_binary_webhook_data(body, content_type)
        
        # Type de contenu non reconnu
        else:
            log_media(f"Type de contenu non reconnu: {content_type}", "WARNING")
            # Essayer de traiter comme texte si possible
            try:
                text_data = body.decode('utf-8')
                log_media(f"Contenu texte reçu: {text_data[:200]}...", "INFO")
            except UnicodeDecodeError:
                log_media("Impossible de décoder le contenu comme texte", "WARNING")
                await handle_binary_webhook_data(body, content_type)
        
        # Facebook attend {"status": "received"} pour confirmer la réception
        print(f"✅ [WEBHOOK POST] Événement traité avec succès")
        return {"status": "received"}
        
    except Exception as e:
        log_media(f"Webhook processing error: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

async def handle_binary_webhook_data(body: bytes, content_type: str):
    """Traite les données binaires reçues via webhook"""
    try:
        log_media(f"Traitement données binaires: {len(body)} bytes, type: {content_type}", "INFO")
        
        # Générer un nom de fichier unique
        timestamp = int(datetime.utcnow().timestamp())
        unique_id = uuid.uuid4().hex[:8]
        
        # Déterminer l'extension du fichier basée sur le Content-Type
        extension = ".bin"  # par défaut
        if "image/jpeg" in content_type:
            extension = ".jpg"
        elif "image/png" in content_type:
            extension = ".png"
        elif "image/gif" in content_type:
            extension = ".gif"
        elif "video/mp4" in content_type:
            extension = ".mp4"
        elif "audio/" in content_type:
            extension = ".audio"
        
        filename = f"webhook_{timestamp}_{unique_id}{extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Sauvegarder le fichier binaire
        with open(file_path, "wb") as f:
            f.write(body)
        
        log_media(f"Fichier binaire sauvegardé: {file_path}", "SUCCESS")
        
        # Si c'est une image, on peut la traiter pour publication
        if "image/" in content_type:
            try:
                # Convertir l'image pour les réseaux sociaux
                success, converted_path, error = await convert_image_for_social(file_path)
                if success:
                    # Uploader sur FTP pour rendre accessible
                    ftp_success, ftp_url, ftp_error = await upload_to_ftp_simple(converted_path, filename)
                    if ftp_success:
                        log_media(f"Image webhook uploadée: {ftp_url}", "SUCCESS")
                    
                    # Nettoyer les fichiers temporaires
                    try:
                        os.unlink(file_path)
                        os.unlink(converted_path)
                    except:
                        pass
            except Exception as img_error:
                log_media(f"Erreur traitement image webhook: {str(img_error)}", "WARNING")
        
    except Exception as e:
        log_media(f"Erreur traitement données binaires: {str(e)}", "ERROR")

# === FRONTEND ROUTES ===
# Root route - serve React app
@app.get("/")
async def serve_root():
    """Serve React app at root"""
    if not frontend_build_available:
        return {"error": "Frontend not built. Run 'npm run build' in /app/frontend"}
    
    index_path = os.path.join(FRONTEND_BUILD_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        raise HTTPException(status_code=404, detail="Frontend index.html not found")

# Catch-all route for SPA - MUST be last
@app.get("/{path:path}")
async def serve_frontend(path: str):
    """Serve React frontend for all non-API routes (SPA catch-all)"""
    # Skip API routes - they should have been handled by specific endpoints
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # If frontend build is not available, return error message
    if not frontend_build_available:
        return {"error": "Frontend not built. Run 'npm run build' in /app/frontend"}
    
    # Try to serve specific file first (for assets like favicon.ico, manifest.json, etc.)
    file_path = os.path.join(FRONTEND_BUILD_DIR, path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # For SPA routing, serve index.html for all other routes
    index_path = os.path.join(FRONTEND_BUILD_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        raise HTTPException(status_code=404, detail="Frontend index.html not found")



if __name__ == "__main__":
    import uvicorn
    
    # Start ngrok tunnel before starting server
    if ENABLE_NGROK:
        start_ngrok_tunnel()
    
    uvicorn.run(app, host="0.0.0.0", port=8001)