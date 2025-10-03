#!/usr/bin/env python3
"""
PATCH 23 - Test final automatique
Test automatique de la correction sans interaction
"""

import sys
import os
import time
import uuid
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import get_active_ngrok_url

def test_patch23_correction():
    """Test automatique de la correction PATCH 23"""
    print("🚀 PATCH 23 - Test final correction automatique")
    print("=" * 60)
    
    # Créer fichier de test
    test_filename = f"webhook_patch23_test_{int(time.time())}.mp4"
    upload_path = os.path.join("/app/backend/uploads", test_filename)
    test_content = b"TEST_PATCH23_VIDEO_CONTENT" * 50
    
    print(f"📁 Création fichier test: {test_filename}")
    
    with open(upload_path, "wb") as f:
        f.write(test_content)
    
    print(f"✅ Fichier créé: {len(test_content)} bytes")
    
    # Générer URL publique
    ngrok_url = get_active_ngrok_url()
    public_url = f"{ngrok_url}/uploads/{test_filename}"
    
    print(f"🔗 URL publique: {public_url}")
    
    # Test d'accessibilité
    success = False
    try:
        print("📡 Test accessibilité...")
        response = requests.head(public_url, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCÈS: Fichier accessible via ngrok")
            success = True
            
            # Test de persistance avec délai
            print("⏳ Test persistance après 5 secondes...")
            time.sleep(5)
            
            response2 = requests.head(public_url, timeout=10)
            if response2.status_code == 200:
                print("✅ SUCCÈS: Fichier toujours accessible après délai")
            else:
                print("❌ ÉCHEC: Fichier supprimé après délai")
                success = False
        else:
            print("❌ ÉCHEC: Fichier non accessible")
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS PATCH 23:")
    
    if success:
        print("✅ CORRECTION RÉUSSIE!")
        print("   → Les fichiers restent accessibles")
        print("   → Facebook/Instagram peuvent accéder aux URLs")
        print("   → Erreurs 'Missing or invalid image file' résolues")
        print("   → Erreurs 'Media ID is not available' résolues")
    else:
        print("❌ CORRECTION INCOMPLÈTE")
        print("   → Problème persistant d'accessibilité")
        print("   → Vérifier si serveur utilise les corrections")
        print("   → Possibles autres suppressions non identifiées")
    
    # Nettoyage
    try:
        if os.path.exists(upload_path):
            os.remove(upload_path)
            print(f"🧹 Fichier test supprimé")
    except:
        pass
    
    return success

if __name__ == "__main__":
    success = test_patch23_correction()
    
    print(f"\n🎯 PATCH 23 FINAL: {'SUCCÈS' if success else 'ÉCHEC'}")
    exit(0 if success else 1)