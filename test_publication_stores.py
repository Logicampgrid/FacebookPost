#!/usr/bin/env python3
"""
TEST PUBLICATION - Simulation publication sur tous les stores
"""

import requests
import json

BACKEND_URL = "https://code-mentor-pro.preview.emergentagent.com"

# Test data pour chaque store
test_data = {
    "gizmobbs": {
        "store": "gizmobbs",
        "title": "Test Berger Blanc Suisse",
        "description": "Test de publication automatique",
        "url": "https://gizmobbs.com/test"
    },
    "logicantiq": {
        "store": "logicantiq",
        "title": "Test LogicAntiq",
        "description": "Test de publication automatique",
        "url": "https://logicantiq.com/test"
    },
    "outdoor": {
        "store": "outdoor",
        "title": "Test Logicamp Outdoor",
        "description": "Test de publication automatique",
        "url": "https://outdoor.com/test"
    },
    "logicamp": {
        "store": "logicamp",
        "title": "Test Logicamp",
        "description": "Test de publication automatique",
        "url": "https://logicamp.org/test"
    }
}

print("=" * 80)
print("🧪 TEST DE PUBLICATION SUR TOUS LES STORES")
print("=" * 80)
print()

for store_name, data in test_data.items():
    print(f"📦 Test store: {store_name.upper()}")
    print("-" * 80)
    
    try:
        # Simulation webhook (sans fichier pour tester juste le routage)
        response = requests.post(
            f"{BACKEND_URL}/api/webhook",
            json=data,
            timeout=30
        )
        
        print(f"  Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Réponse reçue: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"  ❌ Erreur HTTP {response.status_code}")
            try:
                error = response.json()
                print(f"  Détails: {json.dumps(error, indent=2, ensure_ascii=False)}")
            except:
                print(f"  Réponse brute: {response.text[:200]}")
        
    except requests.Timeout:
        print(f"  ⏱️  Timeout - Le serveur ne répond pas après 30s")
    except Exception as e:
        print(f"  ❌ Erreur: {str(e)}")
    
    print()

print("=" * 80)
print("🏁 TEST TERMINÉ")
print("=" * 80)
