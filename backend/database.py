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