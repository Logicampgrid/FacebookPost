#!/usr/bin/env python3
"""
Test simple de la correction Instagram - Test de conversion des chemins locaux
"""

import requests
import json

def test_correction():
    print("🔍 TEST: Correction du problème Instagram")
    print("=" * 60)
    
    # Simuler un webhook avec une image existante dans uploads/
    test_image = "webhook_test_correction.jpg"  # On utilise un fichier existant
    
    webhook_data = {
        "store": "gizmobbs",
        "title": "Test de correction Instagram",
        "url": "https://www.logicamp.org/wordpress/produit/test-correction/",
        "description": "Test pour corriger le problème Instagram avec upload FTP automatique",
        "image_url": f"uploads/{test_image}",  # Chemin local qui causait le problème
        "platforms": ["facebook", "instagram"]
    }
    
    print(f"📤 Envoi webhook de test avec image locale: uploads/{test_image}")
    print(f"🎯 Store cible: {webhook_data['store']}")
    print(f"📱 Plateformes: {webhook_data['platforms']}")
    
    try:
        response = requests.post(
            "http://localhost:8001/api/webhook", 
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"\n📋 Réponse serveur: HTTP {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook traité avec succès!")
            
            # Analyser la réponse pour voir si Instagram a fonctionné
            success = result.get("success", False)
            status = result.get("status", "unknown")
            
            print(f"📊 Status général: {status}")
            print(f"🎯 Succès: {success}")
            
            if "error" in result:
                errors = result["error"] if isinstance(result["error"], list) else [result["error"]]
                print("❌ Erreurs détectées:")
                for error in errors:
                    if "Instagram" in error:
                        print(f"   📱 Instagram: {error}")
                    else:
                        print(f"   📋 Général: {error}")
            
            if "platforms" in result:
                print(f"📱 Plateformes traitées: {result['platforms']}")
            
            # Analyser plus en détail si possible
            if isinstance(result, dict):
                print("\n📋 Réponse complète:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"📋 Détail erreur: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"📋 Réponse brute: {response.text}")
        
    except requests.exceptions.Timeout:
        print("⏰ Timeout - Le traitement prend trop de temps")
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion au serveur")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    test_correction()