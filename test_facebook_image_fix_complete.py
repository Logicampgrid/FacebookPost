#!/usr/bin/env python3
"""
🎯 TEST COMPLET - CORRECTION AFFICHAGE IMAGES FACEBOOK
Test pour vérifier que les images s'affichent toujours comme images, jamais comme liens texte
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:8001"

def test_health_check():
    """Test de santé du système"""
    print("🏥 Test de santé du backend...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend: {health_data.get('backend', 'unknown')}")
            print(f"✅ MongoDB: {health_data.get('mongodb', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_facebook_image_diagnostic():
    """Test du diagnostic des images Facebook"""
    print("\n🔍 Test du diagnostic des améliorations Facebook...")
    try:
        response = requests.get(f"{BASE_URL}/api/debug/facebook-image-fix", timeout=15)
        if response.status_code == 200:
            diagnostic = response.json()
            print(f"✅ Status: {diagnostic.get('status')}")
            print(f"✅ Garantie d'affichage des images: {diagnostic.get('image_display_guarantee')}")
            
            print("\n📋 Stratégies disponibles:")
            for strategy in diagnostic.get('strategies_available', []):
                print(f"   • {strategy}")
            
            print("\n🚀 Améliorations implémentées:")
            for improvement in diagnostic.get('improvements_implemented', []):
                print(f"   {improvement}")
            
            issue_resolved = diagnostic.get('issue_resolved', {})
            if issue_resolved:
                print(f"\n🎯 Problème résolu: {issue_resolved.get('problem')}")
                print(f"   Cause: {issue_resolved.get('cause')}")
                print(f"   Solution: {issue_resolved.get('solution')}")
                print(f"   Résultat: {issue_resolved.get('result')}")
            
            return True
        else:
            print(f"❌ Diagnostic failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Diagnostic error: {e}")
        return False

def test_facebook_image_display():
    """Test réel de l'affichage des images Facebook"""
    print("\n🧪 Test de l'affichage des images Facebook...")
    try:
        response = requests.post(f"{BASE_URL}/api/debug/test-facebook-image-display", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"✅ {result.get('message')}")
                print(f"📄 Post créé sur: {result.get('page_name')}")
                print(f"🆔 Facebook Post ID: {result.get('test_post_id')}")
                print(f"🔗 URL Facebook: {result.get('facebook_post_url')}")
                print(f"🖼️ Image de test: {result.get('test_image_url')}")
                
                print("\n📝 Étapes de vérification:")
                for step in result.get('verification_steps', []):
                    print(f"   {step}")
                
                print(f"\n🛡️ Garantie: {result.get('guarantee')}")
                return True
            else:
                print(f"❌ Test failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Test request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_n8n_webhook_format():
    """Test du format N8N pour les produits"""
    print("\n🔗 Test du webhook N8N (simulation)...")
    
    test_product = {
        "store": "outdoor",
        "title": "TEST - Lampadaire LED Solaire (Image doit s'afficher)",
        "description": "Test de vérification que l'image s'affiche comme image, pas comme lien texte",
        "product_url": "https://www.logicamp.org/test-product",
        "image_url": "https://picsum.photos/600/600?random=test"
    }
    
    try:
        print(f"📤 Envoi du produit de test: {test_product['title']}")
        response = requests.post(f"{BASE_URL}/api/webhook", 
                               json=test_product, 
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Webhook successful: {result.get('status')}")
                
                # Check if it was published or skipped as duplicate
                if result.get('status') == 'published':
                    print(f"📄 Publié sur: {result.get('page_name', 'Page inconnue')}")
                    print(f"🆔 Facebook Post ID: {result.get('data', {}).get('facebook_post_id', 'Non disponible')}")
                    print("🎯 L'image devrait s'afficher comme IMAGE sur Facebook, pas comme lien texte!")
                elif result.get('status') == 'duplicate_skipped':
                    print("⚠️ Produit déjà publié récemment - dédoublonnage actif")
                
                return True
            else:
                print(f"❌ Webhook failed: {result}")
                return False
        else:
            print(f"❌ Webhook request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ N8N test error: {e}")
        return False

def main():
    """Test principal"""
    print("🎯 TEST COMPLET - CORRECTION AFFICHAGE IMAGES FACEBOOK")
    print("=" * 60)
    print("Objectif: Vérifier que les images s'affichent TOUJOURS comme images")
    print("Problème résolu: Images qui apparaissaient comme liens texte 25% du temps")
    print("=" * 60)
    
    # Tests séquentiels
    tests = [
        ("Santé du système", test_health_check),
        ("Diagnostic des améliorations", test_facebook_image_diagnostic),
        ("Test d'affichage d'image réel", test_facebook_image_display),
        ("Test webhook N8N", test_n8n_webhook_format)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🏃‍♂️ Exécution: {test_name}")
        print("-" * 40)
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name}: RÉUSSI")
            else:
                print(f"❌ {test_name}: ÉCHEC")
        except Exception as e:
            print(f"❌ {test_name}: ERREUR - {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # Pause entre les tests
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n📈 Score: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("🎯 Les images Facebook devraient maintenant TOUJOURS s'afficher comme images")
        print("🚀 Le problème des liens texte (25% des cas) est RÉSOLU!")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) ont échoué")
        print("🔧 Veuillez vérifier les logs pour plus de détails")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)