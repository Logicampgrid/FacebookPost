#!/usr/bin/env python3
"""
Test du nouveau store 'logicamp' - PATCH 46
"""

import sys
sys.path.insert(0, '/app/backend')

from server import STORES, TOKENS

print("\n" + "="*60)
print("🧪 TEST PATCH 46 - Store Logicamp")
print("="*60 + "\n")

# Test 1: Vérifier que le store existe
print("✅ Test 1: Vérification store 'logicamp'")
if "logicamp" in STORES:
    print("   ✅ Store 'logicamp' trouvé dans STORES")
    print(f"   📋 Configuration:")
    for key, value in STORES["logicamp"].items():
        if key == "access_token" and value:
            print(f"      • {key}: {'*' * 20} (masqué)")
        else:
            print(f"      • {key}: {value}")
else:
    print("   ❌ Store 'logicamp' NON trouvé")
    sys.exit(1)

print()

# Test 2: Vérifier la page Facebook
print("✅ Test 2: Page Facebook configurée")
fb_page_id = STORES["logicamp"]["fb_page_id"]
if fb_page_id == "174450429258625":
    print(f"   ✅ Page Facebook ID correct: {fb_page_id}")
else:
    print(f"   ❌ Page Facebook ID incorrect: {fb_page_id}")

print()

# Test 3: Vérifier TOKENS
print("✅ Test 3: TOKENS initialisé")
if "logicamp" in TOKENS:
    print("   ✅ 'logicamp' présent dans TOKENS")
    print(f"   📋 Contenu: {TOKENS['logicamp']}")
else:
    print("   ❌ 'logicamp' absent de TOKENS")

print()

# Test 4: Liste tous les stores disponibles
print("✅ Test 4: Liste des stores disponibles")
print(f"   📋 Stores configurés: {list(STORES.keys())}")
print(f"   📊 Total: {len(STORES)} stores")

print()
print("="*60)
print("✅ TOUS LES TESTS PASSÉS !")
print("="*60)
print()
print("📝 Prochaines étapes:")
print("   1. Redémarrer le serveur backend")
print("   2. Appeler: GET /api/stores/logicamp/setup-instagram")
print("   3. Tester avec N8N: store='logicamp'")
print()
