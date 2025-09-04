#!/usr/bin/env python3
"""
Script d'automatisation complet pour le webhook Facebook avec ngrok
Fonctions :
- Détection automatique du port backend
- Lancement de ngrok sur le port exact
- Configuration automatique du webhook Facebook
- Tests de validation
"""

import subprocess
import time
import requests
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

class FacebookWebhookAutomation:
    def __init__(self):
        # Configuration Facebook (à définir dans .env ou directement ici)
        self.FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID", "YOUR_APP_ID")
        self.FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET", "YOUR_APP_SECRET")  
        self.FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "YOUR_ACCESS_TOKEN")
        self.FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "YOUR_PAGE_ID")
        self.FACEBOOK_VERIFY_TOKEN = os.getenv("FACEBOOK_VERIFY_TOKEN", "mon_token_secret_webhook")
        
        # Configuration serveur
        self.BACKEND_PORT = 8001
        self.BACKEND_HOST = "localhost"
        self.NGROK_URL = None
        self.ngrok_process = None
        
        print("🚀 Initialisation de l'automatisation webhook Facebook")
        print(f"📍 Port backend détecté: {self.BACKEND_PORT}")

    def check_backend_running(self):
        """Vérifie si le backend tourne sur le port configuré"""
        try:
            response = requests.get(f"http://{self.BACKEND_HOST}:{self.BACKEND_PORT}/api/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Backend actif sur le port {self.BACKEND_PORT}")
                return True
            else:
                print(f"⚠️ Backend répond mais avec status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Backend non accessible sur le port {self.BACKEND_PORT}: {e}")
            return False

    def start_ngrok(self):
        """Lance ngrok sur le port backend"""
        try:
            print("🔗 Arrêt des processus ngrok existants...")
            subprocess.run(["pkill", "-f", "ngrok"], capture_output=True)
            time.sleep(2)
            
            print(f"🚀 Lancement de ngrok sur le port {self.BACKEND_PORT}...")
            self.ngrok_process = subprocess.Popen(
                ["ngrok", "http", str(self.BACKEND_PORT), "--log=stdout"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Attendre que ngrok démarre
            time.sleep(4)
            
            # Récupérer l'URL publique
            max_attempts = 10
            for attempt in range(max_attempts):
                try:
                    response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
                    if response.status_code == 200:
                        tunnels = response.json()
                        if tunnels.get('tunnels') and len(tunnels['tunnels']) > 0:
                            self.NGROK_URL = tunnels['tunnels'][0]['public_url']
                            print(f"🌐 Ngrok actif: {self.NGROK_URL}")
                            
                            # Sauvegarder l'URL
                            with open("/app/backend/ngrok_url.txt", "w") as f:
                                f.write(self.NGROK_URL)
                            print("💾 URL ngrok sauvegardée")
                            
                            return True
                        else:
                            print(f"⏳ Tentative {attempt + 1}/{max_attempts}: Tunnel en cours de création...")
                            time.sleep(2)
                    else:
                        print(f"⏳ API ngrok status: {response.status_code}")
                        time.sleep(2)
                except requests.exceptions.RequestException:
                    print(f"⏳ Tentative {attempt + 1}/{max_attempts}: Connexion API ngrok...")
                    time.sleep(2)
            
            print("❌ Impossible d'obtenir l'URL ngrok")
            return False
            
        except Exception as e:
            print(f"❌ Erreur ngrok: {e}")
            return False

    def test_webhook_local(self):
        """Teste le webhook en local"""
        print("\n🔍 Test du webhook en local...")
        
        # Test GET (validation Facebook)
        try:
            verify_params = {
                "hub.mode": "subscribe",
                "hub.verify_token": self.FACEBOOK_VERIFY_TOKEN,
                "hub.challenge": "1234567890"
            }
            
            response = requests.get(
                f"http://{self.BACKEND_HOST}:{self.BACKEND_PORT}/api/webhook",
                params=verify_params,
                timeout=10
            )
            
            if response.status_code == 200 and response.text == "1234567890":
                print("✅ Test GET local: SUCCÈS")
            else:
                print(f"❌ Test GET local échoué: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur test GET local: {e}")
            return False
        
        # Test POST (message webhook)
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
                                    "text": "Test message from automation script"
                                }
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"http://{self.BACKEND_HOST}:{self.BACKEND_PORT}/api/webhook",
                json=test_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Test POST local: SUCCÈS")
                return True
            else:
                print(f"❌ Test POST local échoué: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur test POST local: {e}")
            return False

    def test_webhook_ngrok(self):
        """Teste le webhook via ngrok"""
        if not self.NGROK_URL:
            print("❌ URL ngrok non disponible")
            return False
            
        print(f"\n🌐 Test du webhook via ngrok: {self.NGROK_URL}")
        
        # Test GET (validation Facebook)
        try:
            verify_params = {
                "hub.mode": "subscribe",
                "hub.verify_token": self.FACEBOOK_VERIFY_TOKEN,
                "hub.challenge": "9876543210"
            }
            
            response = requests.get(
                f"{self.NGROK_URL}/api/webhook",
                params=verify_params,
                timeout=15
            )
            
            if response.status_code == 200 and response.text == "9876543210":
                print("✅ Test GET ngrok: SUCCÈS")
            else:
                print(f"❌ Test GET ngrok échoué: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur test GET ngrok: {e}")
            return False
        
        # Test POST
        try:
            test_payload = {
                "object": "page",
                "entry": [
                    {
                        "id": "TEST_PAGE_ID_NGROK",
                        "time": int(time.time()),
                        "messaging": [
                            {
                                "sender": {"id": "TEST_USER_ID_NGROK"},
                                "recipient": {"id": "TEST_PAGE_ID_NGROK"},
                                "timestamp": int(time.time() * 1000),
                                "message": {
                                    "mid": "TEST_MESSAGE_ID_NGROK",
                                    "text": "Test message via ngrok"
                                }
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{self.NGROK_URL}/api/webhook",
                json=test_payload,
                timeout=15
            )
            
            if response.status_code == 200:
                print("✅ Test POST ngrok: SUCCÈS")
                return True
            else:
                print(f"❌ Test POST ngrok échoué: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur test POST ngrok: {e}")
            return False

    def configure_facebook_webhook(self):
        """Configure automatiquement le webhook Facebook"""
        if not self.NGROK_URL:
            print("❌ URL ngrok requise pour configurer Facebook")
            return False
            
        print(f"\n📝 Configuration du webhook Facebook...")
        print(f"🔗 URL webhook: {self.NGROK_URL}/api/webhook")
        
        # URL de l'API Graph Facebook
        webhook_url = f"https://graph.facebook.com/v18.0/{self.FACEBOOK_PAGE_ID}/subscriptions"
        
        webhook_data = {
            "callback_url": f"{self.NGROK_URL}/api/webhook",
            "verify_token": self.FACEBOOK_VERIFY_TOKEN,
            "fields": "messages,messaging_postbacks,messaging_optins,message_deliveries,message_reads",
            "access_token": self.FACEBOOK_ACCESS_TOKEN
        }
        
        try:
            response = requests.post(webhook_url, data=webhook_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ Webhook Facebook configuré avec succès!")
                    return True
                else:
                    print(f"❌ Échec configuration Facebook: {result}")
                    return False
            else:
                print(f"❌ Erreur API Facebook: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur configuration Facebook: {e}")
            return False

    def generate_curl_commands(self):
        """Génère les commandes curl pour les tests manuels"""
        print(f"\n📋 COMMANDES CURL POUR TESTS MANUELS:")
        print("=" * 60)
        
        # Commandes locales
        print("\n🏠 TESTS LOCAUX:")
        print(f"# Test GET (validation):")
        print(f'curl -X GET "http://localhost:{self.BACKEND_PORT}/api/webhook?hub.mode=subscribe&hub.verify_token={self.FACEBOOK_VERIFY_TOKEN}&hub.challenge=12345"')
        
        print(f"\n# Test POST (message):")
        print(f'curl -X POST "http://localhost:{self.BACKEND_PORT}/api/webhook" \\')
        print('  -H "Content-Type: application/json" \\')
        print('  -d \'{"object":"page","entry":[{"messaging":[{"sender":{"id":"test"},"message":{"text":"Hello"}}]}]}\'')
        
        # Commandes ngrok si disponible
        if self.NGROK_URL:
            print(f"\n🌐 TESTS NGROK:")
            print(f"# Test GET via ngrok:")
            print(f'curl -X GET "{self.NGROK_URL}/api/webhook?hub.mode=subscribe&hub.verify_token={self.FACEBOOK_VERIFY_TOKEN}&hub.challenge=12345"')
            
            print(f"\n# Test POST via ngrok:")
            print(f'curl -X POST "{self.NGROK_URL}/api/webhook" \\')
            print('  -H "Content-Type: application/json" \\')
            print('  -d \'{"object":"page","entry":[{"messaging":[{"sender":{"id":"test"},"message":{"text":"Hello via ngrok"}}]}]}\'')
            
            print(f"\n📝 CONFIGURATION FACEBOOK:")
            print(f"# Commande pour configurer le webhook Facebook:")
            print(f'curl -X POST "https://graph.facebook.com/v18.0/{self.FACEBOOK_PAGE_ID}/subscriptions" \\')
            print(f'  -d "callback_url={self.NGROK_URL}/api/webhook" \\')
            print(f'  -d "verify_token={self.FACEBOOK_VERIFY_TOKEN}" \\')
            print(f'  -d "fields=messages,messaging_postbacks" \\')
            print(f'  -d "access_token={self.FACEBOOK_ACCESS_TOKEN}"')

    def run_full_automation(self):
        """Exécute le processus complet d'automatisation"""
        print("🎯 DÉMARRAGE DE L'AUTOMATISATION COMPLÈTE")
        print("=" * 50)
        
        # 1. Vérifier le backend
        if not self.check_backend_running():
            print("❌ Backend non accessible. Assurez-vous qu'il tourne sur le port 8001")
            return False
        
        # 2. Lancer ngrok
        if not self.start_ngrok():
            print("❌ Échec du lancement de ngrok")
            return False
        
        # 3. Tester en local
        if not self.test_webhook_local():
            print("❌ Tests locaux échoués")
            return False
        
        # 4. Tester via ngrok
        if not self.test_webhook_ngrok():
            print("❌ Tests ngrok échoués")
            return False
        
        # 5. Configurer Facebook (optionnel - demander confirmation)
        configure_fb = input("\n❓ Configurer automatiquement le webhook Facebook ? (y/N): ").lower().strip()
        if configure_fb == 'y':
            self.configure_facebook_webhook()
        
        # 6. Générer les commandes curl
        self.generate_curl_commands()
        
        print(f"\n🎉 AUTOMATISATION TERMINÉE AVEC SUCCÈS!")
        print(f"🔗 URL ngrok active: {self.NGROK_URL}")
        print(f"📝 URL webhook: {self.NGROK_URL}/api/webhook")
        print(f"🔑 Token de vérification: {self.FACEBOOK_VERIFY_TOKEN}")
        
        return True

    def stop_ngrok(self):
        """Arrête ngrok proprement"""
        if self.ngrok_process:
            print("🛑 Arrêt de ngrok...")
            self.ngrok_process.terminate()
            subprocess.run(["pkill", "-f", "ngrok"], capture_output=True)
            print("✅ Ngrok arrêté")

def main():
    automation = FacebookWebhookAutomation()
    
    try:
        automation.run_full_automation()
        
        # Maintenir ngrok actif
        print(f"\n⏸️ Ngrok reste actif. Appuyez sur Ctrl+C pour arrêter...")
        automation.ngrok_process.wait()
        
    except KeyboardInterrupt:
        print(f"\n🛑 Arrêt demandé par l'utilisateur...")
        automation.stop_ngrok()
        print("✅ Processus terminé proprement")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        automation.stop_ngrok()

if __name__ == "__main__":
    main()