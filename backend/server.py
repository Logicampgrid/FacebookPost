from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
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
from bson import ObjectId
from PIL import Image
import io
import tempfile

load_dotenv()

app = FastAPI(title="Meta Publishing Platform - Pages, Groups & Instagram")

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
    # Log webhook requests specifically
    if request.url.path == "/api/webhook":
        method = request.method
        headers = dict(request.headers)
        print(f"🌐 Webhook request: {method} {request.url}")
        print(f"📋 Headers: {headers}")
        
        if method == "POST":
            # For POST requests, we'll let the endpoint handle it
            pass
        elif method == "GET":
            print(f"ℹ️  GET request to webhook endpoint - will return info")
        else:
            print(f"⚠️  Unexpected method {method} to webhook endpoint")
    
    response = await call_next(request)
    return response

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS requests for CORS"""
    return {"message": "OK"}

# MongoDB setup
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.meta_posts

# Facebook/Meta configuration
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
FACEBOOK_GRAPH_URL = os.getenv("FACEBOOK_GRAPH_URL", "https://graph.facebook.com/v18.0")

# Create uploads directory
os.makedirs("uploads", exist_ok=True)

# Shop Type to Page Mapping Configuration
SHOP_PAGE_MAPPING = {
    "outdoor": {
        "name": "LogicampOutdoor",
        "expected_id": None,  # To be configured when page is added
        "woocommerce_url": "https://logicampoutdoor.com"
    },
    "gizmobbs": {
        "name": "Le Berger Blanc Suisse", 
        "expected_id": "100092995904169",  # Specific page ID provided
        "woocommerce_url": "https://gizmobbs.com"
    },
    "logicantiq": {
        "name": "LogicAntiq",
        "expected_id": "210654558802531",  # Existing page ID
        "woocommerce_url": "https://logicantiq.com"
    }
}

# Optimized static file serving with better performance for social media APIs
from fastapi.staticfiles import StaticFiles
class OptimizedStaticFiles(StaticFiles):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    async def __call__(self, scope, receive, send):
        # Add caching headers for better performance
        response = await super().__call__(scope, receive, send)
        return response

app.mount("/api/uploads", OptimizedStaticFiles(directory="uploads"), name="uploads")

# Image optimization functions
def optimize_image_for_instagram(file_path: str, target_path: str = None):
    """Optimize image specifically for Instagram requirements (2025)"""
    try:
        if target_path is None:
            target_path = file_path
            
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Instagram specific constraints
            max_width = 1440
            max_size = 8 * 1024 * 1024  # 8MB max file size
            
            original_width, original_height = img.size
            aspect_ratio = original_width / original_height
            
            # Check and adjust aspect ratio for Instagram (4:5 to 1.91:1)
            min_ratio = 4/5  # 0.8 (portrait)
            max_ratio = 1.91  # 1.91 (landscape)
            
            if aspect_ratio < min_ratio:
                # Too narrow, crop to 4:5
                new_height = int(original_width / min_ratio)
                if new_height < original_height:
                    # Crop from center
                    top = (original_height - new_height) // 2
                    img = img.crop((0, top, original_width, top + new_height))
                    print(f"📐 Cropped image to 4:5 ratio for Instagram")
            elif aspect_ratio > max_ratio:
                # Too wide, crop to 1.91:1
                new_width = int(original_height * max_ratio)
                if new_width < original_width:
                    # Crop from center
                    left = (original_width - new_width) // 2
                    img = img.crop((left, 0, left + new_width, original_height))
                    print(f"📐 Cropped image to 1.91:1 ratio for Instagram")
            
            # Resize if too large
            if img.size[0] > max_width:
                ratio = max_width / img.size[0]
                new_size = (max_width, int(img.size[1] * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                print(f"🔧 Resized image for Instagram: {new_size}")
            
            # Save with progressive JPEG for better loading
            img.save(target_path, 'JPEG', optimize=True, quality=92, progressive=True)
            
            # Check file size
            file_size = os.path.getsize(target_path)
            if file_size > max_size:
                # Reduce quality if file too large
                quality = 85
                while file_size > max_size and quality > 60:
                    img.save(target_path, 'JPEG', optimize=True, quality=quality, progressive=True)
                    file_size = os.path.getsize(target_path)
                    quality -= 5
                    print(f"🔄 Reduced quality to {quality} for Instagram size limit")
            
            print(f"📱 Image optimized for Instagram: {target_path} ({file_size} bytes, {img.size})")
            return True
            
    except Exception as e:
        print(f"❌ Instagram image optimization failed for {file_path}: {e}")
        return False

def optimize_image(file_path: str, target_path: str = None, max_size: tuple = (1200, 1200), quality: int = 85, instagram_mode: bool = False):
    """Optimize image for social media platforms"""
    try:
        if target_path is None:
            target_path = file_path
            
        # Use Instagram-specific optimization if requested
        if instagram_mode:
            return optimize_image_for_instagram(file_path, target_path)
            
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save with optimization
            img.save(target_path, 'JPEG', optimize=True, quality=quality)
            print(f"📈 Image optimized: {file_path} -> {os.path.getsize(target_path)} bytes")
            return True
            
    except Exception as e:
        print(f"❌ Image optimization failed for {file_path}: {e}")
        return False

async def download_and_optimize_for_facebook(media_url: str) -> tuple:
    """Download media and optimize it specifically for Facebook requirements"""
    try:
        print(f"🔄 Downloading and optimizing media: {media_url}")
        
        # Download the media
        response = requests.get(media_url, timeout=30)
        if response.status_code != 200:
            raise Exception(f"Failed to download media: HTTP {response.status_code}")
        
        media_content = response.content
        content_type = response.headers.get('content-type', '').lower()
        
        # Determine media type
        is_video = content_type.startswith('video/') or media_url.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))
        is_image = content_type.startswith('image/') or media_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
        
        if is_image:
            # Optimize image in memory
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                # Save original
                temp_file.write(media_content)
                temp_file.flush()
                
                # Optimize
                optimized_path = temp_file.name + '.optimized.jpg'
                if optimize_image(temp_file.name, optimized_path, max_size=(1200, 1200), quality=90):
                    with open(optimized_path, 'rb') as f:
                        optimized_content = f.read()
                    
                    # Clean up temp files
                    os.unlink(temp_file.name)
                    os.unlink(optimized_path)
                    
                    return optimized_content, 'image/jpeg'
                else:
                    # Clean up and return original
                    os.unlink(temp_file.name)
                    return media_content, content_type
        else:
            # Return video as-is (might need video optimization in the future)
            return media_content, content_type
            
    except Exception as e:
        print(f"❌ Download and optimization failed: {e}")
        raise e

# Pydantic models
class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    facebook_access_token: Optional[str] = None
    facebook_pages: Optional[List[dict]] = []
    facebook_groups: Optional[List[dict]] = []
    instagram_accounts: Optional[List[dict]] = []
    business_managers: Optional[List[dict]] = []
    selected_business_manager: Optional[dict] = None

class BusinessManager(BaseModel):
    id: str
    name: str
    pages: List[dict] = []
    groups: List[dict] = []
    instagram_accounts: List[dict] = []

class Post(BaseModel):
    id: Optional[str] = None
    user_id: str
    content: str
    media_urls: Optional[List[str]] = []
    link_metadata: Optional[List[dict]] = []  # Store detected link metadata
    comment_link: Optional[str] = None  # Link to add as comment after post (backward compatibility)
    comment_text: Optional[str] = None  # Any text to add as comment after post
    target_type: str  # "page", "group", "instagram", "cross-post"
    target_id: str
    target_name: str
    platform: str  # "facebook", "instagram", "meta" (for cross-posting)
    business_manager_id: Optional[str] = None
    business_manager_name: Optional[str] = None
    cross_post_targets: Optional[List[dict]] = []  # For cross-posting to multiple platforms
    scheduled_time: Optional[datetime] = None
    status: str = "draft"  # "draft", "scheduled", "published", "failed"
    comment_status: Optional[str] = None  # "success", "failed", None if no comment
    created_at: datetime = datetime.utcnow()
    published_at: Optional[datetime] = None

class FacebookAuthRequest(BaseModel):
    access_token: str
    business_manager_id: Optional[str] = None

class PostRequest(BaseModel):
    content: str
    target_type: str
    target_id: str
    target_name: str
    platform: str = "facebook"
    business_manager_id: Optional[str] = None
    cross_post_targets: Optional[List[dict]] = []
    scheduled_time: Optional[str] = None
    comment_link: Optional[str] = None  # Link to add as comment (backward compatibility)
    comment_text: Optional[str] = None  # Any text to add as comment

class FacebookCodeExchangeRequest(BaseModel):
    code: str
    redirect_uri: str

class LinkPreviewRequest(BaseModel):
    url: str

class BusinessManagerSelectRequest(BaseModel):
    business_manager_id: str

# N8N Integration Models
class ProductPublishRequest(BaseModel):
    title: str
    description: str
    image_url: str
    product_url: str
    user_id: Optional[str] = None  # Facebook user ID or MongoDB user ID
    page_id: Optional[str] = None  # Specific Facebook page ID to post to
    shop_type: Optional[str] = None  # Target shop: "outdoor", "gizmobbs", "logicantiq"
    api_key: Optional[str] = None  # Optional API key for authentication

# N8N Webhook Models - For direct webhook from N8N transformations
class N8NWebhookRequest(BaseModel):
    store: str  # "outdoor", "gizmobbs", "logicantiq"
    title: str
    description: str
    product_url: str
    image_url: str

# Facebook/Meta API functions
async def get_facebook_user_info(access_token: str):
    """Get user info from Facebook"""
    try:
        response = requests.get(
            f"{FACEBOOK_GRAPH_URL}/me",
            params={
                "access_token": access_token,
                "fields": "id,name,email"
            }
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error getting Facebook user info: {e}")
        return None

async def get_facebook_business_managers(access_token: str):
    """Get user's Business Managers"""
    try:
        response = requests.get(
            f"{FACEBOOK_GRAPH_URL}/me/businesses",
            params={
                "access_token": access_token,
                "fields": "id,name,verification_status"
            }
        )
        
        if response.status_code == 200:
            businesses = response.json().get("data", [])
            print(f"Found {len(businesses)} business managers")
            return businesses
        else:
            print(f"Error getting business managers: {response.status_code}")
            print(response.json())
            return []
    except Exception as e:
        print(f"Error getting Facebook business managers: {e}")
        return []

async def get_business_manager_pages(access_token: str, business_id: str):
    """Get pages from a specific Business Manager"""
    try:
        # Get pages owned by this business manager
        response = requests.get(
            f"{FACEBOOK_GRAPH_URL}/{business_id}/client_pages",
            params={
                "access_token": access_token,
                "fields": "id,name,access_token,category,verification_status"
            }
        )
        
        if response.status_code == 200:
            pages = response.json().get("data", [])
            print(f"Found {len(pages)} pages for business manager {business_id}")
            return pages
        else:
            print(f"Error getting pages for business {business_id}: {response.status_code}")
            print(response.json())
            return []
    except Exception as e:
        print(f"Error getting business manager pages: {e}")
        return []

async def get_business_manager_groups(access_token: str, business_id: str):
    """Get groups from a specific Business Manager"""
    try:
        # Get groups owned by this business manager
        response = requests.get(
            f"{FACEBOOK_GRAPH_URL}/{business_id}/groups",
            params={
                "access_token": access_token,
                "fields": "id,name,privacy,description,member_count"
            }
        )
        
        if response.status_code == 200:
            groups = response.json().get("data", [])
            print(f"Found {len(groups)} groups for business manager {business_id}")
            return groups
        else:
            print(f"Error getting groups for business {business_id}: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error getting business manager groups: {e}")
        return []

async def get_business_manager_instagram_accounts(access_token: str, business_id: str):
    """Get Instagram accounts from a specific Business Manager"""
    try:
        # First get pages, then their connected Instagram accounts
        pages = await get_business_manager_pages(access_token, business_id)
        instagram_accounts = []
        
        for page in pages:
            try:
                # Get Instagram account connected to this page
                response = requests.get(
                    f"{FACEBOOK_GRAPH_URL}/{page['id']}",
                    params={
                        "access_token": access_token,
                        "fields": "instagram_business_account"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "instagram_business_account" in data:
                        ig_id = data["instagram_business_account"]["id"]
                        
                        # Get Instagram account details
                        ig_response = requests.get(
                            f"{FACEBOOK_GRAPH_URL}/{ig_id}",
                            params={
                                "access_token": access_token,
                                "fields": "id,username,name,profile_picture_url,followers_count,media_count"
                            }
                        )
                        
                        if ig_response.status_code == 200:
                            ig_data = ig_response.json()
                            ig_data["connected_page_id"] = page["id"]
                            ig_data["connected_page_name"] = page["name"]
                            instagram_accounts.append(ig_data)
                            
            except Exception as e:
                print(f"Error getting Instagram for page {page['id']}: {e}")
                continue
        
        print(f"Found {len(instagram_accounts)} Instagram accounts for business manager {business_id}")
        return instagram_accounts
        
    except Exception as e:
        print(f"Error getting business manager Instagram accounts: {e}")
        return []

async def get_facebook_pages(access_token: str):
    """Get user's personal Facebook pages"""
    try:
        response = requests.get(
            f"{FACEBOOK_GRAPH_URL}/me/accounts",
            params={
                "access_token": access_token,
                "fields": "id,name,access_token,category"
            }
        )
        return response.json().get("data", []) if response.status_code == 200 else []
    except Exception as e:
        print(f"Error getting Facebook pages: {e}")
        return []

async def get_facebook_groups(access_token: str):
    """Get user's Facebook groups"""
    try:
        response = requests.get(
            f"{FACEBOOK_GRAPH_URL}/me/groups",
            params={
                "access_token": access_token,
                "fields": "id,name,privacy,description,administrator"
            }
        )
        return response.json().get("data", []) if response.status_code == 200 else []
    except Exception as e:
        print(f"Error getting Facebook groups: {e}")
        return []

async def post_to_facebook(post: Post, page_access_token: str):
    """Post content to Facebook page/group with ENHANCED and OPTIMIZED media handling"""
    try:
        # Extract URLs from post content for Facebook link preview
        urls_in_content = extract_urls_from_text(post.content) if post.content else []
        
        # Initialize variables to avoid scope issues
        data = {"access_token": page_access_token}
        endpoint = ""
        
        # STRATEGY 1: Media posts (images/videos) with OPTIMIZED handling
        if post.media_urls:
            media_url = post.media_urls[0]
            
            # Get full media URL - use environment variable or construct proper public URL
            if media_url.startswith('http'):
                full_media_url = media_url
                # Try to extract local path for direct upload
                local_file_path = None
            else:
                # Use public domain for sharing links
                base_url = os.getenv("PUBLIC_BASE_URL", "https://data-enhancer.preview.emergentagent.com")
                full_media_url = f"{base_url}{media_url}"
                # Extract local file path for direct upload
                local_file_path = media_url.replace('/api/uploads/', 'uploads/')
            
            print(f"📸 Processing OPTIMIZED media upload: {full_media_url}")
            print(f"📁 Local file path: {local_file_path}")
            
            # Try multiple Facebook media strategies with optimization
            try:
                # Use local file for better performance if available
                if local_file_path and os.path.exists(local_file_path):
                    print(f"✅ Using local file for Facebook upload: {local_file_path}")
                    # Read local file content
                    with open(local_file_path, 'rb') as f:
                        media_content = f.read()
                    
                    # Determine content type from file extension
                    file_ext = local_file_path.lower().split('.')[-1]
                    if file_ext in ['jpg', 'jpeg']:
                        content_type = 'image/jpeg'
                    elif file_ext == 'png':
                        content_type = 'image/png'
                    elif file_ext == 'gif':
                        content_type = 'image/gif'
                    elif file_ext in ['mp4', 'mov', 'avi']:
                        content_type = 'video/mp4'
                    else:
                        content_type = 'application/octet-stream'
                        
                    print(f"📊 Local media info: size={len(media_content)} bytes, type={content_type}")
                else:
                    print(f"⚠️ Local file not found, downloading from URL: {full_media_url}")
                    # Fallback to download method
                    media_content, content_type = await download_and_optimize_for_facebook(full_media_url)
                
                print(f"📊 Optimized media info: size={len(media_content)} bytes, type={content_type}")
                
                # Determine media type and file extension
                is_video = content_type.startswith('video/') or media_url.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))
                is_image = content_type.startswith('image/') or media_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
                
                # Prepare base data
                base_data = {
                    "access_token": page_access_token
                }
                
                # Add message/caption if provided
                if post.content and post.content.strip():
                    base_data["message"] = post.content
                
                # STRATEGY 1A: Direct multipart upload with optimized content (preferred)
                try:
                    if is_video:
                        # For videos, use /videos endpoint
                        files = {'source': ('video.mp4', media_content, 'video/mp4')}
                        endpoint = f"{FACEBOOK_GRAPH_URL}/{post.target_id}/videos"
                        print(f"🎥 Uploading optimized video to: {endpoint}")
                    else:
                        # For images, use /photos endpoint with optimized content
                        files = {'source': ('image.jpg', media_content, 'image/jpeg')}
                        endpoint = f"{FACEBOOK_GRAPH_URL}/{post.target_id}/photos"
                        print(f"📸 Uploading optimized image to: {endpoint}")
                    
                    response = requests.post(endpoint, data=base_data, files=files, timeout=60)  # Increased timeout
                    result = response.json()
                    
                    print(f"Facebook direct upload response: {response.status_code} - {result}")
                    
                    if response.status_code == 200 and 'id' in result:
                        print("✅ Direct optimized media upload successful!")
                        return result
                    else:
                        print(f"❌ Direct upload failed: {result}")
                        raise Exception("Direct upload failed")
                        
                except Exception as direct_error:
                    print(f"Direct upload error: {direct_error}")
                    
                    # STRATEGY 1B: Use URL-based posting with link parameter (fallback)
                    try:
                        print("🔄 Trying URL-based media sharing as fallback...")
                        
                        # Use the /feed endpoint with link parameter for better media display
                        feed_data = {
                            "access_token": page_access_token,
                            "link": full_media_url
                        }
                        
                        # Add message
                        if post.content and post.content.strip():
                            feed_data["message"] = post.content
                        else:
                            feed_data["message"] = "📸 Média partagé (optimisé)" if is_image else "🎥 Vidéo partagée"
                        
                        endpoint = f"{FACEBOOK_GRAPH_URL}/{post.target_id}/feed"
                        print(f"🔗 Posting media link to: {endpoint}")
                        
                        response = requests.post(endpoint, data=feed_data, timeout=30)
                        result = response.json()
                        
                        print(f"Facebook link post response: {response.status_code} - {result}")
                        
                        if response.status_code == 200 and 'id' in result:
                            print("✅ URL-based media sharing successful!")
                            return result
                        else:
                            print(f"❌ URL-based sharing failed: {result}")
                            raise Exception("URL-based sharing failed")
                            
                    except Exception as link_error:
                        print(f"URL-based sharing error: {link_error}")
                        
                        # STRATEGY 1C: Last resort - Optimized text post with media information
                        print("🔄 Using optimized text fallback...")
                        
                        # Create a more engaging text post that encourages Facebook to fetch the media
                        media_type_text = "🎥 Vidéo" if is_video else "📸 Image optimisée"
                        
                        fallback_message = ""
                        if post.content and post.content.strip():
                            fallback_message = f"{post.content}\n\n{media_type_text}: {full_media_url}"
                        else:
                            fallback_message = f"{media_type_text} à découvrir : {full_media_url}"
                        
                        data = {
                            "access_token": page_access_token,
                            "message": fallback_message,
                            "link": full_media_url  # Add link parameter to encourage preview
                        }
                        endpoint = f"{FACEBOOK_GRAPH_URL}/{post.target_id}/feed"
                        print("📝 Using enhanced text fallback with link preview")
                        
            except Exception as media_processing_error:
                print(f"Media processing error: {media_processing_error}")
                
                # Final fallback - simple text post
                data = {
                    "access_token": page_access_token,
                    "message": f"{post.content}\n\nMédia disponible: {full_media_url}" if post.content else f"📱 Contenu multimédia: {full_media_url}",
                    "link": full_media_url
                }
                endpoint = f"{FACEBOOK_GRAPH_URL}/{post.target_id}/feed"
                print("📝 Using final text fallback")
                
        # STRATEGY 2: Link posts (URL sharing) - Enhanced
        elif urls_in_content:
            primary_link = urls_in_content[0]
            
            # Determine if we should use link parameter or just message
            content_without_links = post.content if post.content else ""
            for url in urls_in_content:
                content_without_links = content_without_links.replace(url, '').strip()
            
            data = {
                "access_token": page_access_token,
                "link": primary_link  # Always include link for better preview
            }
            
            # Add message content
            if content_without_links:
                data["message"] = content_without_links
            elif post.content:
                data["message"] = post.content
            
            endpoint = f"{FACEBOOK_GRAPH_URL}/{post.target_id}/feed"
            print(f"🔗 Enhanced link post to: {primary_link}")
            
        # STRATEGY 3: Text-only posts
        else:
            data = {
                "access_token": page_access_token,
                "message": post.content if post.content and post.content.strip() else "Post créé depuis Meta Publishing Platform"
            }
            endpoint = f"{FACEBOOK_GRAPH_URL}/{post.target_id}/feed"
            print("📝 Text-only post")
        
        # Make the API call
        print(f"🚀 Posting to: {endpoint}")
        print(f"📋 Request data: {data}")
        
        response = requests.post(endpoint, data=data, timeout=30)  # Increased timeout
        result = response.json()
        
        print(f"📡 Facebook API response: {response.status_code} - {result}")
        
        if response.status_code == 200:
            return result
        else:
            print(f"❌ Facebook API error: {result}")
            return None
            
    except Exception as e:
        print(f"💥 Error posting to Facebook: {e}")
        return None

async def post_to_instagram(post: Post, page_access_token: str):
    """Post content to Instagram Business account with enhanced and optimized media support"""
    try:
        # Instagram posting requires a two-step process:
        # 1. Create media container
        # 2. Publish the container
        
        # Step 1: Create media container
        container_data = {
            "access_token": page_access_token
        }
        
        # Add caption (can be empty)
        if post.content and post.content.strip():
            container_data["caption"] = post.content
        
        # Handle media - PRIORITY: uploaded files over link images
        media_url = None
        media_type = "image"  # default
        
        if post.media_urls:
            # Use uploaded media first (highest priority)
            media_url = post.media_urls[0]
            if media_url.startswith('http'):
                full_media_url = media_url
            else:
                # Use public URL instead of localhost
                base_url = os.getenv("PUBLIC_BASE_URL", "https://data-enhancer.preview.emergentagent.com")
                full_media_url = f"{base_url}{media_url}"
            
            # Determine media type
            if media_url.lower().endswith(('.mp4', '.mov', '.avi')):
                media_type = "video"
                container_data["media_type"] = "VIDEO"
                container_data["video_url"] = full_media_url
                print(f"🎥 Instagram video: {full_media_url}")
            else:
                media_type = "image"
                container_data["image_url"] = full_media_url
                print(f"📸 Instagram optimized image: {full_media_url}")
                
        elif post.link_metadata:
            # Use link image as fallback if no uploaded media
            for link in post.link_metadata:
                if link.get("image"):
                    container_data["image_url"] = link["image"]
                    print(f"🔗 Instagram using link image: {link['image']}")
                    break
        
        if not container_data.get("image_url") and not container_data.get("video_url"):
            # Instagram requires media, so we'll skip posts without images/videos
            print("❌ Instagram requires media - skipping post without images or videos")
            return None
        
        # Create media container with extended timeout
        print(f"📱 Creating Instagram media container: {container_data}")
        container_response = requests.post(
            f"{FACEBOOK_GRAPH_URL}/{post.target_id}/media",
            data=container_data,
            timeout=60  # Increased timeout for optimized images
        )
        
        if container_response.status_code != 200:
            print(f"❌ Failed to create Instagram media container: {container_response.json()}")
            return None
        
        container_result = container_response.json()
        container_id = container_result.get("id")
        
        if not container_id:
            print("❌ No container ID returned from Instagram API")
            return None
        
        print(f"✅ Instagram container created: {container_id}")
        
        # Step 2: Publish the container
        publish_data = {
            "access_token": page_access_token,
            "creation_id": container_id
        }
        
        print("📡 Publishing Instagram container...")
        publish_response = requests.post(
            f"{FACEBOOK_GRAPH_URL}/{post.target_id}/media_publish",
            data=publish_data,
            timeout=60  # Increased timeout
        )
        
        result = publish_response.json()
        print(f"Instagram publish response: {publish_response.status_code} - {result}")
        
        if publish_response.status_code == 200:
            print("✅ Instagram post published successfully!")
            return result
        else:
            print(f"❌ Instagram publish error: {result}")
            return None
            
    except Exception as e:
        print(f"💥 Error posting to Instagram: {e}")
        return None

async def cross_post_to_meta(post: Post, access_tokens: dict):
    """Cross-post to multiple Meta platforms"""
    results = []
    
    for target in post.cross_post_targets:
        try:
            platform = target.get("platform")
            target_id = target.get("id")
            access_token = access_tokens.get(target_id)
            
            if not access_token:
                print(f"No access token for {target_id}")
                continue
            
            # Create a copy of the post for this target
            target_post = Post(
                **{**post.dict(), 
                   "target_id": target_id, 
                   "target_name": target.get("name"),
                   "target_type": target.get("type"),
                   "platform": platform}
            )
            
            if platform == "facebook":
                result = await post_to_facebook(target_post, access_token)
            elif platform == "instagram":
                result = await post_to_instagram(target_post, access_token)
            else:
                print(f"Unsupported platform: {platform}")
                continue
                
            if result:
                results.append({
                    "platform": platform,
                    "target_id": target_id,
                    "target_name": target.get("name"),
                    "status": "success",
                    "post_id": result.get("id"),
                    "result": result
                })
            else:
                results.append({
                    "platform": platform,
                    "target_id": target_id,
                    "target_name": target.get("name"),
                    "status": "failed"
                })
                
        except Exception as e:
            print(f"Error cross-posting to {target}: {e}")
            results.append({
                "platform": target.get("platform"),
                "target_id": target.get("id"),
                "target_name": target.get("name"),
                "status": "error",
                "error": str(e)
            })
    
    return results

async def extract_link_metadata(url: str):
    """Extract metadata from a URL for link preview"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Make request with timeout
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract metadata
        metadata = {
            'url': response.url,  # Final URL after redirects
            'title': '',
            'description': '',
            'image': '',
            'site_name': '',
            'type': 'website'
        }
        
        # Get title - prioritize og:title
        og_title = soup.find('meta', {'property': 'og:title'})
        if og_title and og_title.get('content'):
            metadata['title'] = og_title.get('content').strip()
        else:
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.get_text().strip()
            
        # Get description - prioritize og:description
        og_description = soup.find('meta', {'property': 'og:description'})
        if og_description and og_description.get('content'):
            metadata['description'] = og_description.get('content').strip()
        else:
            description_tag = soup.find('meta', {'name': 'description'})
            if description_tag and description_tag.get('content'):
                metadata['description'] = description_tag.get('content').strip()
            
        # Get image - prioritize og:image
        og_image = soup.find('meta', {'property': 'og:image'})
        if og_image and og_image.get('content'):
            metadata['image'] = og_image.get('content').strip()
            # Make image URL absolute if relative
            if metadata['image'] and not metadata['image'].startswith('http'):
                metadata['image'] = urljoin(response.url, metadata['image'])
            
        # Get site name
        og_site_name = soup.find('meta', {'property': 'og:site_name'})
        if og_site_name and og_site_name.get('content'):
            metadata['site_name'] = og_site_name.get('content').strip()
        else:
            # Extract domain name
            parsed_url = urlparse(response.url)
            metadata['site_name'] = parsed_url.netloc
            
        # Get type
        og_type = soup.find('meta', {'property': 'og:type'})
        if og_type and og_type.get('content'):
            metadata['type'] = og_type.get('content').strip()
            
        # Limit text length
        if metadata['title']:
            metadata['title'] = metadata['title'][:200]
        if metadata['description']:
            metadata['description'] = metadata['description'][:300]
        
        return metadata
        
    except Exception as e:
        print(f"Error extracting metadata from {url}: {e}")
        return None

async def add_comment_to_facebook_post(facebook_post_id: str, comment_text: str, page_access_token: str):
    """Add a comment to a Facebook post"""
    try:
        data = {
            "message": comment_text,
            "access_token": page_access_token
        }
        
        print(f"Adding comment to Facebook post {facebook_post_id}: {comment_text}")
        
        response = requests.post(
            f"{FACEBOOK_GRAPH_URL}/{facebook_post_id}/comments",
            data=data
        )
        
        result = response.json()
        print(f"Facebook comment API response: {response.status_code} - {result}")
        
        if response.status_code == 200:
            return result
        else:
            print(f"Facebook comment API error: {result}")
            return None
            
    except Exception as e:
        print(f"Error adding comment to Facebook post: {e}")
        return None

def extract_urls_from_text(text: str):
    """Extract URLs from text content"""
    # Regex pattern for URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    return list(set(urls))  # Remove duplicates

async def download_product_image(image_url: str) -> str:
    """Download product image from URL and save locally"""
    try:
        print(f"📥 Downloading product image: {image_url}")
        
        # Download the image
        response = requests.get(image_url, timeout=30)
        if response.status_code != 200:
            raise Exception(f"Failed to download image: HTTP {response.status_code}")
        
        # Get content type
        content_type = response.headers.get('content-type', '').lower()
        
        # Determine file extension
        if 'jpeg' in content_type or 'jpg' in content_type:
            ext = 'jpg'
        elif 'png' in content_type:
            ext = 'png'
        elif 'gif' in content_type:
            ext = 'gif'
        elif 'webp' in content_type:
            ext = 'webp'
        else:
            # Default to jpg if we can't determine
            ext = 'jpg'
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}.{ext}"
        file_path = f"uploads/{unique_filename}"
        
        # Save original image
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"📁 Image downloaded: {file_path} ({len(response.content)} bytes)")
        
        # Optimize image for Facebook
        if ext in ['jpg', 'jpeg', 'png', 'webp']:
            optimized_filename = f"{uuid.uuid4()}.jpg"
            optimized_path = f"uploads/{optimized_filename}"
            
            if optimize_image(file_path, optimized_path, max_size=(1200, 1200), quality=90):
                # Remove original and use optimized version
                os.remove(file_path)
                file_path = optimized_path
                unique_filename = optimized_filename
                print(f"✅ Image optimized: {unique_filename}")
            else:
                print(f"⚠️ Image optimization failed, using original: {unique_filename}")
        
        return f"/api/uploads/{unique_filename}"
        
    except Exception as e:
        print(f"❌ Error downloading product image: {e}")
        raise Exception(f"Failed to download product image: {str(e)}")

async def find_page_by_shop_type(user, shop_type: str):
    """Find the appropriate Facebook page based on shop type"""
    try:
        if not shop_type or shop_type not in SHOP_PAGE_MAPPING:
            return None
            
        shop_config = SHOP_PAGE_MAPPING[shop_type]
        expected_name = shop_config["name"]
        expected_id = shop_config.get("expected_id")
        
        print(f"🔍 Looking for page: {expected_name} (shop_type: {shop_type})")
        
        # Search in user's personal pages first
        for page in user.get("facebook_pages", []):
            # Check by ID if available
            if expected_id and page["id"] == expected_id:
                print(f"✅ Found page by ID in personal pages: {page['name']} ({page['id']})")
                return page
            # Check by name (case insensitive, partial match)
            if expected_name.lower() in page["name"].lower():
                print(f"✅ Found page by name in personal pages: {page['name']} ({page['id']})")
                return page
        
        # Search in business manager pages
        for bm in user.get("business_managers", []):
            for page in bm.get("pages", []):
                # Check by ID if available
                if expected_id and page["id"] == expected_id:
                    print(f"✅ Found page by ID in business pages: {page['name']} ({page['id']})")
                    return page
                # Check by name (case insensitive, partial match)
                if expected_name.lower() in page["name"].lower():
                    print(f"✅ Found page by name in business pages: {page['name']} ({page['id']})")
                    return page
        
        print(f"❌ Page not found for shop_type '{shop_type}' (looking for: {expected_name})")
        return None
        
    except Exception as e:
        print(f"❌ Error finding page by shop type: {e}")
        return None

async def find_user_and_page_for_publishing(user_id: str = None, page_id: str = None, shop_type: str = None):
    """Find user and determine which page to publish to"""
    try:
        # Try to find user by different methods
        user = None
        
        if user_id:
            # Try MongoDB ObjectId first
            try:
                if len(user_id) == 24:
                    user = await db.users.find_one({"_id": ObjectId(user_id)})
            except:
                pass
            
            # Try by facebook_id if ObjectId failed
            if not user:
                user = await db.users.find_one({"facebook_id": user_id})
        
        # If no user specified or found, get the first available user
        if not user:
            user = await db.users.find_one({})
            if user:
                print(f"⚠️ No user specified, using first available user: {user.get('name')}")
        
        if not user:
            raise Exception("No user found for publishing")
        
        # Find target page
        target_page = None
        access_token = user.get("facebook_access_token")
        
        # Priority 1: Shop type selection (new feature)
        if shop_type:
            target_page = await find_page_by_shop_type(user, shop_type)
            if target_page:
                access_token = target_page.get("access_token", access_token)
                print(f"🏪 Using shop-specific page: {target_page['name']} for {shop_type}")
        
        # Priority 2: If page_id specified, find that specific page
        if not target_page and page_id:
            # Check personal pages
            for page in user.get("facebook_pages", []):
                if page["id"] == page_id:
                    target_page = page
                    access_token = page.get("access_token", access_token)
                    break
            
            # Check business manager pages if not found
            if not target_page:
                for bm in user.get("business_managers", []):
                    for page in bm.get("pages", []):
                        if page["id"] == page_id:
                            target_page = page
                            access_token = page.get("access_token", access_token)
                            break
                    if target_page:
                        break
        
        # Priority 3: If no specific page or page not found, use first available page
        if not target_page:
            # Try business manager pages first
            for bm in user.get("business_managers", []):
                if bm.get("pages"):
                    target_page = bm["pages"][0]
                    access_token = target_page.get("access_token", access_token)
                    print(f"📄 Using business page: {target_page.get('name')}")
                    break
            
            # If no business pages, try personal pages
            if not target_page and user.get("facebook_pages"):
                target_page = user["facebook_pages"][0]
                access_token = target_page.get("access_token", access_token)
                print(f"📄 Using personal page: {target_page.get('name')}")
        
        if not target_page:
            raise Exception("No Facebook page available for publishing")
        
        return user, target_page, access_token
        
    except Exception as e:
        print(f"❌ Error finding user and page: {e}")
        raise Exception(f"Failed to find user and page for publishing: {str(e)}")

async def create_product_post(request: ProductPublishRequest) -> dict:
    """Create a Facebook post for a product from n8n data"""
    try:
        print(f"🛍️ Creating product post: {request.title}")
        
        # Find user and page for publishing
        user, target_page, access_token = await find_user_and_page_for_publishing(
            request.user_id, request.page_id, request.shop_type
        )
        
        # Download and optimize product image
        media_url = await download_product_image(request.image_url)
        
        # Create post content combining title and description
        post_content = f"{request.title}\n\n{request.description}"
        
        # Create post object
        post_data = {
            "id": str(uuid.uuid4()),
            "user_id": str(user["_id"]) if "_id" in user else user.get("facebook_id"),
            "content": post_content,
            "media_urls": [media_url],
            "link_metadata": [{
                "url": request.product_url,
                "title": request.title,
                "description": request.description,
                "image": request.image_url,
                "type": "product"
            }],
            "comment_link": request.product_url,  # Add product URL as comment
            "comment_text": f"🛒 Voir le produit: {request.product_url}",
            "target_type": "page",
            "target_id": target_page["id"],
            "target_name": target_page["name"],
            "platform": "facebook",
            "business_manager_id": None,
            "business_manager_name": None,
            "cross_post_targets": [],
            "scheduled_time": None,
            "status": "published",
            "comment_status": None,  
            "created_at": datetime.utcnow(),
            "published_at": datetime.utcnow(),
            "source": "n8n_integration",  # Mark as n8n source
            "shop_type": request.shop_type,  # Store shop type for history
            "webhook_data": {  # Store original webhook data for history
                "title": request.title,
                "description": request.description,
                "image_url": request.image_url,
                "product_url": request.product_url,
                "received_at": datetime.utcnow()
            }
        }
        
        # Create Post object for Facebook API
        post_obj = Post(**post_data)
        
        # Publish to Facebook (with test mode detection)
        print(f"📤 Publishing to Facebook page: {target_page['name']} ({target_page['id']})")
        
        # Check if this is a test token - if so, simulate success
        if access_token.startswith("test_"):
            print("🧪 Test token detected - simulating Facebook publication")
            facebook_result = {
                "id": f"test_fb_post_{uuid.uuid4().hex[:8]}",
                "post_id": f"test_page_{target_page['id']}_{uuid.uuid4().hex[:8]}"
            }
            print(f"✅ Simulated Facebook post: {facebook_result['id']}")
        else:
            # Real Facebook API call
            facebook_result = await post_to_facebook(post_obj, access_token)
        
        if not facebook_result or "id" not in facebook_result:
            raise Exception("Facebook publishing failed")
        
        facebook_post_id = facebook_result["id"]
        post_data["facebook_post_id"] = facebook_post_id
        
        print(f"✅ Facebook post published: {facebook_post_id}")
        
        # Add comment with product link if configured
        if request.product_url and post_data.get("comment_text"):
            try:
                # Simulate comment for test tokens
                if access_token.startswith("test_"):
                    print("🧪 Test token - simulating comment addition")
                    comment_result = {"id": f"test_comment_{uuid.uuid4().hex[:8]}"}
                else:
                    comment_result = await add_comment_to_facebook_post(
                        facebook_post_id, 
                        post_data["comment_text"], 
                        access_token
                    )
                    
                if comment_result:
                    post_data["comment_status"] = "success"
                    print(f"✅ Product link comment added")
                else:
                    post_data["comment_status"] = "failed"
                    print(f"⚠️ Failed to add product link comment")
            except Exception as comment_error:
                print(f"⚠️ Comment error: {comment_error}")
                post_data["comment_status"] = "failed"
        
        # Save to database
        result = await db.posts.insert_one(post_data)
        post_data["_id"] = str(result.inserted_id)
        
        return {
            "success": True,
            "message": f"Product '{request.title}' published successfully to Facebook",
            "facebook_post_id": facebook_post_id,
            "post_id": post_data["id"],
            "page_name": target_page["name"],
            "page_id": target_page["id"],
            "user_name": user.get("name"),
            "media_url": media_url,
            "comment_status": post_data.get("comment_status"),
            "published_at": post_data["published_at"].isoformat()
        }
        
    except Exception as e:
        print(f"💥 Error creating product post: {e}")
        raise Exception(f"Failed to create product post: {str(e)}")

# API Routes

@app.get("/api/facebook/auth-url")
async def get_facebook_auth_url(redirect_uri: str = "http://localhost:3000"):
    """Generate Facebook authentication URL with comprehensive Meta permissions"""
    import urllib.parse
    
    params = {
        "client_id": FACEBOOK_APP_ID,
        "redirect_uri": redirect_uri,
        "scope": "pages_manage_posts,pages_read_engagement,pages_show_list,business_management,read_insights,groups_access_member_info,instagram_basic,instagram_content_publish",
        "response_type": "code",
        "state": "meta_platform_auth"
    }
    
    query_string = urllib.parse.urlencode(params)
    auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?{query_string}"
    
    return {
        "auth_url": auth_url,
        "redirect_uri": redirect_uri,
        "app_id": FACEBOOK_APP_ID,
        "scope": params["scope"]
    }

@app.get("/api/debug/permissions/{token}")
async def debug_permissions(token: str):
    """Debug token permissions to help with Meta platform access"""
    try:
        # Check token info and permissions
        response = requests.get(
            f"{FACEBOOK_GRAPH_URL}/me/permissions",
            params={"access_token": token}
        )
        
        if response.status_code == 200:
            permissions_data = response.json()
            granted_permissions = []
            declined_permissions = []
            
            for perm in permissions_data.get("data", []):
                if perm.get("status") == "granted":
                    granted_permissions.append(perm.get("permission"))
                else:
                    declined_permissions.append({
                        "permission": perm.get("permission"),
                        "status": perm.get("status")
                    })
            
            # Test Business Manager access
            business_test = requests.get(
                f"{FACEBOOK_GRAPH_URL}/me/businesses",
                params={"access_token": token}
            )
            
            business_error = None
            if business_test.status_code != 200:
                business_error = business_test.json()
            
            return {
                "status": "success",
                "granted_permissions": granted_permissions,
                "declined_permissions": declined_permissions,
                "has_business_management": "business_management" in granted_permissions,
                "has_groups_access": "groups_access_member_info" in granted_permissions,
                "has_instagram_basic": "instagram_basic" in granted_permissions,
                "has_instagram_publish": "instagram_content_publish" in granted_permissions,
                "business_api_test": {
                    "status_code": business_test.status_code,
                    "error": business_error
                },
                "recommendations": get_permission_recommendations(granted_permissions)
            }
        else:
            return {
                "status": "error",
                "error": response.json(),
                "status_code": response.status_code
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def get_permission_recommendations(granted_permissions):
    """Get recommendations based on granted permissions"""
    recommendations = []
    required_permissions = [
        "pages_manage_posts",
        "pages_read_engagement", 
        "pages_show_list",
        "business_management",
        "groups_access_member_info",
        "instagram_basic",
        "instagram_content_publish"
    ]
    
    missing_permissions = [p for p in required_permissions if p not in granted_permissions]
    
    if missing_permissions:
        recommendations.append({
            "type": "missing_permissions",
            "message": f"Permissions manquantes: {', '.join(missing_permissions)}",
            "action": "Demandez ces permissions lors de l'authentification"
        })
    
    if "business_management" not in granted_permissions:
        recommendations.append({
            "type": "business_management",
            "message": "La permission 'business_management' est requise pour accéder aux Business Managers",
            "action": "Cette permission peut nécessiter une approbation Facebook pour votre application"
        })

    if "groups_access_member_info" not in granted_permissions:
        recommendations.append({
            "type": "groups_access",
            "message": "La permission 'groups_access_member_info' est requise pour publier dans les groupes",
            "action": "Cette permission peut nécessiter une approbation Facebook"
        })

    if "instagram_content_publish" not in granted_permissions:
        recommendations.append({
            "type": "instagram_publish",
            "message": "La permission 'instagram_content_publish' est requise pour publier sur Instagram",
            "action": "Cette permission peut nécessiter une approbation Facebook"
        })
        
    if not missing_permissions:
        recommendations.append({
            "type": "account_access",
            "message": "Toutes les permissions sont accordées. Vous pouvez publier sur toutes les plateformes Meta !",
            "action": "Vérifiez vos rôles sur business.facebook.com"
        })
    
    return recommendations

@app.get("/api/debug/facebook-token/{token}")
async def debug_facebook_token(token: str):
    """Debug Facebook token for troubleshooting"""
    try:
        # Test with Facebook Graph API
        response = requests.get(
            f"{FACEBOOK_GRAPH_URL}/me",
            params={
                "access_token": token,
                "fields": "id,name,email"
            }
        )
        
        if response.status_code == 200:
            user_data = response.json()
            
            # Test business managers access
            business_response = requests.get(
                f"{FACEBOOK_GRAPH_URL}/me/businesses",
                params={
                    "access_token": token,
                    "fields": "id,name"
                }
            )
            
            business_data = business_response.json() if business_response.status_code == 200 else {"data": []}
            
            return {
                "status": "valid",
                "token": token,
                "user": user_data,
                "business_managers": business_data.get("data", []),
                "expires_at": "unknown"
            }
        else:
            error_data = response.json()
            return {
                "status": "invalid", 
                "token": token,
                "error": error_data,
                "status_code": response.status_code
            }
    except Exception as e:
        return {
            "status": "error",
            "token": token, 
            "error": str(e)
        }

@app.get("/api/debug/facebook-config")
async def debug_facebook_config():
    """Debug Facebook app configuration"""
    return {
        "app_id": FACEBOOK_APP_ID,
        "graph_url": FACEBOOK_GRAPH_URL,
        "app_secret_configured": "Yes" if FACEBOOK_APP_SECRET else "No"
    }

@app.post("/api/publishProduct/setup-test-user")
async def setup_test_user():
    """
    Create a test user with mock Facebook pages for testing n8n integration
    This allows testing the real publishProduct endpoint without needing actual Facebook authentication
    """
    try:
        # Check if test user already exists
        existing_user = await db.users.find_one({"facebook_id": "test_user_n8n"})
        
        if existing_user:
            return {
                "status": "success",
                "message": "Test user already exists",
                "user": {
                    "id": str(existing_user["_id"]),
                    "name": existing_user["name"],
                    "facebook_id": existing_user["facebook_id"],
                    "pages_count": len(existing_user.get("facebook_pages", []))
                }
            }
        
        # Create test user with mock Facebook pages matching our shop types
        test_user = {
            "name": "Test User N8N Integration",
            "email": "test-n8n@example.com", 
            "facebook_id": "test_user_n8n",
            "facebook_access_token": "test_access_token_n8n",
            "facebook_pages": [
                {
                    "id": "100092995904169",  # Real Facebook page ID
                    "name": "Le Berger Blanc Suisse",  # Real page name
                    "access_token": "test_page_token_berger_blanc",
                    "category": "Shopping & Retail"
                },
                {
                    "id": "test_page_logicantiq",
                    "name": "LogicAntiq",  # Exact match for shop mapping
                    "access_token": "test_page_token_logicantiq",
                    "category": "Product/Service"
                },
                {
                    "id": "test_page_outdoor",
                    "name": "LogicampOutdoor",  # Exact match for shop mapping
                    "access_token": "test_page_token_outdoor",
                    "category": "Outdoor Gear"
                }
            ],
            "facebook_groups": [],
            "instagram_accounts": [],
            "business_managers": [],
            "selected_business_manager": None,
            "created_at": datetime.utcnow(),
            "test_user": True
        }
        
        # Insert test user
        result = await db.users.insert_one(test_user)
        test_user["_id"] = str(result.inserted_id)
        
        return {
            "status": "success",
            "message": "Test user created successfully for n8n integration testing",
            "user": {
                "id": test_user["_id"],
                "name": test_user["name"], 
                "facebook_id": test_user["facebook_id"],
                "pages": test_user["facebook_pages"],
                "note": "This is a test user. Use user_id or page_id in publishProduct requests"
            },
            "usage": {
                "endpoint": "/api/publishProduct",
                "user_id": test_user["facebook_id"],
                "page_id": "test_page_n8n_1"
            }
        }
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create test user: {str(e)}")

@app.delete("/api/publishProduct/cleanup-test-user")
async def cleanup_test_user():
    """Remove test user and test posts for clean testing"""
    try:
        # Remove test user
        user_result = await db.users.delete_many({"test_user": True})
        
        # Remove test posts
        posts_result = await db.posts.delete_many({"source": {"$in": ["n8n_integration", "n8n_test"]}})
        
        return {
            "status": "success",
            "message": "Test data cleaned up successfully",
            "deleted": {
                "users": user_result.deleted_count,
                "posts": posts_result.deleted_count
            }
        }
        
    except Exception as e:
        print(f"❌ Error cleaning up test data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup test data: {str(e)}")

@app.get("/api/webhook-history")
async def get_webhook_history(limit: int = 50):
    """
    Get history of webhook publications from N8N
    Returns the latest webhook publications with details
    """
    try:
        print(f"📊 Fetching webhook history (limit: {limit})")
        
        # Query posts from n8n integration, sorted by creation date (newest first)
        cursor = db.posts.find(
            {"source": "n8n_integration"},
            {
                "id": 1,
                "content": 1,
                "target_name": 1,
                "platform": 1,
                "status": 1,
                "comment_status": 1,
                "created_at": 1,
                "published_at": 1,
                "shop_type": 1,
                "webhook_data": 1,
                "facebook_post_id": 1,
                "_id": 0
            }
        ).sort("created_at", -1).limit(limit)
        
        webhook_posts = []
        async for post in cursor:
            webhook_data = post.get("webhook_data", {})
            
            webhook_posts.append({
                "id": post.get("id"),
                "title": webhook_data.get("title", "No title"),
                "description": webhook_data.get("description", "No description"),
                "product_url": webhook_data.get("product_url"),
                "image_url": webhook_data.get("image_url"),
                "shop_type": post.get("shop_type", "unknown"),
                "page_name": post.get("target_name"),
                "platform": post.get("platform", "facebook"),
                "status": post.get("status", "unknown"),
                "comment_added": post.get("comment_status") == "success",
                "facebook_post_id": post.get("facebook_post_id"),
                "received_at": webhook_data.get("received_at", post.get("created_at")),
                "published_at": post.get("published_at")
            })
        
        return {
            "status": "success",
            "message": f"Found {len(webhook_posts)} webhook publications",
            "data": {
                "webhook_posts": webhook_posts,
                "total_count": len(webhook_posts),
                "shop_types_available": list(SHOP_PAGE_MAPPING.keys()),
                "shop_mapping": SHOP_PAGE_MAPPING
            }
        }
        
    except Exception as e:
        print(f"❌ Error fetching webhook history: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching webhook history: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
@app.post("/api/publishProduct")
async def publish_product_from_n8n(request: ProductPublishRequest):
    """
    Publish a product to Facebook from n8n integration
    
    This endpoint receives product data from n8n and automatically publishes it to Facebook.
    The post will include the product image, title, description, and a link to the product page.
    """
    try:
        print(f"🚀 N8N Product Publishing Request: {request.title}")
        
        # Validate required fields
        if not request.title or not request.title.strip():
            raise HTTPException(status_code=400, detail="Product title is required")
        
        if not request.description or not request.description.strip():
            raise HTTPException(status_code=400, detail="Product description is required")
        
        if not request.image_url or not request.image_url.startswith('http'):
            raise HTTPException(status_code=400, detail="Valid product image URL is required")
        
        if not request.product_url or not request.product_url.startswith('http'):
            raise HTTPException(status_code=400, detail="Valid product URL is required")
        
        # Optional API key validation (you can implement your own logic here)
        if request.api_key:
            # Add your API key validation logic here
            # For now, we'll accept any API key, but you can implement proper validation
            print(f"🔑 API Key provided: {request.api_key[:10]}...")
        
        # Create and publish the product post
        result = await create_product_post(request)
        
        # Return success response
        return {
            "status": "success",
            "message": result["message"],
            "data": {
                "facebook_post_id": result["facebook_post_id"],
                "post_id": result["post_id"],
                "page_name": result["page_name"],
                "page_id": result["page_id"],
                "user_name": result["user_name"],
                "published_at": result["published_at"],
                "comment_added": result["comment_status"] == "success",
                "product_title": request.title,
                "product_url": request.product_url
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"💥 Error in publish_product_from_n8n: {e}")
        
        # Return detailed error information
        error_message = str(e)
        error_type = "unknown_error"
        
        if "Failed to download" in error_message:
            error_type = "image_download_error"
        elif "No user found" in error_message or "No Facebook page" in error_message:
            error_type = "authentication_error"
        elif "Facebook" in error_message:
            error_type = "facebook_api_error"
        
        raise HTTPException(
            status_code=500, 
            detail={
                "error": error_message,
                "error_type": error_type,
                "product_title": request.title if hasattr(request, 'title') else "Unknown",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.get("/api/webhook")
async def webhook_info():
    """
    GET endpoint for webhook information and testing
    """
    return {
        "message": "N8N Webhook Endpoint - Use POST method to submit product data",
        "method": "POST",
        "url": "/api/webhook", 
        "content_type": "application/json",
        "required_fields": ["store", "title", "description", "product_url", "image_url"],
        "available_stores": list(SHOP_PAGE_MAPPING.keys()),
        "example_payload": {
            "store": "gizmobbs",
            "title": "Product Name",
            "description": "Product Description", 
            "product_url": "https://example.com/product",
            "image_url": "https://example.com/image.jpg"
        },
        "shop_mapping": SHOP_PAGE_MAPPING
    }

@app.post("/api/webhook")
async def webhook_endpoint(request: N8NWebhookRequest):
    """
    Webhook endpoint for N8N integration - accepts transformed product data
    
    This endpoint accepts the exact format from your N8N transformation script:
    {
        "store": "gizmobbs",
        "title": "Product Name", 
        "description": "Product Description",
        "product_url": "https://...",
        "image_url": "https://..."
    }
    """
    try:
        print(f"🔗 N8N Webhook POST received: {request.title} for store '{request.store}'")
        print(f"📋 Full request data: store={request.store}, title='{request.title}', description='{request.description[:50]}...', product_url={request.product_url}, image_url={request.image_url}")
        
        # Validate required fields
        if not request.title or not request.title.strip():
            print(f"❌ Validation failed: Empty title")
            raise HTTPException(status_code=400, detail="Product title is required")
        
        if not request.description or not request.description.strip():
            print(f"❌ Validation failed: Empty description") 
            raise HTTPException(status_code=400, detail="Product description is required")
        
        if not request.image_url or not request.image_url.startswith('http'):
            print(f"❌ Validation failed: Invalid image URL: {request.image_url}")
            raise HTTPException(status_code=400, detail="Valid product image URL is required")
        
        if not request.product_url or not request.product_url.startswith('http'):
            print(f"❌ Validation failed: Invalid product URL: {request.product_url}")
            raise HTTPException(status_code=400, detail="Valid product URL is required")
        
        # Validate store type
        if not request.store or request.store not in SHOP_PAGE_MAPPING:
            available_stores = ", ".join(SHOP_PAGE_MAPPING.keys())
            print(f"❌ Validation failed: Invalid store '{request.store}'. Available: {available_stores}")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid store type '{request.store}'. Available stores: {available_stores}"
            )
        
        # Convert N8N webhook format to ProductPublishRequest format
        product_request = ProductPublishRequest(
            title=request.title,
            description=request.description,
            image_url=request.image_url,
            product_url=request.product_url,
            shop_type=request.store,  # Map 'store' to 'shop_type'
            user_id=None,  # Will be determined automatically
            page_id=None,  # Will be determined from shop_type mapping
            api_key=None
        )
        
        print(f"🏪 Processing webhook for store: {request.store}")
        print(f"📦 Product: {request.title}")
        print(f"🔗 URL: {request.product_url}")
        print(f"📸 Image: {request.image_url}")
        
        # Create and publish the product post using existing logic
        result = await create_product_post(product_request)
        
        # Return webhook-friendly response
        return {
            "success": True,
            "status": "published",
            "message": f"Product '{request.title}' published successfully to {request.store}",
            "data": {
                "facebook_post_id": result["facebook_post_id"],
                "post_id": result["post_id"],
                "page_name": result["page_name"],
                "page_id": result["page_id"],
                "store": request.store,
                "published_at": result["published_at"],
                "comment_added": result["comment_status"] == "success",
                "webhook_processed_at": datetime.utcnow().isoformat()
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"💥 Error in webhook_endpoint: {e}")
        
        # Return webhook-friendly error response
        error_message = str(e)
        
        return {
            "success": False,
            "status": "failed",
            "message": f"Failed to publish product: {error_message}",
            "error": {
                "type": "webhook_processing_error",
                "details": error_message,
                "product_title": request.title if hasattr(request, 'title') else "Unknown",
                "store": request.store if hasattr(request, 'store') else "Unknown",
                "timestamp": datetime.utcnow().isoformat()
            }
        }

@app.get("/api/publishProduct/config")
async def get_publish_config():
    """
    Get configuration information for n8n integration
    Returns available users and their Facebook pages for publishing
    """
    try:
        users = []
        
        # Get all users with Facebook integration
        async for user in db.users.find({}):
            user_info = {
                "user_id": str(user["_id"]),
                "facebook_id": user.get("facebook_id"),
                "name": user.get("name"),
                "email": user.get("email", ""),
                "pages": []
            }
            
            # Add personal pages
            for page in user.get("facebook_pages", []):
                user_info["pages"].append({
                    "id": page["id"],
                    "name": page["name"],
                    "category": page.get("category", "Personal Page"),
                    "type": "personal"
                })
            
            # Add business manager pages
            for bm in user.get("business_managers", []):
                for page in bm.get("pages", []):
                    user_info["pages"].append({
                        "id": page["id"],
                        "name": page["name"],
                        "category": page.get("category", "Business Page"),
                        "type": "business",
                        "business_manager": bm["name"]
                    })
            
            if user_info["pages"]:  # Only include users with pages
                users.append(user_info)
        
        return {
            "status": "success",
            "message": f"Found {len(users)} users with Facebook pages",
            "users": users,
            "total_pages": sum(len(user["pages"]) for user in users),
            "endpoint_url": "/api/publishProduct",
            "shop_types": SHOP_PAGE_MAPPING,
            "usage_example": {
                "method": "POST",
                "url": "/api/publishProduct",
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": {
                    "title": "Chaise design",
                    "description": "Une chaise design moderne et confortable",
                    "image_url": "https://mon-site.com/images/chaise.jpg",
                    "product_url": "https://mon-site.com/produit/chaise-design",
                    "shop_type": "logicantiq",
                    "user_id": "optional_user_id",
                    "page_id": "optional_page_id",
                    "api_key": "optional_api_key"
                }
            }
        }
        
    except Exception as e:
        print(f"❌ Error getting publish config: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting configuration: {str(e)}")

@app.post("/api/publishProduct/test")
async def test_publish_product(request: ProductPublishRequest):
    """
    Test endpoint for n8n integration - simulates publishing without actually posting to Facebook
    Useful for testing the workflow without requiring valid Facebook tokens
    """
    try:
        print(f"🧪 TEST MODE: Product Publishing Request: {request.title}")
        
        # Validate required fields (same as real endpoint)
        if not request.title or not request.title.strip():
            raise HTTPException(status_code=400, detail="Product title is required")
        
        if not request.description or not request.description.strip():
            raise HTTPException(status_code=400, detail="Product description is required")
        
        if not request.image_url or not request.image_url.startswith('http'):
            raise HTTPException(status_code=400, detail="Valid product image URL is required")
        
        if not request.product_url or not request.product_url.startswith('http'):
            raise HTTPException(status_code=400, detail="Valid product URL is required")
        
        # Test image download
        try:
            media_url = await download_product_image(request.image_url)
            print(f"✅ Image downloaded successfully: {media_url}")
        except Exception as img_error:
            raise HTTPException(status_code=400, detail=f"Failed to download image: {str(img_error)}")
        
        # For test mode, use mock user/page if none exists
        try:
            user, target_page, access_token = await find_user_and_page_for_publishing(
                request.user_id, request.page_id, request.shop_type
            )
            print(f"✅ Found real user and page: {user.get('name')} -> {target_page['name']}")
        except Exception as user_error:
            print(f"⚠️ No real user found, using mock data for test: {user_error}")
            # Create mock user and page for testing
            user = {
                "_id": "test_user_id", 
                "name": "Mock Test User",
                "facebook_id": "mock_facebook_id"
            }
            target_page = {
                "id": "mock_page_id",
                "name": "Mock Facebook Page",
                "access_token": "mock_access_token"
            }
            access_token = "mock_access_token"
        
        # Create simulated post data
        post_content = f"{request.title}\n\n{request.description}"
        fake_facebook_post_id = f"test_{uuid.uuid4().hex[:8]}"
        
        # Simulate success response
        return {
            "status": "success",
            "message": f"TEST MODE: Product '{request.title}' would be published successfully to Facebook",
            "test_mode": True,
            "data": {
                "facebook_post_id": fake_facebook_post_id,
                "post_id": str(uuid.uuid4()),
                "page_name": target_page["name"],
                "page_id": target_page["id"],
                "user_name": user.get("name"),
                "published_at": datetime.utcnow().isoformat(),
                "comment_added": True,
                "product_title": request.title,
                "product_url": request.product_url,
                "media_url": media_url,
                "post_content": post_content,
                "warning": "This was a test - no actual Facebook post was created"
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"💥 Error in test_publish_product: {e}")
        raise HTTPException(status_code=500, detail=f"Test error: {str(e)}")

@app.post("/api/auth/facebook")
async def facebook_auth(auth_request: FacebookAuthRequest):
    """Authenticate user with Facebook and load all Meta platforms"""
    user_info = await get_facebook_user_info(auth_request.access_token)
    
    if not user_info:
        raise HTTPException(status_code=400, detail="Invalid Facebook access token")
    
    # Get user's personal pages
    personal_pages = await get_facebook_pages(auth_request.access_token)
    
    # Get user's personal groups
    personal_groups = await get_facebook_groups(auth_request.access_token)
    
    # Get user's business managers
    business_managers = await get_facebook_business_managers(auth_request.access_token)
    
    # Process business managers and their assets
    business_managers_with_assets = []
    for bm in business_managers:
        pages = await get_business_manager_pages(auth_request.access_token, bm["id"])
        groups = await get_business_manager_groups(auth_request.access_token, bm["id"])
        instagram_accounts = await get_business_manager_instagram_accounts(auth_request.access_token, bm["id"])
        
        business_managers_with_assets.append({
            "id": bm["id"],
            "name": bm["name"],
            "verification_status": bm.get("verification_status"),
            "pages": pages,
            "groups": groups,
            "instagram_accounts": instagram_accounts
        })
    
    # Create or update user
    user_data = {
        "facebook_id": user_info["id"],
        "name": user_info["name"],
        "email": user_info.get("email", ""),
        "facebook_access_token": auth_request.access_token,
        "facebook_pages": personal_pages,
        "facebook_groups": personal_groups,
        "business_managers": business_managers_with_assets,
        "selected_business_manager": None,
        "updated_at": datetime.utcnow()
    }
    
    # Update or insert user
    result = await db.users.update_one(
        {"facebook_id": user_info["id"]},
        {"$set": user_data},
        upsert=True
    )
    
    # Get the user document
    user = await db.users.find_one({"facebook_id": user_info["id"]})
    user["_id"] = str(user["_id"])
    
    return {
        "message": "Authentication successful - Meta platforms loaded",
        "user": user,
        "business_managers_count": len(business_managers_with_assets),
        "personal_pages_count": len(personal_pages),
        "personal_groups_count": len(personal_groups),
        "total_instagram_accounts": sum(len(bm.get("instagram_accounts", [])) for bm in business_managers_with_assets)
    }

@app.post("/api/auth/facebook/exchange-code")
async def exchange_facebook_code(request: FacebookCodeExchangeRequest):
    """Exchange Facebook authorization code for access token"""
    try:
        code = request.code
        redirect_uri = request.redirect_uri
        
        if not code or not redirect_uri:
            raise HTTPException(status_code=400, detail="Code and redirect_uri are required")
        
        # Exchange code for access token
        token_url = f"{FACEBOOK_GRAPH_URL}/oauth/access_token"
        token_params = {
            "client_id": FACEBOOK_APP_ID,
            "client_secret": FACEBOOK_APP_SECRET,
            "redirect_uri": redirect_uri,
            "code": code
        }
        
        response = requests.get(token_url, params=token_params)
        token_data = response.json()
        
        if "access_token" not in token_data:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
        # Now authenticate the user with this access token
        access_token = token_data["access_token"]
        
        user_info = await get_facebook_user_info(access_token)
        if not user_info:
            raise HTTPException(status_code=400, detail="Invalid access token received")
        
        # Get all user assets
        personal_pages = await get_facebook_pages(access_token)
        personal_groups = await get_facebook_groups(access_token)
        business_managers = await get_facebook_business_managers(access_token)
        
        # Process business managers and their assets
        business_managers_with_assets = []
        for bm in business_managers:
            pages = await get_business_manager_pages(access_token, bm["id"])
            groups = await get_business_manager_groups(access_token, bm["id"])
            instagram_accounts = await get_business_manager_instagram_accounts(access_token, bm["id"])
            
            business_managers_with_assets.append({
                "id": bm["id"],
                "name": bm["name"],
                "verification_status": bm.get("verification_status"),
                "pages": pages,
                "groups": groups,
                "instagram_accounts": instagram_accounts
            })
        
        # Create or update user
        user_data = {
            "facebook_id": user_info["id"],
            "name": user_info["name"],
            "email": user_info.get("email", ""),
            "facebook_access_token": access_token,
            "facebook_pages": personal_pages,
            "facebook_groups": personal_groups,
            "business_managers": business_managers_with_assets,
            "selected_business_manager": None,
            "updated_at": datetime.utcnow()
        }
        
        # Update or insert user
        await db.users.update_one(
            {"facebook_id": user_info["id"]},
            {"$set": user_data},
            upsert=True
        )
        
        # Get the user document
        user = await db.users.find_one({"facebook_id": user_info["id"]})
        user["_id"] = str(user["_id"])
        
        return {
            "message": "Authentication successful - All Meta platforms connected",
            "user": user,
            "access_token": access_token,
            "business_managers_count": len(business_managers_with_assets),
            "personal_pages_count": len(personal_pages),
            "personal_groups_count": len(personal_groups),
            "total_instagram_accounts": sum(len(bm.get("instagram_accounts", [])) for bm in business_managers_with_assets)
        }
        
    except Exception as e:
        print(f"Error in Facebook code exchange: {e}")
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

@app.post("/api/users/{user_id}/select-business-manager")
async def select_business_manager(user_id: str, request: BusinessManagerSelectRequest):
    """Select a Business Manager for the user"""
    try:
        # Find user
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Find the selected business manager
        selected_bm = None
        for bm in user.get("business_managers", []):
            if bm["id"] == request.business_manager_id:
                selected_bm = bm
                break
        
        if not selected_bm:
            raise HTTPException(status_code=404, detail="Business Manager not found")
        
        # Update user's selected business manager
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"selected_business_manager": selected_bm}}
        )
        
        return {
            "message": "Business Manager selected successfully",
            "selected_business_manager": selected_bm
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error selecting Business Manager: {str(e)}")

@app.get("/api/users/{user_id}/business-managers")
async def get_user_business_managers(user_id: str):
    """Get user's Business Managers"""
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "business_managers": user.get("business_managers", []),
            "selected_business_manager": user.get("selected_business_manager")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Business Managers: {str(e)}")

@app.get("/api/posts")
async def get_posts(user_id: str = None):
    """Get all posts for a user"""
    query = {"user_id": user_id} if user_id else {}
    posts = await db.posts.find(query).sort("created_at", -1).to_list(None)
    
    # Convert ObjectId to string
    for post in posts:
        post["_id"] = str(post["_id"])
    
    return {"posts": posts}

@app.post("/api/posts")
async def create_post(
    content: str = Form(""),  # Made optional with default empty string
    target_type: str = Form(...),
    target_id: str = Form(...),
    target_name: str = Form(...),
    platform: str = Form("facebook"),
    user_id: str = Form(...),
    business_manager_id: Optional[str] = Form(None),
    business_manager_name: Optional[str] = Form(None),
    scheduled_time: Optional[str] = Form(None),
    comment_link: Optional[str] = Form(None),
    comment_text: Optional[str] = Form(None),  # New field for any comment text
    cross_post_targets: Optional[str] = Form(None)  # JSON string of targets
):
    """Create and immediately publish a post to Meta platforms"""
    try:
        print(f"Creating post for user {user_id} on {platform} target {target_name} ({target_id})")
        
        # Parse cross_post_targets if provided
        cross_targets = []
        if cross_post_targets:
            try:
                cross_targets = json.loads(cross_post_targets)
            except json.JSONDecodeError:
                print("Invalid cross_post_targets JSON")
        
        # Extract and get metadata for links in content
        detected_urls = extract_urls_from_text(content)
        link_metadata = []
        
        # Get metadata for each detected URL (limit to first 3 for performance)
        for url in detected_urls[:3]:
            try:
                metadata = await extract_link_metadata(url)
                if metadata:
                    link_metadata.append(metadata)
                    print(f"Link metadata extracted for {url}: {metadata.get('title', 'No title')}")
            except Exception as e:
                print(f"Error extracting metadata for {url}: {e}")
                continue
        
        # Determine initial status - if there are media files to upload, start as draft
        if scheduled_time:
            status = "scheduled"
            scheduled_dt = datetime.fromisoformat(scheduled_time)
        else:
            status = "draft"  # Start as draft, will be published after media upload if needed
            scheduled_dt = None
        
        post_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "content": content,
            "media_urls": [],
            "link_metadata": link_metadata,
            "comment_link": comment_link,
            "comment_text": comment_text,  # New field
            "target_type": target_type,
            "target_id": target_id,
            "target_name": target_name,
            "platform": platform,
            "business_manager_id": business_manager_id,
            "business_manager_name": business_manager_name,
            "cross_post_targets": cross_targets,
            "scheduled_time": scheduled_dt,
            "status": status,
            "comment_status": None,
            "created_at": datetime.utcnow()
        }
        
        # If not scheduled and no media files expected, publish immediately
        if not scheduled_time:
            # For now, just save as draft - will be published via separate endpoint or after media upload
            print(f"Post created as draft, will be published after media upload or via publish endpoint")
        
        # Save to database
        result = await db.posts.insert_one(post_data)
        post_data["_id"] = str(result.inserted_id)
        
        print(f"Post created with {len(link_metadata)} link metadata entries")
        
        # Return appropriate message based on status
        if post_data["status"] == "scheduled":
            message = f"Post programmé avec succès pour {scheduled_dt.strftime('%Y-%m-%d %H:%M')}"
        else:
            message = f"Post créé avec succès ! Utilisez le bouton de publication pour le publier."
        
        return {"message": message, "post": post_data}
        
    except Exception as e:
        print(f"Error in create_post: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating post: {str(e)}")

@app.post("/api/posts/{post_id}/media")
async def upload_media(post_id: str, file: UploadFile = File(...)):
    """Upload and optimize media for a post"""
    try:
        # Generate unique filename
        file_extension = file.filename.split(".")[-1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"uploads/{unique_filename}"
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Optimize image if it's an image file
        if file_extension in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            print(f"🔧 Optimizing uploaded image: {file_path}")
            optimized_filename = f"{uuid.uuid4()}.jpg"
            optimized_path = f"uploads/{optimized_filename}"
            
            if optimize_image(file_path, optimized_path, max_size=(1200, 1200), quality=90):
                # Remove original and use optimized version
                os.remove(file_path)
                file_path = optimized_path
                unique_filename = optimized_filename
                print(f"✅ Image optimized and saved as: {unique_filename}")
            else:
                print(f"⚠️ Image optimization failed, using original: {unique_filename}")
        
        # Update post with media URL
        media_url = f"/api/uploads/{unique_filename}"
        await db.posts.update_one(
            {"id": post_id},
            {"$push": {"media_urls": media_url}}
        )
        
        # Get file size for logging
        file_size = os.path.getsize(file_path)
        print(f"📁 Media uploaded: {unique_filename} ({file_size} bytes)")
        
        return {"message": "Media uploaded and optimized successfully", "url": media_url, "size": file_size}
    except Exception as e:
        print(f"❌ Error uploading media: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading media: {str(e)}")

@app.post("/api/posts/{post_id}/publish")
async def publish_post(post_id: str):
    """Publish a post to Meta platforms"""
    try:
        # Get post
        post = await db.posts.find_one({"id": post_id})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Get user
        user_id = post["user_id"]
        try:
            if len(user_id) == 24:
                user = await db.users.find_one({"_id": ObjectId(user_id)})
            else:
                user = await db.users.find_one({"_id": user_id})
        except Exception:
            user = await db.users.find_one({"_id": user_id}) or await db.users.find_one({"facebook_id": user_id})
            
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Handle cross-posting
        if post.get("target_id") == "cross-post" and post.get("cross_post_targets"):
            # Cross-posting to multiple platforms
            results = []
            
            for target in post.get("cross_post_targets", []):
                try:
                    # Find the correct access token for this target
                    access_token = user["facebook_access_token"]
                    
                    if post.get("business_manager_id"):
                        for bm in user.get("business_managers", []):
                            if bm["id"] == post["business_manager_id"]:
                                for page in bm.get("pages", []):
                                    if page["id"] == target["id"]:
                                        access_token = page.get("access_token", access_token)
                                        break
                                for ig in bm.get("instagram_accounts", []):
                                    if ig["id"] == target["id"]:
                                        access_token = access_token  # Instagram uses connected page token
                                        break
                                break
                    
                    # Create post object for this target
                    target_post = Post(
                        **{**post, 
                           "target_id": target["id"], 
                           "target_name": target.get("name"),
                           "target_type": target.get("type", "page"),
                           "platform": target.get("platform", "facebook")}
                    )
                    
                    print(f"🎯 Cross-posting to {target.get('name')} ({target['id']}) on {target.get('platform', 'facebook')}")
                    
                    # Publish based on platform
                    if target.get("platform") == "instagram":
                        result = await post_to_instagram(target_post, access_token)
                    else:  # facebook
                        result = await post_to_facebook(target_post, access_token)
                    
                    if result and "id" in result:
                        results.append({
                            "target_name": target.get("name"),
                            "target_id": target["id"],
                            "platform": target.get("platform", "facebook"),
                            "status": "success",
                            "post_id": result["id"]
                        })
                        print(f"✅ Successfully posted to {target.get('name')}: {result['id']}")
                    else:
                        results.append({
                            "target_name": target.get("name"),
                            "target_id": target["id"],
                            "platform": target.get("platform", "facebook"),
                            "status": "failed"
                        })
                        print(f"❌ Failed to post to {target.get('name')}")
                        
                except Exception as target_error:
                    print(f"Error publishing to {target.get('name', 'unknown')}: {target_error}")
                    results.append({
                        "target_name": target.get("name"),
                        "target_id": target.get("id"),
                        "platform": target.get("platform", "facebook"),
                        "status": "error",
                        "error": str(target_error)
                    })
            
            # Check if at least one publication succeeded
            successful_posts = [r for r in results if r["status"] == "success"]
            
            if successful_posts:
                # Update post status
                await db.posts.update_one(
                    {"id": post_id},
                    {
                        "$set": {
                            "status": "published",
                            "published_at": datetime.utcnow(),
                            "cross_post_results": results
                        }
                    }
                )
                
                success_count = len(successful_posts)
                total_count = len(results)
                return {"message": f"Cross-post publié avec succès sur {success_count}/{total_count} plateformes", "results": results}
            else:
                await db.posts.update_one(
                    {"id": post_id},
                    {"$set": {"status": "failed", "cross_post_results": results}}
                )
                raise HTTPException(status_code=400, detail=f"Échec de publication sur toutes les plateformes")
        
        else:
            # Single platform posting
            # Find the correct access token
            access_token = user["facebook_access_token"]
            platform = post.get("platform", "facebook")
            
            if post.get("business_manager_id"):
                for bm in user.get("business_managers", []):
                    if bm["id"] == post["business_manager_id"]:
                        for page in bm.get("pages", []):
                            if page["id"] == post["target_id"]:
                                access_token = page.get("access_token", access_token)
                                break
                        for ig in bm.get("instagram_accounts", []):
                            if ig["id"] == post["target_id"]:
                                access_token = access_token  # Instagram uses connected page token
                                break
                        break
            else:
                for page in user.get("facebook_pages", []):
                    if page["id"] == post["target_id"]:
                        access_token = page["access_token"]
                        break
            
            # Create Post object
            post_obj = Post(**post)
            
            print(f"🎯 Publishing to {post.get('target_name')} ({post['target_id']}) on {platform}")
            
            # Publish based on platform
            if platform == "instagram":
                result = await post_to_instagram(post_obj, access_token)
            else:  # facebook
                result = await post_to_facebook(post_obj, access_token)
            
            if result and "id" in result:
                # Update post status
                await db.posts.update_one(
                    {"id": post_id},
                    {
                        "$set": {
                            "status": "published",
                            "published_at": datetime.utcnow(),
                            "platform_post_id": result["id"]
                        }
                    }
                )
                
                # Add comment if comment_text or comment_link is provided (Facebook only)
                comment_to_add = None
                if post.get("comment_text") and post["comment_text"].strip():
                    comment_to_add = post["comment_text"].strip()
                elif post.get("comment_link") and post["comment_link"].strip():
                    comment_to_add = post["comment_link"].strip()
                
                if comment_to_add and platform == "facebook":
                    print(f"Adding comment: {comment_to_add}")
                    comment_result = await add_comment_to_facebook_post(
                        result["id"], 
                        comment_to_add, 
                        access_token
                    )
                    
                    if comment_result and "id" in comment_result:
                        await db.posts.update_one(
                            {"id": post_id},
                            {"$set": {"comment_status": "success"}}
                        )
                        print(f"✅ Comment added successfully with ID: {comment_result['id']}")
                    else:
                        await db.posts.update_one(
                            {"id": post_id},
                            {"$set": {"comment_status": "failed"}}
                        )
                        print("❌ Failed to add comment to Facebook post")
                
                success_message = f"Post published successfully on {platform}"
                if comment_to_add and platform == "facebook":
                    if post.get("comment_status") == "success":
                        success_message += " with comment"
                    elif post.get("comment_status") == "failed":
                        success_message += " but comment failed"
                
                return {"message": success_message, "platform_id": result["id"]}
            else:
                await db.posts.update_one(
                    {"id": post_id},
                    {"$set": {"status": "failed"}}
                )
                raise HTTPException(status_code=400, detail=f"Failed to publish post on {platform}")
            
    except Exception as e:
        print(f"💥 Error in publish_post: {e}")
        raise HTTPException(status_code=500, detail=f"Error publishing post: {str(e)}")

@app.delete("/api/posts/{post_id}")
async def delete_post(post_id: str):
    """Delete a post"""
    result = await db.posts.delete_one({"id": post_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {"message": "Post deleted successfully"}

@app.get("/api/users/{user_id}/platforms")
async def get_user_platforms(user_id: str):
    """Get user's all Meta platforms (pages, groups, Instagram)"""
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get personal assets
        personal_pages = user.get("facebook_pages", [])
        personal_groups = user.get("facebook_groups", [])
        
        # Get Business Manager assets
        business_pages = []
        business_groups = []
        business_instagram = []
        
        for bm in user.get("business_managers", []):
            for page in bm.get("pages", []):
                page["business_manager_id"] = bm["id"]
                page["business_manager_name"] = bm["name"]
                page["platform"] = "facebook"
                page["type"] = "page"
                business_pages.append(page)
            
            for group in bm.get("groups", []):
                group["business_manager_id"] = bm["id"]
                group["business_manager_name"] = bm["name"]
                group["platform"] = "facebook"
                group["type"] = "group"
                business_groups.append(group)
            
            for ig in bm.get("instagram_accounts", []):
                ig["business_manager_id"] = bm["id"]
                ig["business_manager_name"] = bm["name"]
                ig["platform"] = "instagram"
                ig["type"] = "instagram"
                business_instagram.append(ig)
        
        return {
            "personal_pages": personal_pages,
            "personal_groups": personal_groups,
            "business_pages": business_pages,
            "business_groups": business_groups,
            "business_instagram": business_instagram,
            "business_managers": user.get("business_managers", []),
            "selected_business_manager": user.get("selected_business_manager"),
            "summary": {
                "total_pages": len(personal_pages) + len(business_pages),
                "total_groups": len(personal_groups) + len(business_groups),
                "total_instagram": len(business_instagram),
                "total_platforms": len(personal_pages) + len(business_pages) + len(personal_groups) + len(business_groups) + len(business_instagram)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting platforms: {str(e)}")

# Legacy endpoint for backward compatibility
@app.get("/api/users/{user_id}/pages")
async def get_user_pages(user_id: str):
    """Get user's Facebook pages - legacy endpoint"""
    return await get_user_platforms(user_id)

@app.post("/api/links/preview")
async def get_link_preview(request: LinkPreviewRequest):
    """Get link preview metadata"""
    try:
        metadata = await extract_link_metadata(request.url)
        
        if not metadata:
            raise HTTPException(status_code=400, detail="Unable to fetch link metadata")
            
        return {"success": True, "metadata": metadata}
        
    except Exception as e:
        print(f"Error getting link preview: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching link preview: {str(e)}")

@app.post("/api/debug/test-link-post")
async def test_link_post(request: dict):
    """Test endpoint to debug link posting to Meta platforms"""
    try:
        content = request.get("content", "")
        link_url = request.get("link_url", "")
        platform = request.get("platform", "facebook")
        
        if not content and not link_url:
            return {"error": "Content or link_url required"}
        
        # Simulate the post creation flow
        test_content = content if content else f"Check out this link: {link_url}"
        
        # Extract URLs
        urls = extract_urls_from_text(test_content)
        print(f"Extracted URLs: {urls}")
        
        # Get metadata for first URL
        metadata = None
        if urls:
            metadata = await extract_link_metadata(urls[0])
            print(f"Link metadata: {metadata}")
        
        return {
            "content": test_content,
            "platform": platform,
            "detected_urls": urls,
            "link_metadata": metadata,
            "post_strategy": "link_preview" if urls else "text_only",
            "instagram_compatible": bool(metadata and metadata.get("image")) if platform == "instagram" else True
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/text/extract-links")
async def extract_links_from_text_content(text_content: dict):
    """Extract URLs from text content and get their metadata"""
    try:
        text = text_content.get("text", "")
        
        if not text:
            return {"links": []}
            
        # Extract URLs
        urls = extract_urls_from_text(text)
        
        # Get metadata for each URL
        links_metadata = []
        for url in urls[:3]:  # Limit to first 3 URLs to avoid performance issues
            try:
                metadata = await extract_link_metadata(url)
                if metadata:
                    links_metadata.append(metadata)
            except Exception as e:
                print(f"Error processing URL {url}: {e}")
                continue
                
        return {"links": links_metadata}
        
    except Exception as e:
        print(f"Error extracting links: {e}")
        raise HTTPException(status_code=500, detail=f"Error extracting links: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)