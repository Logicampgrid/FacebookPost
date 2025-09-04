#!/usr/bin/env python3
"""
Script d'automatisation webhook Facebook pour Windows
À utiliser depuis C:\FacebookPost
"""

import subprocess
import time
import requests
import os
import sys
import json
import psutil
from pathlib import Path

class WindowsWebhookAutomation:
    def __init__(self):
        # Configuration pour Windows
        self.PROJECT_PATH = Path("C:/FacebookPost")
        self.BACKEND_PATH = self.PROJECT_PATH / "backend"
        self.BACKEND_PORT = 8001
        self.NGROK_URL = None
        self.ngrok_process = None
        self.backend_process = None
        
        # Configuration Facebook (à définir dans .env ou directement ici)
        self.FACEBOOK_APP_ID = "YOUR_APP_ID"
        self.FACEBOOK_APP_SECRET = "YOUR_APP_SECRET"
        self.FACEBOOK_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
        self.FACEBOOK_PAGE_ID = "YOUR_PAGE_ID"
        self.FACEBOOK_VERIFY_TOKEN = "mon_token_secret_webhook"
        
        print("🚀 Automatisation webhook Facebook pour Windows")
        print(f"📁 Chemin projet: {self.PROJECT_PATH}")
        print(f"📁 Chemin backend: {self.BACKEND_PATH}")

    def detect_backend_port(self):
        """Détecte automatiquement le port du backend"""
        print("🔍 Détection du port backend...")
        
        # Vérifier les processus Python qui utilisent des ports
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                    cmdline = proc.info['cmdline']
                    if cmdline and 'server.py' in ' '.join(cmdline):
                        # Processus backend trouvé, vérifier les connexions
                        connections = proc.connections()
                        for conn in connections:
                            if conn.status == 'LISTEN':
                                port = conn.laddr.port
                                if port in [8000, 8001, 5000, 3000]:  # Ports communs
                                    print(f"✅ Backend détecté sur le port {port}")
                                    self.BACKEND_PORT = port
                                    return port
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Si pas trouvé, tester les ports communs
        test_ports = [8001, 8000, 5000]
        for port in test_ports:
            try:
                response = requests.get(f"http://localhost:{port}", timeout=2)
                print(f"✅ Backend trouvé sur le port {port}")
                self.BACKEND_PORT = port
                return port
            except:
                continue
        
        print(f"⚠️ Backend non détecté, utilisation du port par défaut: {self.BACKEND_PORT}")
        return self.BACKEND_PORT

    def start_backend_if_needed(self):
        """Démarre le backend si nécessaire"""
        try:
            # Tester si le backend répond
            response = requests.get(f"http://localhost:{self.BACKEND_PORT}/api/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Backend déjà actif sur le port {self.BACKEND_PORT}")
                return True
        except:
            pass
        
        print("🚀 Démarrage du backend...")
        
        # Changer vers le répertoire backend
        os.chdir(self.BACKEND_PATH)
        
        # Lancer le serveur Python
        try:
            self.backend_process = subprocess.Popen([
                sys.executable, "server.py"
            ], cwd=str(self.BACKEND_PATH))
            
            # Attendre que le serveur démarre
            time.sleep(5)
            
            # Vérifier que le serveur répond
            for attempt in range(10):
                try:
                    response = requests.get(f"http://localhost:{self.BACKEND_PORT}/api/health", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Backend démarré avec succès sur le port {self.BACKEND_PORT}")
                        return True
                except:
                    time.sleep(1)
            
            print("❌ Le backend ne répond pas après le démarrage")
            return False
            
        except Exception as e:
            print(f"❌ Erreur démarrage backend: {e}")
            return False

    def start_ngrok(self):
        """Lance ngrok sur le port détecté"""
        try:
            print("🔗 Arrêt des processus ngrok existants...")
            subprocess.run(["taskkill", "/f", "/im", "ngrok.exe"], capture_output=True, shell=True)
            time.sleep(2)
            
            print(f"🚀 Lancement de ngrok sur le port {self.BACKEND_PORT}...")
            self.ngrok_process = subprocess.Popen([
                "ngrok", "http", str(self.BACKEND_PORT)
            ], shell=True)
            
            # Attendre que ngrok démarre
            time.sleep(5)
            
            # Récupérer l'URL publique
            max_attempts = 15
            for attempt in range(max_attempts):
                try:
                    response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
                    if response.status_code == 200:
                        tunnels = response.json()
                        if tunnels.get('tunnels') and len(tunnels['tunnels']) > 0:
                            self.NGROK_URL = tunnels['tunnels'][0]['public_url']
                            print(f"🌐 Ngrok actif: {self.NGROK_URL}")
                            
                            # Sauvegarder l'URL dans un fichier
                            with open(self.BACKEND_PATH / "ngrok_url.txt", "w") as f:
                                f.write(self.NGROK_URL)
                            print("💾 URL ngrok sauvegardée")
                            
                            return True
                        else:
                            print(f"⏳ Tentative {attempt + 1}/{max_attempts}: Tunnel en cours...")
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

    def test_webhook_endpoints(self):
        """Teste les endpoints webhook localement et via ngrok"""
        print("\n🔍 Tests des endpoints webhook...")
        
        # Test local GET
        print("📍 Test local GET (validation Facebook):")
        try:
            params = {
                "hub.mode": "subscribe",
                "hub.verify_token": self.FACEBOOK_VERIFY_TOKEN,
                "hub.challenge": "test_challenge_123"
            }
            response = requests.get(f"http://localhost:{self.BACKEND_PORT}/api/webhook", params=params, timeout=10)
            if response.status_code == 200 and response.text == "test_challenge_123":
                print("✅ Test GET local: SUCCÈS")
            else:
                print(f"❌ Test GET local: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Erreur test GET local: {e}")
        
        # Test local POST
        print("\n📍 Test local POST (message webhook):")
        try:
            payload = {
                "object": "page",
                "entry": [{
                    "messaging": [{
                        "sender": {"id": "test_user"},
                        "message": {"text": "Test message local"}
                    }]
                }]
            }
            response = requests.post(f"http://localhost:{self.BACKEND_PORT}/api/webhook", json=payload, timeout=10)
            if response.status_code == 200:
                print("✅ Test POST local: SUCCÈS")
            else:
                print(f"❌ Test POST local: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur test POST local: {e}")
        
        # Tests ngrok si disponible
        if self.NGROK_URL:
            print(f"\n🌐 Tests via ngrok: {self.NGROK_URL}")
            
            # Test ngrok GET
            try:
                params = {
                    "hub.mode": "subscribe",
                    "hub.verify_token": self.FACEBOOK_VERIFY_TOKEN,
                    "hub.challenge": "ngrok_test_456"
                }
                response = requests.get(f"{self.NGROK_URL}/api/webhook", params=params, timeout=15)
                if response.status_code == 200 and response.text == "ngrok_test_456":
                    print("✅ Test GET ngrok: SUCCÈS")
                else:
                    print(f"❌ Test GET ngrok: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"❌ Erreur test GET ngrok: {e}")
            
            # Test ngrok POST
            try:
                payload = {
                    "object": "page",
                    "entry": [{
                        "messaging": [{
                            "sender": {"id": "test_user_ngrok"},
                            "message": {"text": "Test message via ngrok"}
                        }]
                    }]
                }
                response = requests.post(f"{self.NGROK_URL}/api/webhook", json=payload, timeout=15)
                if response.status_code == 200:
                    print("✅ Test POST ngrok: SUCCÈS")
                else:
                    print(f"❌ Test POST ngrok: {response.status_code}")
            except Exception as e:
                print(f"❌ Erreur test POST ngrok: {e}")

    def generate_commands(self):
        """Génère toutes les commandes utiles"""
        print(f"\n📋 COMMANDES POUR CONFIGURATION FACEBOOK")
        print("=" * 60)
        
        if self.NGROK_URL:
            print(f"\n🔗 URL ngrok actuelle: {self.NGROK_URL}")
            print(f"📝 URL webhook: {self.NGROK_URL}/api/webhook")
            print(f"🔑 Token de vérification: {self.FACEBOOK_VERIFY_TOKEN}")
            
            print(f"\n📋 COMMANDE CURL pour configurer le webhook Facebook:")
            print(f'curl -X POST "https://graph.facebook.com/v18.0/{self.FACEBOOK_PAGE_ID}/subscriptions" ^')
            print(f'  -d "callback_url={self.NGROK_URL}/api/webhook" ^')
            print(f'  -d "verify_token={self.FACEBOOK_VERIFY_TOKEN}" ^')
            print(f'  -d "fields=messages,messaging_postbacks,messaging_optins" ^')
            print(f'  -d "access_token={self.FACEBOOK_ACCESS_TOKEN}"')
            
            print(f"\n📋 COMMANDES DE TEST:")
            print(f"# Test GET (validation):")
            print(f'curl "{self.NGROK_URL}/api/webhook?hub.mode=subscribe&hub.verify_token={self.FACEBOOK_VERIFY_TOKEN}&hub.challenge=12345"')
            
            print(f"\n# Test POST (message):")
            print(f'curl -X POST "{self.NGROK_URL}/api/webhook" ^')
            print('  -H "Content-Type: application/json" ^')
            print('  -d "{\\"object\\":\\"page\\",\\"entry\\":[{\\"messaging\\":[{\\"sender\\":{\\"id\\":\\"test\\"},\\"message\\":{\\"text\\":\\"Hello\\"}}]}]}"')
        
        print(f"\n📋 COMMANDES LOCALES:")
        print(f'curl "http://localhost:{self.BACKEND_PORT}/api/webhook?hub.mode=subscribe&hub.verify_token={self.FACEBOOK_VERIFY_TOKEN}&hub.challenge=12345"')

    def cleanup(self):
        """Nettoie les processus lancés"""
        print("\n🧹 Nettoyage des processus...")
        
        if self.ngrok_process:
            self.ngrok_process.terminate()
            subprocess.run(["taskkill", "/f", "/im", "ngrok.exe"], capture_output=True, shell=True)
        
        if self.backend_process:
            self.backend_process.terminate()
        
        print("✅ Nettoyage terminé")

    def run_automation(self):
        """Exécute l'automatisation complète"""
        print("🎯 AUTOMATISATION WEBHOOK FACEBOOK - WINDOWS")
        print("=" * 50)
        
        try:
            # 1. Détecter le port backend
            self.detect_backend_port()
            
            # 2. Démarrer le backend si nécessaire
            if not self.start_backend_if_needed():
                print("❌ Impossible de démarrer le backend")
                return False
            
            # 3. Lancer ngrok
            if not self.start_ngrok():
                print("❌ Échec du lancement de ngrok")
                return False
            
            # 4. Tester les endpoints
            self.test_webhook_endpoints()
            
            # 5. Générer les commandes
            self.generate_commands()
            
            print(f"\n🎉 AUTOMATISATION TERMINÉE!")
            print(f"🔗 URL ngrok: {self.NGROK_URL}")
            print(f"📝 Webhook: {self.NGROK_URL}/api/webhook")
            
            # Maintenir les processus actifs
            print(f"\n⏸️ Processus actifs. Appuyez sur Ctrl+C pour arrêter...")
            while True:
                time.sleep(5)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Arrêt demandé...")
            self.cleanup()
        except Exception as e:
            print(f"❌ Erreur: {e}")
            self.cleanup()

def main():
    # Vérifier qu'on est sur Windows
    if os.name != 'nt':
        print("❌ Ce script est conçu pour Windows")
        sys.exit(1)
    
    # Vérifier que le projet existe
    project_path = Path("C:/FacebookPost")
    if not project_path.exists():
        print(f"❌ Projet non trouvé: {project_path}")
        print("Assurez-vous d'être dans le bon répertoire")
        sys.exit(1)
    
    automation = WindowsWebhookAutomation()
    automation.run_automation()

if __name__ == "__main__":
    main()