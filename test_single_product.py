#!/usr/bin/env python3
"""
Test rapide d'un seul produit avec le nouveau webhook
"""

import requests
import json
from PIL import Image
import io

def create_test_product():
    """Créer une image de produit de test"""
    img = Image.new('RGB', (400, 300), color=(139, 69, 19))  # Couleur bois
    
    try:
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.text((50, 100), "Chaise Design", fill=(255, 255, 255))
        draw.text((50, 130), "Ma Boutique", fill=(255, 255, 255))
        draw.text((50, 160), "Premium Quality", fill=(255, 255, 255))
    except:
        pass
    
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG', quality=90)
    return img_buffer.getvalue()

def test_single_product():
    """Test avec un seul produit"""
    print("🧪 Test Produit Unique - Webhook Enhancé")
    print("=" * 50)
    
    # Créer l'image de test
    image_data = create_test_product()
    filename = "chaise_design_ma_boutique.jpg"
    
    # Simulation exacte de votre transformation N8N
    json_data = {
        "store": "ma-boutique",
        "title": filename,
        "description": "Découvrez ce produit dans notre boutique !",
        "product_url": "https://www.logicamp.org/wordpress/gizmobbs/",
        "comment": "Découvrez ce produit dans notre boutique !"
    }
    
    print(f"📦 Produit: {filename}")
    print(f"🏪 Store: {json_data['store']}")
    print(f"📁 Image size: {len(image_data)} bytes")
    print(f"📝 JSON data: {json.dumps(json_data, indent=2)}")
    
    # Préparer la requête multipart
    files = {
        'json_data': (None, json.dumps(json_data), 'application/json'),
        'image': (filename, image_data, 'image/jpeg')
    }
    
    print(f"\n📡 Envoi vers webhook enhancé...")
    
    try:
        response = requests.post(
            "http://localhost:8001/api/webhook/enhanced",
            files=files,
            timeout=60
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"📋 Message: {result.get('message', 'No message')}")
            
            if 'data' in result:
                data = result['data']
                print(f"\n📊 Détails de publication:")
                print(f"   📸 Facebook Post ID: {data.get('facebook_post_id', 'None')}")
                print(f"   📱 Instagram Post ID: {data.get('instagram_post_id', 'None')}")
                print(f"   🏪 Store: {data.get('store', 'None')}")
                print(f"   📄 Page: {data.get('page_name', 'None')}")
                print(f"   📁 Image URL: {data.get('generated_image_url', 'None')}")
                print(f"   📝 Original Filename: {data.get('original_filename', 'None')}")
                print(f"   🎯 Enhanced Webhook: {data.get('enhanced_webhook', False)}")
                print(f"   📅 Published At: {data.get('published_at', 'None')}")
                
                if 'publication_summary' in data:
                    summary = data['publication_summary']
                    print(f"\n📈 Résumé de publication:")
                    print(f"   ✅ Réussies: {summary.get('total_published', 0)}")
                    print(f"   ❌ Échouées: {summary.get('total_failed', 0)}")
        else:
            print("❌ FAILED!")
            try:
                error_result = response.json()
                print(f"💥 Error: {json.dumps(error_result, indent=2)}")
            except:
                print(f"💥 Error: {response.text}")
        
    except Exception as e:
        print(f"💥 Exception: {e}")
    
    print(f"\n🎯 WEBHOOK ENHANCÉ PRÊT POUR N8N!")

if __name__ == "__main__":
    test_single_product()