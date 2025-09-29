#!/usr/bin/env python3
"""
Test des formats webhook n8n
Valide que /api/webhook accepte les deux formats :
1. Format n8n : jsonData + file
2. Format direct : store, title, url, description, file
"""

import requests
import json
import os

BASE_URL = "http://localhost:8001"

def test_n8n_format():
    """Test format n8n avec jsonData"""
    print("🔧 Test format n8n (jsonData + file)...")
    
    # Préparer le JSON comme l'envoie n8n
    json_data = {
        "store": "gizmobbs",
        "title": "Harnais de ceinture de sécurité pour chiens",
        "url": "https://www.logicamp.org/wordpress/produit/harnais-de-ceinture/",
        "description": "Harnais réglable en nylon avec coussin réfléchissant"
    }
    
    # Créer un fichier test
    test_content = "Test format n8n"
    with open("/tmp/test_n8n.txt", "w") as f:
        f.write(test_content)
    
    files = {"file": open("/tmp/test_n8n.txt", "rb")}
    data = {"jsonData": json.dumps(json_data)}
    
    response = requests.post(f"{BASE_URL}/api/webhook", files=files, data=data)
    files["file"].close()
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Store: {result.get('store')}")
        print(f"   Format détecté: n8n")
        print(f"   Fichier traité: {result.get('file_info', {}).get('filename')}")
        print(f"   ✅ Format n8n: FONCTIONNEL")
    else:
        print(f"   ❌ Erreur: {response.text}")
    
    # Nettoyage
    os.remove("/tmp/test_n8n.txt")
    return response.status_code == 200

def test_direct_format():
    """Test format direct avec champs séparés"""
    print("🔧 Test format direct (champs séparés)...")
    
    # Créer un fichier test
    test_content = "Test format direct"
    with open("/tmp/test_direct.txt", "w") as f:
        f.write(test_content)
    
    files = {"file": open("/tmp/test_direct.txt", "rb")}
    data = {
        "store": "gizmobbs",
        "title": "Test Format Direct",
        "url": "https://example.com/test-direct",
        "description": "Test du format direct pour compatibilité"
    }
    
    response = requests.post(f"{BASE_URL}/api/webhook", files=files, data=data)
    files["file"].close()
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Store: {result.get('store')}")
        print(f"   Format détecté: direct")
        print(f"   Fichier traité: {result.get('file_info', {}).get('filename')}")
        print(f"   ✅ Format direct: FONCTIONNEL")
    else:
        print(f"   ❌ Erreur: {response.text}")
    
    # Nettoyage
    os.remove("/tmp/test_direct.txt")
    return response.status_code == 200

def test_webhook_compatibility():
    """Test que les webhooks Facebook standard fonctionnent toujours"""
    print("📦 Test compatibilité webhook Facebook...")
    
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
    print(f"   ✅ Webhook Facebook: {'FONCTIONNEL' if response.status_code == 200 else 'ÉCHOUÉ'}")
    
    return response.status_code == 200

def main():
    print("🧪 Test des formats webhook n8n")
    print("=" * 50)
    
    tests = [
        ("Format n8n (jsonData)", test_n8n_format),
        ("Format direct", test_direct_format),
        ("Compatibilité webhook", test_webhook_compatibility)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
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
        print("🎉 FORMATS WEBHOOK VALIDÉS !")
        print("   → n8n peut utiliser format jsonData + file")
        print("   → Format direct reste compatible")
        print("   → Webhooks Facebook fonctionnels")
    else:
        print("⚠️  Certains formats ne fonctionnent pas")

if __name__ == "__main__":
    main()