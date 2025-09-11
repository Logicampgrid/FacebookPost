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
        
        # Attendre que ngrok soit prêt avec timeout
        max_attempts = 30  # 30 secondes
        for attempt in range(max_attempts):
            try:
                time.sleep(1)
                
                # Vérifier API ngrok
                response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=3)
                if response.status_code == 200:
                    tunnels = response.json()
                    if tunnels.get('tunnels') and len(tunnels['tunnels']) > 0:
                        public_url = tunnels['tunnels'][0]['public_url']
                        NGROK_URL = public_url
                        
                        log_app(f"🌐 Tunnel ngrok actif: {NGROK_URL}", "SUCCESS")
                        
                        # Sauvegarder URL dans fichier
                        save_ngrok_url_to_files(NGROK_URL)
                        
                        return NGROK_URL
                        
            except requests.exceptions.RequestException:
                log_app(f"Tentative {attempt + 1}/{max_attempts} - API ngrok pas prête", "INFO")
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

# === WEBHOOK HANDLER ===
@app.post("/api/webhook")
async def webhook_handler(request: Request):
    """Gestionnaire webhook Windows"""
    try:
        body = await request.body()
        content_type = request.headers.get("content-type", "")
        
        log_app(f"Webhook reçu: {len(body)} bytes, type: {content_type}", "INFO")
        
        # Traitement selon le type de contenu
        if "application/json" in content_type:
            try:
                json_data = json.loads(body.decode('utf-8'))
                log_app(f"Données JSON webhook: {json.dumps(json_data, indent=2)}", "INFO")
            except json.JSONDecodeError:
                log_app("Impossible de décoder le JSON webhook", "WARNING")
        
        return {"status": "received", "timestamp": datetime.utcnow()}
        
    except Exception as e:
        log_app(f"Erreur traitement webhook: {e}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

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