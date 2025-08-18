#!/usr/bin/env python3
"""
Test pour vérifier la fonctionnalité d'images cliquables
"""

import asyncio
import requests
import json
from datetime import datetime

# Configuration
API_BASE = "https://carry-on-174.preview.emergentagent.com"

def test_product_publication_with_clickable_image():
    """Test de publication d'un produit avec image cliquable"""
    
    print("🧪 TEST: Publication de produit avec image cliquable")
    print("=" * 60)
    
    # Test data
    test_payload = {
        "title": "Chaise Design Premium - Test Clickable",
        "description": "Belle chaise moderne avec image cliquable. Cliquez sur l'image pour voir le produit !",
        "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800",
        "product_url": "https://example.com/produit/chaise-design-premium-test"
    }
    
    print(f"📝 Données de test:")
    print(f"   - Titre: {test_payload['title']}")
    print(f"   - Image: {test_payload['image_url'][:50]}...")
    print(f"   - URL cible: {test_payload['product_url']}")
    
    try:
        # Faire l'appel API
        print(f"\n🚀 Envoi de la requête vers {API_BASE}/api/publishProduct...")
        
        response = requests.post(
            f"{API_BASE}/api/publishProduct",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📡 Statut HTTP: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCÈS !")
            print(f"   - Post Facebook ID: {result.get('facebook_post_id', 'Unknown')}")
            print(f"   - Page: {result.get('page_name', 'Unknown')}")
            print(f"   - URL média: {result.get('media_url', 'Unknown')}")
            print(f"   - Publié à: {result.get('published_at', 'Unknown')}")
            
            print(f"\n🎯 FONCTIONNALITÉ CLIQUABLE:")
            print(f"   - L'image devrait être cliquable sur Facebook")
            print(f"   - Clic sur l'image → Redirection vers: {test_payload['product_url']}")
            print(f"   - Type de post: Link post avec picture parameter")
            
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"❌ ÉCHEC:")
            print(f"   - Erreur: {error_data}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERREUR DE CONNEXION:")
        print(f"   - {str(e)}")
    except Exception as e:
        print(f"❌ ERREUR INATTENDUE:")
        print(f"   - {str(e)}")
    
    print("\n" + "=" * 60)

def test_api_health():
    """Test de santé de l'API"""
    print("🏥 TEST: Santé de l'API")
    
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ API accessible")
            return True
        else:
            print(f"❌ API problème: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API inaccessible: {e}")
        return False

def test_manual_post_with_clickable_image():
    """Test manuel pour créer un post avec image cliquable"""
    print("\n📋 INSTRUCTIONS POUR TEST MANUEL:")
    print("=" * 60)
    print("1. Connectez-vous à l'application: https://carry-on-174.preview.emergentagent.com")
    print("2. Authentifiez-vous avec Facebook")
    print("3. Créez un nouveau post avec:")
    print("   - ✅ Une image (uploadée)")
    print("   - ✅ Un lien dans le contenu (ex: https://example.com/produit)")
    print("   - ✅ Ou un lien dans le commentaire")
    print("4. Vérifiez l'indicateur 'Images cliquables activées' 🎯")
    print("5. Publiez le post")
    print("6. Sur Facebook, cliquez sur l'image → doit rediriger vers le lien")
    print("=" * 60)

if __name__ == "__main__":
    print(f"🧪 TESTS DE LA FONCTIONNALITÉ IMAGES CLIQUABLES")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test 1: Santé de l'API
    if test_api_health():
        print()
        # Test 2: Publication avec image cliquable
        test_product_publication_with_clickable_image()
    
    # Test 3: Instructions manuelles
    test_manual_post_with_clickable_image()