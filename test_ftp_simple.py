#!/usr/bin/env python3
"""
Test FTP simplifié pour identifier le problème exact
"""
import os
import ftplib
import tempfile
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration FTP
FTP_HOST = os.getenv("FTP_HOST", "logicamp.org")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER", "logi")
FTP_PASSWORD = os.getenv("FTP_PASSWORD", "")
FTP_DIRECTORY = os.getenv("FTP_DIRECTORY", "/wordpress/uploads/")

def test_simple_ftp():
    """Test FTP très simple"""
    try:
        print(f"🧪 Test connexion FTP: {FTP_HOST}:{FTP_PORT}")
        print(f"🧪 Utilisateur: {FTP_USER}")
        print(f"🧪 Mot de passe: {'*' * len(FTP_PASSWORD)}")
        
        # Connexion et authentification seulement
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
        print("✅ Connexion réussie")
        
        ftp.login(FTP_USER, FTP_PASSWORD)
        print("✅ Authentification réussie")
        
        # Tester différents dossiers
        current_dir = ftp.pwd()
        print(f"📁 Dossier actuel: {current_dir}")
        
        # Essayer de changer vers le dossier wordpress
        try:
            ftp.cwd("/wordpress")
            print("✅ Accès /wordpress réussi")
            current_dir = ftp.pwd()
            print(f"📁 Nouveau dossier: {current_dir}")
        except Exception as e:
            print(f"❌ Impossible d'accéder à /wordpress: {e}")
        
        # Essayer de changer vers le dossier uploads complet
        try:
            ftp.cwd("/wordpress/uploads")
            print("✅ Accès /wordpress/uploads réussi")
            current_dir = ftp.pwd()
            print(f"📁 Dossier final: {current_dir}")
        except Exception as e:
            print(f"❌ Impossible d'accéder à /wordpress/uploads: {e}")
            
        # Test upload très simple sans listage
        print("🧪 Test upload sans listage...")
        
        # Créer un petit fichier test
        test_content = f"Test - {datetime.now().isoformat()}"
        test_filename = f"test_{int(datetime.now().timestamp())}.txt"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_path = temp_file.name
        
        try:
            # Upload en mode binaire
            with open(temp_path, 'rb') as file:
                ftp.storbinary(f'STOR {test_filename}', file)
            print(f"✅ Upload réussi: {test_filename}")
            
            # Construire l'URL
            public_url = f"https://logicamp.org/wordpress/uploads/{test_filename}"
            print(f"🌐 URL publique: {public_url}")
            
            # Essayer de supprimer le fichier
            try:
                ftp.delete(test_filename)
                print("✅ Fichier test supprimé")
            except Exception as del_error:
                print(f"⚠️ Impossible de supprimer: {del_error}")
                
        except Exception as upload_error:
            print(f"❌ Erreur upload: {upload_error}")
        finally:
            os.unlink(temp_path)
        
        ftp.quit()
        print("✅ Test FTP terminé avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur FTP: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_ftp()
    exit(0 if success else 1)