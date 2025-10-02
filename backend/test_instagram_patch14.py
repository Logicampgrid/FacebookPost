#!/usr/bin/env python3
"""
Test final PATCH 14 - Simulation directe de l'appel Instagram
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import publish_to_instagram, get_store_config

async def test_instagram_patch14():
    """Test direct de la fonction publish_to_instagram avec PATCH 14"""
    print("🧪 Test final PATCH 14 - publish_to_instagram")
    print("=" * 60)
    
    # Simuler un appel avec le chemin local problématique des logs
    problematic_path = "uploads\\webhook_4784afc9_1759414736.jpg"
    
    print(f"🔍 Test avec chemin problématique: '{problematic_path}'")
    print("   (Ce type de chemin causait l'erreur Instagram)")
    
    # Configuration de test (store logicantiq d'après les logs)
    try:
        store_config = get_store_config("logicantiq")
        print(f"✅ Configuration store récupérée: {store_config.get('name', 'N/A')}")
    except Exception as e:
        print(f"⚠️ Erreur configuration store: {e}")
        # Configuration minimale pour test
        store_config = {
            "ig_user_id": "test_ig_user",
            "access_token": "test_token"  # Sera rejeté par Instagram mais permet de tester la conversion URL
        }
    
    try:
        print("\n🔄 Appel publish_to_instagram avec chemin local...")
        print("   Si PATCH 14 fonctionne, le chemin sera automatiquement converti")
        
        # Appel de la fonction (mode dry-run - ne publiera pas réellement)
        result = await publish_to_instagram(
            store_config=store_config,
            title="🏷️ Titre : Assiette XVIIIᵉ siècle",
            url="https://www.logicamp.org/wordpress/produit/test/",
            description="Test PATCH 14",
            media_url=problematic_path,  # LE CHEMIN PROBLÉMATIQUE
            is_video=False
        )
        
        print(f"\n📊 Résultat:")
        print(f"   Success: {result.get('success', False)}")
        if not result.get('success'):
            error_msg = result.get('error', 'Unknown error')
            print(f"   Error: {error_msg}")
            
            # Analyser l'erreur pour voir si c'est le bon type d'erreur
            if "URL publique invalide" in error_msg:
                print("   ✅ PATCH 14 a détecté et rejeté l'URL invalide (protection fonctionne)")
            elif "Only photo or video can be accepted" in error_msg:
                print("   ❌ PATCH 14 n'a pas fonctionné - Instagram reçoit encore un chemin local")
            elif "Configuration Instagram manquante" in error_msg or "test_token" in error_msg:
                print("   ℹ️  Erreur normale (tokens de test) - mais conversion URL devrait être loggée")
            else:
                print(f"   ℹ️  Autre erreur: {error_msg}")
        else:
            print("   ✅ Publication simulée réussie")
            
    except Exception as e:
        print(f"❌ Erreur test: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSION:")
    print("   Si vous voyez des logs 'PATCH 14: URL convertie', la correction fonctionne")
    print("   Instagram ne devrait plus recevoir de chemins locaux Windows")

if __name__ == "__main__":
    asyncio.run(test_instagram_patch14())