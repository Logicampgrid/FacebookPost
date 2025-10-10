#!/usr/bin/env python3
"""
Test PATCH 60 - Vérification que get_store_config() préserve FACEBOOK_DIRECT_TOKEN pour logicamp
"""
import sys
sys.path.insert(0, '/app/backend')

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('/app/backend/.env')

# Importer depuis server.py
try:
    from server import STORES, TOKENS, get_store_config
    print("✅ Modules importés avec succès")
except ImportError as e:
    print(f"❌ Erreur import: {e}")
    sys.exit(1)

print("\n" + "="*80)
print("TEST PATCH 60 - Protection get_store_config() pour logicamp")
print("="*80)

# Test 1: Vérifier configuration initiale STORES
print("\n📋 Test 1: Configuration initiale STORES['logicamp']")
print("-" * 80)
logicamp_config = STORES.get("logicamp", {})
access_token = logicamp_config.get("access_token")
facebook_direct_token = os.getenv("FACEBOOK_DIRECT_TOKEN")

print(f"STORES['logicamp']['access_token']: {access_token[:20]}..." if access_token else "❌ Non défini")
print(f"FACEBOOK_DIRECT_TOKEN (.env): {facebook_direct_token[:20]}..." if facebook_direct_token else "❌ Non défini")

if access_token and facebook_direct_token and access_token == facebook_direct_token:
    print("✅ PATCH 58 confirmé: STORES utilise FACEBOOK_DIRECT_TOKEN")
else:
    print("⚠️ ATTENTION: STORES n'utilise pas FACEBOOK_DIRECT_TOKEN")

# Test 2: Simuler un token dynamique dans TOKENS
print("\n📋 Test 2: Simulation token dynamique dans TOKENS")
print("-" * 80)

# Simuler qu'un token OAuth a été sauvegardé (sans permissions vidéo)
fake_oauth_token = "EAABwzLixnjYBO_FAKE_TOKEN_WITHOUT_VIDEO_PERMISSIONS_xyz123"
TOKENS["logicamp"] = {
    "access_token": fake_oauth_token,
    "ig_user_id": "17841461492706552"
}
print(f"TOKENS['logicamp']['access_token'] simulé: {fake_oauth_token[:30]}...")

# Test 3: Appeler get_store_config() et vérifier le résultat
print("\n📋 Test 3: Appel get_store_config('logicamp')")
print("-" * 80)

config = get_store_config("logicamp")
config_token = config.get("access_token")

print(f"Config retournée access_token: {config_token[:30]}..." if config_token else "❌ Non défini")
print(f"Instagram ID: {config.get('ig_user_id', 'Non défini')}")
print(f"Page ID: {config.get('fb_page_id', 'Non défini')}")

# Test 4: Vérification PATCH 60
print("\n📋 Test 4: Vérification PATCH 60")
print("-" * 80)

if config_token == facebook_direct_token:
    print("✅ PATCH 60 RÉUSSI: FACEBOOK_DIRECT_TOKEN préservé malgré token dynamique")
    print("✅ Token OAuth ignoré (sans permissions vidéo)")
    print("✅ Publications vidéos Facebook logicamp fonctionneront")
    test_passed = True
elif config_token == fake_oauth_token:
    print("❌ PATCH 60 ÉCHOUÉ: Token OAuth utilisé (sans permissions vidéo)")
    print("❌ Token dynamique écrase FACEBOOK_DIRECT_TOKEN")
    print("❌ Publications vidéos Facebook logicamp échoueront avec erreur (#100)")
    test_passed = False
else:
    print(f"⚠️ ÉTAT INATTENDU: Token retourné ne correspond ni à FACEBOOK_DIRECT_TOKEN ni au fake token")
    print(f"   Token reçu: {config_token[:50]}..." if config_token else "None")
    test_passed = False

# Test 5: Vérifier que ig_user_id est bien mis à jour
print("\n📋 Test 5: Vérification ig_user_id")
print("-" * 80)
if config.get("ig_user_id") == "17841461492706552":
    print("✅ Instagram ID correctement mis à jour depuis TOKENS")
else:
    print(f"⚠️ Instagram ID: {config.get('ig_user_id', 'Non trouvé')}")

# Test 6: Comparer avec un autre store
print("\n📋 Test 6: Comparaison avec store 'gizmobbs'")
print("-" * 80)

# Simuler token dynamique pour gizmobbs
gizmobbs_oauth_token = "EAABwzLixnjYBO_GIZMOBBS_OAUTH_TOKEN_abc456"
TOKENS["gizmobbs"] = {
    "access_token": gizmobbs_oauth_token
}

gizmobbs_config = get_store_config("gizmobbs")
gizmobbs_token = gizmobbs_config.get("access_token")

if gizmobbs_token == gizmobbs_oauth_token:
    print("✅ Store 'gizmobbs': Token dynamique UTILISÉ (comportement normal)")
    print("✅ PATCH 60 n'affecte QUE logicamp (exception unique)")
else:
    print("⚠️ Store 'gizmobbs': Comportement inattendu")

# Résultat final
print("\n" + "="*80)
print("RÉSULTAT FINAL")
print("="*80)

if test_passed:
    print("✅ PATCH 60 VALIDÉ: get_store_config() protège logicamp correctement")
    print("✅ FACEBOOK_DIRECT_TOKEN préservé pour publications vidéos Facebook")
    print("✅ Erreur (#100) 'No permission to publish the video' sera éliminée")
    sys.exit(0)
else:
    print("❌ PATCH 60 NON FONCTIONNEL: Protection logicamp échouée")
    print("❌ Publications vidéos Facebook logicamp continueront d'échouer")
    print("❌ Investigation supplémentaire requise")
    sys.exit(1)
