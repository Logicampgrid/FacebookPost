from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, validator
from typing import List, Optional
import os
import json
import uuid
import time
import threading
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === FACEBOOK/META CONFIGURATION MISE À JOUR ===
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID", "5664227323683118")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET", "b359a1c87c920288385daf75aed873a3")
FACEBOOK_CLIENT_TOKEN = os.getenv("FACEBOOK_CLIENT_TOKEN", "7725f6e0b13d367a829b44ff16a3421f")
FACEBOOK_GRAPH_URL = os.getenv("FACEBOOK_GRAPH_URL", "https://graph.facebook.com/v18.0")

# === CONFIGURATION STORES (MISE À JOUR) ===
PUBLICATION_TEST_MODE = os.getenv("PUBLICATION_TEST_MODE", "false").lower() == "true"

# Configuration des 3 stores selon les spécifications actualisées
STORES = {
    "gizmobbs": {
        "name": "Le Berger Blanc Suisse",
        "fb_page_id": "102401876209415",
        "ig_user_id": os.getenv("IG_USER_ID_GIZMO"),
        "access_token": "EABQflbGOIS4BPcNEepg39xXlNSs5ufNY2ZCZAOaowF2jBR9tOqZAa3fPwQZBZBo7BkQ8pvL2ZClSmkQh4zFjIfLuyTz3ZAQyQfc4HimmG2TWs81HI3xlorpOOvb5yyR6MJDYlz6ywXrPtZBs8rejrE1KIeOyb24EMkU79KIporIC3WZB2LZCEDMBYj4cfkf6Wh9r7PJUchVjskVnCLi6ZAR"
    },
    "logicantiq": {
        "name": "LogicAntiq",
        "fb_page_id": "210654558802531",
        "ig_user_id": os.getenv("IG_USER_ID_LOGICANTIQ"),
        "access_token": "EABQflbGOIS4BPQwnZCcFNhgWW0NLkP51fapkZBpwmZBEwwCOiTR9P8I8ZAQv7acYZBjVMWNDMPzlO3RdMbNkWhZBfqFzh4qPxtZAT6hA6AZALBM46G8Ho5QpSQmZAKIaeSoXMogbLvph0ZC2wsPXvHBMD0dMb77bhpwdOSkVLAZB2bf9lR798zOaF0wEw3Uqc9OZCA9QhDuZCtJO9Eyp4mmi1"
    },
    "outdoor": {
        "name": "Logicamp Outdoor",
        "fb_page_id": "236260991673388",
        "ig_user_id": os.getenv("IG_USER_ID_OUTDOOR"),
        "access_token": "EABQflbGOIS4BPSQxgJZA7rmIdoSOZCZBYbuAzY4TDjezHZCDGqB3MOZB6CAcJoZB1CJ7AZAE89cTUtWZBu165MT3zZCxlHAfBZCJWwWl1dwnsYC8rzqvcwOdQzpuwzik4HeGP6HggT2GHhUvyxtakytQiAORV17watHXBQOrU1ZA55DZAhTJTpv11gQvxd3yI9vahJUZBEbF5LNEZAKYxKyZCtb"
    }
}

# === FASTAPI APP INITIALIZATION ===
app = FastAPI(title="Meta Publishing Platform - Clean Version")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# === LOGGING FUNCTIONS ===
def log_publish(message: str, level: str = "INFO"):
    """Logging spécialisé pour les publications"""
    icons = {"INFO": "📢", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
    icon = icons.get(level.upper(), "📢")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [PUBLISH] {message}")

def log_app(message: str, level: str = "INFO"):
    """Logging pour l'application"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "START": "🚀"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [APP] {message}")

# === PYDANTIC MODELS ===
class TestPublishRequest(BaseModel):
    stores: Optional[List[str]] = None  # Si None, publie sur tous les stores
    platforms: List[str] = ["facebook"]  # facebook, instagram
    custom_message: Optional[str] = None  # Si None, utilise TEST_MESSAGE de .env
    
    @validator('platforms')
    def validate_platforms(cls, v):
        valid_platforms = ["facebook", "instagram"]
        for platform in v:
            if platform not in valid_platforms:
                raise ValueError(f'Platform must be one of: {valid_platforms}')
        return v

# === UTILITY FUNCTIONS ===
def get_store_config(store: str) -> dict:
    """Récupère la configuration d'un store"""
    if store not in STORES:
        raise ValueError(f"Store inconnu: {store}")
    
    return STORES[store].copy()

async def update_instagram_ids():
    """Mettre à jour automatiquement les IDs Instagram via l'API Graph"""
    try:
        log_app("🔄 Mise à jour automatique des IDs Instagram...", "INFO")
        
        for store_name, config in STORES.items():
            if config.get("access_token") and config.get("fb_page_id"):
                try:
                    # Récupérer le compte Instagram Business associé à la page
                    url = f"{FACEBOOK_GRAPH_URL}/{config['fb_page_id']}"
                    params = {
                        "fields": "instagram_business_account",
                        "access_token": config["access_token"]
                    }
                    
                    response = requests.get(url, params=params, timeout=15)
                    response.raise_for_status()
                    data = response.json()
                    
                    if "instagram_business_account" in data and data["instagram_business_account"]:
                        ig_id = data["instagram_business_account"]["id"]
                        STORES[store_name]["ig_user_id"] = ig_id
                        log_app(f"✅ {store_name}: Instagram ID récupéré → {ig_id}", "SUCCESS")
                    else:
                        log_app(f"⚠️ {store_name}: Aucun compte Instagram Business connecté", "WARNING")
                        
                except Exception as e:
                    log_app(f"❌ {store_name}: Erreur récupération Instagram ID → {str(e)}", "ERROR")
            else:
                log_app(f"⚠️ {store_name}: Token d'accès ou Page ID manquant", "WARNING")
        
        log_app("🎯 Mise à jour des IDs Instagram terminée", "SUCCESS")
        
    except Exception as e:
        log_app(f"❌ Erreur générale mise à jour Instagram: {str(e)}", "ERROR")

async def post_to_facebook(store: str, message: str, product_url: str) -> dict:
    """Publie un post sur la page Facebook correspondante"""
    try:
        log_publish(f"Publication Facebook pour {store}", "INFO")
        
        if store not in STORES:
            raise ValueError(f"Store inconnu: {store}")
        
        creds = get_store_config(store)
        
        if not creds["fb_page_id"] or not creds["access_token"]:
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
        url = f"{FACEBOOK_GRAPH_URL}/{creds['fb_page_id']}/feed"
        payload = {
            "message": message,
            "link": product_url,
            "access_token": creds["access_token"]
        }
        
        log_publish(f"Requête Facebook: POST {url}", "INFO")
        response = requests.post(url, data=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if "id" not in data:
            raise Exception(f"Réponse Facebook invalide: {data}")
        
        log_publish(f"Publication Facebook réussie: {data['id']}", "SUCCESS")
        return data
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Erreur HTTP Facebook: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_msg += f" - {error_data}"
            except:
                error_msg += f" - Status: {e.response.status_code}"
        log_publish(error_msg, "ERROR")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Erreur Facebook: {str(e)}"
        log_publish(error_msg, "ERROR")
        raise Exception(error_msg)

# PATCH 17: FONCTION OBSOLÈTE SUPPRIMÉE - Redirection vers fonction corrigée
# Cette fonction était la source du problème Instagram (chemins locaux Windows)
# Redirige maintenant vers publish_to_instagram() corrigée dans server.py
async def post_to_instagram(store: str, message: str, product_url: str, image_url: str) -> dict:
    """PATCH 17: Redirection vers fonction Instagram corrigée"""
    # Import de la fonction corrigée depuis server.py
    try:
        from server import publish_to_instagram, get_store_config
        store_config = get_store_config(store)
        log_publish(f"🔄 PATCH 17: Redirection vers publish_to_instagram corrigée", "INFO")
        return await publish_to_instagram(store_config, message, product_url, "", image_url, is_video=False)
    except Exception as e:
        log_publish(f"❌ PATCH 17: Erreur redirection - {str(e)}", "ERROR")
        return {"success": False, "error": f"PATCH 17 redirection échouée: {str(e)}"}

async def publish_post(store: str, message: str, product_url: str, image_url: Optional[str] = None, platforms: List[str] = ["facebook", "instagram"]) -> dict:
    """Fonction principale pour publier sur Facebook et/ou Instagram"""
    try:
        log_publish(f"Début publication multi-plateforme pour {store} sur {platforms}", "INFO")
        
        if store not in STORES:
            raise ValueError(f"Store inconnu: {store}")
        
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
        
        # Publication Instagram
        if "instagram" in platforms:
            try:
                if not image_url:
                    raise Exception("Image requise pour Instagram")
                
                ig_result = await post_to_instagram(store, message, product_url, image_url)
                results["instagram_result"] = ig_result
                log_publish("Publication Instagram terminée", "SUCCESS")
            except Exception as e:
                error_msg = f"Échec Instagram: {str(e)}"
                results["errors"].append(error_msg)
                log_publish(error_msg, "ERROR")
        
        # Déterminer le succès global
        success_count = 0
        if "facebook" in platforms and results["facebook_result"]:
            success_count += 1
        if "instagram" in platforms and results["instagram_result"]:
            success_count += 1
        
        results["success"] = success_count > 0 and len(results["errors"]) == 0
        
        if results["success"]:
            log_publish(f"Publication multi-plateforme réussie pour {store}", "SUCCESS")
        else:
            log_publish(f"Publication partiellement échouée pour {store}: {results['errors']}", "WARNING")
        
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

# === ENDPOINTS ===
@app.get("/")
async def root():
    """Endpoint racine"""
    return {"message": "Meta Publishing Platform - Clean Version", "stores": list(STORES.keys())}

@app.get("/api/stores")
async def get_stores():
    """Obtenir la liste des stores configurés"""
    stores_info = {}
    for store_name, config in STORES.items():
        stores_info[store_name] = {
            "name": config.get("name", store_name),
            "facebook_configured": bool(config.get("fb_page_id") and config.get("access_token")),
            "instagram_configured": bool(config.get("ig_user_id") and config.get("access_token")),
            "fb_page_id": config.get("fb_page_id", "Non configuré"),
            "ig_user_id": config.get("ig_user_id", "Non configuré")
        }
    
    return {
        "stores": stores_info,
        "test_mode": PUBLICATION_TEST_MODE,
        "total_stores": len(STORES)
    }

@app.post("/api/post/test")
async def test_publish_endpoint(request: TestPublishRequest):
    """Endpoint pour publier un message de test sur les stores configurés - VERSION CLEAN"""
    try:
        # Mettre à jour les IDs Instagram automatiquement avant publication
        await update_instagram_ids()
        
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
                if platforms_for_store:  # S'il reste des plateformes à publier
                    result = await publish_post(
                        store=store,
                        message=test_message,
                        product_url="https://example.com/test",  # URL de test
                        image_url=None,  # Pas d'image pour le test
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
                else:
                    # Aucune plateforme disponible pour ce store
                    results.append({
                        "store": store,
                        "success": False,
                        "error": "Aucune plateforme configurée disponible",
                        "platforms": []
                    })
                    
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
    
    log_app("🚀 Démarrage serveur clean version...", "START")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
    except KeyboardInterrupt:
        log_app("Arrêt par Ctrl+C", "INFO")
    except Exception as e:
        log_app(f"Erreur serveur: {e}", "ERROR")
    finally:
        log_app("Serveur arrêté", "INFO")