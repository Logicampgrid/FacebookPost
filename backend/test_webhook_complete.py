#!/usr/bin/env python3
"""
Script de test complet pour valider les endpoints webhook Facebook
Ce script teste exactement les cas d'usage demandés par l'utilisateur
"""

import requests
import json
import sys

def test_get_webhook_valid():
    """Test GET /api/webhook avec token valide"""
    print("🧪 TEST 1: GET webhook avec token valide")
    print("-" * 50)
    
    url = "http://localhost:8001/api/webhook"
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "mon_token_secret_webhook",
        "hub.challenge": "12345"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        print(f"URL: {response.url}")
        print(f"Status Code: {response.status_code}")
        print(f"Response Content: '{response.text}'")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200 and response.text == "12345":
            print("✅ SUCCÈS: GET webhook fonctionne correctement!")
            return True
        else:
            print(f"❌ ÉCHEC: Attendu '12345', reçu '{response.text}'")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        return False

def test_get_webhook_invalid_token():
    """Test GET /api/webhook avec token invalide (doit retourner 403)"""
    print("\n🧪 TEST 2: GET webhook avec token invalide")
    print("-" * 50)
    
    url = "http://localhost:8001/api/webhook"
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "invalid",
        "hub.challenge": "12345"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        print(f"URL: {response.url}")
        print(f"Status Code: {response.status_code}")
        print(f"Response Content: '{response.text}'")
        
        if response.status_code == 403:
            print("✅ SUCCÈS: Token invalide correctement rejeté (403)")
            return True
        else:
            print(f"❌ ÉCHEC: Attendu 403, reçu {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        return False

def test_post_webhook():
    """Test POST /api/webhook avec données Facebook"""
    print("\n🧪 TEST 3: POST webhook avec événement Facebook")
    print("-" * 50)
    
    url = "http://localhost:8001/api/webhook"
    headers = {"Content-Type": "application/json"}
    data = {
        "object": "page",
        "entry": [
            {
                "id": "123",
                "time": 456
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        print(f"Request Data: {json.dumps(data, indent=2)}")
        print(f"Response Content: '{response.text}'")
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                if response_json.get("status") == "received":
                    print("✅ SUCCÈS: POST webhook fonctionne correctement!")
                    return True
                else:
                    print(f"❌ ÉCHEC: Attendu status='received', reçu {response_json}")
                    return False
            except json.JSONDecodeError:
                print(f"❌ ÉCHEC: Réponse n'est pas du JSON valide")
                return False
        else:
            print(f"❌ ÉCHEC: Attendu 200, reçu {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        return False

def test_health_endpoint():
    """Test endpoint de santé pour vérifier que le serveur fonctionne"""
    print("\n🧪 TEST 0: Vérification santé serveur")
    print("-" * 50)
    
    url = "http://localhost:8001/api/health"
    
    try:
        response = requests.get(url, timeout=5)
        
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCÈS: Serveur accessible")
            return True
        else:
            print(f"❌ ÉCHEC: Serveur répond {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERREUR: Impossible de se connecter au serveur")
        print("   Assurez-vous que le serveur tourne sur localhost:8001")
        return False
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        return False

def main():
    """Exécute tous les tests"""
    print("=" * 70)
    print("🚀 TESTS COMPLETS WEBHOOK FACEBOOK - FacebookPost")
    print("=" * 70)
    
    # Test préliminaire de santé
    health_ok = test_health_endpoint()
    if not health_ok:
        print("\n❌ IMPOSSIBLE DE CONTINUER: Serveur non accessible")
        sys.exit(1)
    
    # Tests principaux
    results = []
    results.append(("GET webhook valide", test_get_webhook_valid()))
    results.append(("GET webhook token invalide", test_get_webhook_invalid_token()))
    results.append(("POST webhook événement", test_post_webhook()))
    
    # Résumé des résultats
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 70)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASSÉ" if success else "❌ ÉCHOUÉ"
        print(f"{status:<12} {test_name}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 TOUS LES TESTS SONT PASSÉS!")
        print("Le webhook Facebook est parfaitement configuré.")
        print("\n📋 Commandes de test manuelles:")
        print('curl "http://localhost:8001/api/webhook?hub.mode=subscribe&hub.verify_token=mon_token_secret_webhook&hub.challenge=12345"')
        print('curl -X POST "http://localhost:8001/api/webhook" -H "Content-Type: application/json" -d \'{"object":"page","entry":[{"id":"123","time":456}]}\'')
        sys.exit(0)
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("Vérifiez les logs du serveur et les corrections nécessaires.")
        sys.exit(1)

if __name__ == "__main__":
    main()