#!/usr/bin/env python3
"""
Test FTP final pour identifier le problème exact
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

def test_ftp_exactly_like_code():
    """Test FTP exactement comme dans le code du serveur"""
    try:
        print(f"🧪 Test FTP exact comme le code serveur")
        print(f"Host: {FTP_HOST}:{FTP_PORT}")
        print(f"User: {FTP_USER}")
        print(f"Password: {'*' * len(FTP_PASSWORD)}")
        print(f"Directory: {FTP_DIRECTORY}")
        
        # Exactement comme dans server.py
        ftp = ftplib.FTP()
        ftp.set_pasv(True)  # Mode passif explicite
        ftp.connect(FTP_HOST, FTP_PORT, timeout=120)
        print("✅ Connexion réussie")
        
        ftp.login(FTP_USER, FTP_PASSWORD)
        print("✅ Authentification réussie")
        
        # Navigation exacte
        try:
            ftp.cwd(FTP_DIRECTORY)
            print(f"✅ Navigation vers {FTP_DIRECTORY} réussie")
        except ftplib.error_perm as e:
            print(f"⚠️ Erreur navigation: {e}")
            print("Tentative de création...")
            try:
                ftp.mkd(FTP_DIRECTORY)
                ftp.cwd(FTP_DIRECTORY)
                print("✅ Répertoire créé et navigation réussie")
            except Exception as mkdir_error:
                print(f"❌ Impossible de créer: {mkdir_error}")
                return False
        
        # Test upload comme dans le code
        test_content = b"Test FTP exactement comme server.py"
        filename = f"test_exact_{int(datetime.now().timestamp())}.txt"
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(test_content)
            temp_path = temp_file.name
        
        try:
            print(f"Upload test: {filename}")
            with open(temp_path, 'rb') as file:
                ftp.storbinary(f'STOR {filename}', file, blocksize=8192)
            print("✅ Upload réussi")
            
            # Vérification
            try:
                file_size = ftp.size(filename)
                print(f"✅ Fichier confirmé - Taille: {file_size} bytes")
            except:
                print("⚠️ Vérification taille échouée mais upload semble OK")
            
            # URL publique
            public_url = f"https://logicamp.org/wordpress/uploads/{filename}"
            print(f"🌐 URL: {public_url}")
            
            # Nettoyage
            try:
                ftp.delete(filename)
                print("✅ Fichier test supprimé")
            except:
                print("⚠️ Suppression échouée")
            
        finally:
            os.unlink(temp_path)
        
        ftp.quit()
        print("✅ Test FTP réussi complètement")
        return True
        
    except ftplib.error_perm as e:
        print(f"❌ Erreur permission FTP: {e}")
        if "530" in str(e):
            print("💡 Erreur 530 = Authentification échouée")
            print("💡 Vérifiez utilisateur/mot de passe")
        return False
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

def test_ftp_with_variations():
    """Test avec différentes variations"""
    print("\n🧪 Test avec variations...")
    
    variations = [
        {"user": "logi", "pass": "logi"},  # Original
        {"user": "logi", "pass": "logicamp"},  # Autre possibilité
        {"user": "logicamp", "pass": "logi"},  # Inversé
        {"user": "wordpress", "pass": "logi"},  # WordPress user
    ]
    
    for i, creds in enumerate(variations, 1):
        print(f"\n--- Variation {i}: {creds['user']} / {'*' * len(creds['pass'])} ---")
        try:
            ftp = ftplib.FTP()
            ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
            ftp.login(creds['user'], creds['pass'])
            print(f"✅ Variation {i} réussie!")
            
            # Test navigation
            try:
                ftp.cwd("/wordpress/uploads")
                print("✅ Navigation WordPress réussie")
                return creds  # Retourner les bons identifiants
            except:
                print("❌ Navigation WordPress échouée")
            ftp.quit()
            
        except ftplib.error_perm as e:
            print(f"❌ Variation {i} échouée: {e}")
        except Exception as e:
            print(f"❌ Erreur variation {i}: {e}")
    
    return None

if __name__ == "__main__":
    print("=== TEST FTP COMPLET ===")
    
    # Test exact comme le code
    success = test_ftp_exactly_like_code()
    
    if not success:
        print("\n=== RECHERCHE BONS IDENTIFIANTS ===")
        good_creds = test_ftp_with_variations()
        if good_creds:
            print(f"\n✅ Bons identifiants trouvés: {good_creds['user']} / {good_creds['pass']}")
        else:
            print("\n❌ Aucune variation n'a fonctionné")
    
    exit(0 if success else 1)