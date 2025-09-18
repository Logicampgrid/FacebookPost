#!/usr/bin/env python3
"""
Script de test de publication pour les 3 boutiques
"""
import requests
import json
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('/app/backend/.env')

# URL de l'API backend
API_BASE = "http://localhost:8001"

# Configuration des boutiques
STORES = ["gizmobbs", "logicantiq", "outdoor"]

def test_store_publication(store_name):
    """Teste une publication pour une boutique"""
    print(f"\n🧪 Test de publication pour {store_name}...")
    
    try:
        # Données de test
        test_data = {
            "store": store_name,
            "message": f"🧪 Test automatique pour {store_name} - {store_name.upper()} fonctionne parfaitement !",
            "product_url": "https://www.example.com/test-product",
            "platforms": ["facebook"]  # Test Facebook uniquement pour commencer
        }
        
        # Faire l'appel à l'API de publication
        response = requests.post(f"{API_BASE}/api/publish", json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {store_name}: Publication réussie !")
            
            if result.get('facebook_result'):
                fb_result = result['facebook_result']
                if fb_result.get('test_mode'):
                    print(f"   🧪 Mode test - ID simulé: {fb_result.get('id', 'N/A')}")
                else:
                    print(f"   📝 Post Facebook ID: {fb_result.get('id', 'N/A')}")
            
            return True
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"❌ {store_name}: Erreur HTTP {response.status_code}")
            print(f"   Détails: {error_data}")
            return False
            
    except Exception as e:
        print(f"❌ {store_name}: Erreur de publication → {str(e)}")
        return False

def test_store_configuration(store_name):
    """Teste la configuration d'une boutique"""
    print(f"\n🔍 Test de configuration pour {store_name}...")
    
    try:
        response = requests.get(f"{API_BASE}/api/stores/{store_name}/config", timeout=15)
        
        if response.status_code == 200:
            config = response.json()
            print(f"✅ {store_name}: Configuration récupérée")
            print(f"   📄 Nom: {config.get('name', 'N/A')}")
            print(f"   🆔 Page ID: {config.get('fb_page_id', 'N/A')}")
            print(f"   📸 Instagram ID: {config.get('ig_user_id', 'N/A')}")
            print(f"   🔑 Token: {'✅ Présent' if config.get('access_token') else '❌ Manquant'}")
            return True
        else:
            print(f"❌ {store_name}: Impossible de récupérer la configuration")
            return False
            
    except Exception as e:
        print(f"❌ {store_name}: Erreur de configuration → {str(e)}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test de publication pour les 3 boutiques")
    print("=" * 60)
    
    # Vérifier que l'API backend est accessible
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Backend accessible")
        else:
            print("❌ API Backend non accessible")
            return False
    except Exception as e:
        print(f"❌ Impossible de contacter l'API Backend: {e}")
        return False
    
    results = {}
    
    for store_name in STORES:
        print(f"\n{'='*20} {store_name.upper()} {'='*20}")
        
        # Test de configuration
        config_ok = test_store_configuration(store_name)
        
        # Test de publication si la configuration est OK
        publication_ok = False
        if config_ok:
            publication_ok = test_store_publication(store_name)
        
        results[store_name] = {
            'config_ok': config_ok,
            'publication_ok': publication_ok,
            'fully_functional': config_ok and publication_ok
        }
    
    # Résumé final
    print(f"\n{'='*25} RÉSUMÉ FINAL {'='*25}")
    
    all_working = True
    for store_name, result in results.items():
        status = "✅ FONCTIONNEL" if result['fully_functional'] else "❌ PROBLÈME"
        print(f"{status} {store_name}")
        
        if not result['fully_functional']:
            all_working = False
            if not result['config_ok']:
                print(f"   → Problème de configuration")
            if not result['publication_ok']:
                print(f"   → Problème de publication")
    
    if all_working:
        print(f"\n🎉 TOUTES LES BOUTIQUES SONT FONCTIONNELLES !")
        print(f"✅ gizmobbs, logicantiq et outdoor fonctionnent de la même manière")
    else:
        print(f"\n⚠️ Des problèmes ont été détectés.")
    
    print(f"\n💡 Pour désactiver le mode test et faire de vraies publications:")
    print(f"   Modifiez PUBLICATION_TEST_MODE=false dans /app/backend/.env")
    
    return all_working

if __name__ == "__main__":
    main()