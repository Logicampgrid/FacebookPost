#!/usr/bin/env python3
"""
Test de la fonction de conversion URL améliorée
"""
import sys
sys.path.append('/app/backend')

from server import convert_local_path_to_ngrok_url, get_active_ngrok_url

def test_conversion():
    print("=== TEST CONVERSION URL AMÉLIORÉE ===")
    
    # Test 1: URL active ngrok
    print("\n1. Test récupération URL ngrok active:")
    ngrok_url = get_active_ngrok_url()
    print(f"   URL ngrok trouvée: {ngrok_url}")
    
    # Test 2: Différents formats de chemins
    test_cases = [
        "uploads\\webhook_7f61cf62_1758788160.png",  # Cas des logs d'erreur
        "uploads/webhook_test_correction.jpg",        # Format normal
        "backend/uploads/test.jpg",                   # Avec préfixe
        "./uploads/image.png",                        # Avec préfixe local
        "https://example.com/image.jpg",              # URL déjà complète
        "not_uploads/test.jpg"                        # Pas un chemin uploads
    ]
    
    print("\n2. Test conversion différents formats:")
    for i, test_path in enumerate(test_cases, 1):
        try:
            converted = convert_local_path_to_ngrok_url(test_path)
            print(f"   {i}. '{test_path}' -> '{converted}'")
        except Exception as e:
            print(f"   {i}. '{test_path}' -> ERREUR: {e}")
    
    print("\n=== FIN TEST ===")

if __name__ == "__main__":
    test_conversion()