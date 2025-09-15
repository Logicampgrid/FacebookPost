#!/usr/bin/env python3
"""
Script de test pour vérifier les corrections des redirect_uri Facebook
"""

import requests
import json
import os
import sys
from dotenv import load_dotenv

# Ajouter le chemin du backend
sys.path.append('/app/backend')
from server import (
    get_active_ngrok_url, 
    build_dynamic_redirect_uri,
    update_facebook_endpoints_with_ngrok,
    FACEBOOK_APP_ID,
    FACEBOOK_APP_SECRET
)

def test_ngrok_detection():
    """Test de détection de l'URL ngrok"""
    print("🔍 Test de détection ngrok...")
    
    try:
        # Test 1: Via l'API ngrok
        ngrok_url = get_active_ngrok_url()
        if ngrok_url:
            print(f"✅ URL ngrok détectée via API: {ngrok_url}")
            return ngrok_url
        else:
            print("⚠️ Aucune URL ngrok détectée via API")
    except Exception as e:
        print(f"❌ Erreur détection ngrok API: {e}")
    
    # Test 2: Via le fichier ngrok_url.txt
    try:
        ngrok_file = '/app/backend/ngrok_url.txt'
        if os.path.exists(ngrok_file):
            with open(ngrok_file, 'r') as f:
                file_url = f.read().strip()
                if file_url:
                    print(f"✅ URL ngrok détectée via fichier: {file_url}")
                    return file_url
    except Exception as e:
        print(f"❌ Erreur lecture fichier ngrok: {e}")
    
    print("❌ Aucune URL ngrok disponible")
    return None

def test_dynamic_redirect_uri():
    """Test de construction dynamique des redirect_uri"""
    print("\n🎯 Test de construction redirect_uri...")
    
    try:
        # Test avec différents callbacks
        callbacks = ["/auth/callback", "/auth/facebook", "/oauth/callback"]
        
        for callback in callbacks:
            redirect_uri = build_dynamic_redirect_uri(callback)
            print(f"✅ Callback '{callback}' -> {redirect_uri}")
            
            # Vérifier qu'on n'utilise pas localhost
            if "localhost" in redirect_uri:
                print(f"⚠️ ATTENTION: localhost détecté dans {redirect_uri}")
            else:
                print(f"✅ OK: pas de localhost dans {redirect_uri}")
    
    except Exception as e:
        print(f"❌ Erreur construction redirect_uri: {e}")

def test_facebook_config():
    """Test de la configuration Facebook"""
    print(f"\n🔧 Test configuration Facebook...")
    
    print(f"FACEBOOK_APP_ID: {FACEBOOK_APP_ID}")
    print(f"FACEBOOK_APP_SECRET: {'***' + FACEBOOK_APP_SECRET[-4:] if FACEBOOK_APP_SECRET else 'Non défini'}")
    
    if not FACEBOOK_APP_ID or not FACEBOOK_APP_SECRET:
        print("❌ Configuration Facebook incomplète")
        return False
    
    print("✅ Configuration Facebook OK")
    return True

def test_server_health():
    """Test de santé du serveur"""
    print(f"\n🏥 Test de santé du serveur...")
    
    try:
        response = requests.get("http://127.0.0.1:8001/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Serveur backend accessible")
            return True
        else:
            print(f"⚠️ Serveur répond avec status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Serveur backend non accessible")
    except Exception as e:
        print(f"❌ Erreur test serveur: {e}")
    
    return False

def test_facebook_oauth_simulation():
    """Simulation d'un test OAuth Facebook"""
    print(f"\n🔐 Simulation test Facebook OAuth...")
    
    # Construire l'URL d'authentification Facebook
    ngrok_url = test_ngrok_detection()
    if not ngrok_url:
        print("❌ Impossible de tester OAuth sans URL ngrok")
        return
    
    redirect_uri = f"{ngrok_url}/auth/callback"
    auth_url = f"https://www.facebook.com/v18.0/dialog/oauth"
    
    params = {
        'client_id': FACEBOOK_APP_ID,
        'redirect_uri': redirect_uri,
        'scope': 'pages_manage_posts,pages_read_engagement,instagram_basic,instagram_content_publish',
        'response_type': 'code',
        'state': 'test_store'
    }
    
    auth_query = "&".join([f"{k}={v}" for k, v in params.items()])
    full_auth_url = f"{auth_url}?{auth_query}"
    
    print(f"✅ URL d'authentification Facebook générée:")
    print(f"   {full_auth_url}")
    print(f"✅ Redirect URI utilisée: {redirect_uri}")
    
    # Vérifier que le redirect_uri ne contient pas localhost
    if "localhost" in redirect_uri:
        print("❌ ERREUR: redirect_uri contient localhost - Facebook rejettera!")
    else:
        print("✅ OK: redirect_uri utilise ngrok - Facebook devrait accepter")

def main():
    """Fonction principale de test"""
    print("🚀 Test des corrections Facebook OAuth redirect_uri")
    print("=" * 60)
    
    # Charger l'environnement
    load_dotenv('/app/backend/.env')
    
    # Exécuter tous les tests
    test_server_health()
    test_facebook_config()
    test_ngrok_detection()
    test_dynamic_redirect_uri()
    test_facebook_oauth_simulation()
    
    print("\n" + "=" * 60)
    print("🎯 Test terminé!")
    
    # Instructions finales
    print("\n💡 Instructions pour tester Facebook OAuth:")
    print("1. Assurez-vous que ngrok est en cours d'exécution")
    print("2. Utilisez l'URL d'authentification générée ci-dessus")
    print("3. Vérifiez que l'URL ngrok est ajoutée dans les paramètres Facebook:")
    print("   - App Domains")
    print("   - Valid OAuth Redirect URIs")

if __name__ == "__main__":
    main()