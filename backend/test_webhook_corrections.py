#!/usr/bin/env python3
"""
Test webhook /api/webhook - CORRECTIONS PRIORITAIRES FacebookPost
"""

import requests
import json
import time

# Configuration de test
BASE_URL = "http://localhost:8001"
VERIFY_TOKEN = "mon_token_secret_webhook"

def test_webhook_verification():
    """Test de vérification webhook GET /api/webhook"""
    print("🧪 Test 1: Vérification webhook GET")
    
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": VERIFY_TOKEN,
        "hub.challenge": "test_challenge_12345"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/webhook", params=params, timeout=10)
        
        if response.status_code == 200:
            if response.text == "test_challenge_12345":
                print("✅ Webhook GET fonctionne - Challenge retourné correctement")
                return True
            else:
                print(f"❌ Webhook GET - Mauvais challenge: {response.text}")
                return False
        else:
            print(f"❌ Webhook GET - Status: {response.status_code}, Body: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook GET - Erreur: {e}")
        return False

def test_webhook_post():
    """Test de réception webhook POST /api/webhook"""
    print("\n🧪 Test 2: Réception webhook POST")
    
    webhook_data = {
        "object": "page",
        "entry": [
            {
                "id": "102401876209415",  # gizmobbs page
                "time": int(time.time()),
                "messaging": [
                    {
                        "sender": {"id": "test_user_123"},
                        "recipient": {"id": "102401876209415"},
                        "timestamp": int(time.time()),
                        "message": {
                            "text": "Test message pour gizmobbs",
                            "attachments": [
                                {
                                    "type": "image",
                                    "payload": {
                                        "url": "https://test.com/image.jpg"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/webhook",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "received":
                print("✅ Webhook POST fonctionne - Données reçues")
                return True
            else:
                print(f"❌ Webhook POST - Réponse inattendue: {result}")
                return False
        else:
            print(f"❌ Webhook POST - Status: {response.status_code}, Body: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook POST - Erreur: {e}")
        return False

def test_gizmobbs_priority():
    """Test priorité store gizmobbs (@logicamp_berger)"""
    print("\n🧪 Test 3: Test priorité gizmobbs (@logicamp_berger)")
    
    try:
        response = requests.get(f"{BASE_URL}/api/test-gizmobbs", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print("✅ Test gizmobbs store prioritaire réussi")
                print(f"   Store: {result.get('store')}")
                print(f"   Configuration FB: {result.get('configuration', {}).get('fb_page_id')}")
                print(f"   Instagram ID: {result.get('configuration', {}).get('ig_user_id')}")
                return True
            else:
                print(f"❌ Test gizmobbs - Erreur: {result.get('message')}")
                return False
        else:
            print(f"❌ Test gizmobbs - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test gizmobbs - Erreur: {e}")
        return False

def test_ftp_connection():
    """Test connexion FTP htmlkit"""
    print("\n🧪 Test 4: Test connexion FTP htmlkit")
    
    try:
        response = requests.get(f"{BASE_URL}/api/test-ftp", timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print("✅ Connexion FTP htmlkit réussie")
                print(f"   Host: {result.get('ftp_config', {}).get('host')}")
                print(f"   Base URL: {result.get('ftp_config', {}).get('base_url')}")
                return True
            else:
                diagnostic = result.get('diagnostic', {})
                print(f"❌ Connexion FTP échouée")
                print(f"   Host accessible: {diagnostic.get('host_reachable')}")
                print(f"   Login réussi: {diagnostic.get('login_success')}")
                print(f"   Erreur: {diagnostic.get('error')}")
                return False
        else:
            print(f"❌ Test FTP - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test FTP - Erreur: {e}")
        return False

def main():
    """Exécution des tests de correction"""
    print("🚀 Tests de correction FacebookPost - Webhook et améliorations")
    print("=" * 60)
    
    tests_results = []
    
    # Test 1: Webhook GET
    tests_results.append(("Webhook GET", test_webhook_verification()))
    
    # Test 2: Webhook POST  
    tests_results.append(("Webhook POST", test_webhook_post()))
    
    # Test 3: Store gizmobbs prioritaire
    tests_results.append(("Store gizmobbs", test_gizmobbs_priority()))
    
    # Test 4: FTP htmlkit
    tests_results.append(("FTP htmlkit", test_ftp_connection()))
    
    # Résultats
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS DES TESTS")
    print("=" * 60)
    
    passed = 0
    total = len(tests_results)
    
    for test_name, result in tests_results:
        status = "✅ PASSÉ" if result else "❌ ÉCHEC"
        print(f"{test_name:<20}: {status}")
        if result:
            passed += 1
    
    print(f"\nScore: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests passent ! Application prête.")
    else:
        print(f"⚠️ {total - passed} tests en échec - Corrections nécessaires.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)