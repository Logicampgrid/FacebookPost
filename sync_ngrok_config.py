#!/usr/bin/env python3
"""
Script de synchronisation automatique des configurations ngrok
À utiliser après le démarrage de ngrok pour mettre à jour toutes les configurations
"""
import os
import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime

def log_message(message, level="INFO"):
    """Logging avec timestamp et icônes"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "START": "🚀"}
    icon = icons.get(level, "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] {message}")

def get_active_ngrok_url(max_attempts=10):
    """Récupère l'URL ngrok active avec retry"""
    log_message("Recherche de l'URL ngrok active...", "INFO")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
            
            if response.status_code == 200:
                tunnels_data = response.json()
                tunnels = tunnels_data.get('tunnels', [])
                
                if tunnels:
                    # Chercher le tunnel sur le port 8001
                    for tunnel in tunnels:
                        config = tunnel.get('config', {})
                        if config.get('addr') == 'http://localhost:8001':
                            public_url = tunnel.get('public_url')
                            if public_url:
                                log_message(f"URL ngrok trouvée: {public_url}", "SUCCESS")
                                return public_url
                    
                    # Si pas de tunnel spécifique, prendre le premier
                    first_tunnel = tunnels[0]
                    public_url = first_tunnel.get('public_url')
                    if public_url:
                        log_message(f"URL ngrok (premier tunnel): {public_url}", "SUCCESS")
                        return public_url
                
                log_message(f"Tentative {attempt + 1}/{max_attempts}: Aucun tunnel actif", "WARNING")
            else:
                log_message(f"Tentative {attempt + 1}/{max_attempts}: API ngrok status {response.status_code}", "WARNING")
                
        except requests.exceptions.ConnectionError:
            log_message(f"Tentative {attempt + 1}/{max_attempts}: API ngrok non accessible", "WARNING")
        except Exception as e:
            log_message(f"Tentative {attempt + 1}/{max_attempts}: Erreur {e}", "WARNING")
        
        if attempt < max_attempts - 1:
            time.sleep(2)
    
    log_message("Impossible de récupérer l'URL ngrok", "ERROR")
    return None

def update_frontend_env(ngrok_url):
    """Met à jour le fichier .env du frontend"""
    try:
        frontend_env_path = Path(__file__).parent / "frontend" / ".env"
        
        if not frontend_env_path.exists():
            log_message(f"Fichier .env frontend non trouvé: {frontend_env_path}", "ERROR")
            return False
        
        # Lire le fichier actuel
        with open(frontend_env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Créer une sauvegarde
        backup_path = frontend_env_path.with_suffix('.env.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # Mettre à jour REACT_APP_BACKEND_URL
        updated_lines = []
        backend_url_updated = False
        
        for line in lines:
            if line.startswith("REACT_APP_BACKEND_URL="):
                old_url = line.split("=", 1)[1].strip()
                if old_url != ngrok_url:
                    updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}\n")
                    log_message(f"REACT_APP_BACKEND_URL: {old_url} → {ngrok_url}", "SUCCESS")
                else:
                    updated_lines.append(line)
                    log_message(f"REACT_APP_BACKEND_URL déjà à jour: {ngrok_url}", "INFO")
                backend_url_updated = True
            else:
                updated_lines.append(line)
        
        # Si REACT_APP_BACKEND_URL n'existe pas, l'ajouter
        if not backend_url_updated:
            updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}\n")
            log_message(f"REACT_APP_BACKEND_URL ajouté: {ngrok_url}", "SUCCESS")
        
        # Écrire le fichier mis à jour
        with open(frontend_env_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        log_message("Frontend .env mis à jour avec succès", "SUCCESS")
        return True
        
    except Exception as e:
        log_message(f"Erreur mise à jour frontend .env: {e}", "ERROR")
        return False

def save_ngrok_url_for_backend(ngrok_url):
    """Sauvegarde l'URL ngrok pour le backend"""
    try:
        backend_dir = Path(__file__).parent / "backend"
        ngrok_file = backend_dir / "ngrok_url.txt"
        
        with open(ngrok_file, 'w', encoding='utf-8') as f:
            f.write(ngrok_url)
        
        log_message(f"URL ngrok sauvegardée: {ngrok_file}", "SUCCESS")
        return True
        
    except Exception as e:
        log_message(f"Erreur sauvegarde URL ngrok: {e}", "ERROR")
        return False

def notify_backend_of_ngrok_change(ngrok_url):
    """Notifie le backend du changement d'URL ngrok"""
    try:
        # Attendre que le backend soit prêt
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                health_url = f"{ngrok_url}/api/health"
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    log_message("Backend accessible via ngrok", "SUCCESS")
                    break
            except:
                if attempt < max_attempts - 1:
                    log_message(f"Attente du backend... ({attempt + 1}/{max_attempts})", "INFO")
                    time.sleep(2)
                else:
                    log_message("Backend non accessible via ngrok", "WARNING")
        
        # Essayer de notifier le backend via API locale
        try:
            sync_url = "http://localhost:8001/api/sync/ngrok"
            sync_data = {"ngrok_url": ngrok_url}
            response = requests.post(sync_url, json=sync_data, timeout=5)
            if response.status_code == 200:
                log_message("Backend notifié du changement d'URL", "SUCCESS")
            else:
                log_message(f"Erreur notification backend: {response.status_code}", "WARNING")
        except:
            log_message("Backend pas encore prêt pour la notification", "INFO")
        
        return True
        
    except Exception as e:
        log_message(f"Erreur notification backend: {e}", "WARNING")
        return False

def create_oauth_config_summary(ngrok_url):
    """Crée un résumé de la configuration OAuth"""
    try:
        config_file = Path(__file__).parent / "oauth_config_summary.txt"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write("=== CONFIGURATION OAUTH FACEBOOK ===\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"URL Ngrok Active: {ngrok_url}\n")
            f.write(f"URL de redirection OAuth: {ngrok_url}/\n")
            f.write(f"URL de callback: {ngrok_url}/auth/callback\n")
            f.write(f"API Health Check: {ngrok_url}/api/health\n")
            f.write("\n=== URLS FACEBOOK DEVELOPER ===\n")
            f.write("À configurer dans votre application Facebook:\n")
            f.write(f"• Valid OAuth Redirect URIs: {ngrok_url}/\n")
            f.write(f"• Webhook URL: {ngrok_url}/webhook/facebook\n")
            f.write("\n=== COMMANDES DE TEST ===\n")
            f.write(f"• Test API: curl {ngrok_url}/api/health\n")
            f.write(f"• Test Frontend: {ngrok_url}\n")
        
        log_message(f"Résumé de configuration créé: {config_file}", "SUCCESS")
        return True
        
    except Exception as e:
        log_message(f"Erreur création résumé: {e}", "ERROR")
        return False

def main():
    """Point d'entrée principal"""
    log_message("🚀 Synchronisation des configurations ngrok", "START")
    
    # Récupérer l'URL ngrok active
    ngrok_url = get_active_ngrok_url()
    
    if not ngrok_url:
        log_message("❌ Impossible de synchroniser sans URL ngrok", "ERROR")
        return 1
    
    log_message(f"🎯 URL ngrok détectée: {ngrok_url}", "SUCCESS")
    
    # Mettre à jour toutes les configurations
    success_count = 0
    total_tasks = 4
    
    # 1. Mettre à jour le frontend .env
    if update_frontend_env(ngrok_url):
        success_count += 1
    
    # 2. Sauvegarder l'URL pour le backend
    if save_ngrok_url_for_backend(ngrok_url):
        success_count += 1
    
    # 3. Notifier le backend
    if notify_backend_of_ngrok_change(ngrok_url):
        success_count += 1
    
    # 4. Créer le résumé de configuration
    if create_oauth_config_summary(ngrok_url):
        success_count += 1
    
    # Résumé final
    log_message(f"🎊 Synchronisation terminée: {success_count}/{total_tasks} tâches réussies", "SUCCESS")
    
    if success_count == total_tasks:
        log_message("✅ Toutes les configurations OAuth sont synchronisées!", "SUCCESS")
        log_message("🔐 L'authentification Facebook devrait maintenant fonctionner", "SUCCESS")
        log_message(f"🌐 Application accessible sur: {ngrok_url}", "SUCCESS")
        return 0
    else:
        log_message("⚠️ Certaines configurations ont échoué", "WARNING")
        return 1

if __name__ == "__main__":
    sys.exit(main())