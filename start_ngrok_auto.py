#!/usr/bin/env python3
"""
Script pour démarrer ngrok automatiquement et mettre à jour les URLs
Résout le problème de page blanche en s'assurant que ngrok fonctionne correctement
"""

import subprocess
import time
import requests
import json
import os
import sys
from pathlib import Path

# Configuration
BACKEND_PORT = 8001
NGROK_TIMEOUT = 30
PROJECT_ROOT = Path(__file__).parent

def log(message, level="INFO"):
    """Logging avec timestamp"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%H:%M:%S")
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    icon = icons.get(level, "📋")
    print(f"{icon} [{timestamp}] {message}")

def kill_existing_ngrok():
    """Arrête tous les processus ngrok existants"""
    try:
        log("Arrêt des processus ngrok existants...")
        
        # Linux/Mac
        if os.name != 'nt':
            subprocess.run(["pkill", "-f", "ngrok"], check=False, capture_output=True)
        else:
            # Windows
            subprocess.run(["taskkill", "/f", "/im", "ngrok.exe"], 
                         check=False, capture_output=True)
        
        time.sleep(2)
        log("Processus ngrok existants arrêtés", "SUCCESS")
        
    except Exception as e:
        log(f"Erreur lors de l'arrêt de ngrok: {e}", "WARNING")

def start_ngrok():
    """Démarre ngrok sur le port backend"""
    try:
        log(f"Démarrage de ngrok sur le port {BACKEND_PORT}...")
        
        # Démarrer ngrok en arrière-plan
        process = subprocess.Popen(
            ["ngrok", "http", str(BACKEND_PORT)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        log(f"Ngrok démarré (PID: {process.pid})", "SUCCESS")
        return process
        
    except Exception as e:
        log(f"Erreur démarrage ngrok: {e}", "ERROR")
        return None

def get_ngrok_url(max_attempts=10):
    """Récupère l'URL ngrok active"""
    for attempt in range(max_attempts):
        try:
            log(f"Tentative {attempt + 1}/{max_attempts}: Récupération URL ngrok...")
            
            response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get("tunnels", [])
                
                for tunnel in tunnels:
                    if tunnel.get("config", {}).get("addr") == f"http://localhost:{BACKEND_PORT}":
                        public_url = tunnel.get("public_url")
                        if public_url and public_url.startswith("https://"):
                            log(f"URL ngrok trouvée: {public_url}", "SUCCESS")
                            return public_url
                
                # Si pas de tunnel spécifique trouvé, prendre le premier HTTPS
                for tunnel in tunnels:
                    public_url = tunnel.get("public_url")
                    if public_url and public_url.startswith("https://"):
                        log(f"URL ngrok trouvée (premier tunnel): {public_url}", "SUCCESS")
                        return public_url
            
            log(f"Aucun tunnel actif trouvé, nouvelle tentative dans 3s...", "WARNING")
            time.sleep(3)
            
        except requests.exceptions.ConnectionError:
            log(f"API ngrok non disponible, nouvelle tentative dans 3s...", "WARNING")
            time.sleep(3)
            
        except Exception as e:
            log(f"Erreur récupération URL: {e}", "WARNING")
            time.sleep(3)
    
    log("Impossible de récupérer l'URL ngrok", "ERROR")
    return None

def update_env_files(ngrok_url):
    """Met à jour les fichiers .env avec l'URL ngrok"""
    try:
        # Mettre à jour frontend/.env
        frontend_env = PROJECT_ROOT / "frontend" / ".env"
        if frontend_env.exists():
            content = frontend_env.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            updated_lines = []
            backend_url_updated = False
            
            for line in lines:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}")
                    backend_url_updated = True
                else:
                    updated_lines.append(line)
            
            if not backend_url_updated:
                updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}")
            
            frontend_env.write_text('\n'.join(updated_lines) + '\n', encoding='utf-8')
            log(f"Frontend .env mis à jour: {ngrok_url}", "SUCCESS")
        
        # Mettre à jour .env principal
        main_env = PROJECT_ROOT / ".env"
        if main_env.exists():
            content = main_env.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            updated_lines = []
            webhook_url_updated = False
            
            for line in lines:
                if line.startswith("WEBHOOK_URL="):
                    updated_lines.append(f"WEBHOOK_URL={ngrok_url}")
                    webhook_url_updated = True
                else:
                    updated_lines.append(line)
            
            if not webhook_url_updated:
                updated_lines.append(f"WEBHOOK_URL={ngrok_url}")
            
            main_env.write_text('\n'.join(updated_lines) + '\n', encoding='utf-8')
            log(f"WEBHOOK_URL mis à jour: {ngrok_url}", "SUCCESS")
        
        # Sauvegarder l'URL dans le fichier ngrok_url.txt
        ngrok_file = PROJECT_ROOT / "backend" / "ngrok_url.txt"
        ngrok_file.write_text(ngrok_url, encoding='utf-8')
        log(f"URL sauvegardée dans {ngrok_file}", "SUCCESS")
        
        return True
        
    except Exception as e:
        log(f"Erreur mise à jour fichiers .env: {e}", "ERROR")
        return False

def test_ngrok_url(ngrok_url):
    """Teste si l'URL ngrok fonctionne correctement"""
    try:
        log(f"Test de l'URL ngrok: {ngrok_url}/api/health")
        
        response = requests.get(f"{ngrok_url}/api/health", timeout=10)
        if response.status_code == 200:
            log("URL ngrok fonctionne correctement ✅", "SUCCESS")
            return True
        else:
            log(f"URL ngrok retourne status {response.status_code}", "WARNING")
            return False
            
    except Exception as e:
        log(f"Erreur test URL ngrok: {e}", "WARNING")
        return False

def main():
    """Fonction principale"""
    log("🚀 Démarrage automatique de ngrok pour FacebookPost", "INFO")
    
    # Vérifier que ngrok est installé
    try:
        subprocess.run(["ngrok", "version"], check=True, capture_output=True)
        log("Ngrok détecté", "SUCCESS")
    except (subprocess.CalledProcessError, FileNotFoundError):
        log("Ngrok non installé ou non trouvé dans PATH", "ERROR")
        log("Installez ngrok depuis: https://ngrok.com/download", "INFO")
        return False
    
    # Arrêter ngrok existant
    kill_existing_ngrok()
    
    # Démarrer ngrok
    ngrok_process = start_ngrok()
    if not ngrok_process:
        return False
    
    # Attendre que ngrok soit prêt
    log("Attente de l'initialisation de ngrok...")
    time.sleep(10)
    
    # Récupérer l'URL ngrok
    ngrok_url = get_ngrok_url()
    if not ngrok_url:
        log("Impossible de récupérer l'URL ngrok", "ERROR")
        return False
    
    # Mettre à jour les fichiers de configuration
    if not update_env_files(ngrok_url):
        return False
    
    # Attendre un peu que le backend redémarre avec la nouvelle config
    log("Attente de la synchronisation backend...")
    time.sleep(5)
    
    # Tester l'URL
    test_ngrok_url(ngrok_url)
    
    log("🎉 Configuration ngrok terminée avec succès!", "SUCCESS")
    log(f"🌐 URL publique: {ngrok_url}", "SUCCESS")
    log(f"📱 Interface ngrok: http://127.0.0.1:4040", "INFO")
    log(f"🔍 Health check: {ngrok_url}/api/health", "INFO")
    log(f"📦 Webhook URL: {ngrok_url}/api/webhook", "INFO")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)