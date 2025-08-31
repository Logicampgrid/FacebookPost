#!/usr/bin/env python3
"""
Test du webhook avec un fichier média pour vérifier les corrections Instagram
"""

import requests
import json
import os

# Configuration
BASE_URL = "http://localhost:8001"
WEBHOOK_URL = f"{BASE_URL}/api/webhook"

def test_webhook_with_image():
    """Test du webhook avec une image"""
    print("🧪 Test avec image pour Instagram")
    
    test_data = {
        "store": "logicampoutdoor",  # Test du store qui avait des problèmes
        "title": "Test Image Instagram Fix",
        "description": "Test pour vérifier les corrections Instagram avec image",
        "url": "https://example.com/test-image"
    }
    
    # Créer une petite image de test
    test_image_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
    
    files = {
        "json_data": (None, json.dumps(test_data)),
        "image": ("test.jpg", test_image_content, "image/jpeg")
    }
    
    try:
        print(f"📤 Envoi vers {WEBHOOK_URL} avec store: {test_data['store']}")
        response = requests.post(WEBHOOK_URL, files=files, timeout=60)
        print(f"📨 Status: HTTP {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Succès: {result.get('message', 'OK')}")
            
            # Analyser les résultats par plateforme
            if 'routing_result' in result:
                routing = result['routing_result']
                
                # Facebook
                fb_success = routing.get('facebook', {}).get('success', False)
                print(f"📘 Facebook: {'✅ Succès' if fb_success else '❌ Échec'}")
                if not fb_success:
                    fb_error = routing.get('facebook', {}).get('error', 'Unknown')
                    print(f"   Erreur: {fb_error}")
                else:
                    fb_post_id = routing.get('facebook', {}).get('post_id')
                    print(f"   Post ID: {fb_post_id}")
                
                # Instagram  
                ig_success = routing.get('instagram', {}).get('success', False)
                print(f"📱 Instagram: {'✅ Succès' if ig_success else '❌ Échec'}")
                if not ig_success:
                    ig_error = routing.get('instagram', {}).get('error', 'Unknown')
                    print(f"   Erreur: {ig_error}")
                else:
                    ig_post_id = routing.get('instagram', {}).get('post_id')
                    print(f"   Post ID: {ig_post_id}")
                
                # Statistiques globales
                print(f"📊 Plateformes réussies: {routing.get('platforms_successful', 0)}/{routing.get('platforms_attempted', 0)}")
                print(f"⏱️ Temps d'exécution: {routing.get('execution_time', 0):.2f}s")
            
        elif response.status_code == 500:
            try:
                error_data = response.json()
                error_msg = error_data.get("detail", "Unknown server error")
                print(f"💥 Erreur serveur: {error_msg}")
            except:
                print(f"💥 Erreur serveur: {response.text}")
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get("detail", "Unknown error")
                print(f"❌ Erreur: {error_msg}")
            except:
                print(f"❌ Erreur: {response.text}")
                
    except requests.exceptions.Timeout:
        print("⏰ Timeout - Le serveur prend trop de temps à répondre")
    except Exception as e:
        print(f"❌ Erreur de requête: {str(e)}")

def test_all_stores():
    """Test rapide de tous les stores"""
    print("\n🧪 Test rapide de tous les stores avec image")
    
    stores = ["gizmobbs", "logicantiq", "outdoor", "logicampoutdoor"]
    test_image_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
    
    for store in stores:
        print(f"\n🏪 Test store: {store}")
        
        test_data = {
            "store": store,
            "title": f"Test {store}",
            "description": f"Test Instagram pour {store}",
            "url": f"https://example.com/test-{store}"
        }
        
        files = {
            "json_data": (None, json.dumps(test_data)),
            "image": ("test.jpg", test_image_content, "image/jpeg")
        }
        
        try:
            response = requests.post(WEBHOOK_URL, files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                routing = result.get('routing_result', {})
                fb_success = routing.get('facebook', {}).get('success', False)
                ig_success = routing.get('instagram', {}).get('success', False)
                print(f"  Facebook: {'✅' if fb_success else '❌'} | Instagram: {'✅' if ig_success else '❌'}")
                
                if not ig_success:
                    ig_error = routing.get('instagram', {}).get('error', 'Unknown')
                    print(f"  Instagram error: {ig_error}")
            else:
                print(f"  ❌ HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"  ⏰ Timeout")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Test des corrections Instagram avec fichiers média")
    print("=" * 60)
    
    test_webhook_with_image()
    test_all_stores()
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")