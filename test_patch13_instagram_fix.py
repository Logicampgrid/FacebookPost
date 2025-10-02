#!/usr/bin/env python3
"""
Test PATCH 13 - Correction Instagram URLs
Vérifie que les chemins locaux sont bien convertis en URLs publiques
"""
import asyncio
import os
import sys

# Ajouter le dossier backend au path
sys.path.insert(0, '/app/backend')

from server import publish_to_instagram, get_store_config, get_public_url

async def test_instagram_url_conversion():
    """Test que les chemins locaux sont convertis en URLs publiques pour Instagram"""
    
    print("🧪 Test PATCH 13 - Correction URLs Instagram")
    print("=" * 50)
    
    # 1. Test de la fonction get_public_url
    print("\n1. Test de get_public_url:")
    local_filename = "test_patch13.jpg"
    public_url = get_public_url(local_filename)
    print(f"   Fichier local: {local_filename}")
    print(f"   URL publique: {public_url}")
    
    if public_url.startswith('https://'):
        print("   ✅ get_public_url génère bien des URLs HTTPS")
    else:
        print("   ❌ get_public_url ne génère pas d'URL HTTPS")
        return False
    
    # 2. Test de conversion dans publish_to_instagram
    print("\n2. Test de conversion dans publish_to_instagram:")
    
    # Configuration de store de test (gizmobbs)
    store_config = {
        'name': 'Test Store',
        'ig_user_id': '17841459952999804',  # ID Instagram de test  
        'access_token': 'test_token_12345'  # Token de test (ne fonctionnera pas mais testera la logique)
    }
    
    # Test avec chemin local Windows (format problématique)
    local_path_windows = "uploads\\test_patch13.jpg"
    print(f"   Test avec chemin local Windows: {local_path_windows}")
    
    try:
        # Note: Cette fonction va échouer sur l'API call mais on veut voir les logs
        result = await publish_to_instagram(
            store_config=store_config,
            title="Test PATCH 13",
            url="https://example.com/test",
            description="Test conversion URLs",
            media_url=local_path_windows,  # Chemin local problématique
            is_video=False
        )
        print(f"   Résultat: {result}")
        
    except Exception as e:
        print(f"   Exception (attendue pour test): {e}")
    
    # 3. Test avec URL déjà publique
    print(f"\n3. Test avec URL déjà publique:")
    public_test_url = "https://example.com/test.jpg"
    print(f"   Test avec URL publique: {public_test_url}")
    
    try:
        result = await publish_to_instagram(
            store_config=store_config,
            title="Test PATCH 13",
            url="https://example.com/test",
            description="Test URL publique",
            media_url=public_test_url,  # URL déjà publique
            is_video=False
        )
        print(f"   Résultat: {result}")
        
    except Exception as e:
        print(f"   Exception (attendue pour test): {e}")
    
    print("\n✅ Test PATCH 13 terminé - Vérifiez les logs ci-dessus")
    print("   Les logs doivent montrer les conversions d'URLs locales en URLs HTTPS")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_instagram_url_conversion())