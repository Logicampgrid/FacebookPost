#!/usr/bin/env python3
"""
Script de synchronisation automatique ngrok pour FacebookPost
Détecte les URLs ngrok actives et met à jour automatiquement la configuration
"""

import requests
import json
import os
import time
from datetime import datetime
from typing import Optional, Dict, List

# Configuration
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
FRONTEND_ENV_PATH = os.path.join(PROJECT_ROOT, "frontend", ".env")
NGROK_URL_FILE = os.path.join(BACKEND_DIR, "ngrok_url.txt")

def log_sync(message: str, level: str = "INFO"):
    """Logging pour la synchronisation"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "START": "🚀"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [NGROK-SYNC] {message}")

def get_active_ngrok_tunnels() -> List[Dict]:
    """Récupère la liste des tunnels ngrok actifs"""
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('tunnels', [])
        else:
            log_sync(f"API ngrok inaccessible (status: {response.status_code})", "WARNING")
            return []
    except requests.exceptions.ConnectionError:
        log_sync("API ngrok non accessible (port 4040 fermé)", "WARNING")
        return []
    except Exception as e:
        log_sync(f"Erreur récupération tunnels ngrok: {e}", "ERROR")
        return []

def find_backend_tunnel(tunnels: List[Dict], backend_port: int = 8001) -> Optional[str]:
    """Trouve le tunnel ngrok correspondant au port backend"""
    for tunnel in tunnels:
        config = tunnel.get('config', {})
        addr = config.get('addr', '')
        
        # Vérifier si le tunnel pointe vers notre port backend
        if f"localhost:{backend_port}" in addr or f":{backend_port}" in addr:
            public_url = tunnel.get('public_url', '')
            if public_url and public_url.startswith('https://'):
                return public_url
    
    # Si pas de tunnel spécifique trouvé, retourner le premier tunnel HTTPS
    for tunnel in tunnels:
        public_url = tunnel.get('public_url', '')
        if public_url and public_url.startswith('https://'):
            return public_url
    
    return None

def update_frontend_env(ngrok_url: str) -> bool:
    """Met à jour le fichier .env du frontend avec la nouvelle URL ngrok"""
    try:
        if not os.path.exists(FRONTEND_ENV_PATH):
            log_sync(f"Fichier frontend .env non trouvé: {FRONTEND_ENV_PATH}", "ERROR")
            return False
        
        # Lire le contenu actuel
        with open(FRONTEND_ENV_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Mettre à jour ou ajouter REACT_APP_BACKEND_URL
        updated_lines = []
        backend_url_updated = False
        
        for line in lines:
            if line.startswith('REACT_APP_BACKEND_URL='):
                updated_lines.append(f'REACT_APP_BACKEND_URL={ngrok_url}\n')
                backend_url_updated = True
                log_sync(f"Ligne mise à jour dans .env: REACT_APP_BACKEND_URL={ngrok_url}", "SUCCESS")
            else:
                updated_lines.append(line)
        
        # Si REACT_APP_BACKEND_URL n'existe pas, l'ajouter
        if not backend_url_updated:
            updated_lines.append(f'REACT_APP_BACKEND_URL={ngrok_url}\n')
            log_sync(f"Ligne ajoutée dans .env: REACT_APP_BACKEND_URL={ngrok_url}", "SUCCESS")
        
        # Écrire le fichier mis à jour
        with open(FRONTEND_ENV_PATH, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        log_sync("Frontend .env mis à jour avec succès", "SUCCESS")
        return True
        
    except Exception as e:
        log_sync(f"Erreur mise à jour frontend .env: {e}", "ERROR")
        return False

def update_ngrok_url_file(ngrok_url: str) -> bool:
    """Met à jour le fichier ngrok_url.txt"""
    try:
        with open(NGROK_URL_FILE, 'w', encoding='utf-8') as f:
            f.write(ngrok_url)
        log_sync(f"Fichier ngrok_url.txt mis à jour: {ngrok_url}", "SUCCESS")
        return True
    except Exception as e:
        log_sync(f"Erreur mise à jour ngrok_url.txt: {e}", "ERROR")
        return False

def get_facebook_app_config() -> Dict[str, str]:
    """Récupère la configuration Facebook depuis les variables d'environnement"""
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BACKEND_DIR, '.env'))
    
    return {
        'app_id': os.getenv('FACEBOOK_APP_ID', ''),
        'app_secret': os.getenv('FACEBOOK_APP_SECRET', ''),
        'client_token': os.getenv('FACEBOOK_CLIENT_TOKEN', '')
    }

def generate_facebook_config_instructions(ngrok_url: str) -> str:
    """Génère les instructions de configuration Facebook"""
    config = get_facebook_app_config()
    app_id = config.get('app_id', 'VOTRE_APP_ID')
    
    domain = ngrok_url.replace('https://', '').replace('http://', '')
    
    instructions = f"""
═══════════════════════════════════════════════════════════════
🔧 CONFIGURATION FACEBOOK APP REQUISE - URL NGROK MISE À JOUR
═══════════════════════════════════════════════════════════════

Nouvelle URL ngrok détectée: {ngrok_url}

📝 ACTIONS REQUISES dans Facebook Developer Console:

1. 🌐 Allez sur: https://developers.facebook.com/apps/{app_id}/settings/basic/

2. 📋 App Domains (Settings > Basic):
   Ajoutez: {domain}

3. 🔐 OAuth Redirect URIs (Facebook Login > Settings):
   Ajoutez ces deux URLs:
   • {ngrok_url}/auth/callback
   • {ngrok_url}/

4. 🔗 Webhooks (si utilisés):
   URL de callback: {ngrok_url}/api/webhook

═══════════════════════════════════════════════════════════════
💡 IMPORTANT: Ces modifications sont nécessaires pour que 
   l'authentification Facebook fonctionne avec cette URL ngrok.
═══════════════════════════════════════════════════════════════
    """.strip()
    
    return instructions

def sync_ngrok_configuration() -> Dict[str, any]:
    """Fonction principale de synchronisation des configurations ngrok"""
    result = {
        'success': False,
        'ngrok_url': None,
        'tunnels_found': 0,
        'frontend_updated': False,
        'file_updated': False,
        'instructions': '',
        'error': None
    }
    
    try:
        log_sync("🚀 Début de la synchronisation ngrok", "START")
        
        # Étape 1: Récupérer les tunnels actifs
        tunnels = get_active_ngrok_tunnels()
        result['tunnels_found'] = len(tunnels)
        
        if not tunnels:
            log_sync("Aucun tunnel ngrok actif trouvé", "WARNING")
            result['error'] = "Aucun tunnel ngrok actif"
            return result
        
        log_sync(f"Trouvé {len(tunnels)} tunnel(s) ngrok actif(s)", "INFO")
        
        # Étape 2: Identifier le tunnel backend
        ngrok_url = find_backend_tunnel(tunnels)
        if not ngrok_url:
            log_sync("Aucun tunnel correspondant au backend trouvé", "WARNING")
            result['error'] = "Aucun tunnel backend identifié"
            return result
        
        result['ngrok_url'] = ngrok_url
        log_sync(f"URL ngrok détectée: {ngrok_url}", "SUCCESS")
        
        # Étape 3: Mettre à jour le frontend .env
        if update_frontend_env(ngrok_url):
            result['frontend_updated'] = True
        
        # Étape 4: Mettre à jour le fichier ngrok_url.txt
        if update_ngrok_url_file(ngrok_url):
            result['file_updated'] = True
        
        # Étape 5: Générer les instructions Facebook
        result['instructions'] = generate_facebook_config_instructions(ngrok_url)
        
        # Succès si au moins une mise à jour a réussi
        result['success'] = result['frontend_updated'] or result['file_updated']
        
        if result['success']:
            log_sync("🎉 Synchronisation ngrok terminée avec succès", "SUCCESS")
            print(result['instructions'])
        else:
            log_sync("⚠️ Synchronisation partiellement échouée", "WARNING")
        
        return result
        
    except Exception as e:
        log_sync(f"Erreur générale de synchronisation: {e}", "ERROR")
        result['error'] = str(e)
        return result

def watch_ngrok_changes(interval: int = 30):
    """Surveille les changements d'URL ngrok et synchronise automatiquement"""
    log_sync(f"🔄 Début de la surveillance ngrok (intervalle: {interval}s)", "START")
    
    last_ngrok_url = None
    
    while True:
        try:
            result = sync_ngrok_configuration()
            current_url = result.get('ngrok_url')
            
            if current_url and current_url != last_ngrok_url:
                log_sync(f"🔄 Changement d'URL détecté: {current_url}", "INFO")
                last_ngrok_url = current_url
                
                # Afficher les instructions seulement lors d'un changement
                if result.get('instructions'):
                    print("\n" + result['instructions'] + "\n")
            
            time.sleep(interval)
            
        except KeyboardInterrupt:
            log_sync("🛑 Surveillance interrompue par l'utilisateur", "INFO")
            break
        except Exception as e:
            log_sync(f"Erreur dans la surveillance: {e}", "ERROR")
            time.sleep(interval)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        # Mode surveillance continue
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        watch_ngrok_changes(interval)
    else:
        # Mode synchronisation unique
        result = sync_ngrok_configuration()
        
        # Afficher le résultat en JSON pour usage programmatique
        print("\n📊 RÉSULTAT DE LA SYNCHRONISATION:")
        print(json.dumps(result, indent=2, ensure_ascii=False))