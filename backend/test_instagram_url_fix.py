#!/usr/bin/env python3
"""
Test script pour diagnostiquer et corriger le problème d'URL Instagram
"""

import os
import sys
import asyncio
import requests
import shutil
from pathlib import Path

# Ajouter le chemin backend pour les imports
sys.path.append('/app/backend')

# Import depuis server.py
from server import convert_local_path_to_public_url, get_active_ngrok_url, upload_image_to_ftp, FTP_BASE_URL

async def test_url_conversion():
    """Test la conversion d'URLs locales vers URLs publiques"""
    
    print("🔍 TEST: Diagnostic du problème Instagram URL")
    print("=" * 50)
    
    # Créer un fichier de test
    test_filename = "test_instagram_fix.jpg"
    uploads_dir = "/app/backend/uploads"
    test_file_path = f"{uploads_dir}/{test_filename}"
    
    # Créer une image de test simple (1x1 pixel JPEG)
    jpeg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
    
    with open(test_file_path, 'wb') as f:
        f.write(jpeg_data)
    
    print(f"✅ Fichier de test créé: {test_file_path}")
    
    # Test 1: Vérifier get_active_ngrok_url
    print("\n📡 Test 1: Détection ngrok")
    ngrok_url = get_active_ngrok_url()
    if ngrok_url:
        print(f"✅ Ngrok URL détectée: {ngrok_url}")
    else:
        print("❌ Aucune URL ngrok active détectée")
    
    # Test 2: Vérifier accessibilité locale
    print("\n🌐 Test 2: Accessibilité localhost")
    try:
        response = requests.get(f"http://localhost:8001/uploads/{test_filename}", timeout=5)
        if response.status_code == 200:
            print(f"✅ Fichier accessible via localhost: {response.status_code}")
        else:
            print(f"❌ Fichier non accessible via localhost: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur accès localhost: {e}")
    
    # Test 3: Test conversion URL
    print("\n🔄 Test 3: Conversion URL locale -> URL publique")
    test_local_path = f"uploads/{test_filename}"
    
    try:
        converted_url = await convert_local_path_to_public_url(test_local_path)
        print(f"📤 URL convertie: {converted_url}")
        
        # Vérifier si l'URL est accessible publiquement
        if converted_url.startswith(("http://", "https://")):
            try:
                test_response = requests.head(converted_url, timeout=10)
                if test_response.status_code == 200:
                    print(f"✅ URL publique accessible: {test_response.status_code}")
                else:
                    print(f"❌ URL publique non accessible: {test_response.status_code}")
            except Exception as e:
                print(f"❌ Erreur test URL publique: {e}")
        else:
            print("❌ URL convertie n'est pas une URL HTTP valide")
            
    except Exception as e:
        print(f"❌ Erreur conversion URL: {e}")
    
    # Test 4: Test FTP (si disponible)
    print("\n📁 Test 4: Upload FTP")
    if FTP_BASE_URL:
        try:
            success, ftp_url, error = await upload_image_to_ftp(test_file_path, test_filename)
            if success:
                print(f"✅ Upload FTP réussi: {ftp_url}")
                
                # Test accessibilité FTP
                try:
                    ftp_response = requests.head(ftp_url, timeout=10)
                    print(f"✅ Image FTP accessible: {ftp_response.status_code}")
                except:
                    print(f"⚠️ Image FTP uploadée mais test accessibilité échoué")
                    
            else:
                print(f"❌ Upload FTP échoué: {error}")
        except Exception as e:
            print(f"❌ Erreur test FTP: {e}")
    else:
        print("⚠️ FTP_BASE_URL non configurée")
    
    # Nettoyage
    try:
        os.remove(test_file_path)
        print(f"\n🗑️ Fichier de test supprimé")
    except:
        pass
    
    print("\n" + "=" * 50)
    print("🎯 RÉSUMÉ ET SOLUTIONS")
    print("=" * 50)
    
    if not ngrok_url:
        print("💡 SOLUTION 1: Démarrer ngrok")
        print("   cd /app/backend && ngrok http 8001")
        print("   Ou configurer PUBLIC_BASE_URL dans .env")
    
    print("💡 SOLUTION 2: Vérifier que le serveur backend sert /uploads/")
    print("   curl http://localhost:8001/uploads/test_image.jpg")
    
    print("💡 SOLUTION 3: Configurer PUBLIC_BASE_URL si domaine fixe disponible")
    print("   PUBLIC_BASE_URL=https://votre-domaine.com dans .env")
    
    if FTP_BASE_URL:
        print("💡 SOLUTION 4: Vérifier configuration FTP")
        print(f"   FTP configuré sur: {FTP_BASE_URL}")

if __name__ == "__main__":
    asyncio.run(test_url_conversion())