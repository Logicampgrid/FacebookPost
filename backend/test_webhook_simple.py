#!/usr/bin/env python3
"""
Script de test simple pour valider le webhook Facebook
Compatible Windows + Python 3.11
Corrección: Facebook attend le challenge comme string, pas int
"""

import requests
import json
import time
import sys

def test_webhook_simple():
    """Test rapide du webhook avec corrections Facebook"""
    
    # Configuration
    BASE_URL = "http://localhost:8001"  # Port standard backend
    VERIFY_TOKEN = "mon_token_secret_webhook"  # Token par défaut
    
    print("🔍 Test simple du webhook Facebook - v2.0")
    print("=" * 50)
    
    # Test 1: Endpoint de santé
    print("\n1. Test endpoint de santé:")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Endpoint santé: OK")
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Ngrok: {health_data.get('ngrok', {}).get('enabled', 'Unknown')}")
        else:
            print(f"❌ Endpoint santé: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur santé: {e}")
        print("   💡 Vérifiez que server.py tourne sur le port 8001")
        return False
    
    # Test 2: Validation webhook (GET) - CORRECTION FACEBOOK
    print("\n2. Test validation webhook (GET):")
    try:
        # Paramètres Facebook standard
        params = {
            "hub.mode": "subscribe",
            "hub.verify_token": VERIFY_TOKEN,
            "hub.challenge": "test_challenge_12345"
        }
        
        response = requests.get(f"{BASE_URL}/api/webhook", params=params, timeout=10)
        
        if response.status_code == 200:
            # CORRECTION: Facebook attend le challenge exact (string)
            expected_challenge = "test_challenge_12345"
            received_challenge = response.text.strip('"')  # Enlever guillemets JSON
            
            if received_challenge == expected_challenge:
                print("✅ Validation webhook: OK")
                print(f"   Challenge retourné: {received_challenge}")
            else:
                print(f"❌ Challenge incorrect:")
                print(f"   Attendu: {expected_challenge}")
                print(f"   Reçu: {received_challenge}")
                return False
        else:
            print(f"❌ Validation webhook: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
            # Aide au debug
            if response.status_code == 403:
                print("   💡 Vérifiez le token de vérification dans server.py")
            elif response.status_code == 500:
                print("   💡 Erreur serveur, vérifiez les logs backend")
            
            return False
            
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        return False
    
    # Test 3: Webhook message (POST) - CORRECTION FORMAT
    print("\n3. Test message webhook (POST):")
    try:
        # Payload Facebook standard
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
                                "text": "Message de test depuis validation automatique"
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
            result = response.json()
            if result.get("status") == "received":
                print("✅ Message webhook: OK")
                print(f"   Status: {result.get('status')}")
                print(f"   Timestamp: {result.get('timestamp')}")
            else:
                print(f"❌ Statut incorrect: {result}")
                return False
        else:
            print(f"❌ Message webhook: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur message: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎯 TOUS LES TESTS RÉUSSIS!")
    
    # Test ngrok si URL existe
    try:
        with open("ngrok_url.txt", "r") as f:
            ngrok_url = f.read().strip()
        
        if ngrok_url:
            print(f"\n🌐 URL ngrok détectée: {ngrok_url}")
            print(f"📝 Webhook URL: {ngrok_url}/api/webhook")
            
            print("\n4. Test rapide ngrok:")
            try:
                response = requests.get(f"{ngrok_url}/api/health", timeout=15)
                if response.status_code == 200:
                    print("✅ Ngrok accessible: OK")
                else:
                    print(f"⚠️ Ngrok: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Ngrok inaccessible: {e}")
        else:
            print("\n⚠️ Pas d'URL ngrok active")
                
    except FileNotFoundError:
        print("\n⚠️ Fichier ngrok_url.txt non trouvé")
    
    return True

def show_curl_commands():
    """Affiche les commandes curl corrigées pour Windows"""
    
    print("\n📋 COMMANDES CURL POUR WINDOWS:")
    print("=" * 40)
    
    print("\n# Test validation (GET):")
    print('curl "http://localhost:8001/api/webhook?hub.mode=subscribe&hub.verify_token=mon_token_secret_webhook&hub.challenge=12345"')
    
    print("\n# Test message (POST) - Windows:")
    print('curl -X POST "http://localhost:8001/api/webhook" ^')
    print('  -H "Content-Type: application/json" ^')
    print('  -d "{\\"object\\":\\"page\\",\\"entry\\":[{\\"messaging\\":[{\\"sender\\":{\\"id\\":\\"test\\"},\\"message\\":{\\"text\\":\\"Hello\\"}}]}]}"')
    
    print("\n# Test santé:")
    print('curl "http://localhost:8001/api/health"')
    
    print("\n💡 NOTES IMPORTANTES:")
    print("- Le challenge doit être retourné exactement comme reçu")
    print("- Le POST doit retourner: {\"status\": \"received\"}")
    print("- Vérifiez que server.py tourne sur le port 8001")

def main():
    """Point d'entrée avec gestion d'erreurs"""
    try:
        success = test_webhook_simple()
        if success:
            show_curl_commands()
            print("\n🎉 Webhook prêt pour Facebook!")
        else:
            print("\n❌ Tests échoués - Vérifiez server.py")
            show_curl_commands()
            return 1
        return 0
    except KeyboardInterrupt:
        print("\n🛑 Tests interrompus par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    
    # Pause sur Windows pour voir les résultats
    if sys.platform.startswith('win'):
        try:
            input("\nAppuyez sur Entrée pour fermer...")
        except:
            pass
    
    sys.exit(exit_code)