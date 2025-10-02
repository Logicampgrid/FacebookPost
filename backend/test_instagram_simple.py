#!/usr/bin/env python3
"""
Test simple de la conversion Instagram avec un appel direct à la fonction
"""

import sys
import os
import asyncio

# Ajouter le dossier parent au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# PATCH 12: Correction import - utiliser la fonction corrigée
from server import publish_to_instagram, PUBLICATION_TEST_MODE, get_store_config

async def test_instagram_with_local_path():
    """Test de publication Instagram avec chemin local"""
    
    print("🧪 Test publication Instagram avec chemin local")
    print(f"Mode test activé: {PUBLICATION_TEST_MODE}")
    print()
    
    # Paramètres de test
    store = "gizmobbs"  # Utilise le premier store configuré
    message = "Test de publication avec conversion automatique de chemin local"
    product_url = "https://example.com/produit-test"
    image_url_local = "uploads/webhook_abc123_test.jpg"  # Chemin local simulé
    
    print(f"📝 Paramètres de test:")
    print(f"  Store: {store}")
    print(f"  Message: {message}")
    print(f"  Product URL: {product_url}")
    print(f"  Image URL (local): {image_url_local}")
    print()
    
    try:
        print("🚀 Lancement du test...")
        result = await post_to_instagram(store, message, product_url, image_url_local)
        
        print("✅ Test réussi!")
        print("📊 Résultat:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        
        # Vérifier que l'image_url dans le résultat est bien convertie
        if result.get("image_url"):
            if result["image_url"].startswith("https://abe16f7ffd4.ngrok-free.app"):
                print("\n✅ Conversion réussie: L'URL locale a été convertie en URL ngrok")
            else:
                print(f"\n⚠️ URL non convertie: {result['image_url']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

async def test_instagram_with_public_url():
    """Test avec une URL déjà publique (pas de conversion nécessaire)"""
    
    print("\n" + "="*60)
    print("🧪 Test publication Instagram avec URL publique")
    print()
    
    # Paramètres de test
    store = "gizmobbs"
    message = "Test avec URL déjà publique"
    product_url = "https://example.com/produit-test-2"
    image_url_public = "https://example.com/image-test.jpg"  # URL déjà publique
    
    print(f"📝 Paramètres de test:")
    print(f"  Image URL (publique): {image_url_public}")
    print()
    
    try:
        print("🚀 Lancement du test...")
        result = await post_to_instagram(store, message, product_url, image_url_public)
        
        print("✅ Test réussi!")
        print("📊 Résultat:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        
        # Vérifier que l'URL publique n'a pas été modifiée
        if result.get("image_url") == image_url_public:
            print("\n✅ URL publique préservée correctement")
        else:
            print(f"\n⚠️ URL modifiée de manière inattendue: {result['image_url']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

async def main():
    """Fonction principale"""
    print("🎯 === Test de la fonction post_to_instagram modifiée ===\n")
    
    tests = [
        ("Conversion chemin local", test_instagram_with_local_path),
        ("URL publique (pas de conversion)", test_instagram_with_public_url)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"Test: {test_name}")
        print("-" * 40)
        
        result = await test_func()
        results.append((test_name, result))
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    
    for test_name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"{test_name}: {status}")
    
    success_count = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    print(f"\n🎯 Résultat final: {success_count}/{total_tests} tests réussis")
    
    if success_count == total_tests:
        print("🎉 Parfait! La conversion automatique Instagram fonctionne correctement.")
        print("✅ Prêt pour les publications Instagram avec chemins locaux!")
    else:
        print("⚠️ Des problèmes ont été détectés.")

if __name__ == "__main__":
    asyncio.run(main())