#!/usr/bin/env python3
"""
PATCH 29: Gestionnaire FTP intelligent 
Gère les uploads FTP avec retry, cache local et fallback
"""

import os
import time
import threading
import queue
import ftplib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class FTPManager:
    """Gestionnaire FTP intelligent avec retry et cache local"""
    
    def __init__(self, host: str, port: int, user: str, password: str, 
                 base_dir: str = "/wordpress/uploads/", base_url: str = None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.base_dir = base_dir
        self.base_url = base_url or f"https://{host}/wordpress/uploads/"
        
        # Configuration des tentatives
        self.max_retries = 3
        self.retry_delay = 5
        self.connection_timeout = 15
        
        # Cache local des fichiers uploadés
        self.upload_cache = {}
        self.cache_file = "/app/backend/ftp_cache.txt"
        self.load_cache()
        
        # Queue pour les uploads en arrière-plan
        self.upload_queue = queue.Queue()
        self.background_thread = None
        self.is_running = False
        
    def log_ftp(self, message: str, level: str = "INFO"):
        """Logging FTP"""
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
        icon = icons.get(level.upper(), "📋")
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{icon} [{timestamp}] [FTP MGR] {message}")
        
    def load_cache(self):
        """Charge le cache des fichiers uploadés"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split('|')
                        if len(parts) == 2:
                            local_path, ftp_url = parts
                            self.upload_cache[local_path] = ftp_url
                self.log_ftp(f"Cache FTP chargé: {len(self.upload_cache)} entrées", "INFO")
        except Exception as e:
            self.log_ftp(f"Erreur chargement cache: {e}", "WARNING")
    
    def save_cache(self):
        """Sauvegarde le cache"""
        try:
            with open(self.cache_file, 'w') as f:
                for local_path, ftp_url in self.upload_cache.items():
                    f.write(f"{local_path}|{ftp_url}\n")
        except Exception as e:
            self.log_ftp(f"Erreur sauvegarde cache: {e}", "WARNING")
    
    def test_connection(self) -> bool:
        """Test rapide de connexion FTP"""
        try:
            ftp = ftplib.FTP()
            ftp.set_pasv(True)
            ftp.connect(self.host, self.port, timeout=10)
            ftp.login(self.user, self.password)
            ftp.cwd(self.base_dir)
            ftp.quit()
            return True
        except Exception as e:
            self.log_ftp(f"Test connexion échoué: {e}", "ERROR")
            return False
    
    def upload_file_sync(self, local_path: str, remote_filename: str = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """Upload synchrone avec retry"""
        if not os.path.exists(local_path):
            return False, None, f"Fichier local non trouvé: {local_path}"
        
        if not remote_filename:
            remote_filename = os.path.basename(local_path)
        
        # Vérifier le cache
        if local_path in self.upload_cache:
            cached_url = self.upload_cache[local_path]
            self.log_ftp(f"Fichier trouvé dans cache: {cached_url}", "SUCCESS")
            return True, cached_url, None
        
        # Tentatives d'upload
        for attempt in range(self.max_retries):
            try:
                self.log_ftp(f"Upload tentative {attempt + 1}/{self.max_retries}: {remote_filename}", "INFO")
                
                # Configuration FTP optimisée
                configs = [
                    {"pasv": False, "timeout": 10, "blocksize": 4096},  # Actif rapide
                    {"pasv": True, "timeout": 15, "blocksize": 2048},   # Passif standard
                ]
                
                for config in configs:
                    try:
                        ftp = ftplib.FTP()
                        ftp.set_pasv(config["pasv"])
                        ftp.connect(self.host, self.port, timeout=config["timeout"])
                        ftp.login(self.user, self.password)
                        ftp.cwd(self.base_dir)
                        
                        # Upload du fichier
                        with open(local_path, 'rb') as f:
                            ftp.storbinary(f'STOR {remote_filename}', f, blocksize=config["blocksize"])
                        
                        ftp.quit()
                        
                        # Générer URL publique
                        ftp_url = f"{self.base_url}{remote_filename}"
                        
                        # Sauvegarder dans le cache
                        self.upload_cache[local_path] = ftp_url
                        self.save_cache()
                        
                        self.log_ftp(f"Upload réussi: {ftp_url}", "SUCCESS")
                        return True, ftp_url, None
                        
                    except Exception as config_error:
                        self.log_ftp(f"Config {'passif' if config['pasv'] else 'actif'} échouée: {config_error}", "WARNING")
                        continue
                        
            except Exception as e:
                self.log_ftp(f"Tentative {attempt + 1} échouée: {e}", "WARNING")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        return False, None, f"Upload échoué après {self.max_retries} tentatives"
    
    def get_public_url(self, filename: str, local_path: str = None) -> str:
        """Génère une URL publique pour un fichier"""
        # Vérifier d'abord le cache si on a le chemin local
        if local_path and local_path in self.upload_cache:
            return self.upload_cache[local_path]
        
        # Sinon, générer l'URL basée sur le nom de fichier
        return f"{self.base_url}{filename}"
    
    def queue_upload(self, local_path: str, remote_filename: str = None):
        """Ajoute un fichier à la queue d'upload en arrière-plan"""
        self.upload_queue.put((local_path, remote_filename))
        self.log_ftp(f"Fichier ajouté à la queue: {os.path.basename(local_path)}", "INFO")
        
        # Démarrer le thread de traitement si nécessaire
        if not self.is_running:
            self.start_background_worker()
    
    def start_background_worker(self):
        """Démarre le worker d'upload en arrière-plan"""
        if self.is_running:
            return
            
        self.is_running = True
        self.background_thread = threading.Thread(target=self._background_worker, daemon=True)
        self.background_thread.start()
        self.log_ftp("Worker d'upload en arrière-plan démarré", "SUCCESS")
    
    def _background_worker(self):
        """Worker qui traite la queue d'upload"""
        while self.is_running:
            try:
                # Attendre un élément dans la queue (avec timeout)
                try:
                    local_path, remote_filename = self.upload_queue.get(timeout=30)
                except queue.Empty:
                    continue
                
                # Traiter l'upload
                success, url, error = self.upload_file_sync(local_path, remote_filename)
                
                if success:
                    self.log_ftp(f"Upload en arrière-plan réussi: {url}", "SUCCESS")
                else:
                    self.log_ftp(f"Upload en arrière-plan échoué: {error}", "ERROR")
                
                # Marquer la tâche comme terminée
                self.upload_queue.task_done()
                
            except Exception as e:
                self.log_ftp(f"Erreur worker: {e}", "ERROR")
    
    def stop_background_worker(self):
        """Arrête le worker d'upload"""
        self.is_running = False
        if self.background_thread and self.background_thread.is_alive():
            self.background_thread.join(timeout=10)
        self.log_ftp("Worker d'upload arrêté", "INFO")

# Instance globale du gestionnaire FTP
ftp_manager = None

def init_ftp_manager():
    """PATCH 30: Initialise le gestionnaire FTP global avec configuration centralisée .env"""
    global ftp_manager
    if not ftp_manager:
        # PATCH 30: Lire configuration depuis .env backend
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        ftp_host = os.getenv("FTP_HOST", "logicamp.org")
        ftp_port = int(os.getenv("FTP_PORT", "21"))
        ftp_user = os.getenv("FTP_USER", "logi")
        ftp_password = os.getenv("FTP_PASSWORD", "6837")
        ftp_directory = os.getenv("FTP_DIRECTORY", "/wordpress/uploads/")
        ftp_base_url = os.getenv("FTP_BASE_URL", f"https://{ftp_host}/wordpress/uploads/")
        
        ftp_manager = FTPManager(
            host=ftp_host,
            port=ftp_port,
            user=ftp_user, 
            password=ftp_password,
            base_dir=ftp_directory,
            base_url=ftp_base_url
        )
        ftp_manager.log_ftp(f"PATCH 30: Gestionnaire FTP initialisé avec config .env - {ftp_host}:{ftp_port}", "SUCCESS")
    return ftp_manager

def upload_for_publication(local_path: str, filename: str = None) -> Tuple[bool, Optional[str], Optional[str]]:
    """Interface simplifiée pour upload avec publication"""
    manager = init_ftp_manager()
    return manager.upload_file_sync(local_path, filename)

def get_ftp_public_url(filename: str, local_path: str = None) -> str:
    """Interface simplifiée pour obtenir une URL publique"""
    manager = init_ftp_manager()
    return manager.get_public_url(filename, local_path)

if __name__ == "__main__":
    # Test du gestionnaire
    manager = init_ftp_manager()
    
    # Test de connexion
    if manager.test_connection():
        print("✅ Gestionnaire FTP opérationnel")
    else:
        print("❌ Problème de connexion FTP")