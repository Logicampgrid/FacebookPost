#!/usr/bin/env python3
"""
Script pour démarrer ngrok et mettre à jour automatiquement toutes les configurations
"""

import subprocess
import time
import requests
import os
import json
from datetime import datetime

def log_ngrok(message: str, level: str = "INFO"):
    """Logging pour ngrok"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "START": "🚀"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [NGROK] {message}")

def start_ngrok():
    """Démarre ngrok en arrière-plan"""
    try:
        log_ngrok("Arrêt des processus ngrok existants...", "INFO")
        
        # Tuer les processus ngrok existants (Windows et Linux)
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(["taskkill", "/f", "/im", "ngrok.exe"], capture_output=True)
            else:  # Linux/Mac
                subprocess.run(["pkill", "-f", "ngrok"], capture_output=True)
        except:
            pass
        
        time.sleep(2)
        
        log_ngrok("Démarrage de ngrok...", "START")
        
        # Démarrer ngrok en arrière-plan
        cmd = ["ngrok", "http", "8001", "--log=stdout"]
        
        # Utiliser subprocess.Popen pour ne pas attendre
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="/app/backend"
        )
        
        log_ngrok(f"Ngrok démarré avec PID: {process.pid}", "SUCCESS")
        
        # Attendre que ngrok soit prêt
        max_attempts = 20
        for attempt in range(max_attempts):
            try:
                time.sleep(2)
                response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
                if response.status_code == 200:
                    log_ngrok(f"API ngrok accessible après {attempt + 1} tentatives", "SUCCESS")
                    return True
            except:
                log_ngrok(f"Tentative {attempt + 1}/{max_attempts} - En attente de l'API ngrok...", "INFO")
                continue
        
        log_ngrok("Timeout: ngrok ne répond pas", "ERROR")
        return False
        
    except Exception as e:
        log_ngrok(f"Erreur démarrage ngrok: {e}", "ERROR")
        return False

def get_ngrok_url():
    """Récupère l'URL ngrok active"""
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=10)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            
            if tunnels:
                # Chercher le tunnel HTTP/HTTPS
                for tunnel in tunnels:
                    public_url = tunnel.get('public_url', '')
                    if public_url.startswith('https://'):
                        log_ngrok(f"URL ngrok trouvée: {public_url}", "SUCCESS")
                        return public_url
                
                # Si pas de HTTPS, prendre le premier
                first_url = tunnels[0].get('public_url', '')
                if first_url:
                    log_ngrok(f"URL ngrok (fallback): {first_url}", "SUCCESS")
                    return first_url
            
            log_ngrok("Aucun tunnel ngrok trouvé", "WARNING")
            return None
    except Exception as e:
        log_ngrok(f"Erreur récupération URL ngrok: {e}", "ERROR")
        return None

def update_frontend_env(ngrok_url):
    """Met à jour le frontend .env avec la nouvelle URL"""
    try:
        frontend_env_path = "/app/frontend/.env"
        
        # Lire le fichier actuel
        with open(frontend_env_path, "r", encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer l'URL backend
        lines = content.splitlines()
        updated_lines = []
        backend_url_updated = False
        
        for line in lines:
            if line.startswith("REACT_APP_BACKEND_URL="):
                updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}")
                backend_url_updated = True
                log_ngrok("Frontend .env mis à jour", "SUCCESS")
            else:
                updated_lines.append(line)
        
        if not backend_url_updated:
            updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}")
        
        # Réécrire le fichier
        with open(frontend_env_path, "w", encoding='utf-8') as f:
            f.write("\n".join(updated_lines))
            if updated_lines:
                f.write("\n")
        
        return True
    except Exception as e:
        log_ngrok(f"Erreur mise à jour frontend .env: {e}", "ERROR")
        return False

def update_backend_env(ngrok_url):
    """Met à jour le backend .env avec WEBHOOK_URL"""
    try:
        backend_env_path = "/app/backend/.env"
        
        # Lire le fichier actuel
        with open(backend_env_path, "r", encoding='utf-8') as f:
            content = f.read()
        
        # Ajouter ou mettre à jour WEBHOOK_URL
        lines = content.splitlines()
        updated_lines = []
        webhook_url_updated = False
        
        for line in lines:
            if line.startswith("WEBHOOK_URL="):
                updated_lines.append(f"WEBHOOK_URL={ngrok_url}")
                webhook_url_updated = True
                log_ngrok("WEBHOOK_URL mis à jour dans backend .env", "SUCCESS")
            else:
                updated_lines.append(line)
        
        if not webhook_url_updated:
            updated_lines.append(f"WEBHOOK_URL={ngrok_url}")
        
        # Réécrire le fichier
        with open(backend_env_path, "w", encoding='utf-8') as f:
            f.write("\n".join(updated_lines))
            if updated_lines:
                f.write("\n")
        
        return True
    except Exception as e:
        log_ngrok(f"Erreur mise à jour backend .env: {e}", "ERROR")
        return False

def save_ngrok_url(ngrok_url):
    """Sauvegarde l'URL dans le fichier texte"""
    try:
        with open("/app/backend/ngrok_url.txt", "w", encoding='utf-8') as f:
            f.write(ngrok_url)
        log_ngrok("URL sauvegardée dans ngrok_url.txt", "SUCCESS")
        return True
    except Exception as e:
        log_ngrok(f"Erreur sauvegarde ngrok_url.txt: {e}", "ERROR")
        return False

def main():
    log_ngrok("=== DÉMARRAGE ET CONFIGURATION NGROK ===", "START")
    
    # Étape 1: Démarrer ngrok
    if not start_ngrok():
        log_ngrok("Échec du démarrage de ngrok", "ERROR")
        return False
    
    # Étape 2: Récupérer l'URL
    ngrok_url = get_ngrok_url()
    if not ngrok_url:
        log_ngrok("Impossible de récupérer l'URL ngrok", "ERROR")
        return False
    
    # Étape 3: Mettre à jour toutes les configurations
    log_ngrok("Mise à jour des configurations...", "INFO")
    
    success_count = 0
    
    if update_frontend_env(ngrok_url):
        success_count += 1
    
    if update_backend_env(ngrok_url):
        success_count += 1
    
    if save_ngrok_url(ngrok_url):
        success_count += 1
    
    # Résumé
    log_ngrok("=== CONFIGURATION TERMINÉE ===", "SUCCESS")
    log_ngrok(f"URL ngrok active: {ngrok_url}", "SUCCESS")
    log_ngrok(f"Configurations mises à jour: {success_count}/3", "SUCCESS")
    
    if success_count == 3:
        log_ngrok("🎉 Configuration complète réussie !", "SUCCESS")
        log_ngrok("💡 Vous pouvez maintenant redémarrer l'application", "INFO")
        return True
    else:
        log_ngrok("⚠️ Configuration partiellement réussie", "WARNING")
        return False

if __name__ == "__main__":
    main()