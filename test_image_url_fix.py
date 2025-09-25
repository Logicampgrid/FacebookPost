#!/usr/bin/env python3
"""
Test de la correction du problème d'URL d'image Instagram
Teste la conversion des chemins Windows (avec backslashes) vers les URLs ngrok
"""

import os
import sys

# Ajouter le répertoire backend au path pour les imports
backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_path)

from server import convert_local_path_to_ngrok_url, get_active_ngrok_url

def test_path_conversion():
    """Test de conversion des chemins vers URLs"""
    
    print("🧪 Test de conversion des chemins d'images Instagram")
    print("=" * 60)
    
    # Cas de test
    test_cases = [
        "uploads\\webhook_31c55813_1758782446.png",  # Windows backslash (problématique)
        "uploads/webhook_31c55813_1758782446.png",   # Unix slash (normal)
        "https://example.com/image.png",              # URL complète (pas de conversion)
        "some/other/path.png",                        # Autre chemin (pas de conversion)
    ]
    
    # Vérifier l'URL ngrok active
    ngrok_url = get_active_ngrok_url()
    print(f"🔗 URL ngrok active: {ngrok_url}")
    print()
    
    if not ngrok_url:
        print("❌ Aucune URL ngrok active - impossible de tester la conversion")
        return False
    
    all_passed = True
    
    for i, test_path in enumerate(test_cases, 1):
        print(f"Test {i}: {test_path}")
        
        try:
            result = convert_local_path_to_ngrok_url(test_path)
            print(f"  ✅ Résultat: {result}")
            
            # Vérifications spécifiques
            if test_path.startswith("uploads"):
                expected_url = f"{ngrok_url}/uploads/"
                if expected_url in result and "webhook_31c55813_1758782446.png" in result:
                    print(f"  ✅ Conversion correcte détectée")
                else:
                    print(f"  ❌ Conversion incorrecte")
                    all_passed = False
            
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")
            all_passed = False
        
        print()
    
    return all_passed

def main():
    """Fonction principale"""
    try:
        success = test_path_conversion()
        
        if success:
            print("🎉 TOUS LES TESTS SONT PASSÉS!")
            print("✅ La correction du problème d'URL d'image Instagram fonctionne")
        else:
            print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
            print("⚠️ Vérifiez les logs ci-dessus")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur générale: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)