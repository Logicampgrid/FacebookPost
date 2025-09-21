#!/usr/bin/env python3
"""
Script principal de lancement de l'application FacebookPost
Alternative Python au fichier .bat pour la gestion automatique de ngrok
"""

import subprocess
import time
import os
import sys
import requests
import signal
from pathlib import Path

class FacebookPostLauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.processes = []
        
    def log(self, level, message):
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "START": "🚀"}
        icon = icons.get(level, "📋")
        print(f"{icon} [LAUNCHER] {message}")
    
    def cleanup_processes(self):
        """Nettoie les processus existants"""
        try:
            self.log("INFO", "Nettoyage des processus existants...")
            
            # Tuer les processus Python server.py
            subprocess.run(["pkill", "-f", "server.py"], capture_output=True)
            
            # Tuer les processus npm start
            subprocess.run(["pkill", "-f", "npm start"], capture_output=True)
            
            # Tuer ngrok
            subprocess.run(["pkill", "-f", "ngrok"], capture_output=True)
            
            time.sleep(2)
            self.log("SUCCESS", "Processus nettoyés")
            
        except Exception as e:
            self.log("WARNING", f"Erreur nettoyage: {e}")
    
    def test_backend_health(self):
        """Teste si le backend est accessible"""
        try:
            response = requests.get("http://localhost:8001/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_backend(self):
        """Démarre le backend FastAPI"""
        try:
            self.log("START", "Démarrage du backend FastAPI...")
            
            os.chdir(self.backend_dir)
            process = subprocess.Popen(
                [sys.executable, "server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(('backend', process))
            
            # Attendre que le backend soit prêt
            for attempt in range(30):  # 30 secondes max
                if self.test_backend_health():
                    self.log("SUCCESS", "Backend FastAPI démarré avec succès")
                    return True
                time.sleep(1)
                
            self.log("ERROR", "Timeout démarrage backend")
            return False
            
        except Exception as e:
            self.log("ERROR", f"Erreur démarrage backend: {e}")
            return False
        finally:
            os.chdir(self.project_root)
    
    def start_frontend(self):
        """Démarre le frontend React"""
        try:
            self.log("START", "Démarrage du frontend React...")
            
            os.chdir(self.frontend_dir)
            
            # Définir les variables d'environnement
            env = os.environ.copy()
            env['PORT'] = '3000'
            env['BROWSER'] = 'none'  # Ne pas ouvrir automatiquement le navigateur
            
            process = subprocess.Popen(
                ["npm", "start"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            self.processes.append(('frontend', process))
            
            self.log("SUCCESS", "Frontend React démarré (port 3000)")
            return True
            
        except Exception as e:
            self.log("ERROR", f"Erreur démarrage frontend: {e}")
            return False
        finally:
            os.chdir(self.project_root)
    
    def setup_ngrok_if_available(self):
        """Configure ngrok s'il est disponible"""
        try:
            # Vérifier si ngrok est installé
            result = subprocess.run(["ngrok", "version"], capture_output=True, text=True)
            if result.returncode != 0:
                self.log("WARNING", "Ngrok non installé - mode local uniquement")
                return False
            
            self.log("INFO", f"Ngrok détecté: {result.stdout.strip()}")
            
            # Démarrer ngrok
            self.log("START", "Démarrage du tunnel ngrok...")
            process = subprocess.Popen(
                ["ngrok", "http", "8001", "--log=stdout"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(('ngrok', process))
            
            # Attendre l'initialisation
            time.sleep(10)
            
            # Récupérer l'URL
            try:
                response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
                if response.status_code == 200:
                    tunnels = response.json().get('tunnels', [])
                    if tunnels:
                        ngrok_url = tunnels[0].get('public_url')
                        if ngrok_url:
                            self.log("SUCCESS", f"Tunnel ngrok créé: {ngrok_url}")
                            
                            # Utiliser le correcteur de configuration
                            subprocess.run([sys.executable, str(self.project_root / "ngrok_config_fixer.py")])
                            
                            return ngrok_url
            except:
                pass
                
            self.log("WARNING", "Impossible de récupérer l'URL ngrok")
            return False
            
        except Exception as e:
            self.log("WARNING", f"Erreur ngrok: {e}")
            return False
    
    def show_status(self, ngrok_url=None):
        """Affiche le statut de l'application"""
        self.log("SUCCESS", "🎉 Application FacebookPost démarrée!")
        print("\n" + "="*50)
        print("📋 STATUT DE L'APPLICATION")
        print("="*50)
        
        if ngrok_url:
            print(f"🌐 Mode: TUNNEL NGROK")
            print(f"🔗 URL Publique: {ngrok_url}")
            print(f"📱 Interface Ngrok: http://127.0.0.1:4040")
            print(f"🎯 Accès Application: {ngrok_url}")
        else:
            print(f"🏠 Mode: LOCAL")
            print(f"🔗 Backend API: http://localhost:8001")
            print(f"⚛️ Frontend React: http://localhost:3000")
            print(f"🎯 Accès Application: http://localhost:3000")
        
        print(f"✅ Backend Health: http://localhost:8001/api/health")
        print("="*50)
        
        if ngrok_url:
            print("💡 L'application est accessible depuis Internet")
            print("🔄 L'URL ngrok change à chaque redémarrage")
        else:
            print("💡 Pour un accès Internet, installez ngrok:")
            print("   https://ngrok.com/download")
        
        print("\n🛑 Appuyez sur Ctrl+C pour arrêter l'application")
    
    def handle_shutdown(self, signum, frame):
        """Gère l'arrêt propre de l'application"""
        self.log("INFO", "Arrêt de l'application demandé...")
        
        for name, process in self.processes:
            try:
                self.log("INFO", f"Arrêt du processus {name}...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                self.log("WARNING", f"Erreur arrêt {name}: {e}")
        
        self.log("SUCCESS", "Application arrêtée proprement")
        sys.exit(0)
    
    def run(self):
        """Lance l'application complète"""
        # Configurer la gestion des signaux
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        
        self.log("START", "🚀 Lancement de l'application FacebookPost")
        
        # 1. Nettoyage
        self.cleanup_processes()
        
        # 2. Démarrage backend
        if not self.start_backend():
            self.log("ERROR", "Impossible de démarrer le backend")
            return False
        
        # 3. Configuration ngrok (optionnel)
        ngrok_url = self.setup_ngrok_if_available()
        
        # 4. Démarrage frontend
        if not self.start_frontend():
            self.log("ERROR", "Impossible de démarrer le frontend")
            return False
        
        # 5. Attendre que le frontend soit prêt
        time.sleep(15)
        
        # 6. Afficher le statut
        self.show_status(ngrok_url)
        
        # 7. Maintenir l'application en vie
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.handle_shutdown(None, None)
        
        return True

def main():
    """Point d'entrée principal"""
    launcher = FacebookPostLauncher()
    return launcher.run()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)