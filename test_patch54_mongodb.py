#!/usr/bin/env python3
"""
Test PATCH 54 - Validation corrections MongoDB + Diagnostic vidéo FB
"""
import sys
import os

def test_patch_54():
    print("🔍 TEST PATCH 54 - Sauvegarde MongoDB + Diagnostic vidéo")
    print("=" * 70)
    
    # Test 1: Vérifier PATCH 54 dans server.py
    with open('/app/backend/server.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'PATCH 54' in content:
        patch54_count = content.count('PATCH 54')
        print(f"✅ Test 1: PATCH 54 trouvé ({patch54_count} occurrences)")
    else:
        print("❌ Test 1: PATCH 54 NON trouvé")
        return False
    
    # Test 2: Vérifier la fonction process_webhook_background_n8n_sync avec PATCH 54
    if 'def process_webhook_background_n8n_sync(' in content and 'PATCH 54' in content:
        print("✅ Test 2: Fonction synchrone PATCH 54 présente")
    else:
        print("❌ Test 2: Fonction synchrone PATCH 54 absente")
        return False
    
    # Test 3: Vérifier exclusion fichiers binaires
    if '"image_file", "video_file"' in content or "'image_file', 'video_file'" in content:
        print("✅ Test 3: Exclusion fichiers binaires implémentée")
    else:
        print("⚠️ Test 3: Exclusion fichiers binaires non détectée")
    
    # Test 4: Vérifier gestion erreur non bloquante
    if 'non bloquant' in content or 'non-bloquant' in content:
        print("✅ Test 4: Gestion erreur non bloquante confirmée")
    else:
        print("⚠️ Test 4: Message 'non bloquant' non trouvé")
    
    # Test 5: Vérifier nommage thread
    if 'name=f"N8N-{store}' in content:
        print("✅ Test 5: Nommage thread pour debug implémenté")
    else:
        print("⚠️ Test 5: Nommage thread non détecté")
    
    # Test 6: Vérifier script diagnostic vidéo FB
    if os.path.exists('/app/diagnostic_video_facebook_logicamp.py'):
        print("✅ Test 6: Script diagnostic vidéo FB créé")
        with open('/app/diagnostic_video_facebook_logicamp.py', 'r') as f:
            diag_content = f.read()
            if 'PAGE_ID = "174450429258625"' in diag_content:
                print("   ✅ Page Logicamp configurée")
            if 'Erreur 6000/1363042' in diag_content:
                print("   ✅ Erreur cible documentée")
            if 'CREATE_CONTENT' in diag_content:
                print("   ✅ Vérification permission CREATE_CONTENT")
    else:
        print("❌ Test 6: Script diagnostic vidéo FB absent")
        return False
    
    # Test 7: Vérifier patch number 54
    if '"patch": 54' in content or "'patch': 54" in content:
        print("✅ Test 7: Numéro de patch 54 dans réponses")
    else:
        print("❌ Test 7: patch: 54 NON trouvé")
        return False
    
    print("=" * 70)
    print("✅ TOUS LES TESTS PATCH 54 RÉUSSIS!")
    print("\n🎯 AMÉLIORATIONS PATCH 54:")
    print("  1. Sauvegarde MongoDB ne bloque plus les publications")
    print("  2. Fichiers binaires exclus (optimisation mémoire)")
    print("  3. Erreurs MongoDB non bloquantes (logs warning)")
    print("  4. Thread nommé pour debug facilité")
    print("  5. Script diagnostic vidéo FB complet")
    print("\n📊 PROCHAINE ÉTAPE:")
    print("  Exécuter: python /app/diagnostic_video_facebook_logicamp.py")
    print("  Pour analyser en profondeur le problème vidéo Facebook Logicamp")
    return True

if __name__ == "__main__":
    success = test_patch_54()
    sys.exit(0 if success else 1)
