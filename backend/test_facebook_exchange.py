#!/usr/bin/env python3
"""
Test simple pour valider la correction de l'endpoint /api/auth/facebook/exchange-code
"""

import requests
import json
import time
import subprocess
import sys
import os
from threading import Thread

def start_server():
    """Démarrer le serveur en arrière-plan"""
    print("🚀 Démarrage du serveur de test...")
    os.environ["ENABLE_NGROK"] = "false"  # Désactiver ngrok pour le test
    os.environ["DRY_RUN"] = "true"
    
    cmd = [sys.executable, "server_windows.py"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

def wait_for_server(url="http://localhost:8001/api/health", timeout=30):
    """Attendre que le serveur soit prêt"""
    print("⏳ Attente du serveur...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print("✅ Serveur prêt!")
                return True
        except:
            pass
        time.sleep(1)
    
    print("❌ Timeout - Serveur non disponible")
    return False

def test_json_format():
    """Test format JSON"""
    print("\n🧪 Test 1: Format JSON")
    
    url = "http://localhost:8001/api/auth/facebook/exchange-code"
    data = {
        "code": "AQD123456789_TEST",
        "state": "csrf_protection_123_TEST"
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if (result.get("success") and 
                result.get("data", {}).get("code") == data["code"] and
                result.get("data", {}).get("state") == data["state"]):
                print("✅ Test JSON RÉUSSI")
                return True
            else:
                print("❌ Test JSON ÉCHOUÉ - Réponse incorrecte")
                return False
        else:
            print(f"❌ Test JSON ÉCHOUÉ - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test JSON ÉCHOUÉ - Erreur: {e}")
        return False

def test_form_data():
    """Test format form-data"""
    print("\n🧪 Test 2: Format Form-data")
    
    url = "http://localhost:8001/api/auth/facebook/exchange-code"
    data = {
        "code": "AQD987654321_TEST",
        "state": "csrf_protection_456_TEST"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if (result.get("success") and 
                result.get("data", {}).get("code") == data["code"] and
                result.get("data", {}).get("state") == data["state"]):
                print("✅ Test Form-data RÉUSSI")
                return True
            else:
                print("❌ Test Form-data ÉCHOUÉ - Réponse incorrecte")
                return False
        else:
            print(f"❌ Test Form-data ÉCHOUÉ - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test Form-data ÉCHOUÉ - Erreur: {e}")
        return False

def test_missing_parameter():
    """Test paramètre manquant"""
    print("\n🧪 Test 3: Paramètre manquant (doit échouer)")
    
    url = "http://localhost:8001/api/auth/facebook/exchange-code"
    data = {
        "code": "AQD111111111_TEST"
        # state manquant intentionnellement
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            print("✅ Test paramètre manquant RÉUSSI (erreur 400 attendue)")
            return True
        else:
            print(f"❌ Test paramètre manquant ÉCHOUÉ - Status {response.status_code} (400 attendu)")
            return False
            
    except Exception as e:
        print(f"❌ Test paramètre manquant ÉCHOUÉ - Erreur: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("=" * 60)
    print("🔧 TEST DE CORRECTION - /api/auth/facebook/exchange-code")
    print("=" * 60)
    
    # Démarrer le serveur
    server_process = start_server()
    
    try:
        # Attendre que le serveur soit prêt
        if not wait_for_server():
            print("❌ Impossible de démarrer le serveur")
            return False
        
        # Exécuter les tests
        results = []
        results.append(test_json_format())
        results.append(test_form_data())
        results.append(test_missing_parameter())
        
        # Résultats
        print("\n" + "=" * 60)
        print("📊 RÉSULTATS")
        print("=" * 60)
        
        success_count = sum(results)
        total_count = len(results)
        
        print(f"✅ Tests réussis: {success_count}/{total_count}")
        
        if success_count == total_count:
            print("🎉 TOUS LES TESTS SONT PASSÉS!")
            print("✅ La correction fonctionne parfaitement")
            return True
        else:
            print("❌ Certains tests ont échoué")
            return False
            
    finally:
        # Arrêter le serveur
        print("\n🛑 Arrêt du serveur...")
        server_process.terminate()
        server_process.wait(timeout=5)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)