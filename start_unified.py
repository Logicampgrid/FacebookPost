#!/usr/bin/env python3
"""
Script de démarrage unifié pour Meta Publishing Platform
- Construit le frontend React
- Démarre ngrok pour l'accès externe  
- Lance FastAPI qui sert à la fois l'API et le frontend
"""

import os
import sys
import time
import subprocess
import requests
import signal
from datetime import datetime

def log(message: str, level: str = "INFO"):
    """Logging unifié"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "START": "🚀"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [STARTUP] {message}")

def check_dependencies():
    """Vérifier que toutes les dépendances sont installées"""
    log("🔍 Vérification des dépendances...", "INFO")
    
    dependencies = {
        "node": "Node.js requis pour construire le frontend",
        "yarn": "Yarn requis pour gérer les dépendances frontend", 
        "ngrok": "Ngrok requis pour l'accès externe",
        "python": "Python requis pour le backend"
    }
    
    missing = []
    for cmd, description in dependencies.items():
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=True)
            log(f"✅ {cmd} disponible", "SUCCESS")
        except (subprocess.CalledProcessError, FileNotFoundError):
            log(f"❌ {description}", "ERROR")
            missing.append(cmd)
    
    if missing:
        log(f"❌ Dépendances manquantes: {', '.join(missing)}", "ERROR")
        return False
    
    log("✅ Toutes les dépendances sont disponibles", "SUCCESS")
    return True

def build_frontend():
    """Construire le frontend React"""
    try:
        frontend_dir = "/app/frontend"
        
        log("🔨 Construction du frontend React...", "INFO")
        
        # Vérifier si node_modules existe
        node_modules_path = os.path.join(frontend_dir, "node_modules")
        if not os.path.exists(node_modules_path):
            log("📦 Installation des dépendances frontend...", "INFO")
            result = subprocess.run(["yarn", "install"], cwd=frontend_dir, capture_output=True, text=True)
            if result.returncode != 0:
                log(f"❌ Erreur installation dépendances: {result.stderr}", "ERROR")
                return False
            log("✅ Dépendances installées", "SUCCESS")
        
        # Construire le frontend
        log("🏗️ Construction en cours...", "INFO")
        result = subprocess.run(
            ["yarn", "build"], 
            cwd=frontend_dir, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            log("✅ Frontend construit avec succès", "SUCCESS")
            return True
        else:
            log(f"❌ Erreur construction frontend: {result.stderr}", "ERROR")
            return False
            
    except Exception as e:
        log(f"❌ Erreur construction frontend: {e}", "ERROR")
        return False

def start_ngrok(port=8001):
    """Démarrer ngrok sur le port spécifié"""
    try:
        log(f"🚀 Démarrage ngrok sur port {port}...", "INFO")
        
        # Vérifier si ngrok est déjà actif
        try:
            response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=3)
            if response.status_code == 200:
                tunnels = response.json().get('tunnels', [])
                if tunnels:
                    for tunnel in tunnels:
                        if tunnel.get('config', {}).get('addr') == f"http://localhost:{port}":
                            public_url = tunnel.get('public_url')
                            log(f"✅ Ngrok déjà actif: {public_url}", "SUCCESS")
                            return public_url
        except:
            pass
        
        # Configurer le token d'authentification si disponible
        from dotenv import load_dotenv
        load_dotenv("/app/backend/.env")
        
        ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
        if ngrok_token:
            subprocess.run(["ngrok", "config", "add-authtoken", ngrok_token], 
                         capture_output=True, text=True)
            log("✅ Token ngrok configuré", "SUCCESS")
        
        # Démarrer ngrok en arrière-plan
        ngrok_process = subprocess.Popen(
            ["ngrok", "http", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Attendre que ngrok démarre et récupérer l'URL
        log("⏳ Attente du démarrage de ngrok...", "INFO")
        time.sleep(4)
        
        for attempt in range(12):  # 12 tentatives sur 6 secondes
            try:
                response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
                if response.status_code == 200:
                    tunnels = response.json().get('tunnels', [])
                    for tunnel in tunnels:
                        if tunnel.get('config', {}).get('addr') == f"http://localhost:{port}":
                            public_url = tunnel.get('public_url')
                            if public_url:
                                log(f"✅ Ngrok démarré: {public_url}", "SUCCESS")
                                return public_url, ngrok_process
                    
                    # Si pas de tunnel spécifique, prendre le premier
                    if tunnels:
                        public_url = tunnels[0].get('public_url')
                        if public_url:
                            log(f"✅ Ngrok démarré (premier tunnel): {public_url}", "SUCCESS")
                            return public_url, ngrok_process
            except:
                pass
            
            time.sleep(0.5)
        
        log("❌ Impossible de récupérer l'URL ngrok", "ERROR")
        return None, ngrok_process
        
    except FileNotFoundError:
        log("❌ Ngrok non trouvé - installez ngrok pour l'accès externe", "ERROR")
        return None, None
    except Exception as e:
        log(f"❌ Erreur démarrage ngrok: {e}", "ERROR")
        return None, None

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
        
        # Ajouter d'autres configurations nécessaires
        env_content["DANGEROUSLY_DISABLE_HOST_CHECK"] = "true"
        env_content["ESLINT_NO_DEV_ERRORS"] = "true"
        env_content["HOST"] = "0.0.0.0"
        env_content["PORT"] = "3000"
        env_content["BROWSER"] = "none"
        
        # Réécrire le fichier
        with open(frontend_env_path, "w", encoding='utf-8') as f:
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")
        
        log(f"✅ Frontend .env mis à jour avec: {ngrok_url}", "SUCCESS")
        return True
        
    except Exception as e:
        log(f"❌ Erreur mise à jour frontend .env: {e}", "ERROR")
        return False

def start_backend_server():
    """Démarrer le serveur backend unifié"""
    try:
        log("🚀 Démarrage du serveur backend unifié...", "INFO")
        
        # Changer vers le répertoire backend
        backend_dir = "/app/backend"
        os.chdir(backend_dir)
        
        # Démarrer le serveur avec uvicorn
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "server_unified:app", 
            "--host", "0.0.0.0", 
            "--port", "8001",
            "--reload"
        ])
        
        log("✅ Serveur backend démarré", "SUCCESS")
        return backend_process
        
    except Exception as e:
        log(f"❌ Erreur démarrage serveur: {e}", "ERROR")
        return None

def main():
    """Fonction principale"""
    log("🚀 Démarrage de Meta Publishing Platform - Configuration Unifiée", "START")
    
    # Vérifier les dépendances
    if not check_dependencies():
        log("❌ Dépendances manquantes - arrêt du démarrage", "ERROR")
        sys.exit(1)
    
    # Construire le frontend
    if not build_frontend():
        log("⚠️ Construction frontend échouée - API seulement", "WARNING")
    
    # Démarrer ngrok
    ngrok_result = start_ngrok(8001)
    if ngrok_result and ngrok_result[0]:
        ngrok_url, ngrok_process = ngrok_result
        
        # Mettre à jour le frontend .env
        update_frontend_env(ngrok_url)
        
        log(f"🌍 Application sera accessible via: {ngrok_url}", "SUCCESS")
    else:
        ngrok_process = None
        log("⚠️ Ngrok non démarré - mode local uniquement", "WARNING")
    
    # Démarrer le serveur backend
    backend_process = start_backend_server()
    
    if backend_process:
        log("✅ Tous les services démarrés avec succès!", "SUCCESS")
        log("", "INFO")
        log("📋 RÉSUMÉ DES SERVICES:", "INFO")
        if ngrok_result and ngrok_result[0]:
            log(f"   🌍 URL externe: {ngrok_result[0]}", "SUCCESS")
        log("   🌐 URL locale: http://localhost:8001", "INFO")
        log("   📱 Interface ngrok: http://127.0.0.1:4040", "INFO")
        log("", "INFO")
        log("   Pour arrêter: Ctrl+C", "INFO")
        
        # Gestionnaire de signal pour arrêt propre
        def signal_handler(sig, frame):
            log("🛑 Arrêt des services...", "INFO")
            
            if backend_process:
                backend_process.terminate()
                log("✅ Serveur backend arrêté", "SUCCESS")
            
            if ngrok_process:
                ngrok_process.terminate()
                log("✅ Ngrok arrêté", "SUCCESS")
            
            log("✅ Arrêt terminé!", "SUCCESS")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Attendre
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            signal_handler(None, None)
    else:
        log("❌ Échec du démarrage du serveur backend", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()