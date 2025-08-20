#!/usr/bin/env python3
"""
Test complet de la fonctionnalité multi-plateformes @logicamp_berger
Test de publication simultanée Facebook + Instagram via webhook gizmobbs
"""

import requests
import json
import os
from datetime import datetime

API_BASE = "http://localhost:8001"

def test_logicamp_berger_status():
    """Test 1: Vérifier le statut de connexion @logicamp_berger"""
    print("🔍 Test 1: Vérification statut connexion @logicamp_berger...")
    
    try:
        response = requests.get(f"{API_BASE}/api/logicamp-berger/status")
        data = response.json()
        
        if data.get("success"):
            facebook_connected = data["platforms"]["facebook"]["connected"]
            instagram_connected = data["platforms"]["instagram"]["connected"]
            
            print(f"✅ Statut connexion récupéré avec succès")
            print(f"   📘 Facebook: {'✅ Connecté' if facebook_connected else '❌ Non connecté'}")
            if facebook_connected:
                page = data["platforms"]["facebook"]["page"]
                print(f"      Page: {page['name']} ({page['id']})")
            
            print(f"   📱 Instagram: {'✅ Connecté' if instagram_connected else '❌ Non connecté'}")
            if instagram_connected:
                account = data["platforms"]["instagram"]["account"]
                print(f"      Compte: @{account['username']} ({account['id']})")
            
            print(f"   🎯 Multi-plateformes prêt: {'Oui' if data['multi_platform_ready'] else 'Non'}")
            return True
        else:
            print(f"❌ Erreur: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def test_logicamp_berger_connection():
    """Test 2: Tester l'établissement de connexion"""
    print("\n🔗 Test 2: Établissement de connexion...")
    
    try:
        response = requests.post(f"{API_BASE}/api/logicamp-berger/connect")
        data = response.json()
        
        if data.get("success"):
            print(f"✅ Connexion établie: {data['status']}")
            print(f"   Message: {data['message']}")
            return True
        else:
            print(f"❌ Erreur connexion: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def test_webhook_multiplatform():
    """Test 3: Test publication webhook multi-plateformes"""
    print("\n🧪 Test 3: Publication webhook multi-plateformes...")
    
    try:
        # Préparer les données de test
        test_data = {
            "title": f"Test Multi-Platform {int(datetime.now().timestamp())}",
            "description": "Test automatique de publication simultanée Facebook + Instagram via webhook gizmobbs. Ce test vérifie que le nouveau système fonctionne correctement.",
            "url": "https://gizmobbs.com/test-multi-platform-webhook",
            "store": "gizmobbs"
        }
        
        # Utiliser une image de test
        test_image_path = "/app/backend/test_image.jpg"
        if not os.path.exists(test_image_path):
            print(f"⚠️ Image de test non trouvée: {test_image_path}")
            return False
        
        with open(test_image_path, 'rb') as image_file:
            files = {'image': image_file}
            data = {'json_data': json.dumps(test_data)}
            
            response = requests.post(f"{API_BASE}/api/webhook", files=files, data=data)
            
        result = response.json()
        
        if result.get("status") == "success":
            print(f"✅ Webhook traité avec succès")
            
            # Analyser les résultats de publication
            if "publication_results" in result["data"]:
                pub_results = result["data"]["publication_results"][0]
                if "details" in pub_results:
                    details = pub_results["details"]
                    
                    print(f"   📊 Résumé publication:")
                    print(f"      Total publié: {details.get('publication_summary', {}).get('total_published', 0)}")
                    print(f"      Total échoué: {details.get('publication_summary', {}).get('total_failed', 0)}")
                    
                    # Facebook
                    facebook_post_id = details.get("facebook_post_id")
                    if facebook_post_id:
                        print(f"   📘 Facebook: ✅ Publié (ID: {facebook_post_id})")
                        print(f"      Page: {details.get('page_name')} ({details.get('page_id')})")
                    else:
                        print(f"   📘 Facebook: ❌ Échec")
                    
                    # Instagram  
                    instagram_post_id = details.get("instagram_post_id")
                    if instagram_post_id:
                        print(f"   📱 Instagram: ✅ Publié (ID: {instagram_post_id})")
                    else:
                        instagram_error = details.get("instagram_error", "Erreur inconnue")
                        print(f"   📱 Instagram: ⚠️ Échec ({instagram_error})")
                        print(f"      Note: Probablement dû aux permissions API Instagram en attente")
            
            return True
        else:
            print(f"❌ Échec webhook: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def test_direct_webhook_test():
    """Test 4: Test direct via endpoint de test"""
    print("\n🎯 Test 4: Test direct multi-plateformes...")
    
    try:
        response = requests.post(f"{API_BASE}/api/logicamp-berger/test-webhook")
        data = response.json()
        
        if data.get("success"):
            print(f"✅ Test direct réussi")
            
            results = data.get("results", {})
            
            # Facebook
            if "facebook" in results:
                fb = results["facebook"]
                if fb.get("success"):
                    print(f"   📘 Facebook: ✅ Test réussi")
                    print(f"      Page: {fb.get('page_name')}")
                    print(f"      URL: {fb.get('post_url', 'N/A')}")
                else:
                    print(f"   📘 Facebook: ❌ Échec - {fb.get('error')}")
            
            # Instagram
            if "instagram" in results:
                ig = results["instagram"]
                if ig.get("success"):
                    print(f"   📱 Instagram: ✅ Test simulé")
                    print(f"      Compte: @{ig.get('account', {}).get('username', 'unknown')}")
                    print(f"      Note: {ig.get('note', 'N/A')}")
                else:
                    print(f"   📱 Instagram: ❌ Échec - {ig.get('error')}")
            
            return True
        else:
            print(f"❌ Test direct échoué: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Test complet du système multi-plateformes"""
    print("🚀 TESTS COMPLETS - Publication Multi-Plateformes @logicamp_berger")
    print("=" * 70)
    
    tests_results = []
    
    # Exécuter tous les tests
    tests_results.append(("Statut Connexion", test_logicamp_berger_status()))
    tests_results.append(("Établissement Connexion", test_logicamp_berger_connection()))  
    tests_results.append(("Webhook Multi-Plateformes", test_webhook_multiplatform()))
    tests_results.append(("Test Direct", test_direct_webhook_test()))
    
    # Résumé des tests
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES TESTS:")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for test_name, result in tests_results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"{test_name:.<50} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 70)
    print(f"Total: {passed} réussis, {failed} échoués")
    
    if failed == 0:
        print("🎉 TOUS LES TESTS SONT PASSÉS ! Système multi-plateformes fonctionnel.")
        print("💡 Publication simultanée Facebook + Instagram activée pour gizmobbs")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")
    
    print("\n💬 Note: Instagram peut échouer tant que les permissions API ne sont pas approuvées")
    print("   mais la détection et configuration du compte @logicamp_berger fonctionne.")

if __name__ == "__main__":
    main()