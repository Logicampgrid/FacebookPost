#!/usr/bin/env python3
"""
Test du webhook endpoint pour FacebookPost
"""

import requests
import json
from datetime import datetime

def log_test(message: str, level: str = "INFO"):
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [WEBHOOK] {message}")

def test_webhook_endpoint():
    """Test l'endpoint webhook"""
    try:
        log_test("=== TEST ENDPOINT WEBHOOK ===", "TEST")
        
        # Configuration de test
        base_url = "http://localhost:8001"  # URL locale du backend
        webhook_url = f"{base_url}/api/webhook"
        
        log_test(f"Test URL: {webhook_url}", "INFO")
        
        # Test 1: GET request (pour vérification simple)
        log_test("Test 1/3 - GET request", "TEST")
        try:
            response = requests.get(webhook_url, timeout=10)
            log_test(f"GET Response: {response.status_code}", "INFO")
            if response.status_code == 200:
                log_test("✅ GET request réussie", "SUCCESS")
            else:
                log_test(f"⚠️ GET status code: {response.status_code}", "WARNING")
        except Exception as e:
            log_test(f"❌ GET request échouée: {e}", "ERROR")
        
        # Test 2: POST request avec données valides
        log_test("Test 2/3 - POST request avec données", "TEST")
        test_data = {
            "store": "gizmobbs",
            "message": "Test automatique du webhook FacebookPost",
            "product_url": "https://example.com/produit-test",
            "image_url": "https://via.placeholder.com/800x600.jpg",
            "platforms": ["facebook"]
        }
        
        try:
            response = requests.post(
                webhook_url, 
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            log_test(f"POST Response: {response.status_code}", "INFO")
            
            if response.status_code == 200:
                result = response.json()
                log_test("✅ POST request réussie", "SUCCESS")
                log_test(f"Response: {json.dumps(result, indent=2)}", "INFO")
                
                if result.get("success"):
                    log_test("🎉 Webhook traité avec succès !", "SUCCESS")
                else:
                    log_test(f"⚠️ Webhook traité mais avec erreurs: {result.get('error', 'Erreur inconnue')}", "WARNING")
            else:
                log_test(f"❌ POST status code: {response.status_code}", "ERROR")
                try:
                    error_data = response.json()
                    log_test(f"Error details: {error_data}", "ERROR")
                except:
                    log_test(f"Error text: {response.text}", "ERROR")
                    
        except Exception as e:
            log_test(f"❌ POST request échouée: {e}", "ERROR")
        
        # Test 3: Health check du backend
        log_test("Test 3/3 - Health check", "TEST")
        try:
            health_url = f"{base_url}/api/health"
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                log_test("✅ Backend health check OK", "SUCCESS")
                log_test(f"Status: {health_data.get('status', 'Unknown')}", "INFO")
            else:
                log_test(f"⚠️ Health check status: {response.status_code}", "WARNING")
        except Exception as e:
            log_test(f"❌ Health check échoué: {e}", "ERROR")
        
        log_test("=== TEST WEBHOOK TERMINÉ ===", "SUCCESS")
        
    except Exception as e:
        log_test(f"❌ ERREUR GÉNÉRALE: {e}", "ERROR")

def test_webhook_with_video():
    """Test webhook avec données vidéo"""
    log_test("=== TEST WEBHOOK VIDÉO ===", "TEST")
    
    base_url = "http://localhost:8001"
    webhook_url = f"{base_url}/api/webhook"
    
    # Données de test pour vidéo
    video_data = {
        "store": "gizmobbs", 
        "message": "Test publication vidéo automatique",
        "product_url": "https://example.com/produit-video",
        "video_url": "https://sample-videos.com/zip/10/mp4/SampleVideo_360x240_1mb.mp4",
        "platforms": ["facebook", "instagram"]
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=video_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        log_test(f"Video POST Response: {response.status_code}", "INFO")
        
        if response.status_code == 200:
            result = response.json()
            log_test("✅ Webhook vidéo traité", "SUCCESS")
            
            if result.get("success"):
                log_test("🎥 Publication vidéo réussie !", "SUCCESS")
                
                # Vérifier que les bons endpoints ont été utilisés
                if "facebook_result" in result:
                    log_test("✅ Facebook vidéo: endpoint /videos utilisé", "SUCCESS")
                if "instagram_result" in result:
                    log_test("✅ Instagram vidéo: endpoint /media REELS utilisé", "SUCCESS")
            else:
                log_test(f"⚠️ Erreur publication vidéo: {result.get('error')}", "WARNING")
        else:
            log_test(f"❌ Webhook vidéo échoué: {response.status_code}", "ERROR")
            
    except Exception as e:
        log_test(f"❌ Erreur test vidéo: {e}", "ERROR")

if __name__ == "__main__":
    print()
    print("🚀 TEST DES ENDPOINTS WEBHOOK - FacebookPost")
    print("=" * 60)
    
    # Test de base
    test_webhook_endpoint()
    
    print()
    # Test vidéo
    test_webhook_with_video()
    
    print()
    print("=" * 60)
    print("✅ Tests webhook terminés")