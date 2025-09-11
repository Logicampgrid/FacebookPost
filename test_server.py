#!/usr/bin/env python3
"""
Serveur de test simple pour l'endpoint /api/post/test
"""
import os
import sys
import requests
import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import List, Optional
import uuid

# Ajouter le répertoire backend au path
sys.path.append("/app/backend")
from dotenv import load_dotenv

# Charger les variables d'environnement  
load_dotenv("/app/backend/.env")

# Configuration Facebook
FACEBOOK_GRAPH_URL = os.getenv("FACEBOOK_GRAPH_URL", "https://graph.facebook.com/v18.0")
PUBLICATION_TEST_MODE = os.getenv("PUBLICATION_TEST_MODE", "false").lower() == "true"

# Configuration des stores
STORES = {
    "gizmobbs": {
        "fb_page_id": os.getenv("FB_PAGE_ID_GIZMO"),
        "access_token": os.getenv("FB_ACCESS_TOKEN_GIZMO"),
        "ig_user_id": os.getenv("IG_USER_ID_GIZMO")
    },
    "logicantiq": {
        "fb_page_id": os.getenv("FB_PAGE_ID_LOGICANTIQ"),
        "access_token": os.getenv("FB_ACCESS_TOKEN_LOGICANTIQ"),
        "ig_user_id": os.getenv("IG_USER_ID_LOGICANTIQ")
    },
    "logicampoutdoor": {
        "fb_page_id": os.getenv("FB_PAGE_ID_LOGICAMPOUTDOOR"),
        "access_token": os.getenv("FB_ACCESS_TOKEN_LOGICAMPOUTDOOR"),
        "ig_user_id": os.getenv("IG_USER_ID_LOGICAMPOUTDOOR")
    }
}

app = FastAPI(title="Test Publication Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

class TestPublishRequest(BaseModel):
    stores: Optional[List[str]] = None
    platforms: List[str] = ["facebook"]
    custom_message: Optional[str] = None
    
    @validator('platforms')
    def validate_platforms(cls, v):
        valid_platforms = ["facebook", "instagram"]
        for platform in v:
            if platform not in valid_platforms:
                raise ValueError(f'Platform must be one of: {valid_platforms}')
        return v

def log_publish(message: str, level: str = "INFO"):
    """Logging spécialisé pour les publications"""
    icons = {"INFO": "📢", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
    icon = icons.get(level.upper(), "📢")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [PUBLISH] {message}")

def get_store_config(store: str) -> dict:
    """Récupère la configuration d'un store"""
    if store not in STORES:
        raise ValueError(f"Store inconnu: {store}")
    return STORES[store].copy()

async def post_to_facebook(store: str, message: str, product_url: str) -> dict:
    """Publie un post sur la page Facebook correspondante"""
    try:
        log_publish(f"Publication Facebook pour {store}", "INFO")
        
        config = get_store_config(store)
        
        if not config["fb_page_id"] or not config["access_token"]:
            raise ValueError(f"Configuration Facebook manquante pour {store}")
        
        # Mode test : simulation
        if PUBLICATION_TEST_MODE:
            log_publish(f"MODE TEST - Publication Facebook simulée pour {store}", "TEST")
            return {
                "id": f"test_fb_post_{uuid.uuid4().hex[:8]}",
                "message": message,
                "link": product_url,
                "test_mode": True
            }
        
        # Publication réelle
        url = f"{FACEBOOK_GRAPH_URL}/{config['fb_page_id']}/feed"
        payload = {
            "message": message,
            "link": product_url,
            "access_token": config["access_token"]
        }
        
        log_publish(f"Requête Facebook: POST {url}", "INFO")
        response = requests.post(url, data=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if "id" not in data:
            raise Exception(f"Réponse Facebook invalide: {data}")
        
        log_publish(f"Publication Facebook réussie: {data['id']}", "SUCCESS")
        return data
        
    except Exception as e:
        error_msg = f"Erreur Facebook: {str(e)}"
        log_publish(error_msg, "ERROR")
        raise Exception(error_msg)

async def publish_post(store: str, message: str, product_url: str, image_url: Optional[str] = None, platforms: List[str] = ["facebook"]) -> dict:
    """Fonction principale pour publier sur Facebook et/ou Instagram"""
    try:
        log_publish(f"Début publication multi-plateforme pour {store} sur {platforms}", "INFO")
        
        results = {
            "success": False,
            "store": store,
            "platforms": platforms,
            "facebook_result": None,
            "instagram_result": None,
            "errors": [],
            "test_mode": PUBLICATION_TEST_MODE
        }
        
        # Publication Facebook
        if "facebook" in platforms:
            try:
                fb_result = await post_to_facebook(store, message, product_url)
                results["facebook_result"] = fb_result
                log_publish("Publication Facebook terminée", "SUCCESS")
            except Exception as e:
                error_msg = f"Échec Facebook: {str(e)}"
                results["errors"].append(error_msg)
                log_publish(error_msg, "ERROR")
        
        # Publication Instagram (à implémenter plus tard)
        if "instagram" in platforms:
            results["errors"].append("Instagram non implémenté dans ce test")
            log_publish("Instagram non implémenté", "WARNING")
        
        # Déterminer le succès global
        success_count = 0
        if "facebook" in platforms and results["facebook_result"]:
            success_count += 1
        
        results["success"] = success_count > 0 and len([e for e in results["errors"] if "Instagram non implémenté" not in e]) == 0
        
        return results
        
    except Exception as e:
        error_msg = f"Erreur générale publication: {str(e)}"
        log_publish(error_msg, "ERROR")
        return {
            "success": False,
            "store": store,
            "platforms": platforms,
            "facebook_result": None,
            "instagram_result": None,
            "errors": [error_msg],
            "test_mode": PUBLICATION_TEST_MODE
        }

@app.get("/api/health")
async def health():
    return {"status": "ok", "test_mode": PUBLICATION_TEST_MODE}

@app.post("/api/post/test")
async def test_publish_endpoint(request: TestPublishRequest):
    """Endpoint pour publier un message de test sur les stores configurés"""
    try:
        # Récupérer le message de test depuis .env ou utiliser celui fourni
        test_message = request.custom_message or os.getenv("TEST_MESSAGE", "Test automatique 🚀")
        
        # Déterminer quels stores utiliser
        stores_to_use = request.stores if request.stores else list(STORES.keys())
        
        log_publish(f"Publication de test pour stores: {stores_to_use} sur plateformes: {request.platforms}", "INFO")
        log_publish(f"Message de test: {test_message}", "INFO")
        
        results = []
        
        for store in stores_to_use:
            if store not in STORES:
                log_publish(f"Store inconnu ignoré: {store}", "WARNING")
                continue
                
            store_config = get_store_config(store)
            
            # Vérifier la configuration du store
            missing_config = []
            if not store_config.get("fb_page_id"):
                missing_config.append("fb_page_id")
            if not store_config.get("access_token"):
                missing_config.append("access_token")
            
            # Pour Instagram, vérifier si ig_user_id est configuré
            if "instagram" in request.platforms and not store_config.get("ig_user_id"):
                log_publish(f"Store {store}: Instagram non configuré (ig_user_id manquant), publication uniquement sur Facebook", "WARNING")
                # Filtrer Instagram pour ce store
                platforms_for_store = [p for p in request.platforms if p != "instagram"]
            else:
                platforms_for_store = request.platforms.copy()
            
            if missing_config:
                error_msg = f"Configuration manquante pour {store}: {missing_config}"
                log_publish(error_msg, "ERROR")
                results.append({
                    "store": store,
                    "success": False,
                    "error": error_msg,
                    "platforms": platforms_for_store
                })
                continue
            
            try:
                # Publier le message de test
                if platforms_for_store:
                    result = await publish_post(
                        store=store,
                        message=test_message,
                        product_url="https://example.com/test",
                        image_url=None,
                        platforms=platforms_for_store
                    )
                    
                    results.append({
                        "store": store,
                        "success": result["success"],
                        "platforms": platforms_for_store,
                        "facebook_result": result.get("facebook_result"),
                        "instagram_result": result.get("instagram_result"),
                        "errors": result.get("errors", [])
                    })
                    
                    if result["success"]:
                        log_publish(f"✅ Publication de test réussie pour {store}", "SUCCESS")
                    else:
                        log_publish(f"❌ Échec publication de test pour {store}: {result.get('errors', [])}", "ERROR")
                        
            except Exception as e:
                error_msg = f"Erreur publication test {store}: {str(e)}"
                log_publish(error_msg, "ERROR")
                results.append({
                    "store": store,
                    "success": False,
                    "error": error_msg,
                    "platforms": platforms_for_store
                })
        
        # Calculer le succès global
        total_stores = len(results)
        successful_stores = sum(1 for r in results if r["success"])
        
        overall_success = successful_stores > 0
        
        log_publish(f"Publication de test terminée: {successful_stores}/{total_stores} stores réussis", 
                   "SUCCESS" if overall_success else "ERROR")
        
        return {
            "success": overall_success,
            "message": f"Publication de test terminée: {successful_stores}/{total_stores} stores réussis",
            "test_message": test_message,
            "stores_requested": stores_to_use,
            "platforms_requested": request.platforms,
            "results": results,
            "summary": {
                "total_stores": total_stores,
                "successful_stores": successful_stores,
                "failed_stores": total_stores - successful_stores
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Erreur interne test publication: {str(e)}"
        log_publish(error_msg, "ERROR")
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Serveur de test démarré sur http://localhost:8000")
    print(f"Mode test: {PUBLICATION_TEST_MODE}")
    uvicorn.run(app, host="0.0.0.0", port=8000)