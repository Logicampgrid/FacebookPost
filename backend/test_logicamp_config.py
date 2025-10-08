#!/usr/bin/env python3
"""
PATCH 47 - Test de la configuration Logicamp
Vérifie que le store logicamp est correctement configuré
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_env_variables():
    """Teste que toutes les variables d'environnement sont présentes"""
    print("=" * 60)
    print("🔍 Test des variables d'environnement")
    print("=" * 60)
    
    required_vars = {
        "FB_ACCESS_TOKEN_LOGICAMP": os.getenv("FB_ACCESS_TOKEN_LOGICAMP"),
        "IG_USER_ID_LOGICAMP": os.getenv("IG_USER_ID_LOGICAMP")
    }
    
    all_ok = True
    for var_name, var_value in required_vars.items():
        if var_value:
            masked = f"{var_value[:20]}..." if len(var_value) > 20 else var_value
            print(f"✅ {var_name}: {masked}")
        else:
            print(f"❌ {var_name}: NON DÉFINI")
            all_ok = False
    
    print()
    return all_ok

def test_store_config():
    """Teste la configuration du store dans server.py"""
    print("=" * 60)
    print("🔍 Test de la configuration STORES")
    print("=" * 60)
    
    # Importer la configuration du serveur
    sys.path.insert(0, '/app/backend')
    try:
        from server import STORES, get_store_config
        
        if "logicamp" not in STORES:
            print("❌ Store 'logicamp' non trouvé dans STORES")
            return False
        
        print("✅ Store 'logicamp' existe dans STORES")
        
        # Récupérer la configuration
        config = get_store_config("logicamp")
        
        print(f"\n📋 Configuration du store 'logicamp':")
        print(f"  - Name: {config.get('name')}")
        print(f"  - FB Page ID: {config.get('fb_page_id')}")
        print(f"  - IG User ID: {config.get('ig_user_id')}")
        print(f"  - Access Token: {'✅ Défini' if config.get('access_token') else '❌ Manquant'}")
        
        # Vérifier que tous les champs nécessaires sont présents
        required_fields = ['fb_page_id', 'ig_user_id', 'access_token']
        all_ok = True
        
        print(f"\n🔍 Vérification des champs requis:")
        for field in required_fields:
            if config.get(field):
                print(f"  ✅ {field}: Défini")
            else:
                print(f"  ❌ {field}: MANQUANT")
                all_ok = False
        
        print()
        return all_ok
        
    except Exception as e:
        print(f"❌ Erreur lors de l'import: {e}")
        return False

def test_api_call():
    """Teste un appel API Facebook pour vérifier que le token fonctionne"""
    print("=" * 60)
    print("🔍 Test de l'API Facebook")
    print("=" * 60)
    
    import requests
    
    access_token = os.getenv("FB_ACCESS_TOKEN_LOGICAMP")
    page_id = "174450429258625"
    graph_url = "https://graph.facebook.com/v18.0"
    
    if not access_token:
        print("❌ Token non trouvé")
        return False
    
    try:
        # Test 1: Récupérer les infos de la page
        print(f"📘 Test 1: Récupération infos page {page_id}...")
        url = f"{graph_url}/{page_id}"
        params = {
            "fields": "name,fan_count,instagram_business_account",
            "access_token": access_token
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Page trouvée: {data.get('name')}")
            print(f"  📊 Fans: {data.get('fan_count', 'N/A')}")
            
            if "instagram_business_account" in data:
                ig_id = data["instagram_business_account"]["id"]
                print(f"  📸 Instagram lié: {ig_id}")
            else:
                print(f"  ⚠️ Pas d'Instagram lié")
        else:
            print(f"  ❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
        
        # Test 2: Récupérer les infos Instagram
        ig_id = os.getenv("IG_USER_ID_LOGICAMP")
        if ig_id:
            print(f"\n📸 Test 2: Récupération infos Instagram {ig_id}...")
            url = f"{graph_url}/{ig_id}"
            params = {
                "fields": "username,followers_count,media_count",
                "access_token": access_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Compte Instagram: @{data.get('username')}")
                print(f"  👥 Followers: {data.get('followers_count', 'N/A')}")
                print(f"  📷 Posts: {data.get('media_count', 'N/A')}")
            else:
                print(f"  ❌ Erreur HTTP {response.status_code}: {response.text}")
                return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("🚀 PATCH 47 - Test Configuration Logicamp")
    print("=" * 60)
    print()
    
    results = []
    
    # Test 1: Variables d'environnement
    results.append(("Variables .env", test_env_variables()))
    
    # Test 2: Configuration STORES
    results.append(("Configuration STORES", test_store_config()))
    
    # Test 3: API Facebook
    results.append(("API Facebook", test_api_call()))
    
    # Résumé
    print("=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_pass = all(r[1] for r in results)
    
    print()
    if all_pass:
        print("✅ TOUS LES TESTS PASSÉS - Store logicamp opérationnel !")
        print("🎯 Le store peut maintenant publier des images et vidéos")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("⚠️ Vérifiez les erreurs ci-dessus")
    
    print("=" * 60)
    print()
    
    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())
