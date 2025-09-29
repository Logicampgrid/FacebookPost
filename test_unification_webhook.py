#!/usr/bin/env python3
"""
Test de l'unification des endpoints webhook
Vérifie que /api/webhook gère correctement:
1. Les requêtes de vérification webhook (GET)
2. Les événements webhook Facebook (POST JSON)
3. Les publications automatiques n8n (POST form-data)
"""

import requests
import os

BASE_URL = "http://localhost:8001"

def test_webhook_verification():
    """Test de vérification webhook Facebook (GET)"""
    print("🔍 Test vérification webhook...")
    params = {
        "hub.mode": "subscribe",
        "hub.challenge": "test_challenge_123",
        "hub.verify_token": "mon_token_secret_webhook"
    }
    
    response = requests.get(f"{BASE_URL}/api/webhook", params=params)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    return response.status_code == 200

def test_webhook_event():
    """Test événement webhook Facebook (POST JSON)"""
    print("📦 Test événement webhook...")
    headers = {"Content-Type": "application/json"}
    data = {
        "object": "page",
        "entry": [
            {
                "id": "123456789",
                "changes": [
                    {
                        "field": "feed",
                        "value": {"item": "post", "verb": "add"}
                    }
                ]
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/webhook", json=data, headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    return response.status_code == 200

def test_n8n_publication():
    """Test publication n8n (POST form-data)"""
    print("🚀 Test publication n8n...")
    
    # Créer un fichier test
    test_content = "Test unification webhook n8n"
    with open("/tmp/test_unification.txt", "w") as f:
        f.write(test_content)
    
    files = {"file": open("/tmp/test_unification.txt", "rb")}
    data = {
        "store": "gizmobbs",
        "title": "Test Unification Webhook",
        "url": "https://example.com/test-unification",
        "description": "Test de l'endpoint webhook unifié pour n8n"
    }
    
    response = requests.post(f"{BASE_URL}/api/webhook", files=files, data=data)
    files["file"].close()
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Store: {result.get('store')}")
        print(f"   Success: {result.get('success')}")
        print(f"   Message: {result.get('message')}")
    else:
        print(f"   Error: {response.text}")
    
    # Nettoyage
    os.remove("/tmp/test_unification.txt")
    return response.status_code == 200

def main():
    print("🧪 Test d'unification des endpoints webhook")
    print("=" * 50)
    
    tests = [
        ("Vérification webhook", test_webhook_verification),
        ("Événement webhook", test_webhook_event),
        ("Publication n8n", test_n8n_publication)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
            print(f"   ✅ {name}: {'RÉUSSI' if success else 'ÉCHOUÉ'}")
        except Exception as e:
            results.append((name, False))
            print(f"   ❌ {name}: ERREUR - {e}")
        print()
    
    print("📊 Résultats:")
    print("-" * 30)
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        print(f"   {status}: {name}")
    
    print(f"\n🎯 Score: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 UNIFICATION WEBHOOK RÉUSSIE !")
        print("   → n8n peut utiliser uniquement POST /api/webhook")
        print("   → Compatibilité totale maintenue")
    else:
        print("⚠️  Certains tests ont échoué")

if __name__ == "__main__":
    main()