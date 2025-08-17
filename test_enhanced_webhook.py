#!/usr/bin/env python3
"""
Test du nouveau webhook enhancé pour N8N avec format json/binary séparé
"""

import requests
import json
from PIL import Image
import io

def create_test_image():
    """Créer une image de test en mémoire"""
    # Créer une image RGB simple 
    img = Image.new('RGB', (400, 300), color=(70, 130, 180))  # SteelBlue
    
    # Ajouter du texte (si PIL supporte le texte)
    try:
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        draw.text((50, 100), "Test Product", fill=(255, 255, 255))
        draw.text((50, 130), "Enhanced Webhook", fill=(255, 255, 255))
        draw.text((50, 160), "ma-boutique", fill=(255, 255, 255))
    except:
        # Pas grave si on ne peut pas ajouter de texte
        pass
    
    # Convertir en bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG', quality=90)
    img_bytes = img_buffer.getvalue()
    
    return img_bytes

def test_enhanced_webhook_info():
    """Test du GET endpoint pour les informations"""
    print("📋 Test GET /api/webhook/enhanced pour informations...")
    try:
        response = requests.get("http://localhost:8001/api/webhook/enhanced")
        if response.status_code == 200:
            info = response.json()
            print(f"✅ GET endpoint OK")
            print(f"📋 Message: {info.get('message', 'No message')}")
            print(f"🏪 Stores disponibles: {info.get('available_stores', [])}")
            print(f"📝 Exemple transformation N8N disponible: {'✅' if 'n8n_transformation_example' in info else '❌'}")
            return True
        else:
            print(f"❌ GET failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GET error: {e}")
        return False

def test_enhanced_webhook_post():
    """Test du POST endpoint avec données multipart"""
    print("\n📤 Test POST /api/webhook/enhanced avec données multipart...")
    
    try:
        # Créer l'image de test
        image_data = create_test_image()
        
        # Préparer les données JSON selon le nouveau format
        json_data = {
            "store": "ma-boutique",
            "title": "test_product_enhanced.jpg",  # Simulation de fileName
            "description": "Découvrez ce produit dans notre boutique !",
            "product_url": "https://www.logicamp.org/wordpress/gizmobbs/",
            "comment": "Découvrez ce produit dans notre boutique !"
        }
        
        print(f"📊 Données de test créées:")
        print(f"🏪 Store: {json_data['store']}")
        print(f"📦 Title: {json_data['title']}")
        print(f"📝 Description: {json_data['description']}")
        print(f"🔗 Product URL: {json_data['product_url']}")
        print(f"💬 Comment: {json_data['comment']}")
        print(f"📸 Image size: {len(image_data)} bytes")
        
        # Préparer la requête multipart
        files = {
            'json_data': (None, json.dumps(json_data), 'application/json'),
            'image': ('test_product_enhanced.jpg', image_data, 'image/jpeg')
        }
        
        print(f"\n📡 Envoi de la requête multipart...")
        response = requests.post(
            "http://localhost:8001/api/webhook/enhanced",
            files=files,
            timeout=90
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
                print(f"🏪 Store: {data.get('store', 'None')}")
                print(f"📄 Page: {data.get('page_name', 'None')}")
                print(f"📁 Generated Image URL: {data.get('generated_image_url', 'None')}")
                print(f"📝 Original Filename: {data.get('original_filename', 'None')}")
                print(f"🎯 Enhanced Webhook: {data.get('enhanced_webhook', False)}")
                print(f"📅 Published At: {data.get('published_at', 'None')}")
                
                if 'publication_summary' in data:
                    summary = data['publication_summary']
                    print(f"📊 Publications réussies: {summary.get('total_published', 0)}")
                    print(f"❌ Publications échouées: {summary.get('total_failed', 0)}")
            
            return True
        else:
            print("❌ FAILED!")
            try:
                error_result = response.json()
                print(f"💥 Error: {error_result}")
            except:
                print(f"💥 Error: {response.text}")
            return False
                
    except Exception as e:
        print(f"💥 POST error: {e}")
        return False

def test_store_validation():
    """Test de la validation du store"""
    print("\n🧪 Test de validation du store...")
    
    # Test avec un store invalide
    try:
        json_data = {
            "store": "invalid-store",
            "title": "test_validation.jpg",
            "description": "Test validation",
            "product_url": "https://example.com/test",
            "comment": "Test comment"
        }
        
        image_data = create_test_image()
        
        files = {
            'json_data': (None, json.dumps(json_data), 'application/json'),
            'image': ('test_validation.jpg', image_data, 'image/jpeg')
        }
        
        response = requests.post(
            "http://localhost:8001/api/webhook/enhanced",
            files=files,
            timeout=30
        )
        
        if response.status_code == 400:
            error_result = response.json()
            print(f"✅ Validation store fonctionne: {error_result.get('detail', 'No error message')}")
            return True
        else:
            print(f"❌ Validation store échouée: Expected 400, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test validation error: {e}")
        return False

def main():
    """Lance tous les tests"""
    print("🚀 Test du Webhook Enhancé N8N")
    print("=" * 50)
    
    tests = [
        ("Info Endpoint", test_enhanced_webhook_info),
        ("Enhanced Webhook POST", test_enhanced_webhook_post),
        ("Store Validation", test_store_validation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        success = test_func()
        results.append((test_name, success))
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    total_pass = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    print(f"\n🎯 Total: {total_pass}/{total_tests} tests réussis")
    
    if total_pass == total_tests:
        print("🎉 Tous les tests sont réussis ! Le webhook enhancé est prêt pour N8N.")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")

if __name__ == "__main__":
    main()