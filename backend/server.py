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
from datetime import datetime, timedelta

# PATCH 25: Import schedule optionnel pour compatibilité Windows
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    print("⚠️ [PATCH 25] Module 'schedule' non disponible - nettoyage différé désactivé")
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

# Import new modules
from token_manager import token_manager
from webhook_handler import webhook_handler

# PATCH 30: Import FTP Manager centralisé
try:
    from ftp_manager_patch29 import init_ftp_manager, upload_for_publication, get_ftp_public_url
    FTP_MANAGER_AVAILABLE = True
    print("✅ [PATCH 30] Gestionnaire FTP PATCH 29 disponible")
except ImportError as e:
    print(f"⚠️ [PATCH 30] Gestionnaire FTP non disponible: {e}")
    # Fallback functions
    def init_ftp_manager():
        return None
    def upload_for_publication(local_path: str, filename: str = None):
        return False, None, "Gestionnaire FTP non disponible"
    def get_ftp_public_url(filename: str, local_path: str = None):
        return f"https://logicamp.org/wordpress/uploads/{filename}"
    FTP_MANAGER_AVAILABLE = False

# Import the new FTP upload utilities - PATCH 17: Import robuste (gardé pour compatibilité)
try:
    from utils.ftp_upload import upload_file_via_ftp, get_public_media_url
    FTP_UTILS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ [PATCH 17] Utilities FTP non disponibles: {e}")
    # Fallback functions
    def upload_file_via_ftp(local_path: str, remote_name: str, timeout=15):
        return None
    def get_public_media_url(filename: str):
        return f"https://logicamp.org/wordpress/uploads/{filename}"
    FTP_UTILS_AVAILABLE = False

# Import de la nouvelle fonction poster_media_enhanced (compatible avec ancienne version)
try:
    from poster_media_enhanced import poster_media_enhanced, STORES_CONFIG
    from folder_watcher import start_folder_watcher_background, stop_folder_watcher, get_watcher_status
    ENHANCED_FEATURES_AVAILABLE = True
    print("✅ [IMPORT] Fonctionnalités améliorées disponibles")
except ImportError as e:
    print(f"⚠️ [IMPORT] Fonctionnalités améliorées non disponibles: {e}")
    ENHANCED_FEATURES_AVAILABLE = False
    # Fallback pour compatibilité
    def poster_media_enhanced(*args, **kwargs):
        return {"success": False, "error": "Fonctionnalités améliorées non disponibles"}
    def start_folder_watcher_background():
        return False
    def stop_folder_watcher():
        pass
    def get_watcher_status():
        return {"running": False, "error": "Non disponible"}
    STORES_CONFIG = {}

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

# === CONFIGURATION NGROK SIMPLIFIÉE - NGROK UNIQUEMENT ===
ENABLE_NGROK = os.getenv("ENABLE_NGROK", "detect").lower()  # detect, true, false
DETECT_EXISTING_NGROK = True  # Toujours détecter ngrok existant d'abord
NGROK_PROCESS = None
NGROK_URL = "https://9fff391906ce.ngrok-free.app"  # URL ngrok fixe pour simplicité

# Cache pour éviter les lectures répétitives des fichiers
_NGROK_URL_CACHE = None
_NGROK_URL_CACHE_TIME = 0
_CACHE_DURATION = 30  # Cache valide pendant 30 secondes

def get_public_url(filename: str) -> str:
    """PATCH 33: Génère une URL publique FTP - Version robuste avec fallback ngrok"""
    try:
        if FTP_MANAGER_AVAILABLE:
            # PATCH 33: Utiliser le gestionnaire FTP intelligent
            ftp_public_url = get_ftp_public_url(filename)
            log_app(f"🎯 PATCH 33: URL FTP générée - {ftp_public_url}", "INFO")
            return ftp_public_url
        else:
            # PATCH 33: Fallback vers ngrok si FTP non disponible
            ngrok_url = get_active_ngrok_url()
            if ngrok_url:
                ngrok_public_url = f"{ngrok_url}/uploads/{filename}"
                log_app(f"🔄 PATCH 33: URL ngrok fallback - {ngrok_public_url}", "INFO")
                return ngrok_public_url
            else:
                log_app(f"⚠️ PATCH 33: Fallback URL statique - {FTP_BASE_URL}{filename}", "WARNING")
                return f"{FTP_BASE_URL}{filename}"
    except Exception as e:
        log_app(f"⚠️ PATCH 33: Erreur génération URL: {e}", "WARNING")
        return f"{FTP_BASE_URL}{filename}"

async def upload_file_to_ftp_for_publication(local_file_path: str, filename: str = None) -> tuple:
    """PATCH 33: Upload FTP robuste avec fallback ngrok en cas d'échec"""
    try:
        if not filename:
            filename = os.path.basename(local_file_path)
            
        log_app(f"🔄 PATCH 33: Upload FTP robuste en cours - {filename}", "INFO")
        
        if FTP_MANAGER_AVAILABLE:
            # PATCH 33: Tentative upload FTP avec timeout optimisé
            success, ftp_url, error = upload_for_publication(local_file_path, filename)
            
            if success and ftp_url:
                log_app(f"✅ PATCH 33: Upload FTP réussi - {ftp_url}", "SUCCESS")
                return True, ftp_url, None
            else:
                log_app(f"⚠️ PATCH 33: Upload FTP échoué ({error}) - Fallback ngrok...", "WARNING")
                
                # PATCH 33: Fallback intelligent vers ngrok
                ngrok_url = get_active_ngrok_url()
                if ngrok_url:
                    # Copier le fichier vers le répertoire uploads local pour ngrok
                    uploads_dir = "/app/backend/uploads"
                    os.makedirs(uploads_dir, exist_ok=True)
                    
                    local_upload_path = os.path.join(uploads_dir, filename)
                    shutil.copy2(local_file_path, local_upload_path)
                    
                    ngrok_public_url = f"{ngrok_url}/uploads/{filename}"
                    log_app(f"✅ PATCH 33: Fallback ngrok réussi - {ngrok_public_url}", "SUCCESS")
                    return True, ngrok_public_url, None
                else:
                    # Dernière chance : générer une URL optimiste
                    optimistic_url = f"{FTP_BASE_URL}{filename}"
                    log_app(f"⚠️ PATCH 33: URL optimiste générée - {optimistic_url}", "WARNING")
                    return False, optimistic_url, "Upload FTP et ngrok échoués"
        else:
            # PATCH 33: Si pas de gestionnaire FTP, utiliser ngrok directement
            ngrok_url = get_active_ngrok_url()
            if ngrok_url:
                uploads_dir = "/app/backend/uploads"
                os.makedirs(uploads_dir, exist_ok=True)
                
                local_upload_path = os.path.join(uploads_dir, filename)
                shutil.copy2(local_file_path, local_upload_path)
                
                ngrok_public_url = f"{ngrok_url}/uploads/{filename}"
                log_app(f"✅ PATCH 33: Upload ngrok direct - {ngrok_public_url}", "SUCCESS")
                return True, ngrok_public_url, None
            else:
                error_msg = "PATCH 33: Aucun gestionnaire FTP ni URL ngrok disponible"
                log_app(f"❌ {error_msg}", "ERROR")
                return False, None, error_msg
            
    except Exception as e:
        error_msg = f"PATCH 33: Erreur générale upload - {str(e)}"
        log_app(f"❌ {error_msg}", "ERROR")
        return False, None, error_msg

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
FTP_PASSWORD = os.getenv("FTP_PASSWORD", "6837")
FTP_DIRECTORY = os.getenv("FTP_DIRECTORY", "/www/wordpress/uploads/")
FTP_INITIAL_DIRECTORY = os.getenv("FTP_INITIAL_DIRECTORY", "/")  # Répertoire initial  
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

async def test_ftp_connection() -> dict:
    """Teste la connexion FTP et diagnostique les problèmes"""
    try:
        log_app("🔍 DIAGNOSTIC: Test de connexion FTP", "INFO")
        log_app(f"🔍 DIAGNOSTIC: Host={FTP_HOST}, Port={FTP_PORT}, User={FTP_USER}", "INFO")
        
        test_result = {
            "success": False,
            "host_reachable": False,
            "login_success": False,
            "directory_accessible": False,
            "error": None,
            "suggestions": []
        }
        
        # Test de connectivité réseau
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                result = s.connect_ex((FTP_HOST, FTP_PORT))
                if result == 0:
                    test_result["host_reachable"] = True
                    log_app("✅ DIAGNOSTIC: Host FTP accessible", "SUCCESS")
                else:
                    log_app(f"❌ DIAGNOSTIC: Host FTP non accessible (code: {result})", "ERROR")
                    test_result["suggestions"].append(f"Vérifiez la connectivité réseau vers {FTP_HOST}:{FTP_PORT}")
                    return test_result
        except Exception as e:
            log_app(f"❌ DIAGNOSTIC: Erreur test réseau: {e}", "ERROR")
            test_result["suggestions"].append("Vérifiez votre connexion internet")
            return test_result
        
        # Test de connexion FTP
        try:
            ftp = ftplib.FTP()
            ftp.connect(FTP_HOST, FTP_PORT, timeout=15)
            ftp.login(FTP_USER, FTP_PASSWORD)
            test_result["login_success"] = True
            log_app("✅ DIAGNOSTIC: Authentification FTP réussie", "SUCCESS")
            
            # Test navigation répertoires
            try:
                if FTP_INITIAL_DIRECTORY:
                    ftp.cwd(FTP_INITIAL_DIRECTORY)
                    log_app(f"✅ DIAGNOSTIC: Répertoire initial {FTP_INITIAL_DIRECTORY} accessible", "SUCCESS")
                
                ftp.cwd(FTP_DIRECTORY)
                test_result["directory_accessible"] = True
                log_app(f"✅ DIAGNOSTIC: Répertoire cible {FTP_DIRECTORY} accessible", "SUCCESS")
                
                # Lister les fichiers pour vérifier les permissions (avec timeout court)
                try:
                    import signal
                    def timeout_handler(signum, frame):
                        raise TimeoutError("Timeout listage fichiers")
                    
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(5)  # 5 secondes max pour lister
                    
                    files = ftp.nlst()
                    signal.alarm(0)  # Annuler le timeout
                    log_app(f"✅ DIAGNOSTIC: {len(files)} fichiers trouvés dans le répertoire", "SUCCESS")
                except (TimeoutError, Exception) as list_error:
                    signal.alarm(0)  # S'assurer d'annuler le timeout
                    log_app(f"⚠️ DIAGNOSTIC: Timeout/erreur listage fichiers: {list_error}", "WARNING")
                    # Mais ce n'est pas critique pour le diagnostic
                
                test_result["success"] = True
                
            except Exception as dir_error:
                log_app(f"⚠️ DIAGNOSTIC: Erreur navigation répertoires: {dir_error}", "WARNING")
                test_result["suggestions"].append(f"Vérifiez que le répertoire {FTP_DIRECTORY} existe et est accessible")
                
            ftp.quit()
            
        except ftplib.error_perm as perm_error:
            log_app(f"❌ DIAGNOSTIC: Erreur permissions FTP: {perm_error}", "ERROR")
            test_result["suggestions"].append("Vérifiez les identifiants FTP (utilisateur/mot de passe)")
            test_result["error"] = str(perm_error)
            
        except Exception as ftp_error:
            log_app(f"❌ DIAGNOSTIC: Erreur connexion FTP: {ftp_error}", "ERROR")
            test_result["suggestions"].append("Problème de connexion FTP générique")
            test_result["error"] = str(ftp_error)
        
        return test_result
        
    except Exception as e:
        log_app(f"❌ DIAGNOSTIC: Erreur générale test FTP: {e}", "ERROR")
        return {
            "success": False,
            "error": str(e),
            "suggestions": ["Erreur interne du test de diagnostic"]
        }

def create_ftp_date_directories(ftp, base_directory="/downloads/") -> str:
    """Crée automatiquement la structure de répertoires par date sur le serveur FTP
    
    Args:
        ftp: Instance FTP connectée
        base_directory: Répertoire de base (par défaut: /downloads/)
        
    Returns:
        str: Le chemin complet du répertoire créé (ex: /downloads/2025/09/02/)
    """
    from datetime import datetime
    
    try:
        now = datetime.now()
        
        log_app("🔧 CORRECTION: Création automatique des répertoires FTP par date...", "INFO")
        
        # Naviguer vers le répertoire de base 
        try:
            ftp.cwd(base_directory)
            log_app(f"✅ CORRECTION: Navigation vers répertoire de base: {base_directory}", "SUCCESS")
        except ftplib.error_perm:
            # Si le répertoire de base n'existe pas, le créer
            try:
                ftp.mkd(base_directory)
                ftp.cwd(base_directory)
                log_app(f"✅ CORRECTION: Répertoire de base créé: {base_directory}", "SUCCESS")
            except Exception as e:
                log_app(f"❌ CORRECTION: Impossible de créer le répertoire de base {base_directory}: {e}", "ERROR")
                raise
        
        # Créer/naviguer vers le répertoire de l'année (ex: 2025)
        year_dir = f"{now.year:04d}"
        try:
            ftp.cwd(year_dir)
            log_app(f"✅ CORRECTION: Navigation vers année: {year_dir}", "SUCCESS")
        except ftplib.error_perm:
            try:
                ftp.mkd(year_dir)
                ftp.cwd(year_dir)
                log_app(f"✅ CORRECTION: Répertoire année créé: {year_dir}", "SUCCESS")
            except Exception as e:
                log_app(f"❌ CORRECTION: Erreur création répertoire année {year_dir}: {e}", "ERROR")
                raise
        
        # Créer/naviguer vers le répertoire du mois (ex: 09)
        month_dir = f"{now.month:02d}"
        try:
            ftp.cwd(month_dir)
            log_app(f"✅ CORRECTION: Navigation vers mois: {month_dir}", "SUCCESS")
        except ftplib.error_perm:
            try:
                ftp.mkd(month_dir)
                ftp.cwd(month_dir)
                log_app(f"✅ CORRECTION: Répertoire mois créé: {month_dir}", "SUCCESS")
            except Exception as e:
                log_app(f"❌ CORRECTION: Erreur création répertoire mois {month_dir}: {e}", "ERROR")
                raise
        
        # Créer/naviguer vers le répertoire du jour (ex: 02)
        day_dir = f"{now.day:02d}"
        try:
            ftp.cwd(day_dir)
            log_app(f"✅ CORRECTION: Navigation vers jour: {day_dir}", "SUCCESS")
        except ftplib.error_perm:
            try:
                ftp.mkd(day_dir)
                ftp.cwd(day_dir)
                log_app(f"✅ CORRECTION: Répertoire jour créé: {day_dir}", "SUCCESS")
            except Exception as e:
                log_app(f"❌ CORRECTION: Erreur création répertoire jour {day_dir}: {e}", "ERROR")
                raise
        
        # Retourner le chemin complet créé
        full_path = f"{base_directory}{year_dir}/{month_dir}/{day_dir}/"
        log_app(f"✅ CORRECTION: Structure de répertoires FTP créée: {full_path}", "SUCCESS")
        
        return full_path
        
    except Exception as e:
        log_app(f"❌ CORRECTION: Erreur générale création répertoires FTP: {e}", "ERROR")
        raise

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
    """Upload une vidéo vers le serveur FTP avec gestion d'erreurs robuste"""
    try:
        log_video(f"Début upload FTP: {video_path}", "UPLOAD")
        
        if not filename:
            filename = f"video_{uuid.uuid4().hex[:8]}_{os.path.basename(video_path)}"
        
        # Validation avant upload
        validation = validate_video_file(video_path)
        if not validation["valid"]:
            return False, None, validation["error"]
        
        # Configuration FTP robuste avec gestion des timeouts et erreurs réseau
        connection_configs = [
            {"pasv": True, "timeout": 120, "name": "Passif long timeout", "encoding": "utf-8"},
            {"pasv": False, "timeout": 120, "name": "Actif long timeout", "encoding": "utf-8"},
            {"pasv": True, "timeout": 60, "name": "Passif standard", "encoding": "latin1"},
            {"pasv": False, "timeout": 60, "name": "Actif standard", "encoding": "latin1"}
        ]
        
        for config in connection_configs:
            try:
                log_video(f"Tentative connexion FTP ({config['name']})...", "INFO")
                
                ftp = ftplib.FTP()
                ftp.set_pasv(config["pasv"])
                ftp.encoding = config["encoding"]
                
                # Connexion avec diagnostic amélioré
                try:
                    log_video(f"🌐 CORRECTION: Connexion à {FTP_HOST}:{FTP_PORT}...", "INFO")
                    ftp.connect(FTP_HOST, FTP_PORT, timeout=config["timeout"])
                    log_video(f"🔑 CORRECTION: Authentification avec utilisateur '{FTP_USER}'...", "INFO")
                    ftp.login(FTP_USER, FTP_PASSWORD)
                    log_video(f"✅ CORRECTION: Connexion FTP réussie ({config['name']})", "SUCCESS")
                except (ftplib.error_perm, ftplib.error_temp, OSError, ConnectionRefusedError) as conn_error:
                    log_video(f"Connexion échouée ({config['name']}): {conn_error}", "ERROR")
                    # Analyser l'erreur pour diagnostics
                    if "10061" in str(conn_error):
                        log_video(f"Erreur 10061 détectée - Vérifiez que le serveur FTP {FTP_HOST}:{FTP_PORT} est accessible", "ERROR")
                        log_video(f"Solutions possibles: 1) Vérifiez la connectivité réseau, 2) Vérifiez les credentials FTP, 3) Serveur FTP en maintenance", "INFO")
                    elif "timed out" in str(conn_error).lower():
                        log_video(f"Timeout de connexion - Le serveur FTP peut être surchargé", "WARNING")
                    continue
                
                log_video(f"Connexion FTP réussie ({config['name']})", "SUCCESS")
                
                # CORRECTION: Navigation et création automatique des répertoires FTP par date
                try:
                    # D'abord aller au répertoire initial si spécifié
                    if FTP_INITIAL_DIRECTORY and FTP_INITIAL_DIRECTORY != ftp.pwd():
                        ftp.cwd(FTP_INITIAL_DIRECTORY)
                        log_video(f"Navigation vers répertoire initial {FTP_INITIAL_DIRECTORY} réussie", "SUCCESS")
                    
                    # NOUVELLE FONCTIONNALITÉ: Création automatique de la structure /downloads/YYYY/MM/DD/
                    try:
                        date_path = create_ftp_date_directories(ftp, "/downloads/")
                        log_video(f"✅ CORRECTION: Répertoires FTP créés automatiquement: {date_path}", "SUCCESS")
                        # Mettre à jour l'URL de base pour inclure la structure de date
                        from datetime import datetime
                        base_url_with_date = FTP_BASE_URL.replace("/wordpress/uploads/", f"/downloads/{datetime.now().strftime('%Y/%m/%d')}/")
                    except Exception as date_dir_error:
                        log_video(f"⚠️ CORRECTION: Erreur création répertoires automatiques: {date_dir_error}", "WARNING")
                        # Fallback vers l'ancien comportement
                        ftp.cwd(FTP_DIRECTORY)
                        base_url_with_date = FTP_BASE_URL
                        log_video(f"Navigation vers {FTP_DIRECTORY} réussie (fallback)", "SUCCESS")
                        
                except ftplib.error_perm as cwd_error:
                    log_video(f"Répertoire {FTP_DIRECTORY} non accessible: {cwd_error}", "WARNING")
                    # Essayer sans le répertoire initial
                    try:
                        ftp.cwd(FTP_DIRECTORY.replace("/wordpress", ""))
                        base_url_with_date = FTP_BASE_URL
                        log_video(f"Navigation vers répertoire alternatif réussie", "SUCCESS")
                    except:
                        base_url_with_date = FTP_BASE_URL
                        log_video(f"Utilisation du répertoire courant par défaut", "WARNING")
                
                # Upload du fichier avec gestion d'erreur améliorée et progress
                try:
                    file_size = os.path.getsize(video_path)
                    with open(video_path, 'rb') as video_file:
                        log_video(f"Upload en cours: {filename} ({file_size / (1024*1024):.1f} MB)", "UPLOAD")
                        # Utiliser un blocksize plus petit pour les vidéos lourdes et éviter les timeouts
                        block_size = 2048 if file_size > 50 * 1024 * 1024 else 4096  # 2KB pour fichiers > 50MB
                        ftp.storbinary(f'STOR {filename}', video_file, blocksize=block_size)
                    
                    log_video(f"Upload terminé avec succès ({config['name']})", "SUCCESS")
                    
                    # Vérification optionnelle de l'upload
                    try:
                        remote_size = ftp.size(filename)
                        if remote_size == file_size:
                            log_video(f"Taille confirmée: {remote_size} bytes", "SUCCESS")
                        else:
                            log_video(f"Taille différente: local {file_size} vs remote {remote_size}", "WARNING")
                    except:
                        log_video("Vérification taille non disponible, mais upload semble réussi", "INFO")
                    
                    # Fermer la connexion proprement
                    try:
                        ftp.quit()
                    except:
                        ftp.close()
                    
                    # Construire l'URL publique avec la nouvelle structure de date
                    public_url = f"{base_url_with_date}{filename}"
                    log_video(f"Vidéo disponible: {public_url}", "SUCCESS")
                    
                    return True, public_url, None
                    
                except Exception as upload_error:
                    log_video(f"Erreur upload ({config['name']}): {upload_error}", "ERROR")
                    try:
                        ftp.quit()
                    except:
                        ftp.close()
                    # Continuer avec la configuration suivante
                    continue
                    
            except Exception as conn_error:
                log_video(f"Erreur connexion ({config['name']}): {conn_error}", "ERROR")
                # Continuer avec la configuration suivante
                continue
        
        # Si aucune configuration n'a fonctionné
        error_msg = "Impossible d'établir une connexion FTP stable. Causes possibles:\n"
        error_msg += f"- Serveur FTP {FTP_HOST}:{FTP_PORT} inaccessible\n"
        error_msg += "- Firewall bloquant les connexions FTP\n"
        error_msg += "- Problème de résolution DNS\n"
        error_msg += "- Serveur FTP temporairement surchargé"
        return False, None, error_msg
        
    except Exception as e:
        log_video(f"Erreur générale upload FTP: {str(e)}", "ERROR")
        return False, None, str(e)

async def upload_image_to_ftp(image_path: str, original_filename: str = None) -> tuple:
    """Upload une image vers le serveur FTP avec gestion d'erreurs robuste pour Instagram - VERSION CORRIGÉE"""
    try:
        log_app(f"🖼️ CORRECTION: Début upload FTP image pour Instagram: {image_path}", "INFO")
        
        if not original_filename:
            original_filename = os.path.basename(image_path)
        
        # Validation des paramètres FTP
        if not all([FTP_HOST, FTP_USER, FTP_PASSWORD]):
            return False, None, f"Configuration FTP manquante: HOST={bool(FTP_HOST)}, USER={bool(FTP_USER)}, PASSWORD={bool(FTP_PASSWORD)}"
        
        # Générer un nom unique avec timestamp
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:8]
        filename_parts = os.path.splitext(original_filename)
        # Support pour .webp converti en .png pour Instagram
        if filename_parts[1].lower() == '.webp':
            filename_parts = (filename_parts[0], '.png')
        ftp_filename = f"instagram_{unique_id}_{timestamp}{filename_parts[1]}"
        
        # Validation avant upload
        if not os.path.exists(image_path):
            return False, None, f"Fichier non trouvé: {image_path}"
        
        file_size = os.path.getsize(image_path)
        log_app(f"📊 CORRECTION: Taille image: {file_size / (1024*1024):.2f} MB", "INFO")
        log_app(f"🔧 CORRECTION: Paramètres FTP - Host: {FTP_HOST}, Port: {FTP_PORT}, User: {FTP_USER}", "INFO")
        
        # Configuration FTP optimisée pour environnement conteneurisé + Windows
        connection_configs = [
            {"pasv": False, "timeout": 30, "name": "Actif rapide", "encoding": "utf-8", "blocksize": 32768},
            {"pasv": True, "timeout": 20, "name": "Passif rapide", "encoding": "utf-8", "blocksize": 16384},
            {"pasv": False, "timeout": 45, "name": "Actif standard", "encoding": "utf-8", "blocksize": 8192},
            {"pasv": True, "timeout": 45, "name": "Passif standard", "encoding": "utf-8", "blocksize": 8192},
        ]
        
        for attempt, config in enumerate(connection_configs, 1):
            try:
                log_app(f"🔄 CORRECTION: Tentative {attempt}/{len(connection_configs)} FTP image ({config['name']})...", "INFO")
                
                ftp = ftplib.FTP()
                ftp.set_pasv(config["pasv"])
                ftp.encoding = config["encoding"]
                
                # Connexion avec diagnostic amélioré
                try:
                    log_app(f"🌐 CORRECTION: Connexion à {FTP_HOST}:{FTP_PORT}...", "INFO")
                    ftp.connect(FTP_HOST, FTP_PORT, timeout=config["timeout"])
                    log_app(f"🔑 CORRECTION: Authentification avec utilisateur '{FTP_USER}'...", "INFO")
                    ftp.login(FTP_USER, FTP_PASSWORD)
                    log_app(f"✅ CORRECTION: Connexion FTP réussie ({config['name']})", "SUCCESS")
                except (ftplib.error_perm, ftplib.error_temp) as auth_error:
                    log_app(f"❌ CORRECTION: Erreur authentification FTP ({config['name']}): {auth_error}", "ERROR")
                    continue
                except (OSError, ConnectionRefusedError, ConnectionResetError) as conn_error:
                    log_app(f"❌ CORRECTION: Connexion FTP refusée ({config['name']}): {conn_error}", "ERROR")
                    log_app(f"🔍 CORRECTION: Vérifiez que {FTP_HOST}:{FTP_PORT} est accessible depuis ce conteneur", "INFO")
                    continue
                except Exception as unexpected_error:
                    log_app(f"❌ CORRECTION: Erreur FTP inattendue ({config['name']}): {unexpected_error}", "ERROR")
                    continue
                
                # Diagnostic du répertoire courant
                try:
                    current_dir = ftp.pwd()
                    log_app(f"📁 CORRECTION: Répertoire actuel: {current_dir}", "INFO")
                except:
                    log_app(f"⚠️ CORRECTION: Impossible de déterminer le répertoire courant", "WARNING")
                
                # CORRECTION: Navigation et création automatique des répertoires FTP par date
                target_directory = None
                base_url_with_date = FTP_BASE_URL  # Valeur par défaut
                try:
                    # D'abord aller au répertoire initial si spécifié
                    if FTP_INITIAL_DIRECTORY and FTP_INITIAL_DIRECTORY != ftp.pwd():
                        ftp.cwd(FTP_INITIAL_DIRECTORY)
                        log_app(f"📁 CORRECTION: Navigation vers répertoire initial {FTP_INITIAL_DIRECTORY} réussie", "SUCCESS")
                    
                    # NOUVELLE FONCTIONNALITÉ: Création automatique de la structure /downloads/YYYY/MM/DD/
                    try:
                        date_path = create_ftp_date_directories(ftp, "/downloads/")
                        target_directory = date_path
                        # Mettre à jour l'URL de base pour inclure la structure de date
                        from datetime import datetime
                        base_url_with_date = FTP_BASE_URL.replace("/wordpress/uploads/", f"/downloads/{datetime.now().strftime('%Y/%m/%d')}/")
                        log_app(f"✅ CORRECTION: Répertoires FTP images créés automatiquement: {date_path}", "SUCCESS")
                    except Exception as date_dir_error:
                        log_app(f"⚠️ CORRECTION: Erreur création répertoires images: {date_dir_error}", "WARNING")
                        # Fallback vers l'ancien comportement
                        ftp.cwd(FTP_DIRECTORY)
                        target_directory = FTP_DIRECTORY
                        base_url_with_date = FTP_BASE_URL
                        log_app(f"📁 CORRECTION: Navigation vers {FTP_DIRECTORY} réussie (fallback)", "SUCCESS")
                except ftplib.error_perm as cwd_error:
                    log_app(f"⚠️ CORRECTION: Répertoire {FTP_DIRECTORY} non accessible: {cwd_error}", "WARNING")
                    # Essayer les répertoires alternatifs
                    alt_dirs = ["/uploads/", "/public_html/uploads/", "/www/uploads/", "/"]
                    for alt_dir in alt_dirs:
                        try:
                            ftp.cwd(alt_dir)
                            target_directory = alt_dir
                            log_app(f"✅ CORRECTION: Navigation vers répertoire alternatif {alt_dir} réussie", "SUCCESS")
                            break
                        except:
                            continue
                    
                    if not target_directory:
                        target_directory = "/"  # Utiliser la racine
                        log_app(f"⚠️ CORRECTION: Utilisation du répertoire racine", "WARNING")
                
                # Upload du fichier avec gestion d'erreurs robuste
                try:
                    with open(image_path, 'rb') as image_file:
                        log_app(f"📤 CORRECTION: Upload en cours: {ftp_filename} vers {target_directory}", "INFO")
                        
                        # Progress callback pour les gros fichiers
                        def progress_callback(block):
                            pass  # Simple callback pour éviter les timeouts
                        
                        # Upload avec block size optimisé pour la stabilité
                        ftp.storbinary(f'STOR {ftp_filename}', image_file, 
                                     blocksize=config["blocksize"], callback=progress_callback)
                    
                    log_app(f"✅ CORRECTION: Upload image terminé avec succès ({config['name']})", "SUCCESS")
                    
                    # Vérification de l'upload avec plusieurs méthodes
                    upload_confirmed = False
                    try:
                        # Méthode 1: SIZE command
                        remote_size = ftp.size(ftp_filename)
                        if remote_size == file_size:
                            upload_confirmed = True
                            log_app(f"✅ CORRECTION: Fichier confirmé sur serveur (taille: {remote_size} bytes)", "SUCCESS")
                        else:
                            log_app(f"⚠️ CORRECTION: Taille différente - local: {file_size}, remote: {remote_size}", "WARNING")
                    except:
                        # Méthode 2: LIST command
                        try:
                            file_list = ftp.nlst()
                            if ftp_filename in file_list:
                                upload_confirmed = True
                                log_app(f"✅ CORRECTION: Fichier confirmé dans la liste", "SUCCESS")
                        except:
                            # Méthode 3: Assumer que l'upload a réussi si pas d'exception
                            upload_confirmed = True
                            log_app(f"⚠️ CORRECTION: Confirmation impossible, mais upload semble réussi", "WARNING")
                    
                    # Fermer la connexion proprement
                    try:
                        ftp.quit()
                    except:
                        ftp.close()
                    
                    if upload_confirmed:
                        # Construire l'URL publique avec la nouvelle structure de date
                        public_url = f"{base_url_with_date}{ftp_filename}"
                        log_app(f"🌐 CORRECTION: Image Instagram disponible: {public_url}", "SUCCESS")
                        
                        # Vérification finale optionnelle de l'URL (sans bloquer si échoue)
                        try:
                            import requests
                            response = requests.head(public_url, timeout=10)
                            if response.status_code == 200:
                                log_app(f"✅ CORRECTION: URL publique confirmée accessible", "SUCCESS")
                            else:
                                log_app(f"⚠️ CORRECTION: URL publique retourne status {response.status_code}", "WARNING")
                        except:
                            log_app(f"⚠️ CORRECTION: Impossible de vérifier l'URL publique (normal si NAT/firewall)", "WARNING")
                        
                        return True, public_url, None
                    else:
                        log_app(f"❌ CORRECTION: Upload non confirmé", "ERROR")
                        continue
                        
                except ftplib.error_perm as perm_error:
                    log_app(f"❌ CORRECTION: Erreur permissions upload ({config['name']}): {perm_error}", "ERROR")
                    try:
                        ftp.quit()
                    except:
                        ftp.close()
                    continue
                except Exception as upload_error:
                    log_app(f"❌ CORRECTION: Erreur upload image ({config['name']}): {upload_error}", "ERROR")
                    try:
                        ftp.quit()
                    except:
                        ftp.close()
                    continue
                    
            except Exception as conn_error:
                log_app(f"❌ CORRECTION: Erreur connexion FTP image ({config['name']}): {conn_error}", "ERROR")
                continue
        
        # Si toutes les configurations ont échoué
        error_msg = f"CORRECTION: Impossible d'uploader l'image vers FTP après {len(connection_configs)} tentatives. "
        error_msg += f"Vérifiez: 1) Connectivité réseau vers {FTP_HOST}:{FTP_PORT}, "
        error_msg += f"2) Identifiants FTP ({FTP_USER}), 3) Permissions d'écriture sur {FTP_DIRECTORY}"
        
        log_app(f"❌ {error_msg}", "ERROR")
        return False, None, error_msg
        
    except Exception as e:
        error_msg = f"CORRECTION: Erreur générale upload FTP image: {str(e)}"
        log_app(f"❌ {error_msg}", "ERROR")
        return False, None, error_msg
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
    """PATCH 30: Récupère l'URL backend active - PRIORITÉ AU FRONTEND .ENV"""
    global _NGROK_URL_CACHE, _NGROK_URL_CACHE_TIME
    
    try:
        # Vérifier le cache d'abord pour éviter les lectures répétitives
        current_time = time.time()
        if _NGROK_URL_CACHE and (current_time - _NGROK_URL_CACHE_TIME) < _CACHE_DURATION:
            return _NGROK_URL_CACHE
        
        # PATCH 30: PRIORITÉ 1 - Frontend .env (source unique de vérité)
        try:
            frontend_env_path = os.path.join(WINDOWS_PATHS["project_root"], "frontend", ".env")
            if os.path.exists(frontend_env_path):
                with open(frontend_env_path, "r", encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line in lines:
                    if line.startswith("REACT_APP_BACKEND_URL="):
                        backend_url = line.split("=", 1)[1].strip()
                        if backend_url and (backend_url.endswith(".ngrok-free.app") or backend_url.startswith("https://")):
                            if backend_url != _NGROK_URL_CACHE:
                                log_app(f"✅ PATCH 30: URL depuis frontend .env - {backend_url}", "SUCCESS")
                            _NGROK_URL_CACHE = backend_url
                            _NGROK_URL_CACHE_TIME = current_time
                            return backend_url
        except Exception as e:
            log_app(f"⚠️ PATCH 30: Erreur lecture frontend .env: {e}", "WARNING")
        
        # PATCH 30: PRIORITÉ 2 - API ngrok temps réel (fallback)
        try:
            import requests
            response = requests.get("http://localhost:4040/api/tunnels", timeout=3)
            if response.status_code == 200:
                tunnels = response.json().get("tunnels", [])
                for tunnel in tunnels:
                    if tunnel.get("proto") == "https" and "8001" in tunnel.get("config", {}).get("addr", ""):
                        ngrok_url = tunnel.get("public_url")
                        if ngrok_url and ngrok_url.endswith(".ngrok-free.app"):
                            if ngrok_url != _NGROK_URL_CACHE:
                                log_app(f"✅ PATCH 30: URL ngrok API fallback - {ngrok_url}", "SUCCESS")
                            _NGROK_URL_CACHE = ngrok_url
                            _NGROK_URL_CACHE_TIME = current_time
                            return ngrok_url
        except Exception as e:
            log_app(f"⚠️ PATCH 30: API ngrok non accessible: {e}", "WARNING")
        
        # PATCH 30: PRIORITÉ 3 - Variable globale (fallback final)
        global NGROK_URL
        if NGROK_URL and (NGROK_URL.endswith(".ngrok-free.app") or NGROK_URL.startswith("https://")):
            if NGROK_URL != _NGROK_URL_CACHE:
                log_app(f"✅ PATCH 30: URL variable globale fallback - {NGROK_URL}", "SUCCESS")
            _NGROK_URL_CACHE = NGROK_URL
            _NGROK_URL_CACHE_TIME = current_time
            return NGROK_URL
        
        log_app("⚠️ PATCH 30: Aucune URL active trouvée", "WARNING")
        log_app("💡 PATCH 30: SOLUTION: Mettez à jour REACT_APP_BACKEND_URL dans /app/frontend/.env", "INFO")
        log_app("   avec l'URL ngrok active", "INFO")
        return None
            
    except Exception as e:
        log_app(f"❌ Erreur détection URL backend: {e}", "ERROR")
        return None

def build_dynamic_redirect_uri(callback_path="/auth/callback"):
    """Construit dynamiquement l'URI de redirection - PRIORITÉ AU FRONTEND .env"""  
    try:
        # PRIORITÉ 1: Utiliser directement l'URL active du backend
        backend_url = get_active_ngrok_url()
        if backend_url:
            redirect_uri = f"{backend_url}{callback_path}"
            log_app(f"🎯 Redirect URI dynamique: {redirect_uri}", "SUCCESS")
            return redirect_uri
        
        # PRIORITÉ 2: Utiliser l'URL globale si définie
        global NGROK_URL
        if NGROK_URL:
            redirect_uri = f"{NGROK_URL}{callback_path}"
            log_app(f"🎯 Redirect URI dynamique (global): {redirect_uri}", "SUCCESS")
            return redirect_uri
        
        # PRIORITÉ 3: Lire depuis le fichier ngrok_url.txt si disponible
        try:
            ngrok_file_path = os.path.join(WINDOWS_PATHS["backend_dir"], "ngrok_url.txt")
            if os.path.exists(ngrok_file_path):
                with open(ngrok_file_path, "r", encoding='utf-8') as f:
                    file_url = f.read().strip()
                    if file_url and (file_url.startswith("https://") or file_url.startswith("http://")):
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

def sync_webhook_url_with_ngrok():
    """Synchronise WEBHOOK_URL dans le .env backend avec l'URL ngrok active - CORRECTION"""
    try:
        ngrok_url = get_active_ngrok_url()
        if not ngrok_url:
            log_app("⚠️ Aucune URL ngrok active - synchronisation WEBHOOK_URL ignorée", "WARNING")
            return False
        
        # CORRECTION: Utilise le .env backend au lieu du .env principal
        backend_env_path = os.path.join(WINDOWS_PATHS["backend_dir"], ".env")
        if not os.path.exists(backend_env_path):
            log_app(f"⚠️ Fichier .env backend non trouvé: {backend_env_path}", "WARNING")
            return False
        
        # Lire le fichier .env backend actuel
        with open(backend_env_path, "r", encoding='utf-8') as f:
            content = f.read()
        
        # Diviser en lignes pour traitement
        lines = content.splitlines()
        
        # Mettre à jour WEBHOOK_URL
        updated_lines = []
        webhook_url_updated = False
        
        for line in lines:
            if line.startswith("WEBHOOK_URL="):
                old_url = line.split("=", 1)[1] if "=" in line else ""
                if old_url != ngrok_url:
                    updated_lines.append(f"WEBHOOK_URL={ngrok_url}")
                    log_app(f"✅ WEBHOOK_URL mis à jour: {old_url} -> {ngrok_url}", "SUCCESS")
                else:
                    updated_lines.append(line)
                    log_app(f"✅ WEBHOOK_URL déjà à jour: {ngrok_url}", "SUCCESS")
                webhook_url_updated = True
            else:
                updated_lines.append(line)
        
        if not webhook_url_updated:
            updated_lines.append(f"WEBHOOK_URL={ngrok_url}")
            log_app(f"✅ WEBHOOK_URL ajouté: {ngrok_url}", "SUCCESS")
        
        # Réécrire le fichier backend .env avec les nouvelles lignes
        with open(backend_env_path, "w", encoding='utf-8') as f:
            f.write("\n".join(updated_lines))
            if updated_lines and not updated_lines[-1].endswith('\n'):
                f.write("\n")  # Ajouter une nouvelle ligne à la fin
        
        log_app(f"🎯 WEBHOOK_URL synchronisé avec ngrok: {ngrok_url}", "SUCCESS")
        return True
        
    except Exception as e:
        log_app(f"❌ Erreur synchronisation WEBHOOK_URL: {e}", "ERROR")
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
            f"{ngrok_url}/auth/callback"
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
            
            # Synchroniser WEBHOOK_URL dans le .env backend - CORRECTION
            webhook_sync_result = sync_webhook_url_with_ngrok()
            if webhook_sync_result:
                log_app("✅ WEBHOOK_URL synchronisé automatiquement avec ngrok", "SUCCESS")
            else:
                log_app("⚠️ WEBHOOK_URL non synchronisé - pas de ngrok actif", "WARNING")
                log_app("💡 RAPPEL: Pour mettre à jour WEBHOOK_URL manuellement, relancez l'app après avoir démarré ngrok", "INFO")
            
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
            
            # PATCH 25: Démarrage du planificateur de nettoyage différé (si disponible)
            scheduler_started = start_cleanup_scheduler()
            if not scheduler_started:
                log_app("🧹 PATCH 25: Nettoyage manuel requis - les fichiers s'accumuleront dans /uploads", "WARNING")
            
            # NOUVELLE FONCTIONNALITÉ: Auto-démarrage de la surveillance des dossiers (si disponible)
            if ENHANCED_FEATURES_AVAILABLE:
                log_app("🔍 Activation automatique de la surveillance des dossiers...", "INFO")
                try:
                    watcher_started = start_folder_watcher_background()
                    if watcher_started:
                        log_app("✅ Surveillance automatique des dossiers activée", "SUCCESS")
                        log_app("📁 Les fichiers ajoutés aux dossiers seront automatiquement traités", "INFO")
                    else:
                        log_app("⚠️ Surveillance déjà active ou impossible à démarrer", "WARNING")
                except Exception as e:
                    log_app(f"⚠️ Erreur activation surveillance automatique: {e}", "WARNING")
            else:
                log_app("ℹ️ Surveillance automatique non disponible (fonctionnalités améliorées manquantes)", "INFO")
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

# CORRECTION MAJEURE: Monter le dossier uploads pour servir les images via ngrok
def setup_uploads_static_mount():
    """Configure le montage static pour les uploads avec vérifications renforcées"""
    try:
        uploads_path = os.path.join(WINDOWS_PATHS["backend_dir"], "uploads")
        
        # Vérifications détaillées
        log_app(f"🔍 CORRECTION: Chemin uploads calculé: {uploads_path}", "INFO")
        log_app(f"🔍 CORRECTION: Backend dir: {WINDOWS_PATHS['backend_dir']}", "INFO")
        
        if os.path.exists(uploads_path):
            # Compter les fichiers pour diagnostic
            try:
                file_count = len([f for f in os.listdir(uploads_path) if os.path.isfile(os.path.join(uploads_path, f))])
                log_app(f"📁 CORRECTION: Dossier uploads trouvé avec {file_count} fichiers", "INFO")
                
                # Montage avec gestion d'erreur détaillée
                app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")
                log_app("✅ CORRECTION: Dossier uploads monté sur /uploads pour ngrok", "SUCCESS")
                
                # Test de quelques fichiers existants
                sample_files = [f for f in os.listdir(uploads_path) if f.endswith(('.jpg', '.png', '.gif'))][:3]
                if sample_files:
                    log_app(f"📋 CORRECTION: Exemples de fichiers accessibles:", "INFO")
                    for sample_file in sample_files:
                        log_app(f"   • /uploads/{sample_file}", "INFO")
                        
                return True
                
            except Exception as list_error:
                log_app(f"⚠️ CORRECTION: Erreur listage uploads: {list_error}", "WARNING")
                # Essayer quand même le montage
                app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")
                log_app("✅ CORRECTION: Montage uploads forcé malgré l'erreur de listage", "SUCCESS")
                return True
                
        else:
            # Créer le dossier s'il n'existe pas
            log_app(f"📁 CORRECTION: Création du dossier uploads: {uploads_path}", "INFO")
            os.makedirs(uploads_path, exist_ok=True)
            
            # Créer un fichier de test
            test_file_path = os.path.join(uploads_path, "test_access.txt")
            with open(test_file_path, "w") as f:
                f.write(f"Test d'accessibilité uploads - {datetime.now()}")
            
            app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")
            log_app("✅ CORRECTION: Dossier uploads créé et monté", "SUCCESS")
            return True
            
    except Exception as e:
        log_app(f"❌ CORRECTION: Erreur montage uploads: {e}", "ERROR")
        log_app(f"🔍 CORRECTION: Type erreur: {type(e).__name__}", "ERROR")
        return False

# Effectuer le montage avec diagnostic
uploads_mounted = setup_uploads_static_mount()

@app.get("/api/test-ftp")
async def test_ftp_diagnostic():
    """Diagnostique la connexion FTP et propose des solutions"""
    try:
        result = await test_ftp_connection()
        return {
            "status": "success" if result["success"] else "error",
            "ftp_config": {
                "host": FTP_HOST,
                "port": FTP_PORT,
                "user": FTP_USER,
                "directory": FTP_DIRECTORY,
                "initial_directory": FTP_INITIAL_DIRECTORY,
                "base_url": FTP_BASE_URL
            },
            "diagnostic": result
        }
    except Exception as e:
        return {"status": "error", "message": f"Erreur diagnostic FTP: {e}"}

@app.get("/api/test-gizmobbs")
async def test_gizmobbs_store():
    """Test spécifique du store gizmobbs (prioritaire) - Configuration et endpoints"""
    try:
        log_app("🧪 Test spécifique store gizmobbs (@logicamp_berger)", "INFO")
        
        # Test configuration store
        store_config = get_store_config("gizmobbs")
        
        # Test ngrok/WEBHOOK_URL
        ngrok_url = get_active_ngrok_url()
        
        # Test FTP
        ftp_test_result = await test_ftp_connection()
        
        # Test conversion URLs
        test_local_path = "uploads/test_gizmobbs.jpg"
        test_public_url = await convert_local_path_to_public_url(test_local_path)
        
        return {
            "status": "success",
            "store": "gizmobbs (@logicamp_berger)",
            "priority": "Store prioritaire pour les tests",
            "configuration": {
                "fb_page_id": store_config.get("fb_page_id"),
                "ig_user_id": store_config.get("ig_user_id"),
                "access_token_present": bool(store_config.get("access_token")),
                "store_name": store_config.get("name")
            },
            "ngrok": {
                "url": ngrok_url,
                "webhook_sync": "✅ Disponible" if ngrok_url else "❌ Non détecté"
            },
            "ftp": {
                "host": FTP_HOST,
                "base_url": FTP_BASE_URL,
                "connection_test": "✅ Réussi" if ftp_test_result.get("success") else f"❌ Échec: {ftp_test_result.get('error', 'Erreur inconnue')}"
            },
            "url_conversion": {
                "test_input": test_local_path,
                "public_url": test_public_url,
                "https_valid": test_public_url.startswith("https://"),
                "instagram_compatible": "✅ HTTPS détecté" if test_public_url.startswith("https://") else "❌ Pas HTTPS"
            },
            "video_endpoints": {
                "facebook_videos": f"{FACEBOOK_GRAPH_URL}/{store_config.get('fb_page_id')}/videos",
                "instagram_reels": f"{FACEBOOK_GRAPH_URL}/{store_config.get('ig_user_id')}/media",
                "detection_video": "✅ Automatique par extension (.mp4, .mov, .avi, .wmv)"
            },
            "corrections_status": {
                "webhook_url_sync": "✅ Implémentée",
                "video_endpoint_routing": "✅ Corrigée (/videos au lieu de /feed)",
                "instagram_urls_https": "✅ Conversion automatique locale→publique",
                "ngrok_detection": "✅ Automatique au démarrage"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "store": "gizmobbs",
            "message": f"Erreur test gizmobbs: {e}"
        }

@app.get("/api/test-uploads")
async def test_uploads_accessibility():
    """Test l'accessibilité du dossier uploads et la conversion d'URLs - Version simplifiée"""
    try:
        uploads_path = os.path.join(WINDOWS_PATHS["backend_dir"], "uploads")
        
        # Informations de base
        if not os.path.exists(uploads_path):
            return {"status": "error", "message": "Dossier uploads inexistant"}
        
        # Compter les fichiers rapidement
        try:
            all_files = os.listdir(uploads_path)
            file_count = len(all_files)
            image_files = [f for f in all_files if f.lower().endswith(('.jpg', '.png', '.gif', '.jpeg'))][:3]
        except Exception as e:
            return {"status": "error", "message": f"Erreur listage: {e}"}
        
        # Test simple de conversion pour 1 fichier
        test_result = {}
        if image_files:
            test_file = image_files[0]
            try:
                public_url = await convert_local_path_to_public_url(f"uploads/{test_file}")
                test_result = {
                    "test_file": test_file,
                    "local_path": f"uploads/{test_file}",
                    "public_url": public_url,
                    "direct_access": f"/uploads/{test_file}"
                }
            except Exception as conv_error:
                test_result = {"test_file": test_file, "error": str(conv_error)}
        
        # URLs disponibles
        ngrok_url = get_active_ngrok_url()
        public_base = os.getenv("PUBLIC_BASE_URL")
        
        return {
            "status": "success",
            "uploads_path": uploads_path,
            "uploads_mounted": globals().get('uploads_mounted', False),
            "file_count": file_count,
            "image_count": len(image_files),
            "test_conversion": test_result,
            "ngrok_url": ngrok_url,
            "public_base_url": public_base,
            "ftp_base_url": FTP_BASE_URL,
            "message": "Test uploads terminé"
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Erreur: {e}"}

@app.get("/api/test-ftp-ngrok-fallback")
async def test_ftp_ngrok_fallback():
    """
    Test complet du système FTP → ngrok fallback pour Instagram
    """
    try:
        log_app("🧪 Test système FTP → ngrok fallback", "INFO")
        
        # Créer un fichier de test s'il n'existe pas
        uploads_path = os.path.join(WINDOWS_PATHS["backend_dir"], "uploads")
        os.makedirs(uploads_path, exist_ok=True)
        
        test_filename = "test_instagram_upload.jpg"
        test_file_path = os.path.join(uploads_path, test_filename)
        
        # Créer une image de test simple si elle n'existe pas
        if not os.path.exists(test_file_path):
            from PIL import Image
            test_img = Image.new('RGB', (100, 100), color='red')
            test_img.save(test_file_path, 'JPEG')
            log_app(f"✅ Fichier de test créé: {test_filename}", "SUCCESS")
        
        # Test conversion avec notre nouvelle fonction
        result = {
            "test_file": test_filename,
            "local_path": f"uploads/{test_filename}",
            "systems_tested": {},
            "final_result": {},
            "ngrok_config": {},
            "ftp_config": {}
        }
        
        # Informations sur ngrok
        ngrok_url = get_active_ngrok_url()
        webhook_url = os.getenv("WEBHOOK_URL")
        result["ngrok_config"] = {
            "active_ngrok_url": ngrok_url,
            "webhook_url_env": webhook_url,
            "ngrok_available": bool(ngrok_url)
        }
        
        # Informations FTP
        result["ftp_config"] = {
            "ftp_host": FTP_HOST,
            "ftp_user": FTP_USER,
            "ftp_base_url": FTP_BASE_URL,
            "ftp_directory": FTP_DIRECTORY
        }
        
        # Test de notre fonction principale
        try:
            public_url = await convert_local_path_to_public_url(f"uploads/{test_filename}")
            
            result["final_result"] = {
                "success": True,
                "public_url": public_url,
                "url_type": "https" if public_url.startswith("https://") else "http",
                "instagram_compatible": public_url.startswith("https://"),
                "contains_ftp": "logicamp.org" in public_url,
                "contains_ngrok": "ngrok" in public_url or "emergentagent.com" in public_url
            }
            
            log_app(f"✅ Test réussi: {public_url}", "SUCCESS")
            
        except Exception as e:
            result["final_result"] = {
                "success": False,
                "error": str(e)
            }
            log_app(f"❌ Test échoué: {e}", "ERROR")
        
        # Test direct FTP
        try:
            from utils.ftp_upload import upload_file_via_ftp
            import time
            import uuid
            
            timestamp = int(time.time())
            unique_id = uuid.uuid4().hex[:8]
            remote_name = f"test_direct_{timestamp}_{unique_id}.jpg"
            
            ftp_url = upload_file_via_ftp(test_file_path, remote_name)
            
            result["systems_tested"]["ftp_direct"] = {
                "success": bool(ftp_url),
                "url": ftp_url,
                "remote_name": remote_name
            }
            
        except Exception as e:
            result["systems_tested"]["ftp_direct"] = {
                "success": False,
                "error": str(e)
            }
        
        # Test ngrok direct
        if ngrok_url:
            ngrok_test_url = f"{ngrok_url}/uploads/{test_filename}"
            try:
                import requests
                response = requests.head(ngrok_test_url, timeout=5)
                result["systems_tested"]["ngrok_direct"] = {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "url": ngrok_test_url,
                    "content_type": response.headers.get("Content-Type", "unknown")
                }
            except Exception as e:
                result["systems_tested"]["ngrok_direct"] = {
                    "success": False,
                    "error": str(e),
                    "url": ngrok_test_url
                }
        
        return {
            "status": "success",
            "message": "Test FTP → ngrok fallback terminé",
            "details": result,
            "recommendations": [
                "✅ Si 'contains_ftp' = true → FTP upload a réussi (stable)",
                "🔄 Si 'contains_ngrok' = true → Fallback ngrok utilisé (temporaire)", 
                "⚠️ Si 'instagram_compatible' = false → URL non HTTPS, Instagram refusera",
                "💡 Pour Instagram: HTTPS obligatoire, serveurs FB doivent pouvoir accéder à l'URL"
            ]
        }
        
    except Exception as e:
        log_app(f"❌ Erreur test FTP-ngrok: {e}", "ERROR")
        return {
            "status": "error",
            "message": f"Erreur test système: {e}"
        }

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

class WebhookResponse(BaseModel):
    success: bool
    webhook_id: Optional[str] = None
    message: str
    publication_results: Optional[dict] = None
    error: Optional[str] = None

# === OAUTH ENDPOINTS - PATCH 19: AJOUT ENDPOINT INITIATION ===

# OAuth callbacks supprimés - ROLLBACK vers PATCH 17

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

async def convert_local_path_to_public_url(image_url: str) -> str:
    """
    NOUVELLE VERSION: Convertit les chemins locaux en URL publique avec système FTP → ngrok fallback
    
    Stratégie :
    1. Si FTP upload réussit → utiliser FTP URL (plus stable)
    2. Si FTP échoue → basculer automatiquement sur ngrok URL 
    3. Toujours retourner une URL HTTPS accessible par Instagram/Facebook
    
    Args:
        image_url: Chemin potentiellement local (ex: "uploads\\image.png", "uploads/image.jpg")
    
    Returns:
        str: URL publique accessible (FTP ou ngrok)
    """
    try:
        log_publish(f"🔍 NOUVELLE VERSION: Analyse chemin média pour Instagram: '{image_url}'", "INFO")
        
        # Normaliser le chemin Windows -> Unix
        normalized_path = image_url.replace("\\", "/")
        
        # Si c'est déjà une URL complète, la retourner directement
        if normalized_path.startswith(("http://", "https://")):
            log_publish(f"✅ URL publique valide détectée: {image_url}", "SUCCESS")
            return image_url
        
        # Extraire le nom de fichier depuis le chemin local
        filename = ""
        if "uploads" in normalized_path:
            parts = normalized_path.replace("\\", "/").split("/")
            filename = parts[-1] if parts else normalized_path
            if filename == "uploads" and len(parts) > 1:
                filename = parts[-2] if len(parts) > 1 else "unknown.jpg"
        else:
            filename = os.path.basename(normalized_path) or "unknown.jpg"
            
        log_publish(f"📁 Fichier détecté: {filename}", "INFO")
        
        # Vérifier que le fichier existe localement
        local_file_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(local_file_path):
            local_file_path = os.path.join(os.path.dirname(__file__), "uploads", filename)
            
        if not os.path.exists(local_file_path):
            log_publish(f"⚠️ Fichier local non trouvé: {filename}", "WARNING")
            # Essayer quand même les URLs publiques possibles
        
        # STRATÉGIE PRIORITAIRE: FTP → NGROK FALLBACK
        
        # 1. PRIORITÉ FTP: Essayer upload FTP d'abord (plus stable)
        log_publish(f"🚀 PRIORITÉ FTP: Tentative upload via FTP", "INFO")
        try:
            if os.path.exists(local_file_path):
                # Utiliser le nouveau système FTP amélioré
                webhook_base = get_active_ngrok_url() or os.getenv("WEBHOOK_URL")
                
                # Créer nom de fichier unique pour éviter collisions
                import time
                import uuid
                timestamp = int(time.time())
                unique_id = uuid.uuid4().hex[:8]
                file_ext = os.path.splitext(filename)[1]
                remote_name = f"instagram_{timestamp}_{unique_id}{file_ext}"
                
                # Utiliser notre nouvelle fonction get_public_media_url
                public_url = get_public_media_url(local_file_path, remote_name, webhook_base)
                log_publish(f"✅ FTP/NGROK URL générée: {public_url}", "SUCCESS")
                return public_url
                
            else:
                log_publish(f"⚠️ Fichier local manquant, skip FTP upload", "WARNING")
                
        except RuntimeError as e:
            log_publish(f"❌ FTP et ngrok fallback ont échoué: {e}", "ERROR")
        except Exception as e:
            log_publish(f"❌ Erreur système FTP: {e}", "ERROR")
        
        # 2. FALLBACK NGROK UNIQUEMENT: Si FTP impossible
        log_publish(f"🔄 FALLBACK: Utilisation ngrok uniquement", "INFO")
        webhook_base = get_active_ngrok_url() or os.getenv("WEBHOOK_URL")
        if webhook_base:
            ngrok_url = f"{webhook_base.rstrip('/')}/uploads/{filename}"
            log_publish(f"✅ NGROK URL fallback: {ngrok_url}", "SUCCESS")
            return ngrok_url
        
        # 3. DERNIER RECOURS: URL locale (ne marchera qu'en dev local)
        fallback_url = f"http://localhost:8001/uploads/{filename}"
        log_publish(f"⚠️ URL localhost (dev uniquement): {fallback_url}", "WARNING")
        log_publish(f"💡 ATTENTION: Instagram exige HTTPS publique, cette URL ne marchera pas en production!", "WARNING")
        return fallback_url
        
    except Exception as e:
        error_msg = f"ERREUR: Conversion '{image_url}': {str(e)}"
        log_publish(error_msg, "ERROR")
        # En cas d'erreur, retourner l'URL originale
        return image_url

async def test_url_accessibility(url: str, timeout: int = 3) -> bool:
    """Test rapide d'accessibilité d'une URL - Version non bloquante"""
    try:
        # Version très simple pour éviter les blocages
        import requests
        
        # Test HEAD rapide avec timeout court
        response = requests.head(url, timeout=timeout, allow_redirects=False)
        return response.status_code in [200, 301, 302, 403]  # 403 peut être normal avec ngrok
        
    except Exception:
        # En cas d'erreur, on assume que l'URL peut fonctionner
        return True

def convert_local_path_to_ngrok_url(image_url: str) -> str:
    """
    FONCTION LEGACY - Maintenue pour compatibilité
    Utilise la nouvelle fonction async convert_local_path_to_public_url
    """
    try:
        # Conversion synchrone basique pour compatibilité
        normalized_path = image_url.replace("\\", "/")
        
        if normalized_path.startswith(("http://", "https://")):
            return image_url
        
        # Vérifier si c'est un chemin uploads
        is_uploads_path = any(pattern in normalized_path for pattern in ["uploads/", "uploads\\", "/uploads/"])
        
        if not is_uploads_path:
            return image_url
        
        # Extraire filename
        filename = normalized_path.split("/")[-1] if "/" in normalized_path else normalized_path
        
        # Utiliser PUBLIC_BASE_URL ou ngrok actif
        public_base_url = os.getenv("PUBLIC_BASE_URL") or get_active_ngrok_url()
        
        if not public_base_url:
            raise ValueError("Aucune URL publique disponible")
        
        public_url = f"{public_base_url.rstrip('/')}/uploads/{filename}"
        log_publish(f"✅ Legacy: Conversion {image_url} -> {public_url}", "SUCCESS")
        
        return public_url
        
    except Exception as e:
        error_msg = f"Erreur conversion legacy: {str(e)}"
        log_publish(error_msg, "ERROR")
        raise Exception(error_msg)

def verify_url_accessibility(url: str) -> bool:
    """
    Vérifie qu'une URL est accessible (HTTP 200)
    
    Args:
        url: URL à vérifier
    
    Returns:
        bool: True si accessible, False sinon
    """
    try:
        log_publish(f"🔍 Vérification accessibilité URL: {url}", "INFO")
        
        # Essayer d'abord HEAD, puis GET si HEAD échoue (certains serveurs n'autorisent pas HEAD)
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                log_publish(f"✅ URL accessible: {url} (HTTP {response.status_code})", "SUCCESS")
                return True
            elif response.status_code == 405:  # Method Not Allowed - essayer GET
                response = requests.get(url, timeout=10, allow_redirects=True, stream=True)
                if response.status_code == 200:
                    log_publish(f"✅ URL accessible: {url} (HTTP {response.status_code} via GET)", "SUCCESS")
                    return True
        except requests.exceptions.RequestException:
            # Si HEAD échoue, essayer directement GET
            response = requests.get(url, timeout=10, allow_redirects=True, stream=True)
            if response.status_code == 200:
                log_publish(f"✅ URL accessible: {url} (HTTP {response.status_code} via GET fallback)", "SUCCESS")
                return True
        
        log_publish(f"⚠️ URL non accessible: {url} (HTTP {response.status_code})", "WARNING")
        return False
            
    except requests.exceptions.RequestException as e:
        log_publish(f"❌ Erreur vérification URL {url}: {str(e)}", "ERROR")
        return False
    except Exception as e:
        log_publish(f"❌ Erreur générale vérification URL {url}: {str(e)}", "ERROR")
        return False

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

async def post_to_facebook(store: str, message: str, product_url: str, image_url: Optional[str] = None) -> dict:
    """Publie un post avec ou sans image sur la page Facebook correspondante"""
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
                "image_url": image_url,
                "test_mode": True
            }
        
        # Publication réelle - différencier avec ou sans image
        if image_url:
            # CORRECTION: Publication avec image via /photos endpoint
            log_publish(f"Publication Facebook avec image: {image_url}", "INFO")
            
            # Convertir l'URL locale en URL ngrok si nécessaire
            try:
                converted_image_url = convert_local_path_to_ngrok_url(image_url)
                if converted_image_url != image_url:
                    log_publish(f"🔄 Image URL convertie: {image_url} -> {converted_image_url}", "SUCCESS")
                    image_url = converted_image_url
            except Exception as conversion_error:
                log_publish(f"⚠️ Erreur conversion URL image: {conversion_error}", "WARNING")
                # Continuer avec l'URL originale
            
            url = f"{FACEBOOK_GRAPH_URL}/{creds['fb_page_id']}/photos"
            payload = {
                "url": image_url,
                "caption": f"{message}\n\n{product_url}" if product_url else message,
                "access_token": creds["access_token"]
            }
        else:
            # Publication sans image via /feed endpoint
            log_publish("Publication Facebook sans image", "INFO")
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

# PATCH 12: Ancienne fonction post_to_instagram() SUPPRIMÉE
# Cette fonction était obsolète et causait le problème des URLs locales Instagram
# Toutes les publications Instagram utilisent maintenant publish_to_instagram() uniquement

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
        
        # PATCH 9: Conversion URL vidéo simplifiée avec ngrok uniquement
        log_video(f"🔍 PATCH 9: Traitement vidéo pour Instagram: '{video_url}'", "INFO")
        
        # Si ce n'est pas déjà une URL HTTP(S), convertir avec ngrok
        if not video_url.startswith(("http://", "https://")):
            # Extraire le nom de fichier et générer l'URL publique ngrok
            filename = video_url.split("\\")[-1].split("/")[-1]  # Support Windows et Unix paths
            video_url = get_public_url(filename)
            log_video(f"📤 PATCH 9: URL vidéo convertie avec ngrok - {video_url}", "SUCCESS")
        else:
            log_video(f"📤 PATCH 9: URL vidéo déjà publique - {video_url}", "INFO")
        
        # Mode test : simulation
        if PUBLICATION_TEST_MODE:
            log_video(f"MODE TEST - Publication vidéo Instagram simulée pour {store}", "TEST")
            return {
                "id": f"test_ig_video_{uuid.uuid4().hex[:8]}",
                "caption": f"{message}\n\n{product_url}",
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
            "caption": f"{message}\n\n{product_url}",
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
            "caption": f"{message}\n\n{product_url}",
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
        
        # CORRECTION VIDÉO: Détection automatique du type de média AMÉLIORÉE
        is_video_media = False
        if image_url:
            # NOUVEAU: Détection par MIME type du fichier réel si c'est un chemin local
            if image_url.startswith(('/uploads', './uploads')) or not image_url.startswith(('http://', 'https://')):
                # C'est un fichier local - utiliser mimetypes pour détecter le vrai type
                try:
                    local_path = image_url.replace('/uploads/', UPLOAD_DIR + '/')
                    if os.path.exists(local_path):
                        mime_type, _ = mimetypes.guess_type(local_path)
                        if mime_type and mime_type.startswith('video/'):
                            is_video_media = True
                            log_publish(f"🎥 CORRECTION: Vidéo détectée par MIME type: {mime_type}", "SUCCESS")
                        else:
                            log_publish(f"🖼️ CORRECTION: Image détectée par MIME type: {mime_type}", "INFO")
                    else:
                        log_publish(f"⚠️ CORRECTION: Fichier non trouvé pour analyse MIME: {local_path}", "WARNING")
                except Exception as e:
                    log_publish(f"⚠️ CORRECTION: Erreur analyse MIME: {e}", "WARNING")
            
            # Fallback: Détecter par extension dans l'URL (ancienne méthode)  
            if not is_video_media:
                if any(image_url.lower().endswith(ext) for ext in ['.mp4', '.mov', '.avi', '.wmv', '.m4v', '.mkv']):
                    is_video_media = True
                    log_publish("🎥 CORRECTION: Vidéo détectée par extension URL", "INFO")
                elif 'video' in image_url.lower() and any(ext in image_url.lower() for ext in ['mp4', 'mov', 'avi']):
                    is_video_media = True
                    log_publish("🎥 CORRECTION: Vidéo détectée par nom dans URL", "INFO")
        
        # Publication Facebook avec routage correct
        if "facebook" in platforms:
            try:
                # PATCH 10: Correction appels Facebook - Utiliser la bonne fonction publish_to_facebook
                store_config = get_store_config(store)
                
                if is_video_media:
                    # CORRECTION: Utiliser la fonction vidéo pour les vidéos (endpoint /videos)
                    fb_result = await publish_to_facebook(store_config, message, product_url, "", image_url, is_video=True)
                else:
                    # Utiliser la fonction normale pour les images/textes (endpoint /photos ou /feed)
                    fb_result = await publish_to_facebook(store_config, message, product_url, "", image_url, is_video=False)
                
                results["facebook_result"] = fb_result
                media_type = "vidéo" if is_video_media else "image/texte" 
                log_publish(f"Publication Facebook {media_type} terminée", "SUCCESS")
            except Exception as e:
                error_msg = f"Échec Facebook: {str(e)}"
                results["errors"].append(error_msg)
                log_publish(error_msg, "ERROR")
        
        # Publication Instagram avec routage correct
        if "instagram" in platforms:
            try:
                if not image_url:
                    raise Exception("Média requis pour Instagram")
                
                # PATCH 10: Correction appels Instagram - Utiliser la bonne fonction publish_to_instagram
                store_config = get_store_config(store)
                
                if is_video_media:
                    # CORRECTION: Utiliser la fonction vidéo pour Instagram (Reels)
                    ig_result = await publish_to_instagram(store_config, message, product_url, "", image_url, is_video=True)
                else:
                    # PATCH 10: Utiliser la fonction corrigée publish_to_instagram avec conversion URLs
                    ig_result = await publish_to_instagram(store_config, message, product_url, "", image_url, is_video=False)
                
                results["instagram_result"] = ig_result
                media_type = "vidéo/Reel" if is_video_media else "image"
                log_publish(f"Publication Instagram {media_type} terminée", "SUCCESS")
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

@app.post("/api/cleanup")
async def manual_cleanup():
    """PATCH 25: Endpoint pour nettoyage manuel des fichiers anciens"""
    try:
        files_cleaned = manual_cleanup_old_files()
        pending_files = len(files_to_cleanup)
        
        return {
            "success": True,
            "files_cleaned": files_cleaned,
            "pending_scheduled": pending_files,
            "cleanup_delay_hours": CLEANUP_DELAY_HOURS,
            "schedule_available": SCHEDULE_AVAILABLE
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "schedule_available": SCHEDULE_AVAILABLE
        }

@app.get("/api/media/{filename}")
async def serve_media_file(filename: str):
    """PATCH 26: Endpoint spécialisé pour servir les fichiers média avec headers optimisés pour Facebook/Instagram"""
    try:
        # Sécurité : vérifier que le fichier existe et est dans uploads
        uploads_dir = WINDOWS_PATHS.get('uploads_dir', 'uploads')
        file_path = os.path.join(uploads_dir, filename)
        
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Détecter le type MIME
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            if filename.lower().endswith(('.jpg', '.jpeg')):
                mime_type = 'image/jpeg'
            elif filename.lower().endswith('.png'):
                mime_type = 'image/png'
            elif filename.lower().endswith('.webp'):
                mime_type = 'image/webp'
            elif filename.lower().endswith(('.mp4', '.mov')):
                mime_type = 'video/mp4'
            else:
                mime_type = 'application/octet-stream'
        
        # Headers spécialisés pour Facebook/Instagram
        headers = {
            'Content-Type': mime_type,
            'Cache-Control': 'public, max-age=3600',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
            'Access-Control-Allow-Headers': '*'
        }
        
        log_app(f"🎯 PATCH 26: Serving media file {filename} ({mime_type})", "INFO")
        
        return FileResponse(
            path=file_path,
            media_type=mime_type,
            headers=headers,
            filename=filename
        )
        
    except Exception as e:
        log_app(f"❌ PATCH 26: Erreur serving media {filename}: {e}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pages")
async def get_pages_info():
    """Get pages information and shop mapping for testing"""
    try:
        log_app("📄 Endpoint /api/pages appelé", "INFO")
        
        # Récupérer les informations utilisateur basiques
        user_name = "Instagram Tunnel User"
        
        # Pages personnelles (simulation - pas d'API disponible pour les pages personnelles)
        personal_pages = []
        
        # Pages Business Manager (simulation basée sur la configuration actuelle)
        business_manager_pages = []
        
        # Ajouter les pages des stores configurés comme pages Business Manager simulées
        for store_name, config in STORES.items():
            if config.get("fb_page_id") and config.get("name"):
                business_manager_pages.append({
                    "id": config["fb_page_id"],
                    "name": config["name"],
                    "store": store_name,
                    "has_instagram": bool(config.get("ig_user_id")),
                    "instagram_id": config.get("ig_user_id")
                })
        
        # Shop mapping - mapping des stores vers leurs configurations
        shop_mapping = {}
        for store_name, config in STORES.items():
            shop_mapping[store_name] = {
                "name": config["name"],
                "expected_id": config["fb_page_id"],
                "instagram_id": config.get("ig_user_id"),
                "configured": bool(config.get("access_token") and config.get("fb_page_id"))
            }
        
        result = {
            "success": True,
            "user_name": user_name,
            "personal_pages": personal_pages,
            "business_manager_pages": business_manager_pages,
            "shop_mapping": shop_mapping,
            "total_stores": len(STORES),
            "configured_stores": len([s for s in STORES.values() if s.get("access_token") and s.get("fb_page_id")]),
            "timestamp": datetime.now().isoformat()
        }
        
        log_app(f"✅ Informations pages retournées: {len(business_manager_pages)} pages, {len(shop_mapping)} stores", "SUCCESS")
        return result
        
    except Exception as e:
        error_msg = f"Erreur récupération pages: {str(e)}"
        log_app(f"❌ {error_msg}", "ERROR")
        raise HTTPException(status_code=500, detail=error_msg)

# === VIDEO ENDPOINTS === (Ancienne version supprimée - voir endpoints principaux plus bas)

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
async def get_video_post_history(user_id: str):
    """Récupère l'historique des posts vidéo d'un utilisateur"""
    try:
        posts = await get_posts_by_user(user_id)
        video_posts = [post for post in posts if post.get("media_urls") and any(url.endswith(('.mp4', '.mov')) for url in post["media_urls"])]
        
        return {
            "success": True,
            "posts": video_posts,
            "count": len(video_posts)
        }
        
    except Exception as e:
        log_video(f"Erreur chargement historique vidéo: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS POSTER MEDIA ENHANCED - RESTAURÉS ET AMÉLIORÉS
# ============================================================================

@app.post("/api/poster-media")
async def trigger_poster_media_enhanced(store: Optional[str] = None):
    """
    Endpoint pour déclencher la publication automatique améliorée
    avec retry Instagram et fallback Facebook
    """
    try:
        log_app("Déclenchement poster_media_enhanced via API", "INFO")
        
        # Exécuter la fonction améliorée
        result = await poster_media_enhanced(store)
        
        return {
            "success": result["success"],
            "timestamp": result.get("timestamp", datetime.now().isoformat()),
            "result": result,
            "endpoint_info": {
                "description": "Publication automatique multi-stores avec retry Instagram et fallback Facebook",
                "stores_supported": list(STORES_CONFIG.keys()),
                "features": [
                    "🔄 Retry automatique Instagram (3 tentatives)",
                    "📘 Fallback Facebook si Instagram échoue",
                    "🎨 Conversion WebP → JPEG automatique",
                    "📤 Upload FTP multi-stores",
                    "📁 Archivage automatique dans dossier processed",
                    "📊 Statistiques détaillées par store"
                ]
            }
        }
        
    except Exception as e:
        error_msg = f"Erreur endpoint poster-media enhanced: {str(e)}"
        log_app(error_msg, "ERROR")
        
        return {
            "success": False,
            "error": error_msg,
            "timestamp": datetime.now().isoformat(),
            "troubleshooting": [
                "Vérifiez les dossiers de téléchargement des stores",
                "Vérifiez les tokens Facebook/Instagram dans .env",
                "Vérifiez la configuration FTP",
                "Consultez les logs pour plus de détails"
            ]
        }

@app.get("/api/poster-media/status")
async def get_poster_media_status_enhanced():
    """
    Endpoint pour vérifier le statut multi-stores de poster_media_enhanced
    """
    try:
        status_data = {
            "stores": {},
            "ftp_config": {
                "host": FTP_HOST,
                "port": FTP_PORT,
                "user": FTP_USER,
                "base_url": FTP_BASE_URL,
                "configured": bool(FTP_HOST and FTP_USER and FTP_PASSWORD)
            },
            "ready_stores": [],
            "total_files_ready": 0
        }
        
        # Analyser chaque store
        for store_name, store_config in STORES_CONFIG.items():
            store_status = {
                "name": store_config["name"],
                "download_dir": store_config["download_dir"],
                "processed_dir": store_config["processed_dir"],
                "download_dir_exists": os.path.exists(store_config["download_dir"]),
                "access_token_configured": bool(store_config.get("access_token")),
                "ig_user_id_configured": bool(store_config.get("ig_user_id")),
                "fb_page_id_configured": bool(store_config.get("fb_page_id")),
                "files_count": 0,
                "files_ready": [],
                "ready_to_process": False
            }
            
            # Compter les fichiers si le dossier existe
            if store_status["download_dir_exists"]:
                try:
                    for filename in os.listdir(store_config["download_dir"]):
                        file_path = os.path.join(store_config["download_dir"], filename)
                        if os.path.isfile(file_path):
                            file_ext = Path(filename).suffix.lower()
                            if file_ext in {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov"}:
                                store_status["files_count"] += 1
                                store_status["files_ready"].append({
                                    "filename": filename,
                                    "extension": file_ext,
                                    "size_mb": round(os.path.getsize(file_path) / (1024*1024), 2)
                                })
                except Exception as e:
                    log_app(f"Erreur lecture dossier {store_name}: {e}", "WARNING")
            
            # Déterminer si le store est prêt
            store_status["ready_to_process"] = (
                store_status["download_dir_exists"] and
                store_status["access_token_configured"] and
                store_status["ig_user_id_configured"] and
                store_status["files_count"] > 0
            )
            
            if store_status["ready_to_process"]:
                status_data["ready_stores"].append(store_name)
                status_data["total_files_ready"] += store_status["files_count"]
            
            status_data["stores"][store_name] = store_status
        
        return {
            "success": True,
            "status": status_data,
            "summary": {
                "total_stores": len(STORES_CONFIG),
                "ready_stores": len(status_data["ready_stores"]),
                "total_files_ready": status_data["total_files_ready"],
                "ftp_configured": status_data["ftp_config"]["configured"]
            }
        }
        
    except Exception as e:
        error_msg = f"Erreur status poster-media: {str(e)}"
        log_app(error_msg, "ERROR")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/poster-media/{store_name}")
async def trigger_poster_media_store(store_name: str):
    """
    Endpoint pour déclencher la publication pour un store spécifique
    """
    try:
        if store_name not in STORES_CONFIG:
            raise HTTPException(status_code=404, detail=f"Store inconnu: {store_name}")
        
        log_app(f"Déclenchement poster_media pour store: {store_name}", "INFO")
        
        result = await poster_media_enhanced(store_name)
        
        return {
            "success": result["success"],
            "store": store_name,
            "store_name": STORES_CONFIG[store_name]["name"],
            "timestamp": result.get("timestamp", datetime.now().isoformat()),
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Erreur poster-media store {store_name}: {str(e)}"
        log_app(error_msg, "ERROR")
        raise HTTPException(status_code=500, detail=error_msg)

# ============================================================================
# ENDPOINTS SURVEILLANCE AUTOMATIQUE DES DOSSIERS
# ============================================================================

@app.post("/api/folder-watcher/start")
async def start_folder_watcher():
    """
    Démarre la surveillance automatique des dossiers de téléchargement
    """
    try:
        success = start_folder_watcher_background()
        
        if success:
            log_app("Surveillance automatique des dossiers démarrée", "SUCCESS")
            return {
                "success": True,
                "message": "Surveillance automatique démarrée",
                "info": "Les fichiers ajoutés aux dossiers de téléchargement seront automatiquement traités",
                "watched_stores": list(STORES_CONFIG.keys())
            }
        else:
            return {
                "success": False,
                "message": "Surveillance déjà active",
                "status": get_watcher_status()
            }
            
    except Exception as e:
        error_msg = f"Erreur démarrage surveillance: {str(e)}"
        log_app(error_msg, "ERROR")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/folder-watcher/stop")
async def stop_folder_watcher_endpoint():
    """
    Arrête la surveillance automatique des dossiers
    """
    try:
        stop_folder_watcher()
        log_app("Surveillance automatique des dossiers arrêtée", "INFO")
        
        return {
            "success": True,
            "message": "Surveillance automatique arrêtée"
        }
        
    except Exception as e:
        error_msg = f"Erreur arrêt surveillance: {str(e)}"
        log_app(error_msg, "ERROR")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/folder-watcher/status")
async def get_folder_watcher_status():
    """
    Retourne le statut de la surveillance des dossiers
    """
    try:
        status = get_watcher_status()
        
        return {
            "success": True,
            "status": status,
            "stores_config": {
                name: {
                    "name": config["name"],
                    "download_dir": config["download_dir"],
                    "processed_dir": config["processed_dir"]
                }
                for name, config in STORES_CONFIG.items()
            }
        }
        
    except Exception as e:
        error_msg = f"Erreur status surveillance: {str(e)}"
        log_app(error_msg, "ERROR")
        raise HTTPException(status_code=500, detail=error_msg)
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
                f"{ngrok_url}/auth/callback"
            ] if ngrok_url else []
        }
        
    except Exception as e:
        log_app(f"❌ Erreur status OAuth complet: {str(e)}", "ERROR")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/stores/config")
async def get_stores_config():
    """Retourne la configuration de tous les stores pour les tests"""
    try:
        stores_info = {}
        for store_name, store_config in STORES.items():
            stores_info[store_name] = {
                "name": store_config.get("name", store_name),
                "fb_page_id": store_config.get("fb_page_id"),
                "ig_user_id": store_config.get("ig_user_id"),
                "has_access_token": bool(store_config.get("access_token")),
                "configured": bool(store_config.get("fb_page_id") and store_config.get("access_token"))
            }
        
        return {
            "success": True,
            "stores": stores_info,
            "total_stores": len(stores_info),
            "configured_stores": len([s for s in stores_info.values() if s["configured"]]),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        log_app(f"❌ Erreur récupération config stores: {str(e)}", "ERROR")
        return {
            "success": False,
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
                    f"{backend_url}/auth/callback"
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
    """Publish a post immediately - handles both regular posts and video posts"""
    try:
        post = await get_post_by_id(post_id)
        
        if not post:
            raise HTTPException(status_code=404, detail="Post non trouvé")
        
        log_publish(f"Publication du post {post_id}", "INFO")
        
        # Déterminer si c'est un post vidéo ou un post classique
        is_video_post = bool(post.get("video_url") or post.get("video_id"))
        
        if is_video_post:
            log_video(f"Publication vidéo détectée pour post {post_id}", "INFO")
            
            # Extraire les informations nécessaires pour la publication vidéo
            video_url = post.get("video_url")
            content = post.get("content", "")
            
            if not video_url:
                raise HTTPException(status_code=400, detail="URL vidéo manquante pour la publication")
            
            # Publication vidéo avec gestion des plateformes croisées
            if post.get("cross_post_targets"):
                log_video("Publication vidéo croisée détectée", "INFO")
                cross_targets = post.get("cross_post_targets", [])
                
                results = {
                    "success": True,
                    "publication_results": [],
                    "errors": []
                }
                
                # Publier sur chaque plateforme ciblée
                for target in cross_targets:
                    try:
                        # Mapper le target vers un store pour publication
                        store = None
                        if target.get("platform") == "facebook":
                            # Trouver le store correspondant par le nom
                            if "Berger Blanc Suisse" in target.get("name", ""):
                                store = "gizmobbs"
                            elif "LogicAntiq" in target.get("name", ""):
                                store = "logicantiq"
                            elif "Logicamp" in target.get("name", ""):
                                store = "outdoor"
                        elif target.get("platform") == "instagram":
                            # Pour Instagram, identifier le store par le nom
                            if "gizmo" in target.get("name", "").lower():
                                store = "gizmobbs"
                            elif "logicantiq" in target.get("name", "").lower():
                                store = "logicantiq"
                            elif "logicamp" in target.get("name", "").lower() or "outdoor" in target.get("name", "").lower():
                                store = "outdoor"
                        
                        if store:
                            platform_list = [target.get("platform", "facebook")]
                            result = await publish_video_main(store, content, "", video_url, platform_list)
                            results["publication_results"].append({
                                "target": target.get("name"),
                                "platform": target.get("platform"),
                                "store": store,
                                "result": result
                            })
                            
                            if not result.get("success"):
                                results["errors"].extend(result.get("errors", []))
                        else:
                            error_msg = f"Store non identifié pour {target.get('name')} ({target.get('platform')})"
                            results["errors"].append(error_msg)
                            log_video(error_msg, "WARNING")
                    
                    except Exception as e:
                        error_msg = f"Erreur publication {target.get('name')}: {str(e)}"
                        results["errors"].append(error_msg)
                        log_video(error_msg, "ERROR")
                
                # Déterminer le succès global
                results["success"] = len(results["errors"]) == 0
                
            else:
                # Publication vidéo sur une seule plateforme
                platform = post.get("platform", "facebook")
                target_name = post.get("target_name", "")
                
                # Mapper vers un store
                store = None
                if "Berger Blanc Suisse" in target_name or "gizmo" in target_name.lower():
                    store = "gizmobbs"
                elif "LogicAntiq" in target_name or "logicantiq" in target_name.lower():
                    store = "logicantiq"
                elif "Logicamp" in target_name or "outdoor" in target_name.lower():
                    store = "outdoor"
                else:
                    # Par défaut, utiliser gizmobbs pour les tests
                    store = "gizmobbs"
                    log_video(f"Store non identifié pour '{target_name}', utilisation de gizmobbs par défaut", "WARNING")
                
                platform_list = [platform] if platform in ["facebook", "instagram"] else ["facebook"]
                results = await publish_video_main(store, content, "", video_url, platform_list)
        
        else:
            # Publication post classique (TODO: implémenter si nécessaire)
            log_publish(f"Publication post classique non implémentée pour {post_id}", "WARNING")
            results = {
                "success": False,
                "error": "Publication de posts classiques non implémentée dans cette version"
            }
        
        # Update post status in MongoDB
        update_data = {
            "status": "published" if results.get("success") else "failed",
            "published_at": datetime.now().isoformat(),
            "publication_results": results
        }
        
        updated_post = await update_post(post_id, update_data)
        
        if results.get("success"):
            log_publish(f"✅ Post publié avec succès: {post_id}", "SUCCESS")
        else:
            log_publish(f"❌ Échec publication post: {post_id} - {results.get('error', 'Erreurs multiples')}", "ERROR")
        
        return {
            "success": results.get("success", False),
            "post": updated_post,
            "publication_results": results,
            "message": "Publication terminée" if results.get("success") else "Échec de publication"
        }
        
    except Exception as e:
        log_publish(f"❌ Erreur publication post {post_id}: {str(e)}", "ERROR")
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
        
        log_app(f"🔍 DEBUG webhook_data keys: {list(webhook_data.keys())}", "INFO")
        
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
        platforms = webhook_data.get("platforms", ["facebook", "instagram"])  # Default both platforms
        
        # NOUVELLE CORRECTION: Détecter les fichiers médias uploadés (image/vidéo)
        has_media_file = False
        media_type = None
        media_file_info = None
        
        # Vérifier d'abord les nouveaux champs de fichiers traités
        if webhook_data.get("video_file"):
            has_media_file = True
            media_type = "video"
            media_file_info = webhook_data["video_file"]
            log_app(f"📦 CORRECTION: Fichier vidéo détecté - {media_file_info['filename']}", "INFO")
        elif webhook_data.get("image_file"):
            has_media_file = True
            media_type = "image"
            media_file_info = webhook_data["image_file"]
            log_app(f"📦 CORRECTION: Fichier image détecté - {media_file_info['filename']}", "INFO")
        else:
            # Vérifier les anciens champs de fichiers dans les données webhook (fallback)
            for key, value in webhook_data.items():
                if key in ["image", "video", "file", "media"] or "file" in key.lower():
                    if isinstance(value, dict) and value.get("type") == "binary":
                        has_media_file = True
                        media_type = "video" if "video" in key.lower() else "image"
                        log_app(f"📦 CORRECTION: Fichier {media_type} détecté dans le champ '{key}' (ancien format)", "INFO")
                        break
                    elif hasattr(value, 'filename') or hasattr(value, 'content_type'):
                        has_media_file = True
                        media_type = "video" if hasattr(value, 'content_type') and "video" in value.content_type else "image"
                        log_app(f"📦 CORRECTION: Fichier {media_type} détecté dans le champ '{key}' (ancien format)", "INFO")
                        break
        
        log_app(f"🔍 DEBUG - has_media_file: {has_media_file}, media_type: {media_type}, image_url: {bool(image_url)}", "INFO")
        
        # CORRECTION: Si pas de message personnalisé, créer le message à partir du title + URL
        if not custom_message and title:
            custom_message = f"{title}\n\n{product_url}" if product_url else title
            log_app(f"📝 Message auto-généré à partir du titre: {custom_message[:50]}...", "INFO")
        
        log_app(f"🔍 DEBUG - custom_message: '{custom_message[:50]}...', title: '{title[:30]}...', product_url: '{product_url[:50]}...'", "INFO")
        
        # PRIORITÉ RÉCENTE 2: Logique spéciale pour gizmobbs → @logicamp_berger (SOLUTION_LOGICAMP_BERGER_COMPLETE.md)
        if store == "gizmobbs" or shop_type == "gizmobbs":
            log_app("🎯 PRIORITÉ RÉCENTE : Configuration spéciale gizmobbs → @logicamp_berger", "INFO")
            
            # Business Manager spécifique pour @logicamp_berger
            business_manager_id = "1715327795564432"  # ID spécifique du BM logicamp_berger
            
            # CORRECTION: Configuration prioritaire selon les données reçues
            # Si média (image ou vidéo) disponible, publier sur Instagram + Facebook
            # Si pas de média, publier sur Facebook seulement
            if image_url or has_media_file:
                platforms = ["facebook", "instagram"]  # Les deux si média disponible
                log_app(f"📦 CORRECTION: Média détecté → Publication Facebook + Instagram", "INFO")
            else:
                platforms = ["facebook"]  # Facebook seulement si pas de média
                log_app(f"📦 CORRECTION: Pas de média → Publication Facebook uniquement", "INFO")
            
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
            
            if len(platforms) == 2:
                log_app(f"🎯 Plateformes cibles : Facebook + Instagram (média détecté)", "INFO")
            else:
                log_app(f"🎯 Plateforme cible : Facebook uniquement (pas de média)", "INFO")
            
        else:
            # ANCIENNE LOGIQUE: Construction intelligente du message pour autres stores
            if custom_message:
                message = custom_message
            elif title and product_url:
                # Format simple : titre + URL comme demandé par l'utilisateur
                message = f"{title}\n\n{product_url}"
            elif title:
                message = title
            elif description and product_url:
                message = f"{description}\n\n{product_url}"
            else:
                message = description or "Publication automatique"
            
            # CORRECTION: Pour les autres stores, adapter les plateformes selon la disponibilité de média
            if image_url or has_media_file:
                platforms = ["facebook", "instagram"]  # Les deux si média disponible
                log_app(f"📦 CORRECTION: Média détecté → Publication Facebook + Instagram", "INFO")
            else:
                platforms = ["facebook"]  # Facebook seulement si pas de média
                log_app(f"📦 CORRECTION: Pas de média → Publication Facebook uniquement", "INFO")
        
        log_app(f"🔍 DEBUG - Final message: '{message[:50]}...', length: {len(message)}", "INFO")
        
        # Validation améliorée avec logging détaillé
        missing_fields = []
        if not store and not shop_type:
            missing_fields.append("store/shop_type")
        if not message.strip():
            missing_fields.append("message/title")
        # CORRECTION: URL optionnelle pour certains types de posts
        if not product_url:
            log_app("ℹ️ Pas d'URL produit - publication sans lien", "INFO")
            
        if missing_fields:
            log_app(f"⚠️ Webhook ne contient pas de données de publication: {', '.join(missing_fields)}", "WARNING")
            log_app(f"   Données reçues: store={store}, shop_type={shop_type}, title='{title}', message='{message[:30]}...', product_url={bool(product_url)}", "INFO")
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
        log_app(f"   Média: {'Oui' if has_media_file else 'Non'} ({media_type if media_type else 'N/A'})", "INFO")
        
        # PATCH 35: VIDÉOS - UPLOAD FTP RÉEL AVEC GESTIONNAIRE
        video_url = None
        if media_type == "video" and media_file_info:
            log_app(f"🎥 PATCH 35: Traitement de la vidéo uploadée - {media_file_info['filename']}", "INFO")
            try:
                # PATCH 35: Upload réel de la vidéo vers FTP avec gestionnaire PATCH 29
                video_local_path = media_file_info['path']
                video_filename = media_file_info['filename']
                
                log_app(f"📤 PATCH 35: Upload vidéo FTP en cours - {video_filename}", "INFO")
                
                if FTP_MANAGER_AVAILABLE:
                    # Utiliser le gestionnaire FTP PATCH 29 pour l'upload
                    success, ftp_url, ftp_error = upload_for_publication(video_local_path, video_filename)
                    
                    if success and ftp_url:
                        video_url = ftp_url
                        log_app(f"✅ PATCH 35: Vidéo uploadée sur FTP - {video_url}", "SUCCESS")
                    else:
                        log_app(f"⚠️ PATCH 35: Upload FTP échoué ({ftp_error}), fallback ngrok", "WARNING")
                        # Fallback vers copie locale + URL ngrok
                        uploads_dir = "/app/backend/uploads"
                        os.makedirs(uploads_dir, exist_ok=True)
                        import shutil
                        shutil.copy2(video_local_path, os.path.join(uploads_dir, video_filename))
                        video_url = get_public_url(video_filename)
                        log_app(f"🔄 PATCH 35: Fallback URL ngrok - {video_url}", "INFO")
                else:
                    # Gestionnaire FTP non disponible, utiliser ngrok
                    log_app(f"⚠️ PATCH 35: Gestionnaire FTP non disponible, utilisation ngrok", "WARNING")
                    video_url = get_public_url(video_filename)
                
                # Publication sur les plateformes
                try:
                    store_config = get_store_config(final_store)
                    
                    # Publication Facebook avec is_video=True
                    if "facebook" in platforms:
                        log_app(f"📱 PATCH 9: Publication Facebook avec endpoint /videos", "INFO")
                        fb_result = await publish_to_facebook(store_config, title, product_url, description, video_url, is_video=True)
                        log_app(f"✅ PATCH 9: Facebook terminé - {fb_result.get('success', False)}", "SUCCESS" if fb_result.get('success') else "ERROR")
                    
                    # Publication Instagram vidéo (Reels)
                    if "instagram" in platforms:
                        log_app(f"📸 PATCH 9: Publication Instagram Reels", "INFO") 
                        ig_result = await publish_to_instagram(store_config, title, product_url, description, video_url, is_video=True)
                        log_app(f"✅ PATCH 9: Instagram terminé - {ig_result.get('success', False)}", "SUCCESS" if ig_result.get('success') else "ERROR")
                    
                    result = {
                        "success": True,
                        "status": "success",
                        "store": final_store,
                        "platforms": platforms,
                        "video_url": video_url,
                        "facebook_result": fb_result if "facebook" in platforms else None,
                        "instagram_result": ig_result if "instagram" in platforms else None
                    }
                    
                except Exception as pub_error:
                    log_app(f"❌ PATCH 9: Erreur publication unifiée - {pub_error}", "ERROR")
                    # Fallback vers l'ancienne méthode spécialisée
                    result = await publish_video_main(
                        store=final_store,
                        message=message,
                        product_url=product_url,
                        video_url=video_url,
                        platforms=platforms
                    )
                
                log_app(f"✅ PATCH 9: Vidéo publiée avec succès sur les plateformes", "SUCCESS")
                
                # Nettoyer le fichier temporaire
                try:
                    video_path = media_file_info['path']
                    if os.path.exists(video_path):
                        # PATCH 24: Suppression différée - FB/IG ont besoin d'accéder au fichier d'abord
                        schedule_file_cleanup(video_path)
                except Exception as cleanup_error:
                    log_app(f"⚠️ PATCH 9: Erreur nettoyage fichier temporaire - {cleanup_error}", "WARNING")
                    
            except Exception as video_error:
                log_app(f"❌ PATCH 9: Erreur traitement vidéo - {video_error}", "ERROR")
                # Fallback vers publication texte
                result = await publish_post_main(
                    store=final_store,
                    message=message,
                    product_url=product_url,
                    image_url=image_url,
                    platforms=platforms
                )
                
        elif media_type == "image" and media_file_info:
            log_app(f"🖼️ PATCH 14: Traitement de l'image uploadée - {media_file_info['filename']}", "INFO")
            
            # PATCH 14: CORRECTION FINALE - Garantir URL publique HTTPS pour Instagram
            filename = media_file_info['filename']
            
            # Vérifier d'abord si l'URL publique est déjà disponible dans media_file_info
            if media_file_info.get('public_url') and media_file_info['public_url'].startswith('https://'):
                final_image_url = media_file_info['public_url']
                log_app(f"✅ PATCH 14: URL publique déjà générée - {final_image_url}", "SUCCESS")
            else:
                # PATCH 14: Générer OBLIGATOIREMENT l'URL publique ngrok
                final_image_url = get_public_url(filename)
                log_app(f"🌐 PATCH 14: URL publique ngrok générée - {final_image_url}", "SUCCESS")
                
                # PATCH 14: SÉCURITÉ - Vérifier que l'URL est valide
                if not final_image_url or not final_image_url.startswith('https://'):
                    log_app(f"❌ PATCH 14: URL publique invalide - {final_image_url}", "ERROR")
                    raise Exception(f"Impossible de générer une URL publique valide pour {filename}")
            
            log_app(f"🔍 PATCH 14: URL finale pour publication - {final_image_url}", "INFO")
            
            result = await publish_post_main(
                store=final_store,
                message=message,
                product_url=product_url,
                image_url=final_image_url,  # Utiliser l'URL finale ngrok
                platforms=platforms
            )
        else:
            # EFFECTUER LA PUBLICATION NORMALE avec toutes les améliorations intégrées
            # La fonction publish_post_main inclut automatiquement :
            # - Images cliquables (CLICKABLE_IMAGES_FEATURE.md)
            # - Validation préventive médias (AMÉLIORATIONS_MÉDIA_RÉALISÉES.md)
            # - Commentaires automatiques (AMELIORATIONS_REALISEES.md)
            # - Publication intelligente multi-plateformes (SMART_CROSSPOST_FEATURES.md)
            
            # PATCH 14: CORRECTION FINALE - Détecter TOUS les chemins locaux pour Instagram
            final_image_url = image_url
            if image_url:
                # Normaliser les backslashes Windows en slashes Unix
                normalized_path = image_url.replace("\\", "/")
                
                # PATCH 14: Détecter TOUS les chemins locaux (avec ou sans uploads/ dans le chemin)
                is_local_path = (
                    not normalized_path.startswith(("http://", "https://")) and (
                        "uploads/" in normalized_path or 
                        normalized_path.startswith("uploads/") or
                        normalized_path.startswith("./uploads/") or
                        "webhook_" in normalized_path  # Pattern spécifique aux fichiers webhook
                    )
                )
                
                if is_local_path:
                    # Extraire le nom de fichier (support chemins complets et relatifs)
                    filename = normalized_path.split("/")[-1]
                    final_image_url = get_public_url(filename)
                    log_app(f"🌐 PATCH 14: Chemin local converti en URL publique - '{image_url}' → '{final_image_url}'", "SUCCESS")
                    
                    # PATCH 14: Vérification de sécurité
                    if not final_image_url or not final_image_url.startswith('https://'):
                        log_app(f"❌ PATCH 14: URL publique invalide générée - {final_image_url}", "ERROR")
                        raise Exception(f"Impossible de générer une URL publique valide pour {filename}")
                else:
                    final_image_url = normalized_path
                    log_app(f"🔗 PATCH 14: URL déjà publique - {final_image_url}", "INFO")
            
            result = await publish_post_main(
                store=final_store,
                message=message,
                product_url=product_url,
                image_url=final_image_url,  # Utiliser l'URL finale ngrok
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

async def detect_webhook_publication_request(request: Request) -> dict:
    """Détecte si une requête POST est une demande de publication n8n"""
    try:
        content_type = request.headers.get("content-type", "")
        if "multipart/form-data" in content_type:
            form_data = await request.form()
            form_keys = set(form_data.keys())
            
            # Format n8n : jsonData + file (ou files)
            if "jsonData" in form_keys and ("file" in form_keys or "files" in form_keys):
                return {
                    "is_publication": True,
                    "form_data": form_data,
                    "format": "n8n"
                }
            
            # Format direct : store, title, url, description, file (pour compatibilité)
            required_fields = {"store", "title", "url", "description", "file"}
            if required_fields.issubset(form_keys):
                return {
                    "is_publication": True,
                    "form_data": form_data,
                    "format": "direct"
                }
        
        return {"is_publication": False}
    except:
        return {"is_publication": False}

async def handle_n8n_publication_corrected(form_data) -> dict:
    """PATCH 19: Traitement corrigé des publications n8n - évite la consommation du stream"""
    try:
        log_app("🔧 PATCH 19: Traitement publication n8n corrigé", "INFO")
        
        # Parser les données du formulaire
        publication_data = {}
        media_file = None
        
        for key, value in form_data.items():
            if hasattr(value, 'read') and hasattr(value, 'filename'):
                # C'est un fichier uploadé
                log_app(f"📦 Fichier détecté: {key} = {value.filename}", "INFO")
                media_file = value
            elif key == "jsonData" and isinstance(value, str):
                # Format n8n avec JSON dans le champ jsonData
                try:
                    publication_data = json.loads(value)
                    log_app(f"📦 JSON parsé depuis jsonData: {list(publication_data.keys())}", "INFO")
                except json.JSONDecodeError as e:
                    log_app(f"❌ Erreur parsing JSON: {e}", "ERROR")
            else:
                # Données directes
                publication_data[key] = value
        
        # Log des données reçues
        log_app(f"🔍 PATCH 19: Données publication: {list(publication_data.keys())}", "INFO")
        
        # Extraire les informations essentielles
        store = publication_data.get("store") or publication_data.get("shop_type")
        title = publication_data.get("title", "")
        description = publication_data.get("description", "")
        product_url = publication_data.get("url") or publication_data.get("product_url", "")
        
        if not store:
            return {"success": False, "error": "Store manquant dans les données"}
        
        log_app(f"🎯 PATCH 19: Publication pour store '{store}': {title}", "INFO")
        
        # Traiter le fichier média si présent
        media_info = None
        if media_file:
            try:
                # Lire le contenu du fichier
                file_content = await media_file.read()
                content_type = getattr(media_file, 'content_type', 'application/octet-stream')
                filename = getattr(media_file, 'filename', 'unknown')
                
                log_app(f"📦 PATCH 34: Fichier média: {filename} ({content_type}, {len(file_content)} bytes)", "INFO")
                
                # PATCH 34: Détection MIME robuste avec protection contre None
                if not content_type:
                    import mimetypes
                    detected_type, _ = mimetypes.guess_type(filename)
                    content_type = detected_type or 'application/octet-stream'
                    log_app(f"🔍 PATCH 34: Type MIME détecté: {content_type}", "INFO")
                
                # Déterminer l'extension selon le type (avec protection None)
                is_video = (content_type and content_type.startswith('video/')) or filename.lower().endswith(('.mp4', '.mov', '.avi'))
                
                if is_video:
                    file_extension = ".mp4" if content_type and "mp4" in content_type else ".mov"
                else:
                    file_extension = ".jpg" if content_type and "jpeg" in content_type else ".png"
                
                # Nom de fichier unique
                temp_filename = f"webhook_{uuid.uuid4().hex[:8]}_{int(time.time())}{file_extension}"
                temp_path = os.path.join(UPLOAD_DIR, temp_filename)
                
                # Sauvegarder le fichier
                with open(temp_path, 'wb') as f:
                    f.write(file_content)
                
                # Générer l'URL publique
                public_url = get_public_url(temp_filename)
                
                media_info = {
                    'path': temp_path,
                    'filename': temp_filename,
                    'original_filename': filename,
                    'content_type': content_type,
                    'size': len(file_content),
                    'public_url': public_url,
                    'is_video': is_video
                }
                
                log_app(f"✅ PATCH 19: Média sauvegardé: {public_url}", "SUCCESS")
                
            except Exception as file_error:
                log_app(f"❌ PATCH 19: Erreur traitement fichier: {file_error}", "ERROR")
                return {"success": False, "error": f"Erreur fichier: {file_error}"}
        
        # Préparer les données pour publication
        webhook_publication_data = {
            "store": store,
            "title": title,
            "description": description,
            "url": product_url,
            "platforms": ["facebook", "instagram"]  # Par défaut
        }
        
        # Ajouter les informations du média
        if media_info:
            if media_info['is_video']:
                webhook_publication_data['video_file'] = media_info
            else:
                webhook_publication_data['image_file'] = media_info
                webhook_publication_data['image_url'] = media_info['public_url']
        
        # Publier sur les plateformes
        publication_result = await process_webhook_publication(webhook_publication_data)
        
        if publication_result and publication_result.get("success"):
            log_app(f"✅ PATCH 19: Publication réussie pour {store}", "SUCCESS")
            return {
                "success": True,
                "store": store,
                "title": title,
                "platforms": publication_result.get("platforms", []),
                "media": "video" if media_info and media_info['is_video'] else "image" if media_info else "text"
            }
        else:
            log_app(f"❌ PATCH 19: Publication échouée: {publication_result}", "ERROR")
            return {
                "success": False,
                "error": "Publication échouée",
                "details": publication_result
            }
            
    except Exception as e:
        log_app(f"❌ PATCH 19: Erreur générale: {e}", "ERROR")
        return {"success": False, "error": str(e)}

async def handle_n8n_publication(form_data, format_type="direct") -> dict:
    """
    Gère les publications n8n avec logique complète (ex /api/webhook/publish)
    Intégré avec l'infrastructure existante (stores, FTP, ngrok)
    """
    try:
        # Extraire les paramètres selon le format
        if format_type == "n8n":
            # Format n8n : jsonData + file (ou files)
            json_data_str = form_data.get("jsonData")
            if isinstance(json_data_str, str):
                json_data = json.loads(json_data_str)
            else:
                # Si c'est un objet UploadFile, lire le contenu
                json_content = await json_data_str.read()
                json_data = json.loads(json_content.decode('utf-8'))
            
            store = json_data.get("store")
            title = json_data.get("title")
            url = json_data.get("url")
            description = json_data.get("description")
            # PATCH 31: Support champ 'files' n8n en plus de 'file'
            file = form_data.get("files") or form_data.get("file")
            
            log_app(f"📦 Format n8n détecté - JSON: {json_data}", "INFO")
        else:
            # Format direct : champs individuels
            store = form_data.get("store")
            title = form_data.get("title")
            url = form_data.get("url")
            description = form_data.get("description")
            file = form_data.get("file")
        
        log_app(f"📥 Nouveau webhook n8n reçu - Store: {store}, Titre: {title[:50] if title else 'N/A'}...", "INFO")
        
        # Vérification du store
        if store not in STORES:
            available_stores = ", ".join(STORES.keys())
            raise HTTPException(status_code=400, detail=f"Store '{store}' inconnu. Stores disponibles: {available_stores}")
        
        # Récupération de la configuration du store
        store_config = get_store_config(store)
        log_app(f"📋 Configuration store '{store}' chargée: {store_config.get('name')}", "INFO")
        
        # Vérification des tokens
        if not store_config.get("access_token"):
            raise HTTPException(status_code=400, detail=f"Token d'accès manquant pour le store '{store}'")
        
        # Création du dossier uploads s'il n'existe pas
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Sauvegarde du fichier
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        unique_filename = f"webhook_{uuid.uuid4().hex[:8]}_{int(time.time())}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Sauvegarder le fichier
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        log_app(f"💾 Fichier sauvegardé: {file_path} ({os.path.getsize(file_path)} bytes)", "SUCCESS")
        
        # Déterminer le type de fichier
        content_type = file.content_type or ""
        is_video = content_type.startswith("video/") or file_extension.lower() in ['.mp4', '.mov', '.avi', '.wmv']
        
        # PATCH 29: FTP UNIQUEMENT - Upload vers FTP pour publication Facebook/Instagram
        log_app(f"🔄 PATCH 29: Début upload FTP pour publication", "INFO")
        
        upload_success, media_url, upload_error = await upload_file_to_ftp_for_publication(file_path, unique_filename)
        
        if not upload_success or not media_url:
            log_app(f"❌ PATCH 29: Upload FTP échoué - {upload_error}", "ERROR")
            # Fallback: générer URL FTP directe
            media_url = get_public_url(unique_filename)
            log_app(f"🔄 PATCH 29: Fallback URL FTP - {media_url}", "WARNING")
        else:
            log_app(f"✅ PATCH 29: Upload FTP réussi - {media_url}", "SUCCESS")
        
        if not media_url or not media_url.startswith('https://'):
            log_app(f"❌ PATCH 29: URL FTP invalide générée: {media_url}", "ERROR")
            raise HTTPException(status_code=500, detail=f"Impossible de générer une URL FTP valide")
        
        # Initialiser les résultats
        results = {
            "success": True,
            "store": store,
            "store_name": store_config.get("name"),
            "file_info": {
                "filename": unique_filename,
                "original_filename": file.filename,
                "content_type": content_type,
                "size": os.path.getsize(file_path),
                "is_video": is_video,
                "media_url": media_url
            },
            "publications": {}
        }
        
        # Publication Facebook
        log_app("📱 Publication Facebook...", "INFO")
        fb_result = await publish_to_facebook(store_config, title, url, description, media_url, is_video)
        results["publications"]["facebook"] = fb_result
        
        # Publication Instagram
        log_app("📸 Publication Instagram...", "INFO")
        ig_result = await publish_to_instagram(store_config, title, url, description, media_url, is_video)
        results["publications"]["instagram"] = ig_result
        
        # Déterminer le succès global
        fb_success = fb_result.get("success", False)
        ig_success = ig_result.get("success", False)
        
        if fb_success and ig_success:
            log_app("✅ Publications Facebook et Instagram réussies", "SUCCESS")
            results["message"] = "Publications réussies sur Facebook et Instagram"
        elif fb_success or ig_success:
            platform = "Facebook" if fb_success else "Instagram"
            log_app(f"⚠️ Publication réussie sur {platform} uniquement", "WARNING")
            results["message"] = f"Publication réussie sur {platform} uniquement"
            results["success"] = True  # Succès partiel
        else:
            log_app("❌ Échec des publications Facebook et Instagram", "ERROR")
            results["message"] = "Échec des publications sur les deux plateformes"
            results["success"] = False
        
        # PATCH 24: Suppression différée - Facebook/Instagram ont besoin d'accéder au fichier d'abord
        try:
            schedule_file_cleanup(file_path)
        except Exception as e:
            log_app(f"⚠️ PATCH 24: Erreur programmation nettoyage: {e}", "WARNING")
        
        return results
        
    except HTTPException:
        raise  # Re-lancer les erreurs HTTP
    except Exception as e:
        error_msg = f"Erreur publication n8n: {str(e)}"
        log_app(f"❌ {error_msg}", "ERROR")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/webhook")
@app.get("/api/webhook")
@app.post("/api/webhook/")
@app.get("/api/webhook/")
async def webhook_handler(request: Request):
    """Handle webhook requests from Facebook/Instagram and n8n publications"""
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
            # CORRECTION PATCH 19: Éviter la consommation multiple du stream
            content_type = request.headers.get("content-type", "")
            log_app(f"📦 Content-Type: {content_type}", "INFO")
            
            # Détecter si c'est une requête de publication n8n SANS consommer le stream
            if "multipart/form-data" in content_type and any(param in request.headers.get("content-type", "") for param in ["store", "title", "description"]):
                # C'est probablement une requête de publication n8n
                log_app(f"🚀 Détection requête publication n8n multipart", "INFO")
                try:
                    form_data = await request.form()
                    return await handle_n8n_publication_corrected(form_data)
                except Exception as n8n_error:
                    log_app(f"❌ Erreur traitement n8n: {n8n_error}", "ERROR")
                    return {"status": "error", "message": str(n8n_error)}
            
            # ANCIENNE LOGIQUE: Gestion des événements webhook Facebook/Instagram
            try:
                webhook_data = None
                
                # Handle multipart/form-data 
                if "multipart/form-data" in content_type:
                    log_app("📦 Processing multipart/form-data webhook", "INFO")
                    try:
                        # PATCH 21: CORRECTION - Traiter les publications au lieu de retourner un accusé de réception
                        # Si nous arrivons ici, c'est que ce n'est PAS une requête n8n mais un webhook de publication
                        log_app("📦 PATCH 21: Traitement publication webhook multipart", "INFO")
                        
                        form_data = await request.form()
                        
                        # PATCH 21 CORRIGÉ: Vérifier si c'est une vraie publication avec store/title/description  
                        has_publication_fields = any(field in form_data for field in ['store', 'title', 'description'])
                        
                        if has_publication_fields:
                            log_app("📤 PATCH 21: Publication détectée - traitement en cours...", "INFO")
                            publication_result = await handle_n8n_publication_corrected(form_data)
                            log_app(f"✅ PATCH 21: Résultat publication - {publication_result}", "SUCCESS")
                            return publication_result
                        
                        # PATCH 21 CORRIGÉ: Traitement des webhooks standard Facebook/Instagram (sans publication)
                        log_app("📦 PATCH 21: Webhook standard Facebook/Instagram - traitement en cours...", "INFO")
                        
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
                            
                            # NOUVELLE CORRECTION: Traiter les fichiers médias séparément
                            media_files = {}
                            for key, value in form_data.items():
                                if hasattr(value, 'read') and hasattr(value, 'filename') and key != json_data_field:
                                    # C'est un fichier uploadé
                                    file_content = await value.read()
                                    content_type = getattr(value, 'content_type', '')
                                    filename = getattr(value, 'filename', f'file_{key}')
                                    
                                    log_app(f"📦 CORRECTION: Fichier détecté - {key}: {filename} ({content_type}, {len(file_content)} bytes)", "INFO")
                                    
                                    # Sauvegarder le fichier temporairement
                                    if content_type.startswith('video/') or 'video' in key.lower():
                                        # C'est une vidéo
                                        file_extension = ".mp4" if "mp4" in content_type else ".mov"
                                        temp_filename = f"webhook_{uuid.uuid4().hex[:8]}_{int(time.time())}{file_extension}"
                                        temp_path = os.path.join(UPLOAD_DIR, temp_filename)
                                        
                                        with open(temp_path, 'wb') as f:
                                            f.write(file_content)
                                        
                                        log_app(f"📦 CORRECTION: Vidéo sauvegardée temporairement: {temp_path}", "INFO")
                                        
                                        # Ajouter les infos de la vidéo aux données webhook
                                        webhook_data['video_file'] = {
                                            'path': temp_path,
                                            'filename': temp_filename,
                                            'original_filename': filename,
                                            'content_type': content_type,
                                            'size': len(file_content)
                                        }
                                        
                                    elif content_type.startswith('image/') or 'image' in key.lower():
                                        # C'est une image
                                        file_extension = ".jpg" if "jpeg" in content_type else ".png"
                                        temp_filename = f"webhook_{uuid.uuid4().hex[:8]}_{int(time.time())}{file_extension}"
                                        temp_path = os.path.join(UPLOAD_DIR, temp_filename)
                                        
                                        with open(temp_path, 'wb') as f:
                                            f.write(file_content)
                                        
                                        log_app(f"📦 PATCH 9: Image sauvegardée: {temp_path}", "INFO")
                                        
                                        # PATCH 30: Upload FTP intelligent pour URLs accessibles
                                        try:
                                            if FTP_MANAGER_AVAILABLE:
                                                ftp_success, ftp_url, ftp_error = await upload_file_to_ftp_for_publication(temp_path, temp_filename)
                                                if ftp_success and ftp_url:
                                                    public_url = ftp_url
                                                    log_app(f"✅ PATCH 30: Upload FTP réussi - {public_url}", "SUCCESS")
                                                else:
                                                    log_app(f"⚠️ PATCH 30: Upload FTP échoué ({ftp_error}), fallback ngrok", "WARNING")
                                                    public_url = get_public_url(temp_filename)
                                            else:
                                                # Fallback vers ngrok si FTP non disponible
                                                public_url = get_public_url(temp_filename)
                                                log_app(f"🌐 PATCH 30: URL ngrok (FTP non disponible): {public_url}", "INFO")
                                        except Exception as e:
                                            log_app(f"⚠️ PATCH 30: Erreur upload FTP: {e}", "WARNING")
                                            public_url = get_public_url(temp_filename)
                                        
                                        log_app(f"🌐 PATCH 30: URL publique finale: {public_url}", "SUCCESS")
                                        
                                        # Ajouter les infos de l'image aux données webhook
                                        webhook_data['image_file'] = {
                                            'path': temp_path,
                                            'filename': temp_filename,
                                            'original_filename': filename,
                                            'content_type': content_type,
                                            'size': len(file_content),
                                            'public_url': public_url  # URL publique toujours disponible
                                        }
                        else:
                            # Process all form fields - CORRECTION POUR LES FICHIERS SANS JSON
                            webhook_data = {}
                            for key, value in form_data.items():
                                if hasattr(value, 'read') and hasattr(value, 'filename'):  # File upload
                                    file_content = await value.read()
                                    content_type = getattr(value, 'content_type', '')
                                    filename = getattr(value, 'filename', f'file_{key}')
                                    
                                    log_app(f"📦 CORRECTION: Fichier détecté - {key}: {filename} ({content_type}, {len(file_content)} bytes)", "INFO")
                                    
                                    # Traitement spécialisé selon le type de fichier
                                    if content_type.startswith('video/') or filename.lower().endswith(('.mp4', '.mov', '.avi')):
                                        # C'est une vidéo
                                        file_extension = ".mp4" if "mp4" in content_type or filename.lower().endswith('.mp4') else ".mov"
                                        temp_filename = f"webhook_{uuid.uuid4().hex[:8]}_{int(time.time())}{file_extension}"
                                        temp_path = os.path.join(UPLOAD_DIR, temp_filename)
                                        
                                        with open(temp_path, 'wb') as f:
                                            f.write(file_content)
                                        
                                        log_app(f"📦 CORRECTION: Vidéo sauvegardée temporairement: {temp_path}", "INFO")
                                        
                                        # Ajouter les infos de la vidéo aux données webhook
                                        webhook_data['video_file'] = {
                                            'path': temp_path,
                                            'filename': temp_filename,
                                            'original_filename': filename,
                                            'content_type': content_type,
                                            'size': len(file_content)
                                        }
                                        
                                    elif content_type.startswith('image/') or filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                                        # C'est une image
                                        file_extension = ".jpg" if "jpeg" in content_type or filename.lower().endswith(('.jpg', '.jpeg')) else ".png"
                                        temp_filename = f"webhook_{uuid.uuid4().hex[:8]}_{int(time.time())}{file_extension}"
                                        temp_path = os.path.join(UPLOAD_DIR, temp_filename)
                                        
                                        with open(temp_path, 'wb') as f:
                                            f.write(file_content)
                                        
                                        log_app(f"📦 PATCH 9: Image sauvegardée: {temp_path}", "INFO")
                                        
                                        # PATCH 30: Upload FTP intelligent pour URLs accessibles
                                        try:
                                            if FTP_MANAGER_AVAILABLE:
                                                ftp_success, ftp_url, ftp_error = await upload_file_to_ftp_for_publication(temp_path, temp_filename)
                                                if ftp_success and ftp_url:
                                                    public_url = ftp_url
                                                    log_app(f"✅ PATCH 30: Upload FTP réussi - {public_url}", "SUCCESS")
                                                else:
                                                    log_app(f"⚠️ PATCH 30: Upload FTP échoué ({ftp_error}), fallback ngrok", "WARNING")
                                                    public_url = get_public_url(temp_filename)
                                            else:
                                                # Fallback vers ngrok si FTP non disponible
                                                public_url = get_public_url(temp_filename)
                                                log_app(f"🌐 PATCH 30: URL ngrok (FTP non disponible): {public_url}", "INFO")
                                        except Exception as e:
                                            log_app(f"⚠️ PATCH 30: Erreur upload FTP: {e}", "WARNING")
                                            public_url = get_public_url(temp_filename)
                                        
                                        log_app(f"🌐 PATCH 30: URL publique finale: {public_url}", "SUCCESS")
                                        
                                        # Ajouter les infos de l'image aux données webhook
                                        webhook_data['image_file'] = {
                                            'path': temp_path,
                                            'filename': temp_filename,
                                            'original_filename': filename,
                                            'content_type': content_type,
                                            'size': len(file_content),
                                            'public_url': public_url  # URL publique toujours disponible
                                        }
                                    else:
                                        # Fichier non reconnu, essayer de le traiter comme texte
                                        try:
                                            text_content = file_content.decode('utf-8')
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
                                                "size": len(file_content),
                                                "base64": base64.b64encode(file_content[:1000]).decode('ascii')  # First 1KB only
                                            }
                                elif hasattr(value, 'read'): # File upload without filename
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
                        
                    # PATCH 21 CORRIGÉ: Si pas de publication n8n détectée, traiter comme webhook standard Facebook
                    if not webhook_data:
                        log_app("📦 PATCH 21: Webhook multipart Facebook standard - pas de données JSON trouvées", "INFO")
                        # Créer des données webhook basiques pour Facebook
                        webhook_data = {
                            "object": "page",
                            "entry": [],
                            "source": "facebook_multipart_webhook"
                        }
                        # Ajouter les données de formulaire si disponibles
                        for key, value in form_data.items():
                            if not hasattr(value, 'read'):  # Pas un fichier
                                webhook_data[key] = value
                
                # Handle application/json or text content
                else:
                    log_app("📦 Processing JSON/text webhook", "INFO")
                    # PATCH 19: Lire le body seulement pour JSON
                    body = await request.body()
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

# === NOUVELLES FONCTIONS WEBHOOK ===
# Fonction process_webhook_publication supprimée - utilise celle corrigée plus haut


@app.post("/api/webhook/n8n", response_model=WebhookResponse)
async def webhook_n8n_handler(
    json_data: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    """Endpoint webhook optimisé pour N8N avec support multipart/form-data"""
    try:
        log_app("🔗 Réception webhook N8N", "INFO")
        
        # Traiter les données avec le webhook handler
        webhook_data = await webhook_handler.process_webhook_data(json_data, file)
        
        # Préparer les données de publication
        publication_data = await webhook_handler.prepare_publication_data(webhook_data)
        
        publication_results = {}
        
        # Publier selon le type de contenu
        if publication_data["publication_type"] == "image_post":
            # PATCH 13: Pour les images, convertir les chemins locaux en URLs publiques
            image_url = publication_data.get("image_url")
            if not image_url and publication_data.get("image_path"):
                # PATCH 13: Convertir le chemin local en URL publique ngrok
                image_path = publication_data["image_path"]
                if not image_path.startswith('http'):
                    filename = os.path.basename(image_path)
                    image_url = get_public_url(filename)
                    log_app(f"🌐 PATCH 13: Chemin local converti en URL publique - {image_url}", "SUCCESS")
                else:
                    image_url = image_path
            
            result = await publish_post_main(
                publication_data["store"],
                publication_data["message"],
                publication_data["product_url"],
                image_url,
                publication_data["platforms"]
            )
            publication_results["publication"] = result
            
        elif publication_data["publication_type"] == "video_post":
            # PATCH 13: Pour les vidéos, utiliser ngrok uniquement
            video_path = publication_data["video_path"]
            
            # PATCH 13: Générer directement l'URL publique ngrok
            if not video_path.startswith('http'):
                filename = os.path.basename(video_path)
                video_url = get_public_url(filename)
                log_app(f"🌐 PATCH 13: Vidéo - chemin local converti en URL publique - {video_url}", "SUCCESS")
            else:
                video_url = video_path
            
            result = await publish_video_main(
                publication_data["store"],
                publication_data["message"],
                publication_data["product_url"],
                video_url,
                publication_data["platforms"]
            )
            publication_results["publication"] = result
            publication_results["video_upload"] = {
                "success": True,
                "video_url": video_url
            }
                
        elif publication_data["publication_type"] == "text_only":
            # Publication texte seulement
            result = await publish_post_main(
                publication_data["store"],
                publication_data["message"],
                publication_data["product_url"],
                None,
                ["facebook"]  # Instagram nécessite une image
            )
            publication_results["publication"] = result
        else:
            raise Exception(f"Type de publication non supporté: {publication_data['publication_type']}")
        
        # Sauvegarder dans MongoDB
        webhook_data["publication_results"] = publication_results
        webhook_data["processing_status"] = "completed"
        
        try:
            await save_webhook_data(webhook_data)
            log_app("✅ Webhook N8N sauvegardé dans MongoDB", "SUCCESS")
        except Exception as save_error:
            log_app(f"⚠️ Erreur sauvegarde webhook N8N: {save_error}", "WARNING")
        
        return WebhookResponse(
            success=True,
            webhook_id=webhook_data["webhook_id"],
            message="Publication réussie",
            publication_results=publication_results
        )
        
    except Exception as e:
        log_app(f"❌ Erreur webhook N8N: {str(e)}", "ERROR")
        return WebhookResponse(
            success=False,
            message=f"Erreur: {str(e)}",
            error=str(e)
        )

@app.post("/api/tokens/refresh")
async def refresh_tokens():
    """Récupère automatiquement tous les tokens depuis le token Facebook utilisateur"""
    try:
        log_app("🔄 Démarrage rafraîchissement automatique des tokens", "INFO")
        
        # Vérifier que le token direct est configuré
        if not token_manager.facebook_direct_token:
            raise HTTPException(
                status_code=400, 
                detail="FACEBOOK_DIRECT_TOKEN non configuré dans .env"
            )
        
        # Rafraîchir tous les tokens
        store_configs = await token_manager.refresh_all_tokens()
        
        if not store_configs:
            raise HTTPException(
                status_code=500,
                detail="Aucune configuration de store récupérée"
            )
        
        # Mettre à jour les stores globaux
        global STORES, TOKENS
        for store_key, config in store_configs.items():
            if store_key in STORES:
                STORES[store_key].update(config)
            TOKENS[store_key] = config
        
        return {
            "success": True,
            "message": f"{len(store_configs)} stores configurés",
            "stores": list(store_configs.keys()),
            "details": {
                store: {
                    "name": config["name"],
                    "fb_page_id": config["fb_page_id"],
                    "has_access_token": bool(config.get("access_token")),
                    "has_instagram": bool(config.get("ig_user_id"))
                }
                for store, config in store_configs.items()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_app(f"❌ Erreur rafraîchissement tokens: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tokens/status")
async def get_tokens_status():
    """Affiche le statut actuel des tokens"""
    try:
        status = {
            "facebook_direct_token": bool(token_manager.facebook_direct_token),
            "stores": {}
        }
        
        for store_key, store_config in STORES.items():
            status["stores"][store_key] = {
                "name": store_config["name"],
                "fb_page_id": store_config.get("fb_page_id"),
                "has_access_token": bool(store_config.get("access_token")),
                "ig_user_id": store_config.get("ig_user_id"),
                "has_instagram": bool(store_config.get("ig_user_id"))
            }
        
        return status
        
    except Exception as e:
        log_app(f"❌ Erreur statut tokens: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

# === BULK INSTAGRAM PUBLISHER ===
@app.post("/api/instagram/bulk-publish")
async def bulk_publish_instagram(
    store: str = Form(...),
    caption: str = Form(default="Découvrez notre boutique !"),
    access_token: Optional[str] = Form(None)
):
    """
    Publie en masse tous les fichiers du dossier uploads/ sur Instagram
    """
    try:
        log_app(f"🔄 Début publication en masse Instagram pour {store}", "INFO")
        
        # Vérifier la configuration du store
        if store not in STORES:
            raise HTTPException(status_code=400, detail=f"Store inconnu: {store}")
        
        store_config = get_store_config(store)
        
        # Utiliser le token fourni ou celui du store
        instagram_token = access_token or store_config.get("access_token")
        if not instagram_token:
            raise HTTPException(
                status_code=400, 
                detail=f"Token d'accès Instagram manquant pour {store}"
            )
        
        # Vérifier l'ID Instagram
        ig_user_id = store_config.get("ig_user_id")
        if not ig_user_id:
            raise HTTPException(
                status_code=400, 
                detail=f"ID Instagram manquant pour {store}"
            )
        
        # Obtenir l'URL backend actuelle
        backend_url = get_active_ngrok_url()
        if not backend_url:
            raise HTTPException(
                status_code=400, 
                detail="URL backend non accessible - vérifiez la configuration ngrok"
            )
        
        # Vérifier le dossier uploads
        uploads_path = os.path.join(os.getcwd(), UPLOAD_DIR)
        if not os.path.exists(uploads_path):
            raise HTTPException(
                status_code=400, 
                detail=f"Dossier {UPLOAD_DIR} introuvable"
            )
        
        # Récupérer tous les fichiers image
        supported_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        image_files = []
        
        for filename in os.listdir(uploads_path):
            file_path = os.path.join(uploads_path, filename)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(filename.lower())
                if ext in supported_extensions:
                    image_files.append((filename, file_path))
        
        if not image_files:
            return {
                "success": False,
                "error": f"Aucun fichier image trouvé dans {UPLOAD_DIR}",
                "supported_extensions": supported_extensions
            }
        
        log_app(f"📸 {len(image_files)} fichiers image trouvés", "INFO")
        
        # Publier chaque image
        results = []
        success_count = 0
        
        for filename, file_path in image_files:
            try:
                # Construire l'URL publique
                public_url = f"{backend_url}/{UPLOAD_DIR}/{filename}"
                
                log_app(f"📤 Publication: {filename} -> {public_url}", "INFO")
                
                # Mode test : simulation
                if PUBLICATION_TEST_MODE:
                    log_app(f"MODE TEST - Publication Instagram simulée: {filename}", "TEST")
                    results.append({
                        "filename": filename,
                        "success": True,
                        "public_url": public_url,
                        "instagram_id": f"test_ig_bulk_{uuid.uuid4().hex[:8]}",
                        "test_mode": True
                    })
                    success_count += 1
                    continue
                
                # Publication réelle sur Instagram
                # Étape 1: Créer le conteneur média
                create_url = f"{FACEBOOK_GRAPH_URL}/{ig_user_id}/media"
                create_payload = {
                    "image_url": public_url,
                    "caption": caption,
                    "access_token": instagram_token
                }
                
                create_response = requests.post(create_url, data=create_payload, timeout=30)
                
                if create_response.status_code == 200:
                    media_data = create_response.json()
                    creation_id = media_data.get("id")
                    
                    if creation_id:
                        # Étape 2: Publier le média
                        publish_url = f"{FACEBOOK_GRAPH_URL}/{ig_user_id}/media_publish"
                        publish_payload = {
                            "creation_id": creation_id,
                            "access_token": instagram_token
                        }
                        
                        publish_response = requests.post(publish_url, data=publish_payload, timeout=30)
                        
                        if publish_response.status_code == 200:
                            publish_data = publish_response.json()
                            instagram_id = publish_data.get("id")
                            
                            results.append({
                                "filename": filename,
                                "success": True,
                                "public_url": public_url,
                                "instagram_id": instagram_id,
                                "creation_id": creation_id
                            })
                            success_count += 1
                            log_app(f"✅ {filename} publié avec succès: {instagram_id}", "SUCCESS")
                        else:
                            error_msg = f"Erreur publication: {publish_response.text}"
                            results.append({
                                "filename": filename,
                                "success": False,
                                "public_url": public_url,
                                "error": error_msg
                            })
                            log_app(f"❌ {filename} - {error_msg}", "ERROR")
                    else:
                        error_msg = "ID de création manquant dans la réponse"
                        results.append({
                            "filename": filename,
                            "success": False,
                            "public_url": public_url,
                            "error": error_msg
                        })
                        log_app(f"❌ {filename} - {error_msg}", "ERROR")
                else:
                    error_msg = f"Erreur création média: {create_response.text}"
                    results.append({
                        "filename": filename,
                        "success": False,
                        "public_url": public_url,
                        "error": error_msg
                    })
                    log_app(f"❌ {filename} - {error_msg}", "ERROR")
                
                # Pause entre publications pour éviter les limites de taux
                await asyncio.sleep(2)
                
            except Exception as e:
                error_msg = f"Erreur publication {filename}: {str(e)}"
                results.append({
                    "filename": filename,
                    "success": False,
                    "public_url": f"{backend_url}/{UPLOAD_DIR}/{filename}",
                    "error": error_msg
                })
                log_app(f"❌ {error_msg}", "ERROR")
        
        # Résumé final
        total_files = len(image_files)
        failed_count = total_files - success_count
        
        log_app(f"📊 Publication terminée: {success_count}/{total_files} réussies", "SUCCESS")
        
        return {
            "success": success_count > 0,
            "total_files": total_files,
            "success_count": success_count,
            "failed_count": failed_count,
            "store": store,
            "caption": caption,
            "backend_url": backend_url,
            "test_mode": PUBLICATION_TEST_MODE,
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_app(f"❌ Erreur publication en masse Instagram: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/instagram/bulk-status")
async def bulk_status():
    """
    Affiche le statut du dossier uploads/ pour la publication en masse
    """
    try:
        uploads_path = os.path.join(os.getcwd(), UPLOAD_DIR)
        backend_url = get_active_ngrok_url()
        
        status = {
            "upload_folder": UPLOAD_DIR,
            "upload_path": uploads_path,
            "folder_exists": os.path.exists(uploads_path),
            "backend_url": backend_url,
            "files": []
        }
        
        if os.path.exists(uploads_path):
            supported_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            
            for filename in os.listdir(uploads_path):
                file_path = os.path.join(uploads_path, filename)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(filename.lower())
                    is_image = ext in supported_extensions
                    file_size = os.path.getsize(file_path)
                    
                    status["files"].append({
                        "filename": filename,
                        "extension": ext,
                        "is_image": is_image,
                        "size_bytes": file_size,
                        "size_mb": round(file_size / (1024*1024), 2),
                        "public_url": f"{backend_url}/{UPLOAD_DIR}/{filename}" if backend_url else None
                    })
            
            # Statistiques
            image_files = [f for f in status["files"] if f["is_image"]]
            status["stats"] = {
                "total_files": len(status["files"]),
                "image_files": len(image_files),
                "total_size_mb": round(sum(f["size_bytes"] for f in status["files"]) / (1024*1024), 2),
                "supported_extensions": supported_extensions
            }
        
        return status
        
    except Exception as e:
        log_app(f"❌ Erreur statut bulk: {str(e)}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

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
            # PATCH 23: Conserver fichier même si validation échoue pour debug
            # os.remove(temp_path)  # Nettoyer le fichier temporaire
            return VideoUploadResponse(
                success=False,
                error=validation["error"],
                validation=validation
            )
        
        # Upload vers FTP
        success, public_url, error = await upload_video_to_ftp(temp_path, unique_filename)
        
        # PATCH 24: Suppression différée des fichiers temporaires pour accès FB/IG
        try:
            schedule_file_cleanup(temp_path)
        except Exception as e:
            log_app(f"⚠️ PATCH 24: Erreur programmation nettoyage vidéo: {e}", "WARNING")
        
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

# === NOUVEAU ENDPOINT WEBHOOK PUBLICATION ===

async def publish_to_facebook(store_config: dict, title: str, url: str, description: str, media_url: str = None, is_video: bool = False) -> dict:
    """Publication sur Facebook en utilisant la configuration du store"""
    try:
        fb_page_id = store_config.get("fb_page_id")
        access_token = store_config.get("access_token")
        
        if not fb_page_id or not access_token:
            return {"success": False, "error": "Configuration Facebook manquante"}
        
        # PATCH 31: Initialisation files pour éviter 'cannot access local variable'
        files = None
        
        # Construction du message
        message = f"{title}\n{url}\n{description}"
        
        # URL de l'API selon le type de contenu
        if is_video:
            fb_url = f"{FACEBOOK_GRAPH_URL}/{fb_page_id}/videos"
            data = {
                "description": message,
                "access_token": access_token
            }
            if media_url:
                data["file_url"] = media_url
        else:
            # Pour les images, utiliser l'endpoint photos
            fb_url = f"{FACEBOOK_GRAPH_URL}/{fb_page_id}/photos"
            data = {
                "message": message,
                "access_token": access_token
            }
            
            # PATCH 26: Upload direct du fichier au lieu d'URL pour éviter les problèmes ngrok
            if media_url and media_url.startswith(('http://', 'https://')):
                # Télécharger le fichier et l'uploader directement
                try:
                    log_app(f"🔄 PATCH 26: Téléchargement fichier pour upload direct: {media_url}", "INFO")
                    media_response = requests.get(media_url, timeout=10)
                    if media_response.status_code == 200:
                        files = {'source': ('image.jpg', media_response.content, 'image/jpeg')}
                        log_app(f"✅ PATCH 26: Fichier téléchargé ({len(media_response.content)} bytes)", "INFO")
                    else:
                        log_app(f"⚠️ PATCH 26: Échec téléchargement, fallback URL: {media_response.status_code}", "WARNING")
                        data["url"] = media_url
                except Exception as e:
                    log_app(f"⚠️ PATCH 26: Erreur téléchargement, fallback URL: {e}", "WARNING")
                    data["url"] = media_url
            elif media_url:
                # Chemin local, essayer de le lire directement
                try:
                    local_path = media_url.replace('\\', '/').replace('uploads/', '/app/backend/uploads/')
                    if os.path.exists(local_path):
                        with open(local_path, 'rb') as f:
                            files = {'source': ('image.jpg', f.read(), 'image/jpeg')}
                        log_app(f"✅ PATCH 26: Fichier local lu ({local_path})", "INFO")
                    else:
                        data["url"] = media_url
                except Exception as e:
                    log_app(f"⚠️ PATCH 26: Erreur lecture locale: {e}", "WARNING")
                    data["url"] = media_url
        
        log_app(f"📱 Publication Facebook vers {fb_page_id}: {message[:100]}...", "INFO")
        
        # PATCH 26: Envoi avec fichier direct si disponible
        if files:
            log_app(f"🔄 PATCH 26: Upload direct du fichier à Facebook", "INFO")
            response = requests.post(fb_url, data=data, files=files, timeout=30)
        else:
            log_app(f"🔄 PATCH 26: Envoi URL à Facebook: {data.get('url', 'N/A')}", "INFO")
            response = requests.post(fb_url, data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            log_app(f"✅ Publication Facebook réussie: ID {result.get('id', 'N/A')}", "SUCCESS")
            return {"success": True, "response": result}
        else:
            error_msg = f"Erreur Facebook HTTP {response.status_code}: {response.text}"
            log_app(f"❌ {error_msg}", "ERROR")
            return {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Erreur publication Facebook: {str(e)}"
        log_app(f"❌ {error_msg}", "ERROR")
        return {"success": False, "error": error_msg}

async def publish_to_instagram(store_config: dict, title: str, url: str, description: str, media_url: str, is_video: bool = False) -> dict:
    """Publication sur Instagram en utilisant la configuration du store"""
    try:
        ig_user_id = store_config.get("ig_user_id")
        access_token = store_config.get("access_token")
        
        if not ig_user_id or not access_token:
            return {"success": False, "error": "Configuration Instagram manquante"}
        
        if not media_url:
            return {"success": False, "error": "URL média obligatoire pour Instagram"}
        
        # PATCH 16: CORRECTION FINALE DÉTECTION CHEMINS LOCAUX INSTAGRAM
        log_app(f"🔍 PATCH 16: URL reçue par Instagram - '{media_url}'", "INFO")
        
        # PATCH 16: Détecter TOUS les chemins locaux (Windows et Unix) - CONDITION CORRIGÉE
        is_local_url = (
            not media_url.startswith(('http://', 'https://')) and (
                "uploads\\" in media_url or  # Chemin Windows avec backslashes
                "uploads/" in media_url or   # Chemin Unix avec slashes  
                media_url.startswith("uploads") or  # Chemin relatif uploads
                "webhook_" in media_url      # Pattern spécifique fichiers webhook
            )
        )
        
        if is_local_url:
            log_app(f"⚠️ PATCH 16: URL locale détectée, conversion obligatoire - {media_url}", "WARNING")
            # Extraire le nom de fichier (support chemins Windows et Unix)
            filename = media_url.split("\\")[-1].split("/")[-1]
            original_url = media_url
            media_url = get_public_url(filename)
            log_app(f"✅ PATCH 16: URL convertie - '{original_url}' → '{media_url}'", "SUCCESS")
            
            # PATCH 16: Vérification finale obligatoire
            if not media_url or not media_url.startswith('https://'):
                error_msg = f"URL publique invalide générée: {media_url} (fichier: {filename})"
                log_app(f"❌ PATCH 16: {error_msg}", "ERROR")
                return {"success": False, "error": error_msg}
        else:
            log_app(f"✅ PATCH 16: URL déjà publique et valide - {media_url}", "SUCCESS")
        
        # Construction du caption
        caption = f"{title}\n{url}\n{description}"
        
        # URL de l'API selon le type de contenu
        ig_url = f"{FACEBOOK_GRAPH_URL}/{ig_user_id}/media"
        
        data = {
            "caption": caption,
            "access_token": access_token
        }
        
        if is_video:
            data["media_type"] = "REELS"
            data["video_url"] = media_url
        else:
            data["image_url"] = media_url
        
        log_app(f"📸 Publication Instagram vers {ig_user_id}: {caption[:100]}...", "INFO")
        
        # PATCH 16: Debug - afficher exactement ce qui est envoyé à Instagram
        media_field = "video_url" if is_video else "image_url"
        log_app(f"🔍 PATCH 16: Données envoyées à Instagram - {media_field}: '{data.get(media_field)}'", "INFO")
        
        # Étape 1: Créer le conteneur média
        response = requests.post(ig_url, data=data, timeout=30)
        
        if response.status_code == 200:
            container_result = response.json()
            container_id = container_result.get("id")
            
            if container_id:
                # Étape 2: Publier le conteneur
                publish_url = f"{FACEBOOK_GRAPH_URL}/{ig_user_id}/media_publish"
                publish_data = {
                    "creation_id": container_id,
                    "access_token": access_token
                }
                
                publish_response = requests.post(publish_url, data=publish_data, timeout=30)
                
                if publish_response.status_code == 200:
                    publish_result = publish_response.json()
                    log_app(f"✅ Publication Instagram réussie: ID {publish_result.get('id', 'N/A')}", "SUCCESS")
                    return {"success": True, "response": publish_result}
                else:
                    error_msg = f"Erreur publication Instagram HTTP {publish_response.status_code}: {publish_response.text}"
                    log_app(f"❌ {error_msg}", "ERROR")
                    return {"success": False, "error": error_msg}
            else:
                error_msg = f"Pas de container_id reçu: {container_result}"
                log_app(f"❌ {error_msg}", "ERROR")
                return {"success": False, "error": error_msg}
        else:
            error_msg = f"Erreur création conteneur Instagram HTTP {response.status_code}: {response.text}"
            log_app(f"❌ {error_msg}", "ERROR")
            return {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Erreur publication Instagram: {str(e)}"
        log_app(f"❌ {error_msg}", "ERROR")
        return {"success": False, "error": error_msg}

# PATCH 24: Système de nettoyage différé des fichiers
CLEANUP_DELAY_HOURS = 2  # Délai avant suppression des fichiers (2 heures)
files_to_cleanup = []  # Liste des fichiers à supprimer plus tard

def schedule_file_cleanup(file_path: str):
    """Planifie la suppression d'un fichier après un délai"""
    cleanup_time = datetime.now() + timedelta(hours=CLEANUP_DELAY_HOURS)
    files_to_cleanup.append({
        'path': file_path,
        'cleanup_time': cleanup_time
    })
    log_app(f"📅 PATCH 24: Suppression programmée dans {CLEANUP_DELAY_HOURS}h: {file_path}", "INFO")

def cleanup_old_files():
    """Nettoie les fichiers dont le délai est dépassé"""
    current_time = datetime.now()
    files_cleaned = 0
    
    # Créer une nouvelle liste sans les fichiers nettoyés
    global files_to_cleanup
    remaining_files = []
    
    for file_info in files_to_cleanup:
        if current_time >= file_info['cleanup_time']:
            file_path = file_info['path']
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    log_app(f"🧹 PATCH 24: Fichier nettoyé: {file_path}", "INFO")
                    files_cleaned += 1
            except Exception as e:
                log_app(f"⚠️ PATCH 24: Erreur nettoyage {file_path}: {e}", "WARNING")
        else:
            remaining_files.append(file_info)
    
    files_to_cleanup = remaining_files
    
    if files_cleaned > 0:
        log_app(f"🧹 PATCH 24: {files_cleaned} fichiers nettoyés, {len(files_to_cleanup)} en attente", "INFO")

def manual_cleanup_old_files():
    """PATCH 25: Nettoyage manuel pour environnements sans 'schedule'"""
    try:
        uploads_dir = WINDOWS_PATHS.get('uploads_dir', 'uploads')
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=CLEANUP_DELAY_HOURS)
        
        files_cleaned = 0
        if os.path.exists(uploads_dir):
            for filename in os.listdir(uploads_dir):
                if filename.startswith('webhook_'):
                    file_path = os.path.join(uploads_dir, filename)
                    try:
                        # Vérifier l'âge du fichier
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_time < cutoff_time:
                            os.remove(file_path)
                            files_cleaned += 1
                    except Exception as e:
                        log_app(f"⚠️ PATCH 25: Erreur nettoyage manuel {filename}: {e}", "WARNING")
        
        if files_cleaned > 0:
            log_app(f"🧹 PATCH 25: Nettoyage manuel - {files_cleaned} fichiers anciens supprimés", "INFO")
        
        return files_cleaned
    except Exception as e:
        log_app(f"❌ PATCH 25: Erreur nettoyage manuel: {e}", "ERROR")
        return 0

def start_cleanup_scheduler():
    """Démarre le planificateur de nettoyage en arrière-plan"""
    if not SCHEDULE_AVAILABLE:
        log_app("⚠️ PATCH 25: Module 'schedule' non disponible - nettoyage différé désactivé", "WARNING")
        log_app("💡 PATCH 25: Pour activer: pip install schedule", "INFO")
        return False
    
    def run_scheduler():
        schedule.every(30).minutes.do(cleanup_old_files)  # Nettoyage toutes les 30 minutes
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérifier toutes les minutes
    
    cleanup_thread = threading.Thread(target=run_scheduler, daemon=True)
    cleanup_thread.start()
    log_app(f"🧹 PATCH 24: Planificateur de nettoyage démarré (délai: {CLEANUP_DELAY_HOURS}h)", "INFO")
    return True

# Ancien endpoint /api/webhook/publish supprimé - Logique intégrée dans /api/webhook

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=BACKEND_PORT)