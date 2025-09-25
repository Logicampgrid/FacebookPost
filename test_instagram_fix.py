#!/usr/bin/env python3
"""
Test de la publication Instagram avec la correction URL
"""
import sys
sys.path.append('/app/backend')
import asyncio
import requests

from server import convert_local_path_to_ngrok_url, verify_url_accessibility, post_to_instagram

async def test_instagram_url_fix():
    print("=== TEST CORRECTION INSTAGRAM URLs ===")
    
    # Test 1: Conversion URL problématique des logs
    problematic_path = "uploads\\webhook_7f61cf62_1758788160.png"
    print(f"\n1. Test conversion chemin problématique: {problematic_path}")
    
    try:
        converted_url = convert_local_path_to_ngrok_url(problematic_path)
        print(f"   URL convertie: {converted_url}")
        
        # Test accessibilité (avec un fichier existant)
        test_url = convert_local_path_to_ngrok_url("uploads/webhook_test_correction.jpg")
        is_accessible = verify_url_accessibility(test_url)
        print(f"   Test accessibilité: {is_accessible}")
        
        # Test with a HEAD request to see if Instagram would accept it
        print(f"\n2. Test requête HEAD (simulée Instagram):")
        try:
            response = requests.head(test_url, timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"   Content-Length: {response.headers.get('content-length', 'N/A')}")
            
            if response.status_code == 200 and 'image/' in response.headers.get('content-type', ''):
                print("   ✅ L'URL serait acceptée par Instagram!")
            else:
                print("   ❌ Problème potentiel pour Instagram")
        except Exception as e:
            print(f"   ❌ Erreur requête HEAD: {e}")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n=== FIN TEST ===")

if __name__ == "__main__":
    asyncio.run(test_instagram_url_fix())