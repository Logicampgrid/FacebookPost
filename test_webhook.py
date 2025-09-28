#!/usr/bin/env python3
"""
Script de test pour le nouveau endpoint webhook
"""
import requests
import json
import os
from pathlib import Path

def test_webhook_endpoint():
    """Test simple du nouveau endpoint webhook"""
    print("🧪 Test du nouvel endpoint webhook /api/webhook")
    
    # URL du serveur (localhost pour test)
    base_url = "http://localhost:8001"
    webhook_url = f"{base_url}/api/webhook"
    
    # Données de test
    test_data = {
        "store": "gizmobbs",  # Store de test prioritaire
        "title": "Test Webhook - Produit Test",
        "url": "https://example.com/produit-test",
        "description": "Description test du produit via webhook automatique"
    }
    
    # Créer un fichier image de test simple
    test_image_path = "/app/backend/test_webhook_image.jpg"
    if not os.path.exists(test_image_path):
        # Créer une image de test basique (1x1 pixel blanc JPEG)
        with open(test_image_path, "wb") as f:
            # En-tête JPEG minimal
            jpeg_header = bytes([
                0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
                0x01, 0x01, 0x00, 0x48, 0x00, 0x48, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
                0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
                0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
                0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
                0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
                0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
                0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x11, 0x08, 0x00, 0x01,
                0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0x02, 0x11, 0x01, 0x03, 0x11, 0x01,
                0xFF, 0xC4, 0x00, 0x14, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0xFF, 0xC4,
                0x00, 0x14, 0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xDA, 0x00, 0x0C,
                0x03, 0x01, 0x00, 0x02, 0x11, 0x03, 0x11, 0x00, 0x3F, 0x00, 0xAA, 0xFF, 0xD9
            ])
            f.write(jpeg_header)
        print(f"✅ Image de test créée: {test_image_path}")
    
    # Test de l'endpoint
    try:
        print(f"📤 Envoi de la requête vers: {webhook_url}")
        print(f"📋 Données: {json.dumps(test_data, indent=2)}")
        
        # Préparer les fichiers et données
        files = {
            'file': ('test_image.jpg', open(test_image_path, 'rb'), 'image/jpeg')
        }
        
        # Faire la requête POST
        response = requests.post(webhook_url, data=test_data, files=files, timeout=30)
        
        # Fermer le fichier
        files['file'][1].close()
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ Réponse JSON reçue:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                # Analyser les résultats
                if result.get("success"):
                    print("✅ Webhook traité avec succès!")
                    
                    # Vérifier les publications
                    publications = result.get("publications", {})
                    fb_result = publications.get("facebook", {})
                    ig_result = publications.get("instagram", {})
                    
                    if fb_result.get("success"):
                        print("📱 ✅ Publication Facebook réussie")
                    else:
                        print(f"📱 ❌ Publication Facebook échouée: {fb_result.get('error', 'Erreur inconnue')}")
                    
                    if ig_result.get("success"):
                        print("📸 ✅ Publication Instagram réussie")
                    else:
                        print(f"📸 ❌ Publication Instagram échouée: {ig_result.get('error', 'Erreur inconnue')}")
                else:
                    print(f"❌ Webhook échoué: {result.get('message', 'Erreur inconnue')}")
                    
            except json.JSONDecodeError:
                print("⚠️ Réponse non-JSON reçue:")
                print(response.text)
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("💡 Assurez-vous que le serveur FastAPI est démarré sur localhost:8001")
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
    
    print("\n🏁 Test terminé")

if __name__ == "__main__":
    test_webhook_endpoint()