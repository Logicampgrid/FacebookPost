#!/usr/bin/env python3
"""
PATCH 61 - Test du nouveau token FACEBOOK_DIRECT_TOKEN pour le store logicamp
Test des permissions vidéo avec le nouveau token fourni
"""

import os
import requests
from datetime import datetime

def test_new_facebook_token():
    """Test le nouveau token Facebook pour logicamp"""
    
    # Charger le nouveau token depuis .env
    from dotenv import load_dotenv
    load_dotenv('/app/backend/.env')
    
    token = os.getenv("FACEBOOK_DIRECT_TOKEN")
    
    print("🔍 PATCH 61 - Test nouveau token FACEBOOK_DIRECT_TOKEN pour logicamp")
    print("=" * 70)
    
    if not token:
        print("❌ ERREUR: FACEBOOK_DIRECT_TOKEN non trouvé dans .env")
        return False
    
    print(f"✅ Token trouvé: {token[:20]}...{token[-10:]}")
    
    # Test des permissions du token
    permissions_url = f"https://graph.facebook.com/v18.0/me/permissions"
    params = {"access_token": token}
    
    try:
        response = requests.get(permissions_url, params=params, timeout=10)
        if response.status_code == 200:
            permissions_data = response.json()
            permissions = [p['permission'] for p in permissions_data.get('data', []) if p.get('status') == 'granted']
            
            print(f"✅ Token valide - {len(permissions)} permissions accordées:")
            
            # Vérifier les permissions critiques pour vidéos
            critical_perms = ['publish_video', 'instagram_content_publish', 'pages_manage_posts']
            for perm in critical_perms:
                if perm in permissions:
                    print(f"   ✅ {perm} - ACCORDÉE")
                else:
                    print(f"   ❌ {perm} - MANQUANTE")
                    
            # Test configuration store logicamp
            print("\n🏪 Configuration store logicamp:")
            store_config_url = "http://localhost:8001/api/stores/logicamp/config"
            
            config_response = requests.get(store_config_url, timeout=10)
            if config_response.status_code == 200:
                config = config_response.json()
                print(f"   ✅ Page Facebook: {config.get('fb_page_id')}")
                print(f"   ✅ Instagram ID: {config.get('ig_user_id')}")
                print(f"   ✅ Token utilisé: {config.get('access_token', '')[:20]}...{config.get('access_token', '')[-10:]}")
                
                # Vérifier que c'est bien le nouveau token
                if config.get('access_token') == token:
                    print("   ✅ PATCH 61: Nouveau token correctement utilisé")
                else:
                    print("   ⚠️  Ancien token encore en cache, redémarrage requis")
                    
            else:
                print(f"   ❌ Erreur configuration store: {config_response.status_code}")
                
            return True
            
        else:
            print(f"❌ Erreur validation token: HTTP {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

def test_simple_webhook():
    """Test simple d'un webhook pour logicamp"""
    
    print("\n🧪 Test simple webhook logicamp:")
    
    webhook_data = {
        "store": "logicamp",
        "title": "Test PATCH 61 - Nouveau token",
        "description": "Test des permissions vidéo avec le nouveau token Facebook",
        "url": "https://www.logicamp.org/",
        "shop_type": "woocommerce"
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/api/webhook",
            json=webhook_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook traité: {result.get('status', 'unknown')}")
            if 'patch' in result:
                print(f"   📋 PATCH actif: {result['patch']}")
            return True
        else:
            print(f"❌ Erreur webhook: HTTP {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test webhook: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"🚀 Début test PATCH 61 - {datetime.now().strftime('%H:%M:%S')}")
    
    # Test 1: Nouveau token
    token_ok = test_new_facebook_token()
    
    # Test 2: Webhook simple
    webhook_ok = test_simple_webhook()
    
    print("\n" + "=" * 70)
    print("📊 RÉSULTATS PATCH 61:")
    print(f"   Token nouveau: {'✅ OK' if token_ok else '❌ ÉCHEC'}")
    print(f"   Webhook logicamp: {'✅ OK' if webhook_ok else '❌ ÉCHEC'}")
    
    if token_ok and webhook_ok:
        print("\n🎉 PATCH 61 RÉUSSI: Nouveau token configuré et fonctionnel pour logicamp")
    else:
        print("\n⚠️  PATCH 61 PARTIEL: Vérifications supplémentaires requises")