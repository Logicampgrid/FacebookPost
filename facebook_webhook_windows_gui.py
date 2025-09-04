#!/usr/bin/env python3
"""
Script d'automatisation webhook Facebook pour Windows avec GUI
Compatible Python 3.11 + Windows 11
Fonctionnalités :
- Détection automatique du backend sur port 8001
- Lancement ngrok et récupération de l'URL publique
- Tests automatiques GET/POST endpoints
- Configuration webhook Facebook
- Interface GUI avec logs en temps réel
- Logs persistants dans webhook_log.txt
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import time
import requests
import os
import sys
import json
import threading
import psutil
from pathlib import Path
from datetime import datetime

class FacebookWebhookGUI:
    def __init__(self):
        # Configuration projet Windows
        self.PROJECT_PATH = Path("C:/FacebookPost")
        self.BACKEND_PATH = self.PROJECT_PATH / "backend"
        self.LOG_FILE = self.PROJECT_PATH / "webhook_log.txt"
        
        # Configuration serveur
        self.BACKEND_PORT = 8001
        self.BACKEND_HOST = "localhost"
        self.NGROK_URL = None
        self.ngrok_process = None
        self.backend_process = None
        
        # Configuration Facebook (à modifier selon vos besoins)
        self.FACEBOOK_APP_ID = "YOUR_APP_ID"
        self.FACEBOOK_APP_SECRET = "YOUR_APP_SECRET"  
        self.FACEBOOK_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
        self.FACEBOOK_PAGE_ID = "YOUR_PAGE_ID"
        self.FACEBOOK_VERIFY_TOKEN = "mon_token_secret_webhook"
        
        # État de l'application
        self.is_running = False
        self.tests_passed = False
        
        # Initialiser GUI
        self.setup_gui()
        self.log("🚀 Automatisation webhook Facebook - Windows GUI v1.0")
        self.log(f"📁 Projet: {self.PROJECT_PATH}")
        
        # Nettoyer les anciens logs
        self.clear_old_logs()

    def setup_gui(self):
        """Configure l'interface graphique"""
        self.root = tk.Tk()
        self.root.title("Facebook Webhook Automation - Windows")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Frame pour les boutons
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=10)
        
        # Boutons principaux
        self.start_btn = tk.Button(button_frame, text="🚀 Démarrer Automatisation", 
                                  command=self.start_automation, bg='#4CAF50', fg='white',
                                  font=('Arial', 12, 'bold'), padx=20)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.test_btn = tk.Button(button_frame, text="🔍 Tester Webhook", 
                                 command=self.test_only, bg='#2196F3', fg='white',
                                 font=('Arial', 12, 'bold'), padx=20)
        self.test_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(button_frame, text="🛑 Arrêter", 
                                 command=self.stop_automation, bg='#f44336', fg='white',
                                 font=('Arial', 12, 'bold'), padx=20)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame pour les informations
        info_frame = tk.Frame(self.root, bg='#f0f0f0')
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = tk.Label(info_frame, text="Statut: Prêt", 
                                    font=('Arial', 10, 'bold'), bg='#f0f0f0')
        self.status_label.pack(anchor=tk.W)
        
        self.ngrok_label = tk.Label(info_frame, text="URL ngrok: Non configuré", 
                                   font=('Arial', 9), bg='#f0f0f0', fg='#666')
        self.ngrok_label.pack(anchor=tk.W)
        
        # Zone de logs
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(log_frame, text="📋 Logs en temps réel:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=25, 
                                                 font=('Consolas', 9),
                                                 bg='#1e1e1e', fg='#ffffff')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Frame footer avec commandes
        footer_frame = tk.Frame(self.root, bg='#f0f0f0')
        footer_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.commands_btn = tk.Button(footer_frame, text="📋 Voir Commandes curl", 
                                     command=self.show_commands, bg='#FF9800', fg='white',
                                     font=('Arial', 10), padx=15)
        self.commands_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(footer_frame, text="🧹 Effacer Logs", 
                                  command=self.clear_logs, bg='#9E9E9E', fg='white',
                                  font=('Arial', 10), padx=15)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

    def log(self, message, level="INFO"):
        """Affiche un message dans les logs et sauvegarde dans le fichier"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Icônes selon le niveau
        icons = {
            "INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", 
            "ERROR": "❌", "DEBUG": "🔧", "NETWORK": "🌐"
        }
        icon = icons.get(level.upper(), "📝")
        
        log_message = f"[{timestamp}] {icon} {message}"
        
        # Affichage dans GUI
        self.log_text.insert(tk.END, log_message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
        
        # Sauvegarde dans fichier
        try:
            with open(self.LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
        except Exception as e:
            print(f"Erreur sauvegarde log: {e}")

    def clear_old_logs(self):
        """Supprime les anciens logs au démarrage"""
        try:
            if self.LOG_FILE.exists():
                self.LOG_FILE.unlink()
            self.log("🧹 Anciens logs supprimés", "DEBUG")
        except Exception as e:
            self.log(f"Erreur suppression logs: {e}", "WARNING")

    def clear_logs(self):
        """Efface les logs à l'écran"""
        self.log_text.delete(1.0, tk.END)

    def update_status(self, status, color="#000"):
        """Met à jour le statut affiché"""
        self.status_label.config(text=f"Statut: {status}", fg=color)
        self.root.update()

    def update_ngrok_url(self, url=None):
        """Met à jour l'URL ngrok affichée"""
        if url:
            self.ngrok_label.config(text=f"URL ngrok: {url}", fg="#4CAF50")
            self.NGROK_URL = url
        else:
            self.ngrok_label.config(text="URL ngrok: Non configuré", fg="#666")
        self.root.update()

    def detect_backend_port(self):
        """Détecte automatiquement le port du backend"""
        self.log("🔍 Détection du port backend...", "DEBUG")
        
        # Vérifier les processus Python
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline and any('server.py' in str(cmd) for cmd in cmdline):
                        connections = proc.connections()
                        for conn in connections:
                            if conn.status == 'LISTEN' and conn.laddr.port in [8000, 8001, 5000]:
                                self.BACKEND_PORT = conn.laddr.port
                                self.log(f"✅ Backend détecté sur port {self.BACKEND_PORT}", "SUCCESS")
                                return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Test direct des ports communs
        test_ports = [8001, 8000, 5000]
        for port in test_ports:
            try:
                response = requests.get(f"http://localhost:{port}/api/health", timeout=3)
                if response.status_code == 200:
                    self.BACKEND_PORT = port
                    self.log(f"✅ Backend trouvé sur port {port}", "SUCCESS")
                    return True
            except:
                continue
        
        self.log(f"⚠️ Backend non détecté, port par défaut: {self.BACKEND_PORT}", "WARNING")
        return False

    def check_backend_health(self):
        """Vérifie que le backend répond correctement"""
        try:
            self.log("🔍 Vérification santé backend...", "DEBUG")
            response = requests.get(f"http://{self.BACKEND_HOST}:{self.BACKEND_PORT}/api/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                self.log(f"✅ Backend actif: {health_data.get('status', 'unknown')}", "SUCCESS")
                return True
            else:
                self.log(f"❌ Backend répond avec erreur: {response.status_code}", "ERROR")
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Backend inaccessible: {e}", "ERROR")
            return False

    def start_ngrok(self):
        """Lance ngrok et récupère l'URL publique"""
        try:
            self.log("🔗 Arrêt des processus ngrok existants...", "DEBUG")
            subprocess.run(["taskkill", "/f", "/im", "ngrok.exe"], 
                         capture_output=True, shell=True, check=False)
            time.sleep(2)
            
            self.log(f"🚀 Lancement ngrok sur port {self.BACKEND_PORT}...", "NETWORK")
            self.ngrok_process = subprocess.Popen([
                "ngrok", "http", str(self.BACKEND_PORT)
            ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Attendre démarrage ngrok
            time.sleep(6)
            
            # Récupérer URL publique
            max_attempts = 20
            for attempt in range(max_attempts):
                try:
                    response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
                    if response.status_code == 200:
                        tunnels = response.json()
                        if tunnels.get('tunnels') and len(tunnels['tunnels']) > 0:
                            public_url = tunnels['tunnels'][0]['public_url']
                            self.update_ngrok_url(public_url)
                            self.log(f"🌐 Ngrok actif: {public_url}", "SUCCESS")
                            
                            # Sauvegarder URL
                            try:
                                with open(self.BACKEND_PATH / "ngrok_url.txt", "w") as f:
                                    f.write(public_url)
                                self.log("💾 URL ngrok sauvegardée", "DEBUG")
                            except Exception as e:
                                self.log(f"⚠️ Erreur sauvegarde URL: {e}", "WARNING")
                            
                            return True
                        else:
                            self.log(f"⏳ Ngrok démarrage... ({attempt + 1}/{max_attempts})", "DEBUG")
                            time.sleep(2)
                    else:
                        self.log(f"⏳ API ngrok status: {response.status_code}", "DEBUG")
                        time.sleep(2)
                except requests.exceptions.RequestException:
                    self.log(f"⏳ Connexion API ngrok... ({attempt + 1}/{max_attempts})", "DEBUG")
                    time.sleep(2)
            
            self.log("❌ Impossible d'obtenir l'URL ngrok après 20 tentatives", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"❌ Erreur ngrok: {e}", "ERROR")
            return False

    def test_webhook_endpoints(self):
        """Teste les endpoints webhook localement et via ngrok"""
        self.log("🔍 Tests des endpoints webhook...", "INFO")
        local_success = False
        ngrok_success = False
        
        # Test local GET (validation Facebook)
        self.log("📍 Test local GET (validation Facebook):", "DEBUG")
        try:
            params = {
                "hub.mode": "subscribe",
                "hub.verify_token": self.FACEBOOK_VERIFY_TOKEN,
                "hub.challenge": "test_challenge_local_123"
            }
            response = requests.get(f"http://{self.BACKEND_HOST}:{self.BACKEND_PORT}/api/webhook", 
                                  params=params, timeout=10)
            
            if response.status_code == 200:
                # Facebook attend que le challenge soit retourné tel quel
                expected_challenge = "test_challenge_local_123"
                received_challenge = response.text.strip('"')  # Enlever les guillemets JSON
                
                if received_challenge == expected_challenge:
                    self.log("✅ Test GET local: SUCCÈS", "SUCCESS")
                    local_success = True
                else:
                    self.log(f"❌ Test GET local: Challenge incorrect (reçu: {received_challenge})", "ERROR")
            else:
                self.log(f"❌ Test GET local: HTTP {response.status_code} - {response.text}", "ERROR")
        except Exception as e:
            self.log(f"❌ Erreur test GET local: {e}", "ERROR")
        
        # Test local POST (message webhook)
        self.log("📍 Test local POST (message webhook):", "DEBUG")
        try:
            payload = {
                "object": "page",
                "entry": [{
                    "messaging": [{
                        "sender": {"id": "test_user_local"},
                        "message": {"text": "Test message automatisation local"}
                    }]
                }]
            }
            response = requests.post(f"http://{self.BACKEND_HOST}:{self.BACKEND_PORT}/api/webhook", 
                                   json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "received":
                    self.log("✅ Test POST local: SUCCÈS", "SUCCESS")
                    local_success = local_success and True
                else:
                    self.log(f"❌ Test POST local: Statut incorrect ({result})", "ERROR")
                    local_success = False
            else:
                self.log(f"❌ Test POST local: HTTP {response.status_code}", "ERROR")
                local_success = False
        except Exception as e:
            self.log(f"❌ Erreur test POST local: {e}", "ERROR")
            local_success = False
        
        # Tests ngrok si URL disponible
        if self.NGROK_URL:
            self.log(f"🌐 Tests via ngrok: {self.NGROK_URL}", "NETWORK")
            
            # Test ngrok GET
            try:
                params = {
                    "hub.mode": "subscribe",
                    "hub.verify_token": self.FACEBOOK_VERIFY_TOKEN,
                    "hub.challenge": "test_challenge_ngrok_456"
                }
                response = requests.get(f"{self.NGROK_URL}/api/webhook", 
                                      params=params, timeout=15)
                
                if response.status_code == 200:
                    expected_challenge = "test_challenge_ngrok_456"
                    received_challenge = response.text.strip('"')
                    
                    if received_challenge == expected_challenge:
                        self.log("✅ Test GET ngrok: SUCCÈS", "SUCCESS")
                        ngrok_success = True
                    else:
                        self.log(f"❌ Test GET ngrok: Challenge incorrect", "ERROR")
                else:
                    self.log(f"❌ Test GET ngrok: HTTP {response.status_code}", "ERROR")
            except Exception as e:
                self.log(f"❌ Erreur test GET ngrok: {e}", "ERROR")
            
            # Test ngrok POST
            try:
                payload = {
                    "object": "page",
                    "entry": [{
                        "messaging": [{
                            "sender": {"id": "test_user_ngrok"},
                            "message": {"text": "Test message via ngrok automatisation"}
                        }]
                    }]
                }
                response = requests.post(f"{self.NGROK_URL}/api/webhook", 
                                       json=payload, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "received":
                        self.log("✅ Test POST ngrok: SUCCÈS", "SUCCESS")
                        ngrok_success = ngrok_success and True
                    else:
                        self.log(f"❌ Test POST ngrok: Statut incorrect", "ERROR")
                        ngrok_success = False
                else:
                    self.log(f"❌ Test POST ngrok: HTTP {response.status_code}", "ERROR")
                    ngrok_success = False
            except Exception as e:
                self.log(f"❌ Erreur test POST ngrok: {e}", "ERROR")
                ngrok_success = False
        
        # Résultat final
        self.tests_passed = local_success and (ngrok_success if self.NGROK_URL else True)
        
        if self.tests_passed:
            self.log("🎉 Tous les tests webhook ont réussi!", "SUCCESS")
            return True
        else:
            self.log("❌ Certains tests webhook ont échoué", "ERROR")
            return False

    def configure_facebook_webhook(self):
        """Configure automatiquement le webhook Facebook"""
        if not self.NGROK_URL:
            self.log("❌ URL ngrok requise pour configurer Facebook", "ERROR")
            return False
        
        if not self.tests_passed:
            self.log("❌ Les tests doivent passer avant de configurer Facebook", "ERROR")
            return False
        
        self.log("📝 Configuration du webhook Facebook...", "NETWORK")
        self.log(f"🔗 URL webhook: {self.NGROK_URL}/api/webhook", "INFO")
        
        # Demander confirmation utilisateur
        result = messagebox.askyesno(
            "Configuration Facebook",
            f"Configurer automatiquement le webhook Facebook ?\n\n"
            f"URL: {self.NGROK_URL}/api/webhook\n"
            f"Token: {self.FACEBOOK_VERIFY_TOKEN}\n\n"
            f"Assurez-vous que vos clés Facebook sont correctes dans le script."
        )
        
        if not result:
            self.log("⏸️ Configuration Facebook annulée par l'utilisateur", "WARNING")
            return False
        
        # Configuration via API Graph Facebook
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
                    self.log("✅ Webhook Facebook configuré avec succès!", "SUCCESS")
                    messagebox.showinfo("Succès", "Webhook Facebook configuré avec succès!")
                    return True
                else:
                    self.log(f"❌ Échec configuration Facebook: {result}", "ERROR")
                    messagebox.showerror("Erreur", f"Échec configuration: {result}")
                    return False
            else:
                error_msg = f"Erreur API Facebook: {response.status_code} - {response.text}"
                self.log(f"❌ {error_msg}", "ERROR")
                messagebox.showerror("Erreur API Facebook", error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Erreur configuration Facebook: {e}"
            self.log(f"❌ {error_msg}", "ERROR")
            messagebox.showerror("Erreur", error_msg)
            return False

    def show_commands(self):
        """Affiche les commandes curl utiles dans une fenêtre popup"""
        commands_window = tk.Toplevel(self.root)
        commands_window.title("Commandes curl pour tests")
        commands_window.geometry("700x500")
        
        commands_text = scrolledtext.ScrolledText(commands_window, font=('Consolas', 9))
        commands_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        commands_content = f"""📋 COMMANDES CURL POUR TESTS MANUELS

🏠 TESTS LOCAUX:
# Test GET (validation Facebook):
curl "http://localhost:{self.BACKEND_PORT}/api/webhook?hub.mode=subscribe&hub.verify_token={self.FACEBOOK_VERIFY_TOKEN}&hub.challenge=12345"

# Test POST (message webhook):
curl -X POST "http://localhost:{self.BACKEND_PORT}/api/webhook" ^
  -H "Content-Type: application/json" ^
  -d "{{""object"":""page"",""entry"":[{{""messaging"":[{{""sender"":{{""id"":""test""}},""message"":{{""text"":""Hello local""}}}}]}}]}}"

# Test santé backend:
curl "http://localhost:{self.BACKEND_PORT}/api/health"
"""
        
        if self.NGROK_URL:
            commands_content += f"""
🌐 TESTS NGROK:
# Test GET via ngrok:
curl "{self.NGROK_URL}/api/webhook?hub.mode=subscribe&hub.verify_token={self.FACEBOOK_VERIFY_TOKEN}&hub.challenge=12345"

# Test POST via ngrok:
curl -X POST "{self.NGROK_URL}/api/webhook" ^
  -H "Content-Type: application/json" ^
  -d "{{""object"":""page"",""entry"":[{{""messaging"":[{{""sender"":{{""id"":""test""}},""message"":{{""text"":""Hello ngrok""}}}}]}}]}}"

📝 CONFIGURATION FACEBOOK:
# Commande pour configurer le webhook Facebook:
curl -X POST "https://graph.facebook.com/v18.0/{self.FACEBOOK_PAGE_ID}/subscriptions" ^
  -d "callback_url={self.NGROK_URL}/api/webhook" ^
  -d "verify_token={self.FACEBOOK_VERIFY_TOKEN}" ^
  -d "fields=messages,messaging_postbacks,messaging_optins" ^
  -d "access_token={self.FACEBOOK_ACCESS_TOKEN}"
"""
        
        commands_text.insert(tk.END, commands_content)
        commands_text.config(state=tk.DISABLED)

    def start_automation(self):
        """Lance l'automatisation complète en arrière-plan"""
        if self.is_running:
            self.log("⚠️ Automatisation déjà en cours", "WARNING")
            return
        
        # Lancer dans un thread séparé pour ne pas bloquer l'interface
        thread = threading.Thread(target=self._run_automation, daemon=True)
        thread.start()

    def _run_automation(self):
        """Processus d'automatisation complet"""
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        
        try:
            self.update_status("Démarrage automatisation...", "#FF9800")
            self.log("🎯 AUTOMATISATION COMPLÈTE - DÉMARRAGE", "INFO")
            
            # 1. Détecter backend
            self.update_status("Détection backend...", "#2196F3")
            self.detect_backend_port()
            
            # 2. Vérifier santé backend
            self.update_status("Vérification backend...", "#2196F3")
            if not self.check_backend_health():
                self.update_status("Backend inaccessible", "#f44336")
                messagebox.showerror("Erreur", "Backend inaccessible sur le port 8001.\n\nVérifiez que server.py est lancé.")
                return
            
            # 3. Lancer ngrok
            self.update_status("Lancement ngrok...", "#FF9800")
            if not self.start_ngrok():
                self.update_status("Erreur ngrok", "#f44336")
                messagebox.showerror("Erreur", "Impossible de lancer ngrok.\n\nVérifiez que ngrok est installé et accessible.")
                return
            
            # 4. Tester endpoints
            self.update_status("Tests webhook...", "#9C27B0")
            if not self.test_webhook_endpoints():
                self.update_status("Tests échoués", "#f44336")
                messagebox.showwarning("Tests échoués", "Certains tests webhook ont échoué.\n\nVérifiez les logs pour plus de détails.")
                return
            
            # 5. Configuration Facebook (optionnelle)
            self.update_status("Prêt pour Facebook", "#4CAF50")
            configure_fb = messagebox.askyesno(
                "Configuration Facebook",
                "Tests réussis! Configurer automatiquement le webhook Facebook maintenant?"
            )
            
            if configure_fb:
                self.update_status("Configuration Facebook...", "#FF9800")
                if self.configure_facebook_webhook():
                    self.update_status("✅ Configuré avec succès", "#4CAF50")
                else:
                    self.update_status("⚠️ Configuration manuelle requise", "#FF9800")
            else:
                self.update_status("✅ Prêt - Config manuelle", "#4CAF50")
            
            self.log("🎉 AUTOMATISATION TERMINÉE AVEC SUCCÈS!", "SUCCESS")
            self.log(f"🔗 URL webhook: {self.NGROK_URL}/api/webhook", "INFO")
            self.log(f"🔑 Token vérification: {self.FACEBOOK_VERIFY_TOKEN}", "INFO")
            
        except Exception as e:
            self.log(f"❌ Erreur automatisation: {e}", "ERROR")
            self.update_status("Erreur inattendue", "#f44336")
            messagebox.showerror("Erreur", f"Erreur inattendue: {e}")
        
        finally:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)

    def test_only(self):
        """Lance uniquement les tests webhook"""
        thread = threading.Thread(target=self._test_only, daemon=True)
        thread.start()

    def _test_only(self):
        """Tests webhook uniquement"""
        self.update_status("Tests en cours...", "#2196F3")
        
        # Vérifier backend
        if not self.check_backend_health():
            messagebox.showerror("Erreur", "Backend inaccessible. Lancez server.py d'abord.")
            self.update_status("Backend inaccessible", "#f44336")
            return
        
        # Tester endpoints
        if self.test_webhook_endpoints():
            self.update_status("Tests réussis", "#4CAF50")
            messagebox.showinfo("Succès", "Tous les tests webhook ont réussi!")
        else:
            self.update_status("Tests échoués", "#f44336")
            messagebox.showwarning("Tests échoués", "Certains tests ont échoué. Voir les logs.")

    def stop_automation(self):
        """Arrête les processus lancés"""
        self.log("🛑 Arrêt des processus...", "WARNING")
        
        # Arrêter ngrok
        if self.ngrok_process:
            self.ngrok_process.terminate()
            subprocess.run(["taskkill", "/f", "/im", "ngrok.exe"], 
                         capture_output=True, shell=True, check=False)
            self.log("🛑 Ngrok arrêté", "INFO")
        
        self.update_status("Arrêté", "#666")
        self.update_ngrok_url(None)
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)

    def on_closing(self):
        """Nettoyage avant fermeture"""
        if messagebox.askokcancel("Quitter", "Voulez-vous quitter l'application?"):
            self.stop_automation()
            self.root.destroy()

    def run(self):
        """Lance l'interface graphique"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.log("🎮 Interface graphique prête", "SUCCESS")
        self.root.mainloop()

def main():
    """Point d'entrée principal"""
    # Vérifier Windows
    if os.name != 'nt':
        print("❌ Ce script est conçu pour Windows")
        sys.exit(1)
    
    # Vérifier Python 3.11+
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ requis")
        sys.exit(1)
    
    # Vérifier répertoire projet
    project_path = Path("C:/FacebookPost")
    if not project_path.exists():
        print(f"❌ Projet non trouvé: {project_path}")
        print("Placez ce script dans C:/FacebookPost/")
        input("Appuyez sur Entrée pour fermer...")
        sys.exit(1)
    
    try:
        app = FacebookWebhookGUI()
        app.run()
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        input("Appuyez sur Entrée pour fermer...")

if __name__ == "__main__":
    main()