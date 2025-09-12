#!/usr/bin/env python3
"""
Script pour démarrer l'application en local avec ngrok
Compatible avec votre configuration existante
"""
import subprocess
import time
import requests
import os
import sys
from pathlib import Path

def check_ngrok():
    """Vérifier si ngrok est installé"""
    try:
        result = subprocess.run(["ngrok", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ngrok détecté")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Ngrok n'est pas installé ou pas dans le PATH")
    return False

def start_ngrok_tunnel():
    """Démarrer le tunnel ngrok en mode libre (sans authentification si possible)"""
    print("🚀 Démarrage du tunnel ngrok...")
    
    try:
        # Arrêter d'éventuels processus ngrok existants
        subprocess.run(["pkill", "-f", "ngrok"], capture_output=True)
        time.sleep(1)
        
        # Démarrer ngrok en arrière-plan
        ngrok_process = subprocess.Popen(
            ["ngrok", "http", "8001", "--log=stdout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("⏳ Attente de l'initialisation du tunnel ngrok...")
        time.sleep(5)
        
        # Obtenir l'URL ngrok via l'API
        max_attempts = 15
        for attempt in range(max_attempts):
            try:
                response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
                if response.status_code == 200:
                    tunnels = response.json()
                    if tunnels.get('tunnels') and len(tunnels['tunnels']) > 0:
                        public_url = tunnels['tunnels'][0]['public_url']
                        print(f"🌐 Tunnel ngrok actif: {public_url}")
                        
                        # Sauvegarder l'URL
                        with open("/app/backend/ngrok_url.txt", "w") as f:
                            f.write(public_url)
                        
                        return public_url, ngrok_process
                    else:
                        print(f"⏳ Tentative {attempt + 1}/{max_attempts}: Tunnel en cours de création...")
                        time.sleep(2)
                else:
                    print(f"⏳ Tentative {attempt + 1}/{max_attempts}: API ngrok status {response.status_code}")
                    time.sleep(2)
            except requests.exceptions.RequestException as e:
                print(f"⏳ Tentative {attempt + 1}/{max_attempts}: Attente connexion API ngrok...")
                time.sleep(2)
        
        print("❌ Impossible d'obtenir l'URL ngrok")
        return None, ngrok_process
        
    except Exception as e:
        print(f"❌ Erreur démarrage ngrok: {e}")
        return None, None

def update_frontend_env(ngrok_url):
    """Mettre à jour le fichier .env du frontend avec l'URL ngrok"""
    frontend_env_path = "/app/frontend/.env"
    
    try:
        if os.path.exists(frontend_env_path):
            # Lire le fichier actuel
            with open(frontend_env_path, "r") as f:
                lines = f.readlines()
            
            # Mettre à jour REACT_APP_BACKEND_URL
            updated_lines = []
            backend_url_updated = False
            
            for line in lines:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}\n")
                    backend_url_updated = True
                    print(f"✅ REACT_APP_BACKEND_URL mis à jour: {ngrok_url}")
                else:
                    updated_lines.append(line)
            
            # Si REACT_APP_BACKEND_URL n'existe pas, l'ajouter
            if not backend_url_updated:
                updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}\n")
                print(f"✅ REACT_APP_BACKEND_URL ajouté: {ngrok_url}")
            
            # Écrire le fichier mis à jour
            with open(frontend_env_path, "w") as f:
                f.writelines(updated_lines)
            
            print(f"🎯 Frontend .env synchronisé avec l'URL ngrok")
            return True
            
    except Exception as e:
        print(f"⚠️ Erreur mise à jour frontend .env: {e}")
        return False

def start_backend():
    """Démarrer le backend avec ngrok activé"""
    print("🔧 Démarrage du backend...")
    
    # Configurer les variables d'environnement
    env = os.environ.copy()
    env["ENABLE_NGROK"] = "true"
    env["LOCAL_DEV_MODE"] = "true"
    
    try:
        # Démarrer le backend
        backend_process = subprocess.Popen(
            [sys.executable, "/app/backend/server.py"],
            env=env,
            cwd="/app/backend"
        )
        
        print("✅ Backend démarré")
        return backend_process
        
    except Exception as e:
        print(f"❌ Erreur démarrage backend: {e}")
        return None

def main():
    print("=" * 50)
    print("  DÉMARRAGE TUNNEL INSTAGRAM GRATUIT")
    print("    Mode Ngrok - Accès Internet")
    print("=" * 50)
    print()
    
    # Vérifier ngrok
    if not check_ngrok():
        print("\n💡 Pour installer ngrok:")
        print("1. Allez sur https://ngrok.com/download")
        print("2. Téléchargez la version pour votre système")
        print("3. Ajoutez ngrok au PATH système")
        print("\nOu utilisez: sudo apt install snapd && sudo snap install ngrok")
        return False
    
    print()
    
    # Démarrer le tunnel ngrok
    ngrok_url, ngrok_process = start_ngrok_tunnel()
    
    if not ngrok_url:
        print("\n⚠️ Échec du tunnel ngrok, basculement en mode local")
        print("L'application sera accessible uniquement sur http://localhost:3000")
        
        # Configurer en mode local
        update_frontend_env("http://localhost:8001")
    else:
        # Mettre à jour le frontend avec l'URL ngrok
        update_frontend_env(ngrok_url)
        
        print(f"\n🎉 TUNNEL INSTAGRAM GRATUIT PRÊT !")
        print(f"🌐 URL publique: {ngrok_url}")
        print(f"📱 Accessible depuis n'importe où sur Internet")
    
    print(f"\n📋 Services actifs:")
    print(f"   - MongoDB: Port 27017 (local)")
    print(f"   - Backend: Port 8001 (local + {'ngrok' if ngrok_url else 'local seulement'})")
    print(f"   - Frontend: Port 3000 (local)")
    
    if ngrok_url:
        print(f"\n🔗 URL d'accès: {ngrok_url}")
        print(f"🔧 Interface admin ngrok: http://127.0.0.1:4040")
    else:
        print(f"\n🔗 URL d'accès: http://localhost:3000")
    
    print(f"\n⚠️ Important:")
    print(f"   - Gardez cette fenêtre ouverte")
    print(f"   - Les services redémarrent automatiquement")
    print(f"   - Utilisez 'Token Manuel' pour la connexion Facebook")
    
    try:
        print(f"\n🎊 Application prête ! Appuyez sur Ctrl+C pour arrêter")
        
        if ngrok_process:
            ngrok_process.wait()
        else:
            # Mode local sans ngrok
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print(f"\n🛑 Arrêt en cours...")
        
        if ngrok_process:
            ngrok_process.terminate()
            subprocess.run(["pkill", "-f", "ngrok"], capture_output=True)
            print("✅ Tunnel ngrok arrêté")
        
        print("✅ Application arrêtée")

if __name__ == "__main__":
    main()