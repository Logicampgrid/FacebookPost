#!/usr/bin/env python3
"""
Script de publication automatique sur Instagram
Utilise l'API Graph de Meta pour publier images et vidéos automatiquement

Usage:
    python instagram_auto_publisher.py --file "image.webp" --caption "Mon post" --hashtags "#photo #art"
    python instagram_auto_publisher.py --batch /path/to/media --caption "Description générale"
"""

import os
import sys
import argparse
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
import json
import uuid
import tempfile
import subprocess
import mimetypes
import shutil

# Imports pour traitement d'images et vidéos
from PIL import Image, ExifTags
import requests
import motor.motor_asyncio
from dotenv import load_dotenv

# Configuration
load_dotenv()

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/instagram_publisher.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.meta_posts

# Configuration Meta
FACEBOOK_GRAPH_URL = os.getenv("FACEBOOK_GRAPH_URL", "https://graph.facebook.com/v18.0")

# Configuration Instagram Berger Blanc Suisse
BERGER_BLANC_SUISSE_PAGE_ID = "61550969018046"  # ID de la page Facebook "Le Berger Blanc Suisse"

# Formats supportés
SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.avif', '.bmp', '.tiff'}
SUPPORTED_VIDEO_FORMATS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v'}
CONVERSION_FORMATS = {'.webp', '.heic', '.avif', '.bmp', '.tiff'}  # Formats à convertir

# Limitations Instagram
INSTAGRAM_MAX_IMAGE_SIZE = 1080  # pixels
INSTAGRAM_MIN_IMAGE_SIZE = 320   # pixels
INSTAGRAM_MAX_VIDEO_DURATION = 60  # secondes
INSTAGRAM_MAX_CREDITS = 10  # limite quotidienne


class InstagramPublisher:
    """Gestionnaire de publication automatique Instagram"""
    
    def __init__(self):
        self.session_stats = {
            'processed': 0,
            'published': 0,
            'errors': 0,
            'conversions': 0,
            'credits_used': 0,
            'published_posts': []
        }
        self.temp_files = []  # Pour cleanup
        
    async def initialize(self):
        """Initialise la connexion et récupère les tokens"""
        try:
            logger.info("🚀 Initialisation du publisher Instagram...")
            
            # Récupérer l'utilisateur avec accès Instagram
            user = await db.users.find_one({
                "facebook_access_token": {"$exists": True, "$ne": None}
            })
            
            if not user:
                raise Exception("Aucun utilisateur authentifié trouvé")
            
            logger.info(f"👤 Utilisateur trouvé: {user.get('name')}")
            
            # Récupérer le token Instagram pour la page Berger Blanc Suisse
            instagram_account = await self.get_berger_blanc_suisse_instagram(user)
            if not instagram_account:
                raise Exception("Compte Instagram Berger Blanc Suisse non trouvé")
            
            self.user = user
            self.instagram_account = instagram_account
            
            logger.info(f"📱 Compte Instagram connecté: {instagram_account.get('name', 'N/A')}")
            logger.info("✅ Initialisation réussie")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur d'initialisation: {str(e)}")
            return False
    
    async def get_berger_blanc_suisse_instagram(self, user: dict) -> Optional[dict]:
        """Récupère le compte Instagram de la page Berger Blanc Suisse"""
        try:
            # Chercher dans les pages personnelles
            for page in user.get("facebook_pages", []):
                if page.get("id") == BERGER_BLANC_SUISSE_PAGE_ID:
                    return await self.get_instagram_for_page(page, user.get("facebook_access_token"))
            
            # Chercher dans les business managers
            for bm in user.get("business_managers", []):
                for page in bm.get("pages", []):
                    if page.get("id") == BERGER_BLANC_SUISSE_PAGE_ID:
                        return await self.get_instagram_for_page(page, page.get("access_token") or user.get("facebook_access_token"))
            
            logger.error(f"❌ Page Berger Blanc Suisse ({BERGER_BLANC_SUISSE_PAGE_ID}) non trouvée")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche Instagram: {str(e)}")
            return None
    
    async def get_instagram_for_page(self, page: dict, access_token: str) -> Optional[dict]:
        """Récupère le compte Instagram connecté à une page Facebook"""
        try:
            response = requests.get(
                f"{FACEBOOK_GRAPH_URL}/{page['id']}",
                params={
                    "access_token": access_token,
                    "fields": "instagram_business_account,name"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                page_data = response.json()
                if "instagram_business_account" in page_data:
                    return {
                        "id": page_data["instagram_business_account"]["id"],
                        "access_token": access_token,
                        "page_name": page_data.get("name"),
                        "page_id": page["id"]
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération Instagram pour page {page.get('name')}: {str(e)}")
            return None
    
    def detect_media_type(self, file_path: str) -> Tuple[str, str]:
        """
        Détecte le type de média et son format
        Returns: (media_type, file_format) où media_type = 'image' ou 'video'
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        # Détection par extension
        if extension in SUPPORTED_IMAGE_FORMATS:
            media_type = 'image'
        elif extension in SUPPORTED_VIDEO_FORMATS:
            media_type = 'video'
        else:
            # Tentative de détection par contenu
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type:
                if mime_type.startswith('image/'):
                    media_type = 'image'
                elif mime_type.startswith('video/'):
                    media_type = 'video'
                else:
                    raise ValueError(f"Type de fichier non supporté: {extension}")
            else:
                raise ValueError(f"Impossible de détecter le type: {extension}")
        
        logger.info(f"🔍 Type détecté: {media_type} ({extension})")
        return media_type, extension
    
    async def convert_image(self, input_path: str, output_path: str) -> bool:
        """Convertit une image au format compatible Instagram"""
        try:
            logger.info(f"🔄 Conversion image: {Path(input_path).name}")
            
            with Image.open(input_path) as img:
                # Informations image originale
                original_format = img.format
                original_size = img.size
                original_mode = img.mode
                
                logger.info(f"📊 Original: {original_format}, {original_size}, {original_mode}")
                
                # Conversion en RGB pour JPEG
                if img.mode in ('RGBA', 'LA', 'P'):
                    logger.info("🔄 Conversion transparence → fond blanc")
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = rgb_img
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Correction orientation EXIF
                try:
                    exif = img._getexif()
                    if exif is not None:
                        for tag, value in exif.items():
                            if tag in ExifTags.TAGS and ExifTags.TAGS[tag] == 'Orientation':
                                if value == 3:
                                    img = img.rotate(180, expand=True)
                                    logger.info("🔄 Rotation EXIF: 180°")
                                elif value == 6:
                                    img = img.rotate(270, expand=True)
                                    logger.info("🔄 Rotation EXIF: 270°")
                                elif value == 8:
                                    img = img.rotate(90, expand=True)
                                    logger.info("🔄 Rotation EXIF: 90°")
                                break
                except Exception as e:
                    logger.warning(f"⚠️ Pas de données EXIF: {str(e)}")
                
                # Redimensionnement pour Instagram
                max_dimension = INSTAGRAM_MAX_IMAGE_SIZE
                if img.width > max_dimension or img.height > max_dimension:
                    original_dimensions = (img.width, img.height)
                    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                    logger.info(f"📐 Redimensionnement: {original_dimensions} → {img.size}")
                
                # Vérification taille minimale
                if img.width < INSTAGRAM_MIN_IMAGE_SIZE or img.height < INSTAGRAM_MIN_IMAGE_SIZE:
                    logger.warning(f"⚠️ Image trop petite: {img.size}, minimum {INSTAGRAM_MIN_IMAGE_SIZE}px")
                
                # Sauvegarde optimisée
                img.save(output_path, format='JPEG', quality=95, optimize=True)
                
                converted_size = os.path.getsize(output_path)
                logger.info(f"✅ Image convertie: {converted_size / (1024*1024):.2f}MB")
                
                self.session_stats['conversions'] += 1
                return True
                
        except Exception as e:
            logger.error(f"❌ Erreur conversion image: {str(e)}")
            return False
    
    async def convert_video(self, input_path: str, output_path: str) -> bool:
        """Convertit une vidéo au format MP4 compatible Instagram"""
        try:
            logger.info(f"🔄 Conversion vidéo: {Path(input_path).name}")
            
            # Commande FFmpeg optimisée pour Instagram
            cmd = [
                'ffmpeg', '-y', '-i', input_path,
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                '-c:a', 'aac', '-b:a', '128k',
                '-movflags', '+faststart',
                '-vf', f'scale=1080:1080:force_original_aspect_ratio=decrease,pad=1080:1080:(ow-iw)/2:(oh-ih)/2:black',
                '-t', str(INSTAGRAM_MAX_VIDEO_DURATION),  # Limite 60s
                '-r', '30',  # 30 FPS max
                output_path
            ]
            
            logger.info("⚙️ Lancement FFmpeg...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_path):
                converted_size = os.path.getsize(output_path)
                logger.info(f"✅ Vidéo convertie: {converted_size / (1024*1024):.2f}MB")
                self.session_stats['conversions'] += 1
                return True
            else:
                logger.error(f"❌ FFmpeg échoué: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("⏰ Timeout conversion vidéo (>5min)")
            return False
        except FileNotFoundError:
            logger.error("❌ FFmpeg non trouvé. Installez-le: apt-get install ffmpeg")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur conversion vidéo: {str(e)}")
            return False
    
    async def prepare_media(self, file_path: str) -> Optional[str]:
        """Prépare un fichier média pour Instagram (conversion si nécessaire)"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"❌ Fichier introuvable: {file_path}")
                return None
            
            # Détection du type
            media_type, extension = self.detect_media_type(str(file_path))
            
            # Si le fichier est déjà compatible, le retourner tel quel
            if media_type == 'image' and extension == '.jpg':
                logger.info("✅ Image déjà compatible (JPEG)")
                return str(file_path)
            elif media_type == 'video' and extension == '.mp4':
                logger.info("✅ Vidéo déjà compatible (MP4)")
                return str(file_path)
            
            # Sinon, conversion nécessaire
            timestamp = int(datetime.now().timestamp())
            unique_id = uuid.uuid4().hex[:8]
            
            if media_type == 'image':
                output_path = f"/tmp/converted_img_{timestamp}_{unique_id}.jpg"
                if await self.convert_image(str(file_path), output_path):
                    self.temp_files.append(output_path)
                    return output_path
            elif media_type == 'video':
                output_path = f"/tmp/converted_vid_{timestamp}_{unique_id}.mp4"
                if await self.convert_video(str(file_path), output_path):
                    self.temp_files.append(output_path)
                    return output_path
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur préparation média: {str(e)}")
            return None
    
    async def publish_to_instagram(self, media_path: str, caption: str, media_type: str) -> Optional[str]:
        """Publie un média sur Instagram avec fallbacks"""
        try:
            # Vérification limite de crédits
            if self.session_stats['credits_used'] >= INSTAGRAM_MAX_CREDITS:
                logger.error(f"❌ Limite de crédits atteinte ({INSTAGRAM_MAX_CREDITS})")
                return None
            
            logger.info(f"📤 Publication Instagram: {Path(media_path).name}")
            
            instagram_id = self.instagram_account["id"]
            access_token = self.instagram_account["access_token"]
            
            # Lecture du fichier
            with open(media_path, 'rb') as f:
                media_content = f.read()
            
            # Étape 1: Créer le conteneur média
            container_data = {
                "access_token": access_token,
                "caption": caption,
                "media_type": "VIDEO" if media_type == 'video' else "IMAGE"
            }
            
            files = {
                'source': (
                    f'media.{media_path.split(".")[-1]}',
                    media_content,
                    f'{media_type}/{"mp4" if media_type == "video" else "jpeg"}'
                )
            }
            
            logger.info("📱 Création conteneur Instagram...")
            
            # Tentative d'upload direct
            for attempt in range(3):
                try:
                    response = requests.post(
                        f"{FACEBOOK_GRAPH_URL}/{instagram_id}/media",
                        data=container_data,
                        files=files,
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        container_result = response.json()
                        container_id = container_result.get("id")
                        logger.info(f"✅ Conteneur créé: {container_id}")
                        
                        # Attente traitement (surtout pour vidéos)
                        if media_type == 'video':
                            logger.info("⏰ Attente traitement vidéo...")
                            await asyncio.sleep(15)
                        else:
                            await asyncio.sleep(5)
                        
                        # Étape 2: Publier le conteneur
                        return await self.publish_container(instagram_id, container_id, access_token)
                    
                    else:
                        error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                        logger.warning(f"⚠️ Tentative {attempt + 1}/3 échouée: {error_data}")
                        
                        if attempt < 2:
                            await asyncio.sleep((attempt + 1) * 2)
                            continue
                        else:
                            logger.error(f"❌ Échec création conteneur après 3 tentatives")
                            return None
                            
                except Exception as e:
                    logger.warning(f"⚠️ Erreur tentative {attempt + 1}: {str(e)}")
                    if attempt < 2:
                        await asyncio.sleep(3)
                        continue
                    else:
                        logger.error(f"❌ Échec publication après 3 tentatives")
                        return None
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur publication Instagram: {str(e)}")
            return None
    
    async def publish_container(self, instagram_id: str, container_id: str, access_token: str) -> Optional[str]:
        """Publie un conteneur Instagram"""
        try:
            publish_data = {
                "access_token": access_token,
                "creation_id": container_id
            }
            
            logger.info(f"📱 Publication conteneur: {container_id}")
            
            for attempt in range(3):
                try:
                    response = requests.post(
                        f"{FACEBOOK_GRAPH_URL}/{instagram_id}/media_publish",
                        data=publish_data,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        post_id = result.get("id")
                        
                        logger.info(f"🎉 Publication réussie: {post_id}")
                        self.session_stats['credits_used'] += 1
                        self.session_stats['published'] += 1
                        
                        return post_id
                    else:
                        error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                        logger.warning(f"⚠️ Publication tentative {attempt + 1}/3: {error_data}")
                        
                        if attempt < 2:
                            await asyncio.sleep((attempt + 1) * 3)
                            continue
                        
                except Exception as e:
                    logger.warning(f"⚠️ Erreur publication tentative {attempt + 1}: {str(e)}")
                    if attempt < 2:
                        await asyncio.sleep(5)
                        continue
            
            logger.error("❌ Échec publication après 3 tentatives")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur publication conteneur: {str(e)}")
            return None
    
    async def publish_single_file(self, file_path: str, caption: str = "", hashtags: str = "") -> Dict:
        """Publie un seul fichier sur Instagram"""
        result = {
            'success': False,
            'file_path': file_path,
            'post_id': None,
            'error': None,
            'media_type': None,
            'converted': False
        }
        
        try:
            self.session_stats['processed'] += 1
            
            logger.info(f"🎯 Publication: {Path(file_path).name}")
            
            # Détection du type
            media_type, extension = self.detect_media_type(file_path)
            result['media_type'] = media_type
            
            # Préparation du média
            prepared_path = await self.prepare_media(file_path)
            if not prepared_path:
                result['error'] = "Échec préparation du média"
                self.session_stats['errors'] += 1
                return result
            
            result['converted'] = (prepared_path != file_path)
            
            # Composition du caption final
            final_caption = self.compose_caption(caption, hashtags)
            
            # Publication
            post_id = await self.publish_to_instagram(prepared_path, final_caption, media_type)
            
            if post_id:
                result['success'] = True
                result['post_id'] = post_id
                self.session_stats['published_posts'].append({
                    'file': Path(file_path).name,
                    'post_id': post_id,
                    'type': media_type,
                    'converted': result['converted']
                })
                logger.info(f"✅ Publication réussie: {post_id}")
            else:
                result['error'] = "Échec publication Instagram"
                self.session_stats['errors'] += 1
                logger.error(f"❌ Échec publication: {Path(file_path).name}")
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            self.session_stats['errors'] += 1
            logger.error(f"❌ Erreur publication {Path(file_path).name}: {str(e)}")
            return result
    
    async def publish_batch(self, directory: str, caption: str = "", hashtags: str = "") -> List[Dict]:
        """Publie tous les médias d'un dossier"""
        results = []
        
        try:
            directory_path = Path(directory)
            if not directory_path.exists() or not directory_path.is_dir():
                logger.error(f"❌ Dossier introuvable: {directory}")
                return results
            
            # Recherche des fichiers médias
            media_files = []
            for ext in SUPPORTED_IMAGE_FORMATS.union(SUPPORTED_VIDEO_FORMATS):
                media_files.extend(directory_path.glob(f"*{ext}"))
                media_files.extend(directory_path.glob(f"*{ext.upper()}"))
            
            if not media_files:
                logger.warning(f"⚠️ Aucun fichier média trouvé dans: {directory}")
                return results
            
            logger.info(f"📁 Traitement par lots: {len(media_files)} fichiers trouvés")
            
            # Publication de chaque fichier
            for file_path in sorted(media_files):
                # Vérification limite de crédits
                if self.session_stats['credits_used'] >= INSTAGRAM_MAX_CREDITS:
                    logger.warning(f"⚠️ Limite de crédits atteinte, arrêt du traitement")
                    break
                
                result = await self.publish_single_file(str(file_path), caption, hashtags)
                results.append(result)
                
                # Pause entre publications pour éviter rate limiting
                if result['success']:
                    logger.info("⏰ Pause 30s entre publications...")
                    await asyncio.sleep(30)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement par lots: {str(e)}")
            return results
    
    def compose_caption(self, caption: str, hashtags: str) -> str:
        """Compose le caption final avec hashtags"""
        final_caption = caption.strip() if caption else ""
        
        if hashtags:
            hashtags_clean = hashtags.strip()
            if not hashtags_clean.startswith('#'):
                hashtags_clean = '#' + hashtags_clean.replace(' ', ' #')
            
            if final_caption:
                final_caption += f"\n\n{hashtags_clean}"
            else:
                final_caption = hashtags_clean
        
        # Limitation Instagram (2200 caractères)
        if len(final_caption) > 2200:
            final_caption = final_caption[:2197] + "..."
            logger.warning("⚠️ Caption tronqué à 2200 caractères")
        
        return final_caption
    
    def print_session_report(self):
        """Affiche le rapport de session"""
        print("\n" + "="*60)
        print("📊 RAPPORT DE SESSION INSTAGRAM")
        print("="*60)
        print(f"📁 Fichiers traités:     {self.session_stats['processed']}")
        print(f"✅ Publications réussies: {self.session_stats['published']}")
        print(f"❌ Erreurs:              {self.session_stats['errors']}")
        print(f"🔄 Conversions:          {self.session_stats['conversions']}")
        print(f"💳 Crédits utilisés:     {self.session_stats['credits_used']}/{INSTAGRAM_MAX_CREDITS}")
        
        if self.session_stats['published_posts']:
            print(f"\n📋 POSTS PUBLIÉS:")
            for post in self.session_stats['published_posts']:
                converted_badge = " 🔄" if post['converted'] else ""
                print(f"  • {post['file']} → {post['post_id']} ({post['type']}){converted_badge}")
                print(f"    🔗 https://instagram.com/p/{post['post_id']}")
        
        print("="*60)
    
    def cleanup(self):
        """Nettoie les fichiers temporaires"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    logger.info(f"🧹 Fichier temporaire supprimé: {temp_file}")
            except Exception as e:
                logger.warning(f"⚠️ Erreur suppression {temp_file}: {str(e)}")


async def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description='Publication automatique sur Instagram @berger_blanc_suisse',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  
  Publication d'un fichier unique:
    python instagram_auto_publisher.py --file "photo.webp" --caption "Belle photo!" --hashtags "#nature #photo"
  
  Publication par lots:
    python instagram_auto_publisher.py --batch "/path/to/images" --caption "Collection photos"
  
  Formats supportés:
    Images: .jpg, .jpeg, .png, .webp, .heic, .avif, .bmp, .tiff
    Vidéos: .mp4, .mov, .avi, .mkv, .webm, .m4v
  
  Conversions automatiques:
    .webp, .heic, .avif → .jpg
    .mov, .avi, .mkv → .mp4
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', '-f', help='Chemin vers un fichier média unique')
    group.add_argument('--batch', '-b', help='Dossier contenant les médias à publier')
    
    parser.add_argument('--caption', '-c', default='', help='Description du post')
    parser.add_argument('--hashtags', '-t', default='', help='Hashtags (ex: "#photo #art")')
    parser.add_argument('--dry-run', action='store_true', help='Test sans publication réelle')
    
    args = parser.parse_args()
    
    # Initialisation
    publisher = InstagramPublisher()
    
    try:
        logger.info("🚀 Lancement du publisher Instagram")
        
        if not await publisher.initialize():
            logger.error("❌ Échec d'initialisation")
            return 1
        
        if args.dry_run:
            logger.info("🧪 MODE TEST - Aucune publication réelle")
        
        # Publication
        if args.file:
            # Publication fichier unique
            if not args.dry_run:
                result = await publisher.publish_single_file(args.file, args.caption, args.hashtags)
                if not result['success']:
                    logger.error(f"❌ Échec publication: {result['error']}")
                    return 1
            else:
                logger.info(f"🧪 TEST: Publication de {args.file}")
                media_type, ext = publisher.detect_media_type(args.file)
                prepared = await publisher.prepare_media(args.file)
                if prepared:
                    logger.info(f"✅ TEST: Média préparé avec succès")
                else:
                    logger.error(f"❌ TEST: Échec préparation média")
        
        elif args.batch:
            # Publication par lots
            if not args.dry_run:
                results = await publisher.publish_batch(args.batch, args.caption, args.hashtags)
                if not any(r['success'] for r in results):
                    logger.error("❌ Aucune publication réussie")
                    return 1
            else:
                logger.info(f"🧪 TEST: Publication par lots de {args.batch}")
                batch_path = Path(args.batch)
                if batch_path.exists():
                    media_files = []
                    for ext in SUPPORTED_IMAGE_FORMATS.union(SUPPORTED_VIDEO_FORMATS):
                        media_files.extend(batch_path.glob(f"*{ext}"))
                    logger.info(f"🧪 TEST: {len(media_files)} fichiers trouvés")
        
        # Rapport final
        publisher.print_session_report()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("⏹️ Arrêt demandé par l'utilisateur")
        return 0
    except Exception as e:
        logger.error(f"💥 Erreur fatale: {str(e)}")
        return 1
    finally:
        publisher.cleanup()


if __name__ == "__main__":
    # Vérification des dépendances
    try:
        import PIL
        import motor
        import requests
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("📦 Installation: pip install Pillow motor requests python-dotenv")
        sys.exit(1)
    
    # Création du dossier de logs
    os.makedirs('/app/logs', exist_ok=True)
    
    # Lancement
    exit_code = asyncio.run(main())
    sys.exit(exit_code)