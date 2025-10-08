#!/usr/bin/env python3
"""
Diagnostic des permissions Facebook pour les vidéos
Identifie pourquoi les vidéos sont refusées malgré le PATCH 48
"""
import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('/app/backend/.env')

# Configuration
FACEBOOK_GRAPH_URL = "https://graph.facebook.com/v22.0"

# Stores à tester
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
    },
    "logicamp": {
        "name": "Logicamp",
        "fb_page_id": "174450429258625",
        "access_token": os.getenv("FB_ACCESS_TOKEN_LOGICAMP")
    }
}

def check_token_permissions(access_token, store_name):
    """Vérifier les permissions du token"""
    print(f"\n📋 Vérification permissions pour {store_name}...")
    
    try:
        # Obtenir les permissions du token
        url = f"{FACEBOOK_GRAPH_URL}/me/permissions"
        response = requests.get(url, params={"access_token": access_token}, timeout=10)
        
        if response.status_code == 200:
            permissions = response.json().get('data', [])
            
            # Permissions critiques pour les vidéos
            critical_perms = {
                'pages_manage_posts': False,
                'pages_read_engagement': False,
                'publish_video': False,
                'pages_show_list': False
            }
            
            print(f"   ✅ Token valide - {len(permissions)} permissions trouvées")
            
            for perm in permissions:
                perm_name = perm.get('permission')
                perm_status = perm.get('status')
                
                if perm_name in critical_perms:
                    critical_perms[perm_name] = (perm_status == 'granted')
                    status = "✅" if perm_status == 'granted' else "❌"
                    print(f"   {status} {perm_name}: {perm_status}")
            
            # Vérifier permissions manquantes
            missing = [p for p, granted in critical_perms.items() if not granted]
            if missing:
                print(f"\n   ⚠️  Permissions manquantes: {', '.join(missing)}")
                return False, missing
            else:
                print(f"\n   ✅ Toutes les permissions critiques sont présentes")
                return True, []
        else:
            print(f"   ❌ Erreur API: {response.status_code}")
            print(f"   📄 {response.text}")
            return False, []
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False, []

def check_page_features(page_id, access_token, store_name):
    """Vérifier les fonctionnalités de la page"""
    print(f"\n🏢 Vérification page Facebook {store_name}...")
    
    try:
        # Obtenir les infos de la page
        url = f"{FACEBOOK_GRAPH_URL}/{page_id}"
        params = {
            "fields": "id,name,is_published,fan_count,verification_status,supports_donate_button_in_live_video",
            "access_token": access_token
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            page_data = response.json()
            print(f"   ✅ Page: {page_data.get('name')}")
            print(f"   📊 Fans: {page_data.get('fan_count', 'N/A')}")
            print(f"   ✅ Publiée: {page_data.get('is_published', False)}")
            print(f"   🔒 Vérifiée: {page_data.get('verification_status', 'not_verified')}")
            return True
        else:
            print(f"   ❌ Erreur API: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_video_upload_capability(page_id, access_token, store_name):
    """Tester la capacité d'upload vidéo (sans vraiment uploader)"""
    print(f"\n🎬 Test capacité upload vidéo {store_name}...")
    
    try:
        # Vérifier l'endpoint /videos (sans envoyer de fichier)
        url = f"{FACEBOOK_GRAPH_URL}/{page_id}/videos"
        
        # Test avec paramètres minimum (devrait retourner erreur mais nous dit si endpoint accessible)
        params = {
            "access_token": access_token
        }
        
        # GET sur l'endpoint videos pour voir les vidéos existantes
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            videos = response.json().get('data', [])
            print(f"   ✅ Endpoint /videos accessible")
            print(f"   📹 Vidéos existantes: {len(videos)}")
            return True
        elif response.status_code == 403:
            print(f"   ❌ Accès refusé à l'endpoint /videos")
            print(f"   ⚠️  La page n'a pas l'autorisation de publier des vidéos")
            return False
        else:
            print(f"   ⚠️  Status: {response.status_code}")
            error_data = response.json()
            print(f"   📄 {error_data.get('error', {}).get('message', 'N/A')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def main():
    print("=" * 70)
    print("🔍 DIAGNOSTIC PERMISSIONS FACEBOOK - VIDÉOS")
    print("=" * 70)
    print("\n📋 Objectif: Identifier pourquoi les vidéos Facebook sont refusées")
    print("❓ Erreur actuelle: code 6000, subcode 1363042")
    print("   'Vous n'avez pas l'autorisation d'importer une vidéo ici'\n")
    
    results = {}
    
    for store_key, store_config in STORES.items():
        print("\n" + "=" * 70)
        print(f"🏪 STORE: {store_config['name']} ({store_key})")
        print("=" * 70)
        
        if not store_config['access_token']:
            print(f"   ⚠️  Token non configuré pour {store_key}")
            results[store_key] = {'success': False, 'reason': 'Token manquant'}
            continue
        
        # 1. Vérifier permissions du token
        perms_ok, missing = check_token_permissions(store_config['access_token'], store_config['name'])
        
        # 2. Vérifier page
        page_ok = check_page_features(store_config['fb_page_id'], store_config['access_token'], store_config['name'])
        
        # 3. Tester capacité upload vidéo
        video_ok = test_video_upload_capability(store_config['fb_page_id'], store_config['access_token'], store_config['name'])
        
        results[store_key] = {
            'permissions_ok': perms_ok,
            'missing_permissions': missing,
            'page_ok': page_ok,
            'video_capability': video_ok,
            'success': perms_ok and page_ok and video_ok
        }
    
    # Résumé final
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DIAGNOSTIC")
    print("=" * 70)
    
    all_ok = True
    for store_key, result in results.items():
        store_name = STORES[store_key]['name']
        if result.get('success'):
            print(f"\n✅ {store_name} ({store_key}): Toutes les permissions OK")
        else:
            all_ok = False
            print(f"\n❌ {store_name} ({store_key}): Problèmes détectés")
            
            if not result.get('permissions_ok'):
                print(f"   ⚠️  Permissions manquantes: {', '.join(result.get('missing_permissions', []))}")
            
            if not result.get('page_ok'):
                print(f"   ⚠️  Problème avec la page Facebook")
            
            if not result.get('video_capability'):
                print(f"   ⚠️  Endpoint /videos non accessible")
    
    # Recommandations
    print("\n" + "=" * 70)
    print("💡 RECOMMANDATIONS")
    print("=" * 70)
    
    if not all_ok:
        print("\n🔧 Actions à effectuer:")
        print("\n1️⃣ Régénérer le token Facebook avec TOUTES les permissions:")
        print("   • pages_manage_posts")
        print("   • pages_read_engagement")
        print("   • publish_video ← CRITIQUE pour les vidéos")
        print("   • pages_show_list")
        
        print("\n2️⃣ Vérifier les paramètres de la page Facebook:")
        print("   • La page doit être publiée (is_published=true)")
        print("   • Le compte admin doit avoir les droits de publication vidéo")
        
        print("\n3️⃣ Vérifier le Business Manager:")
        print("   • Les pages doivent être liées au Business Manager")
        print("   • Le Business Manager doit avoir les permissions vidéo")
        
        print("\n4️⃣ Solution temporaire:")
        print("   • Désactiver publications vidéos Facebook")
        print("   • Garder uniquement Instagram Reels (qui fonctionnent)")
    else:
        print("\n✅ Toutes les permissions sont OK")
        print("⚠️  Si l'erreur persiste, le problème peut être:")
        print("   • Restrictions temporaires Facebook")
        print("   • Limitations du compte/page spécifiques")
        print("   • Problème avec le fichier vidéo lui-même")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
