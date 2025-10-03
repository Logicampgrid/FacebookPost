#!/usr/bin/env python3
"""
PATCH 23 - Test des publications Facebook/Instagram
Test les problèmes identifiés dans les logs
"""

import sys
import os
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import (
    get_active_ngrok_url, publish_to_facebook, publish_to_instagram,
    get_store_config, FACEBOOK_GRAPH_URL
)

def test_ngrok_accessibility():
    """Test l'accessibilité de l'URL ngrok"""
    print("🔍 PATCH 23: Test accessibilité ngrok...")
    
    ngrok_url = get_active_ngrok_url()
    print(f"✅ URL ngrok active: {ngrok_url}")
    
    # Test avec une image existante
    test_image = f"{ngrok_url}/uploads/test_image.jpg"
    try:
        response = requests.head(test_image, timeout=10)
        print(f"📸 Test image: {test_image} → Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test image: {e}")
    
    # Test avec une vidéo existante
    test_video = f"{ngrok_url}/uploads/webhook_2d6648b1_1755463607.mp4"
    try:
        response = requests.head(test_video, timeout=10)
        print(f"🎥 Test vidéo: {test_video} → Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test vidéo: {e}")

def test_facebook_api():
    """Test direct de l'API Facebook"""
    print("\n🔍 PATCH 23: Test API Facebook...")
    
    try:
        store_config = get_store_config("gizmobbs")
        fb_page_id = store_config.get("fb_page_id")
        access_token = store_config.get("access_token")
        
        print(f"📱 Page ID: {fb_page_id}")
        print(f"🔑 Token disponible: {'Oui' if access_token else 'Non'}")
        
        if access_token:
            # Test simple avec texte seulement
            fb_url = f"{FACEBOOK_GRAPH_URL}/{fb_page_id}/feed"
            data = {
                "message": "Test PATCH 23 - Publication texte seulement",
                "access_token": access_token
            }
            
            print(f"🧪 Test publication texte sur: {fb_url}")
            # Ne pas publier vraiment en mode test
            print("ℹ️  Publication simulée (texte)")
            
            # Test avec image publique
            ngrok_url = get_active_ngrok_url()
            image_url = f"{ngrok_url}/uploads/test_image.jpg"
            
            fb_photo_url = f"{FACEBOOK_GRAPH_URL}/{fb_page_id}/photos"
            photo_data = {
                "message": "Test PATCH 23 - Publication avec image",
                "url": image_url,
                "access_token": access_token
            }
            
            print(f"🧪 Test publication image: {image_url}")
            print("ℹ️  Publication simulée (image)")
            
    except Exception as e:
        print(f"❌ Erreur test Facebook: {e}")

def test_instagram_api():
    """Test direct de l'API Instagram"""
    print("\n🔍 PATCH 23: Test API Instagram...")
    
    try:
        store_config = get_store_config("gizmobbs")
        ig_user_id = store_config.get("ig_user_id")
        access_token = store_config.get("access_token")
        
        print(f"📸 Instagram ID: {ig_user_id}")
        print(f"🔑 Token disponible: {'Oui' if access_token else 'Non'}")
        
        if access_token:
            ngrok_url = get_active_ngrok_url()
            image_url = f"{ngrok_url}/uploads/test_image.jpg"
            
            ig_url = f"{FACEBOOK_GRAPH_URL}/{ig_user_id}/media"
            data = {
                "caption": "Test PATCH 23 - Publication Instagram",
                "image_url": image_url,
                "access_token": access_token
            }
            
            print(f"🧪 Test création conteneur Instagram: {image_url}")
            print("ℹ️  Publication simulée (Instagram)")
            
    except Exception as e:
        print(f"❌ Erreur test Instagram: {e}")

def test_urls_from_logs():
    """Test les URLs spécifiques mentionnées dans les logs"""
    print("\n🔍 PATCH 23: Test URLs des logs d'erreur...")
    
    # URLs mentionnées dans les logs d'erreur
    test_urls = [
        "https://6885312f324f.ngrok-free.app/uploads/webhook_e9ac3760_1759516573.png",
        "https://6885312f324f.ngrok-free.app/uploads/webhook_3189541f_1759516706.mp4"
    ]
    
    for url in test_urls:
        try:
            response = requests.head(url, timeout=10)
            print(f"🌐 {url} → Status: {response.status_code}")
            if response.status_code != 200:
                print(f"   ❌ Problème d'accessibilité détecté!")
        except Exception as e:
            print(f"❌ {url} → Erreur: {e}")

if __name__ == "__main__":
    print("🚀 PATCH 23 - Diagnostic publications Facebook/Instagram")
    print("=" * 60)
    
    test_ngrok_accessibility()
    test_facebook_api()
    test_instagram_api()
    test_urls_from_logs()
    
    print("\n✅ PATCH 23: Tests terminés")