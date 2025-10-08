#!/usr/bin/env python3
"""
Test rapide de connexion FTP avec le mot de passe corrigé
"""

import os
import sys
import ftplib
from datetime import datetime

# Ajouter le backend au path
sys.path.append('/app/backend')

def log_test(message: str, level: str = "INFO"):
    """Logging pour les tests"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [FTP TEST] {message}")

def test_ftp_with_corrected_password():
    """Test FTP avec le mot de passe corrigé"""
    
    # Configuration FTP corrigée
    FTP_HOST = "logicamp.org"
    FTP_PORT = 21
    FTP_USER = "logi"
    FTP_PASSWORD = "6837"
    FTP_DIRECTORY = "/www/wordpress/uploads/"
    
    log_test("🧪 Test connexion FTP avec mot de passe corrigé", "INFO")
    log_test(f"Host: {FTP_HOST}:{FTP_PORT}", "INFO")
    log_test(f"User: {FTP_USER}", "INFO")
    log_test(f"Password: {'*' * len(FTP_PASSWORD)}", "INFO")
    log_test(f"Directory: {FTP_DIRECTORY}", "INFO")
    
    try:
        # Test connexion
        log_test("Connexion au serveur FTP...", "INFO")
        ftp = ftplib.FTP()
        ftp.set_pasv(True)
        ftp.connect(FTP_HOST, FTP_PORT, timeout=20)
        
        log_test("Authentification...", "INFO")
        ftp.login(FTP_USER, FTP_PASSWORD)
        
        log_test("Navigation vers le répertoire...", "INFO")
        ftp.cwd(FTP_DIRECTORY)
        
        # Test liste des fichiers
        log_test("Listage des fichiers...", "INFO")
        files = ftp.nlst()
        log_test(f"Nombre de fichiers dans le répertoire: {len(files)}", "SUCCESS")
        
        # Test upload d'un fichier de test
        test_content = f"Test correction FTP - {datetime.now()}\n"
        test_filename = f"test_correction_{int(datetime.now().timestamp())}.txt"
        
        log_test(f"Test upload: {test_filename}", "INFO")
        
        # Créer fichier temporaire
        temp_path = f"/tmp/{test_filename}"
        with open(temp_path, 'w') as f:
            f.write(test_content)
        
        # Upload
        with open(temp_path, 'rb') as f:
            ftp.storbinary(f'STOR {test_filename}', f)
        
        # Vérifier upload
        remote_size = ftp.size(test_filename)
        local_size = os.path.getsize(temp_path)
        
        if remote_size == local_size:
            log_test(f"Upload réussi: {remote_size} bytes", "SUCCESS")
            
            # Test URL publique
            public_url = f"https://{FTP_HOST}/wordpress/uploads/{test_filename}"
            log_test(f"URL publique: {public_url}", "INFO")
            
            # Nettoyer le fichier de test
            ftp.delete(test_filename)
            log_test("Fichier de test supprimé", "INFO")
            
            success = True
        else:
            log_test(f"Taille différente: local={local_size}, remote={remote_size}", "ERROR")
            success = False
        
        ftp.quit()
        
        # Nettoyer le fichier local
        os.remove(temp_path)
        
        return success
        
    except Exception as e:
        log_test(f"Erreur FTP: {e}", "ERROR")
        try:
            ftp.quit()
        except:
            pass
        return False

if __name__ == "__main__":
    success = test_ftp_with_corrected_password()
    
    if success:
        print("\n✅ RÉSULTAT: Connexion FTP fonctionnelle avec le mot de passe corrigé !")
        print("🔧 La correction du mot de passe dans .env devrait résoudre le problème d'upload.")
    else:
        print("\n❌ RÉSULTAT: Problème persistant avec la connexion FTP")
        print("🔍 Investigation supplémentaire nécessaire.")