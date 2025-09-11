#!/usr/bin/env python3
"""
Script de test pour la publication Facebook/Instagram
"""
import os
import sys
import requests
import asyncio
from datetime import datetime

# Ajouter le répertoire backend au path pour importer nos modules
sys.path.append("/app/backend")
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv("/app/backend/.env")

# Configuration Facebook
FACEBOOK_GRAPH_URL = os.getenv("FACEBOOK_GRAPH_URL", "https://graph.facebook.com/v18.0")

# Configuration des stores
STORES = {
    "gizmobbs": {
        "fb_page_id": os.getenv("FB_PAGE_ID_GIZMO"),
        "access_token": os.getenv("FB_ACCESS_TOKEN_GIZMO")
    },
    "logicantiq": {
        "fb_page_id": os.getenv("FB_PAGE_ID_LOGICANTIQ"),
        "access_token": os.getenv("FB_ACCESS_TOKEN_LOGICANTIQ")
    },
    "logicampoutdoor": {
        "fb_page_id": os.getenv("FB_PAGE_ID_LOGICAMPOUTDOOR"),  
        "access_token": os.getenv("FB_ACCESS_TOKEN_LOGICAMPOUTDOOR")
    }
}

def log_test(message: str, level: str = "INFO"):
    """Logging pour les tests"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
    icon = icons.get(level.upper(), "📢")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [TEST] {message}")

async def test_facebook_publication(store: str, message: str):
    """Test de publication Facebook pour un store"""
    try:
        log_test(f"Test publication Facebook pour {store}", "INFO")
        
        if store not in STORES:
            raise ValueError(f"Store inconnu: {store}")
        
        config = STORES[store]
        
        if not config["fb_page_id"] or not config["access_token"]:
            raise ValueError(f"Configuration manquante pour {store}")
        
        # Publication Facebook
        url = f"{FACEBOOK_GRAPH_URL}/{config['fb_page_id']}/feed"
        payload = {
            "message": message,
            "link": "https://example.com/test",
            "access_token": config["access_token"]
        }
        
        log_test(f"Requête: POST {url}", "INFO")
        log_test(f"Page ID: {config['fb_page_id']}", "INFO")
        log_test(f"Token: {config['access_token'][:20]}...", "INFO")
        
        response = requests.post(url, data=payload, timeout=30)
        
        log_test(f"Status Code: {response.status_code}", "INFO")
        log_test(f"Response: {response.text}", "INFO")
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data:
                log_test(f"✅ Publication réussie pour {store}: {data['id']}", "SUCCESS")
                return True, data
            else:
                log_test(f"❌ Réponse invalide pour {store}: {data}", "ERROR")
                return False, data
        else:
            log_test(f"❌ Erreur HTTP pour {store}: {response.status_code} - {response.text}", "ERROR")
            return False, {"error": response.text}
            
    except Exception as e:
        log_test(f"❌ Erreur pour {store}: {str(e)}", "ERROR")
        return False, {"error": str(e)}

async def test_all_stores():
    """Test de publication pour tous les stores"""
    test_message = os.getenv("TEST_MESSAGE", "Test automatique 🚀")
    log_test(f"Message de test: {test_message}", "INFO")
    
    results = {}
    
    for store in STORES.keys():
        log_test(f"=== Test pour {store} ===", "INFO")
        success, result = await test_facebook_publication(store, test_message)
        results[store] = {"success": success, "result": result}
        print()  # Ligne vide pour séparer les tests
    
    # Résumé
    log_test("=== RÉSUMÉ ===", "INFO")
    successful_stores = [store for store, data in results.items() if data["success"]]
    failed_stores = [store for store, data in results.items() if not data["success"]]
    
    log_test(f"Stores réussis ({len(successful_stores)}): {successful_stores}", "SUCCESS")
    if failed_stores:
        log_test(f"Stores échoués ({len(failed_stores)}): {failed_stores}", "ERROR")
    
    return results

if __name__ == "__main__":
    print("🚀 Test de publication Facebook/Instagram")
    print("=" * 50)
    
    # Vérifier la configuration
    log_test("Vérification de la configuration...", "INFO")
    for store, config in STORES.items():
        if config["fb_page_id"] and config["access_token"]:
            log_test(f"{store}: ✅ Configuré", "SUCCESS")
        else:
            log_test(f"{store}: ❌ Configuration manquante", "ERROR")
    
    print()
    
    # Lancer les tests
    asyncio.run(test_all_stores())