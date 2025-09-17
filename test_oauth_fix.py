#!/usr/bin/env python3
"""
Script de test pour vérifier la correction OAuth Facebook
"""
import requests
import json

BACKEND_URL = "https://local-oauth-proxy.preview.emergentagent.com"

def test_redirect_uri():
    """Test de la construction de l'URI de redirection"""
    print("🔍 Test de la fonction build_dynamic_redirect_uri...")
    
    # Importer et tester la fonction directement
    import sys
    sys.path.append('/app/backend')
    import server
    
    redirect_uri = server.build_dynamic_redirect_uri('/auth/callback')
    print(f"✅ Redirect URI construite: {redirect_uri}")
    
    expected_url = f"{BACKEND_URL}/auth/callback"
    if redirect_uri == expected_url:
        print("✅ SUCCESS: L'URI de redirection est correcte!")
        return True
    else:
        print(f"❌ ERREUR: URI attendue: {expected_url}")
        return False

def test_webhook_accessibility():
    """Test d'accessibilité du webhook"""
    print("\n🌐 Test d'accessibilité du webhook...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/webhook", timeout=10)
        print(f"✅ Status code: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Erreur webhook: {e}")
        return False

def test_health_check():
    """Test du health check"""
    print("\n💚 Test du health check...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
        health_data = response.json()
        print(f"✅ Status: {health_data['status']}")
        print(f"✅ Stores configurés: {health_data['publication']['stores_configured']}")
        return True
    except Exception as e:
        print(f"❌ Erreur health check: {e}")
        return False

def test_oauth_endpoint():
    """Test de l'endpoint d'authentification Facebook"""
    print("\n🔐 Test de l'endpoint OAuth Facebook...")
    
    try:
        # Test avec un code fictif pour voir si l'erreur de redirect_uri persiste
        test_data = {
            "code": "test_code_12345",
            "state": "instagram_tunnel_test"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/auth/facebook/exchange-code",
            json=test_data,
            timeout=10
        )
        
        print(f"✅ Status code: {response.status_code}")
        response_data = response.json()
        print(f"✅ Response: {json.dumps(response_data, indent=2)}")
        
        # Si on n'a plus l'erreur de redirect_uri, c'est bon
        if "redirect_uri" not in str(response_data).lower():
            print("✅ SUCCESS: Plus d'erreur de redirect_uri!")
            return True
        else:
            print("⚠️ L'erreur de redirect_uri persiste peut-être...")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test OAuth: {e}")
        return False

if __name__ == "__main__":
    print("🚀 === TEST DE CORRECTION OAUTH FACEBOOK ===\n")
    
    tests = [
        ("Redirect URI", test_redirect_uri),
        ("Health Check", test_health_check), 
        ("Webhook", test_webhook_accessibility),
        ("OAuth Endpoint", test_oauth_endpoint)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Erreur dans {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
    print("📊 RÉSULTATS DES TESTS:")
    print("="*50)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    success_count = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    print(f"\n🎯 Score: {success_count}/{total_tests} tests réussis")
    
    if success_count == total_tests:
        print("🎉 TOUS LES TESTS SONT PASSÉS! La correction OAuth semble fonctionnelle.")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")