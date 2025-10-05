#!/usr/bin/env python3
"""
Test PATCH 31 - Correction variable 'files' Facebook vidéo + format n8n avec champ 'files'
"""

import requests
import json
import os

def test_patch31_video_fix():
    """Test publication vidéo Facebook sans erreur 'files' variable"""
    
    # URL de test
    webhook_url = "http://localhost:8001/api/webhook"
    
    # Test 1: Format n8n avec champ 'files' (nouvelle info utilisateur)
    print("\n🧪 TEST 1 - Format n8n avec champ 'files'")
    
    # Données de test avec URL WooCommerce (nouvelle info utilisateur)
    test_data = {
        "store": "gizmobbs", 
        "title": "Produit WooCommerce Test",
        "url": "https://www.logicamp.org/wordpress/produit/test-produit/",  # URL WooCommerce
        "description": "Test vidéo avec correction PATCH 31"
    }
    
    # Créer un fichier vidéo de test temporaire
    test_video_content = b"FAKE_MP4_CONTENT_FOR_TEST"
    
    try:
        # Envoi avec champ 'files' (pas 'file')
        files_data = {
            'jsonData': json.dumps(test_data),
            'files': ('test_video_patch31.mp4', test_video_content, 'video/mp4')
        }
        
        response = requests.post(webhook_url, files=files_data, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ Format n8n avec 'files' accepté")
        else:
            print(f"⚠️ Format n8n avec 'files': {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur test: {e}")
    
    # Test 2: Vérifier que le serveur ne crash plus avec vidéos
    print("\n🧪 TEST 2 - Publication vidéo (vérification pas de crash 'files')")
    
    try:
        # Test simple avec format direct
        form_data = {
            'store': 'gizmobbs',
            'title': 'Test vidéo PATCH 31', 
            'url': 'https://www.logicamp.org/wordpress/produit/test-video/',
            'description': 'Vérification correction variable files'
        }
        
        files_upload = {
            'file': ('test_patch31.mp4', test_video_content, 'video/mp4')
        }
        
        response = requests.post(webhook_url, data=form_data, files=files_upload, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        response_text = response.text
        
        # Vérifier qu'il n'y a plus l'erreur 'files'
        if "cannot access local variable 'files'" in response_text:
            print("❌ ÉCHEC: Erreur 'files' encore présente!")
        elif "Erreur publication Facebook:" in response_text and "files" in response_text:
            print("⚠️ Possibles autres erreurs 'files' détectées")
        else:
            print("✅ Pas d'erreur 'cannot access local variable files' détectée")
            
        print(f"📊 Response: {response_text[:500]}...")
        
    except Exception as e:
        print(f"❌ Erreur test vidéo: {e}")

if __name__ == "__main__":
    print("🔧 TEST PATCH 31 - Correction variable 'files' Facebook + format n8n")
    print("=" * 60)
    test_patch31_video_fix()
    print("\n✅ Tests terminés")