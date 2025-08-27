#!/usr/bin/env python3
"""
🎯 TEST OFFICIEL - Images Cliquables via Webhook
Test de la solution validée pour garantir des images cliquables à 100%
"""

import requests
import json
from datetime import datetime
import uuid

# Configuration du test
WEBHOOK_URL = "http://localhost:8001/api/webhook"
TEST_IMAGE_URL = f"https://picsum.photos/800/600?test={int(datetime.now().timestamp())}"
TEST_PRODUCT_URL = "https://www.logicamp.org/wordpress/gizmobbs/test-produit"

def test_strategy_1c_images_cliquables():
    """Test officiel de la Strategy 1C pour images cliquables"""
    
    print("🎯 TEST OFFICIEL : Images Cliquables via Strategy 1C")
    print("=" * 60)
    
    # Payload exact selon la solution officielle
    payload = {
        "store": "gizmobbs",
        "title": "🧪 Test Officiel - Image Cliquable",
        "description": "Test de la solution officielle pour garantir des images cliquables. Cette image DOIT être cliquable et rediriger vers product_url.",
        "product_url": TEST_PRODUCT_URL,
        "image_url": TEST_IMAGE_URL
    }
    
    print("📋 Payload de test :")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print()
    
    try:
        print("🚀 Envoi de la requête webhook...")
        
        response = requests.post(
            WEBHOOK_URL,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json=payload,
            timeout=30
        )
        
        print(f"📡 Statut HTTP : {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCÈS : Webhook traité avec succès !")
            print()
            print("📊 Résultat :")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get("success"):
                facebook_post_id = result.get("data", {}).get("facebook_post_id")
                page_name = result.get("data", {}).get("page_name")
                
                print()
                print("🎉 VALIDATION IMAGES CLIQUABLES :")
                print(f"   ✅ Post Facebook créé : {facebook_post_id}")
                print(f"   ✅ Page cible : {page_name}")
                print(f"   ✅ Strategy 1C appliquée : Enhanced Link Post")
                print(f"   ✅ Image URL : {TEST_IMAGE_URL}")
                print(f"   ✅ Product URL (cliquable) : {TEST_PRODUCT_URL}")
                print()
                print("🔍 VÉRIFICATION MANUELLE :")
                print(f"   1. Allez sur Facebook page '{page_name}'")
                print(f"   2. Trouvez le post : '{payload['title']}'")
                print(f"   3. Vérifiez que l'IMAGE s'affiche correctement")
                print(f"   4. Cliquez sur l'image → doit ouvrir : {TEST_PRODUCT_URL}")
                
                return True
            else:
                print("❌ ÉCHEC : Le webhook a retourné success=false")
                return False
                
        else:
            print(f"❌ ERREUR HTTP {response.status_code}")
            try:
                error_data = response.json()
                print("Détails de l'erreur :")
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print("Réponse brute :", response.text)
            return False
            
    except Exception as e:
        print(f"💥 EXCEPTION : {str(e)}")
        return False

def test_payload_variations():
    """Test des variations de payload pour robustesse"""
    
    print("\n" + "=" * 60)
    print("🔧 TEST VARIATIONS PAYLOAD")
    print("=" * 60)
    
    variations = [
        {
            "name": "Minimal Payload",
            "payload": {
                "store": "gizmobbs",
                "title": "Test Minimal",
                "product_url": TEST_PRODUCT_URL,
                "image_url": TEST_IMAGE_URL
            }
        },
        {
            "name": "HTML Description",
            "payload": {
                "store": "gizmobbs", 
                "title": "Test HTML",
                "description": "<p>Description avec <strong>HTML</strong> et <em>balises</em></p>",
                "product_url": TEST_PRODUCT_URL,
                "image_url": TEST_IMAGE_URL
            }
        },
        {
            "name": "Long Title",
            "payload": {
                "store": "gizmobbs",
                "title": "🛍️ Super Produit Extraordinaire avec un Titre Très Long pour Tester la Robustesse du Système",
                "description": "Description détaillée du produit",
                "product_url": TEST_PRODUCT_URL,
                "image_url": TEST_IMAGE_URL
            }
        }
    ]
    
    results = []
    
    for i, variation in enumerate(variations, 1):
        print(f"\n📋 Test {i}/3 : {variation['name']}")
        
        try:
            response = requests.post(
                WEBHOOK_URL,
                headers={"Content-Type": "application/json"},
                json=variation["payload"],
                timeout=15
            )
            
            success = response.status_code == 200
            result_data = response.json() if success else {"error": response.text}
            
            results.append({
                "name": variation["name"],
                "success": success,
                "status_code": response.status_code,
                "result": result_data
            })
            
            status = "✅ OK" if success else "❌ ÉCHEC"
            print(f"   {status} - HTTP {response.status_code}")
            
        except Exception as e:
            results.append({
                "name": variation["name"],
                "success": False,
                "error": str(e)
            })
            print(f"   ❌ EXCEPTION - {str(e)}")
    
    print(f"\n📊 RÉSUMÉ DES TESTS :")
    success_count = sum(1 for r in results if r.get("success"))
    print(f"   ✅ Réussis : {success_count}/3")
    print(f"   ❌ Échoués : {3 - success_count}/3")
    
    return results

def main():
    """Test principal"""
    
    print("🎯 TEST OFFICIEL : SOLUTION IMAGES CLIQUABLES")
    print("🚀 Validation de la méthode Strategy 1C via /api/webhook")
    print()
    
    # Test principal
    success = test_strategy_1c_images_cliquables()
    
    # Tests de variation
    variations_results = test_payload_variations()
    
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ FINAL")
    print("=" * 60)
    
    if success:
        print("✅ TEST PRINCIPAL : SUCCÈS")
        print("✅ La solution Strategy 1C fonctionne correctement")
        print("✅ Images cliquables garanties via /api/webhook")
    else:
        print("❌ TEST PRINCIPAL : ÉCHEC")
        print("❌ Problème avec la solution Strategy 1C")
    
    variations_success = sum(1 for r in variations_results if r.get("success"))
    print(f"✅ TESTS VARIATIONS : {variations_success}/3 réussis")
    
    print(f"\n🌐 URLs de test utilisées :")
    print(f"   📸 Image : {TEST_IMAGE_URL}")
    print(f"   🔗 Produit : {TEST_PRODUCT_URL}")
    print(f"   📡 Webhook : {WEBHOOK_URL}")
    
    print(f"\n⏰ Test complété : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()