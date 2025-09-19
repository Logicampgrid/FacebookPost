#!/usr/bin/env python3
"""
FOLDER WATCHER - Surveillance automatique des dossiers
Surveille les dossiers de téléchargement et déclenche automatiquement
la publication dès qu'un nouveau fichier est ajouté
"""

import os
import time
import asyncio
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import json

from poster_media_enhanced import STORES_CONFIG, log_poster, poster_media_enhanced

class MediaFileHandler(FileSystemEventHandler):
    """Gestionnaire d'événements pour les fichiers média"""
    
    def __init__(self, store_name: str, api_base_url: str = "http://localhost:8001"):
        self.store_name = store_name
        self.store_config = STORES_CONFIG[store_name]
        self.api_base_url = api_base_url
        self.processing_files: Set[str] = set()
        self.last_processed: Dict[str, float] = {}
        
        # Extensions supportées
        self.supported_extensions = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".mp4", ".mov"}
        
        # Délai pour éviter les déclenchements multiples (en secondes)
        self.processing_delay = 5
        
    def is_media_file(self, file_path: str) -> bool:
        """Vérifie si le fichier est un média supporté"""
        return Path(file_path).suffix.lower() in self.supported_extensions
    
    def should_process_file(self, file_path: str) -> bool:
        """Détermine si le fichier doit être traité"""
        # Vérifier l'extension
        if not self.is_media_file(file_path):
            return False
        
        # Éviter le traitement multiple du même fichier
        if file_path in self.processing_files:
            return False
        
        # Éviter les déclenchements trop fréquents
        now = time.time()
        if file_path in self.last_processed:
            if now - self.last_processed[file_path] < self.processing_delay:
                return False
        
        return True
    
    def on_created(self, event):
        """Déclenché quand un nouveau fichier est créé"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        if not self.should_process_file(file_path):
            return
        
        log_poster(f"Nouveau fichier détecté: {os.path.basename(file_path)} (store: {self.store_name})", "INFO")
        
        # Marquer le fichier comme en cours de traitement
        self.processing_files.add(file_path)
        self.last_processed[file_path] = time.time()
        
        # Lancer le traitement en arrière-plan
        threading.Thread(
            target=self.process_file_async,
            args=(file_path,),
            daemon=True
        ).start()
    
    def on_moved(self, event):
        """Déclenché quand un fichier est déplacé"""
        if event.is_directory:
            return
        
        # Traiter comme un nouveau fichier
        self.on_created(type('Event', (), {'src_path': event.dest_path, 'is_directory': False})())
    
    def process_file_async(self, file_path: str):
        """Traite un fichier de manière asynchrone"""
        try:
            # Attendre que le fichier soit complètement écrit
            self.wait_for_file_complete(file_path)
            
            log_poster(f"Traitement automatique: {os.path.basename(file_path)}", "INFO")
            
            # Lancer le traitement via l'API (plus robuste que l'appel direct)
            self.trigger_api_processing()
            
        except Exception as e:
            log_poster(f"Erreur traitement automatique {file_path}: {str(e)}", "ERROR")
        finally:
            # Nettoyer
            if file_path in self.processing_files:
                self.processing_files.remove(file_path)
    
    def wait_for_file_complete(self, file_path: str, max_wait: int = 30):
        """Attend que le fichier soit complètement écrit"""
        last_size = 0
        stable_count = 0
        
        for _ in range(max_wait):  # Maximum 30 secondes d'attente
            try:
                if not os.path.exists(file_path):
                    break
                
                current_size = os.path.getsize(file_path)
                
                if current_size == last_size:
                    stable_count += 1
                    if stable_count >= 3:  # Stable pendant 3 secondes
                        break
                else:
                    stable_count = 0
                    last_size = current_size
                
                time.sleep(1)
                
            except (OSError, IOError):
                # Fichier pas encore accessible
                time.sleep(1)
                continue
    
    def trigger_api_processing(self):
        """Déclenche le traitement via l'API"""
        try:
            url = f"{self.api_base_url}/api/poster-media/{self.store_name}"
            
            response = requests.post(url, timeout=300)  # 5 minutes timeout
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    log_poster(f"Traitement API réussi pour store {self.store_name}", "SUCCESS")
                else:
                    log_poster(f"Traitement API échoué: {result.get('error', 'Erreur inconnue')}", "ERROR")
            else:
                log_poster(f"Erreur API: {response.status_code} - {response.text}", "ERROR")
                
        except requests.exceptions.Timeout:
            log_poster("Timeout lors du traitement API", "ERROR")
        except Exception as e:
            log_poster(f"Erreur appel API: {str(e)}", "ERROR")

class FolderWatcher:
    """Gestionnaire principal de surveillance des dossiers"""
    
    def __init__(self, api_base_url: str = "http://localhost:8001"):
        self.api_base_url = api_base_url
        self.observers: Dict[str, Observer] = {}
        self.handlers: Dict[str, MediaFileHandler] = {}
        self.running = False
    
    def start_watching(self, stores: list = None):
        """Démarre la surveillance pour les stores spécifiés"""
        if stores is None:
            stores = list(STORES_CONFIG.keys())
        
        log_poster("🔍 Démarrage de la surveillance automatique des dossiers", "INFO")
        
        for store_name in stores:
            if store_name not in STORES_CONFIG:
                log_poster(f"Store inconnu ignoré: {store_name}", "WARNING")
                continue
            
            store_config = STORES_CONFIG[store_name]
            download_dir = store_config["download_dir"]
            
            # Créer le dossier s'il n'existe pas
            os.makedirs(download_dir, exist_ok=True)
            
            if not os.path.exists(download_dir):
                log_poster(f"Impossible de créer le dossier: {download_dir}", "ERROR")
                continue
            
            # Créer le gestionnaire d'événements
            handler = MediaFileHandler(store_name, self.api_base_url)
            self.handlers[store_name] = handler
            
            # Créer l'observateur
            observer = Observer()
            observer.schedule(handler, download_dir, recursive=False)
            
            # Démarrer l'observateur
            observer.start()
            self.observers[store_name] = observer
            
            log_poster(f"📁 Surveillance active: {store_config['name']} -> {download_dir}", "SUCCESS")
        
        self.running = True
        log_poster(f"✅ Surveillance démarrée pour {len(self.observers)} stores", "SUCCESS")
    
    def stop_watching(self):
        """Arrête la surveillance"""
        log_poster("🛑 Arrêt de la surveillance des dossiers", "INFO")
        
        for store_name, observer in self.observers.items():
            observer.stop()
            observer.join(timeout=5)
            log_poster(f"📁 Surveillance arrêtée: {store_name}", "INFO")
        
        self.observers.clear()
        self.handlers.clear()
        self.running = False
        
        log_poster("✅ Surveillance arrêtée", "SUCCESS")
    
    def get_status(self) -> dict:
        """Retourne le statut de la surveillance"""
        return {
            "running": self.running,
            "watched_stores": list(self.observers.keys()),
            "total_watchers": len(self.observers),
            "handlers_status": {
                store: {
                    "processing_files": len(handler.processing_files),
                    "last_processed_count": len(handler.last_processed)
                }
                for store, handler in self.handlers.items()
            }
        }
    
    def run_forever(self):
        """Exécute la surveillance en continu"""
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            log_poster("Interruption clavier détectée", "INFO")
        finally:
            self.stop_watching()

# Instance globale du watcher
folder_watcher = FolderWatcher()

def start_folder_watcher_background():
    """Démarre le watcher en arrière-plan"""
    if not folder_watcher.running:
        threading.Thread(
            target=folder_watcher.start_watching,
            daemon=True
        ).start()
        return True
    return False

def stop_folder_watcher():
    """Arrête le watcher"""
    folder_watcher.stop_watching()

def get_watcher_status():
    """Retourne le statut du watcher"""
    return folder_watcher.get_status()

if __name__ == "__main__":
    # Test standalone
    print("🚀 Démarrage du watcher de dossiers")
    
    try:
        watcher = FolderWatcher()
        watcher.start_watching()
        
        print("✅ Surveillance active. Appuyez sur Ctrl+C pour arrêter.")
        watcher.run_forever()
        
    except KeyboardInterrupt:
        print("🛑 Arrêt du watcher")
    except Exception as e:
        print(f"❌ Erreur: {e}")