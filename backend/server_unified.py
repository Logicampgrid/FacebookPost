from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse, RedirectResponse
from pydantic import BaseModel, field_validator, ValidationInfo
from typing import List, Optional
import os
import json
import uuid
import time
import threading
import subprocess
import signal
import requests
import asyncio
from datetime import datetime
import webbrowser
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Import database functions
from database import (
    connect_to_mongo, close_mongo_connection, 
    create_post, get_posts_by_user, update_post, get_post_by_id, delete_post,
    save_webhook_data, get_recent_webhooks,
    save_user_token, get_user_token, is_token_expired, refresh_facebook_token
)

# Charger les variables d'environnement
load_dotenv()

# === CONFIGURATION UNIFIÉE ===
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8001"))
FRONTEND_BUILD_PATH = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
NGROK_PROCESS = None
NGROK_URL = None

# === FACEBOOK/META CONFIGURATION ===
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
FACEBOOK_CLIENT_TOKEN = os.getenv("FACEBOOK_CLIENT_TOKEN")
FACEBOOK_GRAPH_URL = os.getenv("FACEBOOK_GRAPH_URL", "https://graph.facebook.com/v18.0")

def log_app(message: str, level: str = "INFO"):
    """Logging pour l'application"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "START": "🚀"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [UNIFIED] {message}")

def get_active_ngrok_url():
    """Récupère l'URL ngrok active via l'API locale"""
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        
        if response.status_code == 200:
            tunnels_data = response.json()
            tunnels = tunnels_data.get('tunnels', [])
            
            if tunnels:
                # Chercher le tunnel qui correspond à notre port backend
                for tunnel in tunnels:
                    config = tunnel.get('config', {})
                    if config.get('addr') == f"http://localhost:{BACKEND_PORT}":
                        public_url = tunnel.get('public_url')
                        if public_url:
                            log_app(f"✅ URL ngrok détectée: {public_url}", "SUCCESS")
                            return public_url
                
                # Si pas de tunnel spécifique trouvé, prendre le premier
                first_tunnel = tunnels[0]
                public_url = first_tunnel.get('public_url')
                if public_url:
                    log_app(f"✅ URL ngrok (premier tunnel): {public_url}", "SUCCESS")
                    return public_url
            
        log_app("⚠️ Aucun tunnel ngrok actif trouvé", "WARNING")
        return None
            
    except requests.exceptions.ConnectionError:
        log_app("⚠️ API ngrok non accessible", "WARNING")
        return None
    except Exception as e:
        log_app(f"❌ Erreur détection ngrok: {e}", "ERROR")
        return None

def start_ngrok():
    """Démarrer ngrok sur le port backend"""
    global NGROK_PROCESS, NGROK_URL
    
    try:
        # Vérifier si ngrok est déjà actif
        existing_url = get_active_ngrok_url()
        if existing_url:
            NGROK_URL = existing_url
            log_app(f"✅ Ngrok déjà actif: {existing_url}", "SUCCESS")
            return existing_url
        
        # Démarrer ngrok
        log_app(f"🚀 Démarrage ngrok sur port {BACKEND_PORT}...", "INFO")
        
        # Commande ngrok avec authentification si nécessaire
        ngrok_cmd = ["ngrok", "http", str(BACKEND_PORT)]
        
        # Ajouter le token d'authentification si disponible
        ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
        if ngrok_token:
            # Configurer le token d'authentification
            subprocess.run(["ngrok", "config", "add-authtoken", ngrok_token], 
                         capture_output=True, text=True)
            log_app("✅ Token ngrok configuré", "SUCCESS")
        
        # Démarrer ngrok en arrière-plan
        NGROK_PROCESS = subprocess.Popen(
            ngrok_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Attendre que ngrok démarre et récupérer l'URL
        time.sleep(3)
        
        for attempt in range(10):  # 10 tentatives sur 5 secondes
            ngrok_url = get_active_ngrok_url()
            if ngrok_url:
                NGROK_URL = ngrok_url
                log_app(f"✅ Ngrok démarré avec succès: {ngrok_url}", "SUCCESS")
                return ngrok_url
            time.sleep(0.5)
        
        log_app("❌ Impossible de récupérer l'URL ngrok", "ERROR")
        return None
        
    except FileNotFoundError:
        log_app("❌ Ngrok non trouvé - installez ngrok pour l'accès externe", "ERROR")
        return None
    except Exception as e:
        log_app(f"❌ Erreur démarrage ngrok: {e}", "ERROR")
        return None

def update_frontend_env_with_ngrok(ngrok_url):
    """Met à jour le .env frontend avec l'URL ngrok"""
    try:
        frontend_env_path = os.path.join(os.path.dirname(__file__), "..", "frontend", ".env")
        
        # Lire le fichier .env actuel
        env_content = {}
        if os.path.exists(frontend_env_path):
            with open(frontend_env_path, "r", encoding='utf-8') as f:
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        key, value = line.strip().split("=", 1)
                        env_content[key] = value
        
        # Mettre à jour l'URL backend
        env_content["REACT_APP_BACKEND_URL"] = ngrok_url
        
        # Réécrire le fichier
        with open(frontend_env_path, "w", encoding='utf-8') as f:
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")
        
        log_app(f"✅ Frontend .env mis à jour avec: {ngrok_url}", "SUCCESS")
        return True
        
    except Exception as e:
        log_app(f"❌ Erreur mise à jour frontend .env: {e}", "ERROR")
        return False

def build_frontend():
    """Construire le frontend React"""
    try:
        frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
        
        log_app("🔨 Construction du frontend React...", "INFO")
        
        # Vérifier si node_modules existe
        node_modules_path = os.path.join(frontend_dir, "node_modules")
        if not os.path.exists(node_modules_path):
            log_app("📦 Installation des dépendances...", "INFO")
            subprocess.run(["yarn", "install"], cwd=frontend_dir, check=True)
        
        # Construire le frontend
        result = subprocess.run(
            ["yarn", "build"], 
            cwd=frontend_dir, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            log_app("✅ Frontend construit avec succès", "SUCCESS")
            return True
        else:
            log_app(f"❌ Erreur construction frontend: {result.stderr}", "ERROR")
            return False
            
    except Exception as e:
        log_app(f"❌ Erreur construction frontend: {e}", "ERROR")
        return False

# === LIFESPAN CONTEXT MANAGER ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan events - startup and shutdown"""
    # Startup
    log_app("🚀 Démarrage de l'application unifiée Meta Publishing Platform", "START")
    
    # Connect to MongoDB
    mongo_connected = await connect_to_mongo()
    if not mongo_connected:
        log_app("⚠️ MongoDB non disponible - fonctionnement en mode limité", "WARNING")
    
    # Construire le frontend
    frontend_built = build_frontend()
    if not frontend_built:
        log_app("⚠️ Construction frontend échouée - API uniquement", "WARNING")
    
    # Démarrer ngrok
    ngrok_url = start_ngrok()
    if ngrok_url:
        # Mettre à jour le frontend .env avec l'URL ngrok
        update_frontend_env_with_ngrok(ngrok_url)
        log_app(f"🌍 Application accessible via: {ngrok_url}", "SUCCESS")
    else:
        log_app(f"🌐 Application locale uniquement: http://localhost:{BACKEND_PORT}", "INFO")
    
    yield  # Application runs here
    
    # Shutdown
    log_app("🛑 Arrêt de l'application...", "INFO")
    
    # Arrêter ngrok
    global NGROK_PROCESS
    if NGROK_PROCESS:
        try:
            NGROK_PROCESS.terminate()
            NGROK_PROCESS.wait(timeout=5)
            log_app("✅ Ngrok arrêté", "SUCCESS")
        except Exception as e:
            log_app(f"⚠️ Erreur arrêt ngrok: {e}", "WARNING")
    
    await close_mongo_connection()
    log_app("✅ Application arrêtée proprement!", "SUCCESS")

# === FASTAPI APP INITIALIZATION ===
app = FastAPI(
    title="Meta Publishing Platform - Configuration Unifiée",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Monter les fichiers statiques du build React
if os.path.exists(FRONTEND_BUILD_PATH):
    # Monter les fichiers statiques
    static_path = os.path.join(FRONTEND_BUILD_PATH, "static")
    if os.path.exists(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")
    
    # Route pour servir l'application React (catch-all)
    @app.get("/{path:path}")
    async def serve_react_app(path: str):
        """Servir l'application React pour toutes les routes non-API"""
        # Si c'est une route API, laisser FastAPI la gérer
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Servir les fichiers statiques demandés
        file_path = os.path.join(FRONTEND_BUILD_PATH, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Pour toutes les autres routes, servir index.html (SPA routing)
        index_path = os.path.join(FRONTEND_BUILD_PATH, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            return PlainTextResponse("Frontend not built. Run 'yarn build' in frontend directory.")

# === API ENDPOINTS ===

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "ngrok_url": NGROK_URL,
        "frontend_built": os.path.exists(FRONTEND_BUILD_PATH)
    }

@app.get("/api/config/ngrok-status")
async def ngrok_status():
    """Statut de la configuration ngrok"""
    return {
        "ngrok_active": NGROK_URL is not None,
        "ngrok_url": NGROK_URL,
        "backend_port": BACKEND_PORT,
        "frontend_built": os.path.exists(FRONTEND_BUILD_PATH),
        "timestamp": datetime.now().isoformat()
    }

# === ENDPOINTS D'AUTHENTIFICATION FACEBOOK ===

class FacebookAuthRequest(BaseModel):
    access_token: str

@app.post("/api/auth/facebook")
async def facebook_auth_endpoint(request: FacebookAuthRequest):
    """Authentification Facebook avec token d'accès"""
    try:
        access_token = request.access_token
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Token d'accès manquant")
        
        log_app("Authentification Facebook en cours...", "INFO")
        
        # Récupérer les informations utilisateur
        user_info_url = f"{FACEBOOK_GRAPH_URL}/me"
        user_params = {
            "fields": "id,name,email",
            "access_token": access_token
        }
        
        user_response = requests.get(user_info_url, params=user_params, timeout=15)
        user_response.raise_for_status()
        user_data = user_response.json()
        
        log_app(f"✅ Utilisateur connecté: {user_data.get('name', 'Unknown')}", "SUCCESS")
        
        # Récupérer les pages et business managers
        pages_url = f"{FACEBOOK_GRAPH_URL}/me/accounts"
        pages_params = {
            "fields": "id,name,access_token,category,instagram_business_account",
            "access_token": access_token
        }
        
        pages_response = requests.get(pages_url, params=pages_params, timeout=15)
        pages_response.raise_for_status()
        pages_data = pages_response.json()
        
        facebook_pages = pages_data.get("data", [])
        
        # Récupérer les business managers
        business_managers = []
        try:
            bm_url = f"{FACEBOOK_GRAPH_URL}/me/businesses"
            bm_params = {
                "fields": "id,name,owned_pages,owned_instagram_accounts",
                "access_token": access_token
            }
            bm_response = requests.get(bm_url, params=bm_params, timeout=15)
            if bm_response.status_code == 200:
                bm_data = bm_response.json()
                business_managers = bm_data.get("data", [])
        except Exception as e:
            log_app(f"⚠️ Erreur récupération Business Managers: {e}", "WARNING")
        
        # Sauvegarder le token utilisateur
        try:
            token_data = {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": 5400  # 90 minutes par défaut
            }
            await save_user_token(user_data["id"], token_data)
            log_app(f"✅ Token sauvegardé pour l'utilisateur {user_data.get('name')}", "SUCCESS")
        except Exception as e:
            log_app(f"⚠️ Erreur sauvegarde token: {e}", "WARNING")
        
        return {
            "success": True,
            "user": {
                "_id": user_data["id"],
                "id": user_data["id"],
                "name": user_data["name"],
                "email": user_data.get("email"),
                "facebook_pages": facebook_pages,
                "business_managers": business_managers
            },
            "total_pages": len(facebook_pages),
            "total_business_managers": len(business_managers)
        }
        
    except Exception as e:
        log_app(f"❌ Erreur authentification Facebook: {str(e)}", "ERROR")
        return {
            "success": False,
            "error": str(e)
        }

# === ENDPOINTS POUR LES POSTS ===

class PostBase(BaseModel):
    content: str
    platform: str
    platform_id: str
    scheduled_time: Optional[str] = None
    media_urls: Optional[List[str]] = []

@app.get("/api/posts")
async def get_posts(user_id: str):
    """Récupérer les posts d'un utilisateur"""
    try:
        posts = await get_posts_by_user(user_id)
        return {"success": True, "posts": posts}
    except Exception as e:
        log_app(f"❌ Erreur récupération posts: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/posts")
async def create_post_endpoint(request: PostBase, user_id: str):
    """Créer un nouveau post"""
    try:
        post_data = {
            "user_id": user_id,
            "content": request.content,
            "platform": request.platform,
            "platform_id": request.platform_id,
            "scheduled_time": request.scheduled_time,
            "media_urls": request.media_urls or [],
            "status": "draft",
            "created_at": datetime.now().isoformat()
        }
        
        post_id = await create_post(post_data)
        
        return {
            "success": True,
            "post_id": post_id,
            "message": "Post créé avec succès"
        }
        
    except Exception as e:
        log_app(f"❌ Erreur création post: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

# Servir la page d'accueil si pas de frontend build
@app.get("/")
async def root():
    """Page d'accueil"""
    if os.path.exists(FRONTEND_BUILD_PATH):
        index_path = os.path.join(FRONTEND_BUILD_PATH, "index.html")
        return FileResponse(index_path)
    else:
        return {
            "message": "Meta Publishing Platform - Configuration Unifiée",
            "status": "API active",
            "ngrok_url": NGROK_URL,
            "note": "Frontend non construit. Exécutez 'yarn build' dans le dossier frontend."
        }

if __name__ == "__main__":
    import uvicorn
    
    log_app(f"🚀 Démarrage du serveur sur le port {BACKEND_PORT}", "START")
    uvicorn.run(app, host="0.0.0.0", port=BACKEND_PORT, log_level="info")