#!/usr/bin/env python3
"""
Script de validation de la solution OAuth Facebook
Teste tous les composants de la solution automatique
"""

import os
import sys
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def print_step(step, message):
    """Afficher une étape avec formatage"""
    print(f"\n[{step}] {message}")
    print("=" * (len(message) + 6))

def print_result(success, message):
    """Afficher un résultat avec icône"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def test_facebook_config():
    """Tester la configuration Facebook"""
    print_step("1", "Vérification de la configuration Facebook")
    
    app_id = os.getenv("FACEBOOK_APP_ID")
    app_secret = os.getenv("FACEBOOK_APP_SECRET") 
    client_token = os.getenv("FACEBOOK_CLIENT_TOKEN")
    
    config_ok = all([app_id, app_secret, client_token])
    
    print_result(config_ok, f"Configuration Facebook: {'Complète' if config_ok else 'Incomplète'}")
    
    if config_ok:
        print(f"   • APP_ID: {app_id}")
        print(f"   • APP_SECRET: ***{app_secret[-4:]}")
        print(f"   • CLIENT_TOKEN: ***{client_token[-4:]}")
    
    return config_ok

def test_ngrok_api():
    """Tester l'accès à l'API ngrok"""
    print_step("2", "Test de l'API ngrok")
    
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            
            if tunnels:
                tunnel = tunnels[0]
                public_url = tunnel.get('public_url')
                print_result(True, f"Ngrok actif: {public_url}")
                return public_url
            else:
                print_result(False, "Aucun tunnel ngrok actif")
                return None
        else:
            print_result(False, f"API ngrok inaccessible (status: {response.status_code})")
            return None
            
    except requests.exceptions.RequestException as e:
        print_result(False, f"Erreur connexion API ngrok: {e}")
        return None

def test_backend_health(ngrok_url):
    """Tester la santé du backend"""
    print_step("3", "Test du backend FastAPI")
    
    if not ngrok_url:
        print_result(False, "Pas d'URL ngrok - test backend ignoré")
        return False
    
    try:
        health_url = f"{ngrok_url}/api/health"
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Backend accessible via ngrok")
            print(f"   • URL: {health_url}")
            print(f"   • Status: {data.get('status', 'unknown')}")
            return True
        else:
            print_result(False, f"Backend inaccessible (status: {response.status_code})")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, f"Erreur connexion backend: {e}")
        return False

def test_facebook_oauth_config(ngrok_url):
    """Tester la mise à jour Facebook OAuth"""
    print_step("4", "Test de la configuration Facebook OAuth")
    
    if not ngrok_url:
        print_result(False, "Pas d'URL ngrok - test OAuth ignoré")
        return False
    
    app_id = os.getenv("FACEBOOK_APP_ID")
    app_secret = os.getenv("FACEBOOK_APP_SECRET")
    
    if not app_id or not app_secret:
        print_result(False, "Configuration Facebook manquante")
        return False
    
    try:
        # Générer token d'accès app
        app_access_token = f"{app_id}|{app_secret}"
        
        # Tester la mise à jour d'un paramètre (website_url)
        url = f"https://graph.facebook.com/v18.0/{app_id}"
        data = {
            "website_url": ngrok_url,
            "access_token": app_access_token
        }
        
        response = requests.post(url, data=data, timeout=15)
        
        if response.status_code == 200:
            print_result(True, "Mise à jour Facebook OAuth réussie")
            print(f"   • URL configurée: {ngrok_url}")
            
            # Vérifier la configuration actuelle
            verify_url = f"https://graph.facebook.com/v18.0/{app_id}?fields=website_url,app_domains&access_token={app_access_token}"
            verify_response = requests.get(verify_url, timeout=10)
            
            if verify_response.status_code == 200:
                config = verify_response.json()
                print(f"   • Website URL: {config.get('website_url', 'Non définie')}")
                print(f"   • App domains: {config.get('app_domains', 'Non définies')}")
            
            return True
        else:
            error_data = response.text
            print_result(False, f"Erreur mise à jour Facebook (status: {response.status_code})")
            print(f"   • Détails: {error_data[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, f"Erreur requête Facebook: {e}")
        return False

def test_frontend_env():
    """Tester la configuration frontend"""
    print_step("5", "Vérification du frontend .env")
    
    frontend_env_path = Path(__file__).parent / "frontend" / ".env"
    
    if not frontend_env_path.exists():
        print_result(False, f"Fichier .env frontend non trouvé: {frontend_env_path}")
        return False
    
    try:
        with open(frontend_env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Chercher REACT_APP_BACKEND_URL
        backend_url = None
        for line in content.split('\n'):
            if line.startswith('REACT_APP_BACKEND_URL='):
                backend_url = line.split('=', 1)[1].strip()
                break
        
        if backend_url:
            is_ngrok = 'ngrok' in backend_url
            print_result(True, f"Frontend .env configuré")
            print(f"   • REACT_APP_BACKEND_URL: {backend_url}")
            print(f"   • Type: {'Ngrok' if is_ngrok else 'Local/Autre'}")
            return True
        else:
            print_result(False, "REACT_APP_BACKEND_URL non trouvé dans .env")
            return False
            
    except Exception as e:
        print_result(False, f"Erreur lecture frontend .env: {e}")
        return False

def main():
    """Fonction principale de validation"""
    print("🔍 VALIDATION DE LA SOLUTION OAUTH FACEBOOK")
    print("=" * 50)
    
    # Tests séquentiels
    results = []
    
    # Test 1: Configuration Facebook
    results.append(test_facebook_config())
    
    # Test 2: API Ngrok
    ngrok_url = test_ngrok_api()
    results.append(ngrok_url is not None)
    
    # Test 3: Backend health
    results.append(test_backend_health(ngrok_url))
    
    # Test 4: Facebook OAuth
    results.append(test_facebook_oauth_config(ngrok_url))
    
    # Test 5: Frontend env
    results.append(test_frontend_env())
    
    # Résultat final
    print_step("RÉSULTAT", "Bilan de la validation")
    
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100
    
    overall_success = passed == total
    print_result(overall_success, f"Tests réussis: {passed}/{total} ({success_rate:.0f}%)")
    
    if overall_success:
        print("\n🎉 SOLUTION OAUTH FACEBOOK ENTIÈREMENT FONCTIONNELLE")
        print("✅ L'authentification Facebook devrait maintenant fonctionner parfaitement")
    else:
        print("\n⚠️ SOLUTION PARTIELLEMENT FONCTIONNELLE")
        print("💡 Vérifiez les points en échec ci-dessus")
    
    print(f"\n🌐 URL de test: {ngrok_url if ngrok_url else 'Non disponible'}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)