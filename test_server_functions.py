#!/usr/bin/env python3
"""
Script pour tester toutes les fonctions du serveur FacebookPost
"""
import requests
import json
import time

def test_server_endpoints():
    """Tester tous les endpoints principaux du serveur"""
    base_url = "http://localhost:8001"
    
    print("🧪 === TEST DES ENDPOINTS SERVEUR ===")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check OK")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Stores configurés: {data.get('publication', {}).get('stores_configured')}/{data.get('publication', {}).get('total_stores')}")
            print(f"   - Ngrok: {data.get('ngrok', {}).get('enabled')} (URL: {data.get('ngrok', {}).get('url', 'None')})")
            
            ngrok_info = data.get('ngrok', {})
            if ngrok_info.get('enabled') and not ngrok_info.get('url'):
                print("   ⚠️ Ngrok activé mais pas d'URL - problème de tunnel confirmé")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur health check: {e}")
        return False
    
    # Test 2: Liste des stores
    try:
        response = requests.get(f"{base_url}/api/stores", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Stores endpoint OK")
            print(f"   - Total stores: {data.get('total_stores')}")
            for store_name, info in data.get('stores', {}).items():
                fb_ok = "✅" if info.get('facebook_configured') else "❌"
                ig_ok = "✅" if info.get('instagram_configured') else "❌"
                print(f"   - {store_name}: FB {fb_ok} IG {ig_ok}")
        else:
            print(f"❌ Stores endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur stores: {e}")
    
    # Test 3: Test de publication (mode test)
    try:
        test_data = {
            "stores": ["gizmobbs"],  # Tester un seul store
            "platforms": ["facebook"],  # Facebook seulement pour éviter problème Instagram
            "custom_message": "Test automatique depuis script de diagnostic 🧪"
        }
        
        response = requests.post(f"{base_url}/api/post/test", 
                               json=test_data, 
                               timeout=30)
        if response.status_code == 200:
            data = response.json()
            print("✅ Test publication endpoint OK")
            print(f"   - Succès global: {data.get('success')}")
            print(f"   - Message: {data.get('message')}")
            
            results = data.get('results', [])
            for result in results:
                status = "✅" if result.get('success') else "❌"
                print(f"   - {result.get('store')}: {status}")
                if result.get('errors'):
                    for error in result.get('errors'):
                        print(f"     Erreur: {error}")
        else:
            print(f"❌ Test publication failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Erreur: {error_data.get('detail', 'Inconnue')}")
            except:
                print(f"   Erreur HTTP: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Erreur test publication: {e}")
    
    print("\n🎯 Tests terminés!")
    return True

if __name__ == "__main__":
    # Attendre un peu que le serveur soit prêt
    print("⏳ Attente du démarrage du serveur...")
    time.sleep(3)
    test_server_endpoints()