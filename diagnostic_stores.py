#!/usr/bin/env python3
"""
DIAGNOSTIC STORES - Vérification configuration tous les stores
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv("/app/backend/.env")

def test_facebook_token(token, store_name):
    """Teste la validité d'un token Facebook"""
    try:
        response = requests.get(
            f"https://graph.facebook.com/v18.0/me",
            params={"access_token": token},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "valid": True,
                "store": store_name,
                "name": data.get("name", "N/A"),
                "id": data.get("id", "N/A")
            }
        else:
            return {
                "valid": False,
                "store": store_name,
                "error": response.json().get("error", {}).get("message", "Unknown error"),
                "status": response.status_code
            }
    except Exception as e:
        return {
            "valid": False,
            "store": store_name,
            "error": str(e)
        }

def check_instagram_id(page_id, token, store_name):
    """Vérifie l'Instagram ID d'une page"""
    try:
        response = requests.get(
            f"https://graph.facebook.com/v18.0/{page_id}",
            params={
                "fields": "instagram_business_account",
                "access_token": token
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            ig_id = data.get("instagram_business_account", {}).get("id")
            return {
                "has_instagram": bool(ig_id),
                "store": store_name,
                "ig_id": ig_id or "Non connecté"
            }
        else:
            return {
                "has_instagram": False,
                "store": store_name,
                "error": response.json().get("error", {}).get("message", "Unknown error")
            }
    except Exception as e:
        return {
            "has_instagram": False,
            "store": store_name,
            "error": str(e)
        }

# Configuration des stores
stores_config = {
    "gizmobbs": {
        "token_env": "FB_ACCESS_TOKEN_GIZMO",
        "page_id": "102401876209415",
        "ig_id_env": "IG_USER_ID_GIZMO"
    },
    "logicantiq": {
        "token_env": "FB_ACCESS_TOKEN_LOGICANTIQ",
        "page_id": "210654558802531",
        "ig_id_env": "IG_USER_ID_LOGICANTIQ"
    },
    "outdoor": {
        "token_env": "FB_ACCESS_TOKEN_OUTDOOR",
        "page_id": "236260991673388",
        "ig_id_env": "IG_USER_ID_OUTDOOR"
    },
    "logicamp": {
        "token_env": "FACEBOOK_DIRECT_TOKEN",
        "page_id": "174450429258625",
        "ig_id_env": "IG_USER_ID_LOGICAMP"
    }
}

print("=" * 80)
print("🔍 DIAGNOSTIC COMPLET DES STORES")
print("=" * 80)
print()

all_stores_ok = True

for store_name, config in stores_config.items():
    print(f"📦 STORE: {store_name.upper()}")
    print("-" * 80)
    
    # Vérifier la présence du token dans .env
    token = os.getenv(config["token_env"])
    if not token:
        print(f"  ❌ Token {config['token_env']} absent dans .env")
        all_stores_ok = False
        continue
    else:
        print(f"  ✅ Token {config['token_env']} présent ({len(token)} caractères)")
    
    # Tester la validité du token
    print(f"  🔑 Test validité token...")
    token_result = test_facebook_token(token, store_name)
    if token_result["valid"]:
        print(f"  ✅ Token valide: {token_result.get('name', 'N/A')} (ID: {token_result.get('id', 'N/A')})")
    else:
        print(f"  ❌ Token INVALIDE: {token_result.get('error', 'Unknown')}")
        all_stores_ok = False
    
    # Vérifier Instagram ID
    ig_id = os.getenv(config["ig_id_env"])
    if not ig_id:
        print(f"  ⚠️  Instagram ID {config['ig_id_env']} absent dans .env")
    else:
        print(f"  ✅ Instagram ID configuré: {ig_id}")
    
    # Vérifier connexion Instagram de la page
    if token_result["valid"]:
        print(f"  🔍 Vérification connexion Instagram page...")
        ig_result = check_instagram_id(config["page_id"], token, store_name)
        if ig_result["has_instagram"]:
            print(f"  ✅ Page connectée à Instagram: {ig_result['ig_id']}")
            if ig_id and ig_id != ig_result['ig_id']:
                print(f"  ⚠️  ATTENTION: ID configuré ({ig_id}) différent de l'ID réel ({ig_result['ig_id']})")
                all_stores_ok = False
        else:
            print(f"  ❌ Page NON connectée à Instagram ou erreur: {ig_result.get('error', 'Unknown')}")
            all_stores_ok = False
    
    print()

print("=" * 80)
if all_stores_ok:
    print("✅ TOUS LES STORES SONT CORRECTEMENT CONFIGURÉS")
else:
    print("⚠️  DES PROBLÈMES ONT ÉTÉ DÉTECTÉS - Voir détails ci-dessus")
print("=" * 80)
