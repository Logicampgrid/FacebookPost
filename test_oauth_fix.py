#!/usr/bin/env python3
"""
Test pour vérifier la correction OAuth avec ngrok
"""
import requests
import json
import time

def test_oauth_correction():
    """Test de la correction OAuth avec URL ngrok"""
    print("🧪 Test de la correction OAuth avec ngrok")
    print("=" * 50)
    
    # 1. Vérifier le health check
    try:
        response = requests.get("http://localhost:8001/api/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend accessible")
            print(f"   - Ngrok enabled: {health_data['ngrok']['enabled']}")
            print(f"   - Ngrok URL: {health_data['ngrok']['url']}")
            print(f"   - Tunnel active: {health_data['ngrok']['tunnel_active']}")
            
            ngrok_url = health_data['ngrok']['url']
            if ngrok_url:
                print(f"🌐 URL ngrok détectée: {ngrok_url}")
                return test_with_ngrok_url(ngrok_url)
            else:
                print("⚠️ Ngrok non démarré, impossible de tester OAuth")
                return False
        else:
            print(f"❌ Backend non accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur connexion backend: {e}")
        return False

def test_with_ngrok_url(ngrok_url):
    """Test avec l'URL ngrok disponible"""
    print(f"\n🔗 Test avec URL ngrok: {ngrok_url}")
    
    # Simuler un code d'autorisation (format Facebook)
    mock_code = "AQBzQC1ijC3Va15DLEVlPGWWUEHUvA4ZsqWTO1BAJWM8JI90aJ38RFP"
    
    # Test avec l'ancien comportement (localhost)
    print("\n📝 Test 1: Avec redirect_uri localhost (devrait utiliser ngrok)")
    test_payload = {
        "code": mock_code,
        "state": "test_store",
        "redirect_uri": "http://localhost:8001/"
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/api/auth/facebook/exchange-code",
            json=test_payload,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success', False)}")
            if not data.get('success'):
                print(f"   Error: {data.get('error', 'Unknown')}")
        else:
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   Erreur: {e}")
    
    # Test 2: Avec redirect_uri ngrok explicite
    print(f"\n📝 Test 2: Avec redirect_uri ngrok explicite")
    test_payload2 = {
        "code": mock_code,
        "state": "test_store", 
        "redirect_uri": ngrok_url
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/api/auth/facebook/exchange-code",
            json=test_payload2,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success', False)}")
            if not data.get('success'):
                print(f"   Error: {data.get('error', 'Unknown')}")
        else:
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   Erreur: {e}")
    
    return True

def show_facebook_config_instructions(ngrok_url):
    """Afficher les instructions de configuration Facebook"""
    print(f"\n📋 INSTRUCTIONS CONFIGURATION FACEBOOK APP")
    print("=" * 50)
    print(f"App ID: 5664227323683118")
    print(f"1. Aller sur https://developers.facebook.com/apps/5664227323683118/settings/basic/")
    print(f"2. Dans 'Domaines d'app', ajouter:")
    
    if ngrok_url:
        domain = ngrok_url.replace('https://', '').replace('http://', '')
        print(f"   - {domain}")
        print(f"   - *.ngrok-free.app")
    else:
        print(f"   - *.ngrok-free.app")
    
    print(f"3. Dans 'URI de redirection OAuth valides', ajouter:")
    if ngrok_url:
        print(f"   - {ngrok_url}/")
        print(f"   - {ngrok_url}")
    
    print(f"4. Sauvegarder les modifications")
    print(f"\n💡 Une fois configuré, l'authentification OAuth devrait fonctionner!")

if __name__ == "__main__":
    success = test_oauth_correction()
    
    # Attendre ngrok si nécessaire
    if not success:
        print("\n⏳ Attente du démarrage de ngrok...")
        for i in range(10):
            time.sleep(2)
            try:
                response = requests.get("http://localhost:8001/api/health", timeout=2)
                if response.status_code == 200:
                    health_data = response.json()
                    if health_data['ngrok']['url']:
                        print(f"✅ Ngrok maintenant disponible!")
                        test_with_ngrok_url(health_data['ngrok']['url'])
                        show_facebook_config_instructions(health_data['ngrok']['url'])
                        break
            except:
                pass
        else:
            print("❌ Ngrok ne semble pas démarrer automatiquement")
            show_facebook_config_instructions(None)