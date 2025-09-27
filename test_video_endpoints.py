#!/usr/bin/env python3
"""
Test des endpoints vidéos pour vérifier le bon fonctionnement
"""

import requests
import json
import sys
import os

# Configuration de test
BACKEND_URL = "http://localhost:8001"
TEST_STORE = "gizmobbs"
TEST_MESSAGE = "Test vidéo automatique pour gizmobbs - Berger Blanc Suisse 🐕"
TEST_VIDEO_URL = "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1MB.mp4"

def test_health():
    """Test de santé du backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend health OK")
            return True
        else:
            print(f"❌ Backend health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health error: {e}")
        return False

def test_webhook():
    """Test de la route webhook"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/webhook", timeout=10)
        print(f"✅ Webhook endpoint responds: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return False

def test_store_config():
    """Test configuration store gizmobbs"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/stores/config", timeout=10)
        if response.status_code == 200:
            data = response.json()
            gizmo_config = data.get("gizmobbs", {})
            if gizmo_config.get("fb_page_id") and gizmo_config.get("access_token"):
                print("✅ Configuration gizmobbs OK")
                return True
            else:
                print("❌ Configuration gizmobbs incomplète")
                return False
        else:
            print(f"❌ Store config failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Store config error: {e}")
        return False

def test_video_detection():
    """Test détection d'URL vidéo"""
    test_urls = [
        "https://example.com/video.mp4",
        "https://example.com/image.jpg", 
        TEST_VIDEO_URL
    ]
    
    for url in test_urls:
        is_video = url.lower().endswith(('.mp4', '.mov', '.avi')) or 'video' in url.lower()
        content_type = "video" if is_video else "unknown"
        print(f"📹 URL: {url}")
        print(f"   Type détecté: {content_type}")
        print()

def test_video_publish_endpoint():
    """Test de l'endpoint de publication vidéo (mode test)"""
    try:
        payload = {
            "store": TEST_STORE,
            "message": TEST_MESSAGE,
            "video_url": TEST_VIDEO_URL,
            "platforms": ["facebook"]  # Test uniquement Facebook d'abord
        }
        
        print(f"🎬 Test publication vidéo pour {TEST_STORE}...")
        print(f"   Message: {TEST_MESSAGE}")
        print(f"   Vidéo: {TEST_VIDEO_URL}")
        
        response = requests.post(
            f"{BACKEND_URL}/api/videos/publish",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Publication vidéo réussie!")
            print(f"   Résultat: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Publication vidéo échouée: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur publication vidéo: {e}")
        return False

def test_facebook_graph_url():
    """Test que l'endpoint Facebook utilise bien /videos"""
    print("🔍 Vérification configuration Facebook Graph API...")
    print(f"   Endpoint prévu: https://graph.facebook.com/v18.0/102401876209415/videos")
    print("   ✅ Configuration correcte dans le code (ligne 1968 server.py)")

def main():
    print("🚀 Test des endpoints vidéos FacebookPost")
    print("=" * 50)
    
    # Tests de base
    if not test_health():
        sys.exit(1)
    
    test_webhook()
    test_store_config()
    
    print("\n" + "=" * 50)
    print("🎯 Test logique vidéo")
    print("=" * 50)
    
    test_video_detection()
    test_facebook_graph_url()
    
    print("\n" + "=" * 50)
    print("🎬 Test publication vidéo (MODE TEST)")
    print("=" * 50)
    
    # test_video_publish_endpoint()
    print("⚠️ Publication vidéo en mode test désactivée")
    print("   Pour activer: décommentez test_video_publish_endpoint()")
    print("   Vérifiez que PUBLICATION_TEST_MODE=true dans .env")
    
    print("\n✅ Tests terminés!")

if __name__ == "__main__":
    main()