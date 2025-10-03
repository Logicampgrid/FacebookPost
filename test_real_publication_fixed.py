#!/usr/bin/env python3
"""
Test de publication réelle CORRIGÉ pour diagnostiquer les problèmes
"""

import requests
import json
import os
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8001"

def test_publication_webhook_fixed():
    """Test de publication via webhook avec mode réel - FORMAT CORRIGÉ"""
    
    print("🧪 TEST PUBLICATION RÉELLE CORRIGÉ - Diagnostic des problèmes")
    print("=" * 60)
    
    # 1. Test santé du système
    print("\n1. 🔍 Test santé système...")
    try:
        health_response = requests.get(f"{API_BASE}/api/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ Système en ligne")
        else:
            print(f"❌ Problème santé système: {health_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erreur connexion système: {e}")
        return
    
    # 2. Test webhook avec publication réelle - FORMAT CORRIGÉ
    print("\n2. 📤 Test publication webhook (MODE RÉEL) - FORMAT CORRIGÉ...")
    
    # Créer un fichier test temporaire
    test_image_path = "/app/backend/test_real_pub_fixed.jpg"
    if not os.path.exists(test_image_path):
        # Créer un fichier test basique
        with open(test_image_path, "wb") as f:
            f.write(b"test_image_data")
    
    try:
        print(f"🔧 Mode test: FALSE (publication réelle)")
        print(f"📝 Format: Champs directs (pas de jsonData)")
        
        # Préparer la requête multipart avec champs directs
        files = {
            'file': ('test_real_pub_fixed.jpg', open(test_image_path, 'rb'), 'image/jpeg')
        }
        
        # CORRECTION: Envoyer les champs directement, pas dans jsonData
        data = {
            'store': 'gizmobbs',  # Le Berger Blanc Suisse
            'title': '🧪 Test Publication Réelle PATCH 21',
            'url': 'https://test.com',
            'description': 'Test de publication réelle CORRIGÉ pour diagnostiquer les problèmes. Mode PUBLICATION_TEST_MODE=false activé. PATCH 21 appliqué.'
        }
        
        print(f"📝 Données directes: {data}")
        
        # Envoyer la requête
        print("\n📡 Envoi requête webhook avec champs directs...")
        response = requests.post(
            f"{API_BASE}/api/webhook",
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text[:1000]}...")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ WEBHOOK TRAITÉ")
            
            # Analyser la réponse
            if "success" in result:
                if result["success"]:
                    print("✅ Publication marquée comme réussie")
                    
                    # Vérifier les détails de publication
                    if "facebook_result" in result:
                        fb_result = result["facebook_result"]
                        if fb_result.get("success"):
                            print(f"✅ Facebook: {fb_result.get('post_id', 'ID non fourni')}")
                        else:
                            print(f"❌ Facebook échoué: {fb_result.get('error', 'Erreur inconnue')}")
                    
                    if "instagram_result" in result:
                        ig_result = result["instagram_result"]
                        if ig_result.get("success"):
                            print(f"✅ Instagram: {ig_result.get('media_id', 'ID non fourni')}")
                        else:
                            print(f"❌ Instagram échoué: {ig_result.get('error', 'Erreur inconnue')}")
                            
                else:
                    print(f"❌ Publication échouée: {result.get('error', 'Erreur inconnue')}")
                    
                # Afficher le mode test pour vérification
                if "test_mode" in result:
                    test_mode = result["test_mode"]
                    if test_mode:
                        print(f"⚠️ Mode test détecté: {test_mode} (devrait être False)")
                    else:
                        print(f"✅ Mode test correctement désactivé: {test_mode}")
            else:
                print("⚠️ Format de réponse inattendu")
                print(f"📄 Réponse complète: {result}")
        else:
            print(f"❌ ERREUR WEBHOOK: {response.status_code}")
            print(f"📄 Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ ERREUR REQUÊTE: {e}")
    
    finally:
        # Nettoyer le fichier test
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
    
    print("\n" + "=" * 60)
    print("🔍 DIAGNOSTIC CORRIGÉ TERMINÉ")

if __name__ == "__main__":
    test_publication_webhook_fixed()