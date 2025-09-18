#!/usr/bin/env python3
"""
Script de démarrage pour supervisor - Configuration Unifiée Meta Publishing Platform
Ce script démarre FastAPI qui serve à la fois l'API et le frontend via ngrok
"""

import os
import sys
import time
import subprocess
import requests
from datetime import datetime

def log(message: str, level: str = "INFO"):
    """Logging unifié"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "START": "🚀"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [SUPERVISOR] {message}")

def get_active_ngrok_url():
    """Récupère l'URL ngrok active via l'API locale"""
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=3)
        
        if response.status_code == 200:
            tunnels_data = response.json()
            tunnels = tunnels_data.get('tunnels', [])
            
            if tunnels:
                for tunnel in tunnels:
                    config = tunnel.get('config', {})
                    if config.get('addr') == "http://localhost:8001":
                        public_url = tunnel.get('public_url')
                        if public_url:
                            return public_url
                
                # Premier tunnel disponible
                first_tunnel = tunnels[0]
                public_url = first_tunnel.get('public_url')
                if public_url:
                    return public_url
            
        return None
            
    except:
        return None

def start_ngrok():
    """Démarrer ngrok si pas déjà actif"""
    try:
        # Vérifier si ngrok est déjà actif
        existing_url = get_active_ngrok_url()
        if existing_url:
            log(f"✅ Ngrok déjà actif: {existing_url}", "SUCCESS")
            return existing_url
        
        log("🚀 Démarrage ngrok...", "INFO")
        
        # Configurer le token d'authentification
        from dotenv import load_dotenv
        load_dotenv("/app/backend/.env")
        
        ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
        if ngrok_token:
            subprocess.run(["ngrok", "config", "add-authtoken", ngrok_token], 
                         capture_output=True, text=True)
        
        # Démarrer ngrok en arrière-plan
        subprocess.Popen(
            ["ngrok", "http", "8001"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        # Attendre que ngrok démarre
        time.sleep(4)
        
        for attempt in range(10):
            ngrok_url = get_active_ngrok_url()
            if ngrok_url:
                log(f"✅ Ngrok démarré: {ngrok_url}", "SUCCESS")
                return ngrok_url
            time.sleep(0.5)
        
        log("❌ Impossible de récupérer l'URL ngrok", "ERROR")
        return None
        
    except Exception as e:
        log(f"❌ Erreur démarrage ngrok: {e}", "ERROR")
        return None

def update_frontend_env(ngrok_url):
    """Mettre à jour le .env frontend avec l'URL ngrok"""
    try:
        frontend_env_path = "/app/frontend/.env"
        
        # Lire le fichier .env actuel
        env_content = {}
        if os.path.exists(frontend_env_path):
            with open(frontend_env_path, "r", encoding='utf-8') as f:
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        key, value = line.strip().split("=", 1)
                        env_content[key] = value
        
        # Mettre à jour l'URL backend
        env_content["REACT_APP_BACKEND_URL"] = ngrok_url
        
        # Réécrire le fichier
        with open(frontend_env_path, "w", encoding='utf-8') as f:
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")
        
        log(f"✅ Frontend .env mis à jour: {ngrok_url}", "SUCCESS")
        return True
        
    except Exception as e:
        log(f"❌ Erreur mise à jour .env: {e}", "ERROR")
        return False

def main():
    """Fonction principale pour supervisor"""
    log("🚀 Démarrage serveur unifié via supervisor", "START")
    
    # Démarrer ngrok
    ngrok_url = start_ngrok()
    
    if ngrok_url:
        # Mettre à jour le frontend .env
        update_frontend_env(ngrok_url)
        log(f"🌍 Application accessible via: {ngrok_url}", "SUCCESS")
    else:
        log("⚠️ Mode local uniquement", "WARNING")
    
    # Changer vers le répertoire backend
    os.chdir("/app/backend")
    
    # Démarrer le serveur unifié avec uvicorn
    log("🚀 Démarrage FastAPI unifié...", "INFO")
    
    os.execvp("python", [
        "python", "-m", "uvicorn", 
        "server_unified:app", 
        "--host", "0.0.0.0", 
        "--port", "8001",
        "--log-level", "info"
    ])

if __name__ == "__main__":
    main()