#!/usr/bin/env python3
"""
Script de test simple pour valider le webhook Facebook
"""

import requests
import json
import time

def test_webhook_simple():
    """Test rapide du webhook"""
    
    # Configuration
    BASE_URL = "http://localhost:8001"  # Ajustez le port si nécessaire
    VERIFY_TOKEN = "mon_token_secret_webhook"  # Ajustez selon votre configuration
    
    print("🔍 Test simple du webhook Facebook")
    print("=" * 40)
    
    # Test 1: Endpoint de santé
    print("\n1. Test endpoint de santé:")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Endpoint santé: OK")
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
        else:
            print(f"❌ Endpoint santé: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur santé: {e}")
        return False
    
    # Test 2: Validation webhook (GET)
    print("\n2. Test validation webhook (GET):")
    try:
        params = {
            "hub.mode": "subscribe",
            "hub.verify_token": VERIFY_TOKEN,
            "hub.challenge": "test_challenge_12345"
        }
        
        response = requests.get(f"{BASE_URL}/api/webhook", params=params, timeout=10)
        
        if response.status_code == 200:
            if response.text == "test_challenge_12345":
                print("✅ Validation webhook: OK")
                print(f"   Challenge retourné: {response.text}")
            else:
                print(f"❌ Challenge incorrect: attendu 'test_challenge_12345', reçu '{response.text}'")
        else:
            print(f"❌ Validation webhook: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
    
    # Test 3: Webhook message (POST)
    print("\n3. Test message webhook (POST):")
    try:
        test_payload = {
            "object": "page",
            "entry": [
                {
                    "id": "TEST_PAGE_ID",
                    "time": int(time.time()),
                    "messaging": [
                        {
                            "sender": {"id": "TEST_USER_ID"},
                            "recipient": {"id": "TEST_PAGE_ID"},
                            "timestamp": int(time.time() * 1000),
                            "message": {
                                "mid": "TEST_MESSAGE_ID",
                                "text": "Message de test depuis script de validation"
                            }
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/webhook",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Message webhook: OK")
            result = response.json()
            print(f"   Status: {result.get('status')}")
        else:
            print(f"❌ Message webhook: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur message: {e}")
    
    print("\n" + "=" * 40)
    print("🎯 Tests terminés")
    
    # Vérifier ngrok si fichier URL existe
    try:
        with open("ngrok_url.txt", "r") as f:
            ngrok_url = f.read().strip()
        
        if ngrok_url:
            print(f"\n🌐 URL ngrok détectée: {ngrok_url}")
            print(f"📝 Webhook URL: {ngrok_url}/api/webhook")
            
            # Test rapide ngrok
            print("\n4. Test rapide ngrok:")
            try:
                response = requests.get(f"{ngrok_url}/api/health", timeout=15)
                if response.status_code == 200:
                    print("✅ Ngrok accessible: OK")
                else:
                    print(f"❌ Ngrok: {response.status_code}")
            except Exception as e:
                print(f"❌ Erreur ngrok: {e}")
                
    except FileNotFoundError:
        print("\n⚠️ Fichier ngrok_url.txt non trouvé")

def show_curl_commands():
    """Affiche les commandes curl utiles"""
    
    print("\n📋 COMMANDES CURL UTILES:")
    print("=" * 30)
    
    print("\n# Test validation local:")
    print('curl "http://localhost:8001/api/webhook?hub.mode=subscribe&hub.verify_token=mon_token_secret_webhook&hub.challenge=12345"')
    
    print("\n# Test message local:")
    print('curl -X POST "http://localhost:8001/api/webhook" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"object":"page","entry":[{"messaging":[{"sender":{"id":"test"},"message":{"text":"Hello"}}]}]}\'')
    
    print("\n# Test santé:")
    print('curl "http://localhost:8001/api/health"')

if __name__ == "__main__":
    test_webhook_simple()
    show_curl_commands()