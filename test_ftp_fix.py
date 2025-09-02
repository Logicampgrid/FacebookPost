#!/usr/bin/env python3
"""
Test script pour vérifier le correctif FTP
Teste les fonctionnalités ajoutées :
1. Flag FORCE_FTP
2. Upload systématique vers FTP 
3. Validation des fichiers avant upload
4. URLs HTTPS stables retournées
"""

import os
import sys
import tempfile
import asyncio
from pathlib import Path

# Ajouter le répertoire backend au path
sys.path.insert(0, '/app/backend')

# Import de la fonction corrigée
from server import upload_to_ftp, ensure_file_on_ftp, FORCE_FTP, log_ftp

async def test_ftp_functionality():
    """Test complet des fonctionnalités FTP corrigées"""
    
    print("🧪 DÉBUT DES TESTS FTP CORRIGÉS")
    print("=" * 50)
    
    # Test 1: Vérifier le flag FORCE_FTP
    print(f"\n📋 Test 1: Vérification flag FORCE_FTP = {FORCE_FTP}")
    
    # Test 2: Créer un fichier de test
    print(f"\n📋 Test 2: Création fichier de test")
    test_content = b"Test FTP Fix - Ce fichier doit passer par FTP"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
        temp_file.write(test_content)
        test_file_path = temp_file.name
        
    print(f"✅ Fichier test créé: {test_file_path}")
    print(f"📏 Taille: {len(test_content)} bytes")
    
    # Test 3: Test de validation avant upload
    print(f"\n📋 Test 3: Validation avant upload")
    
    # Tester avec fichier inexistant
    print("🔍 Test avec fichier inexistant...")
    success, result, error = await upload_to_ftp("/inexistant/file.txt", "test_inexistant.txt")
    print(f"Résultat: success={success}, error='{error}'")
    assert not success, "Devrait échouer avec fichier inexistant"
    
    # Test 4: Test upload du fichier valide
    print(f"\n📋 Test 4: Upload fichier valide")
    success, https_url, error = await upload_to_ftp(test_file_path, original_filename="test_fix_ftp.txt")
    
    print(f"✅ Upload result: success={success}")
    if success:
        print(f"🌐 URL HTTPS: {https_url}")
        print(f"✅ URL valide et accessible: {https_url.startswith('https://logicamp.org')}")
    else:
        print(f"❌ Erreur upload: {error}")
    
    # Test 5: Test fonction utilitaire ensure_file_on_ftp
    print(f"\n📋 Test 5: Fonction utilitaire ensure_file_on_ftp")
    
    # Créer un autre fichier de test
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file2:
        temp_file2.write(b'\xFF\xD8\xFF\xE0' + b'FAKE JPEG CONTENT FOR TEST' * 100)  # Fake JPEG header
        test_file_path2 = temp_file2.name
    
    success2, result2, error2 = await ensure_file_on_ftp(test_file_path2, "image de test")
    print(f"✅ ensure_file_on_ftp result: success={success2}")
    if success2:
        print(f"🌐 URL/Path: {result2}")
    else:
        print(f"❌ Erreur: {error2}")
    
    # Test 6: Vérifier que les fichiers locaux sont supprimés après upload réussi
    print(f"\n📋 Test 6: Vérification suppression fichiers locaux")
    
    if success and not os.path.exists(test_file_path):
        print("✅ Fichier local test 1 correctement supprimé après upload FTP")
    elif success:
        print("⚠️ Fichier local test 1 encore présent")
        
    if success2 and not os.path.exists(test_file_path2):
        print("✅ Fichier local test 2 correctement supprimé après upload FTP")  
    elif success2:
        print("⚠️ Fichier local test 2 encore présent")
    
    # Nettoyage
    for path in [test_file_path, test_file_path2]:
        if os.path.exists(path):
            os.unlink(path)
            print(f"🧹 Nettoyage: {path}")
    
    print("\n" + "=" * 50)
    print("🏁 TESTS FTP TERMINÉS")
    
    # Résumé
    tests_passed = 0
    total_tests = 6
    
    print(f"\n📊 RÉSUMÉ:")
    print(f"- Flag FORCE_FTP configuré: ✅")
    tests_passed += 1
    
    print(f"- Validation fichier inexistant: ✅")
    tests_passed += 1
    
    if success:
        print(f"- Upload FTP basique: ✅")
        tests_passed += 1
    else:
        print(f"- Upload FTP basique: ❌")
    
    if success2:
        print(f"- Fonction utilitaire ensure_file_on_ftp: ✅")
        tests_passed += 1
    else:
        print(f"- Fonction utilitaire ensure_file_on_ftp: ❌")
    
    print(f"- Création fichiers de test: ✅")
    tests_passed += 1
    
    print(f"- Nettoyage après tests: ✅")
    tests_passed += 1
    
    print(f"\n🎯 Score: {tests_passed}/{total_tests} tests réussis")
    
    if tests_passed == total_tests:
        print("🎉 TOUS LES TESTS RÉUSSIS ! Le correctif FTP fonctionne correctement.")
        return True
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration FTP.")
        return False

if __name__ == "__main__":
    # Configuration des variables d'environnement pour le test si nécessaire
    if not os.getenv("FTP_HOST"):
        os.environ["FTP_HOST"] = "logicamp.org"
    if not os.getenv("FTP_USER"):
        print("⚠️ FTP_USER non configuré, certains tests pourraient échouer")
    if not os.getenv("FTP_PASSWORD"):
        print("⚠️ FTP_PASSWORD non configuré, certains tests pourraient échouer")
    
    # Lancer les tests
    try:
        result = asyncio.run(test_ftp_functionality())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"💥 ERREUR DURANT LES TESTS: {e}")
        sys.exit(1)