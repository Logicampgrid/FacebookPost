#!/usr/bin/env python3
"""
PATCH 23 - Simulation complète webhook
Simule un webhook complet pour tester les corrections
"""

import sys
import os
import time
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def simulate_webhook_file_handling():
    """Simule le processus complet de gestion de fichiers webhook"""
    print("🔍 PATCH 23: Simulation complète webhook...")
    
    # Étape 1: Création fichier comme dans un webhook réel
    print("1. 📤 Simulation réception fichier multipart...")
    
    test_filename = f"webhook_{uuid.uuid4().hex[:8]}_{int(time.time())}.mp4"
    upload_path = os.path.join("/app/backend/uploads", test_filename)
    
    # Contenu de test simulant une vraie vidéo
    test_content = b"MOCK_VIDEO_CONTENT_FOR_PATCH23_TEST" * 100
    
    with open(upload_path, "wb") as f:
        f.write(test_content)
    
    print(f"✅ Fichier webhook créé: {test_filename} ({len(test_content)} bytes)")
    
    # Étape 2: Génération URL publique (comme dans le code)
    from server import get_active_ngrok_url
    
    ngrok_url = get_active_ngrok_url()
    public_url = f"{ngrok_url}/uploads/{test_filename}"
    
    print(f"🔗 URL publique générée: {public_url}")
    
    # Étape 3: Simulation envoi à Facebook/Instagram
    print("📨 Simulation envoi URL à Facebook/Instagram...")
    
    # Étape 4: Test accessibilité immédiate (comme FB/IG feraient)
    import requests
    
    try:
        response = requests.head(public_url, timeout=10)
        print(f"📡 Test accès FB/IG (immédiat): Status {response.status_code}")
        
        if response.status_code == 200:
            print("✅ PATCH 23: Fichier accessible pour Facebook/Instagram!")
            
            # Étape 5: Simulation délai puis re-test
            print("⏳ Simulation délai traitement FB/IG (10 secondes)...")
            time.sleep(10)
            
            response2 = requests.head(public_url, timeout=10)
            print(f"📡 Test accès FB/IG (après délai): Status {response2.status_code}")
            
            if response2.status_code == 200:
                print("✅ PATCH 23: Fichier TOUJOURS accessible après délai!")
                print("🎉 CORRECTION RÉUSSIE - Facebook/Instagram peuvent accéder aux fichiers")
            else:
                print("❌ PATCH 23: Fichier supprimé pendant le traitement")
                print("🔄 Correction incomplète - vérifier s'il y a d'autres suppressions")
        else:
            print("❌ PATCH 23: Fichier non accessible immédiatement")
            print("🔍 Problème différent - vérifier montage StaticFiles")
            
    except Exception as e:
        print(f"❌ Erreur test accessibilité: {e}")
    
    # Nettoyage optionnel
    cleanup = input("\n🧹 Supprimer le fichier de test? (o/N): ").lower().startswith('o')
    if cleanup:
        try:
            if os.path.exists(upload_path):
                os.remove(upload_path)
                print("✅ Fichier de test supprimé")
        except Exception as e:
            print(f"⚠️ Erreur suppression: {e}")
    else:
        print(f"📁 Fichier conservé: {test_filename}")

def check_current_files():
    """Vérifie les fichiers actuels pour diagnostics"""
    print("\n🔍 PATCH 23: Diagnostic fichiers actuels...")
    
    uploads_dir = "/app/backend/uploads"
    
    if os.path.exists(uploads_dir):
        files = os.listdir(uploads_dir)
        webhook_files = [f for f in files if f.startswith("webhook_")]
        
        print(f"📁 Total fichiers: {len(files)}")
        print(f"🔗 Fichiers webhook: {len(webhook_files)}")
        
        # Montrer les 5 fichiers webhook les plus récents
        webhook_files.sort(key=lambda x: os.path.getctime(os.path.join(uploads_dir, x)), reverse=True)
        recent_files = webhook_files[:5]
        
        print("\n📋 5 fichiers webhook les plus récents:")
        for i, file in enumerate(recent_files, 1):
            file_path = os.path.join(uploads_dir, file)
            size = os.path.getsize(file_path)
            mtime = time.ctime(os.path.getctime(file_path))
            print(f"   {i}. {file} ({size} bytes, {mtime})")
    else:
        print("❌ Dossier uploads non trouvé")

if __name__ == "__main__":
    print("🚀 PATCH 23 - Simulation webhook complète")
    print("=" * 60)
    
    check_current_files()
    
    print("\n" + "="*60)
    simulate_webhook_file_handling()
    
    print("\n✅ PATCH 23: Simulation terminée")
    print("\n💡 Si la correction fonctionne:")
    print("   - Les fichiers restent accessibles via ngrok")
    print("   - Les erreurs Facebook/Instagram seront résolues")
    print("   - 'Missing or invalid image file' → Résolu")
    print("   - 'Media ID is not available' → Résolu")