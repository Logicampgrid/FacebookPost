#!/usr/bin/env python3
"""
Test direct de la fonction Instagram avec URL ngrok
Test pour vérifier que notre correction fonctionne
"""

import sys
sys.path.append('/app/backend')
import asyncio
from server import post_to_instagram, convert_local_path_to_ngrok_url

async def test_instagram_direct():
    print("🔍 TEST: Publication Instagram directe avec URL ngrok")
    print("=" * 60)
    
    # Tester d'abord la conversion
    local_path = "uploads/webhook_test_correction.jpg"
    print(f"📋 Chemin local: {local_path}")
    
    try:
        # Test conversion
        ngrok_url = convert_local_path_to_ngrok_url(local_path)
        print(f"✅ URL ngrok générée: {ngrok_url}")
        
        # Test publication Instagram avec mode test
        print(f"\n📱 Test publication Instagram en mode simulation...")
        
        # NOTE: Nous utilisons PUBLICATION_TEST_MODE=true pour éviter l'appel API réel
        os.environ['PUBLICATION_TEST_MODE'] = 'true'
        
        result = await post_to_instagram(
            store="gizmobbs",
            message="Test de correction Instagram 📱\n\nNouveau produit disponible !",
            product_url="https://www.logicamp.org/test-correction/",
            image_url=local_path  # Notre correction devrait convertir ça automatiquement
        )
        
        print(f"✅ Publication Instagram simulée réussie:")
        print(f"   📋 ID: {result.get('id')}")
        print(f"   🖼️ Image URL: {result.get('image_url')}")
        print(f"   📝 Caption: {result.get('caption', '')[:100]}...")
        print(f"   🧪 Mode test: {result.get('test_mode')}")
        
        # Vérifier que l'URL finale est bien publique
        final_image_url = result.get('image_url', '')
        if final_image_url.startswith('https://'):
            print(f"✅ URL finale est bien publique: {final_image_url}")
            return True
        else:
            print(f"❌ URL finale n'est pas publique: {final_image_url}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    import os
    asyncio.run(test_instagram_direct())