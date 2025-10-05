#!/usr/bin/env python3
"""
Test PATCH 32 - Nouveau chemin FTP /www/wordpress/uploads/
"""

import requests
import json

def test_patch32_ftp_correction():
    """Test nouvelle configuration FTP avec chemin /www/wordpress/uploads/"""
    
    webhook_url = "http://localhost:8001/api/webhook"
    
    print("🔧 TEST PATCH 32 - Correction chemin FTP")
    print("=" * 50)
    
    # Test avec une image pour vérifier le nouvel upload FTP
    print("\n🧪 TEST - Upload image avec nouveau chemin FTP")
    
    test_data = {
        "store": "gizmobbs",
        "title": "Test PATCH 32 - Nouveau chemin FTP", 
        "url": "https://www.logicamp.org/wordpress/produit/test-ftp-path/",
        "description": "Test correction chemin /www/wordpress/uploads/"
    }
    
    # Image de test
    test_image = b"FAKE_IMAGE_CONTENT_PATCH32_TEST"
    
    try:
        files_data = {
            'jsonData': json.dumps(test_data),
            'files': ('test_patch32_ftp.jpg', test_image, 'image/jpeg')
        }
        
        print("📤 Envoi de la requête...")
        response = requests.post(webhook_url, files=files_data, timeout=15)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                print(f"📊 Response: {response_json}")
                
                # Chercher des indices sur l'URL générée
                if 'url' in str(response_json).lower() or 'ftp' in str(response_json).lower():
                    print("✅ Réponse contient des informations d'URL - vérifier les logs")
                else:
                    print("ℹ️ Pas d'URL visible dans la réponse - normal pour webhook")
                    
            except:
                print(f"📊 Response (text): {response.text[:200]}...")
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"📊 Response: {response.text[:200]}...")
            
        print("\n🔍 Vérifiez maintenant les logs backend pour voir:")
        print("  • Si l'upload FTP utilise /www/wordpress/uploads/")
        print("  • Si l'URL générée est accessible")
        print("  • Si Facebook/Instagram peuvent accéder aux images")
        
    except requests.exceptions.Timeout:
        print("⏰ Timeout - traitement en cours, vérifiez les logs")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_patch32_ftp_correction()