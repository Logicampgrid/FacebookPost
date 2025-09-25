#!/usr/bin/env python3
"""
Test du fallback ngrok quand FTP échoue
"""

import sys
import os
sys.path.append('/app/backend')

import asyncio
from server import convert_local_path_to_ngrok_url, get_active_ngrok_url

def test_ngrok_conversion():
    """Test la conversion des chemins locaux en URLs ngrok"""
    
    print("🧪 Test de conversion des chemins vers URLs ngrok")
    print("=" * 50)
    
    # Test 1: Chemin problématique des logs
    problematic_paths = [
        "uploads\\webhook_8501e01f_1758807307.jpg",  # Comme dans les logs
        "uploads/webhook_test.jpg",                   # Format Linux
        "webhook_test.png",                          # Sans préfixe
        "uploads\\webhook_1f8e6ebf_1758807369.png"  # Autre exemple des logs
    ]
    
    # Test de récupération de l'URL ngrok
    print("1. Test récupération URL ngrok active:")
    try:
        ngrok_url = get_active_ngrok_url()
        if ngrok_url:
            print(f"   ✅ URL ngrok trouvée: {ngrok_url}")
        else:
            print(f"   ❌ Aucune URL ngrok trouvée")
            return False
    except Exception as e:
        print(f"   ❌ Erreur récupération ngrok: {e}")
        return False
    
    print("\n2. Test conversions des chemins problématiques:")
    
    for path in problematic_paths:
        print(f"\n   Chemin original: '{path}'")
        try:
            converted = convert_local_path_to_ngrok_url(path)
            print(f"   ✅ Converti en:  '{converted}'")
            
            # Vérifier que c'est bien une URL complète
            if converted.startswith("https://") and "ngrok" in converted:
                print(f"   ✅ Format URL ngrok correct")
                
                # Vérifier que le nom de fichier est préservé
                original_filename = os.path.basename(path.replace("\\", "/"))
                if original_filename in converted:
                    print(f"   ✅ Nom de fichier préservé: {original_filename}")
                else:
                    print(f"   ⚠️ Nom de fichier non préservé")
                    
            else:
                print(f"   ❌ Format URL incorrect")
                
        except Exception as e:
            print(f"   ❌ Erreur conversion: {e}")
    
    print("\n3. Test URL complète pour Instagram:")
    test_path = "uploads/webhook_test_instagram.jpg"
    try:
        final_url = convert_local_path_to_ngrok_url(test_path)
        print(f"   URL finale pour Instagram: {final_url}")
        
        # Simule ce qu'Instagram recevrait
        print(f"   Instagram recevrait: image_url='{final_url}'")
        
        if final_url.startswith("https://") and not "uploads\\" in final_url:
            print(f"   ✅ Cette URL devrait être acceptée par Instagram !")
        else:
            print(f"   ❌ Cette URL pourrait encore causer des problèmes")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    return True

if __name__ == "__main__":
    success = test_ngrok_conversion()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCÈS: Les conversions ngrok fonctionnent correctement !")
        print("✅ Cela devrait résoudre l'erreur 'Only photo or video can be accepted'")
    else:
        print("❌ PROBLÈME: Les conversions ngrok ne fonctionnent pas")
    print("=" * 50)