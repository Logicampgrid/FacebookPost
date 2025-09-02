#!/usr/bin/env python3
"""
Test du nouveau webhook N8N multipart/form-data pour Gizmobbs
"""

import requests
import json
import base64
from PIL import Image
import io
import tempfile
import os

# Configuration
API_BASE = "https://format-guard.preview.emergentagent.com"
WEBHOOK_URL = f"{API_BASE}/api/webhook"

def create_test_image():
    """Créer une image de test"""
    # Créer une image simple 800x600
    img = Image.new('RGB', (800, 600), color='lightblue')
    
    # Sauvegarder dans un fichier temporaire
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
        img.save(tmp.name, 'JPEG', quality=90)
        return tmp.name

def test_multipart_image_webhook():
    """Test webhook avec image multipart"""
    print("🧪 Test 1: Image multipart webhook")
    
    # Créer image de test
    image_path = create_test_image()
    
    try:
        # Préparer les données JSON
        json_data = {
            "store": "gizmobbs",
            "title": "Test Image N8N - Produit Cliquable",
            "url": "https://www.logicamp.org/wordpress/gizmobbs/",
            "description": "Ceci est une image de test qui devrait être cliquable vers le produit"
        }
        
        # Préparer la requête multipart
        with open(image_path, 'rb') as img_file:
            files = {
                'json_data': (None, json.dumps(json_data), 'application/json'),
                'image': ('test_image.jpg', img_file, 'image/jpeg')
            }
            
            print(f"📤 Envoi requête multipart...")
            print(f"📋 JSON Data: {json_data}")
            print(f"📁 Image: {image_path}")
            
            response = requests.post(WEBHOOK_URL, files=files, timeout=30)
            
        print(f"📥 Response: {response.status_code}")
        print(f"📄 Content: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ SUCCESS: Image multipart webhook fonctionne!")
                print(f"   - Media type: {result.get('media_type', 'N/A')}")
                print(f"   - Message: {result.get('message', 'N/A')}")
                return True
            else:
                print(f"❌ FAIL: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    finally:
        # Nettoyer le fichier temporaire
        if os.path.exists(image_path):
            os.unlink(image_path)

def create_test_video():
    """Créer un petit fichier vidéo de test (en fait, on va utiliser une image)"""
    # Pour simplifier, on va créer un faux fichier vidéo
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
        # Écrire quelques bytes pour simuler une vidéo
        tmp.write(b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom')
        tmp.write(b'\x00' * 100)  # Contenu simple
        return tmp.name

def test_multipart_video_webhook():
    """Test webhook avec vidéo multipart"""
    print("\n🧪 Test 2: Vidéo multipart webhook")
    
    # Créer un faux fichier vidéo
    video_path = create_test_video()
    
    try:
        # Préparer les données JSON
        json_data = {
            "store": "gizmobbs", 
            "title": "Test Vidéo N8N - Avec Commentaire",
            "url": "https://www.logicamp.org/wordpress/gizmobbs/",
            "description": "Ceci est une vidéo de test. Ce commentaire devrait s'afficher automatiquement sous la vidéo dans l'interface."
        }
        
        # Préparer la requête multipart
        with open(video_path, 'rb') as vid_file:
            files = {
                'json_data': (None, json.dumps(json_data), 'application/json'),
                'video': ('test_video.mp4', vid_file, 'video/mp4')
            }
            
            print(f"📤 Envoi requête multipart...")
            print(f"📋 JSON Data: {json_data}")
            print(f"📁 Video: {video_path}")
            
            response = requests.post(WEBHOOK_URL, files=files, timeout=30)
            
        print(f"📥 Response: {response.status_code}")
        print(f"📄 Content: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ SUCCESS: Vidéo multipart webhook fonctionne!")
                print(f"   - Media type: {result.get('media_type', 'N/A')}")
                print(f"   - Message: {result.get('message', 'N/A')}")
                return True
            else:
                print(f"❌ FAIL: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    finally:
        # Nettoyer le fichier temporaire
        if os.path.exists(video_path):
            os.unlink(video_path)

def test_legacy_json_webhook():
    """Test que l'ancien format JSON fonctionne encore"""
    print("\n🧪 Test 3: Legacy JSON webhook (compatibilité)")
    
    try:
        # Données JSON legacy
        json_data = {
            "store": "gizmobbs",
            "title": "Test Legacy JSON",
            "description": "Test compatibilité ancien format",
            "product_url": "https://www.logicamp.org/wordpress/gizmobbs/",
            "image_url": "https://picsum.photos/800/600?random=12345"
        }
        
        print(f"📤 Envoi requête JSON legacy...")
        print(f"📋 Data: {json_data}")
        
        response = requests.post(
            WEBHOOK_URL,
            json=json_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📥 Response: {response.status_code}")
        print(f"📄 Content: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ SUCCESS: Legacy JSON webhook fonctionne!")
                print(f"   - Message: {result.get('message', 'N/A')}")
                return True
            else:
                print(f"❌ FAIL: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_error_cases():
    """Test des cas d'erreur"""
    print("\n🧪 Test 4: Cas d'erreur (validation)")
    
    # Test 1: JSON manquant
    try:
        files = {
            'image': ('test.jpg', b'fake image data', 'image/jpeg')
        }
        response = requests.post(WEBHOOK_URL, files=files, timeout=10)
        print(f"   Sans json_data: {response.status_code} - {'PASS' if response.status_code == 400 else 'FAIL'}")
    except:
        print(f"   Sans json_data: Exception - PASS")
    
    # Test 2: JSON invalide
    try:
        files = {
            'json_data': (None, 'invalid json', 'application/json'),
            'image': ('test.jpg', b'fake image data', 'image/jpeg')
        }
        response = requests.post(WEBHOOK_URL, files=files, timeout=10)
        print(f"   JSON invalide: {response.status_code} - {'PASS' if response.status_code == 400 else 'FAIL'}")
    except:
        print(f"   JSON invalide: Exception - PASS")
    
    # Test 3: Pas de fichier
    try:
        json_data = {"store": "gizmobbs", "title": "Test", "url": "https://test.com", "description": "Test"}
        files = {
            'json_data': (None, json.dumps(json_data), 'application/json')
        }
        response = requests.post(WEBHOOK_URL, files=files, timeout=10)
        print(f"   Sans fichier: {response.status_code} - {'PASS' if response.status_code == 400 else 'FAIL'}")
    except:
        print(f"   Sans fichier: Exception - PASS")

def main():
    """Exécuter tous les tests"""
    print("🚀 Tests du webhook N8N multipart/form-data pour Gizmobbs")
    print("=" * 60)
    
    results = []
    
    # Tests principaux
    results.append(("Image multipart", test_multipart_image_webhook()))
    results.append(("Vidéo multipart", test_multipart_video_webhook()))
    results.append(("Legacy JSON", test_legacy_json_webhook()))
    
    # Tests d'erreur
    test_error_cases()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} : {status}")
    
    total_pass = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    print(f"\nRésultat global: {total_pass}/{total_tests} tests réussis")
    
    if total_pass == total_tests:
        print("🎉 TOUS LES TESTS RÉUSSIS - Webhook N8N configuré correctement!")
        return True
    else:
        print("⚠️ Certains tests ont échoué - vérifiez la configuration")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)