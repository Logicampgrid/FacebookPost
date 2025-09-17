#!/usr/bin/env python3
"""
Script de démarrage pour server.py avec gestion automatique des URLs ngrok
Compatible avec 99_start_all_ngrok.bat
"""
import os
import sys
import time
import requests
import subprocess
from pathlib import Path

def log_message(message, level="INFO"):
    """Logging simple avec timestamp"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    icon = icons.get(level, "📋")
    print(f"{icon} {message}")

def get_ngrok_url():
    """Récupère l'URL ngrok active"""
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            tunnels = response.json().get('tunnels', [])
            if tunnels:
                return tunnels[0].get('public_url')
    except:
        pass
    return None

def update_env_files(ngrok_url):
    """Met à jour les fichiers .env avec l'URL ngrok"""
    try:
        # Mettre à jour le frontend .env
        frontend_env = Path(__file__).parent / "frontend" / ".env"
        if frontend_env.exists():
            with open(frontend_env, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            updated_lines = []
            for line in lines:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}\n")
                else:
                    updated_lines.append(line)
            
            with open(frontend_env, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)
            
            log_message(f"Frontend .env mis à jour: {ngrok_url}", "SUCCESS")
        
        # Sauvegarder l'URL pour le backend
        backend_dir = Path(__file__).parent / "backend"
        ngrok_file = backend_dir / "ngrok_url.txt"
        with open(ngrok_file, 'w', encoding='utf-8') as f:
            f.write(ngrok_url)
        
        log_message(f"URL ngrok sauvegardée: {ngrok_url}", "SUCCESS")
        return True
        
    except Exception as e:
        log_message(f"Erreur mise à jour configurations: {e}", "ERROR")
        return False

def main():
    """Point d'entrée principal"""
    log_message("🚀 Démarrage de server_windows.py", "INFO")
    
    # Attendre que ngrok soit prêt si nécessaire
    log_message("🔍 Recherche de l'URL ngrok...", "INFO")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        ngrok_url = get_ngrok_url()
        if ngrok_url:
            log_message(f"✅ URL ngrok trouvée: {ngrok_url}", "SUCCESS")
            
            # Mettre à jour les configurations
            if update_env_files(ngrok_url):
                log_message("🎯 Configurations OAuth mises à jour", "SUCCESS")
            
            break
        
        if attempt < max_attempts - 1:
            log_message(f"⏳ Tentative {attempt + 1}/{max_attempts}: Ngrok non encore prêt...", "INFO")
            time.sleep(2)
    else:
        log_message("⚠️ Ngrok non détecté, démarrage en mode local", "WARNING")
    
    # Configurer les variables d'environnement
    os.environ["ENABLE_NGROK"] = "true" if ngrok_url else "false"
    os.environ["LOCAL_DEV_MODE"] = "true"
    
    # Démarrer le serveur principal
    log_message("🌐 Démarrage du serveur principal...", "INFO")
    
    try:
        # Importer et démarrer le serveur FastAPI
        backend_dir = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_dir))
        
        os.chdir(backend_dir)
        
        # Démarrer le serveur avec uvicorn
        import uvicorn
        from server import app
        
        log_message("✅ Serveur prêt pour l'authentification OAuth Facebook!", "SUCCESS")
        
        if ngrok_url:
            log_message(f"🔗 Application accessible sur: {ngrok_url}", "SUCCESS")
            log_message("🔐 OAuth Facebook configuré automatiquement", "SUCCESS")
        else:
            log_message("🌐 Application accessible sur: http://localhost:8001", "INFO")
        
        # Lancer le serveur
        uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
        
    except KeyboardInterrupt:
        log_message("🛑 Arrêt du serveur demandé", "INFO")
    except Exception as e:
        log_message(f"❌ Erreur serveur: {e}", "ERROR")
        return 1
    
    log_message("✅ Serveur arrêté proprement", "SUCCESS")
    return 0

if __name__ == "__main__":
    sys.exit(main())