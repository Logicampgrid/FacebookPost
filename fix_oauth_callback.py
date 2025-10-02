#!/usr/bin/env python3
"""
PATCH 18 - Script de configuration OAuth Facebook avec ngrok
Résout le problème d'URL de callback Facebook rejetée comme malveillante
"""

import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path

def log_patch18(message, level="INFO"):
    """Logging pour PATCH 18"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "START": "🚀"}
    icon = icons.get(level.upper(), "🔧")
    print(f"{icon} [PATCH 18] {message}")

def kill_existing_ngrok():
    """Arrête tous les processus ngrok existants"""
    try:
        log_patch18("Arrêt des processus ngrok existants...")
        if os.name == 'nt':  # Windows
            subprocess.run(["taskkill", "/f", "/im", "ngrok.exe"], capture_output=True)
        else:  # Unix/Linux
            subprocess.run(["pkill", "-f", "ngrok"], capture_output=True)
        log_patch18("Processus ngrok arrêtés", "SUCCESS")
        time.sleep(2)
    except Exception as e:
        log_patch18(f"Erreur arrêt ngrok: {e}", "WARNING")

def start_ngrok(port=8001):
    """Démarre ngrok sur le port spécifié"""
    try:
        log_patch18(f"Démarrage ngrok sur le port {port}...")
        
        # Démarrer ngrok en arrière-plan
        process = subprocess.Popen(
            ["ngrok", "http", str(port), "--log=stdout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        log_patch18(f"Ngrok démarré (PID: {process.pid})", "SUCCESS")
        log_patch18("Attente de l'initialisation du tunnel...", "INFO")
        time.sleep(5)  # Attendre que ngrok s'initialise
        
        return process
        
    except FileNotFoundError:
        log_patch18("❌ Ngrok non trouvé! Installez ngrok: https://ngrok.com/download", "ERROR")
        return None
    except Exception as e:
        log_patch18(f"Erreur démarrage ngrok: {e}", "ERROR")
        return None

def get_ngrok_url(max_attempts=10):
    """Récupère l'URL ngrok active"""
    for attempt in range(max_attempts):
        try:
            log_patch18(f"Tentative {attempt + 1}/{max_attempts}: Récupération URL ngrok...")
            
            response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get('tunnels', [])
                
                if tunnels:
                    # Rechercher un tunnel HTTP/HTTPS
                    for tunnel in tunnels:
                        public_url = tunnel.get('public_url')
                        if public_url and (public_url.startswith('https://') or public_url.startswith('http://')):
                            log_patch18(f"URL ngrok trouvée: {public_url}", "SUCCESS")
                            return public_url
                    
                    # Prendre le premier tunnel si pas de HTTPS trouvé
                    public_url = tunnels[0].get('public_url')
                    if public_url:
                        log_patch18(f"URL ngrok trouvée (premier tunnel): {public_url}", "SUCCESS")
                        return public_url
            
            log_patch18("API ngrok non disponible, nouvelle tentative dans 3s...", "WARNING")
            time.sleep(3)
            
        except Exception as e:
            log_patch18(f"Erreur récupération URL (tentative {attempt + 1}): {e}", "WARNING")
            time.sleep(3)

    log_patch18("Impossible de récupérer l'URL ngrok", "ERROR")
    return None

def update_env_files(ngrok_url):
    """Met à jour les fichiers .env avec l'URL ngrok"""
    try:
        # Mettre à jour frontend/.env
        frontend_env = Path("/app/frontend/.env")
        if frontend_env.exists():
            with open(frontend_env, "r", encoding='utf-8') as f:
                lines = f.readlines()
            
            updated_lines = []
            backend_url_updated = False
            
            for line in lines:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}\n")
                    backend_url_updated = True
                else:
                    updated_lines.append(line)
            
            if not backend_url_updated:
                updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}\n")
            
            with open(frontend_env, "w", encoding='utf-8') as f:
                f.writelines(updated_lines)
            
            log_patch18(f"Frontend .env mis à jour: {ngrok_url}", "SUCCESS")
        
        # Mettre à jour backend/.env
        backend_env = Path("/app/backend/.env")
        if backend_env.exists():
            with open(backend_env, "r", encoding='utf-8') as f:
                lines = f.readlines()
            
            updated_lines = []
            webhook_url_updated = False
            public_base_url_updated = False
            
            for line in lines:
                if line.startswith("WEBHOOK_URL="):
                    updated_lines.append(f"WEBHOOK_URL={ngrok_url}\n")
                    webhook_url_updated = True
                elif line.startswith("PUBLIC_BASE_URL="):
                    updated_lines.append(f"PUBLIC_BASE_URL={ngrok_url}\n") 
                    public_base_url_updated = True
                else:
                    updated_lines.append(line)
            
            if not webhook_url_updated:
                updated_lines.append(f"WEBHOOK_URL={ngrok_url}\n")
            if not public_base_url_updated:
                updated_lines.append(f"PUBLIC_BASE_URL={ngrok_url}\n")
                
            with open(backend_env, "w", encoding='utf-8') as f:
                f.writelines(updated_lines)
            
            log_patch18(f"Backend .env mis à jour: {ngrok_url}", "SUCCESS")
            
    except Exception as e:
        log_patch18(f"Erreur mise à jour .env: {e}", "ERROR")

def display_facebook_config(ngrok_url):
    """Affiche les instructions de configuration Facebook"""
    callback_urls = [
        f"{ngrok_url}/auth/callback",
        f"{ngrok_url}/auth/callb", 
        f"{ngrok_url}/"
    ]
    
    print("\n" + "="*80)
    log_patch18("CONFIGURATION FACEBOOK OAUTH REQUISE", "START")
    print("="*80)
    
    print(f"""
📋 INSTRUCTIONS POUR FACEBOOK DEVELOPER CONSOLE:

1. 🌐 Allez sur: https://developers.facebook.com/apps/
2. 🔧 Sélectionnez votre application Facebook
3. 📱 Produits → Connexion Facebook → Paramètres
4. 🔗 Section "URI de redirection OAuth valides" - AJOUTEZ ces URLs:

   ✅ {callback_urls[0]}
   ✅ {callback_urls[1]} 
   ✅ {callback_urls[2]}

5. 💾 Sauvegardez la configuration Facebook
6. 🚀 Relancez votre application backend

⚠️  IMPORTANT: 
- Remplacez toute URL contenant "social-poster-7.preview.emergentagent.com"
- Facebook rejette certaines URLs comme malveillantes 
- Ngrok fournit une URL sûre acceptée par Facebook

🎯 URL NGROK ACTIVE: {ngrok_url}
    """)
    
    print("="*80)

def main():
    log_patch18("Démarrage du correctif OAuth Facebook", "START")
    
    # Étape 1: Arrêter ngrok existant
    kill_existing_ngrok()
    
    # Étape 2: Démarrer ngrok
    ngrok_process = start_ngrok(port=8001)
    if not ngrok_process:
        log_patch18("Impossible de démarrer ngrok", "ERROR")
        return False
    
    # Étape 3: Récupérer l'URL ngrok
    ngrok_url = get_ngrok_url()
    if not ngrok_url:
        log_patch18("Impossible de récupérer l'URL ngrok", "ERROR")
        return False
    
    # Étape 4: Mettre à jour les .env
    update_env_files(ngrok_url)
    
    # Étape 5: Afficher les instructions Facebook
    display_facebook_config(ngrok_url)
    
    log_patch18("Configuration OAuth Facebook prête! ✨", "SUCCESS") 
    log_patch18("⚠️ N'oubliez pas de configurer Facebook Developer Console avec les URLs ci-dessus", "WARNING")
    log_patch18("Ngrok continue à fonctionner en arrière-plan...", "INFO")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            log_patch18("Script terminé avec succès", "SUCCESS")
        else:
            log_patch18("Script terminé avec des erreurs", "ERROR")
            sys.exit(1)
    except KeyboardInterrupt:
        log_patch18("Arrêt demandé par l'utilisateur", "INFO")
    except Exception as e:
        log_patch18(f"Erreur inattendue: {e}", "ERROR")
        sys.exit(1)