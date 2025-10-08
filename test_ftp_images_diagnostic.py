#!/usr/bin/env python3
"""
Test diagnostic upload FTP images vs vidéos
Objectif: Identifier pourquoi les PNG/JPG échouent alors que MP4 fonctionnent
"""

import os
import sys
import ftplib
from pathlib import Path

# Configuration FTP
FTP_HOST = "logicamp.org"
FTP_PORT = 21
FTP_USER = "logi"
FTP_PASSWORD = "logi"
FTP_DIRECTORY = "/www/wordpress/uploads/"

def test_ftp_upload(file_path, file_type):
    """Test d'upload FTP pour un fichier"""
    print(f"\n{'='*60}")
    print(f"🔍 Test upload FTP - {file_type}")
    print(f"{'='*60}")
    
    filename = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    
    print(f"📄 Fichier: {filename}")
    print(f"📏 Taille: {file_size} bytes")
    print(f"🎯 Destination: {FTP_DIRECTORY}")
    
    try:
        # Connexion FTP
        print(f"\n📡 Connexion à {FTP_HOST}:{FTP_PORT}...")
        ftp = ftplib.FTP()
        ftp.set_pasv(True)
        ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
        print("✅ Connexion établie")
        
        # Login
        print(f"🔐 Login avec {FTP_USER}...")
        ftp.login(FTP_USER, FTP_PASSWORD)
        print("✅ Authentification réussie")
        
        # Changement de répertoire
        print(f"📁 Changement vers {FTP_DIRECTORY}...")
        ftp.cwd(FTP_DIRECTORY)
        print("✅ Répertoire OK")
        
        # Upload
        print(f"⬆️ Upload de {filename}...")
        with open(file_path, 'rb') as f:
            ftp.storbinary(f'STOR {filename}', f)
        print("✅ Upload réussi")
        
        # Vérification
        print(f"🔍 Vérification présence fichier...")
        files = ftp.nlst()
        if filename in files:
            print(f"✅ Fichier présent sur serveur FTP")
            
            # Taille sur serveur
            ftp.voidcmd('TYPE I')
            size_on_server = ftp.size(filename)
            print(f"📏 Taille sur serveur: {size_on_server} bytes")
            
            if size_on_server == file_size:
                print(f"✅ Taille correspondante !")
            else:
                print(f"⚠️ Taille différente: local={file_size}, serveur={size_on_server}")
        else:
            print(f"❌ Fichier NON trouvé sur serveur FTP")
        
        # URL publique
        public_url = f"https://logicamp.org/wordpress/uploads/{filename}"
        print(f"\n🌐 URL publique: {public_url}")
        
        ftp.quit()
        print(f"\n✅ Test {file_type} RÉUSSI")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR {file_type}: {e}")
        return False

def create_test_files():
    """Créer des fichiers de test"""
    test_dir = "/tmp/ftp_test"
    os.makedirs(test_dir, exist_ok=True)
    
    # Fichier PNG test
    png_file = os.path.join(test_dir, "test_image.png")
    with open(png_file, 'wb') as f:
        # Signature PNG minimale
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(b'\x00' * 1000)  # 1KB de données
    
    # Fichier JPG test
    jpg_file = os.path.join(test_dir, "test_image.jpg")
    with open(jpg_file, 'wb') as f:
        # Signature JPEG minimale
        f.write(b'\xff\xd8\xff\xe0')
        f.write(b'\x00' * 1000)  # 1KB de données
    
    # Fichier MP4 test
    mp4_file = os.path.join(test_dir, "test_video.mp4")
    with open(mp4_file, 'wb') as f:
        # Signature MP4 minimale
        f.write(b'\x00\x00\x00\x18ftypisom')
        f.write(b'\x00' * 1000)  # 1KB de données
    
    return png_file, jpg_file, mp4_file

if __name__ == "__main__":
    print("🚀 Diagnostic FTP Images vs Vidéos")
    print(f"Host: {FTP_HOST}")
    print(f"User: {FTP_USER}")
    print(f"Directory: {FTP_DIRECTORY}")
    
    # Créer fichiers de test
    print("\n📝 Création fichiers de test...")
    png_file, jpg_file, mp4_file = create_test_files()
    print("✅ Fichiers créés")
    
    # Tester chaque type
    results = {}
    results['PNG'] = test_ftp_upload(png_file, "PNG")
    results['JPG'] = test_ftp_upload(jpg_file, "JPG")
    results['MP4'] = test_ftp_upload(mp4_file, "MP4")
    
    # Résumé
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ")
    print(f"{'='*60}")
    for file_type, success in results.items():
        status = "✅ OK" if success else "❌ ÉCHEC"
        print(f"{file_type}: {status}")
    
    # Diagnostic
    print(f"\n{'='*60}")
    print("🔧 DIAGNOSTIC")
    print(f"{'='*60}")
    
    if results['MP4'] and not (results['PNG'] or results['JPG']):
        print("⚠️ PROBLÈME IDENTIFIÉ: Les vidéos passent mais pas les images")
        print("   → Possible problème de type MIME ou format dans le code")
    elif all(results.values()):
        print("✅ FTP fonctionne pour TOUS les types")
        print("   → Le problème est dans le code d'upload, pas dans FTP")
    else:
        print("❌ Problème FTP général")
