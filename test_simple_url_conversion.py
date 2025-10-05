#!/usr/bin/env python3
"""
Test simple pour vérifier que la conversion d'URL fonctionne
"""

import sys
sys.path.append('/app/backend')

import asyncio
import os

# Import depuis server.py
from server import convert_local_path_to_public_url

async def test_conversion():
    """Test direct de la fonction de conversion"""
    
    print("🔍 TEST CONVERSION URL DIRECTE")
    print("=" * 40)
    
    # Test avec différents formats de chemins locaux
    test_paths = [
        "uploads\\webhook_5ba47368_1758830885.png",  # Format Windows original du problème
        "uploads/webhook_5ba47368_1758830885.png",   # Format Unix
        "uploads/test_image.jpg",                     # Fichier existant
    ]
    
    for i, test_path in enumerate(test_paths, 1):
        print(f"\n{i}. Test chemin: '{test_path}'")
        
        try:
            converted_url = await convert_local_path_to_public_url(test_path)
            print(f"   📤 Résultat: {converted_url}")
            
            # Vérifier si c'est une URL publique valide
            if converted_url.startswith('https://code-assistant-33.preview.emergentagent.com'):
                print(f"   ✅ URL publique CORRECTE")
            elif converted_url.startswith('http://localhost:8001'):
                print(f"   ❌ URL locale (problème Instagram)")
            elif converted_url.startswith('https://logicamp.org'):
                print(f"   ⚠️ URL FTP (acceptable mais pas optimal)")
            else:
                print(f"   ⚠️ Format URL inattendu")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    print("\n" + "=" * 40)
    print("🎯 CONCLUSION")
    
    # Test du fichier exact du problème original
    problem_path = "uploads\\webhook_5ba47368_1758830885.png"
    try:
        result_url = await convert_local_path_to_public_url(problem_path)
        
        if result_url.startswith('https://code-assistant-33.preview.emergentagent.com'):
            print("✅ PROBLÈME RÉSOLU: Instagram recevra maintenant une URL publique valide")
            print(f"   Avant: {problem_path}")
            print(f"   Après: {result_url}")
        else:
            print("❌ PROBLÈME PERSISTE: Conversion génère encore une URL locale")
            print(f"   Résultat: {result_url}")
            
    except Exception as e:
        print(f"❌ Erreur test conversion: {e}")
    
    print("=" * 40)

if __name__ == "__main__":
    asyncio.run(test_conversion())