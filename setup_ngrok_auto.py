#!/usr/bin/env python3
"""
Script automatique de configuration Ngrok
Démarre ngrok, récupère l'URL et met à jour tous les fichiers de configuration
"""

import subprocess
import requests
import time
import os
import json
from pathlib import Path

def log_info(message):
    print(f"🔧 [SETUP] {message}")

def log_success(message):
    print(f"✅ [SUCCESS] {message}")

def log_error(message):
    print(f"❌ [ERROR] {message}")

def log_warning(message):
    print(f"⚠️ [WARNING] {message}")

def kill_existing_ngrok():
    """Arrête tous les processus ngrok existants"""
    try:
        log_info("Arrêt des processus ngrok existants...")
        subprocess.run(["pkill", "-f", "ngrok"], capture_output=True)
        time.sleep(2)
        log_success("Processus ngrok arrêtés")
    except Exception as e:
        log_warning(f"Erreur lors de l'arrêt des processus ngrok: {e}")

def start_ngrok():
    """Démarre ngrok sur le port 8001"""
    try:
        log_info("Démarrage de ngrok sur le port 8001...")
        
        # Démarrer ngrok en arrière-plan
        process = subprocess.Popen(
            ["ngrok", "http", "8001", "--log=stdout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        log_info("Attente de l'initialisation de ngrok...")
        time.sleep(8)  # Laisser le temps à ngrok de démarrer
        
        return process
    except Exception as e:
        log_error(f"Impossible de démarrer ngrok: {e}")
        return None

def get_ngrok_url():
    """Récupère l'URL ngrok active"""
    max_attempts = 15
    for attempt in range(max_attempts):
        try:
            log_info(f"Tentative {attempt + 1}/{max_attempts} de récupération de l'URL ngrok...")
            
            response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
            
            if response.status_code == 200:
                tunnels_data = response.json()
                tunnels = tunnels_data.get('tunnels', [])
                
                if tunnels:
                    # Chercher le tunnel HTTPS
                    for tunnel in tunnels:
                        public_url = tunnel.get('public_url')
                        if public_url and public_url.startswith('https://'):
                            log_success(f"URL ngrok trouvée: {public_url}")
                            return public_url
                    
                    # Si pas d'HTTPS, prendre le premier
                    first_url = tunnels[0].get('public_url')
                    if first_url:
                        log_success(f"URL ngrok trouvée (première): {first_url}")
                        return first_url
                
                log_warning("Aucun tunnel trouvé, nouvelle tentative...")
                time.sleep(2)
                
        except requests.exceptions.ConnectionError:
            log_warning("API ngrok non accessible, nouvelle tentative...")
            time.sleep(2)
        except Exception as e:
            log_warning(f"Erreur récupération URL: {e}")
            time.sleep(2)
    
    log_error("Impossible de récupérer l'URL ngrok après plusieurs tentatives")
    return None

def update_env_file(file_path, key, value):
    """Met à jour une variable dans un fichier .env"""
    try:
        if not os.path.exists(file_path):
            log_warning(f"Fichier .env non trouvé: {file_path}")
            return False
        
        # Lire le fichier
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Mettre à jour la ligne
        updated = False
        new_lines = []
        
        for line in lines:
            if line.startswith(f"{key}="):
                new_lines.append(f"{key}={value}\n")
                updated = True
            else:
                new_lines.append(line)
        
        # Si la clé n'existe pas, l'ajouter
        if not updated:
            new_lines.append(f"{key}={value}\n")
        
        # Réécrire le fichier
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        log_success(f"{key} mis à jour dans {file_path}")
        return True
        
    except Exception as e:
        log_error(f"Erreur mise à jour {file_path}: {e}")
        return False

def update_all_configs(ngrok_url):
    """Met à jour tous les fichiers de configuration avec la nouvelle URL ngrok"""
    log_info("Mise à jour des fichiers de configuration...")
    
    # Fichiers à mettre à jour
    updates = [
        {
            "file": "/app/.env",
            "key": "WEBHOOK_URL",
            "value": ngrok_url
        },
        {
            "file": "/app/backend/.env", 
            "key": "WEBHOOK_URL",
            "value": ngrok_url
        },
        {
            "file": "/app/frontend/.env",
            "key": "REACT_APP_BACKEND_URL", 
            "value": ngrok_url
        }
    ]
    
    success_count = 0
    for update in updates:
        if update_env_file(update["file"], update["key"], update["value"]):
            success_count += 1
    
    log_success(f"Configuration mise à jour dans {success_count}/{len(updates)} fichiers")
    
    # Créer un fichier avec l'URL pour référence
    try:
        with open("/app/backend/ngrok_url.txt", "w") as f:
            f.write(ngrok_url)
        log_success("URL sauvegardée dans ngrok_url.txt")
    except Exception as e:
        log_warning(f"Impossible de sauvegarder l'URL: {e}")

def main():
    """Fonction principale"""
    log_info("🚀 Configuration automatique de Ngrok pour FacebookPost")
    
    # 1. Arrêter ngrok existant
    kill_existing_ngrok()
    
    # 2. Démarrer ngrok
    ngrok_process = start_ngrok()
    if not ngrok_process:
        log_error("Impossible de démarrer ngrok")
        return False
    
    # 3. Récupérer l'URL
    ngrok_url = get_ngrok_url()
    if not ngrok_url:
        log_error("Impossible de récupérer l'URL ngrok")
        return False
    
    # 4. Mettre à jour les configurations
    update_all_configs(ngrok_url)
    
    log_success("🎉 Configuration ngrok terminée avec succès!")
    log_info(f"🌐 URL publique: {ngrok_url}")
    log_info("🔄 Redémarrez maintenant votre application avec cette URL")
    
    return True

if __name__ == "__main__":
    main()