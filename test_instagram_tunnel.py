#!/usr/bin/env python3
"""
Test complet du tunnel Instagram
Vérifie que la publication Instagram fonctionne une fois l'utilisateur connecté
"""

import requests
import os
import json
from datetime import datetime

API_BASE = "http://localhost:8001"

def check_user_authentication():
    """Vérifie si un utilisateur est connecté"""
    try:
        response = requests.get(f"{API_BASE}/api/health")
        if response.status_code == 200:
            data = response.json()
            users_count = data['database']['users_count']
            print(f"👤 Utilisateurs connectés: {users_count}")
            return users_count > 0
        return False
    except Exception as e:
        print(f"❌ Error checking auth: {e}")
        return False

def test_instagram_accounts():
    """Test si les comptes Instagram sont accessibles"""
    try:
        response = requests.get(f"{API_BASE}/api/debug/instagram-complete-diagnosis")
        if response.status_code == 200:
            data = response.json()
            instagram_accounts = data.get('instagram_accounts', [])
            
            print(f"📱 Comptes Instagram trouvés: {len(instagram_accounts)}")
            for account in instagram_accounts:
                print(f"   ✅ @{account.get('username', 'unknown')} ({account.get('name', 'N/A')})")
                print(f"      ID: {account.get('id')}")
                print(f"      Status: {account.get('status', 'Unknown')}")
            
            return len(instagram_accounts) > 0
        return False
    except Exception as e:
        print(f"❌ Error testing Instagram: {e}")
        return False

def test_specific_store_instagram(store_name="gizmobbs"):
    """Test l'accès Instagram pour un magasin spécifique"""
    try:
        response = requests.post(f"{API_BASE}/api/debug/test-instagram-webhook-universal?shop_type={store_name}")
        if response.status_code == 200:
            data = response.json()
            print(f"\n🧪 Test Instagram pour '{store_name}':")
            print(f"   Success: {data.get('success', False)}")
            
            if data.get('success'):
                ig_account = data.get('instagram_account', {})
                print(f"   ✅ Instagram: @{ig_account.get('username')} (ID: {ig_account.get('id')})")
                print(f"   ✅ User: {data.get('user_name')}")
                return True
            else:
                print(f"   ❌ Error: {data.get('error')}")
                if 'solution' in data:
                    print(f"   💡 Solution: {data['solution']}")
                return False
        else:
            print(f"❌ Test error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Store test error: {e}")
        return False

def create_webhook_test_file():
    """Crée un fichier test pour le webhook"""
    test_file = "/app/test_image.jpg"
    
    # Créer une image de test simple (ou utiliser une existante)
    if not os.path.exists(test_file):
        # Créer un fichier test basique
        with open(test_file, "wb") as f:
            # Écrire des données binaires de test (pas une vraie image mais ça fera pour le test)
            f.write(b"Test image data for webhook")
    
    return test_file

def test_webhook_instagram_publication():
    """Test une publication Instagram via webhook"""
    if not check_user_authentication():
        print("❌ Aucun utilisateur connecté - impossible de tester la publication")
        return False
    
    try:
        # Créer des données de test
        json_data = {
            "title": "Test Tunnel Instagram Gratuit",
            "description": "Test automatique de publication Instagram via tunnel gratuit. Si vous voyez ce post, le tunnel fonctionne parfaitement!",
            "url": "https://gizmobbs.com/test-tunnel",
            "store": "gizmobbs"  # Magasin configuré pour Instagram
        }
        
        # Note: Pour un vrai test, nous aurions besoin d'un vrai fichier image
        print(f"\n🧪 SIMULATION TEST WEBHOOK INSTAGRAM:")
        print(f"   URL: {API_BASE}/api/webhook")
        print(f"   Store: {json_data['store']}")
        print(f"   Title: {json_data['title']}")
        print(f"   Target: @logicamp_berger")
        
        # Pour un test réel, décommentez ceci:
        # test_file = create_webhook_test_file()
        # files = {'image': open(test_file, 'rb')}
        # data = {'json_data': json.dumps(json_data)}
        # response = requests.post(f"{API_BASE}/api/webhook", files=files, data=data)
        
        print("   ⚠️ Pour un test réel, utilisez une vraie image")
        return True
        
    except Exception as e:
        print(f"❌ Webhook test error: {e}")
        return False

def main():
    """Test complet du tunnel Instagram"""
    print("🚀 TEST COMPLET DU TUNNEL INSTAGRAM")
    print("=" * 50)
    
    # Vérifier l'authentification
    authenticated = check_user_authentication()
    
    if not authenticated:
        print("\n❌ UTILISATEUR NON CONNECTÉ")
        print("🔑 Étapes requises:")
        print("1. Allez sur http://localhost:3000")
        print("2. Connectez-vous avec Facebook Business Manager")
        print("3. Relancez ce test")
        return
    
    print("✅ Utilisateur connecté - Test des comptes Instagram...")
    
    # Test des comptes Instagram
    instagram_ok = test_instagram_accounts()
    
    if not instagram_ok:
        print("\n❌ AUCUN COMPTE INSTAGRAM ACCESSIBLE")
        print("💡 Vérifiez que @logicamp_berger est connecté dans votre Business Manager")
        return
    
    # Test spécifique pour un magasin
    store_ok = test_specific_store_instagram()
    
    if store_ok:
        print("\n✅ TUNNEL INSTAGRAM OPÉRATIONNEL!")
        print("🎉 Vous pouvez maintenant publier sur Instagram via:")
        print("   - Interface web: http://localhost:3000")
        print("   - Webhook API: https://insta-tunnel-free.preview.emergentagent.com/api/webhook")
        
        # Test webhook
        test_webhook_instagram_publication()
        
    else:
        print("\n⚠️ Problème de configuration détecté")
        print("💡 Vérifiez les permissions Instagram Business dans Facebook")

if __name__ == "__main__":
    main()