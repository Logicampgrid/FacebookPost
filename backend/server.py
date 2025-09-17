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

# Charger les variables d'environnement
load_dotenv()

# === CONFIGURATION WINDOWS ===
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8001"))
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "3000"))

# Chemins Windows
WINDOWS_PATHS = {
    "backend_dir": os.path.abspath(os.path.dirname(__file__)),
    "project_root": os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
    "frontend_build": os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "frontend", "build")
}

# === CONFIGURATION NGROK MODIFIÉE POUR MODE STANDALONE ===
ENABLE_NGROK = os.getenv("ENABLE_NGROK", "detect").lower()  # detect, true, false
DETECT_EXISTING_NGROK = True  # Toujours détecter ngrok existant d'abord
NGROK_PROCESS = None
NGROK_URL = None

# === FACEBOOK/META CONFIGURATION MISE À JOUR ===
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
FACEBOOK_CLIENT_TOKEN = os.getenv("FACEBOOK_CLIENT_TOKEN")  # Token client AutoGPT
FACEBOOK_GRAPH_URL = os.getenv("FACEBOOK_GRAPH_URL", "https://graph.facebook.com/v18.0")

# === CONFIGURATION BOUTIQUES MULTI-PLATFORM (MISE À JOUR) ===
PUBLICATION_TEST_MODE = os.getenv("PUBLICATION_TEST_MODE", "true").lower() == "true"

# Configuration des 3 stores selon les spécifications
STORES = {
    "gizmobbs": {
        "name": "Le Berger Blanc Suisse",
        "fb_page_id": "102401876209415",
        "ig_user_id": os.getenv("IG_USER_ID_GIZMO"),
        "access_token": os.getenv("FB_ACCESS_TOKEN_GIZMO")
    },
    "logicantiq": {
        "name": "LogicAntiq", 
        "fb_page_id": "210654558802531",
        "ig_user_id": os.getenv("IG_USER_ID_LOGICANTIQ"),
        "access_token": os.getenv("FB_ACCESS_TOKEN_LOGICANTIQ")
    },
    "outdoor": {
        "name": "Logicamp Outdoor",
        "fb_page_id": "236260991673388", 
        "ig_user_id": os.getenv("IG_USER_ID_OUTDOOR"),
        "access_token": os.getenv("FB_ACCESS_TOKEN_OUTDOOR")
    }
}

# Dictionnaire dynamique pour les tokens récupérés via authentification
TOKENS = {
    "gizmobbs": {},
    "logicantiq": {},
    "outdoor": {}
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

def log_app(message: str, level: str = "INFO"):
    """Logging pour l'application"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "START": "🚀"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [WIN] {message}")

def kill_existing_ngrok():
    """Tuer tous les processus ngrok existants avec vérification robuste"""
    try:
        if os.name == 'nt':  # Windows
            # Vérifier s'il y a des processus ngrok en cours
            check_result = subprocess.run(
                ["tasklist", "/fi", "imagename eq ngrok.exe"],
                capture_output=True, text=True
            )
            
            if "ngrok.exe" in check_result.stdout:
                log_app("🔍 Processus ngrok détectés, arrêt en cours...", "INFO")
                kill_result = subprocess.run(
                    ["taskkill", "/f", "/im", "ngrok.exe"],
                    capture_output=True, text=True
                )
                if kill_result.returncode == 0:
                    log_app("✅ Processus ngrok existants terminés", "SUCCESS")
                else:
                    log_app(f"⚠️ Erreur arrêt ngrok: {kill_result.stderr}", "WARNING")
            else:
                log_app("ℹ️ Aucun processus ngrok en cours", "INFO")
        else:  # Linux/Mac
            subprocess.run(["pkill", "-f", "ngrok"], capture_output=True)
            log_app("Processus ngrok existants terminés", "INFO")
            
    except Exception as e:
        log_app(f"⚠️ Erreur lors de l'arrêt des processus ngrok: {e}", "WARNING")

def get_active_ngrok_url():
    """Récupère l'URL ngrok active via l'API locale - NOUVELLE FONCTION DYNAMIQUE"""
    try:
        log_app("🔍 Détection de l'URL ngrok active...", "INFO")
        
        # Interroger l'API ngrok locale
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
                            log_app(f"✅ URL ngrok active détectée: {public_url}", "SUCCESS")
                            return public_url
                
                # Si pas de tunnel spécifique trouvé, prendre le premier
                first_tunnel = tunnels[0]
                public_url = first_tunnel.get('public_url')
                if public_url:
                    log_app(f"✅ URL ngrok active (premier tunnel): {public_url}", "SUCCESS")
                    return public_url
            
            log_app("⚠️ Aucun tunnel ngrok actif trouvé", "WARNING")
            return None
        else:
            log_app(f"⚠️ API ngrok non accessible (status: {response.status_code})", "WARNING")
            return None
            
    except requests.exceptions.ConnectionError:
        log_app("⚠️ API ngrok non accessible (connexion refusée)", "WARNING")
        return None
    except Exception as e:
        log_app(f"❌ Erreur détection ngrok: {e}", "ERROR")
        return None

def build_dynamic_redirect_uri(callback_path="/auth/callback"):
    """Construit dynamiquement l'URI de redirection - VERSION CORRIGÉE"""  
    try:
        # PRIORITÉ 1: Vérifier le frontend .env pour l'URL backend (maintenant correctement configurée)
        try:
            frontend_env_path = os.path.join(WINDOWS_PATHS["project_root"], "frontend", ".env")
            if os.path.exists(frontend_env_path):
                with open(frontend_env_path, "r", encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line in lines:
                    if line.startswith("REACT_APP_BACKEND_URL="):
                        backend_url = line.split("=", 1)[1].strip()
                        # Utiliser l'URL du frontend .env (maintenant avec ngrok correct)
                        if backend_url and backend_url.startswith("https://"):
                            redirect_uri = f"{backend_url}{callback_path}"
                            log_app(f"✅ URL backend du frontend .env: {backend_url}", "SUCCESS")
                            log_app(f"✅ Redirect URI depuis frontend .env: {redirect_uri}", "SUCCESS")
                            return redirect_uri
        except Exception as e:
            log_app(f"⚠️ Erreur lecture frontend .env: {e}", "WARNING")
        
        # PRIORITÉ 2: Récupérer l'URL ngrok active en temps réel
        ngrok_url = get_active_ngrok_url()
        if ngrok_url:
            redirect_uri = f"{ngrok_url}{callback_path}"
            log_app(f"🎯 Redirect URI dynamique (ngrok actif): {redirect_uri}", "SUCCESS")
            return redirect_uri
        
        # PRIORITÉ 3: Utiliser l'URL globale si ngrok est défini
        global NGROK_URL
        if NGROK_URL:
            redirect_uri = f"{NGROK_URL}{callback_path}"
            log_app(f"🎯 Redirect URI dynamique (global): {redirect_uri}", "SUCCESS")
            return redirect_uri
        
        # PRIORITÉ 4: Lire depuis le fichier ngrok_url.txt si disponible
        try:
            ngrok_file_path = os.path.join(WINDOWS_PATHS["backend_dir"], "ngrok_url.txt")
            if os.path.exists(ngrok_file_path):
                with open(ngrok_file_path, "r", encoding='utf-8') as f:
                    file_url = f.read().strip()
                    if file_url and file_url.startswith("https://"):
                        redirect_uri = f"{file_url}{callback_path}"
                        log_app(f"🎯 Redirect URI depuis fichier: {redirect_uri}", "INFO")
                        return redirect_uri
        except Exception as e:
            log_app(f"⚠️ Erreur lecture ngrok_url.txt: {e}", "WARNING")
        
        # FALLBACK: URL locale (seulement si aucune URL externe n'est disponible)
        redirect_uri = f"http://localhost:{BACKEND_PORT}{callback_path}"
        log_app(f"⚠️ Redirect URI fallback (local): {redirect_uri}", "WARNING")
        log_app("💡 ATTENTION: Cette URL locale ne fonctionnera pas avec Facebook en production!", "WARNING")
        return redirect_uri
        
    except Exception as e:
        log_app(f"❌ Erreur construction redirect URI: {e}", "ERROR")
        # Fallback d'urgence
        return f"http://localhost:{BACKEND_PORT}{callback_path}"

def sync_frontend_env_with_ngrok():
    """Synchronise le .env frontend avec l'URL ngrok active"""
    try:
        ngrok_url = get_active_ngrok_url()
        if not ngrok_url:
            log_app("⚠️ Aucune URL ngrok active - synchronisation ignorée", "WARNING")
            return False
        
        frontend_env_path = os.path.join(WINDOWS_PATHS["project_root"], "frontend", ".env")
        if not os.path.exists(frontend_env_path):
            log_app(f"⚠️ Frontend .env non trouvé: {frontend_env_path}", "WARNING")
            return False
        
        # Lire le fichier .env actuel
        with open(frontend_env_path, "r", encoding='utf-8') as f:
            lines = f.readlines()
        
        # Mettre à jour REACT_APP_BACKEND_URL
        updated_lines = []
        backend_url_updated = False
        for line in lines:
            if line.startswith("REACT_APP_BACKEND_URL="):
                old_url = line.split("=", 1)[1].strip()
                if old_url != ngrok_url:
                    updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}\n")
                    log_app(f"✅ REACT_APP_BACKEND_URL mis à jour: {old_url} -> {ngrok_url}", "SUCCESS")
                else:
                    updated_lines.append(line)
                    log_app(f"✅ REACT_APP_BACKEND_URL déjà à jour: {ngrok_url}", "SUCCESS")
                backend_url_updated = True
            else:
                updated_lines.append(line)
        
        if not backend_url_updated:
            updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}\n")
            log_app(f"✅ REACT_APP_BACKEND_URL ajouté: {ngrok_url}", "SUCCESS")
        
        # Réécrire le fichier
        with open(frontend_env_path, "w", encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        log_app(f"🎯 Frontend .env synchronisé avec ngrok: {ngrok_url}", "SUCCESS")
        return True
        
    except Exception as e:
        log_app(f"❌ Erreur synchronisation frontend .env: {e}", "ERROR")
        return False

# === LIFESPAN CONTEXT MANAGER ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan events - startup and shutdown - VERSION CORRIGÉE NGROK"""
    # Startup
    log_app("🚀 Meta Publishing Platform - Version Windows CORRIGÉE", "START")
    log_app(f"📁 Répertoire backend: {WINDOWS_PATHS['backend_dir']}", "INFO")
    log_app(f"🌐 Port backend: {BACKEND_PORT}", "INFO")
    log_app(f"🔧 Mode test: {PUBLICATION_TEST_MODE}", "INFO")
    
    # Synchroniser avec ngrok si disponible
    enable_setting = os.getenv("ENABLE_NGROK", "detect").lower()
    log_app(f"🔍 Configuration ngrok: {enable_setting}", "INFO")
    
    if enable_setting in ["detect", "true"]:
        log_app("🔄 Démarrage avec tunnel ngrok (accès internet)...", "INFO")
        log_app("🔗 L'application sera accessible depuis n'importe où sur internet", "INFO")
        log_app("🔧 Mode test activé pour économiser les crédits", "INFO")
        
        # Détecter et synchroniser avec ngrok existant
        ngrok_result = get_active_ngrok_url()
        if ngrok_result:
            global NGROK_URL
            NGROK_URL = ngrok_result
            log_app(f"✅ Ngrok configuré avec succès: {NGROK_URL}", "SUCCESS")
            
            # Synchroniser le frontend .env
            sync_frontend_env_with_ngrok()
            
            log_app("ℹ️ 🔄 Attente de la synchronisation ngrok avec le frontend...", "INFO")
            time.sleep(2)  # Laisser le temps au frontend de se synchroniser
            log_app("✅ Application démarrée avec succès!", "SUCCESS")
        else:
            log_app("⚠️ Ngrok non disponible - mode local uniquement", "WARNING")
            log_app(f"🌐 Application accessible sur: http://localhost:{BACKEND_PORT}", "INFO")
    else:
        log_app("🌐 Mode local uniquement (ngrok désactivé)", "INFO")
        log_app(f"🌐 Application accessible sur: http://localhost:{BACKEND_PORT}", "INFO")
    
    yield  # Application runs here
    
    # Shutdown
    log_app("🛑 Arrêt de l'application...", "INFO")
    log_app("✅ Application arrêtée proprement!", "SUCCESS")

# === FASTAPI APP INITIALIZATION ===
app = FastAPI(
    title="Meta Publishing Platform - Windows Version CORRIGÉE",
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

# Vérifier si le frontend build existe
def check_frontend_build():
    """Vérifier si le build frontend existe"""
    if os.path.exists(WINDOWS_PATHS["frontend_build"]):
        log_app(f"✅ Frontend build trouvé: {WINDOWS_PATHS['frontend_build']}", "SUCCESS")
        return True
    else:
        log_app(f"⚠️ Frontend build manquant: {WINDOWS_PATHS['frontend_build']}", "WARNING")
        log_app("💡 Exécutez 'npm run build' dans le dossier frontend", "INFO")
        return False

frontend_available = check_frontend_build()

# Monter les fichiers statiques si disponibles
if frontend_available:
    try:
        static_path = os.path.join(WINDOWS_PATHS["frontend_build"], "static")
        if os.path.exists(static_path):
            app.mount("/static", StaticFiles(directory=static_path), name="static")
            log_app("✅ Fichiers statiques frontend montés sur /static", "SUCCESS")
    except Exception as e:
        log_app(f"⚠️ Erreur montage fichiers statiques: {e}", "WARNING")

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS requests for CORS"""
    return {"message": "OK"}

# === PYDANTIC MODELS FOR AUTHENTICATION ===
class FacebookAuthRequest(BaseModel):
    code: str
    store: str
    redirect_uri: str

class FacebookExchangeCodeRequest(BaseModel):
    code: str
    state: Optional[str] = None
    store: Optional[str] = None
    redirect_uri: Optional[str] = None
    
    @field_validator('store', mode='before')
    @classmethod
    def set_store_from_state(cls, v, info: ValidationInfo):
        """Map state to store if store is not provided"""
        if v is None and info.data and info.data.get('state'):
            return info.data.get('state')
        return v or "default"
    
    @field_validator('redirect_uri', mode='before')
    @classmethod
    def set_dynamic_redirect_uri(cls, v):
        """Set dynamic redirect_uri based on active ngrok URL if not provided"""
        if v:
            return v  # Utiliser l'URI fournie si spécifiée
        
        # Sinon, construire dynamiquement l'URI de redirection avec le bon chemin
        # Utiliser "/" comme chemin car c'est ce que les frontends utilisent maintenant
        return build_dynamic_redirect_uri("/")

class FacebookAuthResponse(BaseModel):
    success: bool
    store: str
    access_token: Optional[str] = None
    fb_page_id: Optional[str] = None
    ig_user_id: Optional[str] = None
    error: Optional[str] = None

# === AUTHENTICATION FUNCTIONS ===
async def exchange_facebook_code(code: str, redirect_uri: str) -> dict:
    """Échange un code d'autorisation Facebook contre un access token - VERSION CORRIGÉE REDIRECT URI"""
    try:
        log_app(f"Échange du code d'autorisation Facebook", "INFO")
        log_app(f"Code exchange reçu - Store: None, Code: {code[:10]}...", "INFO")
        
        if not FACEBOOK_APP_ID or not FACEBOOK_APP_SECRET:
            raise Exception("Configuration Facebook manquante (APP_ID ou APP_SECRET)")
        
        # CORRECTION CRITIQUE: Utiliser EXACTEMENT l'URI de redirection fournie par le frontend
        # Ne plus essayer de "corriger" ou modifier l'URI - cela cause des discordances avec Facebook
        log_app(f"🎯 Redirect URI exacte (depuis frontend): {redirect_uri}", "INFO")
        
        # Faire la requête d'échange de token avec l'URI EXACTE fournie
        log_app("Requête d'échange de token...", "INFO")
        
        token_url = f"{FACEBOOK_GRAPH_URL}/oauth/access_token"
        params = {
            "client_id": FACEBOOK_APP_ID,
            "client_secret": FACEBOOK_APP_SECRET,
            "redirect_uri": redirect_uri,  # Utiliser l'URI exacte du frontend
            "code": code
        }
        
        response = requests.get(token_url, params=params, timeout=30)
        
        if response.status_code != 200:
            error_detail = response.text
            log_app(f"❌ Erreur HTTP lors de l'authentification: {response.status_code} {response.reason} for url: {response.url} - {error_detail}", "ERROR")
            raise Exception(f"Erreur HTTP lors de l'authentification: {response.status_code} {response.reason} for url: {response.url} - {error_detail}")
        
        token_data = response.json()
        
        if "access_token" not in token_data:
            log_app(f"❌ Token d'accès manquant dans la réponse: {token_data}", "ERROR")
            raise Exception(f"Token d'accès manquant dans la réponse: {token_data}")
        
        access_token = token_data["access_token"]
        log_app("✅ Token d'accès obtenu avec succès", "SUCCESS")
        
        return {
            "access_token": access_token,
            "token_type": token_data.get("token_type", "bearer"),
            "expires_in": token_data.get("expires_in")
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Erreur HTTP lors de l'authentification: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_msg += f" - {error_data}"
            except:
                error_msg += f" - Status: {e.response.status_code}"
        log_app(f"❌ Erreur échange Facebook: {error_msg}", "ERROR")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Erreur échange Facebook: {str(e)}"
        log_app(f"❌ Erreur échange Facebook: {error_msg}", "ERROR")
        raise Exception(error_msg)

# === API ENDPOINTS ===

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/auth/facebook/exchange-code")
async def facebook_exchange_code_endpoint(request: FacebookExchangeCodeRequest):
    """Échange un code d'autorisation Facebook contre un access token et récupère les données utilisateur"""
    try:
        log_app(f"Code exchange reçu - Store: {request.store}, Code: {request.code[:10]}...", "INFO")
        
        # Construire dynamiquement l'URI de redirection
        if request.redirect_uri:
            redirect_uri = request.redirect_uri
        else:
            redirect_uri = build_dynamic_redirect_uri("/")
        
        log_app(f"Redirect URI (dynamique): {redirect_uri}", "INFO")
        
        # Échange du code contre token
        token_data = await exchange_facebook_code(request.code, redirect_uri)
        access_token = token_data["access_token"]
        
        # Récupérer les informations utilisateur avec le token
        user_info_url = f"{FACEBOOK_GRAPH_URL}/me"
        user_params = {
            "fields": "id,name,email",
            "access_token": access_token
        }
        
        user_response = requests.get(user_info_url, params=user_params, timeout=15)
        user_response.raise_for_status()
        user_data = user_response.json()
        
        return {
            "success": True,
            "access_token": access_token,
            "user": {
                "_id": user_data["id"],
                "id": user_data["id"],
                "name": user_data["name"],
                "email": user_data.get("email"),
                "business_managers": []  # Sera rempli par d'autres endpoints
            },
            "store": request.store or "default"
        }
        
    except Exception as e:
        log_app(f"❌ Erreur exchange-code: {str(e)}", "ERROR")
        return {
            "success": False,
            "error": str(e),
            "store": request.store or "default"
        }

@app.post("/api/auth/facebook")
async def facebook_auth_endpoint(request: Request):
    """Authentification Facebook avec token d'accès"""
    try:
        request_data = await request.json()
        access_token = request_data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Token d'accès manquant")
        
        log_app("Utilisation du token Facebook fourni dans la requête", "INFO")
        
        # Récupérer les informations utilisateur
        user_info_url = f"{FACEBOOK_GRAPH_URL}/me"
        user_params = {
            "fields": "id,name,email",
            "access_token": access_token
        }
        
        try:
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
            instagram_accounts = []
            
            # Extraire les comptes Instagram des pages
            for page in facebook_pages:
                if page.get("instagram_business_account"):
                    ig_account = page["instagram_business_account"]
                    try:
                        # Récupérer les détails du compte Instagram
                        ig_url = f"{FACEBOOK_GRAPH_URL}/{ig_account['id']}"
                        ig_params = {
                            "fields": "id,username,name,profile_picture_url",
                            "access_token": access_token
                        }
                        ig_response = requests.get(ig_url, params=ig_params, timeout=10)
                        if ig_response.status_code == 200:
                            ig_data = ig_response.json()
                            instagram_accounts.append(ig_data)
                    except Exception as e:
                        log_app(f"⚠️ Erreur récupération Instagram {ig_account['id']}: {e}", "WARNING")
            
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
            
            log_app(f"✅ Récupéré: {len(facebook_pages)} pages, {len(instagram_accounts)} comptes Instagram", "SUCCESS")
            
            return {
                "success": True,
                "user": {
                    "_id": user_data["id"],
                    "id": user_data["id"],
                    "name": user_data["name"],
                    "email": user_data.get("email"),
                    "facebook_pages": facebook_pages,
                    "instagram_accounts": instagram_accounts,
                    "business_managers": business_managers
                },
                "total_pages": len(facebook_pages),
                "total_instagram_accounts": len(instagram_accounts),
                "total_business_managers": len(business_managers)
            }
            
        except requests.exceptions.RequestException as e:
            if e.response and e.response.status_code == 400:
                log_app("⚠️ Requête complète échouée (400), tentative avec requête simplifiée", "WARNING")
                
                # Requête simplifiée
                simple_params = {
                    "fields": "id,name",
                    "access_token": access_token
                }
                
                simple_response = requests.get(user_info_url, params=simple_params, timeout=10)
                simple_response.raise_for_status()
                simple_user_data = simple_response.json()
                
                log_app("✅ Requête Facebook simplifiée réussie", "SUCCESS")
                log_app(f"✅ Utilisateur connecté: {simple_user_data.get('name', 'Unknown')}", "SUCCESS")
                
                return {
                    "success": True,
                    "user": {
                        "_id": simple_user_data["id"],
                        "id": simple_user_data["id"],
                        "name": simple_user_data["name"],
                        "email": None,
                        "facebook_pages": [],
                        "instagram_accounts": [],
                        "business_managers": []
                    },
                    "total_pages": 0,
                    "total_instagram_accounts": 0,
                    "total_business_managers": 0,
                    "simplified_response": True
                }
            else:
                raise e
        
    except Exception as e:
        log_app(f"❌ Erreur authentification Facebook: {str(e)}", "ERROR")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/sync/ngrok")
async def sync_ngrok_url(request: Request):
    """Synchronise l'URL ngrok avec le backend"""
    try:
        data = await request.json()
        new_ngrok_url = data.get("ngrok_url")
        
        if not new_ngrok_url:
            raise HTTPException(status_code=400, detail="URL ngrok manquante")
        
        global NGROK_URL
        NGROK_URL = new_ngrok_url
        
        log_app(f"✅ URL ngrok synchronisée: {new_ngrok_url}", "SUCCESS")
        
        # Sauvegarder dans le fichier
        try:
            ngrok_file_path = os.path.join(WINDOWS_PATHS["backend_dir"], "ngrok_url.txt")
            with open(ngrok_file_path, "w", encoding='utf-8') as f:
                f.write(new_ngrok_url)
            log_app("URL ngrok sauvegardée dans ngrok_url.txt", "SUCCESS")
        except Exception as e:
            log_app(f"⚠️ Erreur sauvegarde ngrok_url.txt: {e}", "WARNING")
        
        return {
            "success": True,
            "message": "URL ngrok synchronisée avec succès",
            "ngrok_url": new_ngrok_url,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        log_app(f"❌ Erreur synchronisation ngrok: {str(e)}", "ERROR")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/config/oauth-status")
async def oauth_status():
    """Retourne le statut de la configuration OAuth"""
    try:
        ngrok_url = get_active_ngrok_url()
        redirect_uri = build_dynamic_redirect_uri("/")  # Utiliser "/" comme les frontends
        
        return {
            "ngrok_active": ngrok_url is not None,
            "ngrok_url": ngrok_url,
            "redirect_uri": redirect_uri,
            "facebook_app_configured": bool(FACEBOOK_APP_ID and FACEBOOK_APP_SECRET),
            "facebook_app_id": FACEBOOK_APP_ID,
            "oauth_ready": bool(ngrok_url and FACEBOOK_APP_ID and FACEBOOK_APP_SECRET),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        log_app(f"❌ Erreur status OAuth: {str(e)}", "ERROR")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/debug/instagram-complete-diagnosis")
async def instagram_complete_diagnosis():
    """Diagnostic complet Instagram avec informations de l'utilisateur connecté"""
    try:
        log_app("Diagnostic Instagram complet démarré", "INFO")
        
        # Récupérer l'URL ngrok active
        ngrok_url = get_active_ngrok_url()
        ngrok_active = ngrok_url is not None
        
        # Token direct depuis l'environnement pour diagnostic
        direct_token = os.getenv("FACEBOOK_DIRECT_TOKEN")
        
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "ngrok_active": ngrok_active,
            "ngrok_url": ngrok_url if ngrok_active else None,
            "webhook_configured": bool(os.getenv("FACEBOOK_VERIFY_TOKEN")),
            "facebook_pages_count": 0,
            "instagram_accounts": [],
            "authentication": None  # CORRECTION: Initialiser à None au lieu d'un objet
        }
        
        if direct_token:
            try:
                # Test d'authentification avec le token direct
                user_info_url = f"{FACEBOOK_GRAPH_URL}/me"
                user_params = {
                    "fields": "id,name,email",
                    "access_token": direct_token
                }
                
                user_response = requests.get(user_info_url, params=user_params, timeout=10)
                
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    
                    # Récupérer les Business Managers
                    bm_count = 0
                    try:
                        bm_url = f"{FACEBOOK_GRAPH_URL}/me/businesses"
                        bm_params = {
                            "fields": "id,name",
                            "access_token": direct_token
                        }
                        bm_response = requests.get(bm_url, params=bm_params, timeout=10)
                        if bm_response.status_code == 200:
                            bm_data = bm_response.json()
                            bm_count = len(bm_data.get("data", []))
                    except Exception:
                        pass
                    
                    # CORRECTION: Créer l'objet authentication correctement
                    diagnosis["authentication"] = {
                        "user_found": True,
                        "user_name": user_data.get("name", "Unknown"),
                        "user_id": user_data.get("id"),
                        "business_managers_count": bm_count
                    }
                    
                    # Récupérer les pages Facebook
                    try:
                        pages_url = f"{FACEBOOK_GRAPH_URL}/me/accounts"
                        pages_params = {
                            "fields": "id,name,instagram_business_account",
                            "access_token": direct_token
                        }
                        
                        pages_response = requests.get(pages_url, params=pages_params, timeout=15)
                        if pages_response.status_code == 200:
                            pages_data = pages_response.json()
                            facebook_pages = pages_data.get("data", [])
                            diagnosis["facebook_pages_count"] = len(facebook_pages)
                            
                            # Récupérer les comptes Instagram
                            for page in facebook_pages:
                                if page.get("instagram_business_account"):
                                    ig_account = page["instagram_business_account"]
                                    try:
                                        ig_url = f"{FACEBOOK_GRAPH_URL}/{ig_account['id']}"
                                        ig_params = {
                                            "fields": "id,username,name,profile_picture_url",
                                            "access_token": direct_token
                                        }
                                        ig_response = requests.get(ig_url, params=ig_params, timeout=10)
                                        if ig_response.status_code == 200:
                                            ig_data = ig_response.json()
                                            diagnosis["instagram_accounts"].append(ig_data)
                                    except Exception as e:
                                        log_app(f"⚠️ Erreur récupération Instagram {ig_account['id']}: {e}", "WARNING")
                    except Exception as e:
                        log_app(f"⚠️ Erreur récupération pages: {e}", "WARNING")
                        
                else:
                    # CORRECTION: En cas d'erreur d'authentification
                    diagnosis["authentication"] = {
                        "user_found": False,
                        "user_name": None,
                        "user_id": None,
                        "business_managers_count": 0
                    }
                    
            except Exception as e:
                log_app(f"⚠️ Erreur diagnostic authentification: {e}", "WARNING")
                # CORRECTION: En cas d'exception
                diagnosis["authentication"] = {
                    "user_found": False,
                    "user_name": None,
                    "user_id": None,
                    "business_managers_count": 0
                }
        else:
            # CORRECTION: Pas de token disponible
            diagnosis["authentication"] = {
                "user_found": False,
                "user_name": None,
                "user_id": None,
                "business_managers_count": 0
            }
        
        log_app(f"✅ Diagnostic terminé: {len(diagnosis['instagram_accounts'])} comptes Instagram trouvés", "SUCCESS")
        return diagnosis
        
    except Exception as e:
        log_app(f"❌ Erreur diagnostic Instagram: {str(e)}", "ERROR")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "ngrok_active": False,
            "ngrok_url": None,
            "webhook_configured": False,
            "facebook_pages_count": 0,
            "instagram_accounts": [],
            "authentication": {
                "user_found": False,
                "user_name": None,
                "user_id": None,
                "business_managers_count": 0
            }
        }

# === ROUTES FRONTEND ===
@app.get("/")
async def serve_frontend(request: Request):
    """Route principale pour servir le frontend React - GESTION AMÉLIORÉE CODE FACEBOOK"""
    
    # Récupérer les paramètres de l'URL
    query_params = dict(request.query_params)
    
    # Vérifier si c'est un callback Facebook
    if "code" in query_params and "state" in query_params:
        log_app(f"🔄 Code Facebook reçu sur route racine: {query_params['code'][:20]}...", "INFO")
        log_app(f"🔄 State Facebook: {query_params['state']}", "INFO")
        
        # Rediriger vers le frontend avec les paramètres
        query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
        frontend_url = f"/?{query_string}"
        log_app(f"🔄 Redirection vers frontend: {frontend_url}", "INFO")
        
        # Servir le frontend avec les paramètres préservés
        if frontend_available:
            return FileResponse(os.path.join(WINDOWS_PATHS["frontend_build"], "index.html"))
        else:
            return {"message": "Frontend non disponible", "query_params": query_params}
    
    # Route normale - servir le frontend
    if frontend_available:
        return FileResponse(os.path.join(WINDOWS_PATHS["frontend_build"], "index.html"))
    else:
        return {
            "message": "Meta Publishing Platform API", 
            "version": "1.0.0",
            "status": "running",
            "frontend_build": "non disponible"
        }

# Catch-all route pour le frontend (doit être à la fin)
@app.get("/{path:path}")
async def catch_all_frontend(path: str, request: Request):
    """Route catch-all pour le frontend React"""
    
    # Vérifier si c'est une route API
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Servir le frontend pour toutes les autres routes
    if frontend_available:
        return FileResponse(os.path.join(WINDOWS_PATHS["frontend_build"], "index.html"))
    else:
        return {"message": f"Route {path} non trouvée - Frontend non disponible"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=BACKEND_PORT)