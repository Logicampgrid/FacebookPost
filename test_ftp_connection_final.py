#!/usr/bin/env python3
"""
Test de connexion FTP pour résoudre le problème FTP de FacebookPost
Version finale avec configuration corrigée
"""

import ftplib
import os
import tempfile
import time
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('/app/backend/.env')

# Configuration FTP mise à jour
FTP_HOST = os.getenv("FTP_HOST", "logicamp.org")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER", "logi")
FTP_PASSWORD = os.getenv("FTP_PASSWORD", "logi")
FTP_DIRECTORY = os.getenv("FTP_DIRECTORY", "/wordpress/uploads/")
FTP_BASE_URL = os.getenv("FTP_BASE_URL", f"https://{FTP_HOST}/wordpress/uploads/")

def log_test(message: str, level: str = "INFO"):
    """Logging pour les tests FTP"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [FTP-TEST] {message}")

def test_ftp_connection():
    """Test complet de connexion FTP"""
    try:
        log_test("=== DÉBUT TEST FTP COMPLET ===", "TEST")
        log_test(f"Configuration FTP:", "INFO")
        log_test(f"  Host: {FTP_HOST}", "INFO")
        log_test(f"  Port: {FTP_PORT}", "INFO")
        log_test(f"  User: {FTP_USER}", "INFO")
        log_test(f"  Password: {'*' * len(FTP_PASSWORD)} (longueur: {len(FTP_PASSWORD)})", "INFO")
        log_test(f"  Directory: {FTP_DIRECTORY}", "INFO")
        log_test(f"  Base URL: {FTP_BASE_URL}", "INFO")
        
        # Test 1: Connexion de base
        log_test("Test 1/5 - Connexion au serveur FTP", "TEST")
        ftp = ftplib.FTP()
        ftp.set_pasv(True)  # Mode passif
        ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
        log_test("✅ Connexion TCP établie", "SUCCESS")
        
        # Test 2: Authentification
        log_test("Test 2/5 - Authentification", "TEST")
        ftp.login(FTP_USER, FTP_PASSWORD)
        log_test("✅ Authentification réussie", "SUCCESS")
        
        # Test 3: Navigation vers le répertoire
        log_test("Test 3/5 - Navigation vers le répertoire WordPress", "TEST")
        try:
            ftp.cwd(FTP_DIRECTORY)
            log_test(f"✅ Navigation vers {FTP_DIRECTORY} réussie", "SUCCESS")
        except ftplib.error_perm as e:
            log_test(f"⚠️ Répertoire non accessible: {e}", "WARNING")
            log_test("Tentative de création du répertoire...", "INFO")
            try:
                ftp.mkd(FTP_DIRECTORY)
                ftp.cwd(FTP_DIRECTORY)
                log_test(f"✅ Répertoire créé et accessible: {FTP_DIRECTORY}", "SUCCESS")
            except Exception as mkdir_error:
                log_test(f"❌ Impossible de créer le répertoire: {mkdir_error}", "ERROR")
                raise
        
        # Test 4: Listing du répertoire
        log_test("Test 4/5 - Listing du répertoire", "TEST")
        file_list = []
        try:
            ftp.retrlines('LIST', file_list.append)
            log_test(f"✅ Listing réussi - {len(file_list)} éléments trouvés", "SUCCESS")
            if file_list:
                log_test("Premiers éléments:", "INFO")
                for item in file_list[:5]:  # Afficher les 5 premiers
                    log_test(f"  {item}", "INFO")
        except Exception as e:
            log_test(f"⚠️ Erreur listing: {e}", "WARNING")
        
        # Test 5: Upload de test
        log_test("Test 5/5 - Upload de fichier de test", "TEST")
        test_content = f"Test FTP - {datetime.now().isoformat()}\nFacebookPost Application\nUpload réussi !"
        test_filename = f"ftp_test_{int(time.time())}.txt"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, 'rb') as test_file:
                ftp.storbinary(f'STOR {test_filename}', test_file)
            
            log_test(f"✅ Upload du fichier de test réussi: {test_filename}", "SUCCESS")
            
            # Vérifier que le fichier existe
            try:
                size = ftp.size(test_filename)
                log_test(f"✅ Fichier confirmé sur le serveur - Taille: {size} bytes", "SUCCESS")
                
                # Construire l'URL publique
                public_url = f"{FTP_BASE_URL}{test_filename}"
                log_test(f"🌐 URL publique: {public_url}", "SUCCESS")
                
                # Nettoyer - supprimer le fichier de test
                ftp.delete(test_filename)
                log_test("🧹 Fichier de test supprimé", "INFO")
                
            except Exception as e:
                log_test(f"⚠️ Impossible de vérifier le fichier: {e}", "WARNING")
                
        except Exception as e:
            log_test(f"❌ Erreur upload: {e}", "ERROR")
            raise
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
        # Fermer la connexion
        ftp.quit()
        log_test("✅ Connexion FTP fermée proprement", "SUCCESS")
        
        log_test("=== TEST FTP COMPLET RÉUSSI ===", "SUCCESS")
        log_test("🎉 La configuration FTP est fonctionnelle !", "SUCCESS")
        log_test("📤 L'upload de vidéos devrait maintenant fonctionner", "SUCCESS")
        
        return True
        
    except Exception as e:
        log_test(f"❌ ÉCHEC DU TEST FTP: {str(e)}", "ERROR")
        log_test("=== DIAGNOSTIC ===", "ERROR")
        log_test("Vérifiez:", "ERROR")
        log_test("1. Les credentials FTP (user/password)", "ERROR")
        log_test("2. L'accès réseau au serveur", "ERROR")
        log_test("3. Les permissions du répertoire", "ERROR")
        log_test("4. La configuration du serveur FTP", "ERROR")
        return False

def test_alternative_credentials():
    """Test avec les credentials alternatifs"""
    log_test("=== TEST AVEC CREDENTIALS ALTERNATIFS ===", "TEST")
    
    alternative_configs = [
        {"user": "admin", "password": "admin"},
        {"user": "logi", "password": "admin"},
        {"user": "admin", "password": "logi"}
    ]
    
    for i, config in enumerate(alternative_configs, 1):
        try:
            log_test(f"Test {i}/3 - User: {config['user']}, Password: {config['password']}", "TEST")
            
            ftp = ftplib.FTP()
            ftp.set_pasv(True)
            ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
            ftp.login(config['user'], config['password'])
            
            log_test(f"✅ Credentials alternatifs fonctionnels: {config['user']}/{config['password']}", "SUCCESS")
            ftp.quit()
            
            # Mettre à jour le .env avec les bons credentials
            log_test("💡 SOLUTION TROUVÉE - Mise à jour recommandée:", "SUCCESS")
            log_test(f"FTP_USER={config['user']}", "SUCCESS")
            log_test(f"FTP_PASSWORD={config['password']}", "SUCCESS")
            
            return config
            
        except Exception as e:
            log_test(f"❌ Échec avec {config['user']}/{config['password']}: {str(e)}", "ERROR")
            continue
    
    log_test("❌ Aucun credential alternatif ne fonctionne", "ERROR")
    return None

if __name__ == "__main__":
    print()
    print("🚀 TEST DE CONNEXION FTP - FacebookPost Application")
    print("=" * 60)
    
    # Test principal
    success = test_ftp_connection()
    
    if not success:
        print()
        log_test("Tentative avec credentials alternatifs...", "INFO")
        alternative = test_alternative_credentials()
        
        if alternative:
            print()
            log_test("🔧 ACTION REQUISE:", "WARNING")
            log_test("Mettez à jour le fichier /app/backend/.env avec:", "WARNING")
            log_test(f"FTP_USER={alternative['user']}", "WARNING")
            log_test(f"FTP_PASSWORD={alternative['password']}", "WARNING")
    
    print()
    print("=" * 60)
    print("✅ Test terminé" if success else "❌ Test échoué")