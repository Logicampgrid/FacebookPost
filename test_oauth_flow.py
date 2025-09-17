#!/usr/bin/env python3
"""
Script de test du flow OAuth Facebook
Simule le processus d'authentification pour vérifier que tout fonctionne
"""
import requests
import json
import sys
from pathlib import Path
from urllib.parse import urlencode, parse_qs

def log_message(message, level="INFO"):
    """Logging avec icônes"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
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

def test_backend_health(base_url):
    """Test la santé du backend"""
    try:
        health_url = f"{base_url}/api/health"
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_message(f"Backend OK: {data.get('status')}", "SUCCESS")
            return True
        else:
            log_message(f"Backend erreur: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log_message(f"Backend non accessible: {e}", "ERROR")
        return False

def test_oauth_status(base_url):
    """Test le statut OAuth"""
    try:
        oauth_url = f"{base_url}/api/config/oauth-status"
        response = requests.get(oauth_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_message("Statut OAuth:", "INFO")
            print(f"   • Ngrok actif: {'✅' if data.get('ngrok_active') else '❌'}")
            print(f"   • URL ngrok: {data.get('ngrok_url', 'N/A')}")
            print(f"   • Facebook configuré: {'✅' if data.get('facebook_app_configured') else '❌'}")
            print(f"   • OAuth prêt: {'✅' if data.get('oauth_ready') else '❌'}")
            return data.get('oauth_ready', False)
        else:
            log_message(f"Erreur statut OAuth: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log_message(f"Erreur test OAuth: {e}", "ERROR")
        return False

def generate_facebook_auth_url(base_url, facebook_app_id):
    """Génère l'URL d'authentification Facebook"""
    if not facebook_app_id:
        log_message("FACEBOOK_APP_ID manquant", "ERROR")
        return None
    
    params = {
        'client_id': facebook_app_id,
        'redirect_uri': f"{base_url}/",
        'scope': 'pages_show_list,pages_read_engagement,instagram_basic,instagram_content_publish',
        'response_type': 'code',
        'state': 'test_oauth'
    }
    
    auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"
    return auth_url

def test_oauth_endpoints(base_url):
    """Test les endpoints OAuth"""
    endpoints = [
        ("/api/auth/facebook", "POST"),
        ("/api/auth/facebook/exchange-code", "POST")
    ]
    
    log_message("Test des endpoints OAuth:", "TEST")
    
    for endpoint, method in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            if method == "POST":
                response = requests.post(url, json={}, timeout=5)
            else:
                response = requests.get(url, timeout=5)
            
            # Pour les endpoints OAuth, on s'attend à des erreurs 400/422 sans les bons paramètres
            if response.status_code in [200, 400, 422]:
                log_message(f"Endpoint {endpoint}: ✅ Disponible", "SUCCESS")
            else:
                log_message(f"Endpoint {endpoint}: ❌ Erreur {response.status_code}", "ERROR")
                
        except Exception as e:
            log_message(f"Endpoint {endpoint}: ❌ Non accessible - {e}", "ERROR")

def read_facebook_config():
    """Lit la configuration Facebook depuis le .env"""
    try:
        backend_env = Path(__file__).parent / "backend" / ".env"
        if not backend_env.exists():
            return {}
        
        config = {}
        with open(backend_env, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value
        
        return config
    except:
        return {}

def main():
    """Point d'entrée principal"""
    log_message("🧪 Test du flow OAuth Facebook", "TEST")
    print("=" * 50)
    
    # 1. Récupérer l'URL ngrok
    log_message("1. Vérification de ngrok...", "INFO")
    ngrok_url = get_ngrok_url()
    if not ngrok_url:
        log_message("❌ Ngrok non actif - impossible de tester OAuth", "ERROR")
        return 1
    
    log_message(f"URL ngrok: {ngrok_url}", "SUCCESS")
    
    # 2. Test santé backend
    log_message("2. Test santé backend...", "INFO")
    if not test_backend_health(ngrok_url):
        log_message("❌ Backend non accessible", "ERROR")
        return 1
    
    # 3. Test statut OAuth
    log_message("3. Test statut OAuth...", "INFO")
    oauth_ready = test_oauth_status(ngrok_url)
    
    # 4. Test endpoints OAuth
    log_message("4. Test endpoints OAuth...", "INFO")
    test_oauth_endpoints(ngrok_url)
    
    # 5. Générer URL d'authentification
    log_message("5. Génération URL d'authentification...", "INFO")
    facebook_config = read_facebook_config()
    facebook_app_id = facebook_config.get('FACEBOOK_APP_ID')
    
    if facebook_app_id:
        auth_url = generate_facebook_auth_url(ngrok_url, facebook_app_id)
        if auth_url:
            log_message("URL d'authentification Facebook:", "SUCCESS")
            print(f"   {auth_url}")
            print()
            log_message("💡 Copiez cette URL dans votre navigateur pour tester l'OAuth", "INFO")
    else:
        log_message("FACEBOOK_APP_ID manquant - impossible de générer l'URL d'auth", "ERROR")
    
    # Résumé final
    print("=" * 50)
    log_message("📋 Résumé du test:", "INFO")
    
    if oauth_ready and facebook_app_id:
        log_message("✅ OAuth Facebook prêt pour les tests!", "SUCCESS")
        log_message(f"🌐 Application: {ngrok_url}", "SUCCESS")
        log_message("💡 Configurez Facebook Developer avec les URLs ci-dessus", "INFO")
        return 0
    else:
        issues = []
        if not oauth_ready:
            issues.append("Configuration OAuth incomplète")
        if not facebook_app_id:
            issues.append("FACEBOOK_APP_ID manquant")
        
        log_message(f"⚠️ Problèmes: {', '.join(issues)}", "WARNING")
        return 1

if __name__ == "__main__":
    sys.exit(main())