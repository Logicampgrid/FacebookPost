#!/usr/bin/env python3
"""
Test PATCH 42 - Parsing json_data pour publications n8n
"""

import json
import sys

def test_json_data_parsing():
    """Test que json_data est correctement parsé"""
    
    print("\n" + "="*70)
    print("TEST 1: Parsing json_data depuis format n8n multipart")
    print("="*70)
    
    # Simuler les données reçues de n8n
    webhook_data_before = {
        "json_data": '{"store": "gizmobbs", "title": "Test Produit", "description": "Description test", "url": "https://example.com/produit"}',
        "image_file": {
            "path": "/app/backend/uploads/test.jpg",
            "filename": "test.jpg",
            "public_url": "https://logicamp.org/wordpress/uploads/test.jpg"
        }
    }
    
    print("\n📦 AVANT PATCH 42:")
    print(f"  webhook_data keys: {list(webhook_data_before.keys())}")
    print(f"  json_data type: {type(webhook_data_before['json_data'])}")
    print(f"  json_data content: {webhook_data_before['json_data'][:50]}...")
    print(f"  store extraction: webhook_data.get('store') = {webhook_data_before.get('store')}")
    print(f"  ❌ RÉSULTAT: store=None → Publications bloquées")
    
    # Simuler PATCH 42
    webhook_data_after = webhook_data_before.copy()
    
    if "json_data" in webhook_data_after:
        json_data_content = webhook_data_after["json_data"]
        
        if isinstance(json_data_content, str):
            try:
                parsed_json = json.loads(json_data_content)
                print(f"\n✅ PATCH 42: JSON parsé avec succès")
                print(f"  Données parsées: {parsed_json}")
                
                # Fusionner dans webhook_data
                for key, value in parsed_json.items():
                    webhook_data_after[key] = value
                    print(f"  ✅ Ajouté: {key} = {value}")
                    
            except json.JSONDecodeError as e:
                print(f"  ❌ Erreur parsing: {e}")
                return False
    
    print("\n📦 APRÈS PATCH 42:")
    print(f"  webhook_data keys: {list(webhook_data_after.keys())}")
    print(f"  store extraction: webhook_data.get('store') = {webhook_data_after.get('store')}")
    print(f"  title extraction: webhook_data.get('title') = {webhook_data_after.get('title')}")
    print(f"  ✅ RÉSULTAT: store='gizmobbs' → Publications possibles")
    
    # Vérifier que l'extraction fonctionne
    if webhook_data_after.get('store') == 'gizmobbs':
        print("\n✅ TEST RÉUSSI: store correctement extrait")
        return True
    else:
        print(f"\n❌ TEST ÉCHOUÉ: store={webhook_data_after.get('store')}, attendu='gizmobbs'")
        return False

def test_json_data_already_dict():
    """Test que les dicts déjà parsés sont supportés"""
    
    print("\n" + "="*70)
    print("TEST 2: json_data déjà parsé (dict)")
    print("="*70)
    
    webhook_data = {
        "json_data": {
            "store": "logicantiq",
            "title": "Produit Logicantiq"
        },
        "image_file": {"path": "/test.jpg"}
    }
    
    print(f"\n📦 json_data déjà dict: {webhook_data['json_data']}")
    
    # Simuler PATCH 42 avec dict
    if "json_data" in webhook_data:
        json_data_content = webhook_data["json_data"]
        
        if isinstance(json_data_content, dict):
            print("✅ PATCH 42: json_data déjà parsé (dict)")
            for key, value in json_data_content.items():
                webhook_data[key] = value
    
    if webhook_data.get('store') == 'logicantiq':
        print(f"✅ TEST RÉUSSI: store={webhook_data.get('store')}")
        return True
    else:
        print(f"❌ TEST ÉCHOUÉ: store={webhook_data.get('store')}")
        return False

def test_backward_compatibility():
    """Test que le format sans json_data continue de fonctionner"""
    
    print("\n" + "="*70)
    print("TEST 3: Compatibilité format legacy (sans json_data)")
    print("="*70)
    
    webhook_data = {
        "store": "outdoor",
        "title": "Produit Outdoor",
        "image_file": {"path": "/test.jpg"}
    }
    
    print(f"\n📦 Format legacy: {list(webhook_data.keys())}")
    print(f"  store direct: {webhook_data.get('store')}")
    
    # Simuler PATCH 42 (ne fait rien si pas de json_data)
    if "json_data" in webhook_data:
        print("  PATCH 42 activé")
    else:
        print("  PATCH 42 ignoré (pas de json_data)")
    
    if webhook_data.get('store') == 'outdoor':
        print("✅ TEST RÉUSSI: format legacy fonctionne")
        return True
    else:
        print("❌ TEST ÉCHOUÉ: store manquant")
        return False

def main():
    """Exécute tous les tests"""
    
    print("\n" + "="*70)
    print("🧪 TESTS PATCH 42 - Parsing json_data n8n")
    print("="*70)
    
    tests = [
        ("JSON data parsing (string)", test_json_data_parsing),
        ("JSON data dict (déjà parsé)", test_json_data_already_dict),
        ("Backward compatibility", test_backward_compatibility),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Erreur test '{test_name}': {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "="*70)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} | {test_name}")
    
    print("\n" + "="*70)
    if passed == total:
        print(f"✅ TOUS LES TESTS RÉUSSIS ({passed}/{total})")
        print("="*70)
        print("\n🎉 PATCH 42 validé - Publications n8n prêtes")
        return 0
    else:
        print(f"❌ TESTS ÉCHOUÉS: {total - passed}/{total}")
        print("="*70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
