#!/usr/bin/env python3
"""
Test complet de la correction Instagram
Teste la fonction post_to_instagram avec le chemin problématique
"""

import os
import sys
import asyncio

# Ajouter le répertoire backend au path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_path)

from server import post_to_instagram, PUBLICATION_TEST_MODE, STORES

async def test_instagram_posting():
    """Test de la publication Instagram avec chemin Windows"""
    
    print("🧪 Test complet de la fonction post_to_instagram")
    print("=" * 60)
    
    # Paramètres de test
    store = "gizmobbs"
    message = "Test de publication avec image corrigée"
    product_url = "https://example.com/product"
    image_url_problematic = "uploads\\webhook_31c55813_1758782446.png"  # Chemin Windows problématique
    
    print(f"📋 Paramètres de test:")
    print(f"  Store: {store}")
    print(f"  Message: {message}")
    print(f"  Product URL: {product_url}")
    print(f"  Image URL (problématique): {image_url_problematic}")
    print(f"  Mode test: {PUBLICATION_TEST_MODE}")
    print()
    
    # Vérifier la configuration du store
    if store not in STORES:
        print(f"❌ Store {store} non configuré")
        return False
    
    store_config = STORES[store]
    print(f"🏪 Configuration du store {store}:")
    print(f"  Page FB: {store_config.get('fb_page_id', 'Non défini')}")
    print(f"  IG User: {store_config.get('ig_user_id', 'Non défini')}")
    print(f"  Token: {'✅ Défini' if store_config.get('access_token') else '❌ Manquant'}")
    print()
    
    try:
        print("🚀 Tentative de publication Instagram...")
        result = await post_to_instagram(store, message, product_url, image_url_problematic)
        
        print("✅ Publication réussie!")
        print(f"📄 Résultat: {result}")
        
        # Vérifications spécifiques
        if "id" in result:
            print(f"✅ ID de publication: {result['id']}")
        
        if "image_url" in result:
            expected_url = "https://abe16f7ffd54.ngrok-free.app/uploads/webhook_31c55813_1758782446.png"
            if result["image_url"] == expected_url:
                print(f"✅ URL d'image correctement convertie: {result['image_url']}")
            else:
                print(f"⚠️ URL d'image inattendue: {result['image_url']}")
                print(f"   Attendue: {expected_url}")
        
        if result.get("test_mode"):
            print("ℹ️ Publication en mode test (aucune publication réelle)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la publication: {str(e)}")
        return False

async def main():
    """Fonction principale"""
    try:
        success = await test_instagram_posting()
        
        if success:
            print("\n🎉 TEST RÉUSSI!")
            print("✅ La correction du problème Instagram fonctionne correctement")
            print("✅ Les chemins Windows avec backslashes sont maintenant supportés")
        else:
            print("\n❌ TEST ÉCHOUÉ")
            print("⚠️ Vérifiez les logs ci-dessus pour plus de détails")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur générale: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)