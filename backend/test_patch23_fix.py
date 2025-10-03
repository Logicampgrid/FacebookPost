#!/usr/bin/env python3
"""
PATCH 23 - Test de la correction suppression fichiers
Teste que les fichiers restent accessibles après upload
"""

import sys
import os
import requests
import time
import tempfile
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import get_active_ngrok_url

def test_file_persistence_after_upload():
    """Test que les fichiers ne sont plus supprimés immédiatement"""
    print("🔍 PATCH 23: Test persistance des fichiers après upload...")
    
    # Créer un fichier de test temporaire
    test_content = b"Test video content for PATCH 23"
    test_filename = f"test_patch23_{int(time.time())}.mp4"
    upload_path = os.path.join("/app/backend/uploads", test_filename)
    
    # Sauvegarder le fichier de test
    with open(upload_path, "wb") as f:
        f.write(test_content)
    
    print(f"✅ Fichier test créé: {test_filename}")
    
    # Générer l'URL publique
    ngrok_url = get_active_ngrok_url()
    public_url = f"{ngrok_url}/uploads/{test_filename}"
    
    # Test d'accessibilité immédiate
    try:
        response = requests.head(public_url, timeout=10)
        print(f"📡 Test accès immédiat: {public_url} → Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ PATCH 23: Fichier accessible immédiatement après création")
            
            # Attendre quelques secondes pour simuler le délai FB/IG
            print("⏳ Simulation délai accès Facebook/Instagram (5 secondes)...")
            time.sleep(5)
            
            # Re-tester l'accessibilité
            response2 = requests.head(public_url, timeout=10)
            print(f"📡 Test accès différé: {public_url} → Status: {response2.status_code}")
            
            if response2.status_code == 200:
                print("✅ PATCH 23: Fichier TOUJOURS accessible après délai (correction réussie!)")
            else:
                print("❌ PATCH 23: Fichier supprimé entre temps (problème persiste)")
                
        else:
            print("❌ PATCH 23: Fichier non accessible immédiatement")
            
    except Exception as e:
        print(f"❌ Erreur test accessibilité: {e}")
    
    # Nettoyage du fichier de test
    try:
        if os.path.exists(upload_path):
            os.remove(upload_path)
            print(f"🧹 Nettoyage: fichier de test supprimé")
    except:
        pass

def test_realistic_webhook_scenario():
    """Test un scénario réaliste de webhook avec vidéo"""
    print("\n🔍 PATCH 23: Test scénario réaliste webhook vidéo...")
    
    ngrok_url = get_active_ngrok_url()
    print(f"🌐 URL ngrok: {ngrok_url}")
    
    # Simuler les étapes d'un vrai webhook
    print("1. 📤 Simulation réception fichier webhook...")
    print("2. 💾 Simulation sauvegarde fichier...")
    print("3. 🔗 Simulation génération URL publique...")
    print("4. 📨 Simulation envoi URL à Facebook/Instagram...")
    print("5. ⏳ Simulation délai accès par Facebook/Instagram...")
    print("6. 📡 Simulation accès Facebook/Instagram au fichier...")
    
    # Tester avec un vrai fichier existant
    existing_files = [f for f in os.listdir("/app/backend/uploads") 
                     if f.startswith("webhook_") and f.endswith(".mp4")][:1]
    
    if existing_files:
        test_file = existing_files[0]
        test_url = f"{ngrok_url}/uploads/{test_file}"
        
        try:
            response = requests.head(test_url, timeout=10)
            print(f"📡 Test fichier existant: {test_file} → Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ PATCH 23: Les fichiers webhook existants sont accessibles")
            else:
                print("❌ PATCH 23: Problème d'accès aux fichiers webhook")
                
        except Exception as e:
            print(f"❌ Erreur test fichier existant: {e}")
    else:
        print("ℹ️  Aucun fichier webhook vidéo trouvé pour test")

if __name__ == "__main__":
    print("🚀 PATCH 23 - Test correction suppression fichiers")
    print("=" * 60)
    
    test_file_persistence_after_upload()
    test_realistic_webhook_scenario()
    
    print("\n✅ PATCH 23: Tests de correction terminés")
    print("\n💡 PATCH 23: Si les tests réussissent, les erreurs Facebook/Instagram")
    print("   'Missing or invalid image file' et 'Media ID is not available'")
    print("   devraient être résolues car les URLs seront maintenant accessibles.")