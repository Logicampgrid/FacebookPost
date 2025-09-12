#!/usr/bin/env python3
"""
Test complet de l'implémentation OAuth dynamique avec ngrok
"""

import requests
import json
import sys
import time

def test_complete_implementation():
    """Test complet de toutes les fonctionnalités implémentées"""
    
    base_url = "http://localhost:8001"
    
    print("🎯 TEST COMPLET DE L'IMPLÉMENTATION OAUTH DYNAMIQUE")
    print("=" * 70)
    
    tests_passed = 0
    tests_total = 6
    
    # Test 1: Détection de l'URL ngrok active
    print("\n1️⃣ Test de détection de l'URL ngrok active...")
    try:
        response = requests.get(f"{base_url}/api/ngrok/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['ngrok_enabled'] and data['active_url']:
                print(f"✅ URL ngrok active détectée: {data['active_url']}")
                print(f"   Redirect URI dynamique: {data['current_redirect_uri']}")
                tests_passed += 1
                ngrok_url = data['active_url']
            else:
                print("❌ Ngrok non activé ou URL non trouvée")
        else:
            print(f"❌ Erreur API ngrok status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test ngrok: {e}")
    
    # Test 2: Génération d'URL d'authentification avec URI dynamique
    print("\n2️⃣ Test de génération d'URL d'authentification Facebook...")
    try:
        response = requests.get(f"{base_url}/api/auth/facebook/login-url?store=gizmobbs", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['success'] and data['ngrok_detected']:
                print(f"✅ URL d'authentification générée avec succès")
                print(f"   Store: {data['store']}")
                print(f"   Ngrok détecté: {data['ngrok_detected']}")
                print(f"   Redirect URI: {data['redirect_uri']}")
                print(f"   Auth URL: {data['auth_url'][:80]}...")
                tests_passed += 1
                
                # Vérifier que l'URL d'auth contient bien l'URL ngrok (avec ou sans encodage)
                import urllib.parse
                encoded_ngrok = urllib.parse.quote(ngrok_url, safe='')
                if ngrok_url in data['auth_url'] or encoded_ngrok in data['auth_url']:
                    print(f"✅ URL ngrok correctement injectée dans l'auth URL")
                    tests_passed += 1
                else:
                    print(f"❌ URL ngrok non trouvée dans l'auth URL")
                    print(f"   Cherché: {ngrok_url} ou {encoded_ngrok}")
                    print(f"   Trouvé: {data['auth_url']}")
            else:
                print("❌ Génération d'URL d'authentification échouée")
        else:
            print(f"❌ Erreur génération auth URL: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test auth URL: {e}")
        tests_total -= 1  # Skip the injection test
    
    # Test 3: Mise à jour automatique des endpoints
    print("\n3️⃣ Test de mise à jour automatique des endpoints...")
    try:
        response = requests.post(f"{base_url}/api/ngrok/update-endpoints", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Mise à jour des endpoints réussie")
                print(f"   Message: {data['message']}")
                print(f"   URL active: {data['active_url']}")
                tests_passed += 1
            else:
                print(f"❌ Mise à jour échouée: {data['message']}")
        else:
            print(f"❌ Erreur mise à jour endpoints: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test mise à jour: {e}")
    
    # Test 4: Test d'échange de code avec URI dynamique
    print("\n4️⃣ Test d'échange de code OAuth avec URI dynamique...")
    try:
        payload = {
            "code": "test_code_dynamic_uri",
            "store": "gizmobbs"
            # redirect_uri volontairement omis pour tester la génération automatique
        }
        response = requests.post(f"{base_url}/api/auth/facebook/exchange-code", 
                               json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Le test échouera avec Facebook (car code invalide) mais on vérifie la logique
            if 'redirect_uri' in data.get('data', {}):
                redirect_uri = data['data']['redirect_uri']
                if ngrok_url in redirect_uri:
                    print(f"✅ Redirect URI dynamique correctement injecté")
                    print(f"   URI utilisé: {redirect_uri}")
                    tests_passed += 1
                else:
                    print(f"❌ Redirect URI ne contient pas l'URL ngrok")
                    print(f"   URI: {redirect_uri}")
            else:
                print("❌ Pas de redirect_uri dans la réponse")
        else:
            print(f"❌ Erreur échange code: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test échange code: {e}")
    
    # Test 5: Vérification de la synchronisation frontend
    print("\n5️⃣ Test de synchronisation frontend .env...")
    try:
        # Lire le .env du frontend
        with open('/app/frontend/.env', 'r') as f:
            env_content = f.read()
        
        if f"REACT_APP_BACKEND_URL={ngrok_url}" in env_content:
            print(f"✅ Frontend .env correctement synchronisé")
            print(f"   REACT_APP_BACKEND_URL = {ngrok_url}")
            tests_passed += 1
        else:
            print(f"❌ Frontend .env non synchronisé")
            print(f"   Contenu: {env_content}")
    except Exception as e:
        print(f"❌ Erreur test synchronisation frontend: {e}")
    
    # Résultats finaux
    print("\n" + "=" * 70)
    print(f"📊 RÉSULTATS DES TESTS: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("🎉 TOUS LES TESTS PASSÉS - IMPLÉMENTATION RÉUSSIE !")
        print("\n✅ Fonctionnalités implémentées avec succès:")
        print("   • Détection automatique de l'URL ngrok active")
        print("   • Injection automatique dans redirect_uri OAuth")
        print("   • Mise à jour automatique des endpoints Facebook")
        print("   • Gestion dynamique de la configuration")
        print("   • Synchronisation automatique du frontend")
        return True
    else:
        print(f"⚠️ {tests_total - tests_passed} test(s) échoué(s)")
        return False

if __name__ == "__main__":
    success = test_complete_implementation()
    sys.exit(0 if success else 1)