#!/usr/bin/env python3
"""
Test de connexion FTP pour diagnostiquer le problème
"""
import os
import ftplib
import tempfile
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration FTP depuis .env
FTP_HOST = os.getenv("FTP_HOST", "logicamp.org")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER", "logi")
FTP_PASSWORD = os.getenv("FTP_PASSWORD", "")
FTP_DIRECTORY = os.getenv("FTP_DIRECTORY", "/wordpress/uploads/")
FTP_BASE_URL = os.getenv("FTP_BASE_URL", f"https://{FTP_HOST}/wordpress/uploads/")

def log_test(message: str, level: str = "INFO"):
    """Logging pour les tests"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [FTP_TEST] {message}")

def test_ftp_connection():
    """Test complet de connexion FTP"""
    try:
        log_test("=== DÉBUT TEST CONNEXION FTP ===", "TEST")
        log_test(f"Host: {FTP_HOST}:{FTP_PORT}", "INFO")
        log_test(f"User: {FTP_USER}", "INFO")
        log_test(f"Password: {'*' * len(FTP_PASSWORD)}", "INFO")
        log_test(f"Directory: {FTP_DIRECTORY}", "INFO")
        
        # Test 1: Connexion de base
        log_test("Test 1: Connexion au serveur FTP...", "TEST")
        ftp = ftplib.FTP()
        ftp.set_debuglevel(2)  # Mode debug pour voir les détails
        ftp.set_pasv(False)  # Utiliser mode actif au lieu de passif
        ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
        log_test("✅ Connexion au serveur réussie", "SUCCESS")
        
        # Test 2: Authentification
        log_test("Test 2: Authentification...", "TEST")
        ftp.login(FTP_USER, FTP_PASSWORD)
        log_test("✅ Authentification réussie", "SUCCESS")
        
        # Test 3: Navigation vers le dossier
        log_test("Test 3: Navigation vers le dossier cible...", "TEST")
        current_dir = ftp.pwd()
        log_test(f"Dossier actuel: {current_dir}", "INFO")
        
        try:
            ftp.cwd(FTP_DIRECTORY)
            log_test(f"✅ Navigation vers {FTP_DIRECTORY} réussie", "SUCCESS")
        except ftplib.error_perm as e:
            log_test(f"⚠️ Dossier {FTP_DIRECTORY} non accessible: {e}", "WARNING")
            log_test("Tentative de création du dossier...", "INFO")
            try:
                ftp.mkd(FTP_DIRECTORY)
                ftp.cwd(FTP_DIRECTORY)
                log_test(f"✅ Dossier {FTP_DIRECTORY} créé et accessible", "SUCCESS")
            except Exception as mkdir_error:
                log_test(f"❌ Impossible de créer le dossier: {mkdir_error}", "ERROR")
                return False
        
        # Test 4: Listage des fichiers
        log_test("Test 4: Listage des fichiers...", "TEST")
        files = ftp.nlst()
        log_test(f"Fichiers trouvés: {len(files)}", "INFO")
        if files:
            log_test(f"Premiers fichiers: {files[:5]}", "INFO")
        
        # Test 5: Upload d'un fichier test
        log_test("Test 5: Upload d'un fichier test...", "TEST")
        
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(f"Test FTP - {datetime.now().isoformat()}")
            temp_file_path = temp_file.name
        
        try:
            test_filename = f"test_ftp_{int(datetime.now().timestamp())}.txt"
            with open(temp_file_path, 'rb') as test_file:
                ftp.storbinary(f'STOR {test_filename}', test_file)
            log_test(f"✅ Upload du fichier test réussi: {test_filename}", "SUCCESS")
            
            # Vérifier que le fichier existe
            files_after = ftp.nlst()
            if test_filename in files_after:
                log_test("✅ Fichier confirmé sur le serveur", "SUCCESS")
                
                # Construire l'URL publique
                public_url = f"{FTP_BASE_URL}{test_filename}"
                log_test(f"URL publique: {public_url}", "INFO")
                
                # Supprimer le fichier test
                try:
                    ftp.delete(test_filename)
                    log_test("✅ Fichier test supprimé", "SUCCESS")
                except:
                    log_test("⚠️ Impossible de supprimer le fichier test", "WARNING")
            else:
                log_test("❌ Fichier non trouvé après upload", "ERROR")
                return False
                
        except Exception as upload_error:
            log_test(f"❌ Erreur upload: {upload_error}", "ERROR")
            return False
        finally:
            # Nettoyer le fichier temporaire local
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        # Test 6: Test spécifique dossier gizmobbs
        log_test("Test 6: Test dossier gizmobbs...", "TEST")
        gizmobbs_dir = f"{FTP_DIRECTORY}gizmobbs/"
        try:
            ftp.cwd(gizmobbs_dir)
            log_test(f"✅ Dossier gizmobbs accessible: {gizmobbs_dir}", "SUCCESS")
        except ftplib.error_perm:
            log_test("Dossier gizmobbs n'existe pas, création...", "INFO")
            try:
                ftp.mkd(gizmobbs_dir)
                ftp.cwd(gizmobbs_dir)
                log_test(f"✅ Dossier gizmobbs créé: {gizmobbs_dir}", "SUCCESS")
            except Exception as e:
                log_test(f"❌ Impossible de créer le dossier gizmobbs: {e}", "ERROR")
                return False
        
        # Fermer la connexion
        ftp.quit()
        log_test("=== TEST FTP TERMINÉ AVEC SUCCÈS ===", "SUCCESS")
        return True
        
    except ftplib.error_perm as e:
        log_test(f"❌ Erreur de permission FTP: {e}", "ERROR")
        return False
    except Exception as e:
        log_test(f"❌ Erreur générale FTP: {e}", "ERROR")
        return False

if __name__ == "__main__":
    success = test_ftp_connection()
    exit(0 if success else 1)