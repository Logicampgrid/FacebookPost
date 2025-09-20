#!/usr/bin/env python3
"""
Windows Helper pour FacebookPost Application
Utilitaires pour configuration et gestion Windows
"""

import os
import sys
import subprocess
import json
import time
import requests
from pathlib import Path

def log_info(message, level="INFO"):
    """Log avec timestamp"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    icon = icons.get(level.upper(), "📋")
    print(f"{icon} [{timestamp}] {message}")

def check_prerequisites():
    """Vérifier les prérequis Windows"""
    log_info("Vérification des prérequis Windows...")
    
    # Vérifier Python
    try:
        result = subprocess.run(["python", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            log_info(f"Python: {result.stdout.strip()}", "SUCCESS")
        else:
            log_info("Python non trouvé", "ERROR")
            return False
    except FileNotFoundError:
        log_info("Python non installé", "ERROR")
        return False
    
    # Vérifier Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            log_info(f"Node.js: {result.stdout.strip()}", "SUCCESS")
        else:
            log_info("Node.js non trouvé", "ERROR")
            return False
    except FileNotFoundError:
        log_info("Node.js non installé", "ERROR")
        return False
    
    # Vérifier ngrok (optionnel)
    try:
        result = subprocess.run(["ngrok", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            log_info(f"Ngrok: {result.stdout.strip()}", "SUCCESS")
            return True, True  # Prérequis OK, ngrok disponible
        else:
            log_info("Ngrok non trouvé (optionnel)", "WARNING")
            return True, False  # Prérequis OK, pas de ngrok
    except FileNotFoundError:
        log_info("Ngrok non installé (optionnel)", "WARNING")
        return True, False

def update_env_file(file_path, key, value):
    """Mettre à jour une variable dans un fichier .env"""
    try:
        if not os.path.exists(file_path):
            log_info(f"Fichier .env non trouvé: {file_path}", "WARNING")
            return False
        
        # Lire le fichier
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Chercher et remplacer la ligne
        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                updated = True
                break
        
        # Si la clé n'existe pas, l'ajouter
        if not updated:
            lines.append(f"{key}={value}\n")
        
        # Réécrire le fichier
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        log_info(f"✅ {file_path}: {key}={value}", "SUCCESS")
        return True
        
    except Exception as e:
        log_info(f"Erreur mise à jour {file_path}: {e}", "ERROR")
        return False

def configure_local_mode():
    """Configurer l'application pour le mode local"""
    log_info("Configuration mode local...")
    
    project_root = Path(__file__).parent
    backend_env = project_root / "backend" / ".env"
    frontend_env = project_root / "frontend" / ".env"
    ngrok_url_file = project_root / "backend" / "ngrok_url.txt"
    
    # Configuration backend
    success = True
    success &= update_env_file(str(backend_env), "ENABLE_NGROK", "false")
    
    # Configuration frontend
    success &= update_env_file(str(frontend_env), "REACT_APP_BACKEND_URL", "http://localhost:8001")
    
    # Fichier URL ngrok
    try:
        with open(str(ngrok_url_file), 'w') as f:
            f.write("http://localhost:8001\n")
        log_info("Fichier ngrok_url.txt mis à jour", "SUCCESS")
    except Exception as e:
        log_info(f"Erreur fichier ngrok_url.txt: {e}", "ERROR")
        success = False
    
    return success

def get_ngrok_url(max_attempts=10):
    """Récupérer l'URL ngrok active"""
    log_info("Récupération de l'URL ngrok...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get('tunnels', [])
                
                if tunnels:
                    # Chercher le tunnel HTTP
                    for tunnel in tunnels:
                        public_url = tunnel.get('public_url', '')
                        if public_url.startswith('https://'):
                            log_info(f"URL ngrok trouvée: {public_url}", "SUCCESS")
                            return public_url
                    
                    # Prendre le premier tunnel si pas de HTTPS
                    public_url = tunnels[0].get('public_url', '')
                    if public_url:
                        log_info(f"URL ngrok trouvée: {public_url}", "SUCCESS")
                        return public_url
                
            log_info(f"Tentative {attempt + 1}/{max_attempts}: Tunnel pas encore prêt...", "WARNING")
            time.sleep(2)
            
        except requests.exceptions.ConnectionError:
            log_info(f"Tentative {attempt + 1}/{max_attempts}: Ngrok pas encore accessible...", "WARNING")
            time.sleep(2)
        except Exception as e:
            log_info(f"Erreur lors de la récupération: {e}", "ERROR")
            time.sleep(2)
    
    log_info("Impossible de récupérer l'URL ngrok", "ERROR")
    return None

def configure_ngrok_mode(ngrok_url):
    """Configuer l'application pour le mode ngrok"""
    log_info(f"Configuration mode ngrok: {ngrok_url}")
    
    project_root = Path(__file__).parent
    backend_env = project_root / "backend" / ".env"
    frontend_env = project_root / "frontend" / ".env"
    ngrok_url_file = project_root / "backend" / "ngrok_url.txt"
    
    # Configuration backend
    success = True
    success &= update_env_file(str(backend_env), "ENABLE_NGROK", "detect")
    
    # Configuration frontend
    success &= update_env_file(str(frontend_env), "REACT_APP_BACKEND_URL", ngrok_url)
    
    # Fichier URL ngrok
    try:
        with open(str(ngrok_url_file), 'w') as f:
            f.write(f"{ngrok_url}\n")
        log_info("Fichier ngrok_url.txt mis à jour", "SUCCESS")
    except Exception as e:
        log_info(f"Erreur fichier ngrok_url.txt: {e}", "ERROR")
        success = False
    
    return success

def install_dependencies():
    """Installer les dépendances Python et Node.js"""
    log_info("Installation des dépendances...")
    
    project_root = Path(__file__).parent
    
    # Dépendances Python
    log_info("Installation dépendances Python...")
    try:
        result = subprocess.run([
            "pip", "install", "-r", str(project_root / "backend" / "requirements.txt")
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            log_info("Dépendances Python installées", "SUCCESS")
        else:
            # Essayer avec --user
            result = subprocess.run([
                "pip", "install", "--user", "-r", str(project_root / "backend" / "requirements.txt")
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                log_info("Dépendances Python installées avec --user", "SUCCESS")
            else:
                log_info(f"Erreur dépendances Python: {result.stderr}", "ERROR")
                return False
                
    except Exception as e:
        log_info(f"Erreur installation Python: {e}", "ERROR")
        return False
    
    # Dépendances Node.js
    log_info("Installation dépendances Node.js...")
    node_modules = project_root / "frontend" / "node_modules"
    
    if not node_modules.exists():
        try:
            result = subprocess.run([
                "npm", "install"
            ], cwd=str(project_root / "frontend"), capture_output=True, text=True)
            
            if result.returncode == 0:
                log_info("Dépendances Node.js installées", "SUCCESS")
            else:
                log_info(f"Erreur dépendances Node.js: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            log_info(f"Erreur installation Node.js: {e}", "ERROR")
            return False
    else:
        log_info("Dépendances Node.js déjà installées", "SUCCESS")
    
    return True

def print_instructions(mode="local", ngrok_url=None):
    """Afficher les instructions d'utilisation"""
    print("\n" + "="*50)
    print("   FACEBOOK POST APPLICATION - PRÊTE")
    print("="*50)
    
    if mode == "local":
        print("\n📋 Mode LOCAL configuré:")
        print("   • Backend API: http://localhost:8001")
        print("   • Frontend App: http://localhost:3000")
        print("   • Accès limité à cet ordinateur")
        print("\n💡 URLs importantes:")
        print("   • Application: http://localhost:3000")
        print("   • API Health: http://localhost:8001/api/health")
        print("   • Webhook N8N: http://localhost:8001/api/webhook")
        
    elif mode == "tunnel" and ngrok_url:
        print(f"\n📋 Mode TUNNEL configuré:")
        print(f"   • URL Publique: {ngrok_url}")
        print(f"   • Accessible depuis Internet")
        print(f"   • Interface Ngrok: http://127.0.0.1:4040")
        print(f"\n📱 Configuration Facebook requise:")
        domain = ngrok_url.replace("https://", "").replace("http://", "")
        print(f"   1. App Domains: {domain}")
        print(f"   2. OAuth Redirect: {ngrok_url}/auth/callback")
        print(f"   3. Webhook URL: {ngrok_url}/api/webhook")
    
    print("\n✅ Fonctionnalités disponibles:")
    print("   • Publication Facebook automatique")
    print("   • Publication Instagram (avec tokens)")
    print("   • Interface utilisateur React")
    print("   • API Webhook pour N8N/e-commerce")
    print("   • OAuth Facebook intégré")
    
    print("\n⚠️ Important:")
    print("   • Gardez les fenêtres de commande ouvertes")
    print("   • Les services doivent rester actifs")
    print("="*50)

def main():
    """Fonction principale"""
    if len(sys.argv) < 2:
        print("Usage: python windows_helper.py [command]")
        print("Commands:")
        print("  check_prereq    - Vérifier les prérequis")
        print("  config_local    - Configuration mode local")
        print("  config_ngrok    - Configuration mode ngrok")
        print("  install_deps    - Installer les dépendances")
        print("  get_ngrok_url   - Récupérer URL ngrok")
        return
    
    command = sys.argv[1]
    
    if command == "check_prereq":
        prereq_ok, ngrok_available = check_prerequisites()
        if prereq_ok:
            log_info("Prérequis vérifiés avec succès", "SUCCESS")
            if ngrok_available:
                log_info("Mode tunnel disponible", "SUCCESS")
            else:
                log_info("Mode local uniquement", "WARNING")
        else:
            log_info("Prérequis manquants", "ERROR")
            sys.exit(1)
    
    elif command == "config_local":
        if configure_local_mode():
            print_instructions("local")
        else:
            log_info("Erreur configuration locale", "ERROR")
            sys.exit(1)
    
    elif command == "config_ngrok":
        ngrok_url = get_ngrok_url()
        if ngrok_url and configure_ngrok_mode(ngrok_url):
            print_instructions("tunnel", ngrok_url)
        else:
            log_info("Erreur configuration ngrok", "ERROR")
            sys.exit(1)
    
    elif command == "install_deps":
        if install_dependencies():
            log_info("Dépendances installées avec succès", "SUCCESS")
        else:
            log_info("Erreur installation dépendances", "ERROR")
            sys.exit(1)
    
    elif command == "get_ngrok_url":
        ngrok_url = get_ngrok_url()
        if ngrok_url:
            print(ngrok_url)
        else:
            sys.exit(1)
    
    else:
        log_info(f"Commande inconnue: {command}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()