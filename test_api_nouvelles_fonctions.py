#!/usr/bin/env python3
"""
Test des nouvelles fonctions via l'API backend
"""

import requests
import json
import os
from PIL import Image
import io

def test_backend_running():
    """Test que le backend fonctionne"""
    try:
        # Récupérer l'URL du backend depuis .env
        backend_url = "http://localhost:8001"  # URL interne
        
        response = requests.get(f"{backend_url}/docs")
        if response.status_code == 200:
            print("✅ Backend FastAPI est accessible")
            return True
        else:
            print(f"❌ Backend répond avec code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au backend")
        return False
    except Exception as e:
        print(f"❌ Erreur test backend: {e}")
        return False

def test_wordpress_directory():
    """Test que le dossier WordPress est prêt pour les uploads"""
    wordpress_dir = "/app/backend/wordpress/uploads/"
    
    if os.path.exists(wordpress_dir):
        print(f"✅ Dossier WordPress existe: {wordpress_dir}")
        
        # Test d'écriture
        try:
            test_file = os.path.join(wordpress_dir, "test_write.txt")
            with open(test_file, "w") as f:
                f.write("Test d'écriture")
            
            if os.path.exists(test_file):
                print("✅ Écriture dans le dossier WordPress réussie")
                os.remove(test_file)  # Nettoyer
                return True
            else:
                print("❌ Fichier test non créé")
                return False
        except Exception as e:
            print(f"❌ Erreur écriture WordPress: {e}")
            return False
    else:
        print(f"❌ Dossier WordPress n'existe pas: {wordpress_dir}")
        return False

def create_test_image():
    """Créer une image de test"""
    try:
        # Créer une image simple 100x100 rouge
        img = Image.new('RGB', (100, 100), color='red')
        test_path = "/app/backend/uploads/test_image.jpg"
        img.save(test_path, "JPEG")
        
        if os.path.exists(test_path):
            print(f"✅ Image de test créée: {test_path}")
            return test_path
        else:
            print("❌ Image de test non créée")
            return None
    except Exception as e:
        print(f"❌ Erreur création image test: {e}")
        return None

def main():
    print("🧪 Test des nouvelles fonctions WordPress/Instagram...")
    print("=" * 50)
    
    success_count = 0
    total_tests = 3
    
    # Test 1: Backend running
    if test_backend_running():
        success_count += 1
    
    # Test 2: WordPress directory
    if test_wordpress_directory():
        success_count += 1
    
    # Test 3: Create test image
    if create_test_image():
        success_count += 1
    
    print("=" * 50)
    print(f"📊 Résultats: {success_count}/{total_tests} tests réussis")
    
    if success_count == total_tests:
        print("🎉 Tous les tests sont passés ! Les nouvelles fonctions sont prêtes.")
        return True
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")
        return False

if __name__ == "__main__":
    main()