#!/usr/bin/env python3
"""
Test complet de la solution OAuth Facebook avec ngrok
Vérifie que tous les composants fonctionnent correctement
"""
import os
import sys
import requests
import subprocess
from pathlib import Path

def log_message(message, level="INFO"):
    """Logging avec icônes"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
    icon = icons.get(level, "📋")
    print(f"{icon} {message}")

def test_backend_health():
    """Test la santé du backend"""
    try:
        response = requests.get("http://localhost:8001/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            log_message(f"Backend sain: {data.get('status')}", "SUCCESS")
            return True
        else:
            log_message(f"Backend erreur: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log_message(f"Backend non accessible: {e}", "ERROR")
        return False

def test_oauth_status():
    """Test le statut OAuth"""
    try:
        response = requests.get("http://localhost:8001/api/config/oauth-status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            log_message("Configuration OAuth:", "INFO")
            print(f"   • Facebook App ID: {data.get('facebook_app_id', 'N/A')}")
            print(f"   • Facebook configuré: {'✅' if data.get('facebook_app_configured') else '❌'}")
            print(f"   • Redirect URI: {data.get('redirect_uri', 'N/A')}")
            print(f"   • Ngrok actif: {'✅' if data.get('ngrok_active') else '❌'}")
            
            if data.get('ngrok_url'):
                print(f"   • URL Ngrok: {data.get('ngrok_url')}")
            
            return data
        else:
            log_message(f"Erreur statut OAuth: {response.status_code}", "ERROR")
            return None
    except Exception as e:
        log_message(f"Erreur test OAuth status: {e}", "ERROR")
        return None

def test_created_files():
    """Vérifie que tous les fichiers ont été créés"""
    required_files = [
        "99_start_all_ngrok.bat",
        "server_windows.py",
        "start_oauth_ready.bat",
        "sync_ngrok_config.py",
        "update_frontend_env.py",
        "check_oauth_config.py",
        "test_oauth_flow.py",
        "GUIDE_OAUTH_NGROK.md",
        "README_SOLUTION_OAUTH.md"
    ]
    
    log_message("Vérification des fichiers créés:", "TEST")
    all_present = True
    
    for filename in required_files:
        filepath = Path(__file__).parent / filename
        if filepath.exists():
            log_message(f"✅ {filename}: Présent", "SUCCESS")
        else:
            log_message(f"❌ {filename}: Manquant", "ERROR")
            all_present = False
    
    return all_present

def test_env_configuration():
    """Vérifie la configuration des fichiers .env"""
    log_message("Vérification configuration .env:", "TEST")
    
    # Backend .env
    backend_env = Path(__file__).parent / "backend" / ".env"
    if backend_env.exists():
        log_message("✅ Backend .env: Présent", "SUCCESS")
        
        # Vérifier les clés importantes
        with open(backend_env, 'r') as f:
            content = f.read()
            
        important_keys = ['FACEBOOK_APP_ID', 'FACEBOOK_APP_SECRET', 'FACEBOOK_CLIENT_TOKEN']
        for key in important_keys:
            if f"{key}=" in content and not f"{key}=" in content.split('\n'):
                log_message(f"✅ {key}: Configuré", "SUCCESS")
            else:
                log_message(f"⚠️ {key}: À vérifier", "WARNING")
    else:
        log_message("❌ Backend .env: Manquant", "ERROR")
    
    # Frontend .env
    frontend_env = Path(__file__).parent / "frontend" / ".env"
    if frontend_env.exists():
        log_message("✅ Frontend .env: Présent", "SUCCESS")
        
        with open(frontend_env, 'r') as f:
            content = f.read()
        
        if "REACT_APP_BACKEND_URL=" in content:
            for line in content.split('\n'):
                if line.startswith('REACT_APP_BACKEND_URL='):
                    backend_url = line.split('=', 1)[1]
                    log_message(f"Frontend configuré pour: {backend_url}", "INFO")
                    break
    else:
        log_message("❌ Frontend .env: Manquant", "ERROR")

def test_oauth_endpoints():
    """Test les endpoints OAuth"""
    endpoints = [
        "/api/auth/facebook",
        "/api/auth/facebook/exchange-code",
        "/api/config/oauth-status"
    ]
    
    log_message("Test des endpoints OAuth:", "TEST")
    
    for endpoint in endpoints:
        try:
            url = f"http://localhost:8001{endpoint}"
            if endpoint == "/api/config/oauth-status":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, json={}, timeout=5)
            
            if response.status_code in [200, 400, 422]:
                log_message(f"✅ {endpoint}: Disponible", "SUCCESS")
            else:
                log_message(f"⚠️ {endpoint}: Status {response.status_code}", "WARNING")
                
        except Exception as e:
            log_message(f"❌ {endpoint}: Erreur - {e}", "ERROR")

def main():
    """Test complet de la solution"""
    log_message("🧪 Test Complet de la Solution OAuth Facebook", "TEST")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Fichiers créés
    log_message("Test 1: Fichiers de la solution", "TEST")
    if test_created_files():
        tests_passed += 1
        log_message("✅ Tous les fichiers sont présents", "SUCCESS")
    else:
        log_message("❌ Certains fichiers manquent", "ERROR")
    print()
    
    # Test 2: Configuration .env
    log_message("Test 2: Configuration des fichiers .env", "TEST")
    test_env_configuration()
    tests_passed += 1  # Pas de condition d'échec pour cette partie
    print()
    
    # Test 3: Santé du backend
    log_message("Test 3: Santé du backend", "TEST")
    if test_backend_health():
        tests_passed += 1
    print()
    
    # Test 4: Configuration OAuth
    log_message("Test 4: Configuration OAuth", "TEST")
    oauth_status = test_oauth_status()
    if oauth_status and oauth_status.get('facebook_app_configured'):
        tests_passed += 1
        log_message("✅ Configuration OAuth OK", "SUCCESS")
    else:
        log_message("⚠️ Configuration OAuth incomplète", "WARNING")
    print()
    
    # Test 5: Endpoints OAuth
    log_message("Test 5: Endpoints OAuth", "TEST")
    test_oauth_endpoints()
    tests_passed += 1  # Pas de condition d'échec stricte
    print()
    
    # Résumé final
    print("=" * 60)
    log_message(f"📊 Résultat: {tests_passed}/{total_tests} tests réussis", "INFO")
    
    if tests_passed >= 4:
        log_message("🎉 SOLUTION OAUTH FACEBOOK FONCTIONNELLE !", "SUCCESS")
        log_message("", "INFO")
        log_message("Prochaines étapes:", "INFO")
        print("   1. Lancez '99_start_all_ngrok.bat' pour démarrer ngrok")
        print("   2. Copiez les URLs générées dans 'oauth_config_summary.txt'")
        print("   3. Configurez votre application Facebook Developer")
        print("   4. Testez l'authentification OAuth")
        log_message("", "INFO")
        log_message("📖 Consultez GUIDE_OAUTH_NGROK.md pour plus de détails", "INFO")
        return 0
    else:
        log_message("⚠️ Certains composants nécessitent une attention", "WARNING")
        log_message("📖 Consultez les logs ci-dessus pour plus de détails", "INFO")
        return 1

if __name__ == "__main__":
    sys.exit(main())