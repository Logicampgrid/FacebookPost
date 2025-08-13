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

app = FastAPI(title="Meta Publishing Platform - Pages, Groups & Instagram")

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
db = client.meta_posts

# Facebook/Meta configuration
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
    """Post content to Facebook page/group with FIXED media priority"""
    try:
        data = {
            "access_token": page_access_token
        }
        
        # Extract URLs from post content for Facebook link preview
        urls_in_content = extract_urls_from_text(post.content) if post.content else []
        
        # FIXED PRIORITY: 1. Uploaded media files (always use picture), 2. Link previews, 3. Text only
        
        if post.media_urls:
            # Strategy 1: Uploaded media has ABSOLUTE priority - always use picture parameter
            media_url = post.media_urls[0]
            
            # Convert all uploaded media to picture parameter (not link!)
            if media_url.startswith('http'):
                # External URL - use picture parameter to force image display
                data["picture"] = media_url
            else:
                # Local uploaded file
                data["picture"] = f"http://localhost:8001{media_url}"
            
            # Add text content as message
            if post.content and post.content.strip():
                data["message"] = post.content
            
            print(f"📸 Using uploaded media with picture parameter: {data.get('picture')}")
                    
        elif urls_in_content:
            # Strategy 2: Use link sharing for preview ONLY if no uploaded media
            primary_link = urls_in_content[0]
            
            # If content contains only a link (or link + short text), use link parameter
            content_without_links = post.content if post.content else ""
            for url in urls_in_content:
                content_without_links = content_without_links.replace(url, '').strip()
            
            if len(content_without_links) <= 50:  # Short or no additional text
                data["link"] = primary_link
                if content_without_links:
                    data["message"] = content_without_links
            else:
                # Long text with embedded links - use message only
                data["message"] = post.content
                data["link"] = primary_link  # Facebook will still show preview
            
            print(f"🔗 Using link preview for: {primary_link}")
                
        else:
            # Strategy 3: Text-only post
            if post.content and post.content.strip():
                data["message"] = post.content
            else:
                # This shouldn't happen due to frontend validation, but handle gracefully
                data["message"] = "Post créé depuis Meta Publishing Platform"
            
            print("📝 Text-only post")
        
        print(f"Facebook API request data: {data}")
        
        # Choose endpoint based on target type
        if post.target_type == "group":
            endpoint = f"{FACEBOOK_GRAPH_URL}/{post.target_id}/feed"
        else:  # page
            endpoint = f"{FACEBOOK_GRAPH_URL}/{post.target_id}/feed"
        
        response = requests.post(endpoint, data=data)
        
        result = response.json()
        print(f"Facebook API response: {response.status_code} - {result}")
        
        if response.status_code == 200:
            return result
        else:
            print(f"Facebook API error: {result}")
            return None
            
    except Exception as e:
        print(f"Error posting to Facebook: {e}")
        return None

async def post_to_instagram(post: Post, page_access_token: str):
    """Post content to Instagram Business account with media priority"""
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
        
        if post.media_urls:
            # Use uploaded media first (highest priority)
            media_url = post.media_urls[0]
            if media_url.startswith('http'):
                container_data["image_url"] = media_url
            else:
                container_data["image_url"] = f"http://localhost:8001{media_url}"
        elif post.link_metadata:
            # Use link image as fallback if no uploaded media
            for link in post.link_metadata:
                if link.get("image"):
                    container_data["image_url"] = link["image"]
                    break
        
        if not container_data.get("image_url"):
            # Instagram requires media, so we'll skip posts without images
            print("Instagram requires media - skipping post without images")
            return None
        
        # Create media container
        container_response = requests.post(
            f"{FACEBOOK_GRAPH_URL}/{post.target_id}/media",
            data=container_data
        )
        
        if container_response.status_code != 200:
            print(f"Failed to create Instagram media container: {container_response.json()}")
            return None
        
        container_result = container_response.json()
        container_id = container_result.get("id")
        
        if not container_id:
            print("No container ID returned from Instagram API")
            return None
        
        # Step 2: Publish the container
        publish_data = {
            "access_token": page_access_token,
            "creation_id": container_id
        }
        
        publish_response = requests.post(
            f"{FACEBOOK_GRAPH_URL}/{post.target_id}/media_publish",
            data=publish_data
        )
        
        result = publish_response.json()
        print(f"Instagram publish response: {publish_response.status_code} - {result}")
        
        if publish_response.status_code == 200:
            return result
        else:
            print(f"Instagram publish error: {result}")
            return None
            
    except Exception as e:
        print(f"Error posting to Instagram: {e}")
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

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

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
        
        # If not scheduled, publish immediately
        if not scheduled_time:
            print(f"Publishing immediately to {platform}...")
            
            # Get user to find access token
            try:
                if len(user_id) == 24:
                    user = await db.users.find_one({"_id": ObjectId(user_id)})
                else:
                    user = await db.users.find_one({"_id": user_id})
            except Exception:
                user = await db.users.find_one({"_id": user_id}) or await db.users.find_one({"facebook_id": user_id})
                
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Find the correct access token
            access_token = user["facebook_access_token"]
            
            # If cross-posting, handle multiple platforms
            if cross_targets:
                # Build access tokens dict for cross-posting
                access_tokens = {}
                
                for target in cross_targets:
                    target_id_cross = target.get("id")
                    target_type_cross = target.get("type")
                    
                    if business_manager_id:
                        # Look in business manager assets
                        for bm in user.get("business_managers", []):
                            if bm["id"] == business_manager_id:
                                # Check pages
                                for page in bm.get("pages", []):
                                    if page["id"] == target_id_cross:
                                        access_tokens[target_id_cross] = page.get("access_token", access_token)
                                        break
                                # Check Instagram accounts
                                for ig in bm.get("instagram_accounts", []):
                                    if ig["id"] == target_id_cross:
                                        # Instagram uses the connected page's token
                                        access_tokens[target_id_cross] = access_token
                                        break
                                break
                    else:
                        # Look in personal assets
                        for page in user.get("facebook_pages", []):
                            if page["id"] == target_id_cross:
                                access_tokens[target_id_cross] = page["access_token"]
                                break
                
                # Create Post object for cross-posting
                post_obj = Post(**post_data)
                
                # Cross-post to multiple platforms
                cross_results = await cross_post_to_meta(post_obj, access_tokens)
                
                successful_posts = [r for r in cross_results if r["status"] == "success"]
                failed_posts = [r for r in cross_results if r["status"] != "success"]
                
                if successful_posts:
                    post_data["status"] = "published"
                    post_data["published_at"] = datetime.utcnow()
                    post_data["cross_post_results"] = cross_results
                    print(f"✅ Cross-posted successfully to {len(successful_posts)} platforms")
                else:
                    post_data["status"] = "failed"
                    post_data["cross_post_results"] = cross_results
                    print("❌ All cross-posts failed")
                    
            else:
                # Single platform posting
                # Find the correct page access token
                page_access_token = access_token
                
                if business_manager_id:
                    for bm in user.get("business_managers", []):
                        if bm["id"] == business_manager_id:
                            # Check pages
                            for page in bm.get("pages", []):
                                if page["id"] == target_id:
                                    page_access_token = page.get("access_token", access_token)
                                    break
                            # Check Instagram accounts
                            for ig in bm.get("instagram_accounts", []):
                                if ig["id"] == target_id:
                                    page_access_token = access_token  # Instagram uses connected page token
                                    break
                            break
                else:
                    # Look in personal assets
                    for page in user.get("facebook_pages", []):
                        if page["id"] == target_id:
                            page_access_token = page["access_token"]
                            break
                
                # Create Post object
                post_obj = Post(**post_data)
                
                # Publish based on platform
                if platform == "instagram":
                    result = await post_to_instagram(post_obj, page_access_token)
                else:  # facebook (pages or groups)
                    result = await post_to_facebook(post_obj, page_access_token)
                
                if result and "id" in result:
                    post_data["status"] = "published"
                    post_data["published_at"] = datetime.utcnow()
                    post_data["platform_post_id"] = result["id"]
                    print(f"✅ Post published successfully to {platform} with ID: {result['id']}")
                    
                    # Add comment if comment_text or comment_link is provided (Facebook only)
                    comment_to_add = None
                    if comment_text and comment_text.strip():
                        comment_to_add = comment_text.strip()
                    elif comment_link and comment_link.strip():
                        comment_to_add = comment_link.strip()
                    
                    if comment_to_add and platform == "facebook":
                        print(f"Adding comment: {comment_to_add}")
                        comment_result = await add_comment_to_facebook_post(
                            result["id"], 
                            comment_to_add, 
                            page_access_token
                        )
                        
                        if comment_result and "id" in comment_result:
                            post_data["comment_status"] = "success"
                            print(f"✅ Comment added successfully with ID: {comment_result['id']}")
                        else:
                            post_data["comment_status"] = "failed"
                            print("❌ Failed to add comment to Facebook post")
                            
                else:
                    post_data["status"] = "failed"
                    print(f"❌ Failed to publish post to {platform}")
        
        # Save to database
        result = await db.posts.insert_one(post_data)
        post_data["_id"] = str(result.inserted_id)
        
        print(f"Post created with {len(link_metadata)} link metadata entries")
        
        # Return appropriate message based on status
        if post_data["status"] == "published":
            if cross_targets:
                successful_count = len([r for r in post_data.get("cross_post_results", []) if r["status"] == "success"])
                message = f"Cross-post créé avec succès sur {successful_count}/{len(cross_targets)} plateformes !"
            else:
                message = f"Post créé et publié avec succès sur {platform.title()} !"
                if (comment_text or comment_link) and post_data.get("comment_status") == "success":
                    message += " Commentaire ajouté !"
                elif (comment_text or comment_link) and post_data.get("comment_status") == "failed":
                    message += " Mais échec de l'ajout du commentaire."
        elif post_data["status"] == "scheduled":
            message = f"Post programmé avec succès pour {scheduled_dt.strftime('%Y-%m-%d %H:%M')}"
        else:
            message = f"Post créé mais échec de publication sur {platform}"
        
        return {"message": message, "post": post_data}
        
    except Exception as e:
        print(f"Error in create_post: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating post: {str(e)}")

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
            return {"message": f"Post published successfully on {platform}", "platform_id": result["id"]}
        else:
            await db.posts.update_one(
                {"id": post_id},
                {"$set": {"status": "failed"}}
            )
            raise HTTPException(status_code=400, detail=f"Failed to publish post on {platform}")
            
    except Exception as e:
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