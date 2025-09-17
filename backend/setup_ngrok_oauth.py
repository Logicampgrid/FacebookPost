#!/usr/bin/env python3
"""
Script utilitaire pour configurer ngrok et OAuth Facebook automatiquement
Usage: python setup_ngrok_oauth.py [--force] [--url URL_NGROK]
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

# Ajouter le répertoire parent au PYTHONPATH pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def log_setup(message: str, level: str = "INFO"):
    """Logging pour le setup"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "START": "🚀"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [SETUP] {message}")

def check_ngrok_api():
    """Vérifier si l'API ngrok est accessible"""
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_ngrok_tunnels():
    """Récupérer les tunnels ngrok actifs"""
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            return response.json().get('tunnels', [])
        return []
    except:
        return []

def update_frontend_env(ngrok_url: str):
    """Mettre à jour le .env du frontend avec la nouvelle URL"""
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        frontend_env_path = os.path.join(project_root, "frontend", ".env")
        
        if not os.path.exists(frontend_env_path):
            log_setup(f"Fichier .env non trouvé: {frontend_env_path}", "ERROR")
            return False
        
        # Lire le contenu actuel
        with open(frontend_env_path, "r", encoding='utf-8') as f:
            content = f.read()
        
        lines = content.splitlines()
        updated_lines = []
        backend_url_updated = False
        
        for line in lines:
            if line.startswith("REACT_APP_BACKEND_URL="):
                old_url = line.split("=", 1)[1] if "=" in line else ""
                updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}")
                log_setup(f"REACT_APP_BACKEND_URL mis à jour: {old_url} -> {ngrok_url}", "SUCCESS")
                backend_url_updated = True
            else:
                updated_lines.append(line)
        
        if not backend_url_updated:
            updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}")
            log_setup(f"REACT_APP_BACKEND_URL ajouté: {ngrok_url}", "SUCCESS")
        
        # Réécrire le fichier
        with open(frontend_env_path, "w", encoding='utf-8') as f:
            f.write("\n".join(updated_lines))
            if updated_lines:
                f.write("\n")
        
        log_setup("Frontend .env mis à jour avec succès", "SUCCESS")
        return True
        
    except Exception as e:
        log_setup(f"Erreur mise à jour frontend .env: {e}", "ERROR")
        return False

def trigger_oauth_setup():
    """Déclencher la configuration OAuth via l'API backend"""
    try:
        response = requests.post("http://localhost:8001/api/config/force-oauth-setup", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                log_setup("Configuration OAuth déclenchée avec succès", "SUCCESS")
                log_setup(f"URL utilisée: {data.get('backend_url')}", "SUCCESS")
                for uri in data.get("redirect_uris", []):
                    log_setup(f"  • {uri}", "SUCCESS")
                return True
            else:
                log_setup(f"Erreur configuration OAuth: {data.get('error')}", "ERROR")
                return False
        else:
            log_setup(f"Erreur HTTP: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log_setup(f"Erreur déclenchement OAuth: {e}", "ERROR")
        return False

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Configuration automatique ngrok et OAuth Facebook")
    parser.add_argument("--force", action="store_true", help="Forcer la configuration même si ngrok n'est pas actif")
    parser.add_argument("--url", help="URL ngrok spécifique à utiliser")
    
    args = parser.parse_args()
    
    log_setup("🚀 Démarrage de la configuration ngrok et OAuth", "START")
    
    ngrok_url = None
    
    # Étape 1: Déterminer l'URL ngrok à utiliser
    if args.url:
        ngrok_url = args.url
        log_setup(f"URL ngrok spécifiée: {ngrok_url}", "INFO")
    else:
        # Vérifier si ngrok est actif
        if check_ngrok_api():
            tunnels = get_ngrok_tunnels()
            if tunnels:
                # Prendre le premier tunnel HTTPS
                for tunnel in tunnels:
                    url = tunnel.get('public_url', '')
                    if url.startswith('https://'):
                        ngrok_url = url
                        break
                
                if ngrok_url:
                    log_setup(f"URL ngrok détectée automatiquement: {ngrok_url}", "SUCCESS")
                else:
                    log_setup("Aucun tunnel HTTPS trouvé", "WARNING")
            else:
                log_setup("Aucun tunnel ngrok trouvé", "WARNING")
        else:
            log_setup("API ngrok non accessible", "WARNING")
    
    if not ngrok_url and not args.force:
        log_setup("Aucune URL ngrok disponible. Utilisez --force pour configurer manuellement", "ERROR")
        log_setup("Ou spécifiez une URL avec --url https://votre-url.ngrok-free.app", "INFO")
        return False
    
    # Étape 2: Mettre à jour le frontend .env si une URL est disponible
    if ngrok_url:
        if not update_frontend_env(ngrok_url):
            log_setup("Échec de la mise à jour du frontend .env", "ERROR")
            return False
        
        # Attendre un peu pour que le backend détecte le changement
        log_setup("Attente de la synchronisation backend...", "INFO")
        time.sleep(3)
    
    # Étape 3: Déclencher la configuration OAuth
    if not trigger_oauth_setup():
        log_setup("Échec de la configuration OAuth", "ERROR")
        return False
    
    # Étape 4: Vérifier le statut final
    try:
        response = requests.get("http://localhost:8001/api/config/oauth-status-complete", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_setup("État final de la configuration:", "INFO")
            log_setup(f"  • Ngrok actif: {'✅' if data.get('ngrok_active') else '❌'}", "INFO")
            log_setup(f"  • URL ngrok: {data.get('ngrok_url', 'N/A')}", "INFO")
            log_setup(f"  • OAuth prêt: {'✅' if data.get('oauth_ready') else '❌'}", "INFO")
            log_setup(f"  • Configuration complète: {'✅' if data.get('auto_config_completed') else '❌'}", "INFO")
            
            if data.get('oauth_ready'):
                log_setup("🎉 Configuration terminée avec succès!", "SUCCESS")
                return True
            else:
                log_setup("⚠️ Configuration incomplète", "WARNING")
                return False
    except Exception as e:
        log_setup(f"Erreur vérification finale: {e}", "ERROR")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)