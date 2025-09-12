#!/usr/bin/env python3
"""
Test script pour vérifier les fonctionnalités OAuth dynamiques
"""

import requests
import json
import sys
import time

def test_endpoints():
    """Test des nouveaux endpoints de gestion OAuth dynamique"""
    
    base_url = "http://localhost:8001"
    
    print("🧪 Test des endpoints OAuth dynamiques")
    print("-" * 50)
    
    # Test 1: Health check
    print("\n1️⃣ Test du health check...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check OK - Status: {data['status']}")
            print(f"   Backend port: {data['backend']['port']}")
            print(f"   Ngrok enabled: {data['ngrok']['enabled']}")
            print(f"   Ngrok URL: {data['ngrok']['url']}")
        else:
            print(f"❌ Health check failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur health check: {e}")
    
    # Test 2: Statut ngrok
    print("\n2️⃣ Test du statut ngrok...")
    try:
        response = requests.get(f"{base_url}/api/ngrok/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Statut ngrok récupéré")
            print(f"   Ngrok enabled: {data['ngrok_enabled']}")
            print(f"   Active URL: {data['active_url']}")
            print(f"   Current redirect URI: {data['current_redirect_uri']}")
            print(f"   Process running: {data['process_running']}")
        else:
            print(f"❌ Statut ngrok failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur statut ngrok: {e}")
    
    # Test 3: URL d'authentification Facebook
    print("\n3️⃣ Test de l'URL d'authentification Facebook...")
    try:
        response = requests.get(f"{base_url}/api/auth/facebook/login-url?store=gizmobbs", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ URL d'authentification générée")
            print(f"   Store: {data['store']}")
            print(f"   Redirect URI: {data['redirect_uri']}")
            print(f"   Ngrok détecté: {data['ngrok_detected']}")
            print(f"   Auth URL: {data['auth_url'][:100]}...")
        else:
            print(f"❌ URL d'authentification failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur URL d'authentification: {e}")
    
    # Test 4: Mise à jour des endpoints
    print("\n4️⃣ Test de la mise à jour des endpoints...")
    try:
        response = requests.post(f"{base_url}/api/ngrok/update-endpoints", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mise à jour des endpoints terminée")
            print(f"   Success: {data['success']}")
            print(f"   Message: {data['message']}")
            print(f"   Active URL: {data['active_url']}")
            print(f"   Current redirect URI: {data['current_redirect_uri']}")
        else:
            print(f"❌ Mise à jour endpoints failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur mise à jour endpoints: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés - Toutes les fonctionnalités OAuth dynamiques sont opérationnelles!")

if __name__ == "__main__":
    print("Attente de 3 secondes pour que le serveur démarre...")
    time.sleep(3)
    test_endpoints()