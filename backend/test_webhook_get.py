#!/usr/bin/env python3
"""
Script de test pour vérifier l'endpoint GET /api/webhook
Ce script simule la requête de vérification que Facebook envoie
"""

import requests
import sys

def test_webhook_verification():
    """Test de l'endpoint GET /api/webhook"""
    
    # Configuration du test
    base_url = "http://localhost:8001"
    webhook_url = f"{base_url}/api/webhook"
    
    # Paramètres de test (simulant Facebook)
    verify_token = "mon_token_secret_webhook"  # Doit correspondre à FACEBOOK_VERIFY_TOKEN
    test_challenge = "test_challenge_12345"
    
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": verify_token,
        "hub.challenge": test_challenge
    }
    
    print("🧪 Test de vérification webhook Facebook")
    print(f"URL: {webhook_url}")
    print(f"Paramètres: {params}")
    print("-" * 50)
    
    try:
        # Envoyer la requête GET
        response = requests.get(webhook_url, params=params, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content: '{response.text}'")
        print(f"Expected Challenge: '{test_challenge}'")
        
        # Vérifier le résultat
        if response.status_code == 200:
            if response.text == test_challenge:
                print("✅ SUCCESS: Webhook verification fonctionne correctement!")
                print("✅ Le challenge a été renvoyé correctement")
                return True
            else:
                print(f"❌ ERREUR: Challenge incorrect")
                print(f"   Attendu: '{test_challenge}'")
                print(f"   Reçu: '{response.text}'")
                return False
        else:
            print(f"❌ ERREUR: Status code incorrect ({response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERREUR: Impossible de se connecter au serveur")
        print("   Assurez-vous que le serveur tourne sur localhost:8001")
        return False
    except requests.exceptions.Timeout:
        print("❌ ERREUR: Timeout de la requête")
        return False
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        return False

def test_webhook_invalid_token():
    """Test avec un token invalide (doit retourner 403)"""
    
    base_url = "http://localhost:8001"
    webhook_url = f"{base_url}/api/webhook"
    
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "invalid_token",  # Token incorrect
        "hub.challenge": "test_challenge_12345"
    }
    
    print("\n🧪 Test avec token invalide (doit retourner 403)")
    print(f"Paramètres: {params}")
    print("-" * 50)
    
    try:
        response = requests.get(webhook_url, params=params, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Content: '{response.text}'")
        
        if response.status_code == 403:
            print("✅ SUCCESS: Token invalide correctement rejeté (403)")
            return True
        else:
            print(f"❌ ERREUR: Devrait retourner 403, mais retourne {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DE L'ENDPOINT WEBHOOK GET /api/webhook")
    print("=" * 60)
    
    # Test 1: Vérification normale
    test1_success = test_webhook_verification()
    
    # Test 2: Token invalide
    test2_success = test_webhook_invalid_token()
    
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"✅ Test token valide: {'PASSÉ' if test1_success else 'ÉCHOUÉ'}")
    print(f"✅ Test token invalide: {'PASSÉ' if test2_success else 'ÉCHOUÉ'}")
    
    if test1_success and test2_success:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("Le webhook GET /api/webhook fonctionne correctement.")
        sys.exit(0)
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("Vérifiez les logs du serveur pour plus de détails.")
        sys.exit(1)