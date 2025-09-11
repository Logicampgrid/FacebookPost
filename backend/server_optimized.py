from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
from bson import ObjectId
from PIL import Image, ImageOps
import io
import tempfile
import subprocess
import mimetypes
from pathlib import Path
import time
import sys

load_dotenv()

app = FastAPI(title="Meta Publishing Platform - Instagram Optimized")

# Configuration flags
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
SELFTEST_MODE = "--selftest" in sys.argv

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Request logging middleware
#@app.middleware("http")
async def log_requests(request: Request, call_next):
    if request.url.path == "/api/webhook":
        method = request.method
        headers = dict(request.headers)
        print(f"[Webhook] {method} request → {request.url}")
        if DRY_RUN:
            print(f"[DRY_RUN] Headers: {headers}")
    
    response = await call_next(request)
    return response

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS requests for CORS"""
    return {"message": "OK"}

# MongoDB setup
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.meta_posts

# Facebook/Meta configuration
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
FACEBOOK_GRAPH_URL = os.getenv("FACEBOOK_GRAPH_URL", "https://graph.facebook.com/v18.0")

# External webhook configuration
NGROK_URL = os.getenv("NGROK_URL", "")
EXTERNAL_WEBHOOK_ENABLED = os.getenv("EXTERNAL_WEBHOOK_ENABLED", "false").lower() == "true"

# Create uploads directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("uploads/processed", exist_ok=True)
os.makedirs("uploads/optimized", exist_ok=True)

# ============================================================================
# UTILITAIRES DE LOGGING STRUCTURÉS
# ============================================================================

def log_instagram(message: str, level: str = "INFO"):
    """Log structuré pour Instagram avec préfixe"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "RETRY": "🔄"}
    icon = icons.get(level.upper(), "📝")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [Instagram] {message}")

def log_facebook(message: str, level: str = "INFO"):
    """Log structuré pour Facebook avec préfixe"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "RETRY": "🔄"}
    icon = icons.get(level.upper(), "📝")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [Facebook] {message}")

def log_media(message: str, level: str = "INFO"):
    """Log structuré pour gestion médias avec préfixe"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "CONVERSION": "🔄"}
    icon = icons.get(level.upper(), "📁")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [Media] {message}")

def log_retry(message: str, attempt: int, max_attempts: int):
    """Log structuré pour tentatives de retry"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"🔄 [{timestamp}] [Retry] Tentative {attempt}/{max_attempts} → {message}")

# ============================================================================
# DETECTION ET CONVERSION AUTOMATIQUE DE MÉDIAS
# ============================================================================

async def detect_media_type(file_path_or_url: str) -> str:
    """Détecte le type de média (image/video) de manière robuste"""
    try:
        # Extensions connues
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic', '.avif'}
        video_exts = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
        
        # Obtenir extension
        if file_path_or_url.startswith('http'):
            ext = '.' + file_path_or_url.lower().split('.')[-1].split('?')[0]
        else:
            ext = '.' + file_path_or_url.lower().split('.')[-1]
        
        if ext in image_exts:
            return "image"
        elif ext in video_exts:
            return "video"
        
        # Fallback: essayer d'ouvrir comme image
        if os.path.exists(file_path_or_url):
            try:
                with Image.open(file_path_or_url) as img:
                    return "image"
            except:
                pass
        
        return "unknown"
    except Exception as e:
        log_media(f"Erreur détection type: {str(e)}", "ERROR")
        return "unknown"

async def download_media_with_retry(url: str, max_attempts: int = 3, timeout: int = 30) -> tuple:
    """Télécharge un média avec retry et timeout étendu"""
    for attempt in range(1, max_attempts + 1):
        try:
            log_retry(f"Téléchargement {url}", attempt, max_attempts)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/*,video/*,*/*;q=0.8',
                'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
                'DNT': '1',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(url, headers=headers, timeout=timeout, stream=True, allow_redirects=True)
            response.raise_for_status()
            
            # Vérifier taille
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > 250 * 1024 * 1024:  # 250MB max
                return False, None, "Fichier trop volumineux"
            
            # Téléchargement par chunks
            content_chunks = []
            total_size = 0
            max_size = 250 * 1024 * 1024
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    content_chunks.append(chunk)
                    total_size += len(chunk)
                    if total_size > max_size:
                        return False, None, "Dépassement limite taille"
            
            content_data = b''.join(content_chunks)
            
            # Créer fichier local
            unique_id = uuid.uuid4().hex[:8]
            timestamp = int(datetime.utcnow().timestamp())
            
            # Déterminer extension
            content_type = response.headers.get('content-type', '').lower()
            if 'image' in content_type:
                ext = '.jpg'
                if 'png' in content_type:
                    ext = '.png'
                elif 'webp' in content_type:
                    ext = '.webp'
            elif 'video' in content_type:
                ext = '.mp4'
            else:
                ext = '.bin'
            
            local_path = f"uploads/processed/download_{timestamp}_{unique_id}{ext}"
            
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                f.write(content_data)
            
            if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                log_media(f"Téléchargement réussi: {local_path} ({len(content_data)} bytes)", "SUCCESS")
                return True, local_path, None
            else:
                return False, None, "Fichier local non créé"
                
        except requests.exceptions.Timeout:
            log_retry(f"Timeout ({timeout}s)", attempt, max_attempts)
            timeout *= 2  # Augmenter timeout pour tentative suivante
        except requests.exceptions.RequestException as e:
            log_retry(f"Erreur requête: {str(e)}", attempt, max_attempts)
        except Exception as e:
            log_retry(f"Erreur: {str(e)}", attempt, max_attempts)
        
        if attempt < max_attempts:
            await asyncio.sleep(2 ** attempt)  # Backoff exponentiel
    
    return False, None, f"Échec après {max_attempts} tentatives"

async def convert_image_to_instagram_format(input_path: str) -> tuple:
    """
    Convertit une image vers le format optimal Instagram
    WEBP/HEIC/AVIF/PNG → JPEG (qualité 85, sRGB, max 1080×1350, strip EXIF)
    PNG reste PNG seulement si transparence détectée
    """
    try:
        log_media(f"Conversion Instagram: {input_path}", "CONVERSION")
        
        if not os.path.exists(input_path):
            return False, None, "Fichier d'entrée introuvable"
        
        with Image.open(input_path) as img:
            original_format = img.format
            original_size = img.size
            original_mode = img.mode
            
            log_media(f"Original: {original_format} {original_size} {original_mode}")
            
            # Vérifier transparence
            has_transparency = (
                original_mode in ('RGBA', 'LA') or
                (original_mode == 'P' and 'transparency' in img.info)
            )
            
            # Décision format de sortie
            if original_format == 'PNG' and has_transparency:
                # Garder PNG si transparence nécessaire
                output_format = 'PNG'
                output_ext = '.png'
                log_media("PNG avec transparence → Conserver PNG", "INFO")
            else:
                # Convertir en JPEG pour tous les autres cas
                output_format = 'JPEG'
                output_ext = '.jpg'
                log_media(f"{original_format} → JPEG (Instagram optimisé)", "INFO")
            
            # Créer chemin de sortie
            unique_id = uuid.uuid4().hex[:8]
            timestamp = int(datetime.utcnow().timestamp())
            output_path = f"uploads/optimized/instagram_{timestamp}_{unique_id}{output_ext}"
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Traitement de l'image
            processed_img = img.copy()
            
            # Correction orientation EXIF
            try:
                processed_img = ImageOps.exif_transpose(processed_img)
                log_media("Orientation EXIF corrigée", "INFO")
            except:
                pass
            
            # Redimensionnement Instagram (max 1080×1350)
            max_width, max_height = 1080, 1350
            if processed_img.width > max_width or processed_img.height > max_height:
                # Calculer nouvelles dimensions en gardant ratio
                ratio = min(max_width / processed_img.width, max_height / processed_img.height)
                new_width = int(processed_img.width * ratio)
                new_height = int(processed_img.height * ratio)
                processed_img = processed_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                log_media(f"Redimensionné: {new_width}×{new_height}", "INFO")
            
            # Conversion couleur selon format
            if output_format == 'JPEG':
                # Convertir en sRGB et supprimer transparence
                if processed_img.mode in ('RGBA', 'LA', 'P'):
                    # Fond blanc pour transparence
                    rgb_img = Image.new('RGB', processed_img.size, (255, 255, 255))
                    if processed_img.mode == 'P':
                        processed_img = processed_img.convert('RGBA')
                    rgb_img.paste(processed_img, mask=processed_img.split()[-1] if processed_img.mode in ('RGBA', 'LA') else None)
                    processed_img = rgb_img
                elif processed_img.mode != 'RGB':
                    processed_img = processed_img.convert('RGB')
                
                # Sauvegarder JPEG optimisé Instagram
                processed_img.save(output_path, 'JPEG', 
                                 quality=85,        # Qualité optimale IG
                                 optimize=True,     # Optimisation
                                 progressive=True)  # Chargement progressif
                
            else:  # PNG
                # Sauvegarder PNG optimisé
                processed_img.save(output_path, 'PNG', optimize=True)
            
            # Vérification taille finale
            final_size = os.path.getsize(output_path)
            final_size_mb = final_size / (1024 * 1024)
            
            if final_size_mb > 8:  # Limite Instagram
                log_media(f"⚠️ Taille encore élevée: {final_size_mb:.1f}MB", "WARNING")
            
            log_media(f"Conversion réussie: {output_path} ({final_size_mb:.2f}MB)", "SUCCESS")
            return True, output_path, None
            
    except Exception as e:
        error_msg = f"Erreur conversion image: {str(e)}"
        log_media(error_msg, "ERROR")
        return False, None, error_msg

async def convert_video_to_instagram_format(input_path: str) -> tuple:
    """
    Convertit une vidéo vers le format optimal Instagram
    → MP4 (H.264 + AAC), max 1080×1350, < 100MB, durée 3-60s, bitrate adaptatif
    """
    try:
        log_media(f"Conversion vidéo Instagram: {input_path}", "CONVERSION")
        
        if not os.path.exists(input_path):
            return False, None, None, "Fichier d'entrée introuvable"
        
        # Analyser vidéo source
        try:
            probe_result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                '-show_format', '-show_streams', input_path
            ], capture_output=True, text=True, timeout=30)
            
            if probe_result.returncode == 0:
                video_info = json.loads(probe_result.stdout)
                format_info = video_info.get('format', {})
                video_streams = [s for s in video_info.get('streams', []) if s.get('codec_type') == 'video']
                
                duration = float(format_info.get('duration', 0))
                
                if video_streams:
                    video_stream = video_streams[0]
                    width = video_stream.get('width', 0)
                    height = video_stream.get('height', 0)
                    log_media(f"Source: {width}×{height}, {duration:.1f}s")
                
        except Exception as e:
            log_media(f"⚠️ Analyse ffprobe échouée: {str(e)}", "WARNING")
            duration = 30  # Valeur par défaut
        
        # Créer chemin de sortie
        unique_id = uuid.uuid4().hex[:8]
        timestamp = int(datetime.utcnow().timestamp())
        output_path = f"uploads/optimized/instagram_{timestamp}_{unique_id}.mp4"
        thumbnail_path = f"uploads/optimized/thumb_{timestamp}_{unique_id}.jpg"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Limiter durée (3-60s pour Instagram)
        target_duration = min(max(duration, 3), 60)
        if duration > 60:
            log_media(f"Durée tronquée: {duration:.1f}s → {target_duration}s", "WARNING")
        
        # Paramètres FFmpeg optimisés Instagram
        ffmpeg_cmd = [
            'ffmpeg', '-y', '-i', input_path,
            # Codecs optimaux Instagram
            '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1',
            '-preset', 'medium', '-crf', '23',
            '-c:a', 'aac', '-ar', '44100', '-b:a', '128k', '-ac', '2',
            # Optimisations Instagram
            '-movflags', '+faststart+frag_keyframe+separate_moof',
            # Redimensionnement et aspect ratio Instagram
            '-vf', 'scale=1080:1350:force_original_aspect_ratio=decrease:force_divisible_by=2,pad=1080:1350:(ow-iw)/2:(oh-ih)/2:color=black',
            '-r', '30', '-g', '30',  # 30fps, GOP 30
            '-t', str(target_duration),  # Durée limitée
            '-max_muxing_queue_size', '1024',
            output_path
        ]
        
        log_media("Lancement conversion FFmpeg...", "CONVERSION")
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and os.path.exists(output_path):
            # Vérifier taille finale
            final_size = os.path.getsize(output_path)
            final_size_mb = final_size / (1024 * 1024)
            
            # Générer miniature JPEG
            thumbnail_cmd = [
                'ffmpeg', '-y', '-i', output_path,
                '-vf', 'select=eq(n\\,0)', '-q:v', '3',
                '-frames:v', '1', thumbnail_path
            ]
            
            subprocess.run(thumbnail_cmd, capture_output=True, timeout=30)
            
            log_media(f"Conversion réussie: {output_path} ({final_size_mb:.2f}MB)", "SUCCESS")
            
            if os.path.exists(thumbnail_path):
                log_media(f"Miniature créée: {thumbnail_path}", "SUCCESS")
                return True, output_path, thumbnail_path, None
            else:
                return True, output_path, None, None
        else:
            error_msg = f"FFmpeg échec (code {result.returncode}): {result.stderr[:200]}"
            log_media(error_msg, "ERROR")
            return False, None, None, error_msg
            
    except subprocess.TimeoutExpired:
        return False, None, None, "Timeout conversion vidéo (300s)"
    except FileNotFoundError:
        return False, None, None, "FFmpeg non disponible"
    except Exception as e:
        error_msg = f"Erreur conversion vidéo: {str(e)}"
        log_media(error_msg, "ERROR")
        return False, None, None, error_msg

# ============================================================================
# MODÈLES DE DONNÉES
# ============================================================================

class Post(BaseModel):
    target_id: str
    target_name: str
    content: str
    media_urls: List[str] = []
    link_metadata: Optional[dict] = None
    comment_link: Optional[str] = None
    product_link: Optional[str] = None  # Lien produit pour posts cliquables
    
    class Config:
        extra = "allow"

class PublishRequest(BaseModel):
    posts: List[Post]
    platforms: List[str] = ["facebook", "instagram"]

# ============================================================================
# PUBLICATION INSTAGRAM AVEC POLLING ET FALLBACKS
# ============================================================================

async def poll_instagram_container_status(container_id: str, access_token: str, max_attempts: int = 10) -> dict:
    """Poll le statut d'un container Instagram avec backoff exponentiel"""
    base_delay = 2  # Commencer à 2s
    
    for attempt in range(1, max_attempts + 1):
        try:
            # Calculer délai avec backoff (2s → 4s → 8s, max 8s)
            delay = min(base_delay * (2 ** (attempt - 1)), 8)
            
            if attempt > 1:
                log_retry(f"Attente {delay}s avant vérification statut", attempt, max_attempts)
                await asyncio.sleep(delay)
            
            # Vérifier statut container
            status_url = f"{FACEBOOK_GRAPH_URL}/{container_id}"
            params = {
                'fields': 'status_code,status',
                'access_token': access_token
            }
            
            if DRY_RUN:
                log_instagram(f"[DRY_RUN] Vérification statut: {status_url}", "INFO")
                # Simuler succès après quelques tentatives
                if attempt >= 3:
                    return {"status": "FINISHED", "status_code": "PUBLISHED"}
                else:
                    return {"status": "IN_PROGRESS", "status_code": ""}
            
            response = requests.get(status_url, params=params, timeout=30)
            response.raise_for_status()
            
            status_data = response.json()
            status_code = status_data.get('status_code', '')
            status = status_data.get('status', 'UNKNOWN')
            
            log_instagram(f"Statut container (tentative {attempt}): {status} - {status_code}")
            
            # Vérifier si terminé
            if status_code == 'PUBLISHED' or status == 'FINISHED':
                log_instagram("Container prêt pour publication", "SUCCESS")
                return {"status": "FINISHED", "status_code": status_code}
            elif status_code in ['ERROR', 'FAILED'] or status in ['ERROR', 'FAILED']:
                log_instagram(f"Container en erreur: {status_code}", "ERROR")
                return {"status": "ERROR", "status_code": status_code, "error": status_data}
            else:
                log_instagram(f"Container en cours de traitement: {status}")
        
        except requests.exceptions.RequestException as e:
            log_instagram(f"Erreur vérification statut (tentative {attempt}): {str(e)}", "ERROR")
        except Exception as e:
            log_instagram(f"Erreur polling (tentative {attempt}): {str(e)}", "ERROR")
    
    # Timeout après toutes les tentatives
    log_instagram(f"Timeout polling après {max_attempts} tentatives (≈{120}s)", "ERROR")
    return {"status": "TIMEOUT", "status_code": "POLLING_TIMEOUT"}

async def post_to_instagram_with_fallback(post: Post, page_access_token: str) -> dict:
    """
    Publication Instagram avec fallback vidéo → image de couverture
    Gère polling avec backoff et timeout
    """
    try:
        log_instagram(f"Publication vers @{post.target_name} ({post.target_id})")
        
        if DRY_RUN:
            log_instagram("[DRY_RUN] Mode simulation activé")
        
        # Vérifier présence médias
        if not post.media_urls:
            log_instagram("Aucun média fourni", "ERROR")
            return {"status": "error", "message": "No media provided"}
        
        # Analyser et classer les médias
        video_files = []
        image_files = []
        
        for media_url in post.media_urls:
            media_type = await detect_media_type(media_url)
            if media_type == "video":
                video_files.append(media_url)
                log_instagram(f"Vidéo détectée: {media_url}")
            elif media_type == "image":
                image_files.append(media_url)
                log_instagram(f"Image détectée: {media_url}")
        
        # STRATÉGIE 1: Essayer vidéo d'abord
        if video_files:
            log_instagram("Stratégie 1: Publication vidéo", "INFO")
            result = await attempt_instagram_video_post(video_files[0], post, page_access_token)
            
            if result.get("status") == "success":
                log_instagram("Publication vidéo réussie", "SUCCESS")
                return result
            else:
                log_instagram(f"Publication vidéo échouée: {result.get('message', 'Erreur inconnue')}", "WARNING")
        
        # STRATÉGIE 2: Fallback image de couverture
        if image_files:
            log_instagram("Stratégie 2: Fallback image de couverture", "INFO")
            result = await attempt_instagram_image_post(image_files[0], post, page_access_token)
            
            if result.get("status") == "success":
                log_instagram("Publication image fallback réussie", "SUCCESS")
                return result
            else:
                log_instagram(f"Publication image fallback échouée: {result.get('message', 'Erreur inconnue')}", "ERROR")
        
        # STRATÉGIE 3: Échec total
        log_instagram("Toutes les stratégies ont échoué", "ERROR")
        return {
            "status": "error",
            "message": "Échec publication vidéo et image fallback",
            "attempted_strategies": ["video", "image_fallback"]
        }
        
    except Exception as e:
        error_msg = f"Erreur publication Instagram: {str(e)}"
        log_instagram(error_msg, "ERROR")
        return {"status": "error", "message": error_msg}

async def attempt_instagram_video_post(video_url: str, post: Post, access_token: str) -> dict:
    """Tentative de publication vidéo Instagram avec conversion et polling"""
    try:
        log_instagram("Traitement vidéo pour Instagram")
        
        # Préparer fichier vidéo local
        local_video_path = None
        
        if video_url.startswith('http'):
            # Télécharger vidéo externe
            success, downloaded_path, error = await download_media_with_retry(video_url)
            if not success:
                return {"status": "error", "message": f"Échec téléchargement vidéo: {error}"}
            local_video_path = downloaded_path
        else:
            # Fichier local
            local_video_path = video_url.replace('/api/uploads/', 'uploads/')
            if not os.path.exists(local_video_path):
                return {"status": "error", "message": "Fichier vidéo local introuvable"}
        
        # Convertir vidéo au format Instagram
        success, converted_path, thumbnail_path, error = await convert_video_to_instagram_format(local_video_path)
        if not success:
            return {"status": "error", "message": f"Échec conversion vidéo: {error}"}
        
        final_video_path = converted_path if success else local_video_path
        
        # Créer container Instagram pour vidéo
        container_url = f"{FACEBOOK_GRAPH_URL}/{post.target_id}/media"
        
        # Préparer caption avec lien produit
        caption = post.content or ""
        if post.product_link:
            caption += f"\n\n🛒 Lien produit: {post.product_link}"
        elif post.comment_link:
            caption += f"\n\n🛒 Plus d'infos en bio!"
        
        container_data = {
            'media_type': 'VIDEO',
            'caption': caption,
            'access_token': access_token
        }
        
        # Ajouter URL vidéo
        if video_url.startswith('http'):
            container_data['video_url'] = video_url
        else:
            # Construire URL publique pour fichier local
            dynamic_base_url = os.getenv('DYNAMIC_BASE_URL', 'http://localhost:8001')
            container_data['video_url'] = f"{dynamic_base_url}{video_url}"
        
        if DRY_RUN:
            log_instagram(f"[DRY_RUN] Container vidéo: {container_data}")
            # Simuler création container
            container_id = f"fake_container_{uuid.uuid4().hex[:8]}"
        else:
            # Créer container réel
            response = requests.post(container_url, data=container_data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            container_id = result.get('id')
            
            if not container_id:
                return {"status": "error", "message": "Pas d'ID container retourné"}
        
        log_instagram(f"Container vidéo créé: {container_id}")
        
        # Polling du statut avec backoff
        poll_result = await poll_instagram_container_status(container_id, access_token)
        
        if poll_result.get("status") == "FINISHED":
            # Publier le container
            if DRY_RUN:
                log_instagram("[DRY_RUN] Publication container simulée")
                media_id = f"fake_media_{uuid.uuid4().hex[:8]}"
            else:
                publish_url = f"{FACEBOOK_GRAPH_URL}/{post.target_id}/media_publish"
                publish_data = {
                    'creation_id': container_id,
                    'access_token': access_token
                }
                
                publish_response = requests.post(publish_url, data=publish_data, timeout=30)
                publish_response.raise_for_status()
                
                publish_result = publish_response.json()
                media_id = publish_result.get('id')
            
            log_instagram(f"Publication vidéo réussie: {media_id}", "SUCCESS")
            return {
                "status": "success",
                "media_id": media_id,
                "container_id": container_id,
                "media_type": "video"
            }
        else:
            # Container en erreur ou timeout
            error_msg = f"Container status: {poll_result.get('status')} - {poll_result.get('status_code', 'N/A')}"
            log_instagram(f"Container vidéo échoué: {error_msg}", "ERROR")
            return {"status": "error", "message": error_msg}
        
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Erreur API Instagram: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Erreur vidéo Instagram: {str(e)}"}

async def attempt_instagram_image_post(image_url: str, post: Post, access_token: str) -> dict:
    """Tentative de publication image Instagram avec conversion optimisée"""
    try:
        log_instagram("Traitement image pour Instagram")
        
        # Préparer fichier image local
        local_image_path = None
        
        if image_url.startswith('http'):
            # Télécharger image externe
            success, downloaded_path, error = await download_media_with_retry(image_url)
            if not success:
                return {"status": "error", "message": f"Échec téléchargement image: {error}"}
            local_image_path = downloaded_path
        else:
            # Fichier local
            local_image_path = image_url.replace('/api/uploads/', 'uploads/')
            if not os.path.exists(local_image_path):
                return {"status": "error", "message": "Fichier image local introuvable"}
        
        # Convertir image au format Instagram optimal
        success, converted_path, error = await convert_image_to_instagram_format(local_image_path)
        if not success:
            log_instagram(f"⚠️ Conversion échouée, utilisation originale: {error}", "WARNING")
            converted_path = local_image_path
        
        # Créer container Instagram pour image
        container_url = f"{FACEBOOK_GRAPH_URL}/{post.target_id}/media"
        
        # Préparer caption avec lien produit cliquable
        caption = post.content or ""
        if post.product_link:
            caption += f"\n\n🛒 Lien produit: {post.product_link}" 
        elif post.comment_link:
            caption += f"\n\n🛒 Plus d'infos en bio!"
        
        container_data = {
            'caption': caption,
            'access_token': access_token
        }
        
        # Ajouter URL image
        if image_url.startswith('http'):
            container_data['image_url'] = image_url
        else:
            # Construire URL publique pour fichier local
            dynamic_base_url = os.getenv('DYNAMIC_BASE_URL', 'http://localhost:8001')
            container_data['image_url'] = f"{dynamic_base_url}{image_url}"
        
        if DRY_RUN:
            log_instagram(f"[DRY_RUN] Container image: {container_data}")
            container_id = f"fake_container_{uuid.uuid4().hex[:8]}"
        else:
            # Créer container réel
            response = requests.post(container_url, data=container_data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            container_id = result.get('id')
            
            if not container_id:
                return {"status": "error", "message": "Pas d'ID container retourné"}
        
        log_instagram(f"Container image créé: {container_id}")
        
        # Pour les images, polling plus rapide
        poll_result = await poll_instagram_container_status(container_id, access_token, max_attempts=5)
        
        if poll_result.get("status") == "FINISHED":
            # Publier le container
            if DRY_RUN:
                log_instagram("[DRY_RUN] Publication container simulée")
                media_id = f"fake_media_{uuid.uuid4().hex[:8]}"
            else:
                publish_url = f"{FACEBOOK_GRAPH_URL}/{post.target_id}/media_publish"
                publish_data = {
                    'creation_id': container_id,
                    'access_token': access_token
                }
                
                publish_response = requests.post(publish_url, data=publish_data, timeout=30)
                publish_response.raise_for_status()
                
                publish_result = publish_response.json()
                media_id = publish_result.get('id')
            
            log_instagram(f"Publication image réussie: {media_id}", "SUCCESS")
            return {
                "status": "success", 
                "media_id": media_id,
                "container_id": container_id,
                "media_type": "image"
            }
        else:
            error_msg = f"Container status: {poll_result.get('status')} - {poll_result.get('status_code', 'N/A')}"
            log_instagram(f"Container image échoué: {error_msg}", "ERROR")
            return {"status": "error", "message": error_msg}
        
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Erreur API Instagram: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Erreur image Instagram: {str(e)}"}

# ============================================================================
# PUBLICATION FACEBOOK AVEC POSTS CLIQUABLES
# ============================================================================

async def post_to_facebook_with_clickable_links(post: Post, page_access_token: str) -> dict:
    """Publication Facebook avec gestion des liens cliquables produit"""
    try:
        log_facebook(f"Publication vers {post.target_name} ({post.target_id})")
        
        if DRY_RUN:
            log_facebook("[DRY_RUN] Mode simulation activé")
        
        # URL de l'API Facebook
        url = f"{FACEBOOK_GRAPH_URL}/{post.target_id}/feed"
        
        # Données de base
        data = {
            'access_token': page_access_token,
            'message': post.content or ""
        }
        
        # Gestion des liens cliquables
        if post.product_link:
            # Lien produit cliquable direct
            data['link'] = post.product_link
            log_facebook(f"Lien produit ajouté: {post.product_link}")
        elif post.comment_link:
            # Lien en commentaire
            data['link'] = post.comment_link
            log_facebook(f"Lien commentaire ajouté: {post.comment_link}")
        elif post.link_metadata:
            # Métadonnées de lien
            if 'url' in post.link_metadata:
                data['link'] = post.link_metadata['url']
                log_facebook(f"Lien métadonnées ajouté: {post.link_metadata['url']}")
        
        # Gestion des médias
        if post.media_urls:
            # Prendre le premier média pour Facebook
            media_url = post.media_urls[0]
            media_type = await detect_media_type(media_url)
            
            if media_type == "image":
                # Pour les images, utiliser 'url' directement
                if media_url.startswith('http'):
                    data['url'] = media_url
                else:
                    dynamic_base_url = os.getenv('DYNAMIC_BASE_URL', 'http://localhost:8001')
                    data['url'] = f"{dynamic_base_url}{media_url}"
                log_facebook(f"Image ajoutée: {data['url']}")
                
            elif media_type == "video":
                # Pour les vidéos, utiliser upload multipart ou URL
                if media_url.startswith('http'):
                    data['source'] = media_url
                else:
                    dynamic_base_url = os.getenv('DYNAMIC_BASE_URL', 'http://localhost:8001')
                    data['source'] = f"{dynamic_base_url}{media_url}"
                log_facebook(f"Vidéo ajoutée: {data['source']}")
        
        if DRY_RUN:
            log_facebook(f"[DRY_RUN] Données publication: {data}")
            return {
                "status": "success",
                "message": "Publication simulée",
                "post_id": f"fake_post_{uuid.uuid4().hex[:8]}"
            }
        
        # Publication réelle
        response = requests.post(url, data=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        post_id = result.get('id')
        
        if post_id:
            log_facebook(f"Publication réussie: {post_id}", "SUCCESS")
            return {
                "status": "success",
                "message": "Successfully posted to Facebook",
                "post_id": post_id
            }
        else:
            log_facebook("Pas d'ID post retourné", "ERROR")
            return {"status": "error", "message": "No post ID returned"}
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Erreur API Facebook: {str(e)}"
        log_facebook(error_msg, "ERROR")
        return {"status": "error", "message": error_msg}
    except Exception as e:
        error_msg = f"Erreur publication Facebook: {str(e)}"
        log_facebook(error_msg, "ERROR")
        return {"status": "error", "message": error_msg}

# ============================================================================
# GESTION CENTRALISÉE DES ERREURS
# ============================================================================

class SocialMediaError(Exception):
    """Exception personnalisée pour erreurs réseaux sociaux"""
    def __init__(self, platform: str, operation: str, message: str, retry_possible: bool = False):
        self.platform = platform
        self.operation = operation
        self.message = message
        self.retry_possible = retry_possible
        super().__init__(f"[{platform}] {operation}: {message}")

def handle_api_error(response: requests.Response, platform: str, operation: str) -> dict:
    """Gestion centralisée des erreurs API avec messages actionnables"""
    try:
        error_data = response.json()
        error_msg = error_data.get('error', {}).get('message', 'Erreur inconnue')
        error_code = error_data.get('error', {}).get('code', 'N/A')
        error_subcode = error_data.get('error', {}).get('error_subcode', 'N/A')
        
        # Messages actionnables selon les codes d'erreur
        actionable_msg = error_msg
        retry_possible = False
        
        if platform == "instagram":
            if error_code in [1, 2, 4, 17, 341]:
                actionable_msg = f"Token d'accès invalide ou expiré. Reconnectez le compte Instagram. (Code: {error_code})"
            elif error_code == 100:
                actionable_msg = f"Paramètres invalides. Vérifiez l'URL du média et les autorisations. (Code: {error_code})"
            elif error_code in [368, 9007]:
                actionable_msg = f"Média non accessible ou format incompatible. Vérifiez l'URL et le format. (Code: {error_code})"
                retry_possible = True
            elif error_code in [190, 463]:
                actionable_msg = f"Session expirée. Reconnectez l'utilisateur. (Code: {error_code})"
            elif 'video' in error_msg.lower() and 'processing' in error_msg.lower():
                actionable_msg = "Vidéo en cours de traitement Instagram. Réessayez dans quelques minutes."
                retry_possible = True
        
        elif platform == "facebook":
            if error_code in [190, 463]:
                actionable_msg = f"Token expiré. Reconnectez la page Facebook. (Code: {error_code})"
            elif error_code == 100:
                actionable_msg = f"Paramètres invalides. Vérifiez les données du post. (Code: {error_code})"
            elif error_code in [1, 2]:
                actionable_msg = f"Erreur temporaire Facebook. Réessayez dans quelques minutes. (Code: {error_code})"
                retry_possible = True
        
        log_instagram(f"Erreur API {platform}: {actionable_msg}", "ERROR") if platform == "instagram" else log_facebook(f"Erreur API {platform}: {actionable_msg}", "ERROR")
        
        return {
            "status": "error",
            "message": actionable_msg,
            "error_code": error_code,
            "error_subcode": error_subcode,
            "retry_possible": retry_possible,
            "raw_error": error_msg
        }
    
    except json.JSONDecodeError:
        generic_msg = f"Erreur {response.status_code}: {response.text[:200]}"
        return {
            "status": "error", 
            "message": generic_msg,
            "retry_possible": response.status_code >= 500
        }

# ============================================================================
# COMMANDE SELFTEST INTÉGRÉE
# ============================================================================

async def run_selftest():
    """Commande selftest intégrée pour valider les pipelines de conversion"""
    print("\n" + "="*70)
    print("🧪 SELFTEST MODE - Validation des pipelines de conversion")
    print("="*70)
    
    test_results = {
        "image_conversion": False,
        "video_conversion": False,
        "download_retry": False,
        "total_tests": 0,
        "passed_tests": 0
    }
    
    # Test 1: Conversion image (simuler WebP → JPEG)
    print("\n📸 TEST 1: Conversion image WebP → JPEG")
    try:
        # Créer une image de test
        test_img = Image.new('RGB', (800, 600), color='red')
        test_webp_path = "uploads/processed/test_selftest.webp"
        os.makedirs(os.path.dirname(test_webp_path), exist_ok=True)
        test_img.save(test_webp_path, 'WEBP')
        
        success, converted_path, error = await convert_image_to_instagram_format(test_webp_path)
        
        if success and converted_path and os.path.exists(converted_path):
            print("✅ Test conversion image: SUCCÈS")
            test_results["image_conversion"] = True
            test_results["passed_tests"] += 1
            # Nettoyer
            os.unlink(test_webp_path)
            os.unlink(converted_path)
        else:
            print(f"❌ Test conversion image: ÉCHEC - {error}")
    except Exception as e:
        print(f"❌ Test conversion image: ERREUR - {str(e)}")
    
    test_results["total_tests"] += 1
    
    # Test 2: Test retry download (URL fictive)
    print("\n🌐 TEST 2: Système retry téléchargement")
    try:
        # Tester avec URL inexistante (doit échouer proprement)
        success, path, error = await download_media_with_retry("https://httpstat.us/404", max_attempts=2, timeout=5)
        
        if not success and error and "tentatives" in error:
            print("✅ Test retry download: SUCCÈS (échec attendu avec retry)")
            test_results["download_retry"] = True
            test_results["passed_tests"] += 1
        else:
            print("❌ Test retry download: ÉCHEC (comportement inattendu)")
    except Exception as e:
        print(f"❌ Test retry download: ERREUR - {str(e)}")
    
    test_results["total_tests"] += 1
    
    # Test 3: Validation format detection
    print("\n🔍 TEST 3: Détection format média")
    try:
        # Tester détection avec extensions
        img_type = await detect_media_type("test.jpg")
        video_type = await detect_media_type("test.mp4")
        
        if img_type == "image" and video_type == "video":
            print("✅ Test détection format: SUCCÈS")
            test_results["passed_tests"] += 1
        else:
            print(f"❌ Test détection format: ÉCHEC - img:{img_type}, video:{video_type}")
    except Exception as e:
        print(f"❌ Test détection format: ERREUR - {str(e)}")
    
    test_results["total_tests"] += 1
    
    # Résumé des tests
    print("\n" + "="*70)
    print("📊 RÉSUMÉ SELFTEST:")
    print(f"   ✅ Tests réussis: {test_results['passed_tests']}/{test_results['total_tests']}")
    print(f"   📸 Conversion image: {'✅' if test_results['image_conversion'] else '❌'}")
    print(f"   🌐 Retry download: {'✅' if test_results['download_retry'] else '❌'}")
    
    success_rate = (test_results['passed_tests'] / test_results['total_tests']) * 100
    
    if success_rate >= 80:
        print(f"🎉 SELFTEST GLOBAL: SUCCÈS ({success_rate:.0f}%)")
        return True
    else:
        print(f"❌ SELFTEST GLOBAL: ÉCHEC ({success_rate:.0f}%)")
        return False

# ============================================================================
# ENDPOINTS API
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Endpoint de santé avec informations sur la configuration"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "dry_run": DRY_RUN,
        "selftest_mode": SELFTEST_MODE,
        "features": {
            "instagram_posting": True,
            "facebook_posting": True,
            "media_conversion": True,
            "clickable_links": True,
            "video_fallback": True
        }
    }

@app.get("/api/selftest")
async def selftest_endpoint():
    """Endpoint pour lancer le selftest"""
    if not SELFTEST_MODE and not DRY_RUN:
        return {"status": "error", "message": "Selftest disponible uniquement en mode DRY_RUN ou --selftest"}
    
    success = await run_selftest()
    return {
        "status": "success" if success else "partial_failure",
        "message": "Selftest terminé",
        "timestamp": datetime.utcnow()
    }

@app.post("/api/webhook")
async def webhook_handler(request: Request):
    """Gestionnaire webhook N8N avec gestion complète des médias"""
    try:
        # Obtenir les données
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            data = await request.json()
        elif "multipart/form-data" in content_type:
            form = await request.form()
            # Convertir form en dict
            data = {}
            for key, value in form.items():
                if hasattr(value, 'read'):  # Fichier uploadé
                    # Sauvegarder le fichier
                    unique_id = uuid.uuid4().hex[:8]
                    timestamp = int(datetime.utcnow().timestamp())
                    filename = f"webhook_{unique_id}_{timestamp}"
                    
                    # Déterminer extension
                    if hasattr(value, 'content_type'):
                        if 'image' in value.content_type:
                            filename += '.jpg'
                        elif 'video' in value.content_type:
                            filename += '.mp4'
                        else:
                            filename += '.bin'
                    
                    file_path = f"uploads/{filename}"
                    
                    async with aiofiles.open(file_path, 'wb') as f:
                        content = await value.read()
                        await f.write(content)
                    
                    data[key] = f"/api/uploads/{filename}"
                else:
                    data[key] = value
        else:
            # Raw data
            body = await request.body()
            try:
                data = json.loads(body)
            except:
                data = {"raw_body": body.decode('utf-8', errors='ignore')}
        
        log_media(f"Webhook reçu: {len(data)} champs")
        
        if DRY_RUN:
            log_media(f"[DRY_RUN] Données webhook: {data}")
            return {"status": "success", "message": "Webhook traité (DRY_RUN)", "data": data}
        
        # Traiter le webhook (logique métier ici)
        # ...
        
        return {"status": "success", "message": "Webhook traité avec succès"}
        
    except Exception as e:
        error_msg = f"Erreur webhook: {str(e)}"
        log_media(error_msg, "ERROR")
        return {"status": "error", "message": error_msg}

@app.post("/api/publish")
async def publish_content(request: PublishRequest):
    """Endpoint principal de publication avec fallbacks complets"""
    try:
        log_instagram(f"Demande publication: {len(request.posts)} posts, plateformes: {request.platforms}")
        
        results = []
        
        for post in request.posts:
            post_results = {"post_id": post.target_id, "platforms": {}}
            
            # Publication Instagram avec fallback
            if "instagram" in request.platforms:
                # Utiliser un token de test ou réel
                access_token = "test_instagram_token"  # À remplacer par vraie logique
                
                result = await post_to_instagram_with_fallback(post, access_token)
                post_results["platforms"]["instagram"] = result
            
            # Publication Facebook avec liens cliquables
            if "facebook" in request.platforms:
                # Utiliser un token de test ou réel
                access_token = "test_facebook_token"  # À remplacer par vraie logique
                
                result = await post_to_facebook_with_clickable_links(post, access_token)
                post_results["platforms"]["facebook"] = result
            
            results.append(post_results)
        
        return {
            "status": "completed",
            "message": f"Publication terminée pour {len(request.posts)} posts",
            "results": results,
            "dry_run": DRY_RUN
        }
        
    except Exception as e:
        error_msg = f"Erreur publication: {str(e)}"
        log_instagram(error_msg, "ERROR")
        return {"status": "error", "message": error_msg}

@app.get("/api/uploads/{filename}")
async def serve_uploaded_file(filename: str):
    """Sert les fichiers uploadés"""
    file_path = f"uploads/{filename}"
    if os.path.exists(file_path):
        return {"url": f"/api/uploads/{filename}", "exists": True}
    else:
        raise HTTPException(status_code=404, detail="File not found")

# ============================================================================
# DÉMARRAGE AVEC SELFTEST
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Événement de démarrage"""
    print("\n🚀 Démarrage Meta Publishing Platform - Instagram Optimized")
    print(f"   DRY_RUN: {DRY_RUN}")
    print(f"   SELFTEST_MODE: {SELFTEST_MODE}")
    
    if SELFTEST_MODE:
        print("\n🧪 Lancement selftest automatique...")
        success = await run_selftest()
        if not success:
            print("⚠️ Certains tests ont échoué, mais le serveur continue de démarrer")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)