#!/usr/bin/env python3
"""
Test de la logique de conversion des chemins pour Instagram
Sans upload FTP réel - juste test de la logique
"""

import sys
sys.path.append('/app/backend')

from server import convert_local_path_to_ngrok_url, get_active_ngrok_url

def test_conversions():
    print("🔍 TEST: Logique de conversion des chemins Instagram")
    print("=" * 60)
    
    # Test des différents formats de chemins qui causaient problème
    test_paths = [
        "uploads\\webhook_b58ff13f_1758810711.png",  # Chemin Windows avec backslash
        "uploads/webhook_965e2b7e_1758810721.jpg",   # Chemin Unix normal
        "./uploads/webhook_8eb8126a_1758810745.png", # Chemin relatif
        "backend/uploads/webhook_test.jpg",          # Chemin avec sous-dossier
        "https://logicamp.org/uploads/test.jpg",     # URL déjà publique
        "webhook_test_correction.jpg"                # Nom de fichier seul
    ]
    
    print("🔍 Test de détection des chemins locaux:")
    for path in test_paths:
        print(f"\n📋 Chemin: {path}")
        
        # Vérifier si c'est détecté comme chemin local
        normalized_path = path.replace("\\", "/")
        is_local = ("uploads/" in normalized_path) or normalized_path.startswith("uploads")
        
        print(f"   🔍 Normalisé: {normalized_path}")
        print(f"   📍 Local détecté: {is_local}")
        
        if is_local and not path.startswith("http"):
            try:
                converted = convert_local_path_to_ngrok_url(path)
                print(f"   ✅ Conversion ngrok: {converted}")
            except Exception as e:
                print(f"   ❌ Erreur conversion: {e}")
        elif path.startswith("http"):
            print(f"   ✅ Déjà URL publique: {path}")
        else:
            print(f"   ⚠️ Type non reconnu")
    
    # Test URL ngrok active
    print(f"\n🔍 URL ngrok active:")
    try:
        ngrok_url = get_active_ngrok_url()
        if ngrok_url:
            print(f"   ✅ URL ngrok: {ngrok_url}")
        else:
            print(f"   ⚠️ Aucune URL ngrok active")
    except Exception as e:
        print(f"   ❌ Erreur ngrok: {e}")

if __name__ == "__main__":
    test_conversions()