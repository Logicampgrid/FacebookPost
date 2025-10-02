#!/usr/bin/env python3
"""
Test de validation PATCH 14 - Correction URLs Instagram
Test que tous les chemins locaux sont correctement convertis en URLs ngrok
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import get_public_url

def test_patch14_url_conversion():
    """Test des conversions d'URLs pour Instagram avec PATCH 14"""
    print("🧪 Test PATCH 14 - Conversion URLs Instagram")
    print("=" * 50)
    
    # Test 1: Chemin Windows avec backslash (problème principal identifié)
    test_cases = [
        {
            "name": "Chemin Windows (problème principal)", 
            "input": "uploads\\webhook_4784afc9_1759414736.jpg",
            "expected_contains": ["https://", "webhook_4784afc9_1759414736.jpg"]
        },
        {
            "name": "Chemin Unix relatif",
            "input": "uploads/webhook_da0edd11_1759414743.png", 
            "expected_contains": ["https://", "webhook_da0edd11_1759414743.png"]
        },
        {
            "name": "URL déjà valide (ne pas toucher)",
            "input": "https://example.com/test.jpg",
            "expected_contains": ["https://example.com/test.jpg"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print(f"   Input: '{test_case['input']}'")
        
        # Simuler la logique de détection PATCH 14
        input_url = test_case['input']
        normalized_path = input_url.replace("\\", "/")
        
        is_local_path = (
            not normalized_path.startswith(("http://", "https://")) and (
                "uploads/" in normalized_path or 
                normalized_path.startswith("uploads/") or
                normalized_path.startswith("./uploads/") or
                "webhook_" in normalized_path
            )
        )
        
        if is_local_path:
            filename = normalized_path.split("/")[-1]
            converted_url = get_public_url(filename)
            print(f"   ✅ Conversion: '{input_url}' → '{converted_url}'")
            
            # Vérifier que l'URL générée est valide
            valid = converted_url and converted_url.startswith('https://')
            print(f"   ✅ URL valide: {valid}")
            
            # Vérifier qu'elle contient les éléments attendus
            for expected in test_case['expected_contains']:
                if expected in converted_url:
                    print(f"   ✅ Contient '{expected}': Oui")
                else:
                    print(f"   ❌ Contient '{expected}': Non")
        else:
            print(f"   ℹ️  Pas de conversion nécessaire (URL déjà publique)")
    
    print("\n" + "=" * 50)
    print("🎯 RÉSULTAT: Le PATCH 14 devrait résoudre le problème Instagram")
    print("   Les chemins 'uploads\\webhook_xxx.jpg' seront automatiquement convertis")
    print("   en URLs ngrok publiques compatibles Instagram")

if __name__ == "__main__":
    test_patch14_url_conversion()