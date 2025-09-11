#!/usr/bin/env python3
"""
Test script pour vérifier la correction de la route /api/auth/facebook/exchange-code
"""
import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8001"
ENDPOINT = "/api/auth/facebook/exchange-code"

def test_format_with_state():
    """Test avec le format frontend: {"code": "...", "state": "..."}"""
    print("🧪 Test 1: Format frontend avec state...")
    
    data = {
        "code": "test_code_123456789",
        "state": "logicantiq"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        # Vérifier que la requête est bien parsée (même si elle échoue pour manque de config)
        if response.status_code in [200, 400]:
            print("✅ Format avec state accepté - parsing OK")
            return True
        else:
            print("❌ Format avec state refusé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur requête: {e}")
        return False

def test_format_with_store():
    """Test avec le format legacy: {"code": "...", "store": "...", "redirect_uri": "..."}"""
    print("\n🧪 Test 2: Format legacy avec store...")
    
    data = {
        "code": "test_code_123456789",
        "store": "logicantiq",
        "redirect_uri": "http://localhost:3000/auth/callback"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        # Vérifier que la requête est bien parsée
        if response.status_code in [200, 400]:
            print("✅ Format avec store accepté - parsing OK")
            return True
        else:
            print("❌ Format avec store refusé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur requête: {e}")
        return False

def test_minimal_format():
    """Test avec format minimal: {"code": "...", "state": "..."}"""
    print("\n🧪 Test 3: Format minimal...")
    
    data = {
        "code": "test_code_123456789",
        "state": "default"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # Vérifier que le mapping state->store fonctionne
        if 'data' in result and result['data'].get('store') == 'default':
            print("✅ Mapping state->store fonctionne")
            return True
        else:
            print("❌ Mapping state->store échoué")
            return False
            
    except Exception as e:
        print(f"❌ Erreur requête: {e}")
        return False

def main():
    """Lancer tous les tests"""
    print("🚀 Test de correction Facebook Exchange Code")
    print("=" * 50)
    
    # Vérifier que le serveur répond
    try:
        health_response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Serveur backend non disponible")
            sys.exit(1)
        print("✅ Serveur backend disponible")
    except Exception as e:
        print(f"❌ Impossible de contacter le serveur: {e}")
        sys.exit(1)
    
    # Lancer les tests
    test1_ok = test_format_with_state()
    test2_ok = test_format_with_store() 
    test3_ok = test_minimal_format()
    
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DES TESTS:")
    print(f"   Test 1 (format frontend): {'✅ OK' if test1_ok else '❌ ÉCHEC'}")
    print(f"   Test 2 (format legacy):   {'✅ OK' if test2_ok else '❌ ÉCHEC'}")
    print(f"   Test 3 (format minimal):  {'✅ OK' if test3_ok else '❌ ÉCHEC'}")
    
    if all([test1_ok, test2_ok, test3_ok]):
        print("\n🎉 TOUS LES TESTS RÉUSSIS - La correction fonctionne!")
        return 0
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
        return 1

if __name__ == "__main__":
    sys.exit(main())