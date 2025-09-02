#!/usr/bin/env python3
"""
Test simple pour vérifier que les corrections FTP fonctionnent
en utilisant un des fichiers webhook existants
"""

import os
import sys
import asyncio

# Ajouter le répertoire backend au path
sys.path.insert(0, '/app/backend')

async def test_existing_webhook_file():
    """Test avec un fichier webhook existant"""
    
    print("🔍 RECHERCHE D'UN FICHIER WEBHOOK EXISTANT...")
    
    # Chercher des fichiers webhook existants
    upload_dirs = [
        "/app/backend/uploads",
        "/app/backend/C:\\gizmobbs\\uploads"
    ]
    
    webhook_file = None
    for upload_dir in upload_dirs:
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                if filename.startswith("webhook_") and filename.endswith((".jpg", ".png")):
                    webhook_file = os.path.join(upload_dir, filename)
                    break
            if webhook_file:
                break
    
    if not webhook_file:
        print("❌ Aucun fichier webhook trouvé pour le test")
        return False
    
    print(f"✅ Fichier webhook trouvé: {webhook_file}")
    file_size = os.path.getsize(webhook_file)
    print(f"📏 Taille: {file_size} bytes")
    
    # Importer les fonctions après avoir défini FORCE_FTP
    os.environ["FORCE_FTP"] = "true"
    from server import ensure_file_on_ftp
    
    print(f"\n📤 TEST UPLOAD FTP avec FORCE_FTP=true...")
    
    # Tester notre fonction utilitaire
    success, result, error = await ensure_file_on_ftp(webhook_file, "fichier webhook test")
    
    print(f"\n📊 RÉSULTAT:")
    print(f"- Succès: {success}")
    if success:
        print(f"- URL/Path résultat: {result}")
        if result and result.startswith("https://"):
            print(f"✅ URL HTTPS obtenue - CORRECTION RÉUSSIE!")
            return True
        else:
            print(f"⚠️ Chemin local retourné au lieu d'URL HTTPS")
            return False
    else:
        print(f"❌ Erreur: {error}")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(test_existing_webhook_file())
        print(f"\n🏁 TEST {'RÉUSSI' if result else 'ÉCHOUÉ'}")
    except Exception as e:
        print(f"💥 ERREUR DURANT LE TEST: {e}")
        import traceback
        traceback.print_exc()