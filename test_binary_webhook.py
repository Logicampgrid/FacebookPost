#!/usr/bin/env python3
"""
Test du nouveau webhook binary pour N8N
"""

import requests
import base64
from PIL import Image
import io
import json

# Créer une image de test simple
def create_test_image():
    """Créer une image de test en mémoire et retourner les données base64"""
    # Créer une image RGB simple plus petite
    img = Image.new('RGB', (200, 150), color=(70, 130, 180))  # SteelBlue plus petit
    
    # Ajouter du texte (si PIL supporte le texte)
    try:
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        # Utiliser une police par défaut
        draw.text((50, 50), "Test Product Image", fill=(255, 255, 255))
        draw.text((50, 100), "Generated for N8N Binary Webhook Test", fill=(255, 255, 255))
    except:
        # Pas grave si on ne peut pas ajouter de texte
        pass
    
    # Convertir en bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG', quality=90)
    img_bytes = img_buffer.getvalue()
    
    # Encoder en base64
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    return img_base64, len(img_bytes)

def test_binary_webhook():
    """Test le webhook binary avec une image de test"""
    
    print("🧪 Test du webhook binary N8N...")
    
    # Créer une image de test
    image_data, image_size = create_test_image()
    
    # Données de test selon le format N8N
    test_data = {
        "filename": "test_product_image.jpg",
        "mimetype": "image/jpeg",
        "comment": "Découvrez ce produit dans notre boutique !",
        "link": "https://www.logicamp.org/wordpress/gizmobbs/",
        "data": image_data
    }
    
    print(f"📊 Image de test créée: {len(image_data)} caractères base64, {image_size} bytes")
    print(f"📁 Nom de fichier: {test_data['filename']}")
    print(f"🔗 Lien: {test_data['link']}")
    print(f"💬 Commentaire: {test_data['comment']}")
    
    # Test GET pour info
    print("\n📋 Test GET /api/webhook/binary pour info...")
    try:
        response = requests.get("http://localhost:8001/api/webhook/binary")
        if response.status_code == 200:
            info = response.json()
            print(f"✅ GET endpoint OK: {info.get('message', 'No message')}")
        else:
            print(f"❌ GET failed: {response.status_code}")
    except Exception as e:
        print(f"❌ GET error: {e}")
    
    # Test POST avec données binaires
    print("\n📤 Test POST /api/webhook/binary avec image...")
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            "http://localhost:8001/api/webhook/binary", 
            json=test_data,
            headers=headers,
            timeout=30
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"📋 Message: {result.get('message', 'No message')}")
            
            if 'data' in result:
                data = result['data']
                print(f"📸 Facebook Post ID: {data.get('facebook_post_id', 'None')}")
                print(f"📱 Instagram Post ID: {data.get('instagram_post_id', 'None')}")
                print(f"🏪 Shop Type: {data.get('shop_type', 'None')}")
                print(f"📄 Page: {data.get('page_name', 'None')}")
                print(f"📁 Generated Image URL: {data.get('generated_image_url', 'None')}")
                print(f"📝 Generated Title: {data.get('generated_title', 'None')}")
                
                if 'publication_summary' in data:
                    summary = data['publication_summary']
                    print(f"📊 Publications réussies: {summary.get('total_published', 0)}")
                    print(f"❌ Publications échouées: {summary.get('total_failed', 0)}")
        else:
            print("❌ FAILED!")
            try:
                error_result = response.json()
                print(f"💥 Error: {error_result}")
            except:
                print(f"💥 Error: {response.text}")
                
    except Exception as e:
        print(f"💥 POST error: {e}")

if __name__ == "__main__":
    test_binary_webhook()