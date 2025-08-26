#!/usr/bin/env python3
"""
Test script pour reproduire et corriger le problème des images non-cliquables sur Facebook pour gizmobbs
"""

import requests
import json
import os
from datetime import datetime

# Configuration de test
BACKEND_URL = "http://localhost:8001"
TEST_IMAGE_PATH = "/app/test_hamac.jpg"

def test_gizmobbs_configuration():
    """Vérifier la configuration actuelle de gizmobbs"""
    print("🔍 Test 1: Vérification de la configuration gizmobbs...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/webhook/info")
        if response.status_code == 200:
            data = response.json()
            gizmobbs_config = data.get("shop_mapping", {}).get("gizmobbs", {})
            
            print(f"📋 Configuration gizmobbs actuelle:")
            print(f"   - Nom: {gizmobbs_config.get('name')}")
            print(f"   - Plateforme: {gizmobbs_config.get('platform')}")
            print(f"   - Plateformes: {gizmobbs_config.get('platforms')}")
            print(f"   - Instagram priority: {gizmobbs_config.get('instagram_priority')}")
            
            if gizmobbs_config.get("platform") == "multi" and gizmobbs_config.get("instagram_priority"):
                print("❌ PROBLÈME IDENTIFIÉ: gizmobbs configuré pour Instagram en priorité")
                print("   → Les images sont publiées sur Instagram (non-cliquables) au lieu de Facebook (cliquables)")
                return True
            else:
                print("✅ Configuration semble correcte")
                return False
        else:
            print(f"❌ Erreur lors de la vérification: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_webhook_with_gizmobbs():
    """Tester le webhook avec gizmobbs pour reproduire le problème"""
    print("\n🧪 Test 2: Simulation du webhook N8N/WooCommerce avec gizmobbs...")
    
    # Créer les données de test
    json_data = {
        "title": "Test Gizmobbs - Image Cliquable",
        "description": "Test pour reproduire le problème des images non-cliquables sur Facebook",
        "url": "https://gizmobbs.com/test-product",
        "store": "gizmobbs"
    }
    
    print(f"📦 Données de test:")
    print(f"   - Produit: {json_data['title']}")
    print(f"   - Store: {json_data['store']}")
    print(f"   - URL: {json_data['url']}")
    
    try:
        if not os.path.exists(TEST_IMAGE_PATH):
            print(f"❌ Image de test non trouvée: {TEST_IMAGE_PATH}")
            return False
            
        # Simuler le webhook multipart comme N8N
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'image': ('test_image.jpg', f, 'image/jpeg')}
            data = {'json_data': json.dumps(json_data)}
            
            print("📤 Envoi de la requête webhook...")
            response = requests.post(
                f"{BACKEND_URL}/api/webhook",
                files=files,
                data=data,
                timeout=30
            )
        
        print(f"📬 Réponse webhook: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook traité avec succès")
            print(f"📊 Résultat:")
            
            # Analyser la réponse pour identifier le problème
            if "instagram" in str(result).lower() and "facebook" not in str(result).lower():
                print("❌ PROBLÈME CONFIRMÉ: Publication dirigée vers Instagram uniquement")
                print("   → Instagram ne supporte pas les images cliquables")
                return True
            elif "facebook" in str(result).lower():
                print("✅ Publication dirigée vers Facebook (images cliquables possibles)")
                return False
            else:
                print(f"🤔 Résultat inattendu: {result}")
                return False
        else:
            print(f"❌ Webhook échoué: {response.status_code}")
            if response.text:
                print(f"   Erreur: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test webhook: {e}")
        return False

def analyze_current_logic():
    """Analyser la logique actuelle du système"""
    print("\n🔍 Test 3: Analyse de la logique actuelle...")
    
    issues_found = []
    
    # Test 1: Configuration gizmobbs
    config_issue = test_gizmobbs_configuration()
    if config_issue:
        issues_found.append("Configuration gizmobbs dirige vers Instagram (non-cliquables)")
    
    # Test 2: Webhook behavior  
    webhook_issue = test_webhook_with_gizmobbs()
    if webhook_issue:
        issues_found.append("Webhook redirige gizmobbs vers Instagram au lieu de Facebook")
    
    return issues_found

def propose_solution():
    """Proposer une solution pour corriger le problème"""
    print("\n💡 SOLUTION PROPOSÉE:")
    print("=" * 60)
    
    print("🎯 PROBLÈME IDENTIFIÉ:")
    print("   - gizmobbs configuré avec 'instagram_priority: True'")
    print("   - Les publications sont dirigées vers Instagram")
    print("   - Instagram ne supporte PAS les images cliquables")
    print("   - L'utilisateur veut des images cliquables sur Facebook")
    
    print("\n🔧 SOLUTION:")
    print("   1. Modifier la configuration gizmobbs dans SHOP_PAGE_MAPPING")
    print("   2. Changer 'platform' de 'multi' à 'facebook' ou 'multi' sans instagram_priority")  
    print("   3. Ou ajouter support pour publication Facebook + Instagram simultanée")
    print("   4. Utiliser la logique d'images cliquables existante pour Facebook")
    
    print("\n📋 MODIFICATIONS NÉCESSAIRES:")
    print("   - server.py: SHOP_PAGE_MAPPING['gizmobbs']")
    print("   - Retirer 'instagram_priority: True' ou ajouter 'facebook_priority: True'")
    print("   - S'assurer que les images utilisent l'endpoint Facebook /photos avec comment_link")
    
def main():
    """Fonction principale de test et diagnostic"""
    print("🔍 DIAGNOSTIC: Images non-cliquables gizmobbs sur Facebook")
    print("=" * 60)
    print(f"⏰ Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Objectif: Identifier pourquoi les images gizmobbs ne sont pas cliquables sur Facebook")
    
    # Analyser le problème
    issues = analyze_current_logic()
    
    print("\n📊 RÉSUMÉ DU DIAGNOSTIC:")
    print("=" * 40)
    
    if issues:
        print("❌ PROBLÈMES IDENTIFIÉS:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        propose_solution()
        
        print(f"\n🎯 STATUT: PROBLÈME CONFIRMÉ - SOLUTION DISPONIBLE")
        return True
    else:
        print("✅ Aucun problème détecté dans la configuration actuelle")
        print("🤔 Le problème pourrait être ailleurs (authentification, permissions, etc.)")
        return False

if __name__ == "__main__":
    main()