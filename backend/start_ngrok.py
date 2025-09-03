#!/usr/bin/env python3
"""
Script pour démarrer ngrok et mettre à jour automatiquement le frontend .env
"""
import subprocess
import time
import requests
import os
from pathlib import Path

def start_ngrok_standalone():
    """Démarre ngrok de manière autonome"""
    print("🚀 Démarrage de ngrok en mode autonome...")
    
    try:
        # Kill any existing ngrok processes
        try:
            subprocess.run(["pkill", "-f", "ngrok"], capture_output=True)
            time.sleep(1)
        except:
            pass
        
        # Start ngrok with subprocess in background
        print("🔗 Lancement du tunnel ngrok sur le port 8001...")
        ngrok_process = subprocess.Popen(
            ["ngrok", "http", "8001", "--log=stdout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give ngrok time to start
        time.sleep(4)
        
        # Get ngrok URL via API
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
                if response.status_code == 200:
                    tunnels = response.json()
                    if tunnels.get('tunnels') and len(tunnels['tunnels']) > 0:
                        public_url = tunnels['tunnels'][0]['public_url']
                        print(f"🌐 Tunnel ngrok actif: {public_url}")
                        
                        # Save URL to file for backend access
                        ngrok_url_file = "/app/backend/ngrok_url.txt"
                        with open(ngrok_url_file, "w") as f:
                            f.write(public_url)
                        print(f"💾 URL ngrok sauvegardée: {ngrok_url_file}")
                        
                        # Update frontend .env file
                        try:
                            frontend_env_path = "/app/frontend/.env"
                            if os.path.exists(frontend_env_path):
                                # Read current .env
                                with open(frontend_env_path, "r") as f:
                                    lines = f.readlines()
                                
                                # Update REACT_APP_BACKEND_URL
                                updated_lines = []
                                backend_url_updated = False
                                for line in lines:
                                    if line.startswith("REACT_APP_BACKEND_URL="):
                                        updated_lines.append(f"REACT_APP_BACKEND_URL={public_url}\n")
                                        backend_url_updated = True
                                    else:
                                        updated_lines.append(line)
                                
                                # If REACT_APP_BACKEND_URL doesn't exist, add it
                                if not backend_url_updated:
                                    updated_lines.append(f"REACT_APP_BACKEND_URL={public_url}\n")
                                
                                # Write back to file
                                with open(frontend_env_path, "w") as f:
                                    f.writelines(updated_lines)
                                print(f"✅ Frontend .env mis à jour avec l'URL ngrok: {public_url}")
                            
                        except Exception as e:
                            print(f"⚠️ Attention: Impossible de mettre à jour le frontend .env: {e}")
                        
                        return public_url, ngrok_process
                    else:
                        print(f"⏳ Tentative {attempt + 1}/{max_attempts}: Aucun tunnel trouvé, attente...")
                        time.sleep(2)
                else:
                    print(f"⏳ Tentative {attempt + 1}/{max_attempts}: API ngrok status {response.status_code}, attente...")
                    time.sleep(2)
            except requests.exceptions.RequestException as e:
                print(f"⏳ Tentative {attempt + 1}/{max_attempts}: Connexion API ngrok échouée: {e}")
                time.sleep(2)
        
        print("❌ Impossible d'obtenir l'URL ngrok après plusieurs tentatives")
        return None, ngrok_process
        
    except Exception as e:
        print(f"❌ Erreur lors du démarrage de ngrok: {e}")
        return None, None

if __name__ == "__main__":
    print("📋 Script de démarrage ngrok autonome")
    url, process = start_ngrok_standalone()
    
    if url:
        print(f"🎉 Ngrok configuré avec succès!")
        print(f"🔗 URL publique: {url}")
        print("ℹ️ Le tunnel ngrok reste actif en arrière-plan")
        print("ℹ️ Le frontend .env a été mis à jour automatiquement")
        
        # Keep the script running to maintain the tunnel
        try:
            print("⏸️ Appuyez sur Ctrl+C pour arrêter le tunnel ngrok")
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du tunnel ngrok...")
            process.terminate()
            subprocess.run(["pkill", "-f", "ngrok"], capture_output=True)
            print("✅ Tunnel ngrok arrêté")
    else:
        print("❌ Échec de la configuration ngrok")