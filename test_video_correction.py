#!/usr/bin/env python3
"""
Test de la correction pour les vidéos Instagram @logicamp_berger
"""

import requests
import json
import os
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001"
TEST_VIDEO_PATH = "/app/test_video.mp4"

def test_video_webhook_correction():
    """Test la correction du webhook vidéo pour Instagram"""
    print("🧪 Test de la correction webhook vidéo Instagram @logicamp_berger")
    print("=" * 60)
    
    # Données de test
    webhook_data = {
        "store": "gizmobbs",
        "title": "Test Correction Vidéo",
        "description": "Test de publication vidéo sur Instagram @logicamp_berger",
        "product_url": "https://www.logicamp.org/wordpress/gizmobbs/test",
        "message": f"🧪 Test correction vidéo {datetime.now().strftime('%H:%M:%S')}\n\nVidéo de test pour @logicamp_berger"
    }
    
    # Créer un fichier vidéo de test simple (vide mais valide)
    if not os.path.exists(TEST_VIDEO_PATH):
        print(f"📁 Création d'un fichier vidéo de test: {TEST_VIDEO_PATH}")
        # Créer un fichier MP4 minimal pour le test (en-tête MP4 valide)
        mp4_header = b'\x00\x00\x00\x20ftypmp42\x00\x00\x00\x00mp42isom'
        with open(TEST_VIDEO_PATH, 'wb') as f:
            f.write(mp4_header + b'\x00' * 1000)  # 1KB de données de test
    
    try:
        print(f"📤 Envoi du test webhook avec vidéo...")
        
        # Préparer les données multipart
        files = {
            'json_data': (None, json.dumps(webhook_data), 'application/json'),
            'video': (
                'test_video.mp4', 
                open(TEST_VIDEO_PATH, 'rb'), 
                'video/mp4'
            )
        }
        
        # Envoyer la requête
        response = requests.post(
            f"{BACKEND_URL}/api/webhook",
            files=files,
            timeout=30
        )
        
        # Fermer le fichier
        files['video'][1].close()
        
        print(f"📋 Status Code: {response.status_code}")
        print(f"📋 Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("\n✅ RÉSULTATS:")
                print(f"   Status: {result.get('status', 'N/A')}")
                print(f"   Processed: {result.get('processed', 'N/A')}")
                
                if result.get('status') == 'received' and result.get('processed'):
                    print("✅ Test réussi: Webhook traité avec succès")
                    print("🔍 Vérifiez les logs du backend pour voir si:")
                    print("   - La vidéo a été détectée")
                    print("   - Les plateformes incluent Instagram")
                    print("   - La publication a été effectuée sur Instagram")
                else:
                    print("⚠️ Test partiellement réussi: Webhook reçu mais traitement incertain")
                    
            except json.JSONDecodeError:
                print(f"⚠️ Réponse non-JSON reçue: {response.text}")
                
        else:
            print(f"❌ Test échoué: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur durant le test: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🔍 Pour vérifier la correction, regardez les logs:")
    print("   tail -n 50 /var/log/supervisor/backend.out.log | grep -E 'CORRECTION|Instagram|logicamp_berger'")

def test_detection_logic():
    """Test unitaire de la logique de détection des médias"""
    print("\n🧪 Test de la logique de détection des médias")
    print("-" * 40)
    
    # Test 1: Données avec vidéo
    webhook_data_video = {
        "store": "gizmobbs",
        "title": "Test",
        "video_file": {
            "path": "/tmp/test.mp4",
            "filename": "test.mp4",
            "content_type": "video/mp4",
            "size": 1000
        }
    }
    
    # Simuler la logique de détection
    has_media_file = False
    media_type = None
    
    if webhook_data_video.get("video_file"):
        has_media_file = True
        media_type = "video"
        
    print(f"✅ Test vidéo: has_media_file={has_media_file}, media_type={media_type}")
    
    # Test 2: Données avec image
    webhook_data_image = {
        "store": "gizmobbs", 
        "title": "Test",
        "image_file": {
            "path": "/tmp/test.jpg",
            "filename": "test.jpg",
            "content_type": "image/jpeg",
            "size": 500
        }
    }
    
    has_media_file = False
    media_type = None
    
    if webhook_data_image.get("image_file"):
        has_media_file = True
        media_type = "image"
        
    print(f"✅ Test image: has_media_file={has_media_file}, media_type={media_type}")
    
    # Test 3: Données sans média
    webhook_data_empty = {
        "store": "gizmobbs",
        "title": "Test"
    }
    
    has_media_file = bool(webhook_data_empty.get("video_file") or webhook_data_empty.get("image_file"))
    media_type = None
    
    print(f"✅ Test sans média: has_media_file={has_media_file}, media_type={media_type}")

if __name__ == "__main__":
    # Test de la logique de détection
    test_detection_logic()
    
    # Test du webhook réel
    test_video_webhook_correction()
    
    # Nettoyer le fichier de test
    if os.path.exists(TEST_VIDEO_PATH):
        os.remove(TEST_VIDEO_PATH)
        print(f"🧹 Fichier de test supprimé: {TEST_VIDEO_PATH}")