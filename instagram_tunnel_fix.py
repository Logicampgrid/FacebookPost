#!/usr/bin/env python3
"""
Instagram Tunnel Fix - Résolution des problèmes de publication Instagram

Ce script diagnostique et corrige les problèmes de publication Instagram
pour créer un "tunnel gratuit" de publication.
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8001"
BACKEND_URL = "https://social-media-bridge.preview.emergentagent.com"

def test_connection():
    """Test la connexion au backend"""
    try:
        response = requests.get(f"{API_BASE}/api/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend connecté")
            print(f"   Status: {data['status']}")
            print(f"   MongoDB: {data['mongodb']}")
            print(f"   Utilisateurs: {data['database']['users_count']}")
            return True
        else:
            print(f"❌ Backend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connexion error: {e}")
        return False

def test_instagram_diagnosis():
    """Test le diagnostic Instagram complet"""
    try:
        response = requests.get(f"{API_BASE}/api/debug/instagram-complete-diagnosis")
        if response.status_code == 200:
            data = response.json()
            print("\n📱 DIAGNOSTIC INSTAGRAM:")
            print(f"   Status: {data['status']}")
            print(f"   Utilisateur trouvé: {data['authentication']['user_found']}")
            print(f"   Business Managers: {data['authentication']['business_managers_count']}")
            print(f"   Comptes Instagram: {len(data['instagram_accounts'])}")
            
            if data['issues']:
                print("   ❌ Problèmes:")
                for issue in data['issues']:
                    print(f"      {issue}")
            
            if data['recommendations']:
                print("   💡 Recommandations:")
                for rec in data['recommendations']:
                    print(f"      {rec}")
            
            return data
        else:
            print(f"❌ Instagram diagnosis error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Instagram diagnosis error: {e}")
        return None

def test_webhook_endpoint():
    """Test l'endpoint webhook pour publication automatique"""
    try:
        response = requests.get(f"{API_BASE}/api/webhook")
        if response.status_code == 200:
            data = response.json()
            print("\n🌐 WEBHOOK ENDPOINT:")
            print("   ✅ Endpoint disponible")
            print(f"   URL: {BACKEND_URL}/api/webhook")
            print("   Méthode: POST (multipart/form-data)")
            print("   Champs requis: image, json_data")
            
            if 'available_stores' in data:
                print(f"   Magasins supportés: {', '.join(data['available_stores'])}")
            
            return True
        else:
            print(f"❌ Webhook error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return False

def check_instagram_configuration():
    """Vérifie la configuration Instagram dans le mapping des magasins"""
    try:
        response = requests.get(f"{API_BASE}/api/webhook")
        if response.status_code == 200:
            data = response.json()
            shop_mapping = data.get('shop_mapping', {})
            
            print("\n⚙️ CONFIGURATION INSTAGRAM:")
            instagram_shops = []
            for shop, config in shop_mapping.items():
                if 'instagram' in config.get('platforms', []):
                    instagram_shops.append(shop)
                    print(f"   ✅ {shop}:")
                    print(f"      Instagram: @{config.get('instagram_username', 'N/A')}")
                    print(f"      Plateformes: {', '.join(config.get('platforms', []))}")
            
            if instagram_shops:
                print(f"\n✅ {len(instagram_shops)} magasins configurés pour Instagram")
                return instagram_shops
            else:
                print("\n❌ Aucun magasin configuré pour Instagram")
                return []
        else:
            return []
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return []

def create_test_publication():
    """Crée une publication de test pour vérifier le tunnel Instagram"""
    print("\n🧪 TEST DE PUBLICATION (simulation):")
    print("   Pour tester la publication Instagram, vous devez:")
    print("   1. Vous connecter via l'interface web (http://localhost:3000)")
    print("   2. Connecter votre compte Facebook Business Manager")
    print("   3. Vérifier que @logicamp_berger est accessible")
    print("   4. Utiliser l'endpoint webhook ou l'interface pour publier")
    
    # Exemple de requête webhook
    example_curl = f"""
    curl -X POST "{BACKEND_URL}/api/webhook" \\
      -F "image=@/path/to/image.jpg" \\
      -F 'json_data={{"title":"Test Instagram","description":"Test de publication via tunnel gratuit","url":"https://example.com","store":"gizmobbs"}}'
    """
    
    print(f"\n📝 Exemple de requête webhook:")
    print(example_curl)

def main():
    """Fonction principale de diagnostic et correction"""
    print("🚀 INSTAGRAM TUNNEL - DIAGNOSTIC ET CORRECTION")
    print("=" * 50)
    
    # Test 1: Connexion backend
    if not test_connection():
        print("❌ Impossible de continuer sans connexion backend")
        sys.exit(1)
    
    # Test 2: Diagnostic Instagram
    instagram_status = test_instagram_diagnosis()
    
    # Test 3: Endpoint webhook
    webhook_ok = test_webhook_endpoint()
    
    # Test 4: Configuration Instagram
    instagram_shops = check_instagram_configuration()
    
    # Test 5: Exemple de publication
    create_test_publication()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DU DIAGNOSTIC:")
    print(f"   Backend: ✅")
    print(f"   Webhook: {'✅' if webhook_ok else '❌'}")
    print(f"   Configuration Instagram: {'✅' if instagram_shops else '❌'}")
    print(f"   Magasins avec Instagram: {len(instagram_shops)}")
    
    if instagram_status and not instagram_status['authentication']['user_found']:
        print("\n🔑 ÉTAPE SUIVANTE REQUISE:")
        print("   Connectez-vous via http://localhost:3000")
        print("   avec votre compte Facebook Business Manager")
        print("   pour activer le tunnel Instagram gratuit!")
    
    print(f"\n🌐 URL du tunnel: {BACKEND_URL}/api/webhook")

if __name__ == "__main__":
    main()