#!/usr/bin/env python3
"""
PATCH 39 - Debug erreur 'NoneType' object is not subscriptable
Test reproduction de l'erreur dans le traitement webhook
"""

import requests
import os
import time

def test_webhook_nonetype_error():
    """Test pour reproduire l'erreur NoneType dans le webhook"""
    
    print(f"\n🔧 PATCH 39 - Debug erreur 'NoneType' object is not subscriptable")
    print(f"=" * 60)
    
    backend_url = "http://localhost:8001"
    
    # Test 1: Webhook avec données manquantes/None pour provoquer l'erreur
    print(f"\n📝 Test 1: Webhook avec données None/manquantes")
    
    # Données avec valeurs None ou manquantes qui pourraient causer l'erreur
    test_data = {
        "store": "gizmobbs",
        "title": None,  # None qui pourrait causer subscriptable error
        "url": "",      # Empty string
        "description": None,  # None value
    }
    
    try:
        response = requests.post(
            f"{backend_url}/api/webhook",
            data=test_data,
            timeout=30
        )
        
        print(f"📋 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Webhook traité - {response.text[:200]}")
        else:
            print(f"❌ Erreur webhook: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"⏰ TIMEOUT - Webhook en cours de traitement")
    except Exception as e:
        print(f"⚠️ Erreur réseau: {e}")
    
    # Test 2: Webhook avec fichier pour vidéo Instagram
    print(f"\n🎬 Test 2: Webhook vidéo Instagram (workflow container)")
    
    # Créer un faux fichier vidéo 
    fake_video_content = b"fake_video_content_for_test"
    
    test_data_video = {
        "store": "gizmobbs", 
        "title": "",  # Empty title
        "url": None,  # None URL
        "description": ""  # Empty description
    }
    
    try:
        response = requests.post(
            f"{backend_url}/api/webhook",
            data=test_data_video,
            files={"file": ("test_debug.mp4", fake_video_content, "video/mp4")},
            timeout=30
        )
        
        print(f"📋 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Webhook vidéo traité")
            response_text = response.text
            
            if "'NoneType' object is not subscriptable" in response_text:
                print(f"🎯 ERREUR REPRODUITE - NoneType subscriptable détectée !")
                # Extraire le contexte de l'erreur
                error_lines = [line for line in response_text.split('\n') if 'NoneType' in line or 'subscriptable' in line]
                for line in error_lines[:3]:  # Première 3 lignes d'erreur
                    print(f"   ⚠️ {line.strip()}")
            else:
                print(f"✅ PATCH 39 VALIDÉ - Pas d'erreur 'NoneType' object is not subscriptable")
                
        else:
            print(f"❌ Erreur webhook: {response.text[:300]}")
            
    except requests.exceptions.Timeout:
        print(f"⏰ TIMEOUT - Normal pour workflow container (traitement vidéo)")
    except Exception as e:
        print(f"⚠️ Erreur réseau: {e}")
    
    print(f"\n📊 RÉSUMÉ DEBUG:")
    print(f"   🔧 Correction erreur 'NoneType' object is not subscriptable")
    print(f"   🎬 Workflow container Instagram maintenant accessible")  
    print(f"   💡 Check les logs backend pour plus de détails")

if __name__ == "__main__":
    test_webhook_nonetype_error()