#!/usr/bin/env python3
"""
Script de test pour la conversion automatique des chemins locaux vers URLs ngrok
pour la publication Instagram.
"""

import sys
import os
import requests

# Ajouter le dossier parent au path pour importer les fonctions du serveur
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import convert_local_path_to_ngrok_url, verify_url_accessibility, get_active_ngrok_url

def test_ngrok_detection():
    """Test de la détection de l'URL ngrok active"""
    print("🔍 Test détection URL ngrok active...")
    try:
        ngrok_url = get_active_ngrok_url()
        if ngrok_url:
            print(f"✅ URL ngrok détectée: {ngrok_url}")
            return True
        else:
            print("❌ Aucune URL ngrok détectée")
            return False
    except Exception as e:
        print(f"❌ Erreur détection ngrok: {e}")
        return False

def test_local_path_conversion():
    """Test de conversion des chemins locaux"""
    print("\n🔄 Test conversion chemins locaux...")
    
    test_cases = [
        "uploads/test_image.jpg",  # Chemin local à convertir
        "uploads/webhook_abc123_1234567890.png",  # Autre chemin local
        "https://example.com/image.jpg",  # URL déjà publique
        "http://localhost:8001/uploads/local.png",  # URL locale
    ]
    
    results = []
    for test_case in test_cases:
        try:
            print(f"  Test: {test_case}")
            converted = convert_local_path_to_ngrok_url(test_case)
            print(f"  ✅ Résultat: {converted}")
            results.append((test_case, converted, True))
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
            results.append((test_case, None, False))
    
    return results

def test_url_accessibility():
    """Test de vérification d'accessibilité d'URL"""
    print("\n🌐 Test accessibilité URLs...")
    
    # Test avec l'URL ngrok si disponible
    ngrok_url = get_active_ngrok_url()
    if ngrok_url:
        # Test de l'endpoint de santé
        health_url = f"{ngrok_url}/api/health"
        print(f"  Test endpoint santé: {health_url}")
        try:
            accessible = verify_url_accessibility(health_url)
            if accessible:
                print(f"  ✅ Endpoint accessible: {health_url}")
            else:
                print(f"  ⚠️ Endpoint non accessible: {health_url}")
        except Exception as e:
            print(f"  ❌ Erreur test accessibilité: {e}")
        
        # Test avec une image du dossier uploads si elle existe
        import glob
        upload_files = glob.glob("/app/backend/uploads/*.jpg")[:1]  # Prendre la première image trouvée
        if upload_files:
            image_file = os.path.basename(upload_files[0])
            image_url = f"{ngrok_url}/uploads/{image_file}"
            print(f"  Test image uploads: {image_url}")
            try:
                accessible = verify_url_accessibility(image_url)
                if accessible:
                    print(f"  ✅ Image accessible: {image_url}")
                else:
                    print(f"  ⚠️ Image non accessible: {image_url}")
            except Exception as e:
                print(f"  ❌ Erreur test image: {e}")
        else:
            print("  ℹ️ Aucune image trouvée dans uploads pour le test")
    else:
        print("  ⚠️ Pas d'URL ngrok disponible pour les tests d'accessibilité")

def test_complete_workflow():
    """Test du workflow complet de conversion"""
    print("\n🎯 Test workflow complet...")
    
    # Vérifier qu'on a une URL ngrok
    ngrok_url = get_active_ngrok_url()
    if not ngrok_url:
        print("❌ Pas d'URL ngrok - impossible de tester le workflow complet")
        return False
    
    # Test avec un chemin local typique
    test_path = "uploads/test_conversion.jpg"
    
    try:
        print(f"  📝 Chemin de test: {test_path}")
        
        # Étape 1: Conversion
        converted_url = convert_local_path_to_ngrok_url(test_path)
        print(f"  🔄 URL convertie: {converted_url}")
        
        # Étape 2: Vérification du format attendu
        expected_url = f"{ngrok_url}/{test_path}"
        if converted_url == expected_url:
            print(f"  ✅ Format URL correct")
        else:
            print(f"  ❌ Format URL incorrect. Attendu: {expected_url}")
            return False
        
        # Étape 3: Test de vérification d'accessibilité (même si le fichier n'existe pas)
        print(f"  🌐 Test accessibilité (fichier peut ne pas exister)")
        accessible = verify_url_accessibility(converted_url)
        print(f"  ℹ️ Accessible: {accessible}")
        
        print("  ✅ Workflow complet testé avec succès")
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur workflow: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 === Test de conversion Instagram ngrok ===\n")
    
    tests = [
        ("Détection ngrok", test_ngrok_detection),
        ("Conversion chemins", test_local_path_conversion),
        ("Accessibilité URLs", test_url_accessibility),
        ("Workflow complet", test_complete_workflow)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Test: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur lors du test {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé final
    print(f"\n{'='*50}")
    print("📊 RÉSUMÉ DES TESTS")
    print('='*50)
    
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{test_name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_tests = len(results)
    
    print(f"\nRésultats: {success_count}/{total_tests} tests réussis")
    
    if success_count == total_tests:
        print("🎉 Tous les tests sont passés! La conversion Instagram est prête.")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")

if __name__ == "__main__":
    main()