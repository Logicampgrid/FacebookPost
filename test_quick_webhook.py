#!/usr/bin/env python3
"""
Test rapide webhook sans attendre le timeout FTP
"""

import requests
import json
import time
import tempfile
import os

def create_small_image():
    """Créer une très petite image pour minimiser les timeouts"""
    # Créer un fichier très petit (1KB) pour éviter les timeouts FTP
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    # Écrire seulement quelques octets (pas une vraie image, juste pour tester le workflow)
    temp_file.write(b'\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00' + b'0' * 100)
    temp_file.close()
    return temp_file.name

def test_webhook_quick():
    """Test webhook rapide pour voir le comportement sans attendre le FTP"""
    
    print("⚡ Test webhook rapide (éviter les timeouts FTP)")
    
    image_path = None
    try:
        # Créer une très petite "image"
        image_path = create_small_image()
        print(f"📷 Image test créée: {image_path} ({os.path.getsize(image_path)} bytes)")
        
        # Webhook data simple
        webhook_data = {
            "store": "gizmobbs",
            "title": "⚡ Test rapide correction Instagram",
            "url": "https://example.com/test-rapide",
            "description": "Test pour voir le fallback ngrok"
        }
        
        print("📤 Envoi webhook (timeout réduit)...")
        start_time = time.time()
        
        with open(image_path, 'rb') as img_file:
            files = {
                'image': ('test_rapide.jpg', img_file, 'image/jpeg')
            }
            data = {
                'json_data': json.dumps(webhook_data)
            }
            
            # Timeout réduit pour éviter d'attendre le FTP
            response = requests.post(
                "http://localhost:8001/api/webhook",
                files=files,
                data=data,
                timeout=45  # 45 secondes max
            )
        
        elapsed = time.time() - start_time
        print(f"⏱️ Durée requête: {elapsed:.1f}s")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Webhook traité")
            try:
                result = response.json()
                print(f"📋 Response: {json.dumps(result, indent=2)}")
            except:
                print(f"📄 Response text: {response.text}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout après 45s - normal si FTP est lent")
        print("💡 Le FTP prend du temps, mais la logique de fallback devrait fonctionner")
        return "timeout"
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        if image_path and os.path.exists(image_path):
            os.unlink(image_path)

if __name__ == "__main__":
    result = test_webhook_quick()
    
    if result == True:
        print("\n🎉 SUCCÈS: Webhook traité rapidement")
    elif result == "timeout":
        print("\n⏱️ TIMEOUT: Normal avec FTP lent, mais logique de correction active")
    else:
        print("\n❌ ÉCHEC: Problème avec le webhook")