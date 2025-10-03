#!/usr/bin/env python3
"""
Script de démarrage ngrok indépendant et stable
Lance ngrok dans une fenêtre séparée et maintient l'URL stable
"""

import subprocess
import requests
import time
import os
import signal
import sys
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Variable globale pour éviter les appels récursifs dans le signal handler
_cleanup_in_progress = False

def log_ngrok(message: str, level: str = "INFO"):
    """Logging pour ngrok standalone"""
    icons = {"INFO": "🌐", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "START": "🚀"}
    icon = icons.get(level.upper(), "🌐")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [NGROK] {message}")

def check_ngrok_running():
    """Vérifier si ngrok est déjà en cours d'exécution"""
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=3)
        if response.status_code == 200:
            tunnels = response.json().get('tunnels', [])
            if tunnels:
                url = tunnels[0]['public_url']
                log_ngrok(f"Ngrok déjà actif avec URL: {url}", "SUCCESS")
                return url
    except:
        pass
    return None

def kill_existing_ngrok():
    """Arrêter tous les processus ngrok existants"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(["tasklist", "/fi", "imagename eq ngrok.exe"], 
                                  capture_output=True, text=True)
            if "ngrok.exe" in result.stdout:
                log_ngrok("Arrêt des processus ngrok existants...", "INFO")
                subprocess.run(["taskkill", "/f", "/im", "ngrok.exe"], 
                             capture_output=True)
                time.sleep(2)
        else:  # Linux/Mac
            subprocess.run(["pkill", "-f", "ngrok"], capture_output=True)
            time.sleep(2)
        log_ngrok("Processus ngrok nettoyés", "SUCCESS")
    except Exception as e:
        log_ngrok(f"Erreur nettoyage ngrok: {e}", "WARNING")

def configure_ngrok():
    """Configurer le token d'authentification ngrok"""
    try:
        ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
        if ngrok_token:
            result = subprocess.run([
                "ngrok", "config", "add-authtoken", ngrok_token
            ], capture_output=True, text=True)
            if result.returncode == 0:
                log_ngrok("Token ngrok configuré", "SUCCESS")
                return True
            else:
                log_ngrok(f"Erreur configuration token: {result.stderr}", "ERROR")
        else:
            log_ngrok("NGROK_AUTH_TOKEN non défini dans .env", "WARNING")
        return False
    except Exception as e:
        log_ngrok(f"Erreur configuration ngrok: {e}", "ERROR")
        return False

def update_env_files_with_ngrok_url(ngrok_url):
    """Met à jour automatiquement les fichiers .env avec la nouvelle URL ngrok"""
    try:
        log_ngrok("🔄 Mise à jour automatique des fichiers .env...", "INFO")
        
        # Déterminer les chemins des fichiers .env
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(backend_dir)
        
        frontend_env_path = os.path.join(project_root, "frontend", ".env")
        backend_env_path = os.path.join(backend_dir, ".env")
        
        updated_files = []
        
        # 1. Mettre à jour le .env frontend (REACT_APP_BACKEND_URL)
        if os.path.exists(frontend_env_path):
            try:
                with open(frontend_env_path, "r", encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.splitlines()
                updated_lines = []
                backend_url_updated = False
                
                for line in lines:
                    if line.startswith("REACT_APP_BACKEND_URL="):
                        old_url = line.split("=", 1)[1] if "=" in line else ""
                        if old_url != ngrok_url:
                            updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}")
                            log_ngrok(f"Frontend .env: {old_url} → {ngrok_url}", "SUCCESS")
                        else:
                            updated_lines.append(line)
                        backend_url_updated = True
                    else:
                        updated_lines.append(line)
                
                if not backend_url_updated:
                    updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}")
                    log_ngrok(f"Frontend .env: REACT_APP_BACKEND_URL ajouté → {ngrok_url}", "SUCCESS")
                
                with open(frontend_env_path, "w", encoding='utf-8') as f:
                    f.write("\n".join(updated_lines))
                    if updated_lines:
                        f.write("\n")
                
                updated_files.append("frontend/.env")
                
            except Exception as e:
                log_ngrok(f"Erreur mise à jour frontend .env: {e}", "ERROR")
        else:
            log_ngrok(f"Fichier frontend .env non trouvé: {frontend_env_path}", "WARNING")
        
        # 2. Mettre à jour le .env backend (WEBHOOK_URL et PUBLIC_BASE_URL)
        if os.path.exists(backend_env_path):
            try:
                with open(backend_env_path, "r", encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.splitlines()
                updated_lines = []
                webhook_url_updated = False
                public_base_url_updated = False
                
                for line in lines:
                    if line.startswith("WEBHOOK_URL="):
                        old_url = line.split("=", 1)[1] if "=" in line else ""
                        if old_url != ngrok_url:
                            updated_lines.append(f"WEBHOOK_URL={ngrok_url}")
                            log_ngrok(f"Backend .env WEBHOOK_URL: {old_url} → {ngrok_url}", "SUCCESS")
                        else:
                            updated_lines.append(line)
                        webhook_url_updated = True
                    elif line.startswith("PUBLIC_BASE_URL="):
                        old_url = line.split("=", 1)[1] if "=" in line else ""
                        if old_url != ngrok_url:
                            updated_lines.append(f"PUBLIC_BASE_URL={ngrok_url}")
                            log_ngrok(f"Backend .env PUBLIC_BASE_URL: {old_url} → {ngrok_url}", "SUCCESS")
                        else:
                            updated_lines.append(line)
                        public_base_url_updated = True
                    else:
                        updated_lines.append(line)
                
                # Ajouter les variables si elles n'existent pas
                if not webhook_url_updated:
                    updated_lines.append(f"WEBHOOK_URL={ngrok_url}")
                    log_ngrok(f"Backend .env: WEBHOOK_URL ajouté → {ngrok_url}", "SUCCESS")
                
                if not public_base_url_updated:
                    updated_lines.append(f"PUBLIC_BASE_URL={ngrok_url}")
                    log_ngrok(f"Backend .env: PUBLIC_BASE_URL ajouté → {ngrok_url}", "SUCCESS")
                
                with open(backend_env_path, "w", encoding='utf-8') as f:
                    f.write("\n".join(updated_lines))
                    if updated_lines:
                        f.write("\n")
                
                updated_files.append("backend/.env")
                
            except Exception as e:
                log_ngrok(f"Erreur mise à jour backend .env: {e}", "ERROR")
        else:
            log_ngrok(f"Fichier backend .env non trouvé: {backend_env_path}", "WARNING")
        
        if updated_files:
            log_ngrok(f"✅ Fichiers .env mis à jour: {', '.join(updated_files)}", "SUCCESS")
            log_ngrok("🎯 server.py récupérera automatiquement la nouvelle URL", "SUCCESS")
            return True
        else:
            log_ngrok("⚠️ Aucun fichier .env mis à jour", "WARNING")
            return False
            
    except Exception as e:
        log_ngrok(f"❌ Erreur générale mise à jour .env: {e}", "ERROR")
        return False

def start_ngrok_tunnel(port=8001):
    """Démarrer le tunnel ngrok de manière stable"""
    try:
        log_ngrok("🚀 DÉMARRAGE NGROK STANDALONE", "START")
        log_ngrok("=" * 50, "INFO")
        
        # Vérifier si ngrok est déjà actif
        existing_url = check_ngrok_running()
        if existing_url:
            log_ngrok("Ngrok déjà en cours, utilisation de l'URL existante", "INFO")
            # Même pour une URL existante, s'assurer que les .env sont à jour
            update_env_files_with_ngrok_url(existing_url)
            return existing_url
        
        # Nettoyer les processus existants
        kill_existing_ngrok()
        
        # Configurer l'authentification
        configure_ngrok()
        
        # Démarrer ngrok
        log_ngrok(f"Démarrage tunnel ngrok sur port {port}...", "INFO")
        
        # Créer un processus ngrok détaché
        ngrok_cmd = ["ngrok", "http", str(port), "--log=stdout", "--log-level=info"]
        
        if os.name == 'nt':  # Windows
            # Créer une nouvelle console pour ngrok
            process = subprocess.Popen(
                ngrok_cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        else:  # Linux
            process = subprocess.Popen(
                ngrok_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        
        log_ngrok(f"Processus ngrok lancé (PID: {process.pid})", "SUCCESS")
        
        # Attendre que ngrok démarre
        log_ngrok("Attente du démarrage ngrok...", "INFO")
        max_attempts = 15
        
        for attempt in range(max_attempts):
            time.sleep(2)
            
            # Vérifier que le processus est toujours en vie
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                log_ngrok(f"Processus ngrok arrêté prématurément", "ERROR")
                if stderr:
                    log_ngrok(f"Erreur: {stderr[:200]}", "ERROR")
                return None
            
            # Essayer de récupérer l'URL
            try:
                response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=3)
                if response.status_code == 200:
                    tunnels = response.json().get('tunnels', [])
                    if tunnels:
                        url = tunnels[0]['public_url']
                        log_ngrok(f"🎯 URL NGROK STABLE: {url}", "SUCCESS")
                        
                        # Sauvegarder l'URL dans le fichier
                        try:
                            with open("ngrok_url.txt", "w") as f:
                                f.write(url)
                            log_ngrok("URL sauvegardée dans ngrok_url.txt", "SUCCESS")
                        except Exception as e:
                            log_ngrok(f"Erreur sauvegarde URL: {e}", "WARNING")
                        
                        # NOUVELLE FONCTIONNALITÉ: Mise à jour automatique des fichiers .env
                        env_update_success = update_env_files_with_ngrok_url(url)
                        if env_update_success:
                            log_ngrok("✅ Les fichiers .env ont été mis à jour automatiquement", "SUCCESS")
                            log_ngrok("🔄 server.py utilisera maintenant la nouvelle URL ngrok", "SUCCESS")
                        else:
                            log_ngrok("⚠️ Mise à jour partielle des fichiers .env", "WARNING")
                        
                        # Afficher les instructions de configuration Facebook
                        domain = url.replace("https://", "").replace("http://", "")
                        
                        log_ngrok("=" * 50, "INFO")
                        log_ngrok("📋 CONFIGURATION FACEBOOK REQUISE:", "INFO")
                        log_ngrok(f"1. App Domains: {domain}", "INFO")
                        log_ngrok(f"2. OAuth Redirect URIs: {url}/auth/callback", "INFO")
                        log_ngrok(f"3. Webhooks: {url}/api/webhook", "INFO")
                        log_ngrok("=" * 50, "INFO")
                        log_ngrok("✅ PROBLÈME RÉSOLU: server.py récupère maintenant l'URL ngrok active", "SUCCESS")
                        log_ngrok("🎯 Les fichiers .env ont été synchronisés automatiquement", "SUCCESS")
                        
                        return url
            except requests.exceptions.ConnectionError:
                log_ngrok(f"Tentative {attempt + 1}/{max_attempts}: API ngrok non accessible", "INFO")
            except Exception as e:
                log_ngrok(f"Tentative {attempt + 1}/{max_attempts}: {e}", "INFO")
        
        log_ngrok("Échec du démarrage ngrok après plusieurs tentatives", "ERROR")
        return None
        
    except Exception as e:
        log_ngrok(f"Erreur critique ngrok: {e}", "ERROR")
        return None

def monitor_ngrok():
    """Surveiller ngrok et redémarrer si nécessaire"""
    log_ngrok("🔍 Mode surveillance ngrok activé", "INFO")
    log_ngrok("Appuyez sur Ctrl+C pour arrêter", "INFO")
    
    try:
        while True:
            time.sleep(30)  # Vérifier toutes les 30 secondes
            
            current_url = check_ngrok_running()
            if not current_url:
                log_ngrok("Ngrok s'est arrêté, redémarrage...", "WARNING")
                new_url = start_ngrok_tunnel()
                if new_url:
                    log_ngrok(f"Ngrok redémarré avec nouvelle URL: {new_url}", "SUCCESS")
                else:
                    log_ngrok("Échec redémarrage ngrok", "ERROR")
                    break
            
    except KeyboardInterrupt:
        log_ngrok("Arrêt demandé par l'utilisateur", "INFO")
    except Exception as e:
        log_ngrok(f"Erreur surveillance: {e}", "ERROR")

def main():
    """Fonction principale"""
    try:
        log_ngrok("🚀 NGROK STANDALONE - DÉMARRAGE", "START")
        
        # Variable globale pour éviter les appels récursifs
        global _cleanup_in_progress
        _cleanup_in_progress = False
        
        # Gestion des signaux pour arrêt propre
        def signal_handler(sig, frame):
            global _cleanup_in_progress
            if _cleanup_in_progress:
                return
            _cleanup_in_progress = True
            log_ngrok("Signal d'arrêt reçu, nettoyage...", "INFO")
            try:
                kill_existing_ngrok()
            except:
                pass
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Démarrer ngrok
        url = start_ngrok_tunnel()
        
        if url:
            log_ngrok(f"✅ NGROK PRÊT: {url}", "SUCCESS")
            log_ngrok("💡 Vous pouvez maintenant démarrer le serveur dans une autre fenêtre", "INFO")
            
            # Mode surveillance optionnel
            if "--monitor" in sys.argv:
                monitor_ngrok()
            else:
                log_ngrok("Mode standalone - laissez cette fenêtre ouverte", "INFO")
                log_ngrok("Ajoutez --monitor pour surveillance automatique", "INFO")
                
                # Attendre indéfiniment
                try:
                    while True:
                        time.sleep(60)
                except KeyboardInterrupt:
                    log_ngrok("Arrêt demandé", "INFO")
        else:
            log_ngrok("❌ ÉCHEC DÉMARRAGE NGROK", "ERROR")
            sys.exit(1)
            
    except Exception as e:
        log_ngrok(f"Erreur fatale: {e}", "ERROR")
        sys.exit(1)
    finally:
        kill_existing_ngrok()

if __name__ == "__main__":
    main()