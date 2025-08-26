#!/usr/bin/env python3
"""
Test direct de la logique d'images cliquables pour vérifier que notre correction fonctionne
"""

import sys
import os
import asyncio

# Ajouter le chemin du backend pour importer les fonctions
sys.path.append('/app/backend')

# Importer les fonctions nécessaires
from server import post_to_facebook, Post
from datetime import datetime
import uuid

async def test_clickable_logic():
    """Tester la logique d'images cliquables directement"""
    print("🧪 Test de la logique d'images cliquables...")
    
    # Créer un post de test avec un produit link
    post_data = {
        "id": str(uuid.uuid4()),
        "user_id": "test_user",
        "content": "Test produit gizmobbs avec image cliquable",
        "media_urls": ["/api/uploads/test_image.jpg"],
        "link_metadata": [{
            "url": "https://gizmobbs.com/test-product",
            "title": "Test Product",
            "description": "Test description",
            "type": "product"
        }],
        "comment_link": "https://gizmobbs.com/test-product",
        "target_type": "page",
        "target_id": "test_page_id",
        "target_name": "Test Page",
        "platform": "facebook",
        "status": "published",
        "created_at": datetime.utcnow(),
        "published_at": datetime.utcnow()
    }
    
    # Créer un objet Post
    test_post = Post(**post_data)
    
    # Token de test pour déclencher la simulation
    test_token = "test_clickable_token"
    
    print(f"📦 Post de test créé:")
    print(f"   - Contenu: {test_post.content}")
    print(f"   - Image: {test_post.media_urls[0]}")
    print(f"   - Lien produit: {test_post.comment_link}")
    print(f"   - Target: {test_post.target_name}")
    
    try:
        # Tester la fonction post_to_facebook
        print(f"\n📤 Test de post_to_facebook avec logique cliquable...")
        result = await post_to_facebook(test_post, test_token)
        
        print(f"\n📊 Résultat:")
        if result:
            print(f"✅ Publication réussie: {result}")
            
            # Vérifier si le résultat indique une image cliquable
            if "clickable" in str(result).lower() or result.get("clickable_image_configured"):
                print("✅ CORRECTION CONFIRMÉE: Logique d'images cliquables activée!")
                return True
            else:
                print("❌ Logique d'images cliquables non détectée dans le résultat")
                return False
        else:
            print("❌ Aucun résultat retourné")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

async def main():
    """Fonction principale de test"""
    print("🔍 TEST DIRECT DE LA LOGIQUE D'IMAGES CLIQUABLES")
    print("=" * 60)
    
    success = await test_clickable_logic()
    
    print(f"\n📊 RÉSULTAT FINAL:")
    if success:
        print("✅ La correction des images cliquables fonctionne!")
        print("🎯 Les images gizmobbs seront maintenant cliquables sur Facebook")
    else:
        print("❌ La logique d'images cliquables nécessite des ajustements")
        print("🔧 Vérification supplémentaire nécessaire")

if __name__ == "__main__":
    asyncio.run(main())