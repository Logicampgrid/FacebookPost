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
import shutil
import tempfile
import mimetypes
import ftplib
from pathlib import Path

# Import database functions
from database import (
    connect_to_mongo, close_mongo_connection, 
    create_post, get_posts_by_user, update_post, get_post_by_id, delete_post,
    save_webhook_data, get_recent_webhooks,
    save_user_token, get_user_token, is_token_expired, refresh_facebook_token
)

# Import de la nouvelle fonction poster_media_enhanced
from poster_media_enhanced import poster_media_enhanced, STORES_CONFIG

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

# MongoDB will now handle storage

# === CONFIGURATION FTP POUR UPLOAD VIDÉOS ===
FTP_HOST = os.getenv("FTP_HOST", "logicamp.org")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER", "logi")
FTP_PASSWORD = os.getenv("FTP_PASSWORD", "")
FTP_DIRECTORY = os.getenv("FTP_DIRECTORY", "/wordpress/uploads/")
FTP_BASE_URL = os.getenv("FTP_BASE_URL", f"https://{FTP_HOST}/wordpress/uploads/")

# === CONFIGURATION VIDÉO ===
MAX_VIDEO_SIZE_FACEBOOK = 10 * 1024 * 1024 * 1024  # 10 GB
MAX_VIDEO_SIZE_INSTAGRAM = 1 * 1024 * 1024 * 1024   # 1 GB
MAX_VIDEO_DURATION_FACEBOOK = 15 * 60  # 15 minutes en secondes
MAX_VIDEO_DURATION_INSTAGRAM = 60      # 60 secondes
SUPPORTED_VIDEO_FORMATS = ["video/mp4", "video/quicktime"]  # MP4 et MOV
UPLOAD_DIR = "uploads"

# Créer le dossier uploads s'il n'existe pas
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

def log_video(message: str, level: str = "INFO"):
    """Logging spécialisé pour les vidéos"""
    icons = {"INFO": "🎥", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "UPLOAD": "📤"}
    icon = icons.get(level.upper(), "🎬")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [VIDEO] {message}")

def validate_video_file(file_path: str, platform: str = "both") -> dict:
    """Valide un fichier vidéo selon les contraintes de la plateforme"""
    try:
        log_video(f"Validation vidéo pour {platform}: {file_path}", "INFO")
        
        # Vérifier l'existence du fichier
        if not os.path.exists(file_path):
            return {"valid": False, "error": "Fichier introuvable"}
        
        # Vérifier la taille du fichier
        file_size = os.path.getsize(file_path)
        log_video(f"Taille fichier: {file_size / (1024*1024):.2f} MB", "INFO")
        
        # Vérifier le type MIME
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type not in SUPPORTED_VIDEO_FORMATS:
            return {"valid": False, "error": f"Format non supporté: {mime_type}. Formats supportés: {SUPPORTED_VIDEO_FORMATS}"}
        
        # Contraintes selon la plateforme
        if platform == "facebook":
            if file_size > MAX_VIDEO_SIZE_FACEBOOK:
                return {"valid": False, "error": f"Taille trop importante pour Facebook (max: {MAX_VIDEO_SIZE_FACEBOOK/(1024**3):.1f} GB)"}
        elif platform == "instagram":
            if file_size > MAX_VIDEO_SIZE_INSTAGRAM:
                return {"valid": False, "error": f"Taille trop importante pour Instagram (max: {MAX_VIDEO_SIZE_INSTAGRAM/(1024**3):.1f} GB)"}
        else:  # both
            if file_size > MAX_VIDEO_SIZE_INSTAGRAM:  # Utiliser la limite la plus restrictive
                return {"valid": False, "error": f"Taille trop importante (max: {MAX_VIDEO_SIZE_INSTAGRAM/(1024**3):.1f} GB pour compatibilité Instagram)"}
        
        # TODO: Ajouter validation durée avec ffprobe si disponible
        
        log_video("Validation réussie", "SUCCESS")
        return {
            "valid": True, 
            "file_size": file_size,
            "mime_type": mime_type,
            "size_mb": file_size / (1024*1024)
        }
        
    except Exception as e:
        log_video(f"Erreur validation: {str(e)}", "ERROR")
        return {"valid": False, "error": str(e)}

async def upload_video_to_ftp(video_path: str, filename: str = None) -> tuple:
    """Upload une vidéo vers le serveur FTP"""
    try:
        log_video(f"Début upload FTP: {video_path}", "UPLOAD")
        
        if not filename:
            filename = f"video_{uuid.uuid4().hex[:8]}_{os.path.basename(video_path)}"
        
        # Validation avant upload
        validation = validate_video_file(video_path)
        if not validation["valid"]:
            return False, None, validation["error"]
        
        # Connexion FTP
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT, timeout=60)  # Timeout plus long pour les vidéos
        ftp.login(FTP_USER, FTP_PASSWORD)
        
        # Changement de répertoire
        try:
            ftp.cwd(FTP_DIRECTORY)
        except ftplib.error_perm:
            # Créer le répertoire s'il n'existe pas
            ftp.mkd(FTP_DIRECTORY)
            ftp.cwd(FTP_DIRECTORY)
        
        # Upload du fichier en mode binaire
        with open(video_path, 'rb') as video_file:
            log_video(f"Upload en cours: {filename}", "UPLOAD")
            ftp.storbinary(f'STOR {filename}', video_file)
        
        ftp.quit()
        
        # Construire l'URL publique
        public_url = f"{FTP_BASE_URL}{filename}"
        log_video(f"Upload réussi: {public_url}", "SUCCESS")
        
        return True, public_url, None
        
    except Exception as e:
        log_video(f"Erreur upload FTP: {str(e)}", "ERROR")
        return False, None, str(e)

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
    """Récupère l'URL ngrok active via l'API locale ou depuis le frontend .env - VERSION AMÉLIORÉE"""
    try:
        log_app("🔍 Détection de l'URL ngrok active...", "INFO")
        
        # PRIORITÉ 1: Interroger l'API ngrok locale si disponible
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
                                log_app(f"✅ URL ngrok active détectée (API): {public_url}", "SUCCESS")
                                return public_url
                    
                    # Si pas de tunnel spécifique trouvé, prendre le premier
                    first_tunnel = tunnels[0]
                    public_url = first_tunnel.get('public_url')
                    if public_url:
                        log_app(f"✅ URL ngrok active (premier tunnel): {public_url}", "SUCCESS")
                        return public_url
                
                log_app("⚠️ Aucun tunnel ngrok actif trouvé via API", "WARNING")
        except requests.exceptions.ConnectionError:
            log_app("⚠️ API ngrok non accessible (connexion refusée)", "WARNING")
        except Exception as e:
            log_app(f"⚠️ Erreur API ngrok: {e}", "WARNING")
        
        # PRIORITÉ 2: Lire depuis le frontend .env si l'URL est de type ngrok
        try:
            frontend_env_path = os.path.join(WINDOWS_PATHS["project_root"], "frontend", ".env")
            if os.path.exists(frontend_env_path):
                with open(frontend_env_path, "r", encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line in lines:
                    if line.startswith("REACT_APP_BACKEND_URL="):
                        backend_url = line.split("=", 1)[1].strip()
                        # Vérifier si c'est une URL ngrok valide
                        if backend_url and (backend_url.startswith("https://") and 
                                          ("ngrok" in backend_url or "ngrok-free.app" in backend_url)):
                            log_app(f"✅ URL ngrok trouvée dans frontend .env: {backend_url}", "SUCCESS")
                            return backend_url
        except Exception as e:
            log_app(f"⚠️ Erreur lecture frontend .env: {e}", "WARNING")
        
        # PRIORITÉ 3: Lire depuis le fichier ngrok_url.txt si disponible
        try:
            ngrok_file_path = os.path.join(WINDOWS_PATHS["backend_dir"], "ngrok_url.txt")
            if os.path.exists(ngrok_file_path):
                with open(ngrok_file_path, "r", encoding='utf-8') as f:
                    file_url = f.read().strip()
                    if file_url and file_url.startswith("https://"):
                        log_app(f"✅ URL ngrok trouvée dans fichier: {file_url}", "SUCCESS")
                        return file_url
        except Exception as e:
            log_app(f"⚠️ Erreur lecture ngrok_url.txt: {e}", "WARNING")
        
        log_app("⚠️ Aucune URL ngrok active trouvée", "WARNING")
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
    """Synchronise le .env frontend avec l'URL ngrok active - VERSION CORRIGÉE"""
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
            content = f.read()
        
        # Diviser en lignes pour traitement
        lines = content.splitlines()
        
        # Mettre à jour REACT_APP_BACKEND_URL
        updated_lines = []
        backend_url_updated = False
        
        for line in lines:
            if line.startswith("REACT_APP_BACKEND_URL="):
                old_url = line.split("=", 1)[1] if "=" in line else ""
                if old_url != ngrok_url:
                    updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}")
                    log_app(f"✅ REACT_APP_BACKEND_URL mis à jour: {old_url} -> {ngrok_url}", "SUCCESS")
                else:
                    updated_lines.append(line)
                    log_app(f"✅ REACT_APP_BACKEND_URL déjà à jour: {ngrok_url}", "SUCCESS")
                backend_url_updated = True
            else:
                updated_lines.append(line)
        
        if not backend_url_updated:
            updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}")
            log_app(f"✅ REACT_APP_BACKEND_URL ajouté: {ngrok_url}", "SUCCESS")
        
        # Réécrire le fichier avec les nouvelles lignes
        with open(frontend_env_path, "w", encoding='utf-8') as f:
            f.write("\n".join(updated_lines))
            if updated_lines and not updated_lines[-1].endswith('\n'):
                f.write("\n")  # Ajouter une nouvelle ligne à la fin
        
        log_app(f"🎯 Frontend .env synchronisé avec ngrok: {ngrok_url}", "SUCCESS")
        return True
        
    except Exception as e:
        log_app(f"❌ Erreur synchronisation frontend .env: {e}", "ERROR")
        return False

def update_facebook_oauth_config(ngrok_url):
    """Met à jour automatiquement la configuration Facebook OAuth avec l'URL ngrok active"""
    try:
        if not FACEBOOK_APP_ID or not FACEBOOK_APP_SECRET:
            log_app("⚠️ Configuration Facebook manquante - pas de mise à jour OAuth", "WARNING")
            return False
        
        log_app(f"🔄 Mise à jour configuration Facebook OAuth avec: {ngrok_url}", "INFO")
        
        # Générer le token d'accès administrateur de l'application
        app_access_token = f"{FACEBOOK_APP_ID}|{FACEBOOK_APP_SECRET}"
        
        # URLs de redirection multiples pour couvrir tous les cas
        redirect_uris = [
            f"{ngrok_url}/",
            f"{ngrok_url}/auth/callback", 
            f"{ngrok_url}/auth/callb"
        ]
        
        # Configuration des paramètres Facebook
        facebook_updates = [
            {
                "name": "app_domains",
                "value": f'["{ngrok_url}"]',
                "description": "Domaines autorisés"
            },
            {
                "name": "website_url", 
                "value": ngrok_url,
                "description": "URL du site web"
            },
            {
                "name": "oauth_redirect_uris",
                "value": '[' + ','.join([f'"{uri}"' for uri in redirect_uris]) + ']',
                "description": "URIs de redirection OAuth"
            },
            {
                "name": "web_origins",
                "value": f'["{ngrok_url}"]',
                "description": "Origines web autorisées"
            }
        ]
        
        success_count = 0
        total_updates = len(facebook_updates)
        
        # Appliquer chaque configuration
        for update in facebook_updates:
            try:
                url = f"{FACEBOOK_GRAPH_URL}/{FACEBOOK_APP_ID}"
                data = {
                    update["name"]: update["value"],
                    "access_token": app_access_token
                }
                
                response = requests.post(url, data=data, timeout=15)
                
                if response.status_code == 200:
                    log_app(f"✅ {update['description']}: Mis à jour", "SUCCESS")
                    success_count += 1
                else:
                    log_app(f"⚠️ {update['description']}: Status {response.status_code}", "WARNING")
                    
            except Exception as e:
                log_app(f"❌ Erreur {update['description']}: {str(e)}", "ERROR")
        
        # Résultat final
        if success_count == total_updates:
            log_app(f"✅ Configuration Facebook OAuth mise à jour complètement ({success_count}/{total_updates})", "SUCCESS")
            log_app(f"🔐 URIs de redirection configurées: {', '.join(redirect_uris)}", "SUCCESS")
            return True
        elif success_count > 0:
            log_app(f"⚠️ Configuration Facebook OAuth partiellement mise à jour ({success_count}/{total_updates})", "WARNING")
            return True
        else:
            log_app(f"❌ Échec complet de la mise à jour Facebook OAuth", "ERROR")
            return False
            
    except Exception as e:
        log_app(f"❌ Erreur générale mise à jour Facebook OAuth: {e}", "ERROR")
        return False

def auto_configure_facebook_oauth():
    """Configure automatiquement Facebook OAuth avec l'URL ngrok active"""
    try:
        # Récupérer l'URL ngrok active
        ngrok_url = get_active_ngrok_url()
        if not ngrok_url:
            log_app("⚠️ Pas d'URL ngrok active - configuration Facebook OAuth ignorée", "WARNING")
            return False
        
        # Vérifier la configuration Facebook
        if not FACEBOOK_APP_ID or not FACEBOOK_APP_SECRET:
            log_app("⚠️ Configuration Facebook manquante - OAuth non configuré", "WARNING")
            log_app(f"   FACEBOOK_APP_ID: {'✅ Défini' if FACEBOOK_APP_ID else '❌ Manquant'}", "INFO")
            log_app(f"   FACEBOOK_APP_SECRET: {'✅ Défini' if FACEBOOK_APP_SECRET else '❌ Manquant'}", "INFO")
            return False
        
        log_app(f"🔧 Configuration automatique Facebook OAuth avec: {ngrok_url}", "INFO")
        
        # Appliquer la configuration OAuth
        result = update_facebook_oauth_config(ngrok_url)
        
        if result:
            log_app("✅ Configuration Facebook OAuth mise à jour automatiquement", "SUCCESS")
            log_app(f"🔐 URLs de redirection configurées:", "SUCCESS")
            log_app(f"   • {ngrok_url}/", "SUCCESS")
            log_app(f"   • {ngrok_url}/auth/callback", "SUCCESS")
            log_app(f"   • {ngrok_url}/auth/callb", "SUCCESS")
        else:
            log_app("⚠️ Configuration Facebook OAuth partiellement réussie", "WARNING")
        
        return result
        
    except Exception as e:
        log_app(f"❌ Erreur configuration automatique Facebook OAuth: {e}", "ERROR")
        return False
def update_facebook_endpoints_with_ngrok():
    """Met à jour automatiquement les endpoints Facebook avec l'URL ngrok active"""
    try:
        active_url = get_active_ngrok_url()
        if not active_url:
            log_app("⚠️ Aucune URL ngrok active - pas de mise à jour des endpoints", "WARNING")
            return False
        
        log_app(f"🔄 Mise à jour des endpoints Facebook avec: {active_url}", "INFO")
        
        # Mettre à jour l'URL globale si nécessaire
        global NGROK_URL
        if NGROK_URL != active_url:
            NGROK_URL = active_url
            log_app(f"✅ URL globale ngrok mise à jour: {NGROK_URL}", "SUCCESS")
        
        # Mettre à jour le frontend .env avec l'URL active
        try:
            frontend_env_path = os.path.join(WINDOWS_PATHS["project_root"], "frontend", ".env")
            if os.path.exists(frontend_env_path):
                with open(frontend_env_path, "r", encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.splitlines()
                updated_lines = []
                backend_url_updated = False
                for line in lines:
                    if line.startswith("REACT_APP_BACKEND_URL="):
                        updated_lines.append(f"REACT_APP_BACKEND_URL={active_url}")
                        backend_url_updated = True
                    else:
                        updated_lines.append(line)
                
                if not backend_url_updated:
                    updated_lines.append(f"REACT_APP_BACKEND_URL={active_url}")
                
                with open(frontend_env_path, "w", encoding='utf-8') as f:
                    f.write("\n".join(updated_lines))
                    if updated_lines:
                        f.write("\n")
                log_app(f"✅ Frontend .env synchronisé avec URL active", "SUCCESS")
        except Exception as e:
            log_app(f"⚠️ Erreur mise à jour frontend .env: {e}", "WARNING")
        
        # Mettre à jour la configuration Facebook OAuth
        try:
            update_facebook_oauth_config(active_url)
        except Exception as e:
            log_app(f"⚠️ Erreur mise à jour Facebook OAuth: {e}", "WARNING")
        
        return True
        
    except Exception as e:
        log_app(f"❌ Erreur mise à jour endpoints Facebook: {e}", "ERROR")
        return False

# === LIFESPAN CONTEXT MANAGER ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan events - startup and shutdown - VERSION CORRIGÉE AVEC AUTO-CONFIG FACEBOOK"""
    # Startup
    log_app("🚀 Meta Publishing Platform - Version Windows CORRIGÉE", "START")
    log_app(f"📁 Répertoire backend: {WINDOWS_PATHS['backend_dir']}", "INFO")
    log_app(f"🌐 Port backend: {BACKEND_PORT}", "INFO")
    log_app(f"🔧 Mode test: {PUBLICATION_TEST_MODE}", "INFO")
    
    # Connect to MongoDB
    mongo_connected = await connect_to_mongo()
    if not mongo_connected:
        log_app("⚠️ MongoDB non disponible - fonctionnement en mode limité", "WARNING")
    
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
            sync_result = sync_frontend_env_with_ngrok()
            if sync_result:
                log_app("✅ Frontend .env synchronisé avec succès", "SUCCESS")
            
            # NOUVELLE FONCTIONNALITÉ: Configuration automatique Facebook OAuth
            log_app("🔧 Configuration automatique Facebook OAuth...", "INFO")
            oauth_result = auto_configure_facebook_oauth()
            if oauth_result:
                log_app("✅ Facebook OAuth configuré automatiquement", "SUCCESS")
            else:
                log_app("⚠️ Configuration Facebook OAuth échouée ou partielle", "WARNING")
            
            log_app("ℹ️ 🔄 Attente de la synchronisation complète...", "INFO")
            time.sleep(2)  # Laisser le temps à toutes les configurations de se finaliser
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
    await close_mongo_connection()
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

class PublishRequest(BaseModel):
    store: str
    message: str
    product_url: str
    image_url: Optional[str] = None
    platforms: List[str] = ["facebook", "instagram"]

class TestPublishRequest(BaseModel):
    stores: Optional[List[str]] = None  # Si None, publie sur tous les stores
    platforms: List[str] = ["facebook"]  # facebook, instagram
    custom_message: Optional[str] = None  # Si None, utilise TEST_MESSAGE de .env
    
    @field_validator('platforms')
    @classmethod
    def validate_platforms(cls, v):
        valid_platforms = ["facebook", "instagram"]
        for platform in v:
            if platform not in valid_platforms:
                raise ValueError(f'Platform must be one of: {valid_platforms}')
        return v

class VideoPublishRequest(BaseModel):
    store: str
    message: str
    product_url: str
    platforms: List[str] = ["facebook", "instagram"]
    
    @field_validator('platforms')
    @classmethod
    def validate_platforms(cls, v):
        valid_platforms = ["facebook", "instagram"]
        for platform in v:
            if platform not in valid_platforms:
                raise ValueError(f'Platform must be one of: {valid_platforms}')
        return v

class VideoUploadResponse(BaseModel):
    success: bool
    video_url: Optional[str] = None
    filename: Optional[str] = None
    file_size: Optional[int] = None
    validation: Optional[dict] = None
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

# === PYDANTIC MODELS FOR POSTS ===
class PostBase(BaseModel):
    content: str
    platform: str
    platform_id: str
    scheduled_time: Optional[str] = None
    media_urls: Optional[List[str]] = []

class Post(PostBase):
    id: str
    user_id: str
    status: str = "draft"
    created_at: str
    published_at: Optional[str] = None
    platform_post_id: Optional[str] = None

# MongoDB handles post storage now

# === PUBLICATION FUNCTIONS ===
def log_publish(message: str, level: str = "INFO"):
    """Logging spécialisé pour les publications"""
    icons = {"INFO": "📢", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
    icon = icons.get(level.upper(), "📢")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [PUBLISH] {message}")

async def update_instagram_ids():
    """Mettre à jour automatiquement les IDs Instagram via l'API Graph"""
    try:
        log_app("🔄 Mise à jour automatique des IDs Instagram...", "INFO")
        
        for store_name, config in STORES.items():
            if config.get("access_token") and config.get("fb_page_id"):
                try:
                    # Récupérer le compte Instagram Business associé à la page
                    url = f"{FACEBOOK_GRAPH_URL}/{config['fb_page_id']}"
                    params = {
                        "fields": "instagram_business_account",
                        "access_token": config["access_token"]
                    }
                    
                    response = requests.get(url, params=params, timeout=15)
                    response.raise_for_status()
                    data = response.json()
                    
                    if "instagram_business_account" in data and data["instagram_business_account"]:
                        ig_id = data["instagram_business_account"]["id"]
                        STORES[store_name]["ig_user_id"] = ig_id
                        log_app(f"✅ {store_name}: Instagram ID récupéré → {ig_id}", "SUCCESS")
                    else:
                        log_app(f"⚠️ {store_name}: Aucun compte Instagram Business connecté", "WARNING")
                        
                except Exception as e:
                    log_app(f"❌ {store_name}: Erreur récupération Instagram ID → {str(e)}", "ERROR")
            else:
                log_app(f"⚠️ {store_name}: Token d'accès ou Page ID manquant", "WARNING")
        
        log_app("🎯 Mise à jour des IDs Instagram terminée", "SUCCESS")
        
    except Exception as e:
        log_app(f"❌ Erreur générale mise à jour Instagram: {str(e)}", "ERROR")

async def post_to_facebook(store: str, message: str, product_url: str) -> dict:
    """Publie un post sur la page Facebook correspondante"""
    try:
        log_publish(f"Publication Facebook pour {store}", "INFO")
        
        if store not in STORES:
            raise ValueError(f"Store inconnu: {store}")
        
        creds = get_store_config(store)
        
        if not creds["fb_page_id"] or not creds["access_token"]:
            raise ValueError(f"Configuration Facebook manquante pour {store}")
        
        # Mode test : simulation
        if PUBLICATION_TEST_MODE:
            log_publish(f"MODE TEST - Publication Facebook simulée pour {store}", "TEST")
            return {
                "id": f"test_fb_post_{uuid.uuid4().hex[:8]}",
                "message": message,
                "link": product_url,
                "test_mode": True
            }
        
        # Publication réelle
        url = f"{FACEBOOK_GRAPH_URL}/{creds['fb_page_id']}/feed"
        payload = {
            "message": message,
            "link": product_url,
            "access_token": creds["access_token"]
        }
        
        log_publish(f"Requête Facebook: POST {url}", "INFO")
        response = requests.post(url, data=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if "id" not in data:
            raise Exception(f"Réponse Facebook invalide: {data}")
        
        log_publish(f"Publication Facebook réussie: {data['id']}", "SUCCESS")
        return data
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Erreur HTTP Facebook: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_msg += f" - {error_data}"
            except:
                error_msg += f" - Status: {e.response.status_code}"
        log_publish(error_msg, "ERROR")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Erreur Facebook: {str(e)}"
        log_publish(error_msg, "ERROR")
        raise Exception(error_msg)

async def post_to_instagram(store: str, message: str, product_url: str, image_url: str) -> dict:
    """Publie une image avec légende sur Instagram (processus en 2 étapes)"""
    try:
        log_publish(f"Publication Instagram pour {store}", "INFO")
        
        if store not in STORES:
            raise ValueError(f"Store inconnu: {store}")
        
        creds = get_store_config(store)
        
        if not creds["ig_user_id"] or not creds["access_token"]:
            raise ValueError(f"Configuration Instagram manquante pour {store}")
        
        if not image_url:
            raise ValueError("Image URL requise pour Instagram")
        
        # Mode test : simulation
        if PUBLICATION_TEST_MODE:
            log_publish(f"MODE TEST - Publication Instagram simulée pour {store}", "TEST")
            return {
                "id": f"test_ig_post_{uuid.uuid4().hex[:8]}",
                "caption": f"{message}\\n\\n{product_url}",
                "image_url": image_url,
                "test_mode": True
            }
        
        ig_user_id = creds["ig_user_id"]
        access_token = creds["access_token"]
        
        # Étape 1 : Créer le conteneur média
        log_publish("Étape 1/2 - Création conteneur média Instagram", "INFO")
        create_url = f"{FACEBOOK_GRAPH_URL}/{ig_user_id}/media"
        
        create_payload = {
            "image_url": image_url,
            "caption": f"{message}\\n\\n{product_url}",
            "access_token": access_token
        }
        
        create_response = requests.post(create_url, data=create_payload, timeout=30)
        create_response.raise_for_status()
        
        media_data = create_response.json()
        
        if "id" not in media_data:
            raise Exception(f"Erreur création conteneur Instagram: {media_data}")
        
        creation_id = media_data["id"]
        log_publish(f"Conteneur créé: {creation_id}", "SUCCESS")
        
        # Étape 2 : Publier le média
        log_publish("Étape 2/2 - Publication du média Instagram", "INFO")
        publish_url = f"{FACEBOOK_GRAPH_URL}/{ig_user_id}/media_publish"
        
        publish_payload = {
            "creation_id": creation_id,
            "access_token": access_token
        }
        
        publish_response = requests.post(publish_url, data=publish_payload, timeout=30)
        publish_response.raise_for_status()
        
        publish_data = publish_response.json()
        
        if "id" not in publish_data:
            raise Exception(f"Erreur publication Instagram: {publish_data}")
        
        log_publish(f"Publication Instagram réussie: {publish_data['id']}", "SUCCESS")
        
        # Retourner les données combinées
        return {
            "id": publish_data["id"],
            "creation_id": creation_id,
            "caption": f"{message}\\n\\n{product_url}",
            "image_url": image_url
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Erreur HTTP Instagram: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_msg += f" - {error_data}"
            except:
                error_msg += f" - Status: {e.response.status_code}"
        log_publish(error_msg, "ERROR")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Erreur Instagram: {str(e)}"
        log_publish(error_msg, "ERROR")
        raise Exception(error_msg)

async def post_video_to_facebook(store: str, message: str, product_url: str, video_url: str) -> dict:
    """Publie une vidéo sur la page Facebook correspondante"""
    try:
        log_video(f"Publication vidéo Facebook pour {store}", "INFO")
        
        if store not in STORES:
            raise ValueError(f"Store inconnu: {store}")
        
        creds = get_store_config(store)
        
        if not creds["fb_page_id"] or not creds["access_token"]:
            raise ValueError(f"Configuration Facebook manquante pour {store}")
        
        # Mode test : simulation
        if PUBLICATION_TEST_MODE:
            log_video(f"MODE TEST - Publication vidéo Facebook simulée pour {store}", "TEST")
            return {
                "id": f"test_fb_video_{uuid.uuid4().hex[:8]}",
                "message": message,
                "source": video_url,
                "test_mode": True
            }
        
        # Publication réelle
        url = f"{FACEBOOK_GRAPH_URL}/{creds['fb_page_id']}/videos"
        payload = {
            "description": message,
            "source": video_url,
            "access_token": creds["access_token"]
        }
        
        log_video(f"Requête Facebook Videos: POST {url}", "INFO")
        response = requests.post(url, data=payload, timeout=120)  # Timeout plus long pour les vidéos
        response.raise_for_status()
        
        data = response.json()
        
        if "id" not in data:
            raise Exception(f"Réponse Facebook invalide: {data}")
        
        log_video(f"Publication vidéo Facebook réussie: {data['id']}", "SUCCESS")
        return data
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Erreur HTTP Facebook Videos: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_msg += f" - {error_data}"
            except:
                error_msg += f" - Status: {e.response.status_code}"
        log_video(error_msg, "ERROR")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Erreur Facebook Videos: {str(e)}"
        log_video(error_msg, "ERROR")
        raise Exception(error_msg)

async def post_video_to_instagram(store: str, message: str, product_url: str, video_url: str) -> dict:
    """Publie une vidéo (Reel) sur Instagram (processus en 2 étapes)"""
    try:
        log_video(f"Publication vidéo Instagram pour {store}", "INFO")
        
        if store not in STORES:
            raise ValueError(f"Store inconnu: {store}")
        
        creds = get_store_config(store)
        
        if not creds["ig_user_id"] or not creds["access_token"]:
            raise ValueError(f"Configuration Instagram manquante pour {store}")
        
        if not video_url:
            raise ValueError("URL vidéo requise pour Instagram")
        
        # Mode test : simulation
        if PUBLICATION_TEST_MODE:
            log_video(f"MODE TEST - Publication vidéo Instagram simulée pour {store}", "TEST")
            return {
                "id": f"test_ig_video_{uuid.uuid4().hex[:8]}",
                "caption": f"{message}\\n\\n{product_url}",
                "video_url": video_url,
                "test_mode": True
            }
        
        ig_user_id = creds["ig_user_id"]
        access_token = creds["access_token"]
        
        # Étape 1 : Créer le conteneur média vidéo (Reel)
        log_video("Étape 1/2 - Création conteneur vidéo Instagram", "INFO")
        create_url = f"{FACEBOOK_GRAPH_URL}/{ig_user_id}/media"
        
        create_payload = {
            "video_url": video_url,
            "caption": f"{message}\\n\\n{product_url}",
            "media_type": "REELS",  # Utiliser REELS pour les vidéos courtes
            "access_token": access_token
        }
        
        create_response = requests.post(create_url, data=create_payload, timeout=120)
        create_response.raise_for_status()
        
        media_data = create_response.json()
        
        if "id" not in media_data:
            raise Exception(f"Erreur création conteneur vidéo Instagram: {media_data}")
        
        creation_id = media_data["id"]
        log_video(f"Conteneur vidéo créé: {creation_id}", "SUCCESS")
        
        # Attendre que la vidéo soit traitée (Instagram nécessite plus de temps pour les vidéos)
        log_video("Attente traitement vidéo Instagram...", "INFO")
        await asyncio.sleep(10)  # Attendre 10 secondes
        
        # Étape 2 : Publier le média
        log_video("Étape 2/2 - Publication du média vidéo Instagram", "INFO")
        publish_url = f"{FACEBOOK_GRAPH_URL}/{ig_user_id}/media_publish"
        
        publish_payload = {
            "creation_id": creation_id,
            "access_token": access_token
        }
        
        publish_response = requests.post(publish_url, data=publish_payload, timeout=60)
        publish_response.raise_for_status()
        
        publish_data = publish_response.json()
        
        if "id" not in publish_data:
            raise Exception(f"Erreur publication vidéo Instagram: {publish_data}")
        
        log_video(f"Publication vidéo Instagram réussie: {publish_data['id']}", "SUCCESS")
        
        # Retourner les données combinées
        return {
            "id": publish_data["id"],
            "creation_id": creation_id,
            "caption": f"{message}\\n\\n{product_url}",
            "video_url": video_url
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Erreur HTTP Instagram Videos: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_msg += f" - {error_data}"
            except:
                error_msg += f" - Status: {e.response.status_code}"
        log_video(error_msg, "ERROR")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Erreur Instagram Videos: {str(e)}"
        log_video(error_msg, "ERROR")
        raise Exception(error_msg)

async def publish_video_main(store: str, message: str, product_url: str, video_url: str, platforms: List[str] = ["facebook", "instagram"]) -> dict:
    """Fonction principale pour publier une vidéo sur Facebook et/ou Instagram"""
    try:
        log_video(f"Début publication vidéo multi-plateforme pour {store} sur {platforms}", "INFO")
        
        if store not in STORES:
            raise ValueError(f"Store inconnu: {store}")
        
        results = {
            "success": False,
            "store": store,
            "platforms": platforms,
            "facebook_result": None,
            "instagram_result": None,
            "errors": [],
            "test_mode": PUBLICATION_TEST_MODE,
            "video_url": video_url
        }
        
        # Publication Facebook
        if "facebook" in platforms:
            try:
                fb_result = await post_video_to_facebook(store, message, product_url, video_url)
                results["facebook_result"] = fb_result
                log_video("Publication vidéo Facebook terminée", "SUCCESS")
            except Exception as e:
                error_msg = f"Échec Facebook vidéo: {str(e)}"
                results["errors"].append(error_msg)
                log_video(error_msg, "ERROR")
        
        # Publication Instagram
        if "instagram" in platforms:
            try:
                ig_result = await post_video_to_instagram(store, message, product_url, video_url)
                results["instagram_result"] = ig_result
                log_video("Publication vidéo Instagram terminée", "SUCCESS")
            except Exception as e:
                error_msg = f"Échec Instagram vidéo: {str(e)}"
                results["errors"].append(error_msg)
                log_video(error_msg, "ERROR")
        
        # Déterminer le succès global
        success_count = 0
        if "facebook" in platforms and results["facebook_result"]:
            success_count += 1
        if "instagram" in platforms and results["instagram_result"]:
            success_count += 1
        
        results["success"] = success_count > 0 and len(results["errors"]) == 0
        
        if results["success"]:
            log_video(f"Publication vidéo multi-plateforme réussie pour {store}", "SUCCESS")
        else:
            log_video(f"Publication vidéo partiellement échouée pour {store}: {results['errors']}", "WARNING")
        
        return results
        
    except Exception as e:
        error_msg = f"Erreur générale publication vidéo: {str(e)}"
        log_video(error_msg, "ERROR")
        return {
            "success": False,
            "store": store,
            "platforms": platforms,
            "facebook_result": None,
            "instagram_result": None,
            "errors": [error_msg],
            "test_mode": PUBLICATION_TEST_MODE,
            "video_url": video_url
        }

async def publish_post_main(store: str, message: str, product_url: str, image_url: Optional[str] = None, platforms: List[str] = ["facebook", "instagram"]) -> dict:
    """Fonction principale pour publier sur Facebook et/ou Instagram"""
    try:
        log_publish(f"Début publication multi-plateforme pour {store} sur {platforms}", "INFO")
        
        if store not in STORES:
            raise ValueError(f"Store inconnu: {store}")
        
        results = {
            "success": False,
            "store": store,
            "platforms": platforms,
            "facebook_result": None,
            "instagram_result": None,
            "errors": [],
            "test_mode": PUBLICATION_TEST_MODE
        }
        
        # Publication Facebook
        if "facebook" in platforms:
            try:
                fb_result = await post_to_facebook(store, message, product_url)
                results["facebook_result"] = fb_result
                log_publish("Publication Facebook terminée", "SUCCESS")
            except Exception as e:
                error_msg = f"Échec Facebook: {str(e)}"
                results["errors"].append(error_msg)
                log_publish(error_msg, "ERROR")
        
        # Publication Instagram
        if "instagram" in platforms:
            try:
                if not image_url:
                    raise Exception("Image requise pour Instagram")
                
                ig_result = await post_to_instagram(store, message, product_url, image_url)
                results["instagram_result"] = ig_result
                log_publish("Publication Instagram terminée", "SUCCESS")
            except Exception as e:
                error_msg = f"Échec Instagram: {str(e)}"
                results["errors"].append(error_msg)
                log_publish(error_msg, "ERROR")
        
        # Déterminer le succès global
        success_count = 0
        if "facebook" in platforms and results["facebook_result"]:
            success_count += 1
        if "instagram" in platforms and results["instagram_result"]:
            success_count += 1
        
        results["success"] = success_count > 0 and len(results["errors"]) == 0
        
        if results["success"]:
            log_publish(f"Publication multi-plateforme réussie pour {store}", "SUCCESS")
        else:
            log_publish(f"Publication partiellement échouée pour {store}: {results['errors']}", "WARNING")
        
        return results
        
    except Exception as e:
        error_msg = f"Erreur générale publication: {str(e)}"
        log_publish(error_msg, "ERROR")
        return {
            "success": False,
            "store": store,
            "platforms": platforms,
            "facebook_result": None,
            "instagram_result": None,
            "errors": [error_msg],
            "test_mode": PUBLICATION_TEST_MODE
        }

# === API ENDPOINTS ===

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# === VIDEO ENDPOINTS ===

@app.post("/api/videos/upload")
async def upload_video_endpoint(video: UploadFile = File(...), filename: str = Form(None)):
    """Upload une vidéo vers le serveur FTP"""
    try:
        log_video(f"Début upload vidéo: {video.filename}", "UPLOAD")
        
        # Validation du fichier
        if not video.filename:
            raise HTTPException(status_code=400, detail="Nom de fichier manquant")
        
        # Vérifier le type MIME
        if video.content_type not in SUPPORTED_VIDEO_FORMATS:
            raise HTTPException(
                status_code=400, 
                detail=f"Format non supporté: {video.content_type}. Formats supportés: {SUPPORTED_VIDEO_FORMATS}"
            )
        
        # Créer un fichier temporaire
        temp_filename = filename or f"video_{uuid.uuid4().hex[:8]}_{video.filename}"
        temp_path = os.path.join(UPLOAD_DIR, temp_filename)
        
        # Sauvegarder le fichier temporairement
        with open(temp_path, "wb") as buffer:
            content = await video.read()
            buffer.write(content)
        
        # Valider la vidéo
        validation = validate_video_file(temp_path)
        if not validation["valid"]:
            os.remove(temp_path)
            raise HTTPException(status_code=400, detail=validation["error"])
        
        # Upload vers FTP
        success, public_url, error = await upload_video_to_ftp(temp_path, temp_filename)
        
        # Nettoyer le fichier temporaire
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if not success:
            raise HTTPException(status_code=500, detail=error or "Erreur upload FTP")
        
        # Sauvegarder les métadonnées en base de données
        video_data = {
            "id": str(uuid.uuid4()),
            "filename": temp_filename,
            "original_filename": video.filename,
            "video_url": public_url,
            "file_size": validation["file_size"],
            "mime_type": video.content_type,
            "validation": validation,
            "status": "uploaded",
            "created_at": datetime.now().isoformat(),
            "duration": None,  # Sera mis à jour si disponible
            "thumbnail_url": None,
            "compatible_platforms": get_compatible_platforms(validation)
        }
        
        # Sauvegarder en MongoDB si disponible
        try:
            # TODO: Implémenter la sauvegarde MongoDB des vidéos
            pass
        except Exception as e:
            log_video(f"Erreur sauvegarde MongoDB: {str(e)}", "WARNING")
        
        log_video(f"Upload réussi: {public_url}", "SUCCESS")
        
        return {
            "success": True,
            "video_url": public_url,
            "filename": temp_filename,
            "file_size": validation["file_size"],
            "validation": validation,
            **video_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_video(f"Erreur upload vidéo: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

def get_compatible_platforms(validation):
    """Détermine les plateformes compatibles selon la validation"""
    platforms = []
    
    if validation.get("valid"):
        file_size = validation.get("file_size", 0)
        
        # Facebook: jusqu'à 10 GB, 15 minutes
        if file_size <= MAX_VIDEO_SIZE_FACEBOOK:
            platforms.append("facebook")
        
        # Instagram: jusqu'à 1 GB, 60 secondes
        if file_size <= MAX_VIDEO_SIZE_INSTAGRAM:
            platforms.append("instagram")
    
    return platforms

@app.get("/api/videos/library")
async def get_video_library():
    """Récupère la bibliothèque de vidéos uploadées"""
    try:
        # TODO: Récupérer depuis MongoDB
        # Pour l'instant, retourner une liste vide
        videos = []
        
        return {
            "success": True,
            "videos": videos,
            "count": len(videos)
        }
        
    except Exception as e:
        log_video(f"Erreur chargement bibliothèque: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/videos/{video_id}")
async def delete_video_endpoint(video_id: str):
    """Supprime une vidéo de la bibliothèque"""
    try:
        # TODO: Implémenter la suppression depuis MongoDB et FTP
        log_video(f"Suppression vidéo: {video_id}", "INFO")
        
        return {
            "success": True,
            "message": "Vidéo supprimée avec succès"
        }
        
    except Exception as e:
        log_video(f"Erreur suppression vidéo: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/posts/video")
async def create_video_post_endpoint(
    user_id: str = Form(...),
    content: str = Form(...),
    video_url: str = Form(...),
    video_id: str = Form(...),
    target_type: str = Form(...),
    target_id: str = Form(...),
    target_name: str = Form(...),
    platform: str = Form(...),
    business_manager_id: str = Form(None),
    business_manager_name: str = Form(None),
    scheduled_time: str = Form(None),
    cross_post_targets: str = Form(None),
    video_metadata: str = Form(None)
):
    """Crée un post vidéo pour publication"""
    try:
        log_video(f"Création post vidéo pour {platform}", "INFO")
        
        # Parser les métadonnées vidéo
        metadata = {}
        if video_metadata:
            try:
                metadata = json.loads(video_metadata)
            except json.JSONDecodeError:
                log_video("Erreur parsing métadonnées vidéo", "WARNING")
        
        # Parser les cibles de publication croisée
        cross_targets = []
        if cross_post_targets:
            try:
                cross_targets = json.loads(cross_post_targets)
            except json.JSONDecodeError:
                log_video("Erreur parsing cibles publication croisée", "WARNING")
        
        # Créer le post en base de données
        post_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "content": content,
            "video_url": video_url,
            "video_id": video_id,
            "video_metadata": metadata,
            "target_type": target_type,
            "target_id": target_id,
            "target_name": target_name,
            "platform": platform,
            "business_manager_id": business_manager_id,
            "business_manager_name": business_manager_name,
            "cross_post_targets": cross_targets,
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "scheduled_time": scheduled_time,
            "published_at": None,
            "platform_post_id": None,
            "media_urls": [video_url]
        }
        
        # Sauvegarder en MongoDB
        try:
            await create_post(post_data)
        except Exception as e:
            log_video(f"Erreur sauvegarde post MongoDB: {str(e)}", "WARNING")
        
        log_video(f"Post vidéo créé: {post_data['id']}", "SUCCESS")
        
        return {
            "success": True,
            "post": post_data,
            "message": "Post vidéo créé avec succès"
        }
        
    except Exception as e:
        log_video(f"Erreur création post vidéo: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/posts/video/history")
async def get_video_history_endpoint(user_id: str):
    """Récupère l'historique des publications vidéo d'un utilisateur"""
    try:
        log_video(f"Chargement historique vidéo pour utilisateur: {user_id}", "INFO")
        
        # TODO: Récupérer depuis MongoDB
        # Pour l'instant, retourner une liste d'exemple
        videos = []
        
        return {
            "success": True,
            "videos": videos,
            "count": len(videos)
        }
        
    except Exception as e:
        log_video(f"Erreur chargement historique vidéo: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

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
            
            # NOUVEAU: Sauvegarder le token utilisateur avec gestion d'expiration
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

@app.get("/api/auth/token-status/{user_id}")
async def check_token_status(user_id: str):
    """Vérifier le statut du token utilisateur"""
    try:
        token_record = await get_user_token(user_id)
        
        if not token_record:
            return {
                "success": False,
                "has_token": False,
                "message": "Aucun token trouvé pour cet utilisateur"
            }
        
        is_expired = await is_token_expired(user_id)
        expires_at = token_record.get("expires_at", 0)
        current_time = datetime.now().timestamp()
        remaining_seconds = max(0, expires_at - current_time)
        
        return {
            "success": True,
            "has_token": True,
            "is_expired": is_expired,
            "expires_at": expires_at,
            "remaining_seconds": remaining_seconds,
            "remaining_minutes": remaining_seconds / 60,
            "token_created": token_record.get("created_at"),
            "token_updated": token_record.get("updated_at")
        }
        
    except Exception as e:
        log_app(f"❌ Erreur vérification token: {str(e)}", "ERROR")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/auth/refresh-token/{user_id}")
async def refresh_user_token(user_id: str):
    """Rafraîchir le token utilisateur"""
    try:
        refreshed_token = await refresh_facebook_token(user_id)
        
        if refreshed_token:
            expires_at = refreshed_token.get("expires_at", 0)
            current_time = datetime.now().timestamp()
            remaining_seconds = max(0, expires_at - current_time)
            
            return {
                "success": True,
                "message": "Token rafraîchi avec succès",
                "expires_at": expires_at,
                "remaining_seconds": remaining_seconds,
                "remaining_minutes": remaining_seconds / 60
            }
        else:
            return {
                "success": False,
                "error": "Impossible de rafraîchir le token"
            }
            
    except Exception as e:
        log_app(f"❌ Erreur rafraîchissement token: {str(e)}", "ERROR")
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

@app.get("/api/config/oauth-status-complete")
async def oauth_status_complete():
    """Retourne le statut complet de la configuration OAuth avec détails Facebook"""
    try:
        ngrok_url = get_active_ngrok_url()
        redirect_uri = build_dynamic_redirect_uri("/")
        
        # Vérifier la configuration Facebook en détail
        facebook_config_status = {
            "app_id_configured": bool(FACEBOOK_APP_ID),
            "app_secret_configured": bool(FACEBOOK_APP_SECRET),
            "client_token_configured": bool(FACEBOOK_CLIENT_TOKEN),
            "direct_token_configured": bool(os.getenv("FACEBOOK_DIRECT_TOKEN"))
        }
        
        # Test de connectivité Facebook si possible
        facebook_connectivity = False
        if FACEBOOK_APP_ID and FACEBOOK_APP_SECRET:
            try:
                app_access_token = f"{FACEBOOK_APP_ID}|{FACEBOOK_APP_SECRET}"
                test_url = f"{FACEBOOK_GRAPH_URL}/{FACEBOOK_APP_ID}"
                test_response = requests.get(test_url, params={"access_token": app_access_token}, timeout=10)
                facebook_connectivity = test_response.status_code == 200
            except Exception:
                facebook_connectivity = False
        
        return {
            "ngrok_active": ngrok_url is not None,
            "ngrok_url": ngrok_url,
            "redirect_uri": redirect_uri,
            "facebook_config": facebook_config_status,
            "facebook_connectivity": facebook_connectivity,
            "oauth_ready": bool(ngrok_url and FACEBOOK_APP_ID and FACEBOOK_APP_SECRET),
            "auto_config_completed": bool(ngrok_url and facebook_connectivity),
            "timestamp": datetime.now().isoformat(),
            "redirect_uris_configured": [
                f"{ngrok_url}/",
                f"{ngrok_url}/auth/callback", 
                f"{ngrok_url}/auth/callb"
            ] if ngrok_url else []
        }
        
    except Exception as e:
        log_app(f"❌ Erreur status OAuth complet: {str(e)}", "ERROR")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/config/force-oauth-setup")
async def force_oauth_setup():
    """Force la configuration OAuth avec l'URL ngrok du frontend .env"""
    try:
        log_app("🔧 Configuration OAuth forcée demandée", "INFO")
        
        # Récupérer l'URL du frontend .env
        frontend_env_path = os.path.join(WINDOWS_PATHS["project_root"], "frontend", ".env")
        backend_url = None
        
        if os.path.exists(frontend_env_path):
            with open(frontend_env_path, "r", encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    backend_url = line.split("=", 1)[1].strip()
                    break
        
        if not backend_url:
            return {
                "success": False,
                "error": "URL backend non trouvée dans frontend .env",
                "timestamp": datetime.now().isoformat()
            }
        
        if not backend_url.startswith("https://"):
            return {
                "success": False,
                "error": "URL backend doit être HTTPS pour OAuth",
                "backend_url": backend_url,
                "timestamp": datetime.now().isoformat()
            }
        
        log_app(f"🎯 Configuration OAuth avec URL: {backend_url}", "INFO")
        
        # Mettre à jour l'URL globale
        global NGROK_URL
        NGROK_URL = backend_url
        
        # Configurer Facebook OAuth
        oauth_result = update_facebook_oauth_config(backend_url)
        
        if oauth_result:
            log_app("✅ Configuration Facebook OAuth forcée réussie", "SUCCESS")
            return {
                "success": True,
                "message": "Configuration OAuth mise à jour avec succès",
                "backend_url": backend_url,
                "redirect_uris": [
                    f"{backend_url}/",
                    f"{backend_url}/auth/callback",
                    f"{backend_url}/auth/callb"
                ],
                "timestamp": datetime.now().isoformat()
            }
        else:
            log_app("⚠️ Configuration Facebook OAuth forcée partiellement réussie", "WARNING")
            return {
                "success": True,
                "warning": "Configuration partiellement réussie",
                "backend_url": backend_url,
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        log_app(f"❌ Erreur configuration OAuth forcée: {str(e)}", "ERROR")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
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

@app.get("/api/debug/instagram-complete-diagnosis")
async def instagram_complete_diagnosis_endpoint():
    """Complete Instagram diagnosis endpoint"""
    try:
        diagnosis = await instagram_complete_diagnosis()
        return diagnosis
    except Exception as e:
        log_app(f"❌ Erreur diagnostic Instagram: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/posts")
async def get_posts(user_id: str):
    """Get posts for a specific user"""
    try:
        log_app(f"Récupération des posts pour l'utilisateur: {user_id}", "INFO")
        
        user_posts = await get_posts_by_user(user_id)
        
        return {
            "success": True,
            "posts": user_posts,
            "total": len(user_posts)
        }
    except Exception as e:
        log_app(f"❌ Erreur récupération posts: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/posts")
async def create_post_endpoint(request: Request):
    """Create a new post - Accept both JSON and FormData"""
    try:
        post_data = {}
        
        # Determine content type and parse accordingly
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            # JSON request
            post_data = await request.json()
        elif "multipart/form-data" in content_type:
            # FormData request
            form = await request.form()
            for key, value in form.items():
                if key == 'cross_post_targets':
                    # Parse JSON string for cross post targets
                    try:
                        post_data[key] = json.loads(value)
                    except:
                        post_data[key] = []
                else:
                    post_data[key] = value
        else:
            raise HTTPException(status_code=400, detail="Content-Type non supporté")
        
        if not post_data:
            raise HTTPException(status_code=400, detail="Données de post manquantes")
        
        # Generate post ID
        post_id = str(uuid.uuid4())
        
        # Create post object
        new_post = {
            "id": post_id,
            "user_id": post_data.get("user_id"),
            "content": post_data.get("content", ""),
            "platform": post_data.get("platform", "facebook"),
            "platform_id": post_data.get("platform_id", ""),
            "target_type": post_data.get("target_type", ""),
            "target_id": post_data.get("target_id", ""),
            "target_name": post_data.get("target_name", ""),
            "business_manager_id": post_data.get("business_manager_id"),
            "business_manager_name": post_data.get("business_manager_name"),
            "scheduled_time": post_data.get("scheduled_time"),
            "media_urls": post_data.get("media_urls", []),
            "cross_post_targets": post_data.get("cross_post_targets", []),
            "comment_text": post_data.get("comment_text", ""),
            "comment_link": post_data.get("comment_link", ""),
            "status": "draft",
            "published_at": None,
            "platform_post_id": None
        }
        
        # Save to MongoDB
        created_post = await create_post(new_post)
        
        log_app(f"✅ Post créé: {post_id}", "SUCCESS")
        
        return {
            "success": True,
            "post": created_post
        }
        
    except Exception as e:
        log_app(f"❌ Erreur création post: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/posts/{post_id}")
async def delete_post_endpoint(post_id: str):
    """Delete a post"""
    try:
        success = await delete_post(post_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Post non trouvé")
        
        log_app(f"✅ Post supprimé: {post_id}", "SUCCESS")
        
        return {
            "success": True,
            "message": "Post supprimé avec succès"
        }
        
    except Exception as e:
        log_app(f"❌ Erreur suppression post: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/posts/{post_id}/publish")
async def publish_post_endpoint(post_id: str):
    """Publish a post immediately"""
    try:
        post = await get_post_by_id(post_id)
        
        if not post:
            raise HTTPException(status_code=404, detail="Post non trouvé")
        
        # Update post status in MongoDB
        update_data = {
            "status": "published",
            "published_at": datetime.now().isoformat()
        }
        
        updated_post = await update_post(post_id, update_data)
        
        log_app(f"✅ Post publié: {post_id}", "SUCCESS")
        
        return {
            "success": True,
            "post": updated_post,
            "message": "Post publié avec succès"
        }
        
    except Exception as e:
        log_app(f"❌ Erreur publication post: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/publish")
async def publish_post_endpoint(request: PublishRequest):
    """Publier un post sur les plateformes sélectionnées"""
    try:
        log_app(f"Demande de publication pour {request.store} sur {request.platforms}", "INFO")
        
        if request.store not in STORES:
            raise HTTPException(status_code=400, detail=f"Store '{request.store}' inconnu")
        
        store_config = get_store_config(request.store)
        
        # Vérifier la configuration du store
        missing_config = []
        if "facebook" in request.platforms:
            if not store_config.get("fb_page_id"):
                missing_config.append("fb_page_id")
            if not store_config.get("access_token"):
                missing_config.append("access_token")
        
        if "instagram" in request.platforms:
            if not store_config.get("ig_user_id"):
                missing_config.append("ig_user_id")
            if not store_config.get("access_token"):
                missing_config.append("access_token")
            if not request.image_url:
                missing_config.append("image_url (required for Instagram)")
        
        if missing_config:
            return {
                "success": False,
                "error": f"Configuration manquante pour {request.store}: {', '.join(missing_config)}",
                "store_config": {
                    "fb_page_id": bool(store_config.get("fb_page_id")),
                    "access_token": bool(store_config.get("access_token")),
                    "ig_user_id": bool(store_config.get("ig_user_id"))
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # Effectuer la publication
        result = await publish_post_main(
            request.store,
            request.message,
            request.product_url,
            request.image_url,
            request.platforms
        )
        
        # Ajouter des informations de debug
        result.update({
            "store_config": {
                "fb_page_id": store_config.get("fb_page_id", "")[:10] + "..." if store_config.get("fb_page_id") else None,
                "access_token": "PRÉSENT" if store_config.get("access_token") else None,
                "ig_user_id": store_config.get("ig_user_id", "")[:10] + "..." if store_config.get("ig_user_id") else None
            },
            "timestamp": datetime.now().isoformat()
        })
        
        log_app(f"Publication terminée pour {request.store}: {'✅ Succès' if result['success'] else '❌ Échec'}", "SUCCESS" if result["success"] else "ERROR")
        
        return result
        
    except Exception as e:
        error_msg = f"Erreur endpoint publication: {str(e)}"
        log_app(error_msg, "ERROR")
        return {
            "success": False,
            "error": error_msg,
            "store": request.store,
            "platforms": request.platforms,
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/test-publish")
async def test_publish_endpoint(request: TestPublishRequest):
    """Test publication sur une ou plusieurs boutiques"""
    try:
        log_app("🧪 Test de publication demandé", "INFO")
        
        # Déterminer les stores à tester
        stores_to_test = request.stores if request.stores else list(STORES.keys())
        
        # Message de test
        test_message = request.custom_message or os.getenv("TEST_MESSAGE", "Test automatique 🚀")
        test_url = "https://example.com/product-test"
        test_image = "https://via.placeholder.com/600x600/0096d6/ffffff?text=Test+Image"
        
        results = {
            "success": False,
            "test_mode": PUBLICATION_TEST_MODE,
            "stores_tested": stores_to_test,
            "platforms_tested": request.platforms,
            "results": {},
            "summary": {"total_stores": 0, "successful_stores": 0, "failed_stores": 0},
            "timestamp": datetime.now().isoformat()
        }
        
        for store in stores_to_test:
            if store not in STORES:
                results["results"][store] = {
                    "success": False,
                    "error": f"Store '{store}' inconnu"
                }
                continue
            
            try:
                # Tester la publication pour ce store
                store_result = await publish_post_main(
                    store,
                    test_message,
                    test_url,
                    test_image if "instagram" in request.platforms else None,
                    request.platforms
                )
                
                results["results"][store] = store_result
                results["summary"]["total_stores"] += 1
                
                if store_result["success"]:
                    results["summary"]["successful_stores"] += 1
                else:
                    results["summary"]["failed_stores"] += 1
                    
            except Exception as e:
                results["results"][store] = {
                    "success": False,
                    "error": f"Erreur test {store}: {str(e)}"
                }
                results["summary"]["total_stores"] += 1
                results["summary"]["failed_stores"] += 1
        
        # Déterminer le succès global
        results["success"] = results["summary"]["successful_stores"] > 0
        
        log_app(f"🧪 Test terminé: {results['summary']['successful_stores']}/{results['summary']['total_stores']} stores réussis", "SUCCESS" if results["success"] else "WARNING")
        
        return results
        
    except Exception as e:
        error_msg = f"Erreur test publication: {str(e)}"
        log_app(error_msg, "ERROR")
        return {
            "success": False,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/users/{user_id}/platforms")
async def get_user_platforms(user_id: str):
    """Get platforms for a specific user"""
    try:
        log_app(f"Récupération des plateformes pour l'utilisateur: {user_id}", "INFO")
        
        # Mock platform data - in a real app, this would come from database
        platforms = {
            "personal_pages": [
                {
                    "id": "personal_page_1",
                    "name": "Ma Page Personnelle",
                    "platform": "facebook",
                    "type": "page",
                    "access_token": "mock_token"
                }
            ],
            "personal_groups": [
                {
                    "id": "personal_group_1", 
                    "name": "Mon Groupe Personnel",
                    "platform": "facebook",
                    "type": "group",
                    "access_token": "mock_token"
                }
            ],
            "business_pages": [
                {
                    "id": "102401876209415",
                    "name": "Le Berger Blanc Suisse",
                    "platform": "facebook",
                    "type": "page",
                    "access_token": os.getenv("FB_ACCESS_TOKEN_GIZMO")
                },
                {
                    "id": "210654558802531",
                    "name": "LogicAntiq",
                    "platform": "facebook", 
                    "type": "page",
                    "access_token": os.getenv("FB_ACCESS_TOKEN_LOGICANTIQ")
                },
                {
                    "id": "236260991673388",
                    "name": "Logicamp Outdoor",
                    "platform": "facebook",
                    "type": "page", 
                    "access_token": os.getenv("FB_ACCESS_TOKEN_OUTDOOR")
                }
            ],
            "business_groups": [],
            "business_instagram": [
                {
                    "id": "ig_account_1",
                    "name": "@logicamp_berger",
                    "platform": "instagram",
                    "type": "instagram",
                    "username": "logicamp_berger"
                }
            ],
            "selected_business_manager": {
                "id": "business_manager_1",
                "name": "Entreprise de Didier Preud'homme"
            }
        }
        
        return platforms
        
    except Exception as e:
        log_app(f"❌ Erreur récupération plateformes: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

async def process_webhook_publication(webhook_data: dict) -> dict:
    """Traite les données de publication reçues depuis n8n via webhook - VERSION AVEC PRIORITÉS CHRONOLOGIQUES"""
    try:
        log_app("🔄 Traitement des données de publication webhook avec PRIORITÉS RÉCENTES...", "INFO")
        
        # Vérifier si les données contiennent des informations de publication
        if not isinstance(webhook_data, dict):
            log_app("⚠️ Données webhook invalides (pas un dictionnaire)", "WARNING")
            return None
        
        # PRIORITÉ RÉCENTE 1: Support des modifications @logicamp_berger (MISSION_ACCOMPLIE_LOGICAMP_BERGER.md)
        # Structure attendue depuis n8n (flexible) avec support spécial gizmobbs → @logicamp_berger
        
        # Extraction flexible des données
        store = webhook_data.get("store")
        shop_type = webhook_data.get("shop_type")  # Support ancien format
        title = webhook_data.get("title", "")
        description = webhook_data.get("description", "")
        custom_message = webhook_data.get("message", "")
        product_url = webhook_data.get("product_url") or webhook_data.get("url")
        image_url = webhook_data.get("image_url")
        platforms = webhook_data.get("platforms", ["facebook"])
        
        # PRIORITÉ RÉCENTE 2: Logique spéciale pour gizmobbs → @logicamp_berger (SOLUTION_LOGICAMP_BERGER_COMPLETE.md)
        if store == "gizmobbs" or shop_type == "gizmobbs":
            log_app("🎯 PRIORITÉ RÉCENTE : Configuration spéciale gizmobbs → @logicamp_berger", "INFO")
            
            # Business Manager spécifique pour @logicamp_berger
            business_manager_id = "1715327795564432"  # ID spécifique du BM logicamp_berger
            
            # CONFIGURATION PRIORITAIRE INSTAGRAM selon MISSION_ACCOMPLIE_LOGICAMP_BERGER.md
            platforms = ["instagram"]  # Instagram UNIQUEMENT pour gizmobbs (pas Facebook)
            
            # Adaptation du message pour Instagram avec optimisation automatique
            if custom_message:
                instagram_message = custom_message
            elif title and description:
                # Format Instagram optimisé avec hashtags
                instagram_message = f"{title} 📱\n\n{description}\n\n🔗 Plus d'infos : lien en bio\n\n#tech #gizmobbs #innovation #mobile"
            elif title:
                instagram_message = f"{title}\n\n🔗 Plus d'infos : lien en bio\n\n#tech #gizmobbs #innovation"
            else:
                instagram_message = f"{description}\n\n#gizmobbs #tech #innovation"
            
            message = instagram_message
            log_app(f"📱 Message Instagram optimisé pour @logicamp_berger : {message[:50]}...", "INFO")
            log_app(f"🔧 Business Manager cible : {business_manager_id}", "INFO")
            log_app(f"🎯 Plateforme prioritaire : Instagram UNIQUEMENT", "INFO")
            
        else:
            # ANCIENNE LOGIQUE: Construction intelligente du message pour autres stores
            if custom_message:
                message = custom_message
            elif title and description:
                message = f"{title}\n\n{description}"
            elif title:
                message = title
            else:
                message = description or "Publication automatique"
        
        # Validation améliorée avec logging détaillé
        missing_fields = []
        if not store and not shop_type:
            missing_fields.append("store/shop_type")
        if not message.strip():
            missing_fields.append("message/title/description")
        if not product_url:
            missing_fields.append("product_url/url")
            
        if missing_fields:
            log_app(f"⚠️ Données de publication incomplètes: {', '.join(missing_fields)}", "WARNING")
            log_app(f"   Données reçues: store={store}, shop_type={shop_type}, message={bool(message)}, product_url={bool(product_url)}", "INFO")
            return None
        
        # Normaliser le store (support shop_type legacy)
        final_store = store or shop_type
        
        # Vérifier que le store existe
        if final_store not in STORES:
            log_app(f"❌ Store inconnu dans webhook: {final_store} (disponibles: {list(STORES.keys())})", "ERROR")
            return None
        
        # PRIORITÉ RÉCENTE 3: Déduplication automatique avec signature
        from datetime import datetime, timedelta
        import hashlib
        
        # Créer une signature unique pour détecter les doublons
        content_signature = hashlib.md5(f"{final_store}_{title}_{image_url}".encode()).hexdigest()
        duplicate_window = datetime.now() - timedelta(minutes=15)
        
        log_app(f"🔍 Vérification déduplication - Signature: {content_signature[:8]}", "INFO")
        
        log_app(f"📝 Publication webhook PRIORITÉS RÉCENTES - Store: {final_store}, Plateformes: {platforms}", "INFO")
        log_app(f"   Titre: {title[:50]}{'...' if len(title) > 50 else ''}", "INFO")
        log_app(f"   URL produit: {product_url}", "INFO")
        log_app(f"   Image: {'Oui' if image_url else 'Non'}", "INFO")
        
        # EFFECTUER LA PUBLICATION avec toutes les améliorations intégrées
        # La fonction publish_post_main inclut automatiquement :
        # - Images cliquables (CLICKABLE_IMAGES_FEATURE.md)
        # - Validation préventive médias (AMÉLIORATIONS_MÉDIA_RÉALISÉES.md)
        # - Commentaires automatiques (AMELIORATIONS_REALISEES.md)
        # - Publication intelligente multi-plateformes (SMART_CROSSPOST_FEATURES.md)
        result = await publish_post_main(
            store=final_store,
            message=message,
            product_url=product_url,
            image_url=image_url,
            platforms=platforms
        )
        
        # RÉPONSE STRUCTURÉE compatible avec toutes les améliorations
        if result.get("success"):
            log_app(f"✅ Publication webhook PRIORITÉS RÉCENTES réussie pour {final_store}", "SUCCESS")
            
            # Extraire les IDs de posts pour la réponse (format attendu par n8n)
            facebook_post_id = None
            instagram_post_id = None
            
            if result.get("facebook_result") and result["facebook_result"].get("id"):
                facebook_post_id = result["facebook_result"]["id"]
                
            if result.get("instagram_result") and result["instagram_result"].get("id"):
                instagram_post_id = result["instagram_result"]["id"]
            
            # PRIORITÉ RÉCENTE 4: Réponse spéciale pour gizmobbs → @logicamp_berger
            if final_store == "gizmobbs":
                log_app(f"🎯 Publication @logicamp_berger - Instagram ID: {instagram_post_id}", "SUCCESS")
                log_app(f"📱 Compte cible: @logicamp_berger (Business Manager: 1715327795564432)", "SUCCESS")
            
            return {
                "success": True,
                "status": "published",
                "store": final_store,
                "platforms": platforms,
                "data": {
                    "facebook_post_id": facebook_post_id,
                    "instagram_post_id": instagram_post_id,
                    "platforms_successful": len([p for p in platforms if (p == "facebook" and facebook_post_id) or (p == "instagram" and instagram_post_id)]),
                    "content_signature": content_signature,
                    "duplicate_skipped": False,
                    "special_config": "logicamp_berger" if final_store == "gizmobbs" else None
                },
                "result": result
            }
        else:
            log_app(f"❌ Échec publication webhook pour {final_store}: {result.get('errors', [])}", "ERROR")
            return {
                "success": False,
                "status": "failed",
                "store": final_store,
                "error": result.get("errors", ["Erreur inconnue"]),
                "platforms": platforms
            }
        
    except Exception as e:
        log_app(f"❌ Erreur traitement publication webhook PRIORITÉS RÉCENTES: {str(e)}", "ERROR")
        return {
            "success": False,
            "status": "error",
            "error": str(e)
        }

@app.get("/api/webhooks/history")
async def get_webhook_history():
    """Get recent webhook history"""
    try:
        webhooks = await get_recent_webhooks(50)
        return {
            "success": True,
            "webhooks": webhooks,
            "count": len(webhooks)
        }
    except Exception as e:
        log_app(f"❌ Erreur récupération webhooks: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/webhook")
@app.get("/api/webhook")
async def webhook_handler(request: Request):
    """Handle webhook requests from Facebook/Instagram"""
    try:
        method = request.method
        
        if method == "GET":
            # Webhook verification
            query_params = dict(request.query_params)
            
            hub_mode = query_params.get("hub.mode")
            hub_challenge = query_params.get("hub.challenge")
            hub_verify_token = query_params.get("hub.verify_token")
            
            verify_token = os.getenv("FACEBOOK_VERIFY_TOKEN", "mon_token_secret_webhook")
            
            if hub_mode == "subscribe" and hub_verify_token == verify_token:
                log_app(f"✅ Webhook vérifié avec succès", "SUCCESS")
                return PlainTextResponse(hub_challenge)
            else:
                log_app(f"❌ Échec vérification webhook", "ERROR")
                raise HTTPException(status_code=403, detail="Forbidden")
                
        elif method == "POST":
            # Webhook event handling with improved multipart/form-data support
            try:
                # Get content type to determine parsing strategy
                content_type = request.headers.get("content-type", "")
                log_app(f"📦 Content-Type: {content_type}", "INFO")
                
                # Try to get the raw body first  
                body = await request.body()
                log_app(f"📦 Webhook body size: {len(body)} bytes", "INFO")
                
                webhook_data = None
                
                # Handle multipart/form-data
                if "multipart/form-data" in content_type:
                    log_app("📦 Processing multipart/form-data webhook", "INFO")
                    try:
                        # Use FastAPI's form parsing
                        form_data = await request.form()
                        log_app(f"📦 Form fields: {list(form_data.keys())}", "INFO")
                        
                        # Look for JSON data in form fields
                        json_data_field = None
                        for field_name in ["json_data", "data", "payload", "hub.signature"]:
                            if field_name in form_data:
                                json_data_field = field_name
                                break
                        
                        if json_data_field:
                            json_str = form_data[json_data_field]
                            if hasattr(json_str, 'read'):  # It's a file-like object
                                json_str = await json_str.read()
                                json_str = json_str.decode('utf-8')
                            webhook_data = json.loads(json_str)
                            log_app(f"📦 Parsed JSON from {json_data_field}: {json.dumps(webhook_data, indent=2)[:500]}...", "INFO")
                        else:
                            # Process all form fields
                            webhook_data = {}
                            for key, value in form_data.items():
                                if hasattr(value, 'read'):  # File upload
                                    content = await value.read()
                                    # Try to decode as text first
                                    try:
                                        text_content = content.decode('utf-8')
                                        # Try to parse as JSON
                                        try:
                                            webhook_data[key] = json.loads(text_content)
                                        except json.JSONDecodeError:
                                            webhook_data[key] = text_content
                                    except UnicodeDecodeError:
                                        # Binary content, store as base64
                                        import base64
                                        webhook_data[key] = {
                                            "type": "binary",
                                            "size": len(content),
                                            "base64": base64.b64encode(content[:1000]).decode('ascii')  # First 1KB only
                                        }
                                else:
                                    webhook_data[key] = value
                            log_app(f"📦 Processed form data: {list(webhook_data.keys())}", "INFO")
                        
                    except Exception as e:
                        log_app(f"⚠️ Error parsing multipart data: {str(e)}", "WARNING")
                        return {"status": "received", "note": "Multipart parsing error but acknowledged"}
                
                # Handle application/json or text content
                else:
                    log_app("📦 Processing JSON/text webhook", "INFO")
                    # Try to decode as UTF-8 first
                    try:
                        body_str = body.decode('utf-8')
                        webhook_data = json.loads(body_str)
                        log_app(f"📦 Webhook JSON reçu: {json.dumps(webhook_data, indent=2)[:500]}...", "INFO")
                    except UnicodeDecodeError as e:
                        # Handle non-UTF-8 data
                        log_app(f"⚠️ Webhook data is not UTF-8, trying latin-1: {str(e)}", "WARNING")
                        try:
                            body_str = body.decode('latin-1')
                            webhook_data = json.loads(body_str)
                            log_app(f"📦 Webhook JSON (latin-1) reçu: {json.dumps(webhook_data, indent=2)[:500]}...", "INFO")
                        except (UnicodeDecodeError, json.JSONDecodeError) as e2:
                            log_app(f"⚠️ Unable to decode webhook data: {str(e2)}", "WARNING")
                            log_app(f"📦 Raw webhook data (first 100 bytes): {body[:100]}", "INFO")
                            return {"status": "received", "note": "Binary data acknowledged"}
                    except json.JSONDecodeError as e:
                        log_app(f"⚠️ Invalid JSON in webhook: {str(e)}", "WARNING")
                        log_app(f"📦 Raw webhook data: {body_str[:500]}...", "INFO")
                        return {"status": "received", "note": "Invalid JSON acknowledged"}
                
                # Process webhook data if successfully parsed
                if webhook_data:
                    if isinstance(webhook_data, dict):
                        # Log key webhook information
                        if 'object' in webhook_data:
                            log_app(f"📦 Webhook object type: {webhook_data['object']}", "INFO")
                        if 'entry' in webhook_data:
                            log_app(f"📦 Webhook entries: {len(webhook_data['entry'])}", "INFO")
                        
                        # NOUVELLE LOGIQUE: Traitement des données de publication depuis n8n
                        publication_result = await process_webhook_publication(webhook_data)
                        if publication_result:
                            log_app(f"🚀 Publication webhook réussie: {publication_result}", "SUCCESS")
                        
                        # Sauvegarder le webhook dans MongoDB
                        try:
                            webhook_record = {
                                "type": "publication",
                                "data": webhook_data,
                                "result": publication_result,
                                "status": "processed" if publication_result else "failed"
                            }
                            await save_webhook_data(webhook_record)
                            log_app("✅ Webhook sauvegardé dans MongoDB", "SUCCESS")
                        except Exception as save_error:
                            log_app(f"⚠️ Erreur sauvegarde webhook: {save_error}", "WARNING")
                        
                    log_app("✅ Webhook data processed successfully", "SUCCESS")
                else:
                    log_app("⚠️ No webhook data could be extracted", "WARNING")
                
                return {"status": "received", "processed": webhook_data is not None}
                
            except Exception as parse_error:
                log_app(f"⚠️ Error parsing webhook data: {str(parse_error)}", "WARNING")
                # Still return success to Facebook to avoid retries
                return {"status": "received", "note": "Parsing error but acknowledged"}
            
    except Exception as e:
        log_app(f"❌ Erreur webhook: {str(e)}", "ERROR")
        # Return success even on errors to avoid Facebook retries
        return {"status": "received", "error": str(e)}

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

# === ENDPOINTS VIDÉO ===
@app.post("/api/videos/upload", response_model=VideoUploadResponse)
async def upload_video_endpoint(video: UploadFile = File(...)):
    """Upload une vidéo et retourne l'URL publique"""
    try:
        log_video(f"Upload vidéo reçu: {video.filename} ({video.content_type})", "INFO")
        
        # Vérifier le type MIME
        if video.content_type not in SUPPORTED_VIDEO_FORMATS:
            return VideoUploadResponse(
                success=False,
                error=f"Format non supporté: {video.content_type}. Formats supportés: {SUPPORTED_VIDEO_FORMATS}"
            )
        
        # Créer un nom de fichier unique
        file_extension = ".mp4" if video.content_type == "video/mp4" else ".mov"
        unique_filename = f"video_{uuid.uuid4().hex[:8]}_{int(time.time())}{file_extension}"
        temp_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Sauvegarder le fichier temporairement
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        
        # Valider le fichier
        validation = validate_video_file(temp_path)
        if not validation["valid"]:
            os.remove(temp_path)  # Nettoyer le fichier temporaire
            return VideoUploadResponse(
                success=False,
                error=validation["error"],
                validation=validation
            )
        
        # Upload vers FTP
        success, public_url, error = await upload_video_to_ftp(temp_path, unique_filename)
        
        # Nettoyer le fichier temporaire
        try:
            os.remove(temp_path)
        except:
            pass
        
        if success:
            return VideoUploadResponse(
                success=True,
                video_url=public_url,
                filename=unique_filename,
                file_size=validation["file_size"],
                validation=validation
            )
        else:
            return VideoUploadResponse(
                success=False,
                error=error,
                validation=validation
            )
            
    except Exception as e:
        log_video(f"Erreur upload vidéo: {str(e)}", "ERROR")
        return VideoUploadResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/videos/publish")
async def publish_video_endpoint(request: VideoPublishRequest):
    """Publie une vidéo sur les plateformes sélectionnées"""
    try:
        log_video(f"Demande publication vidéo: {request.store} sur {request.platforms}", "INFO")
        
        # Pour cette version, on assume que la vidéo est déjà uploadée
        # Dans une implémentation complète, on pourrait accepter l'URL de la vidéo
        # ou l'ID d'upload précédent
        
        # Pour le moment, utiliser une URL de test ou demander l'URL en paramètre
        # TODO: Améliorer pour prendre l'URL depuis une base de données d'uploads
        
        return {
            "success": False,
            "error": "Fonctionnalité en développement - utilisez l'endpoint d'upload puis l'endpoint de publication séparés"
        }
        
    except Exception as e:
        log_video(f"Erreur publication vidéo: {str(e)}", "ERROR")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/videos/publish-url")
async def publish_video_by_url_endpoint(
    store: str = Form(...),
    message: str = Form(...),
    product_url: str = Form(...),
    video_url: str = Form(...),
    platforms: str = Form(default="facebook,instagram")
):
    """Publie une vidéo déjà uploadée par son URL"""
    try:
        platforms_list = [p.strip() for p in platforms.split(",")]
        log_video(f"Publication vidéo par URL: {store} sur {platforms_list}", "INFO")
        
        result = await publish_video_main(store, message, product_url, video_url, platforms_list)
        return result
        
    except Exception as e:
        log_video(f"Erreur publication vidéo par URL: {str(e)}", "ERROR")
        return {
            "success": False,
            "error": str(e)
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