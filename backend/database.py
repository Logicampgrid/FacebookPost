# Database configuration for MongoDB
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid

# MongoDB configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = "meta_platform"

class Database:
    client: AsyncIOMotorClient = None

# Database instance
db = Database()

async def connect_to_mongo():
    """Create database connection"""
    db.client = AsyncIOMotorClient(MONGO_URL)
    try:
        # Test the connection
        await db.client.admin.command('ismaster')
        print(f"✅ MongoDB connecté avec succès: {MONGO_URL}")
        return True
    except Exception as e:
        print(f"❌ Erreur connexion MongoDB: {e}")
        return False

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("✅ MongoDB déconnecté")

def get_database():
    """Get database instance"""
    return db.client[DATABASE_NAME]

# Collection helpers
async def get_posts_collection():
    """Get posts collection"""
    database = get_database()
    return database.posts

async def get_webhooks_collection():
    """Get webhooks collection"""
    database = get_database()
    return database.webhooks

async def get_users_collection():
    """Get users collection"""
    database = get_database()
    return database.users

# Post operations
async def create_post(post_data: dict) -> dict:
    """Create a new post in MongoDB"""
    posts_collection = await get_posts_collection()
    
    # Generate post ID if not provided
    if 'id' not in post_data:
        post_data['id'] = str(uuid.uuid4())
    
    # Add timestamps
    post_data['created_at'] = datetime.now().isoformat()
    if 'status' not in post_data:
        post_data['status'] = 'draft'
    
    try:
        result = await posts_collection.insert_one(post_data)
        post_data['_id'] = str(result.inserted_id)
        return post_data
    except Exception as e:
        print(f"❌ Erreur création post MongoDB: {e}")
        raise e

async def get_posts_by_user(user_id: str) -> list:
    """Get all posts for a user"""
    posts_collection = await get_posts_collection()
    
    try:
        cursor = posts_collection.find({"user_id": user_id})
        posts = []
        async for post in cursor:
            post['_id'] = str(post['_id'])
            posts.append(post)
        return posts
    except Exception as e:
        print(f"❌ Erreur récupération posts: {e}")
        return []

async def update_post(post_id: str, update_data: dict) -> dict:
    """Update a post"""
    posts_collection = await get_posts_collection()
    
    try:
        result = await posts_collection.update_one(
            {"id": post_id},
            {"$set": update_data}
        )
        if result.modified_count > 0:
            return await get_post_by_id(post_id)
        return None
    except Exception as e:
        print(f"❌ Erreur mise à jour post: {e}")
        return None

async def get_post_by_id(post_id: str) -> dict:
    """Get a post by ID"""
    posts_collection = await get_posts_collection()
    
    try:
        post = await posts_collection.find_one({"id": post_id})
        if post:
            post['_id'] = str(post['_id'])
        return post
    except Exception as e:
        print(f"❌ Erreur récupération post: {e}")
        return None

async def delete_post(post_id: str) -> bool:
    """Delete a post"""
    posts_collection = await get_posts_collection()
    
    try:
        result = await posts_collection.delete_one({"id": post_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"❌ Erreur suppression post: {e}")
        return False

# Webhook operations
async def save_webhook_data(webhook_data: dict) -> dict:
    """Save webhook data to MongoDB"""
    webhooks_collection = await get_webhooks_collection()
    
    # Add timestamp
    webhook_data['created_at'] = datetime.now().isoformat()
    webhook_data['id'] = str(uuid.uuid4())
    
    try:
        result = await webhooks_collection.insert_one(webhook_data)
        webhook_data['_id'] = str(result.inserted_id)
        return webhook_data
    except Exception as e:
        print(f"❌ Erreur sauvegarde webhook: {e}")
        raise e

async def get_recent_webhooks(limit: int = 50) -> list:
    """Get recent webhook data"""
    webhooks_collection = await get_webhooks_collection()
    
    try:
        cursor = webhooks_collection.find().sort("created_at", -1).limit(limit)
        webhooks = []
        async for webhook in cursor:
            webhook['_id'] = str(webhook['_id'])
            webhooks.append(webhook)
        return webhooks
    except Exception as e:
        print(f"❌ Erreur récupération webhooks: {e}")
        return []

# User token operations  
async def save_user_token(user_id: str, token_data: dict) -> dict:
    """Save or update user token data with expiration"""
    users_collection = await get_users_collection()
    
    # Calculate expiration timestamp
    expires_in = token_data.get("expires_in", 5400)  # Default 90 minutes
    expires_at = datetime.now().timestamp() + expires_in
    
    token_record = {
        "user_id": user_id,
        "access_token": token_data["access_token"],
        "token_type": token_data.get("token_type", "bearer"),
        "expires_at": expires_at,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    try:
        result = await users_collection.update_one(
            {"user_id": user_id},
            {"$set": token_record},
            upsert=True
        )
        return token_record
    except Exception as e:
        print(f"❌ Erreur sauvegarde token utilisateur: {e}")
        raise e

async def get_user_token(user_id: str) -> dict:
    """Get user token data"""
    users_collection = await get_users_collection()
    
    try:
        token_record = await users_collection.find_one({"user_id": user_id})
        if token_record:
            token_record['_id'] = str(token_record['_id'])
        return token_record
    except Exception as e:
        print(f"❌ Erreur récupération token utilisateur: {e}")
        return None

async def is_token_expired(user_id: str) -> bool:
    """Check if user token is expired"""
    token_record = await get_user_token(user_id)
    
    if not token_record:
        return True
    
    current_time = datetime.now().timestamp()
    expires_at = token_record.get("expires_at", 0)
    
    # Consider token expired if it expires in less than 10 minutes
    buffer_time = 600  # 10 minutes
    return current_time >= (expires_at - buffer_time)

async def refresh_facebook_token(user_id: str) -> dict:
    """Refresh Facebook token if needed"""
    try:
        token_record = await get_user_token(user_id)
        
        if not token_record:
            raise Exception("Aucun token trouvé pour cet utilisateur")
        
        # Check if token is expired or will expire soon
        if not await is_token_expired(user_id):
            return token_record  # Token is still valid
        
        # Refresh token using Facebook API
        current_token = token_record["access_token"]
        
        # Facebook long-lived token exchange
        refresh_url = f"https://graph.facebook.com/v18.0/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": os.getenv("FACEBOOK_APP_ID"),
            "client_secret": os.getenv("FACEBOOK_APP_SECRET"),
            "fb_exchange_token": current_token
        }
        
        import requests
        response = requests.get(refresh_url, params=params, timeout=30)
        response.raise_for_status()
        
        new_token_data = response.json()
        
        # Save the refreshed token
        refreshed_token = await save_user_token(user_id, new_token_data)
        
        print(f"✅ Token rafraîchi pour l'utilisateur {user_id}")
        return refreshed_token
        
    except Exception as e:
        print(f"❌ Erreur rafraîchissement token: {e}")
        raise e