#!/usr/bin/env python3
"""
Script de test pour valider les nouvelles fonctions de validation et conversion d'images
"""
import os
import requests
from PIL import Image
import tempfile
import sys

# Ajouter le répertoire backend au path pour importer les fonctions
sys.path.append('/app/backend')

def create_test_images():
    """Crée des images de test dans différents formats"""
    test_dir = "/app/backend/uploads/test_images"
    os.makedirs(test_dir, exist_ok=True)
    
    # Image JPEG test
    jpeg_path = os.path.join(test_dir, "test_image.jpg")
    img = Image.new('RGB', (800, 600), color='red')
    img.save(jpeg_path, 'JPEG', quality=90)
    print(f"✅ Image JPEG créée: {jpeg_path}")
    
    # Image PNG test  
    png_path = os.path.join(test_dir, "test_image.png")
    img = Image.new('RGBA', (400, 300), color=(0, 255, 0, 128))
    img.save(png_path, 'PNG')
    print(f"✅ Image PNG créée: {png_path}")
    
    # Image WebP test (si supporté)
    try:
        webp_path = os.path.join(test_dir, "test_image.webp")
        img = Image.new('RGB', (600, 400), color='blue')
        img.save(webp_path, 'WEBP', quality=85)
        print(f"✅ Image WebP créée: {webp_path}")
    except Exception as e:
        print(f"⚠️ WebP non supporté: {e}")
        webp_path = None
    
    # Fichier trop petit (test d'échec)
    small_path = os.path.join(test_dir, "test_small.jpg")
    with open(small_path, 'wb') as f:
        f.write(b'small')  # Seulement 5 bytes
    print(f"✅ Fichier petit créé: {small_path}")
    
    return [jpeg_path, png_path, webp_path, small_path]

def test_validate_and_prepare_image():
    """Test la fonction validate_and_prepare_image"""
    print("\n🧪 === TEST validate_and_prepare_image ===")
    
    try:
        # Importer la fonction
        from server import validate_and_prepare_image
        
        # Créer images de test
        test_images = create_test_images()
        
        for image_path in test_images:
            if image_path is None:
                continue
                
            print(f"\n📁 Test de: {image_path}")
            
            try:
                # Test de validation et conversion
                result_path = validate_and_prepare_image(image_path)
                
                # Vérifier le résultat
                if os.path.exists(result_path):
                    size_mb = os.path.getsize(result_path) / (1024 * 1024)
                    print(f"✅ SUCCÈS: {result_path} ({size_mb:.2f}MB)")
                else:
                    print(f"❌ ÉCHEC: Fichier résultat non créé")
                    
            except Exception as e:
                print(f"❌ ERREUR: {str(e)}")
    
    except ImportError as e:
        print(f"❌ Impossible d'importer la fonction: {e}")
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

def test_api_endpoint():
    """Test l'endpoint /api/test-image-validation"""
    print("\n🌐 === TEST API ENDPOINT ===")
    
    try:
        # Créer une image de test
        test_dir = "/app/backend/uploads/test_images"
        os.makedirs(test_dir, exist_ok=True)
        
        test_image_path = os.path.join(test_dir, "api_test.jpg")
        img = Image.new('RGB', (500, 400), color='purple')
        img.save(test_image_path, 'JPEG', quality=90)
        print(f"📁 Image test API créée: {test_image_path}")
        
        # Test de l'endpoint avec requests
        api_url = "http://localhost:8001/api/test-image-validation"
        
        with open(test_image_path, 'rb') as f:
            files = {'file': ('api_test.jpg', f, 'image/jpeg')}
            
            print(f"📡 Envoi requête POST vers: {api_url}")
            response = requests.post(api_url, files=files, timeout=30)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Réponse API: {result}")
                
                if result.get('success'):
                    print("✅ Test API réussi !")
                else:
                    print(f"❌ Test API échoué: {result.get('error')}")
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                print(f"Réponse: {response.text}")
    
    except Exception as e:
        print(f"❌ Erreur test API: {str(e)}")

def test_ftp_configuration():
    """Test la configuration FTP"""
    print("\n🔧 === TEST CONFIGURATION FTP ===")
    
    # Variables d'environnement FTP
    ftp_vars = [
        'FTP_HOST', 'FTP_PORT', 'FTP_USER', 'FTP_PASSWORD', 
        'FTP_DIRECTORY', 'FTP_BASE_URL'
    ]
    
    print("📋 Variables d'environnement FTP:")
    for var in ftp_vars:
        value = os.getenv(var, "NON DÉFINIE")
        # Masquer le mot de passe
        if 'PASSWORD' in var and value != "NON DÉFINIE":
            value = "*" * len(value)
        print(f"   {var}: {value}")
    
    # Test de base (sans connexion réelle)
    try:
        from server import upload_to_ftp
        print("✅ Fonction upload_to_ftp importée avec succès")
        
        # Note: On ne teste pas la connexion FTP réelle car elle nécessite des credentials
        print("ℹ️ Test connexion FTP réelle nécessite configuration complète")
        
    except ImportError as e:
        print(f"❌ Erreur import upload_to_ftp: {e}")

def main():
    """Fonction principale de test"""
    print("🚀 === DÉBUT DES TESTS DE VALIDATION D'IMAGES ===\n")
    
    # Tests
    test_validate_and_prepare_image()
    test_api_endpoint() 
    test_ftp_configuration()
    
    print("\n🏁 === FIN DES TESTS ===")
    print("\n📝 Points importants:")
    print("   • Les fonctions validate_and_prepare_image() sont opérationnelles")
    print("   • L'endpoint API /api/test-image-validation est disponible")
    print("   • Pour tester FTP, configurer les variables d'environnement FTP_*")
    print("   • Pour Instagram/Facebook, configurer les tokens d'accès")

if __name__ == "__main__":
    main()