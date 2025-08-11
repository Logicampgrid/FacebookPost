from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
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

load_dotenv()

app = FastAPI(title="Facebook Post Manager")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS requests for CORS"""
    return {"message": "OK"}

# MongoDB setup
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.facebook_posts

# Facebook configuration
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
FACEBOOK_GRAPH_URL = os.getenv("FACEBOOK_GRAPH_URL", "https://graph.facebook.com/v18.0")

# Create uploads directory
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Pydantic models
class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    facebook_access_token: Optional[str] = None
    facebook_pages: Optional[List[dict]] = []

class Post(BaseModel):
    id: Optional[str] = None
    user_id: str
    content: str
    media_urls: Optional[List[str]] = []
    target_type: str  # "page" or "group"
    target_id: str
    target_name: str
    scheduled_time: Optional[datetime] = None
    status: str = "draft"  # "draft", "scheduled", "published", "failed"
    created_at: datetime = datetime.utcnow()
    published_at: Optional[datetime] = None

class FacebookAuthRequest(BaseModel):
    access_token: str

class PostRequest(BaseModel):
    content: str
    target_type: str
    target_id: str
    target_name: str
    scheduled_time: Optional[str] = None

class FacebookCodeExchangeRequest(BaseModel):
    code: str
    redirect_uri: str

class LinkPreviewRequest(BaseModel):
    url: str

# Facebook API functions
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

async def get_facebook_pages(access_token: str):
    """Get user's Facebook pages"""
    try:
        response = requests.get(
            f"{FACEBOOK_GRAPH_URL}/me/accounts",
            params={
                "access_token": access_token,
                "fields": "id,name,access_token"
            }
        )
        return response.json().get("data", []) if response.status_code == 200 else []
    except Exception as e:
        print(f"Error getting Facebook pages: {e}")
        return []

async def post_to_facebook(post: Post, page_access_token: str):
    """Post content to Facebook page"""
    try:
        data = {
            "message": post.content,
            "access_token": page_access_token
        }
        
        # Add media if present
        if post.media_urls:
            # For simplicity, we'll post the first image
            # In a real app, you'd handle multiple media properly
            media_url = post.media_urls[0]
            if media_url.startswith('http'):
                data["link"] = media_url
            else:
                # Handle local uploaded files
                data["picture"] = f"http://localhost:8001{media_url}"
        
        response = requests.post(
            f"{FACEBOOK_GRAPH_URL}/{post.target_id}/feed",
            data=data
        )
        
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error posting to Facebook: {e}")
        return None

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

def extract_urls_from_text(text: str):
    """Extract URLs from text content"""
    # Regex pattern for URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    return list(set(urls))  # Remove duplicates

# API Routes

@app.get("/api/facebook/auth-url")
async def get_facebook_auth_url(redirect_uri: str = "http://localhost:3000"):
    """Generate Facebook authentication URL"""
    import urllib.parse
    
    params = {
        "client_id": FACEBOOK_APP_ID,
        "redirect_uri": redirect_uri,
        "scope": "pages_manage_posts,pages_read_engagement,pages_show_list",
        "response_type": "code",
        "state": "test123"
    }
    
    query_string = urllib.parse.urlencode(params)
    auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?{query_string}"
    
    return {
        "auth_url": auth_url,
        "redirect_uri": redirect_uri,
        "app_id": FACEBOOK_APP_ID
    }

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
            return {
                "status": "valid",
                "token": token,
                "user": user_data,
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

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/api/auth/facebook")
async def facebook_auth(auth_request: FacebookAuthRequest):
    """Authenticate user with Facebook"""
    user_info = await get_facebook_user_info(auth_request.access_token)
    
    if not user_info:
        raise HTTPException(status_code=400, detail="Invalid Facebook access token")
    
    # Get user's pages
    pages = await get_facebook_pages(auth_request.access_token)
    
    # Create or update user
    user_data = {
        "facebook_id": user_info["id"],
        "name": user_info["name"],
        "email": user_info.get("email", ""),
        "facebook_access_token": auth_request.access_token,
        "facebook_pages": pages,
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
        "message": "Authentication successful",
        "user": user
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
        
        # Get user's pages
        pages = await get_facebook_pages(access_token)
        
        # Create or update user
        user_data = {
            "facebook_id": user_info["id"],
            "name": user_info["name"],
            "email": user_info.get("email", ""),
            "facebook_access_token": access_token,
            "facebook_pages": pages,
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
            "message": "Authentication successful",
            "user": user,
            "access_token": access_token
        }
        
    except Exception as e:
        print(f"Error in Facebook code exchange: {e}")
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

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
    content: str = Form(...),
    target_type: str = Form(...),
    target_id: str = Form(...),
    target_name: str = Form(...),
    user_id: str = Form(...),
    scheduled_time: Optional[str] = Form(None)
):
    """Create a new post"""
    post_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "content": content,
        "media_urls": [],
        "target_type": target_type,
        "target_id": target_id,
        "target_name": target_name,
        "scheduled_time": datetime.fromisoformat(scheduled_time) if scheduled_time else None,
        "status": "scheduled" if scheduled_time else "draft",
        "created_at": datetime.utcnow()
    }
    
    result = await db.posts.insert_one(post_data)
    post_data["_id"] = str(result.inserted_id)
    
    return {"message": "Post created successfully", "post": post_data}

@app.post("/api/posts/{post_id}/media")
async def upload_media(post_id: str, file: UploadFile = File(...)):
    """Upload media for a post"""
    try:
        # Generate unique filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"uploads/{unique_filename}"
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Update post with media URL
        media_url = f"/uploads/{unique_filename}"
        await db.posts.update_one(
            {"id": post_id},
            {"$push": {"media_urls": media_url}}
        )
        
        return {"message": "Media uploaded successfully", "url": media_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading media: {str(e)}")

@app.post("/api/posts/{post_id}/publish")
async def publish_post(post_id: str):
    """Publish a post to Facebook"""
    try:
        # Get post
        post = await db.posts.find_one({"id": post_id})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Get user
        user = await db.users.find_one({"_id": post["user_id"]})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Find the correct page access token
        page_access_token = user["facebook_access_token"]
        for page in user.get("facebook_pages", []):
            if page["id"] == post["target_id"]:
                page_access_token = page["access_token"]
                break
        
        # Create Post object
        post_obj = Post(**post)
        
        # Publish to Facebook
        result = await post_to_facebook(post_obj, page_access_token)
        
        if result and "id" in result:
            # Update post status
            await db.posts.update_one(
                {"id": post_id},
                {
                    "$set": {
                        "status": "published",
                        "published_at": datetime.utcnow(),
                        "facebook_post_id": result["id"]
                    }
                }
            )
            return {"message": "Post published successfully", "facebook_id": result["id"]}
        else:
            await db.posts.update_one(
                {"id": post_id},
                {"$set": {"status": "failed"}}
            )
            raise HTTPException(status_code=400, detail="Failed to publish post to Facebook")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing post: {str(e)}")

@app.delete("/api/posts/{post_id}")
async def delete_post(post_id: str):
    """Delete a post"""
    result = await db.posts.delete_one({"id": post_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {"message": "Post deleted successfully"}

@app.get("/api/users/{user_id}/pages")
async def get_user_pages(user_id: str):
    """Get user's Facebook pages"""
    user = await db.users.find_one({"_id": user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"pages": user.get("facebook_pages", [])}

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