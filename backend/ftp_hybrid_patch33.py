#!/usr/bin/env python3
"""
PATCH 33: Solution FTP hybride pour environnement conteneurisé
Contourne les problèmes de firewall/NAT en utilisant des méthodes alternatives
"""

import os
import time
import ftplib
import requests
import tempfile
from datetime import datetime
from typing import Tuple, Optional
from dotenv import load_dotenv

# Charger configuration
load_dotenv('/app/backend/.env')

class HybridFTPManager:
    """Gestionnaire FTP hybride qui contourne les problèmes de firewall"""
    
    def __init__(self):
        self.host = os.getenv("FTP_HOST", "logicamp.org")
        self.port = int(os.getenv("FTP_PORT", "21"))
        self.user = os.getenv("FTP_USER", "logi")
        self.password = os.getenv("FTP_PASSWORD", "logi")
        self.base_dir = os.getenv("FTP_DIRECTORY", "/www/wordpress/uploads/")
        self.base_url = os.getenv("FTP_BASE_URL", f"https://{self.host}/wordpress/uploads/")
        
        self.max_retries = 3
        self.upload_cache = {}
    
    def log_hybrid(self, message: str, level: str = "INFO"):
        """Logging pour le gestionnaire hybride"""
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
        icon = icons.get(level.upper(), "📋")
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{icon} [{timestamp}] [HYBRID PATCH 33] {message}")
    
    def test_connection_only(self) -> bool:
        """Teste uniquement la connexion de contrôle FTP"""
        try:
            ftp = ftplib.FTP()
            ftp.connect(self.host, self.port, timeout=10)
            ftp.login(self.user, self.password)
            ftp.cwd(self.base_dir)
            ftp.quit()
            return True
        except Exception as e:
            self.log_hybrid(f"Test connexion échoué: {e}", "ERROR")
            return False
    
    def upload_via_sftp_fallback(self, local_path: str, remote_filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Méthode alternative: SFTP si disponible"""
        try:
            import paramiko
            
            self.log_hybrid("Tentative upload SFTP...", "INFO")
            
            # Configuration SFTP
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Tentative de connexion SSH
            ssh.connect(self.host, username=self.user, password=self.password, timeout=10)
            sftp = ssh.open_sftp()
            
            # Upload via SFTP
            remote_path = f"{self.base_dir.rstrip('/')}/{remote_filename}"
            sftp.put(local_path, remote_path)
            
            sftp.close()
            ssh.close()
            
            # Générer URL publique
            public_url = f"{self.base_url}{remote_filename}"
            self.log_hybrid(f"Upload SFTP réussi: {public_url}", "SUCCESS")
            return True, public_url, None
            
        except ImportError:
            return False, None, "Module paramiko non disponible"
        except Exception as e:
            return False, None, f"Erreur SFTP: {e}"
    
    def upload_via_web_api(self, local_path: str, remote_filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Méthode alternative: API Web si disponible"""
        try:
            # Construire l'URL de l'API d'upload (hypothétique)
            upload_url = f"https://{self.host}/api/upload.php"
            
            with open(local_path, 'rb') as f:
                files = {'file': (remote_filename, f, 'application/octet-stream')}
                data = {
                    'username': self.user,
                    'password': self.password,
                    'directory': self.base_dir
                }
                
                response = requests.post(upload_url, files=files, data=data, timeout=30)
                
                if response.status_code == 200:
                    public_url = f"{self.base_url}{remote_filename}"
                    self.log_hybrid(f"Upload API Web réussi: {public_url}", "SUCCESS")
                    return True, public_url, None
                else:
                    return False, None, f"API Web status: {response.status_code}"
                    
        except Exception as e:
            return False, None, f"Erreur API Web: {e}"
    
    def upload_via_minimal_ftp(self, local_path: str, remote_filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Méthode FTP minimale sans transferts de données complexes"""
        try:
            self.log_hybrid("Tentative FTP minimal avec workarounds...", "INFO")
            
            # Lire le fichier en mémoire
            with open(local_path, 'rb') as f:
                file_data = f.read()
            
            # Créer un fichier temporaire avec un nom plus court
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file_data)
                temp_path = temp_file.name
            
            try:
                ftp = ftplib.FTP()
                ftp.set_pasv(True)  # Forcer mode passif
                ftp.connect(self.host, self.port, timeout=20)
                ftp.login(self.user, self.password)
                ftp.cwd(self.base_dir)
                
                # Tentative upload avec gestion d'erreur spécifique
                try:
                    with open(temp_path, 'rb') as f:
                        # Utiliser un blocksize très petit pour éviter les timeouts
                        ftp.storbinary(f'STOR {remote_filename}', f, blocksize=1024)
                    
                    ftp.quit()
                    
                    # Générer URL publique
                    public_url = f"{self.base_url}{remote_filename}"
                    self.log_hybrid(f"FTP minimal réussi: {public_url}", "SUCCESS")
                    
                    # Nettoyer
                    os.unlink(temp_path)
                    
                    return True, public_url, None
                    
                except ftplib.error_temp as e:
                    if "425" in str(e):
                        self.log_hybrid("Erreur 425 - Problème connexion données", "WARNING")
                        return False, None, "Connexion données FTP bloquée par firewall"
                    raise
                    
            finally:
                # Nettoyer le fichier temporaire
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        except Exception as e:
            return False, None, f"FTP minimal échoué: {e}"
    
    def upload_file(self, local_path: str, remote_filename: str = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """Upload avec plusieurs méthodes de fallback"""
        if not os.path.exists(local_path):
            return False, None, f"Fichier local non trouvé: {local_path}"
        
        if not remote_filename:
            remote_filename = os.path.basename(local_path)
        
        self.log_hybrid(f"Début upload hybride: {remote_filename}", "INFO")
        
        # Vérifier d'abord la connexion de contrôle
        if not self.test_connection_only():
            return False, None, "Connexion FTP de base échouée"
        
        # Méthode 1: FTP minimal avec workarounds
        success, url, error = self.upload_via_minimal_ftp(local_path, remote_filename)
        if success:
            return success, url, error
        
        self.log_hybrid("FTP minimal échoué, tentative SFTP...", "WARNING")
        
        # Méthode 2: SFTP fallback
        success, url, error = self.upload_via_sftp_fallback(local_path, remote_filename)
        if success:
            return success, url, error
        
        self.log_hybrid("SFTP échoué, tentative API Web...", "WARNING")
        
        # Méthode 3: API Web fallback 
        success, url, error = self.upload_via_web_api(local_path, remote_filename)
        if success:
            return success, url, error
        
        # Toutes les méthodes ont échoué - mais on peut quand même générer l'URL
        self.log_hybrid("Tous les uploads ont échoué, génération URL optimiste...", "WARNING")
        
        # Générer l'URL même si l'upload échoue (pour compatibilité)
        optimistic_url = f"{self.base_url}{remote_filename}"
        self.log_hybrid(f"URL optimiste générée: {optimistic_url}", "WARNING")
        self.log_hybrid("⚠️ IMPORTANT: Le fichier n'a PAS été uploadé!", "WARNING")
        
        return False, optimistic_url, "Upload échoué mais URL générée"
    
    def verify_upload(self, url: str) -> bool:
        """Vérifie si un fichier uploadé est accessible"""
        try:
            response = requests.head(url, timeout=10)
            return response.status_code == 200
        except:
            return False

# Instance globale
hybrid_manager = None

def init_hybrid_ftp_manager():
    """Initialise le gestionnaire FTP hybride"""
    global hybrid_manager
    if not hybrid_manager:
        hybrid_manager = HybridFTPManager()
        hybrid_manager.log_hybrid("Gestionnaire FTP hybride initialisé", "SUCCESS")
    return hybrid_manager

def upload_for_publication_hybrid(local_path: str, filename: str = None) -> Tuple[bool, Optional[str], Optional[str]]:
    """Interface pour upload hybride"""
    manager = init_hybrid_ftp_manager()
    return manager.upload_file(local_path, filename)

if __name__ == "__main__":
    # Test du gestionnaire hybride
    manager = init_hybrid_ftp_manager()
    
    # Créer un fichier de test
    test_content = b"PATCH 33 Hybrid Test"
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
        f.write(test_content)
        test_file = f.name
    
    try:
        success, url, error = manager.upload_file(test_file, f"hybrid_test_{int(time.time())}.txt")
        
        if success:
            print(f"✅ Upload hybride réussi: {url}")
            
            # Vérifier l'accessibilité
            if manager.verify_upload(url):
                print("✅ URL accessible publiquement!")
            else:
                print("⚠️ URL non accessible (mais upload peut avoir réussi)")
        else:
            print(f"❌ Upload hybride échoué: {error}")
            if url:
                print(f"ℹ️ URL générée quand même: {url}")
    
    finally:
        # Nettoyer
        try:
            os.unlink(test_file)
        except:
            pass