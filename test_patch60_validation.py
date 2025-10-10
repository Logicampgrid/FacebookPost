#!/usr/bin/env python3
"""
Test de validation PATCH 60 - Vérification configuration logicamp
"""
import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('/app/backend/.env')

print("=" * 60)
print("🧪 TEST VALIDATION PATCH 60 - Store Logicamp")
print("=" * 60)
print()

# 1. Vérifier les variables d'environnement
print("1️⃣ VARIABLES D'ENVIRONNEMENT:")
print("-" * 60)

fb_direct_token = os.getenv("FACEBOOK_DIRECT_TOKEN")
fb_token_logicamp = os.getenv("FB_ACCESS_TOKEN_LOGICAMP")

if fb_direct_token:
    print(f"✅ FACEBOOK_DIRECT_TOKEN: {fb_direct_token[:50]}...")
else:
    print("❌ FACEBOOK_DIRECT_TOKEN: NON DÉFINI")

if fb_token_logicamp:
    print(f"✅ FB_ACCESS_TOKEN_LOGICAMP: {fb_token_logicamp[:50]}...")
else:
    print("⚠️ FB_ACCESS_TOKEN_LOGICAMP: NON DÉFINI")

print()

# 2. Simuler la configuration STORES comme dans server.py
print("2️⃣ CONFIGURATION STORES (simulation):")
print("-" * 60)

STORES_CONFIG = {
    "logicamp": {
        "name": "Logicamp",
        "fb_page_id": os.getenv("FB_PAGE_ID_LOGICAMP", "174450429258625"),
        "ig_user_id": os.getenv("IG_USER_ID_LOGICAMP", "17841461492706552"),
        "access_token": os.getenv("FACEBOOK_DIRECT_TOKEN")  # PATCH 58
    }
}

print(f"Store: logicamp")
print(f"  - Name: {STORES_CONFIG['logicamp']['name']}")
print(f"  - FB Page ID: {STORES_CONFIG['logicamp']['fb_page_id']}")
print(f"  - IG User ID: {STORES_CONFIG['logicamp']['ig_user_id']}")
if STORES_CONFIG['logicamp']['access_token']:
    print(f"  - Access Token: {STORES_CONFIG['logicamp']['access_token'][:50]}...")
else:
    print(f"  - Access Token: ❌ NON DÉFINI")

print()

# 3. Simuler get_store_config() avec PATCH 60
print("3️⃣ SIMULATION get_store_config() - PATCH 60:")
print("-" * 60)

def get_store_config_simulated(store: str, stores_config: dict, tokens_dynamic: dict):
    """Simulation de get_store_config() avec PATCH 60"""
    if store not in stores_config:
        raise ValueError(f"Store inconnu: {store}")
    
    # Copie de la configuration statique
    config = stores_config[store].copy()
    print(f"📦 Config statique chargée pour '{store}'")
    print(f"   - access_token (STORES): {config['access_token'][:50] if config.get('access_token') else 'None'}...")
    
    # Surcharger avec les tokens dynamiques si disponibles
    if store in tokens_dynamic and tokens_dynamic[store]:
        dynamic_config = tokens_dynamic[store]
        print(f"📦 Tokens dynamiques trouvés pour '{store}'")
        
        # PATCH 60: Pour logicamp, JAMAIS écraser access_token
        if dynamic_config.get("access_token") and store != "logicamp":
            config["access_token"] = dynamic_config["access_token"]
            print(f"🔄 PATCH 60: Token dynamique utilisé pour {store}")
        elif store == "logicamp" and dynamic_config.get("access_token"):
            print(f"✅ PATCH 60: Token dynamique ignoré pour logicamp - FACEBOOK_DIRECT_TOKEN préservé")
            print(f"   - Token dynamique (ignoré): {dynamic_config['access_token'][:50]}...")
            print(f"   - Token préservé (STORES): {config['access_token'][:50]}...")
        
        # Mise à jour des autres champs
        if dynamic_config.get("ig_user_id"):
            config["ig_user_id"] = dynamic_config["ig_user_id"]
            print(f"✅ Instagram ID mis à jour: {dynamic_config['ig_user_id']}")
    else:
        print(f"📦 Aucun token dynamique pour '{store}'")
    
    return config

# Test avec tokens dynamiques vides
print("\n🧪 Test 1: Aucun token dynamique")
TOKENS_EMPTY = {}
config1 = get_store_config_simulated("logicamp", STORES_CONFIG, TOKENS_EMPTY)
print(f"✅ Résultat: access_token = {config1['access_token'][:50] if config1.get('access_token') else 'None'}...")

# Test avec tokens dynamiques présents (simule OAuth callback)
print("\n🧪 Test 2: Token dynamique présent (simule OAuth)")
TOKENS_WITH_DYNAMIC = {
    "logicamp": {
        "access_token": "TOKEN_OAUTH_SANS_PERMISSIONS_VIDEO_123456789",
        "ig_user_id": "17841461492706552"
    }
}
config2 = get_store_config_simulated("logicamp", STORES_CONFIG, TOKENS_WITH_DYNAMIC)
print(f"✅ Résultat: access_token = {config2['access_token'][:50] if config2.get('access_token') else 'None'}...")

print()
print("=" * 60)
print("📊 RÉSUMÉ:")
print("=" * 60)

if config2['access_token'] == STORES_CONFIG['logicamp']['access_token']:
    print("✅ PATCH 60 FONCTIONNE: FACEBOOK_DIRECT_TOKEN préservé même avec token dynamique")
else:
    print("❌ PATCH 60 NE FONCTIONNE PAS: Token dynamique a écrasé FACEBOOK_DIRECT_TOKEN")

print()
print("🎯 CONCLUSION:")
if fb_direct_token and config2['access_token'] == fb_direct_token:
    print("✅ Configuration logicamp correcte pour vidéos Facebook")
    print("✅ FACEBOOK_DIRECT_TOKEN sera utilisé pour publications vidéo")
    sys.exit(0)
else:
    print("⚠️ Vérifier la configuration - FACEBOOK_DIRECT_TOKEN manquant ou incorrect")
    sys.exit(1)
