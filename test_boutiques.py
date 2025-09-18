#!/usr/bin/env python3
"""
Script de test pour vérifier que les 3 boutiques fonctionnent correctement
"""
import requests
import json
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('/app/backend/.env')

# Configuration des boutiques
STORES = {
    "gizmobbs": {
        "name": "Le Berger Blanc Suisse",
        "fb_page_id": "102401876209415",
        "access_token": os.getenv("FB_ACCESS_TOKEN_GIZMO")
    },
    "logicantiq": {
        "name": "LogicAntiq", 
        "fb_page_id": "210654558802531",
        "access_token": os.getenv("FB_ACCESS_TOKEN_LOGICANTIQ")
    },
    "outdoor": {
        "name": "Logicamp Outdoor",
        "fb_page_id": "236260991673388", 
        "access_token": os.getenv("FB_ACCESS_TOKEN_OUTDOOR")
    }
}

FACEBOOK_GRAPH_URL = "https://graph.facebook.com/v18.0"

def test_token_validity(store_name, config):
    """Teste la validité d'un token d'accès"""
    print(f"\n🔍 Test de {store_name} ({config['name']})...")
    
    if not config['access_token']:
        print(f"❌ {store_name}: Token d'accès manquant")
        return False
    
    try:
        # Test du token en récupérant les infos de la page
        url = f"{FACEBOOK_GRAPH_URL}/{config['fb_page_id']}"
        params = {
            "fields": "id,name,category,access_token,instagram_business_account",
            "access_token": config['access_token']
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {store_name}: Token valide")
            print(f"   📄 Page: {data.get('name', 'N/A')}")
            print(f"   🏷️ Catégorie: {data.get('category', 'N/A')}")
            print(f"   🆔 ID: {data.get('id', 'N/A')}")
            
            # Vérifier si un compte Instagram est connecté
            if data.get('instagram_business_account'):
                ig_id = data['instagram_business_account']['id']
                print(f"   📸 Instagram ID: {ig_id}")
            else:
                print(f"   ⚠️ Aucun compte Instagram Business connecté")
            
            return True
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"❌ {store_name}: Erreur HTTP {response.status_code}")
            print(f"   Détails: {error_data}")
            return False
            
    except Exception as e:
        print(f"❌ {store_name}: Erreur de connexion → {str(e)}")
        return False

def test_publication_permissions(store_name, config):
    """Teste les permissions de publication"""
    print(f"\n📝 Test des permissions de publication pour {store_name}...")
    
    if not config['access_token']:
        print(f"❌ {store_name}: Token d'accès manquant")
        return False
    
    try:
        # Vérifier les permissions du token
        url = f"{FACEBOOK_GRAPH_URL}/me/permissions"
        params = {
            "access_token": config['access_token']
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            permissions = response.json()
            granted_permissions = [p['permission'] for p in permissions.get('data', []) if p.get('status') == 'granted']
            
            required_permissions = ['pages_manage_posts', 'pages_read_engagement', 'instagram_basic', 'instagram_content_publish']
            
            print(f"✅ {store_name}: Permissions récupérées")
            print(f"   📋 Permissions accordées: {len(granted_permissions)}")
            
            missing_permissions = [p for p in required_permissions if p not in granted_permissions]
            if missing_permissions:
                print(f"   ⚠️ Permissions manquantes: {', '.join(missing_permissions)}")
            else:
                print(f"   ✅ Toutes les permissions requises sont accordées")
            
            return len(missing_permissions) == 0
        else:
            print(f"❌ {store_name}: Impossible de récupérer les permissions")
            return False
            
    except Exception as e:
        print(f"❌ {store_name}: Erreur lors du test des permissions → {str(e)}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test de fonctionnement des 3 boutiques")
    print("=" * 50)
    
    results = {}
    
    for store_name, config in STORES.items():
        print(f"\n{'='*20} {store_name.upper()} {'='*20}")
        
        # Test de validité du token
        token_valid = test_token_validity(store_name, config)
        
        # Test des permissions si le token est valide
        permissions_ok = False
        if token_valid:
            permissions_ok = test_publication_permissions(store_name, config)
        
        results[store_name] = {
            'token_valid': token_valid,
            'permissions_ok': permissions_ok,
            'fully_functional': token_valid and permissions_ok
        }
    
    # Résumé final
    print(f"\n{'='*20} RÉSUMÉ FINAL {'='*20}")
    
    all_working = True
    for store_name, result in results.items():
        config = STORES[store_name]
        status = "✅ FONCTIONNEL" if result['fully_functional'] else "❌ PROBLÈME"
        print(f"{status} {store_name} ({config['name']})")
        
        if not result['fully_functional']:
            all_working = False
            if not result['token_valid']:
                print(f"   → Token invalide ou expiré")
            if not result['permissions_ok']:
                print(f"   → Permissions insuffisantes")
    
    if all_working:
        print(f"\n🎉 TOUTES LES BOUTIQUES SONT FONCTIONNELLES !")
        print(f"Les 3 boutiques peuvent maintenant publier comme 'outdoor'")
    else:
        print(f"\n⚠️ Des problèmes ont été détectés. Vérifiez les tokens et permissions.")
    
    return all_working

if __name__ == "__main__":
    main()