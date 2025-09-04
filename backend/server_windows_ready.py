from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel, field_validator
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

# === CONFIGURATION DIRECTORIES - ADAPTÉS POUR WINDOWS ===
# Utilise le répertoire du script pour les uploads en local Windows
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
DOWNLOAD_DIR = os.path.join(UPLOAD_DIR, "downloaded")
OPTIMIZED_DIR = os.path.join(UPLOAD_DIR, "optimized")
PROCESSED_DIR = os.path.join(UPLOAD_DIR, "processed")
WORDPRESS_UPLOADS_DIR = os.path.join(BASE_DIR, "wordpress", "uploads")

# === FRONTEND BUILD DIRECTORY ===
FRONTEND_BUILD_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend", "build")

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
        print("🚀 Starting ngrok tunnel on port 8001...")
        
        # Try pyngrok first for Windows compatibility
        try:
            if NGROK_AUTH_TOKEN:
                ngrok.set_auth_token(NGROK_AUTH_TOKEN)
                print("🔑 Ngrok auth token configured")
            
            NGROK_TUNNEL = ngrok.connect(8001)
            NGROK_URL = NGROK_TUNNEL.public_url
            print(f"🌐 Ngrok tunnel active: {NGROK_URL}")
            
            # Save URL to file for reference
            ngrok_url_file = os.path.join(BASE_DIR, "ngrok_url.txt")
            with open(ngrok_url_file, "w") as f:
                f.write(NGROK_URL)
            print(f"💾 Ngrok URL saved to: {ngrok_url_file}")
            
            return NGROK_URL
            
        except Exception as pyngrok_error:
            print(f"❌ Pyngrok failed: {pyngrok_error}")
            print("🔧 Continuing without ngrok - backend will be available locally only")
        
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
    print("🚀 FacebookPost - Webhook Platform Starting...")
    print(f"📁 Upload directory: {UPLOAD_DIR}")
    print(f"🔧 Port: 8001")
    print(f"🔧 FACEBOOK_VERIFY_TOKEN: {os.getenv('FACEBOOK_VERIFY_TOKEN', 'NOT SET')}")
    
    # Start ngrok tunnel in background thread
    if ENABLE_NGROK:
        ngrok_thread = threading.Thread(target=start_ngrok_tunnel, daemon=True)
        ngrok_thread.start()
        # Give ngrok a moment to start
        await asyncio.sleep(2)
    
    print("✅ Application started successfully!")
    print("🔗 Webhook endpoints:")
    print("   GET  /api/webhook - Facebook verification")
    print("   POST /api/webhook - Facebook events")
    
    yield  # This is where the application runs
    
    # Shutdown
    print("🛑 Shutting down application...")
    if ENABLE_NGROK:
        stop_ngrok_tunnel()
    print("✅ Application shutdown complete!")

# === FASTAPI APP INITIALIZATION ===
app = FastAPI(
    title="FacebookPost - Webhook Platform",
    lifespan=lifespan
)

# Configuration flags
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

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

# === PYDANTIC MODELS ===
class PostCreate(BaseModel):
    content: str
    media_urls: Optional[List[str]] = []
    platform: str = "facebook"  # facebook, instagram, both
    page_id: Optional[str] = None
    
    @field_validator('platform')
    @classmethod
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
def log_webhook(message: str, level: str = "INFO"):
    """Structured logging for webhook operations"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "DEBUG": "🔍"}
    icon = icons.get(level.upper(), "📝")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] {message}")

# === API ENDPOINTS ===
@app.get("/api/health")
async def health_check():
    """Health check endpoint with webhook info"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "webhook_endpoint": "/api/webhook",
        "verify_token_configured": bool(os.getenv("FACEBOOK_VERIFY_TOKEN")),
        "ngrok": {
            "enabled": ENABLE_NGROK,
            "url": NGROK_URL,
            "tunnel_active": NGROK_TUNNEL is not None
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

@app.get("/api/webhook")
async def webhook_verify(request: Request):
    """
    Handle Facebook webhook verification (GET request)
    
    Facebook envoie une requête GET avec les paramètres:
    - hub.mode=subscribe
    - hub.verify_token=<votre_token>
    - hub.challenge=<challenge_string>
    
    Le serveur doit vérifier le token et retourner le challenge en texte plain
    """
    try:
        # === ÉTAPE 1: Récupération des paramètres de la requête ===
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token") 
        challenge = request.query_params.get("hub.challenge")
        
        # === ÉTAPE 2: Configuration du token depuis .env ===
        VERIFY_TOKEN = os.getenv("FACEBOOK_VERIFY_TOKEN", "mon_token_secret_webhook")
        
        # === ÉTAPE 3: Logging détaillé pour debug ===
        log_webhook("=== FACEBOOK WEBHOOK VERIFICATION ===", "DEBUG")
        log_webhook(f"Mode reçu: '{mode}'", "DEBUG")
        log_webhook(f"Token reçu: '{token}'", "DEBUG")
        log_webhook(f"Challenge reçu: '{challenge}'", "DEBUG")
        log_webhook(f"Token attendu: '{VERIFY_TOKEN}'", "DEBUG")
        log_webhook(f"URL complète: {request.url}", "DEBUG")
        
        # === ÉTAPE 4: Validation des paramètres requis ===
        if not mode or not token or not challenge:
            log_webhook("Paramètres manquants dans la requête", "ERROR")
            log_webhook(f"Détail: mode={mode}, token={token}, challenge={challenge}", "ERROR")
            raise HTTPException(
                status_code=400, 
                detail="Paramètres hub.mode, hub.verify_token et hub.challenge requis"
            )
        
        # === ÉTAPE 5: Vérification des conditions Facebook ===
        if mode == "subscribe" and token == VERIFY_TOKEN:
            log_webhook("Vérification réussie! Renvoi du challenge", "SUCCESS")
            log_webhook(f"Challenge retourné: '{challenge}'", "SUCCESS")
            
            # === ÉTAPE 6: CRITIQUE - Réponse en texte plain pour Facebook ===
            # Facebook EXIGE une réponse en texte pur, pas en JSON
            return PlainTextResponse(content=str(challenge), status_code=200)
        else:
            # === ÉTAPE 7: Gestion des échecs de vérification ===
            if mode != "subscribe":
                log_webhook(f"Mode incorrect: '{mode}' != 'subscribe'", "ERROR")
            if token != VERIFY_TOKEN:
                log_webhook(f"Token incorrect: '{token}' != '{VERIFY_TOKEN}'", "ERROR")
            
            raise HTTPException(status_code=403, detail="Verification failed")
            
    except HTTPException:
        # Re-lancer les HTTPException sans les wrapper
        raise
    except Exception as e:
        # === ÉTAPE 8: Gestion des erreurs inattendues ===
        error_msg = f"Erreur interne webhook GET: {str(e)}"
        log_webhook(error_msg, "ERROR")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/webhook")
async def webhook_handler(request: Request):
    """
    Handle Facebook webhook events (POST request)
    
    Facebook envoie des événements via POST avec du JSON contenant:
    - object: "page"
    - entry: liste des événements
    
    Le serveur doit traiter les événements et retourner {"status": "received"}
    """
    try:
        # === ÉTAPE 1: Récupération du body de la requête ===
        body = await request.body()
        log_webhook("Événement POST webhook reçu", "INFO")
        
        # === ÉTAPE 2: Parse du JSON ===
        try:
            webhook_data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            log_webhook("JSON invalide dans la requête webhook", "ERROR")
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        # === ÉTAPE 3: Logging de l'événement reçu ===
        log_webhook("Contenu webhook:", "DEBUG")
        log_webhook(json.dumps(webhook_data, indent=2), "DEBUG")
        
        # === ÉTAPE 4: Traitement des événements Facebook ===
        if webhook_data.get("object") == "page":
            entries = webhook_data.get("entry", [])
            log_webhook(f"Traitement de {len(entries)} entrée(s)", "INFO")
            
            for entry in entries:
                # Gestion des messages
                if "messaging" in entry:
                    for messaging_event in entry["messaging"]:
                        sender_id = messaging_event.get("sender", {}).get("id")
                        message = messaging_event.get("message", {})
                        
                        if message:
                            text = message.get('text', 'Pas de texte')
                            log_webhook(f"Message de {sender_id}: {text}", "INFO")
                            
                            # Gestion des pièces jointes
                            if "attachments" in message:
                                for attachment in message["attachments"]:
                                    attachment_type = attachment.get("type")
                                    payload = attachment.get("payload", {})
                                    url = payload.get("url")
                                    log_webhook(f"Pièce jointe: {attachment_type} - {url}", "INFO")
                
                # Gestion des changements de page
                if "changes" in entry:
                    for change in entry["changes"]:
                        field = change.get("field")
                        value = change.get("value", {})
                        log_webhook(f"Changement page: {field} - {value}", "INFO")
        else:
            log_webhook(f"Type d'objet non géré: {webhook_data.get('object')}", "WARNING")
        
        # === ÉTAPE 5: Réponse de confirmation pour Facebook ===
        log_webhook("Événement traité avec succès", "SUCCESS")
        return {"status": "received"}
        
    except HTTPException:
        # Re-lancer les HTTPException sans les wrapper
        raise
    except Exception as e:
        error_msg = f"Erreur traitement webhook POST: {str(e)}"
        log_webhook(error_msg, "ERROR")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/posts", response_model=PostResponse)
async def create_post(post: PostCreate):
    """Create a new social media post"""
    try:
        # Generate post ID
        post_id = str(uuid.uuid4())
        
        # Create post document
        post_doc = {
            "_id": post_id,
            "content": post.content,
            "media_urls": post.media_urls,
            "platform": post.platform,
            "status": "created",
            "created_at": datetime.utcnow(),
            "facebook_post_id": None,
            "instagram_post_id": None
        }
        
        # Save to database
        await db.posts.insert_one(post_doc)
        
        # Convert for response
        post_doc["id"] = post_doc["_id"]
        del post_doc["_id"]
        
        return PostResponse(**post_doc)
        
    except Exception as e:
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
        raise HTTPException(status_code=500, detail=str(e))

# === FRONTEND ROUTES ===
@app.get("/")
async def serve_root():
    """Serve React app at root"""
    if not frontend_build_available:
        return {"message": "FacebookPost Backend", "status": "running", "webhook": "/api/webhook"}
    
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
    
    # If frontend build is not available, return info
    if not frontend_build_available:
        return {"message": "FacebookPost Backend", "status": "running", "info": f"Path: {path}"}
    
    # Try to serve specific file first (for assets like favicon.ico, manifest.json, etc.)
    file_path = os.path.join(FRONTEND_BUILD_DIR, path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # For SPA routing, serve index.html for all other routes
    index_path = os.path.join(FRONTEND_BUILD_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"message": "FacebookPost Backend", "status": "running", "spa_path": path}

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Démarrage FacebookPost Backend")
    print("📍 Serveur: http://localhost:8001")
    print("🔗 Webhook: http://localhost:8001/api/webhook")
    print("💡 Santé: http://localhost:8001/api/health")
    
    # Start ngrok tunnel before starting server if enabled
    if ENABLE_NGROK:
        start_ngrok_tunnel()
    
    uvicorn.run(app, host="0.0.0.0", port=8001)