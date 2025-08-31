#!/usr/bin/env python3
"""
Script de test pour vérifier les corrections Instagram
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001"
WEBHOOK_URL = f"{BASE_URL}/api/webhook"

def test_store_mapping():
    """Test si tous les stores sont correctement mappés"""
    print("🧪 Test 1: Vérification du mapping des stores")
    
    stores_to_test = ["gizmobbs", "logicantiq", "outdoor", "logicampoutdoor"]
    
    for store in stores_to_test:
        test_data = {
            "store": store,
            "title": f"Test {store}",
            "description": f"Test pour vérifier le mapping du store {store}",
            "url": f"https://example.com/test-{store}"
        }
        
        payload = {
            "json_data": json.dumps(test_data)
        }
        
        try:
            response = requests.post(WEBHOOK_URL, data=payload)
            print(f"  Store '{store}': HTTP {response.status_code}")
            
            if response.status_code == 400:
                error_msg = response.json().get("detail", "Unknown error")
                if "Invalid store" in error_msg:
                    print(f"    ❌ Store non reconnu: {error_msg}")
                else:
                    print(f"    ⚠️ Autre erreur: {error_msg}")
            elif response.status_code == 200:
                print(f"    ✅ Store reconnu")
            else:
                print(f"    ⚠️ Status inattendu: {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Erreur de requête: {str(e)}")

def test_instagram_info():
    """Test pour obtenir des informations sur la configuration Instagram"""
    print("\n🧪 Test 2: Vérification de la configuration Instagram")
    
    try:
        # Test avec l'endpoint d'information
        info_response = requests.get(f"{BASE_URL}/api/pages")
        
        if info_response.status_code == 200:
            info_data = info_response.json()
            print(f"  ✅ Informations récupérées:")
            print(f"    - Utilisateur: {info_data.get('user_name', 'Unknown')}")
            print(f"    - Pages personnelles: {len(info_data.get('personal_pages', []))}")
            print(f"    - Pages Business Manager: {len(info_data.get('business_manager_pages', []))}")
            
            # Vérifier le mapping des stores
            shop_mapping = info_data.get('shop_mapping', {})
            for store_name in ["gizmobbs", "logicantiq", "outdoor", "logicampoutdoor"]:
                if store_name in shop_mapping:
                    store_config = shop_mapping[store_name]
                    print(f"    - Store '{store_name}': {store_config.get('name')} (ID: {store_config.get('expected_id')})")
                else:
                    print(f"    - Store '{store_name}': ❌ Non trouvé dans le mapping")
        else:
            print(f"  ❌ Erreur récupération info: HTTP {info_response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Erreur: {str(e)}")

def test_webhook_basic():
    """Test basique du webhook avec données minimales"""
    print("\n🧪 Test 3: Test webhook basique")
    
    test_data = {
        "store": "gizmobbs",
        "title": "Test Instagram Fix",
        "description": "Test pour vérifier les corrections Instagram", 
        "url": "https://example.com/test"
    }
    
    payload = {
        "json_data": json.dumps(test_data)
    }
    
    try:
        response = requests.post(WEBHOOK_URL, data=payload)
        print(f"  Status: HTTP {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Succès: {result.get('message', 'OK')}")
            if 'routing_result' in result:
                routing = result['routing_result']
                print(f"    - Facebook: {'✅' if routing.get('facebook', {}).get('success') else '❌'}")
                print(f"    - Instagram: {'✅' if routing.get('instagram', {}).get('success') else '❌'}")
                if not routing.get('instagram', {}).get('success'):
                    print(f"    - Erreur Instagram: {routing.get('instagram', {}).get('error')}")
        else:
            print(f"  ❌ Échec: {response.text}")
            
    except Exception as e:
        print(f"  ❌ Erreur: {str(e)}")

if __name__ == "__main__":
    print("🚀 Test des corrections Instagram pour server.py")
    print("=" * 50)
    
    test_store_mapping()
    test_instagram_info()
    test_webhook_basic()
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés")