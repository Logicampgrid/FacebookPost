#!/usr/bin/env python3
"""
Script de test d'intégration pour valider que le serveur FacebookPost
combine correctement backend + frontend
"""

import requests
import json
import sys

def test_backend_frontend_integration():
    """Test complet de l'intégration backend + frontend"""
    
    BASE_URL = "http://localhost:8001"
    
    print("🧪 Test d'intégration Backend + Frontend FastAPI")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Endpoint API Health
    tests_total += 1
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Test 1: API Health endpoint - PASS")
            print(f"   Status: {data.get('status')}")
            tests_passed += 1
        else:
            print(f"❌ Test 1: API Health endpoint - FAIL (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Test 1: API Health endpoint - FAIL (error: {e})")
    
    # Test 2: Frontend à la racine
    tests_total += 1
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200 and "<!doctype html>" in response.text.lower():
            print("✅ Test 2: Frontend React à la racine - PASS")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
            tests_passed += 1
        else:
            print(f"❌ Test 2: Frontend React à la racine - FAIL (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Test 2: Frontend React à la racine - FAIL (error: {e})")
    
    # Test 3: Fichiers statiques CSS
    tests_total += 1
    try:
        response = requests.get(f"{BASE_URL}/static/css/main.90f3d3a2.css", timeout=5)
        if response.status_code == 200 and "text/css" in response.headers.get('content-type', ''):
            print("✅ Test 3: Fichiers statiques CSS - PASS")
            print(f"   Taille: {len(response.content)} bytes")
            tests_passed += 1
        else:
            print(f"❌ Test 3: Fichiers statiques CSS - FAIL (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Test 3: Fichiers statiques CSS - FAIL (error: {e})")
    
    # Test 4: Fichiers statiques JS
    tests_total += 1
    try:
        response = requests.get(f"{BASE_URL}/static/js/main.aaecbe7f.js", timeout=5)
        if response.status_code == 200 and "javascript" in response.headers.get('content-type', ''):
            print("✅ Test 4: Fichiers statiques JS - PASS")
            print(f"   Taille: {len(response.content)} bytes")
            tests_passed += 1
        else:
            print(f"❌ Test 4: Fichiers statiques JS - FAIL (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Test 4: Fichiers statiques JS - FAIL (error: {e})")
    
    # Test 5: CORS Headers
    tests_total += 1
    try:
        headers = {"Origin": "https://example.com"}
        response = requests.get(f"{BASE_URL}/api/health", headers=headers, timeout=5)
        cors_header = response.headers.get('access-control-allow-origin')
        if cors_header == "*":
            print("✅ Test 5: CORS Headers - PASS")
            print(f"   Access-Control-Allow-Origin: {cors_header}")
            tests_passed += 1
        else:
            print(f"❌ Test 5: CORS Headers - FAIL (header: {cors_header})")
    except Exception as e:
        print(f"❌ Test 5: CORS Headers - FAIL (error: {e})")
    
    # Test 6: SPA Routing (routes non-API servent l'index.html)
    tests_total += 1
    try:
        response = requests.get(f"{BASE_URL}/some-spa-route", timeout=5)
        if response.status_code == 200 and "<!doctype html>" in response.text.lower():
            print("✅ Test 6: SPA Routing - PASS")
            print("   Routes non-API servent bien l'index.html")
            tests_passed += 1
        else:
            print(f"❌ Test 6: SPA Routing - FAIL (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Test 6: SPA Routing - FAIL (error: {e})")
    
    # Test 7: API Posts endpoint
    tests_total += 1
    try:
        response = requests.get(f"{BASE_URL}/api/posts", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Test 7: API Posts endpoint - PASS")
            print(f"   Posts count: {data.get('total', 0)}")
            tests_passed += 1
        else:
            print(f"❌ Test 7: API Posts endpoint - FAIL (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Test 7: API Posts endpoint - FAIL (error: {e})")
    
    # Test 8: Webhook endpoint
    tests_total += 1
    try:
        params = {
            "hub.mode": "subscribe",
            "hub.verify_token": "mon_token_secret_webhook",
            "hub.challenge": "test_challenge_123"
        }
        response = requests.get(f"{BASE_URL}/api/webhook", params=params, timeout=5)
        if response.status_code == 200 and response.text == "test_challenge_123":
            print("✅ Test 8: Webhook verification - PASS")
            print("   Challenge response correct")
            tests_passed += 1
        else:
            print(f"❌ Test 8: Webhook verification - FAIL (status: {response.status_code}, response: {response.text})")
    except Exception as e:
        print(f"❌ Test 8: Webhook verification - FAIL (error: {e})")
    
    print("=" * 60)
    print(f"🎯 Résultats: {tests_passed}/{tests_total} tests réussis")
    
    if tests_passed == tests_total:
        print("🎉 SUCCÈS: Intégration Backend + Frontend parfaitement fonctionnelle !")
        print("✅ Le serveur FastAPI sert correctement:")
        print("   - Frontend React à la racine /")
        print("   - Fichiers statiques CSS/JS sur /static/*")
        print("   - Endpoints API sur /api/*")
        print("   - CORS configuré pour toutes les origines")
        print("   - SPA routing fonctionnel")
        return True
    else:
        print(f"⚠️  ATTENTION: {tests_total - tests_passed} test(s) ont échoué")
        return False

if __name__ == "__main__":
    success = test_backend_frontend_integration()
    sys.exit(0 if success else 1)