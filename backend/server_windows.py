from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request, Body
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
import threading
import signal
import webbrowser

# Load environment variables
load_dotenv()

# === WINDOWS CONFIGURATION ===
WINDOWS_PATHS = {
    "backend_dir": "C:\\FacebookPost\\backend",
    "frontend_dir": "C:\\FacebookPost\\frontend", 
    "upload_dir": "C:\\FacebookPost\\backend\\uploads",
    "download_dir": "C:\\FacebookPost\\backend\\uploads\\downloaded",
    "optimized_dir": "C:\\FacebookPost\\backend\\uploads\\optimized",
    "processed_dir": "C:\\FacebookPost\\backend\\uploads\\processed",
    "wordpress_uploads": "C:\\FacebookPost\\backend\\wordpress\\uploads",
    "frontend_build": "C:\\FacebookPost\\frontend\\build",
    "logs_dir": "C:\\FacebookPost\\logs",
    "ngrok_url_file": "C:\\FacebookPost\\backend\\ngrok_url.txt",
    "frontend_env": "C:\\FacebookPost\\frontend\\.env"
}

# === NGROK CONFIGURATION ===
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")  # Optional for free version
ENABLE_NGROK = os.getenv("ENABLE_NGROK", "true").lower() == "true"
NGROK_TUNNEL = None
NGROK_URL = None
NGROK_PROCESS = None

# Server configuration
BACKEND_PORT = 8001
FRONTEND_PORT = 3000

# === LOGGING SETUP ===
def setup_logging():
    """Setup logging for Windows"""
    try:
        os.makedirs(WINDOWS_PATHS["logs_dir"], exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(WINDOWS_PATHS["logs_dir"], f"backend_{timestamp}.log")
        
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.info(f"Logging configuré : {log_file}")
        return logger
        
    except Exception as e:
        print(f"❌ Erreur configuration logging: {e}")
        return None

logger = setup_logging()

def log_app(message: str, level: str = "INFO"):
    """Application logging avec horodatage"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "START": "🚀"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted_msg = f"{icon} [{timestamp}] {message}"
    print(formatted_msg)
    
    if logger:
        if level.upper() == "ERROR":
            logger.error(message)
        elif level.upper() == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)

# === DIRECTORY SETUP ===
def ensure_windows_directories():
    """Créer toutes les répertoires nécessaires sur Windows"""
    try:
        log_app("Création des répertoires Windows...", "START")
        
        directories = [
            WINDOWS_PATHS["backend_dir"],
            WINDOWS_PATHS["frontend_dir"],
            WINDOWS_PATHS["upload_dir"],
            WINDOWS_PATHS["download_dir"],
            WINDOWS_PATHS["optimized_dir"],
            WINDOWS_PATHS["processed_dir"],
            WINDOWS_PATHS["wordpress_uploads"],
            WINDOWS_PATHS["logs_dir"]
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                log_app(f"Répertoire créé/vérifié: {directory}", "SUCCESS")
            except Exception as e:
                log_app(f"Erreur création {directory}: {e}", "ERROR")
                raise
                
        return True
        
    except Exception as e:
        log_app(f"Erreur critique création répertoires: {e}", "ERROR")
        return False

def check_frontend_build():
    """Vérifier si le build frontend existe"""
    build_path = WINDOWS_PATHS["frontend_build"]
    if os.path.exists(build_path):
        log_app(f"Build frontend trouvé: {build_path}", "SUCCESS")
        return True
    else:
        log_app(f"Build frontend manquant: {build_path}", "WARNING")
        log_app("Exécutez 'npm run build' dans le frontend", "INFO")
        return False

# Initialisation des répertoires
directories_ok = ensure_windows_directories()
frontend_build_available = check_frontend_build()

if not directories_ok:
    log_app("Impossible de créer les répertoires, arrêt du serveur", "ERROR")
    sys.exit(1)

# === NGROK FUNCTIONS FOR WINDOWS ===
def kill_existing_ngrok():
    """Tuer tous les processus ngrok existants sur Windows"""
    try:
        log_app("Arrêt des processus ngrok existants...", "INFO")
        subprocess.run(["taskkill", "/F", "/IM", "ngrok.exe"], 
                      capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        time.sleep(2)
    except Exception as e:
        log_app(f"Erreur arrêt ngrok: {e}", "WARNING")

def start_ngrok_tunnel_windows():
    """Démarrer tunnel ngrok optimisé pour Windows"""
    global NGROK_TUNNEL, NGROK_URL, NGROK_PROCESS
    
    if not ENABLE_NGROK:
        log_app("Ngrok désactivé (ENABLE_NGROK=false)", "INFO")
        return None
        
    try:
        log_app("🚀 Démarrage tunnel ngrok Windows...", "START")
        
        # Tuer processus existants
        kill_existing_ngrok()
        
        # Démarrer ngrok en arrière-plan
        ngrok_cmd = ["ngrok", "http", str(BACKEND_PORT), "--log=stdout"]
        
        log_app(f"Commande ngrok: {' '.join(ngrok_cmd)}", "INFO")
        
        NGROK_PROCESS = subprocess.Popen(
            ngrok_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        log_app("Processus ngrok démarré, attente de l'URL...", "INFO")
        
        # Attendre que ngrok soit prêt avec timeout intelligent
        max_attempts = 45  # 45 secondes pour être sûr
        for attempt in range(max_attempts):
            try:
                time.sleep(1)
                
                # Vérifier API ngrok
                response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
                if response.status_code == 200:
                    tunnels = response.json()
                    if tunnels.get('tunnels') and len(tunnels['tunnels']) > 0:
                        tunnel = tunnels['tunnels'][0]
                        public_url = tunnel.get('public_url', '')
                        
                        # Valider l'URL
                        if public_url and public_url.startswith('https://') and 'ngrok' in public_url:
                            NGROK_URL = public_url
                            log_app(f"🌐 Tunnel ngrok actif: {NGROK_URL}", "SUCCESS")
                            
                            # Sauvegarder URL dans fichier
                            save_ngrok_url_to_files(NGROK_URL)
                            
                            return NGROK_URL
                        else:
                            log_app(f"URL ngrok invalide reçue: {public_url}", "WARNING")
                            continue
                        
            except requests.exceptions.RequestException as e:
                if attempt < 10:  # Logs moins verbeux les premières secondes
                    pass
                else:
                    log_app(f"Tentative {attempt + 1}/{max_attempts} - API ngrok: {str(e)}", "INFO")
                continue
                
        # Timeout atteint
        log_app("❌ Timeout: ngrok n'a pas pu créer l'URL dans les temps", "ERROR")
        
        # Essayer de tuer le processus si échoué
        if NGROK_PROCESS:
            try:
                NGROK_PROCESS.terminate()
                NGROK_PROCESS = None
            except:
                pass
                
        return None
        
    except Exception as e:
        log_app(f"❌ Erreur démarrage ngrok: {e}", "ERROR")
        return None

def save_ngrok_url_to_files(url: str):
    """Sauvegarder l'URL ngrok dans les fichiers de configuration"""
    try:
        # Sauvegarder dans fichier backend
        with open(WINDOWS_PATHS["ngrok_url_file"], "w", encoding='utf-8') as f:
            f.write(url)
        log_app(f"URL sauvée: {WINDOWS_PATHS['ngrok_url_file']}", "SUCCESS")
        
        # Mettre à jour le .env frontend
        update_frontend_env(url)
        
    except Exception as e:
        log_app(f"Erreur sauvegarde URL: {e}", "ERROR")

def update_frontend_env(ngrok_url: str):
    """Mettre à jour le fichier .env du frontend avec l'URL ngrok"""
    try:
        env_path = WINDOWS_PATHS["frontend_env"]
        
        # Lire le .env existant
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding='utf-8') as f:
                lines = f.readlines()
        
        # Mettre à jour REACT_APP_BACKEND_URL
        updated_lines = []
        backend_url_updated = False
        
        for line in lines:
            if line.startswith("REACT_APP_BACKEND_URL="):
                updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}\n")
                backend_url_updated = True
            else:
                updated_lines.append(line)
        
        # Ajouter la ligne si elle n'existe pas
        if not backend_url_updated:
            updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}\n")
        
        # Écrire le fichier mis à jour
        with open(env_path, "w", encoding='utf-8') as f:
            f.writelines(updated_lines)
            
        log_app(f"Frontend .env mis à jour: {ngrok_url}", "SUCCESS")
        
    except Exception as e:
        log_app(f"Erreur mise à jour frontend .env: {e}", "WARNING")

def stop_ngrok_tunnel():
    """Arrêter le tunnel ngrok proprement"""
    global NGROK_PROCESS, NGROK_URL
    
    try:
        if NGROK_PROCESS:
            log_app("Arrêt du tunnel ngrok...", "INFO")
            NGROK_PROCESS.terminate()
            NGROK_PROCESS.wait(timeout=5)
            NGROK_PROCESS = None
            NGROK_URL = None
            log_app("Tunnel ngrok arrêté", "SUCCESS")
    except Exception as e:
        log_app(f"Erreur arrêt ngrok: {e}", "WARNING")
        kill_existing_ngrok()

def open_browser_when_ready():
    """Ouvrir le navigateur une fois que l'URL ngrok est disponible"""
    def wait_and_open():
        max_wait = 60  # 60 secondes
        start_time = time.time()
        
        log_app("Attente de l'URL ngrok pour ouvrir le navigateur...", "INFO")
        
        while time.time() - start_time < max_wait:
            if NGROK_URL:
                try:
                    log_app(f"🌐 Ouverture du navigateur: {NGROK_URL}", "SUCCESS")
                    webbrowser.open(NGROK_URL)
                    return
                except Exception as e:
                    log_app(f"Erreur ouverture navigateur: {e}", "WARNING")
                    return
            time.sleep(2)
        
        log_app("⚠️ Timeout: URL ngrok non disponible après 60s", "WARNING")
        log_app("💡 Ouvrez manuellement http://localhost:8001 ou vérifiez ngrok", "INFO")
    
    # Lancer dans un thread séparé
    browser_thread = threading.Thread(target=wait_and_open, daemon=True)
    browser_thread.start()

# === LIFESPAN CONTEXT MANAGER ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan events - startup and shutdown"""
    # Startup
    log_app("🚀 Meta Publishing Platform - Version Windows", "START")
    log_app(f"📁 Répertoire backend: {WINDOWS_PATHS['backend_dir']}", "INFO")
    log_app(f"🌐 Port backend: {BACKEND_PORT}", "INFO")
    log_app(f"🔧 Mode DRY_RUN: {os.getenv('DRY_RUN', 'false')}", "INFO")
    
    # Démarrer ngrok en arrière-plan
    if ENABLE_NGROK:
        ngrok_thread = threading.Thread(target=start_ngrok_tunnel_windows, daemon=True)
        ngrok_thread.start()
        
        # Ouvrir le navigateur une fois ngrok prêt
        open_browser_when_ready()
    
    log_app("✅ Application démarrée avec succès!", "SUCCESS")
    
    yield  # Application running
    
    # Shutdown
    log_app("🛑 Arrêt de l'application...", "INFO")
    if ENABLE_NGROK:
        stop_ngrok_tunnel()
    log_app("✅ Arrêt terminé!", "SUCCESS")

# === FASTAPI APP INITIALIZATION ===
app = FastAPI(
    title="Meta Publishing Platform - Windows Version",
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
if frontend_build_available:
    app.mount("/static", StaticFiles(directory=f"{WINDOWS_PATHS['frontend_build']}\\static"), name="static")
    log_app("✅ Fichiers statiques frontend montés", "SUCCESS")
else:
    log_app("⚠️ Build frontend non disponible", "WARNING")

# === DATABASE SETUP ===
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.meta_posts

log_app(f"🗄️ MongoDB configuré: {MONGO_URL}", "INFO")

# === FACEBOOK/META CONFIGURATION ===
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
FACEBOOK_GRAPH_URL = os.getenv("FACEBOOK_GRAPH_URL", "https://graph.facebook.com/v18.0")

# === CONFIGURATION BOUTIQUES MULTI-PLATFORM ===
PUBLICATION_TEST_MODE = os.getenv("PUBLICATION_TEST_MODE", "true").lower() == "true"

# Configuration des boutiques (même structure que l'original)
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

# === FTP CONFIGURATION ===
FTP_HOST = os.getenv("FTP_HOST", "logicamp.org")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER", "logi")
FTP_PASSWORD = os.getenv("FTP_PASSWORD", "logi")
FTP_DIRECTORY = os.getenv("FTP_DIRECTORY", "/wordpress/uploads/")
FTP_BASE_URL = os.getenv("FTP_BASE_URL", "https://logicamp.org/wordpress/uploads/")

# === HEALTH CHECK ENDPOINT ===
@app.get("/api/health")
async def health_check():
    """Health check avec informations Windows et ngrok"""
    from fastapi.responses import JSONResponse
    
    try:
        # Vérifier MongoDB
        await client.admin.command('ping')
        mongo_status = "connected"
    except Exception:
        mongo_status = "disconnected"
    
    response_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "platform": "Windows",
        "backend_port": BACKEND_PORT,
        "directories": {
            "backend": WINDOWS_PATHS["backend_dir"],
            "frontend": WINDOWS_PATHS["frontend_dir"],
            "uploads": WINDOWS_PATHS["upload_dir"]
        },
        "services": {
            "mongodb": mongo_status,
            "ngrok": {
                "enabled": ENABLE_NGROK,
                "active": NGROK_URL is not None,
                "url": NGROK_URL
            }
        },
        "frontend": {
            "build_available": frontend_build_available,
            "build_path": WINDOWS_PATHS["frontend_build"]
        },
        "stores": {name: bool(config.get("access_token")) for name, config in STORES.items()},
        "publication": {
            "test_mode": PUBLICATION_TEST_MODE
        }
    }
    
    return JSONResponse(content=response_data, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "*"
    })

@app.get("/api/ngrok-url")
async def get_ngrok_url():
    """Endpoint pour récupérer l'URL ngrok actuelle"""
    from fastapi.responses import JSONResponse
    
    response_data = {
        "ngrok_enabled": ENABLE_NGROK,
        "ngrok_url": NGROK_URL,
        "ngrok_active": NGROK_URL is not None
    }
    
    return JSONResponse(content=response_data, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "*"
    })

# === FRONTEND ROUTES ===
@app.get("/")
async def serve_root():
    """Servir l'application React à la racine"""
    if not frontend_build_available:
        return {"error": "Frontend non compilé. Exécutez 'npm run build' dans C:\\FacebookPost\\frontend"}
    
    index_path = os.path.join(WINDOWS_PATHS["frontend_build"], "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        raise HTTPException(status_code=404, detail="Frontend index.html non trouvé")

# Catch-all route pour SPA
@app.get("/{path:path}")
async def serve_frontend(path: str):
    """Servir le frontend React pour toutes les routes non-API"""
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Endpoint API non trouvé")
    
    if not frontend_build_available:
        return {"error": "Frontend non compilé. Exécutez 'npm run build' dans C:\\FacebookPost\\frontend"}
    
    # Servir fichier spécifique s'il existe
    file_path = os.path.join(WINDOWS_PATHS["frontend_build"], path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Sinon servir index.html pour le routing SPA
    index_path = os.path.join(WINDOWS_PATHS["frontend_build"], "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        raise HTTPException(status_code=404, detail="Frontend index.html non trouvé")

# === PYDANTIC MODELS FOR AUTHENTICATION ===
class FacebookAuthRequest(BaseModel):
    code: str
    store: str
    redirect_uri: str

class FacebookExchangeCodeRequest(BaseModel):
    code: str
    state: Optional[str] = None
    store: Optional[str] = None
    redirect_uri: Optional[str] = "http://localhost:3000/auth/callback"
    
    @validator('store', pre=True, always=True)
    def set_store_from_state(cls, v, values):
        """Map state to store if store is not provided"""
        if v is None and 'state' in values and values['state']:
            return values['state']
        return v or "default"
    
    @validator('redirect_uri', pre=True, always=True) 
    def set_default_redirect_uri(cls, v):
        """Set default redirect_uri if not provided"""
        return v or "http://localhost:3000/auth/callback"

class FacebookAuthResponse(BaseModel):
    success: bool
    store: str
    access_token: Optional[str] = None
    fb_page_id: Optional[str] = None
    ig_user_id: Optional[str] = None
    error: Optional[str] = None

# === AUTHENTICATION FUNCTIONS ===
async def exchange_facebook_code(code: str, redirect_uri: str) -> dict:
    """Échange un code d'autorisation Facebook contre un access token"""
    try:
        log_app(f"Échange du code d'autorisation Facebook", "INFO")
        
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
        
        log_app("Requête d'échange de token...", "INFO")
        response = requests.get(token_url, params=token_params, timeout=30)
        response.raise_for_status()
        
        token_data = response.json()
        
        if "access_token" not in token_data:
            raise Exception(f"Token non reçu: {token_data}")
        
        access_token = token_data["access_token"]
        log_app("Access token reçu avec succès", "SUCCESS")
        
        # Étape 2: Obtenir les informations utilisateur et ses pages
        user_url = f"{FACEBOOK_GRAPH_URL}/me"
        user_params = {
            'access_token': access_token,
            'fields': 'id,name,accounts'
        }
        
        user_response = requests.get(user_url, params=user_params, timeout=30)
        user_response.raise_for_status()
        user_data = user_response.json()
        
        log_app(f"Utilisateur: {user_data.get('name', 'Inconnu')}", "INFO")
        
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
        log_app(f"Trouvé {len(pages)} page(s) gérée(s)", "INFO")
        
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
                    log_app(f"Page '{page.get('name')}' a un compte Instagram: {ig_account.get('id')}", "INFO")
                else:
                    log_app(f"Page '{page.get('name')}' n'a pas de compte Instagram", "WARNING")
            
            result["pages"].append(page_info)
        
        log_app("Authentification Facebook réussie", "SUCCESS")
        return result
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Erreur HTTP lors de l'authentification: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_msg += f" - {error_data}"
            except:
                error_msg += f" - Status: {e.response.status_code}"
        log_app(error_msg, "ERROR")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Erreur authentification: {str(e)}"
        log_app(error_msg, "ERROR")
        raise Exception(error_msg)

def save_store_tokens(store: str, page_id: str, page_access_token: str, ig_user_id: str = None):
    """Sauvegarde les tokens d'un store"""
    global STORES
    
    log_app(f"Sauvegarde tokens pour {store}", "INFO")
    
    # Mettre à jour la configuration du store
    STORES[store].update({
        "fb_page_id": page_id,
        "access_token": page_access_token,
        "ig_user_id": ig_user_id
    })
    
    log_app(f"Tokens sauvegardés: Page={page_id}, Instagram={ig_user_id}", "SUCCESS")

# === AUTHENTICATION ENDPOINTS ===
@app.post("/api/auth/facebook/exchange-code")
async def exchange_facebook_code_endpoint(request: FacebookExchangeCodeRequest):
    """Échange un code d'autorisation Facebook - Accepte JSON avec code/state ou code/store et retourne access_token"""
    try:
        # Log des données reçues pour debug
        log_app(f"Code exchange reçu - Store: {request.store}, Code: {request.code[:10]}...", "INFO")
        if request.state:
            log_app(f"State reçu: {request.state} (mappé vers store: {request.store})", "INFO")
        log_app(f"Redirect URI: {request.redirect_uri}", "INFO")
        
        # VALIDATION: Configuration Facebook requise
        if not FACEBOOK_APP_ID or not FACEBOOK_APP_SECRET:
            log_app("Configuration Facebook manquante", "ERROR")
            return {
                "success": False,
                "error": "Configuration Facebook manquante (FACEBOOK_APP_ID ou FACEBOOK_APP_SECRET)",
                "test_mode": True,
                "data": {
                    "code": request.code[:10] + "...",
                    "state": request.state,
                    "store": request.store,
                    "redirect_uri": request.redirect_uri
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            # VRAIE AUTHENTIFICATION FACEBOOK
            auth_result = await exchange_facebook_code(request.code, request.redirect_uri)
            
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
                    "data": {
                        "code": request.code[:10] + "...",
                        "state": request.state,
                        "store": request.store,
                        "redirect_uri": request.redirect_uri
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Prendre la première page disponible
            selected_page = pages[0]
            page_id = selected_page["page_id"]
            page_access_token = selected_page["page_access_token"]
            ig_user_id = selected_page.get("instagram_business_account")
            
            # Sauvegarder les tokens pour ce store si ce n'est pas "default"
            if request.store != "default" and request.store in STORES:
                save_store_tokens(request.store, page_id, page_access_token, ig_user_id)
                log_app(f"Tokens sauvegardés pour le store: {request.store}", "SUCCESS")
            
            # SUCCÈS - Retourner l'access token
            return {
                "success": True,
                "message": "Authentification Facebook réussie",
                "access_token": page_access_token,
                "fb_page_id": page_id,
                "ig_user_id": ig_user_id,
                "store": request.store,
                "user_info": {
                    "user_id": auth_result.get("user_id"),
                    "user_name": auth_result.get("user_name"),
                    "total_pages": len(pages)
                },
                "data": {
                    "code": request.code[:10] + "...",
                    "state": request.state,
                    "store": request.store,
                    "redirect_uri": request.redirect_uri
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as facebook_error:
            # Erreur lors de l'échange Facebook
            log_app(f"Erreur échange Facebook: {str(facebook_error)}", "ERROR")
            return {
                "success": False,
                "error": f"Erreur Facebook OAuth: {str(facebook_error)}",
                "data": {
                    "code": request.code[:10] + "...",
                    "state": request.state,
                    "store": request.store,
                    "redirect_uri": request.redirect_uri
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        
    except Exception as e:
        error_msg = f"Erreur exchange-code: {str(e)}"
        log_app(error_msg, "ERROR")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/auth/facebook/exchange-code-legacy", response_model=FacebookAuthResponse)
async def exchange_facebook_code_legacy(request: FacebookAuthRequest):
    """Ancien endpoint pour compatibilité (utilise store et redirect_uri)"""
    try:
        log_app(f"Demande d'authentification legacy pour le store: {request.store}", "INFO")
        
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
        selected_page = pages[0]
        
        page_id = selected_page["page_id"]
        page_access_token = selected_page["page_access_token"]
        ig_user_id = selected_page.get("instagram_business_account")
        
        # Sauvegarder les tokens pour ce store
        save_store_tokens(request.store, page_id, page_access_token, ig_user_id)
        
        log_app(f"Authentification legacy réussie pour {request.store}", "SUCCESS")
        
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
        log_app(error_msg, "ERROR")
        return FacebookAuthResponse(
            success=False,
            store=request.store,
            error=error_msg
        )

# === WEBHOOK HANDLERS ===
@app.get("/api/webhook")
async def webhook_verify(request: Request):
    """Handle Facebook webhook verification (GET request)"""
    try:
        # Récupération des paramètres de requête Facebook
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token") 
        challenge = request.query_params.get("hub.challenge")
        
        # Token de vérification depuis .env
        VERIFY_TOKEN = os.getenv("FACEBOOK_VERIFY_TOKEN", "mon_token_secret_webhook")
        
        log_app(f"Webhook verification - mode: {mode}, token: {token}", "INFO")
        
        if not mode or not token or not challenge:
            log_app("Paramètres manquants dans la requête webhook", "ERROR")
            raise HTTPException(
                status_code=400, 
                detail="Paramètres hub.mode, hub.verify_token et hub.challenge requis"
            )
        
        if mode == "subscribe" and token == VERIFY_TOKEN:
            log_app("✅ Webhook verification successful!", "SUCCESS")
            return PlainTextResponse(content=str(challenge), status_code=200)
        else:
            log_app(f"Vérification échouée - Mode: {mode}, Token attendu: {VERIFY_TOKEN}", "ERROR")
            raise HTTPException(status_code=403, detail="Token de vérification invalide")
            
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Erreur interne webhook: {str(e)}"
        log_app(error_detail, "ERROR")
        raise HTTPException(status_code=500, detail=error_detail)

@app.post("/api/webhook")
async def webhook_handler(request: Request):
    """Handle Facebook webhook events (POST request)"""
    try:
        body = await request.body()
        content_type = request.headers.get("content-type", "").lower()
        
        log_app(f"Webhook reçu: {len(body)} bytes, type: {content_type}", "INFO")
        
        # Traitement selon le type de contenu
        if "application/json" in content_type or "text/" in content_type:
            try:
                webhook_data = json.loads(body.decode('utf-8'))
                log_app(f"Webhook JSON reçu: {json.dumps(webhook_data, indent=2)}", "INFO")
                
                # Process Facebook webhook data
                if webhook_data.get("object") == "page":
                    entries = webhook_data.get("entry", [])
                    for entry in entries:
                        log_app(f"Processing entry: {entry.get('id', 'unknown')}", "INFO")
                        
            except json.JSONDecodeError:
                log_app("Impossible de décoder le JSON webhook", "WARNING")
        
        return {"status": "received", "timestamp": datetime.utcnow()}
        
    except Exception as e:
        log_app(f"Erreur traitement webhook: {e}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/facebook")
async def authenticate_facebook(request: Request):
    """Authentification Facebook avec token d'accès direct"""
    try:
        data = await request.json()
        access_token = data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Token d'accès requis")
            
        log_app("Authentification Facebook avec token direct", "INFO")
        
        # Récupérer les informations utilisateur
        user_url = f"{FACEBOOK_GRAPH_URL}/me"
        user_params = {
            'access_token': access_token,
            'fields': 'id,name,accounts{id,name,access_token,instagram_business_account},business_users{business{id,name}}'
        }
        
        response = requests.get(user_url, params=user_params, timeout=30)
        response.raise_for_status()
        user_data = response.json()
        
        log_app(f"Utilisateur connecté: {user_data.get('name')}", "SUCCESS")
        
        return {
            "success": True,
            "user": user_data,
            "message": "Authentification réussie"
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Erreur API Facebook: {str(e)}"
        log_app(error_msg, "ERROR")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = f"Erreur authentification: {str(e)}"
        log_app(error_msg, "ERROR")
        raise HTTPException(status_code=500, detail=error_msg)

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

# === PUBLICATION ENDPOINTS ===
class PublishRequest(BaseModel):
    store: str
    message: str
    product_url: str
    image_url: Optional[str] = None
    platforms: List[str] = ["facebook", "instagram"]

@app.post("/api/publish")
async def publish_post_endpoint(request: PublishRequest):
    """Publier un post sur les plateformes sélectionnées"""
    try:
        log_app(f"Demande de publication pour {request.store} sur {request.platforms}", "INFO")
        
        if request.store not in STORES:
            raise HTTPException(status_code=400, detail=f"Store '{request.store}' inconnu")
        
        # Simulation en mode test
        if PUBLICATION_TEST_MODE:
            log_app(f"MODE TEST - Publication simulée pour {request.store}", "INFO")
            return {
                "success": True,
                "store": request.store,
                "platforms": request.platforms,
                "test_mode": True,
                "message": "Publication simulée en mode test",
                "facebook_result": {"id": f"test_fb_{uuid.uuid4().hex[:8]}", "message": request.message} if "facebook" in request.platforms else None,
                "instagram_result": {"id": f"test_ig_{uuid.uuid4().hex[:8]}", "caption": request.message} if "instagram" in request.platforms else None
            }
        
        # TODO: Implémenter la publication réelle
        log_app("Publication réelle non implémentée dans cette version", "WARNING")
        return {
            "success": False,
            "error": "Publication réelle non implémentée - utilisez le mode test"
        }
        
    except Exception as e:
        error_msg = f"Erreur publication: {str(e)}"
        log_app(error_msg, "ERROR")
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    import uvicorn
    
    log_app("🚀 Démarrage serveur Windows...", "START")
    
    # Démarrer ngrok si activé
    if ENABLE_NGROK:
        start_ngrok_tunnel_windows()
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=BACKEND_PORT, log_level="info")
    except KeyboardInterrupt:
        log_app("Arrêt par Ctrl+C", "INFO")
    except Exception as e:
        log_app(f"Erreur serveur: {e}", "ERROR")
    finally:
        if ENABLE_NGROK:
            stop_ngrok_tunnel()
        log_app("Serveur arrêté", "INFO")