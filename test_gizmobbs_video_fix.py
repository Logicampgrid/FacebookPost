#!/usr/bin/env python3
"""
Test spécifique pour corriger le problème gizmobbs avec vidéos et Instagram
"""
import os
import sys
import json
import asyncio
import requests
import tempfile
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration test
API_BASE = "http://localhost:8001"
TEST_STORE = "gizmobbs"

def log_test(message: str, level: str = "INFO"):
    """Logging pour les tests"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [GIZMO_TEST] {message}")

def create_test_video():
    """Crée une vidéo de test basique (fichier avec en-tête MP4)"""
    # Créer un fichier avec un en-tête MP4 minimal pour les tests
    mp4_header = b'\\x00\\x00\\x00\\x20ftypmp41\\x00\\x00\\x00\\x00mp41isom'
    test_content = mp4_header + b'Test video content for gizmobbs' * 100
    
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
        temp_file.write(test_content)
        return temp_file.name

async def test_health_check():
    """Test de connectivité API"""
    try:
        log_test("Test connectivité API...", "TEST")
        response = requests.get(f"{API_BASE}/api/health", timeout=10)
        if response.status_code == 200:
            log_test("✅ API accessible", "SUCCESS")
            return True
        else:
            log_test(f"❌ API inaccessible: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log_test(f"❌ Erreur connexion API: {e}", "ERROR")
        return False

async def test_ftp_direct():
    """Test FTP direct depuis l'API"""
    try:
        log_test("Test FTP direct via API...", "TEST")
        
        # Créer un fichier de test
        test_video_path = create_test_video()
        log_test(f"Fichier test créé: {test_video_path}", "INFO")
        
        # Test upload FTP via l'API
        with open(test_video_path, 'rb') as video_file:
            files = {'file': ('test_gizmo.mp4', video_file, 'video/mp4')}
            data = {
                'store': TEST_STORE,
                'title': 'Test Gizmobbs Video',
                'description': 'Test de correction du problème FTP et Instagram',
                'url': 'https://www.logicamp.org/wordpress/gizmobbs/'
            }
            
            log_test("Envoi webhook avec vidéo...", "TEST")
            response = requests.post(f"{API_BASE}/api/webhook", files=files, data=data, timeout=60)
            
            log_test(f"Réponse webhook: {response.status_code}", "INFO")
            
            if response.status_code == 200:
                result = response.json()
                log_test(f"Réponse: {json.dumps(result, indent=2)}", "SUCCESS")
                return True
            else:
                log_test(f"❌ Échec webhook: {response.status_code} - {response.text}", "ERROR")
                return False
                
    except Exception as e:
        log_test(f"❌ Erreur test FTP: {e}", "ERROR")
        return False
    finally:
        # Nettoyer
        try:
            os.unlink(test_video_path)
        except:
            pass

async def test_webhook_text_only():
    """Test webhook texte seulement (pour vérifier l'API de base)"""
    try:
        log_test("Test webhook texte simple...", "TEST")
        
        data = {
            'store': TEST_STORE,
            'title': 'Test Gizmobbs Texte',
            'description': 'Test de publication texte seulement',
            'url': 'https://www.logicamp.org/wordpress/gizmobbs/'
        }
        
        response = requests.post(f"{API_BASE}/api/webhook", data=data, timeout=30)
        
        log_test(f"Réponse webhook texte: {response.status_code}", "INFO")
        
        if response.status_code == 200:
            result = response.json()
            log_test(f"Réponse: {json.dumps(result, indent=2)}", "SUCCESS")
            return True
        else:
            log_test(f"❌ Échec webhook texte: {response.status_code} - {response.text}", "ERROR")
            return False
            
    except Exception as e:
        log_test(f"❌ Erreur test webhook texte: {e}", "ERROR")
        return False

async def test_store_config():
    """Test configuration du store gizmobbs"""
    try:
        log_test("Test configuration store gizmobbs...", "TEST")
        
        response = requests.get(f"{API_BASE}/api/stores", timeout=10)
        
        if response.status_code == 200:
            stores = response.json()
            log_test(f"Stores disponibles: {list(stores.keys())}", "INFO")
            
            if TEST_STORE in stores:
                config = stores[TEST_STORE]
                log_test(f"Configuration {TEST_STORE}:", "INFO")
                log_test(f"  - Nom: {config.get('name', 'Non défini')}", "INFO")
                log_test(f"  - Page FB: {config.get('fb_page_id', 'Non défini')}", "INFO")
                log_test(f"  - Instagram: {config.get('ig_user_id', 'Non défini')}", "INFO")
                log_test(f"  - Token: {'✅ Défini' if config.get('access_token') else '❌ Manquant'}", "INFO")
                return True
            else:
                log_test(f"❌ Store {TEST_STORE} non trouvé", "ERROR")
                return False
        else:
            log_test(f"❌ Impossible de récupérer les stores: {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test(f"❌ Erreur test store config: {e}", "ERROR")
        return False

async def run_complete_test():
    """Test complet de diagnostic"""
    log_test("=== DÉBUT DIAGNOSTIC GIZMOBBS ===", "TEST")
    
    results = {
        "health_check": False,
        "store_config": False,
        "webhook_text": False,
        "webhook_video": False
    }
    
    # Test 1: Santé de l'API
    results["health_check"] = await test_health_check()
    
    # Test 2: Configuration du store
    results["store_config"] = await test_store_config()
    
    # Test 3: Webhook texte simple
    results["webhook_text"] = await test_webhook_text_only()
    
    # Test 4: Webhook avec vidéo (problème principal)
    if results["health_check"]:
        results["webhook_video"] = await test_ftp_direct()
    
    # Résumé
    log_test("=== RÉSUMÉ DIAGNOSTIC ===", "TEST")
    for test_name, result in results.items():
        status = "✅ OK" if result else "❌ ÉCHEC"
        log_test(f"{test_name}: {status}", "INFO")
    
    # Recommandations
    log_test("=== RECOMMANDATIONS ===", "TEST")
    if not results["health_check"]:
        log_test("🔧 Redémarrer le serveur backend", "WARNING")
    if not results["store_config"]:
        log_test("🔧 Vérifier la configuration du store gizmobbs", "WARNING")
    if not results["webhook_video"]:
        log_test("🔧 Problème FTP/Instagram confirmé - correction nécessaire", "WARNING")
    
    if all(results.values()):
        log_test("🎉 Tous les tests passent - problème résolu!", "SUCCESS")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(run_complete_test())
    success = all(results.values())
    exit(0 if success else 1)