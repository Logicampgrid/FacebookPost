#!/usr/bin/env python3
"""
POSTER MEDIA ENHANCED - Version restaurée et améliorée
Restaure la fonctionnalité poster_media() avec améliorations :
- Gestion robuste des erreurs Instagram (retry + fallback Facebook)
- Support multi-stores (gizmobbs, logicantiq, outdoor)
- Conversion WebP → JPEG améliorée
- Upload FTP optimisé
- Surveillance automatique de dossier
"""

import os
import sys
import time
import shutil
import asyncio
import uuid
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import requests
from PIL import Image
import ftplib
import mimetypes
import logging

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIGURATION MULTI-STORES ===
STORES_CONFIG = {
    "gizmobbs": {
        "name": "Gizmo BBS",
        "download_dir": "C:/gizmobbs/download",
        "processed_dir": "C:/gizmobbs/processed",
        "ftp_subdir": "gizmobbs",
        "access_token": os.getenv("FB_ACCESS_TOKEN_GIZMO"),
        "ig_user_id": os.getenv("IG_USER_ID_GIZMO"),
        "fb_page_id": "102401876209415"
    },
    "logicantiq": {
        "name": "LogicAntiq",
        "download_dir": "C:/logicantiq/download", 
        "processed_dir": "C:/logicantiq/processed",
        "ftp_subdir": "logicantiq",
        "access_token": os.getenv("FB_ACCESS_TOKEN_LOGICANTIQ"),
        "ig_user_id": os.getenv("IG_USER_ID_LOGICANTIQ"),
        "fb_page_id": "210654558802531"
    },
    "outdoor": {
        "name": "Logicamp Outdoor",
        "download_dir": "C:/outdoor/download",
        "processed_dir": "C:/outdoor/processed", 
        "ftp_subdir": "outdoor",
        "access_token": os.getenv("FB_ACCESS_TOKEN_OUTDOOR"),
        "ig_user_id": os.getenv("IG_USER_ID_OUTDOOR"),
        "fb_page_id": "236260991673388"
    }
}

# === CONFIGURATION FTP ===
FTP_HOST = os.getenv("FTP_HOST", "logicamp.org")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER", "logi")
FTP_PASSWORD = os.getenv("FTP_PASSWORD", "6837")
FTP_BASE_DIR = "/wordpress/uploads/"
FTP_BASE_URL = f"https://{FTP_HOST}/wordpress/uploads/"

# === CONFIGURATION RETRY INSTAGRAM ===
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 30
INSTAGRAM_ERRORS_TO_RETRY = [
    "temporarily blocked",
    "rate limit",
    "try again later",
    "server error",
    "timeout"
]

# Extensions supportées
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".mp4", ".mov"}

def log_poster(message: str, level: str = "INFO"):
    """Logging spécialisé pour poster_media"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "RETRY": "🔄"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [POSTER] {message}")
    
    # Log aussi via le logger standard
    if level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)
    else:
        logger.info(message)

async def convert_webp_to_jpeg(webp_path: str, quality: int = 95) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Convertit un fichier WebP en JPEG avec gestion d'erreurs améliorée
    Retourne (success, jpeg_path, error_message)
    """
    try:
        if not webp_path.lower().endswith('.webp'):
            return False, None, "Fichier non WebP"
        
        if not os.path.exists(webp_path):
            return False, None, f"Fichier non trouvé: {webp_path}"
        
        # Générer le nom du fichier JPEG
        jpeg_path = webp_path.replace('.webp', '_converted.jpeg').replace('.WEBP', '_converted.jpeg')
        
        # Conversion avec PIL
        with Image.open(webp_path) as img:
            # Convertir en RGB si nécessaire (pour gérer la transparence)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Sauvegarder en JPEG
            img.save(jpeg_path, 'JPEG', quality=quality, optimize=True)
        
        log_poster(f"Conversion WebP → JPEG réussie: {os.path.basename(jpeg_path)}", "SUCCESS")
        return True, jpeg_path, None
        
    except Exception as e:
        error_msg = f"Erreur conversion WebP: {str(e)}"
        log_poster(error_msg, "ERROR")
        return False, None, error_msg

async def upload_to_ftp_enhanced(local_file_path: str, store_config: dict, original_filename: str = None) -> dict:
    """
    Upload FTP amélioré avec retry et validation
    """
    try:
        if not os.path.exists(local_file_path):
            return {"success": False, "error": f"Fichier local non trouvé: {local_file_path}"}
        
        # Construire le nom de fichier et les URLs
        if not original_filename:
            original_filename = os.path.basename(local_file_path)
        
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:8]
        filename_parts = os.path.splitext(original_filename)
        ftp_filename = f"{store_config['ftp_subdir']}_{timestamp}_{unique_id}{filename_parts[1]}"
        
        # URL publique (fichier sera dans le sous-dossier store ou à la racine selon le succès de création)
        public_url = f"{FTP_BASE_URL}{store_config['ftp_subdir']}/{ftp_filename}"
        fallback_url = f"{FTP_BASE_URL}{ftp_filename}"  # En cas d'échec création dossier
        
        log_poster(f"Upload FTP: {ftp_filename}", "INFO")
        
        # Connexion FTP avec retry et configuration optimisée
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                ftp = ftplib.FTP()
                ftp.set_pasv(True)  # Mode passif par défaut
                ftp.connect(FTP_HOST, FTP_PORT, timeout=60)  # Timeout plus long
                ftp.login(FTP_USER, FTP_PASSWORD)
                
                log_poster(f"Connexion FTP réussie (tentative {attempt + 1})", "INFO")
                
                # Navigation vers le dossier WordPress uploads
                ftp.cwd(FTP_BASE_DIR)
                log_poster(f"Navigation vers {FTP_BASE_DIR}", "INFO")
                
                # Créer le dossier du store s'il n'existe pas
                try:
                    ftp.cwd(store_config['ftp_subdir'])
                    log_poster(f"Dossier store trouvé: {store_config['ftp_subdir']}", "INFO")
                except ftplib.error_perm:
                    try:
                        ftp.mkd(store_config['ftp_subdir'])
                        ftp.cwd(store_config['ftp_subdir'])
                        log_poster(f"Dossier store créé: {store_config['ftp_subdir']}", "SUCCESS")
                    except Exception as mkdir_error:
                        log_poster(f"Erreur création dossier store: {mkdir_error}", "WARNING")
                        # Rester dans le dossier parent
                
                # Upload du fichier avec timeout plus court pour l'opération
                log_poster(f"Début upload: {ftp_filename}", "INFO")
                with open(local_file_path, 'rb') as file:
                    ftp.storbinary(f'STOR {ftp_filename}', file, blocksize=8192)
                
                # Vérification que le fichier existe
                try:
                    ftp.size(ftp_filename)  # Test existence
                    log_poster("Upload confirmé sur le serveur", "SUCCESS")
                except:
                    log_poster("Fichier non confirmé, mais upload semble réussi", "WARNING")
                
                ftp.quit()
                
                # Déterminer l'URL publique correcte
                current_dir = ftp.pwd()
                if store_config['ftp_subdir'] in current_dir:
                    final_url = public_url
                else:
                    final_url = fallback_url
                    log_poster(f"Utilisation URL fallback: {final_url}", "WARNING")
                
                log_poster(f"Upload FTP réussi: {final_url}", "SUCCESS")
                return {
                    "success": True,
                    "ftp_url": final_url,
                    "filename": ftp_filename,
                    "attempt": attempt + 1
                }
                
            except Exception as ftp_error:
                log_poster(f"Tentative FTP {attempt + 1}/{max_attempts} échouée: {ftp_error}", "WARNING")
                if attempt == max_attempts - 1:
                    return {"success": False, "error": f"Upload FTP échoué après {max_attempts} tentatives: {ftp_error}"}
                await asyncio.sleep(5)  # Attendre avant retry
        
    except Exception as e:
        return {"success": False, "error": f"Erreur upload FTP: {str(e)}"}

async def publish_to_instagram_with_retry(image_url: str, caption: str, store_config: dict) -> dict:
    """
    Publication Instagram avec retry automatique et gestion d'erreurs
    """
    access_token = store_config.get("access_token")
    ig_user_id = store_config.get("ig_user_id")
    
    if not access_token or not ig_user_id:
        return {"success": False, "error": "Configuration Instagram manquante"}
    
    # PATCH 15: CORRECTION FINALE URLS INSTAGRAM - Convertir tous les chemins locaux
    log_poster(f"🔍 PATCH 15: URL originale reçue - '{image_url}'", "INFO")
    
    # Détecter et convertir les chemins locaux Windows (uploads\) et Unix (uploads/)
    if (not image_url.startswith(("http://", "https://")) and 
        ("uploads" in image_url or "webhook_" in image_url)):
        
        # Normaliser les backslashes Windows
        normalized_path = image_url.replace("\\", "/")
        filename = normalized_path.split("/")[-1]
        
        # Générer URL publique ngrok (réutiliser la logique du server.py)
        import os
        from pathlib import Path
        
        # Détecter l'URL ngrok active
        try:
            frontend_env_path = Path(__file__).parent.parent / "frontend" / ".env"
            if frontend_env_path.exists():
                with open(frontend_env_path, 'r') as f:
                    for line in f:
                        if line.startswith('REACT_APP_BACKEND_URL='):
                            ngrok_url = line.split('=', 1)[1].strip()
                            image_url = f"{ngrok_url}/uploads/{filename}"
                            log_poster(f"✅ PATCH 15: URL convertie - '{normalized_path}' → '{image_url}'", "SUCCESS")
                            break
        except Exception as e:
            log_poster(f"⚠️ PATCH 15: Erreur détection ngrok, fallback - {e}", "WARNING")
            # Fallback hardcodé si détection échoue
            image_url = f"https://9fff391906ce.ngrok-free.app/uploads/{filename}"
            log_poster(f"🔄 PATCH 15: Fallback URL - '{image_url}'", "INFO")
    else:
        log_poster(f"✅ PATCH 15: URL déjà publique - '{image_url}'", "SUCCESS")
    
    # PATCH 15: Vérification finale obligatoire
    if not image_url.startswith('https://'):
        error_msg = f"URL Instagram invalide: {image_url}"
        log_poster(f"❌ PATCH 15: {error_msg}", "ERROR")
        return {"success": False, "error": error_msg}
    
    for attempt in range(MAX_RETRY_ATTEMPTS):
        try:
            log_poster(f"Publication Instagram tentative {attempt + 1}/{MAX_RETRY_ATTEMPTS}", "INFO")
            
            # Étape 1: Créer le container de média
            container_url = f"https://graph.facebook.com/v18.0/{ig_user_id}/media"
            container_data = {
                "image_url": image_url,  # Maintenant garanti d'être une URL HTTPS valide
                "caption": caption,
                "access_token": access_token
            }
            
            log_poster(f"🔍 PATCH 15: URL finale envoyée à Instagram - '{image_url}'", "INFO")
            
            container_response = requests.post(container_url, data=container_data, timeout=30)
            
            if container_response.status_code != 200:
                error_detail = container_response.text
                log_poster(f"Erreur création container Instagram: {error_detail}", "ERROR")
                
                # Vérifier si c'est une erreur temporaire
                if any(error_keyword in error_detail.lower() for error_keyword in INSTAGRAM_ERRORS_TO_RETRY):
                    if attempt < MAX_RETRY_ATTEMPTS - 1:
                        log_poster(f"Erreur temporaire détectée, retry dans {RETRY_DELAY_SECONDS}s", "RETRY")
                        await asyncio.sleep(RETRY_DELAY_SECONDS)
                        continue
                
                return {"success": False, "error": f"Erreur container Instagram: {error_detail}"}
            
            container_id = container_response.json().get("id")
            if not container_id:
                return {"success": False, "error": "Container ID manquant"}
            
            # Étape 2: Publier le média
            publish_url = f"https://graph.facebook.com/v18.0/{ig_user_id}/media_publish"
            publish_data = {
                "creation_id": container_id,
                "access_token": access_token
            }
            
            publish_response = requests.post(publish_url, data=publish_data, timeout=30)
            
            if publish_response.status_code != 200:
                error_detail = publish_response.text
                log_poster(f"Erreur publication Instagram: {error_detail}", "ERROR")
                
                # Vérifier si c'est une erreur temporaire
                if any(error_keyword in error_detail.lower() for error_keyword in INSTAGRAM_ERRORS_TO_RETRY):
                    if attempt < MAX_RETRY_ATTEMPTS - 1:
                        log_poster(f"Erreur temporaire détectée, retry dans {RETRY_DELAY_SECONDS}s", "RETRY")
                        await asyncio.sleep(RETRY_DELAY_SECONDS)
                        continue
                
                return {"success": False, "error": f"Erreur publication Instagram: {error_detail}"}
            
            media_id = publish_response.json().get("id")
            log_poster(f"Publication Instagram réussie: {media_id}", "SUCCESS")
            
            return {
                "success": True,
                "media_id": media_id,
                "platform": "instagram",
                "attempt": attempt + 1
            }
            
        except requests.exceptions.Timeout:
            log_poster(f"Timeout Instagram tentative {attempt + 1}", "WARNING")
            if attempt < MAX_RETRY_ATTEMPTS - 1:
                await asyncio.sleep(RETRY_DELAY_SECONDS)
                continue
            return {"success": False, "error": "Timeout Instagram après plusieurs tentatives"}
            
        except Exception as e:
            log_poster(f"Erreur Instagram tentative {attempt + 1}: {str(e)}", "ERROR")
            if attempt < MAX_RETRY_ATTEMPTS - 1:
                await asyncio.sleep(RETRY_DELAY_SECONDS)
                continue
            return {"success": False, "error": f"Erreur Instagram: {str(e)}"}
    
    return {"success": False, "error": "Échec Instagram après toutes les tentatives"}

async def publish_to_facebook_fallback(image_url: str, message: str, store_config: dict) -> dict:
    """
    Publication Facebook en fallback si Instagram échoue
    """
    try:
        access_token = store_config.get("access_token")
        page_id = store_config.get("fb_page_id")
        
        if not access_token or not page_id:
            return {"success": False, "error": "Configuration Facebook manquante"}
        
        log_poster("Publication Facebook (fallback)", "INFO")
        
        # Publication sur page Facebook
        url = f"https://graph.facebook.com/v18.0/{page_id}/photos"
        data = {
            "url": image_url,
            "caption": message,
            "access_token": access_token
        }
        
        response = requests.post(url, data=data, timeout=30)
        
        if response.status_code == 200:
            post_id = response.json().get("id")
            log_poster(f"Publication Facebook réussie: {post_id}", "SUCCESS")
            return {
                "success": True,
                "post_id": post_id,
                "platform": "facebook"
            }
        else:
            error_detail = response.text
            log_poster(f"Erreur Facebook: {error_detail}", "ERROR")
            return {"success": False, "error": f"Erreur Facebook: {error_detail}"}
            
    except Exception as e:
        error_msg = f"Erreur publication Facebook: {str(e)}"
        log_poster(error_msg, "ERROR")
        return {"success": False, "error": error_msg}

async def process_single_file(file_path: str, store_config: dict) -> dict:
    """
    Traite un seul fichier : conversion, upload, publication
    """
    try:
        filename = os.path.basename(file_path)
        log_poster(f"Traitement: {filename}", "INFO")
        
        # Vérifier l'extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in SUPPORTED_EXTENSIONS:
            return {"success": False, "error": f"Extension non supportée: {file_ext}"}
        
        # Conversion WebP si nécessaire
        processed_file = file_path
        webp_converted = False
        
        if file_ext == '.webp':
            success, converted_path, error = await convert_webp_to_jpeg(file_path)
            if success and converted_path:
                processed_file = converted_path
                webp_converted = True
            else:
                return {"success": False, "error": f"Conversion WebP échouée: {error}"}
        
        # Upload FTP
        log_poster("Upload FTP en cours...", "INFO")
        ftp_result = await upload_to_ftp_enhanced(processed_file, store_config, filename)
        
        if not ftp_result["success"]:
            return {"success": False, "error": f"Upload FTP échoué: {ftp_result['error']}"}
        
        public_url = ftp_result["ftp_url"]
        
        # Préparer le message de publication
        caption = f"Nouveau produit {store_config['name']} disponible ! 🚀\n\n#shop #nouveaute #{store_config['ftp_subdir']}"
        
        # Publication Instagram avec retry
        instagram_result = await publish_to_instagram_with_retry(public_url, caption, store_config)
        
        publication_results = []
        
        if instagram_result["success"]:
            publication_results.append(instagram_result)
            log_poster("✅ Publication Instagram réussie", "SUCCESS")
        else:
            log_poster(f"❌ Instagram échoué: {instagram_result['error']}", "ERROR")
            
            # Fallback vers Facebook
            log_poster("🔄 Tentative fallback Facebook...", "INFO")
            facebook_result = await publish_to_facebook_fallback(public_url, caption, store_config)
            
            if facebook_result["success"]:
                publication_results.append(facebook_result)
                log_poster("✅ Publication Facebook (fallback) réussie", "SUCCESS")
            else:
                log_poster(f"❌ Facebook (fallback) échoué: {facebook_result['error']}", "ERROR")
        
        # Archivage du fichier
        if publication_results:  # Au moins une publication réussie
            processed_dir = store_config["processed_dir"]
            os.makedirs(processed_dir, exist_ok=True)
            
            # Nom de fichier unique pour l'archivage
            archive_filename = f"{int(time.time())}_{filename}"
            archive_path = os.path.join(processed_dir, archive_filename)
            
            # Déplacer le fichier original
            shutil.move(file_path, archive_path)
            log_poster(f"Fichier archivé: {archive_filename}", "SUCCESS")
            
            # Nettoyer le fichier converti si nécessaire
            if webp_converted and os.path.exists(processed_file):
                os.unlink(processed_file)
                log_poster("Fichier JPEG temporaire supprimé", "INFO")
        
        return {
            "success": bool(publication_results),
            "file": filename,
            "ftp_url": public_url,
            "publications": publication_results,
            "webp_converted": webp_converted
        }
        
    except Exception as e:
        error_msg = f"Erreur traitement {filename}: {str(e)}"
        log_poster(error_msg, "ERROR")
        return {"success": False, "error": error_msg}

async def poster_media_enhanced(store_name: str = None) -> dict:
    """
    Fonction principale de publication automatique améliorée
    Si store_name est None, traite tous les stores
    """
    try:
        log_poster("=== DÉBUT PUBLICATION AUTOMATIQUE AMÉLIORÉE ===", "INFO")
        
        stores_to_process = []
        if store_name:
            if store_name in STORES_CONFIG:
                stores_to_process = [store_name]
            else:
                return {"success": False, "error": f"Store inconnu: {store_name}"}
        else:
            stores_to_process = list(STORES_CONFIG.keys())
        
        global_stats = {
            "stores_processed": 0,
            "total_files_found": 0,
            "total_files_processed": 0,
            "total_files_published": 0,
            "total_files_failed": 0,
            "store_results": {},
            "errors": []
        }
        
        # Traiter chaque store
        for store in stores_to_process:
            store_config = STORES_CONFIG[store]
            log_poster(f"📁 Traitement store: {store_config['name']}", "INFO")
            
            download_dir = store_config["download_dir"]
            
            # Vérifier l'existence du dossier
            if not os.path.exists(download_dir):
                log_poster(f"Dossier non trouvé: {download_dir}", "WARNING")
                global_stats["store_results"][store] = {
                    "success": False,
                    "error": f"Dossier non trouvé: {download_dir}"
                }
                continue
            
            # Statistiques du store
            store_stats = {
                "files_found": 0,
                "files_processed": 0,
                "files_published": 0,
                "files_failed": 0,
                "processed_files": [],
                "errors": []
            }
            
            # Parcourir les fichiers
            for filename in os.listdir(download_dir):
                file_path = os.path.join(download_dir, filename)
                
                # Ignorer les dossiers
                if not os.path.isfile(file_path):
                    continue
                
                store_stats["files_found"] += 1
                
                # Traiter le fichier
                result = await process_single_file(file_path, store_config)
                store_stats["files_processed"] += 1
                
                if result["success"]:
                    store_stats["files_published"] += 1
                    store_stats["processed_files"].append({
                        "file": result["file"],
                        "ftp_url": result["ftp_url"],
                        "publications": result["publications"],
                        "webp_converted": result.get("webp_converted", False)
                    })
                else:
                    store_stats["files_failed"] += 1
                    store_stats["errors"].append(result["error"])
            
            # Enregistrer les résultats du store
            global_stats["store_results"][store] = store_stats
            global_stats["stores_processed"] += 1
            global_stats["total_files_found"] += store_stats["files_found"]
            global_stats["total_files_processed"] += store_stats["files_processed"]
            global_stats["total_files_published"] += store_stats["files_published"]
            global_stats["total_files_failed"] += store_stats["files_failed"]
            global_stats["errors"].extend(store_stats["errors"])
            
            log_poster(f"Store {store} terminé: {store_stats['files_published']}/{store_stats['files_processed']} publiés", "INFO")
        
        # Résumé final
        log_poster("=== RÉSUMÉ PUBLICATION AUTOMATIQUE AMÉLIORÉE ===", "INFO")
        log_poster(f"Stores traités: {global_stats['stores_processed']}", "INFO")
        log_poster(f"Fichiers trouvés: {global_stats['total_files_found']}", "INFO")
        log_poster(f"Fichiers traités: {global_stats['total_files_processed']}", "INFO")
        log_poster(f"Fichiers publiés: {global_stats['total_files_published']}", "SUCCESS")
        log_poster(f"Fichiers en échec: {global_stats['total_files_failed']}", "ERROR")
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "stats": global_stats,
            "message": f"Publication terminée: {global_stats['total_files_published']}/{global_stats['total_files_processed']} fichiers publiés sur {global_stats['stores_processed']} stores"
        }
        
    except Exception as e:
        error_msg = f"Erreur générale poster_media_enhanced: {str(e)}"
        log_poster(error_msg, "ERROR")
        return {"success": False, "error": error_msg}

if __name__ == "__main__":
    # Test de la fonction
    import asyncio
    
    async def test_poster_media():
        result = await poster_media_enhanced("gizmobbs")  # Test sur un store spécifique
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    asyncio.run(test_poster_media())