# Webhook Handler - Traitement des données N8N
import os
import json
import uuid
import aiofiles
from typing import Dict, Optional, Union
from datetime import datetime
from fastapi import UploadFile
import mimetypes
from pathlib import Path

class WebhookHandler:
    def __init__(self):
        self.upload_dir = "/app/backend/uploads"
        os.makedirs(self.upload_dir, exist_ok=True)
        
    def log_webhook(self, message: str, level: str = "INFO"):
        """Logging spécialisé pour les webhooks"""
        icons = {"INFO": "🔗", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "UPLOAD": "📤"}
        icon = icons.get(level.upper(), "🔗")
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{icon} [{timestamp}] [WEBHOOK] {message}")
    
    async def save_uploaded_file(self, file: UploadFile, custom_filename: str = None) -> Dict:
        """Sauvegarde le fichier uploadé et retourne les informations"""
        try:
            # Générer un nom de fichier unique
            file_extension = ""
            if file.filename:
                file_extension = Path(file.filename).suffix
            
            if custom_filename:
                filename = f"{custom_filename}{file_extension}"
            else:
                filename = f"{uuid.uuid4().hex[:8]}_{file.filename}" if file.filename else f"{uuid.uuid4().hex[:8]}{file_extension}"
            
            file_path = os.path.join(self.upload_dir, filename)
            
            # Sauvegarder le fichier
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Obtenir les informations du fichier
            file_size = len(content)
            mime_type = mimetypes.guess_type(file_path)[0] or file.content_type
            
            file_info = {
                "filename": filename,
                "original_filename": file.filename,
                "file_path": file_path,
                "file_size": file_size,
                "mime_type": mime_type,
                "is_image": mime_type and mime_type.startswith("image/"),
                "is_video": mime_type and mime_type.startswith("video/"),
                "created_at": datetime.now().isoformat()
            }
            
            self.log_webhook(f"Fichier sauvegardé: {filename} ({file_size} bytes)", "SUCCESS")
            return file_info
            
        except Exception as e:
            self.log_webhook(f"Erreur sauvegarde fichier: {str(e)}", "ERROR")
            raise e
    
    def parse_json_data(self, json_data: str) -> Dict:
        """Parse et valide les données JSON du webhook"""
        try:
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
            
            # Validation des champs requis
            required_fields = ["store", "message"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                raise ValueError(f"Champs manquants: {missing_fields}")
            
            # Normaliser les données
            normalized_data = {
                "store": data.get("store", "").lower(),
                "message": data.get("message", ""),
                "product_url": data.get("product_url", ""),
                "platforms": data.get("platforms", ["facebook", "instagram"]),
                "publish_immediately": data.get("publish_immediately", True),
                "metadata": data.get("metadata", {})
            }
            
            # Valider le store
            valid_stores = ["gizmobbs", "logicantiq", "outdoor"]
            if normalized_data["store"] not in valid_stores:
                raise ValueError(f"Store invalide. Stores valides: {valid_stores}")
            
            # Valider les plateformes
            valid_platforms = ["facebook", "instagram"]
            invalid_platforms = [p for p in normalized_data["platforms"] if p not in valid_platforms]
            if invalid_platforms:
                raise ValueError(f"Plateformes invalides: {invalid_platforms}")
            
            self.log_webhook(f"Données JSON validées pour store: {normalized_data['store']}", "SUCCESS")
            return normalized_data
            
        except json.JSONDecodeError as e:
            self.log_webhook(f"Erreur parsing JSON: {str(e)}", "ERROR")
            raise ValueError(f"JSON invalide: {str(e)}")
        except Exception as e:
            self.log_webhook(f"Erreur validation données: {str(e)}", "ERROR")
            raise e
    
    async def process_webhook_data(self, json_data: str, file: Optional[UploadFile] = None) -> Dict:
        """Traite complètement les données du webhook"""
        try:
            webhook_id = uuid.uuid4().hex[:8]
            self.log_webhook(f"Début traitement webhook {webhook_id}", "INFO")
            
            # Parser les données JSON
            parsed_data = self.parse_json_data(json_data)
            
            # Traiter le fichier si fourni
            file_info = None
            if file and file.filename:
                custom_filename = f"webhook_{webhook_id}_{parsed_data['store']}"
                file_info = await self.save_uploaded_file(file, custom_filename)
                
                self.log_webhook(f"Type de média détecté: {'Image' if file_info['is_image'] else 'Vidéo' if file_info['is_video'] else 'Autre'}", "INFO")
            
            # Créer la structure de données complète
            webhook_data = {
                "webhook_id": webhook_id,
                "received_at": datetime.now().isoformat(),
                "data": parsed_data,
                "file": file_info,
                "processing_status": "received",
                "publication_results": {}
            }
            
            self.log_webhook(f"Webhook {webhook_id} traité avec succès", "SUCCESS")
            return webhook_data
            
        except Exception as e:
            self.log_webhook(f"Erreur traitement webhook: {str(e)}", "ERROR")
            raise e
    
    def determine_publication_type(self, webhook_data: Dict) -> str:
        """Détermine le type de publication basé sur le fichier"""
        file_info = webhook_data.get("file")
        
        if not file_info:
            return "text_only"
        elif file_info.get("is_image"):
            return "image_post"
        elif file_info.get("is_video"):
            return "video_post"
        else:
            return "unknown_media"
    
    async def prepare_publication_data(self, webhook_data: Dict) -> Dict:
        """Prépare les données pour la publication sur les réseaux sociaux"""
        try:
            publication_type = self.determine_publication_type(webhook_data)
            data = webhook_data["data"]
            file_info = webhook_data.get("file")
            
            # Données de base pour la publication
            publication_data = {
                "store": data["store"],
                "message": data["message"],
                "product_url": data["product_url"],
                "platforms": data["platforms"],
                "publication_type": publication_type,
                "webhook_id": webhook_data["webhook_id"]
            }
            
            # Ajouter les informations spécifiques au média
            if file_info:
                if publication_type == "image_post":
                    # Pour les images, on peut utiliser directement le chemin local ou uploader sur FTP
                    publication_data["image_path"] = file_info["file_path"]
                    publication_data["image_url"] = None  # Sera défini après upload FTP si nécessaire
                elif publication_type == "video_post":
                    # Pour les vidéos, on doit uploader sur FTP
                    publication_data["video_path"] = file_info["file_path"]
                    publication_data["video_url"] = None  # Sera défini après upload FTP
                
                publication_data["file_info"] = file_info
            
            self.log_webhook(f"Données de publication préparées: {publication_type}", "SUCCESS")
            return publication_data
            
        except Exception as e:
            self.log_webhook(f"Erreur préparation publication: {str(e)}", "ERROR")
            raise e

# Instance globale
webhook_handler = WebhookHandler()