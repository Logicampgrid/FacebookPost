#!/usr/bin/env python3
"""
Script de configuration ngrok pour l'application existante
Démarre ngrok et synchronise les variables d'environnement
"""

import os
import time
import subprocess
import requests
from datetime import datetime
from dotenv import load_dotenv

def log(message: str, level: str = "INFO"):
    """Logging unifié"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "START": "🚀"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [NGROK] {message}")

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
    """Démarrer ngrok pour pointer vers le backend existant"""
    try:
        # Vérifier si ngrok est déjà actif
        existing_url = get_active_ngrok_url()
        if existing_url:
            log(f"✅ Ngrok déjà actif: {existing_url}", "SUCCESS")
            return existing_url
        
        log("🚀 Démarrage ngrok vers port 8001...", "INFO")
        
        # Charger les variables d'environnement
        load_dotenv("/app/backend/.env")
        
        # Configurer le token d'authentification
        ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
        if ngrok_token:
            subprocess.run(["ngrok", "config", "add-authtoken", ngrok_token], 
                         capture_output=True, text=True)
            log("✅ Token ngrok configuré", "SUCCESS")
        
        # Démarrer ngrok en arrière-plan
        subprocess.Popen(
            ["ngrok", "http", "8001"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        # Attendre que ngrok démarre
        log("⏳ Attente du démarrage de ngrok...", "INFO")
        time.sleep(4)
        
        for attempt in range(12):
            ngrok_url = get_active_ngrok_url()
            if ngrok_url:
                log(f"✅ Ngrok démarré avec succès: {ngrok_url}", "SUCCESS")
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
        old_url = env_content.get("REACT_APP_BACKEND_URL", "N/A")
        env_content["REACT_APP_BACKEND_URL"] = ngrok_url
        
        # Réécrire le fichier
        with open(frontend_env_path, "w", encoding='utf-8') as f:
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")
        
        log(f"✅ Frontend .env mis à jour: {old_url} → {ngrok_url}", "SUCCESS")
        return True
        
    except Exception as e:
        log(f"❌ Erreur mise à jour .env: {e}", "ERROR")
        return False

def test_ngrok_connection(ngrok_url):
    """Tester la connexion ngrok"""
    try:
        log("🔍 Test de la connexion ngrok...", "INFO")
        
        # Tester l'API health
        response = requests.get(f"{ngrok_url}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log(f"✅ API accessible: {data.get('status', 'unknown')}", "SUCCESS")
        else:
            log(f"⚠️ API répond avec status: {response.status_code}", "WARNING")
        
        # Tester l'accès au frontend
        response = requests.get(ngrok_url, timeout=10)
        if response.status_code == 200:
            log("✅ Frontend accessible via ngrok", "SUCCESS")
        else:
            log(f"⚠️ Frontend répond avec status: {response.status_code}", "WARNING")
        
        return True
        
    except Exception as e:
        log(f"❌ Erreur test connexion: {e}", "ERROR")
        return False

def main():
    """Fonction principale"""
    log("🚀 Configuration ngrok pour Meta Publishing Platform", "START")
    
    # Vérifier que l'application locale fonctionne
    try:
        response = requests.get("http://localhost:8001/api/health", timeout=5)
        if response.status_code == 200:
            log("✅ Application locale accessible", "SUCCESS")
        else:
            log("⚠️ Application locale répond mais avec erreurs", "WARNING")
    except Exception as e:
        log(f"❌ Application locale non accessible: {e}", "ERROR")
        log("💡 Assurez-vous que le backend tourne sur le port 8001", "INFO")
        return False
    
    # Démarrer ngrok
    ngrok_url = start_ngrok()
    
    if not ngrok_url:
        log("❌ Impossible de démarrer ngrok", "ERROR")
        return False
    
    # Mettre à jour le frontend .env
    if update_frontend_env(ngrok_url):
        log("🔄 Redémarrage du frontend recommandé pour appliquer les changements", "INFO")
    
    # Tester la connexion
    test_ngrok_connection(ngrok_url)
    
    # Afficher le résumé
    log("", "INFO")
    log("📋 RÉSUMÉ DE LA CONFIGURATION:", "SUCCESS")
    log(f"   🌍 URL externe (ngrok): {ngrok_url}", "SUCCESS")
    log("   🌐 URL locale: http://localhost:8001", "INFO")
    log("   📱 Interface ngrok: http://127.0.0.1:4040", "INFO")
    log("", "INFO")
    log("✅ Configuration ngrok terminée avec succès!", "SUCCESS")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)