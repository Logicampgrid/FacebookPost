#!/usr/bin/env python3
"""
Script de vérification de la configuration OAuth Facebook
Vérifie que toutes les URLs sont correctement configurées
"""
import os
import sys
import requests
from pathlib import Path
from datetime import datetime

def log_message(message, level="INFO"):
    """Logging avec icônes"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "CHECK": "🔍"}
    icon = icons.get(level, "📋")
    print(f"{icon} {message}")

def check_ngrok_status():
    """Vérifie le statut de ngrok"""
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            tunnels = response.json().get('tunnels', [])
            if tunnels:
                tunnel = tunnels[0]
                public_url = tunnel.get('public_url')
                log_message(f"Ngrok actif: {public_url}", "SUCCESS")
                return public_url
            else:
                log_message("Ngrok démarré mais aucun tunnel actif", "WARNING")
                return None
        else:
            log_message(f"Ngrok API erreur: {response.status_code}", "WARNING")
            return None
    except:
        log_message("Ngrok non accessible", "ERROR")
        return None

def check_frontend_config():
    """Vérifie la configuration du frontend"""
    try:
        frontend_env = Path(__file__).parent / "frontend" / ".env"
        if not frontend_env.exists():
            log_message("Fichier .env frontend manquant", "ERROR")
            return None
        
        with open(frontend_env, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for line in content.split('\n'):
            if line.startswith('REACT_APP_BACKEND_URL='):
                backend_url = line.split('=', 1)[1].strip()
                log_message(f"Frontend configuré pour: {backend_url}", "INFO")
                return backend_url
        
        log_message("REACT_APP_BACKEND_URL non trouvé dans .env", "WARNING")
        return None
        
    except Exception as e:
        log_message(f"Erreur lecture .env frontend: {e}", "ERROR")
        return None

def check_backend_config():
    """Vérifie la configuration du backend"""
    try:
        backend_env = Path(__file__).parent / "backend" / ".env"
        if not backend_env.exists():
            log_message("Fichier .env backend manquant", "ERROR")
            return {}
        
        config = {}
        with open(backend_env, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value
        
        # Vérifier les clés importantes
        important_keys = [
            'FACEBOOK_APP_ID',
            'FACEBOOK_APP_SECRET',
            'FACEBOOK_CLIENT_TOKEN'
        ]
        
        for key in important_keys:
            if key in config and config[key]:
                log_message(f"{key}: ✓ Configuré", "SUCCESS")
            else:
                log_message(f"{key}: ✗ Manquant", "ERROR")
        
        return config
        
    except Exception as e:
        log_message(f"Erreur lecture .env backend: {e}", "ERROR")
        return {}

def check_backend_health(url):
    """Vérifie la santé du backend"""
    try:
        health_url = f"{url}/api/health"
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            log_message(f"Backend accessible: {health_url}", "SUCCESS")
            return True
        else:
            log_message(f"Backend erreur {response.status_code}: {health_url}", "ERROR")
            return False
    except Exception as e:
        log_message(f"Backend non accessible: {e}", "ERROR")
        return False

def check_oauth_endpoints(base_url):
    """Vérifie les endpoints OAuth"""
    endpoints = [
        "/api/auth/facebook",
        "/api/auth/facebook/exchange-code"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            # Pour les endpoints POST, on s'attend à une erreur 400 ou 422 si les paramètres manquent
            response = requests.post(url, json={}, timeout=5)
            if response.status_code in [400, 422, 200]:
                log_message(f"Endpoint OAuth disponible: {endpoint}", "SUCCESS")
            else:
                log_message(f"Endpoint OAuth erreur {response.status_code}: {endpoint}", "WARNING")
        except Exception as e:
            log_message(f"Endpoint OAuth non accessible: {endpoint} - {e}", "ERROR")

def generate_oauth_urls(base_url, facebook_app_id):
    """Génère les URLs OAuth pour Facebook"""
    if not facebook_app_id:
        log_message("FACEBOOK_APP_ID manquant, impossible de générer les URLs OAuth", "ERROR")
        return
    
    log_message("🔗 URLs à configurer dans Facebook Developer:", "INFO")
    print(f"   • Valid OAuth Redirect URIs: {base_url}/")
    print(f"   • Webhook URL: {base_url}/webhook/facebook")
    print(f"   • Auth URL: https://www.facebook.com/v18.0/dialog/oauth?client_id={facebook_app_id}&redirect_uri={base_url}/&scope=pages_show_list,pages_read_engagement,instagram_basic,instagram_content_publish")

def main():
    """Point d'entrée principal"""
    log_message("🔍 Vérification de la configuration OAuth Facebook", "CHECK")
    print("=" * 60)
    
    # 1. Vérifier ngrok
    log_message("1. Vérification de ngrok...", "CHECK")
    ngrok_url = check_ngrok_status()
    
    # 2. Vérifier la configuration frontend
    log_message("2. Vérification configuration frontend...", "CHECK")
    frontend_url = check_frontend_config()
    
    # 3. Vérifier la configuration backend
    log_message("3. Vérification configuration backend...", "CHECK")
    backend_config = check_backend_config()
    
    # 4. Déterminer l'URL de base à utiliser
    base_url = ngrok_url or frontend_url or "http://localhost:8001"
    log_message(f"URL de base détectée: {base_url}", "INFO")
    
    # 5. Vérifier la santé du backend
    log_message("4. Vérification santé backend...", "CHECK")
    backend_healthy = check_backend_health(base_url)
    
    # 6. Vérifier les endpoints OAuth
    if backend_healthy:
        log_message("5. Vérification endpoints OAuth...", "CHECK")
        check_oauth_endpoints(base_url)
    
    # 7. Générer les URLs OAuth
    log_message("6. Génération des URLs OAuth...", "CHECK")
    facebook_app_id = backend_config.get('FACEBOOK_APP_ID')
    generate_oauth_urls(base_url, facebook_app_id)
    
    # Résumé final
    print("=" * 60)
    log_message("📋 Résumé de la configuration:", "INFO")
    
    issues = []
    if not ngrok_url:
        issues.append("Ngrok non actif")
    if not backend_healthy:
        issues.append("Backend non accessible")
    if not facebook_app_id:
        issues.append("FACEBOOK_APP_ID manquant")
    
    if not issues:
        log_message("✅ Configuration OAuth complète et fonctionnelle!", "SUCCESS")
        log_message(f"🌐 Application prête sur: {base_url}", "SUCCESS")
        return 0
    else:
        log_message(f"⚠️ Problèmes détectés: {', '.join(issues)}", "WARNING")
        log_message("💡 Résolvez ces problèmes avant de tester l'OAuth", "INFO")
        return 1

if __name__ == "__main__":
    sys.exit(main())