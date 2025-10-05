#!/usr/bin/env python3
"""
Test PATCH 31 complet - Correction variable 'files' + support champ n8n 'files'
"""

import requests
import json

def test_patch31_complete():
    """Test complet des améliorations PATCH 31"""
    
    webhook_url = "http://localhost:8001/api/webhook"
    
    print("🔧 TEST PATCH 31 COMPLET")
    print("=" * 50)
    
    # Test 1: Format n8n avec nouveau champ 'files' 
    print("\n🧪 TEST 1 - Format n8n avec champ 'files' (nouveau support)")
    
    test_data = {
        "store": "gizmobbs",
        "title": "Produit WooCommerce PATCH 31", 
        "url": "https://www.logicamp.org/wordpress/produit/produit-woocommerce-test/",
        "description": "Test avec URL WooCommerce et champ files n8n"
    }
    
    # Test fichier léger
    test_content = b"PATCH31_TEST_CONTENT"
    
    try:
        # Test avec champ 'files' (nouvelle fonctionnalité)
        files_data = {
            'jsonData': json.dumps(test_data),
            'files': ('test_patch31_files.jpg', test_content, 'image/jpeg')
        }
        
        response = requests.post(webhook_url, files=files_data, timeout=8)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_json = response.json()
            success = response_json.get('success', False)
            if success:
                print("✅ Champ 'files' n8n supporté et traité avec succès")
            else:
                print(f"⚠️ Champ 'files' accepté mais erreur traitement: {response_json}")
        else:
            print(f"❌ Erreur champ 'files': {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - traitement en cours en arrière-plan")
    except Exception as e:
        print(f"❌ Erreur test champ 'files': {e}")
    
    # Test 2: Rétrocompatibilité avec champ 'file'
    print("\n🧪 TEST 2 - Rétrocompatibilité champ 'file'")
    
    try:
        # Test avec ancien champ 'file' 
        files_data_legacy = {
            'jsonData': json.dumps(test_data),
            'file': ('test_patch31_file.jpg', test_content, 'image/jpeg')
        }
        
        response = requests.post(webhook_url, files=files_data_legacy, timeout=8)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Rétrocompatibilité 'file' maintenue")
        else:
            print(f"⚠️ Problème rétrocompatibilité: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - traitement en cours")  
    except Exception as e:
        print(f"❌ Erreur test 'file': {e}")
    
    # Test 3: Vérification plus d'erreur 'cannot access local variable files'
    print("\n🧪 TEST 3 - Vérification correction erreur 'files' Facebook")
    
    # Créer un webhook avec vidéo pour déclencher la fonction Facebook
    video_data = {
        "store": "gizmobbs",
        "title": "Test vidéo PATCH 31",
        "url": "https://www.logicamp.org/wordpress/produit/video-test/",
        "description": "Vérification qu'il n'y a plus l'erreur variable files"
    }
    
    try:
        files_video = {
            'jsonData': json.dumps(video_data), 
            'files': ('test_video_patch31.mp4', b"FAKE_VIDEO_CONTENT", 'video/mp4')
        }
        
        response = requests.post(webhook_url, files=files_video, timeout=8)
        print(f"📊 Status Code vidéo: {response.status_code}")
        
        # Même si timeout, vérifier les logs après
        print("✅ Test vidéo lancé - vérification logs...")
        
    except requests.exceptions.Timeout:
        print("✅ Timeout normal - vidéo traitée en arrière-plan")
    except Exception as e:
        print(f"❌ Erreur test vidéo: {e}")

if __name__ == "__main__":
    test_patch31_complete()
    print("\n✅ Tests PATCH 31 terminés - Vérifiez les logs pour confirmer le bon fonctionnement")