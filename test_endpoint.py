#!/usr/bin/env python3
"""
Test direct de l'endpoint via simulation
"""
import os
import sys
import json
import asyncio
from datetime import datetime

# Ajouter le répertoire backend au path
sys.path.append("/app/backend")
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv("/app/backend/.env")

# Simuler l'endpoint de test
async def simulate_test_endpoint():
    """Simule l'appel à l'endpoint /api/post/test"""
    
    from test_publication import test_all_stores, log_test
    
    print("🚀 Simulation de l'endpoint /api/post/test")
    print("=" * 50)
    
    # Simuler la requête
    request_data = {
        "platforms": ["facebook"],
        "stores": None,  # Tous les stores
        "custom_message": None  # Utiliser TEST_MESSAGE de .env
    }
    
    log_test(f"Requête simulée: {json.dumps(request_data, indent=2)}", "INFO")
    print()
    
    # Exécuter la logique de publication
    results = await test_all_stores()
    
    # Construire la réponse comme l'endpoint
    successful_stores = [store for store, data in results.items() if data["success"]]
    failed_stores = [store for store, data in results.items() if not data["success"]]
    
    response = {
        "success": len(successful_stores) > 0,
        "message": f"Publication de test terminée: {len(successful_stores)}/{len(results)} stores réussis",
        "test_message": os.getenv("TEST_MESSAGE", "Test automatique 🚀"),
        "stores_requested": list(results.keys()),
        "platforms_requested": ["facebook"],
        "results": [
            {
                "store": store,
                "success": data["success"],
                "platforms": ["facebook"],
                "facebook_result": data["result"] if data["success"] else None,
                "instagram_result": None,
                "errors": [] if data["success"] else [str(data["result"])]
            }
            for store, data in results.items()
        ],
        "summary": {
            "total_stores": len(results),
            "successful_stores": len(successful_stores),
            "failed_stores": len(failed_stores)
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    print()
    print("📋 RÉPONSE ENDPOINT (FORMAT JSON):")
    print("=" * 50)
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    return response

if __name__ == "__main__":
    asyncio.run(simulate_test_endpoint())