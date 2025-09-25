#!/usr/bin/env python3
"""
Test de correction du problème Instagram - Upload FTP automatique
Ce script teste la correction que nous avons apportée pour résoudre le problème Instagram.
"""

import asyncio
import os
import sys
import tempfile
import requests
import json
from PIL import Image

# Ajouter le dossier backend au path pour importer les modules
sys.path.append('/app/backend')

from server import upload_image_to_ftp, log_app

async def test_ftp_upload():
    """Test de la fonction d'upload FTP corrigée"""
    
    print("🔍 TEST: Vérification de la correction Instagram FTP")
    print("=" * 60)
    
    # Créer une image de test
    test_image_path = "/tmp/test_instagram_image.png"
    
    try:
        # Créer une image de test simple
        test_image = Image.new('RGB', (300, 300), color='red')
        test_image.save(test_image_path)
        print(f"✅ Image de test créée: {test_image_path}")
        
        # Tester l'upload FTP
        print("\n🔄 Test d'upload FTP...")
        success, ftp_url, error = await upload_image_to_ftp(test_image_path, "test_instagram.png")
        
        if success and ftp_url:
            print(f"✅ Upload FTP RÉUSSI!")
            print(f"🌐 URL publique: {ftp_url}")
            
            # Vérifier que l'URL est accessible
            try:
                response = requests.head(ftp_url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ URL publique confirmée accessible (HTTP {response.status_code})")
                else:
                    print(f"⚠️ URL publique retourne HTTP {response.status_code}")
            except Exception as e:
                print(f"⚠️ Impossible de vérifier l'URL publique: {e}")
                
            return True
        else:
            print(f"❌ Upload FTP ÉCHOUÉ: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False
    finally:
        # Nettoyer
        if os.path.exists(test_image_path):
            os.unlink(test_image_path)

async def test_webhook_simulation():
    """Test de simulation d'un webhook avec image"""
    
    print("\n🔍 TEST: Simulation webhook Instagram")
    print("=" * 60)
    
    # Créer une image de test dans le dossier uploads
    uploads_dir = "/app/backend/uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    
    test_image_path = os.path.join(uploads_dir, "webhook_test_instagram.png")
    
    try:
        # Créer une image de test
        test_image = Image.new('RGB', (600, 600), color='blue')
        test_image.save(test_image_path)
        print(f"✅ Image de test créée dans uploads: {test_image_path}")
        
        # Simuler les données webhook
        webhook_data = {
            "store": "gizmobbs",
            "title": "Test correction Instagram",
            "url": "https://www.logicamp.org/wordpress/produit/test/",
            "description": "Test de la correction du problème Instagram",
            "image_file": {
                "path": test_image_path,
                "filename": "webhook_test_instagram.png",
                "original_filename": "test_image.png",
                "content_type": "image/png",
                "size": os.path.getsize(test_image_path),
                "ftp_url": None,  # Sera mis à jour par le système
                "ftp_error": None
            }
        }
        
        # Tester l'endpoint webhook
        print("\n📤 Test de l'endpoint webhook...")
        
        response = requests.post(
            "http://localhost:8001/api/webhook",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook traité avec succès")
            print(f"📋 Réponse: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Webhook échoué: HTTP {response.status_code}")
            print(f"📋 Erreur: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test webhook: {e}")
        return False
    finally:
        # Nettoyer
        if os.path.exists(test_image_path):
            os.unlink(test_image_path)

async def main():
    """Test principal"""
    
    print("🚀 DÉMARRAGE DES TESTS DE CORRECTION INSTAGRAM")
    print("=" * 80)
    
    # Test 1: Upload FTP direct
    ftp_success = await test_ftp_upload()
    
    # Test 2: Simulation webhook complet (optionnel si FTP fonctionne)
    if ftp_success:
        webhook_success = await test_webhook_simulation()
        
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 80)
        print(f"Upload FTP: {'✅ RÉUSSI' if ftp_success else '❌ ÉCHOUÉ'}")
        print(f"Webhook complet: {'✅ RÉUSSI' if webhook_success else '❌ ÉCHOUÉ'}")
        
        if ftp_success and webhook_success:
            print("\n🎉 CORRECTION INSTAGRAM: TOUTES LES CORRECTIONS FONCTIONNENT!")
            print("✅ Les images seront maintenant uploadées automatiquement vers FTP")
            print("✅ Instagram recevra des URLs publiques au lieu de chemins locaux")
        else:
            print("\n⚠️ CORRECTION PARTIELLE: Certains tests ont échoué")
    else:
        print("\n❌ CORRECTION ÉCHOUÉE: L'upload FTP ne fonctionne pas")
        print("🔍 Vérifiez la configuration FTP dans le fichier .env")
        print("🔍 Testez la connectivité réseau vers logicamp.org:21")

if __name__ == "__main__":
    asyncio.run(main())