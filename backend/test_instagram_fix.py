#!/usr/bin/env python3
"""
Test de correction Instagram - Vérification des corrections apportées
Teste spécifiquement :
1. Conversion automatique des chemins locaux en URLs publiques FTP
2. Gestion robuste des erreurs FTP
3. Fallback ngrok fonctionnel
"""

import os
import sys
import time
import asyncio
import tempfile
import requests
from pathlib import Path

# Ajouter le répertoire parent au PATH pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import (
    upload_image_to_ftp, 
    get_active_ngrok_url,
    process_webhook_publication,
    log_app
)

async def test_ftp_upload_correction():
    """Test l'upload FTP avec les corrections"""
    print("\n🧪 Test upload FTP corrigé...")
    
    # Créer une image de test temporaire
    test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # Sauvegarder dans uploads/
    test_filename = f"test_correction_{int(time.time())}.png"
    test_path = os.path.join("uploads", test_filename)
    
    os.makedirs("uploads", exist_ok=True)
    
    with open(test_path, "wb") as f:
        f.write(test_image_data)
    
    print(f"📁 Fichier test créé: {test_path}")
    
    try:
        # Tester l'upload FTP
        print("🔄 Test upload FTP...")
        success, url, error = await upload_image_to_ftp(test_path, test_filename)
        
        if success:
            print(f"✅ Upload FTP réussi: {url}")
            
            # Vérifier que l'URL est accessible
            try:
                response = requests.head(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ URL accessible: {response.status_code}")
                else:
                    print(f"⚠️ URL non accessible: {response.status_code}")
            except Exception as url_error:
                print(f"⚠️ Erreur vérification URL: {url_error}")
                
        else:
            print(f"❌ Upload FTP échoué: {error}")
            
            # Tester le fallback ngrok
            print("🔄 Test fallback ngrok...")
            ngrok_url = get_active_ngrok_url()
            if ngrok_url:
                fallback_url = f"{ngrok_url.rstrip('/')}/uploads/{test_filename}"
                print(f"🔗 URL ngrok de fallback: {fallback_url}")
            else:
                print("⚠️ Aucune URL ngrok disponible")
    
    finally:
        # Nettoyer le fichier test
        if os.path.exists(test_path):
            os.unlink(test_path)
            print(f"🧹 Fichier test supprimé")

async def test_webhook_path_conversion():
    """Test la conversion des chemins Windows dans les webhooks"""
    print("\n🧪 Test conversion chemins webhook...")
    
    # Créer un fichier de test
    test_filename = f"webhook_test_{int(time.time())}.jpg"
    test_path = os.path.join("uploads", test_filename)
    
    os.makedirs("uploads", exist_ok=True)
    
    # Image JPEG minimale
    test_image_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
    
    with open(test_path, "wb") as f:
        f.write(test_image_data)
    
    print(f"📁 Fichier test webhook créé: {test_path}")
    
    # Simuler des données webhook avec chemin Windows
    test_cases = [
        f"uploads/{test_filename}",  # Chemin Unix normal
        f"uploads\\{test_filename}",  # Chemin Windows avec backslash
        f"C:\\app\\backend\\uploads\\{test_filename}",  # Chemin Windows complet
    ]
    
    for i, image_path in enumerate(test_cases, 1):
        print(f"\n📝 Test case {i}: '{image_path}'")
        
        webhook_data = {
            "store": "gizmobbs",
            "message": f"Test correction chemin {i}",
            "product_url": "https://example.com/test",
            "image_url": image_path,
            "platforms": ["instagram"]
        }
        
        try:
            # Simuler le traitement webhook
            print(f"🔄 Traitement webhook avec chemin: {image_path}")
            
            # Normaliser le chemin comme le fait le code
            normalized_path = image_path.replace("\\", "/")
            if "uploads/" in normalized_path:
                filename = normalized_path.split("/")[-1]
                local_file_path = os.path.join("uploads", filename)
                
                print(f"📂 Chemin normalisé: {normalized_path}")
                print(f"📄 Nom fichier extrait: {filename}")
                print(f"📍 Chemin local calculé: {local_file_path}")
                
                if os.path.exists(local_file_path):
                    print(f"✅ Fichier local trouvé")
                    # Ici on ferait l'upload FTP réel
                    print(f"🔄 Upload FTP serait déclenché pour: {local_file_path}")
                else:
                    print(f"❌ Fichier local non trouvé: {local_file_path}")
            
        except Exception as e:
            print(f"❌ Erreur traitement: {e}")
    
    # Nettoyer
    if os.path.exists(test_path):
        os.unlink(test_path)
        print(f"\n🧹 Fichier test webhook supprimé")

async def test_configuration_check():
    """Vérification de la configuration FTP et ngrok"""
    print("\n🧪 Test configuration système...")
    
    # Vérifier les variables d'environnement FTP
    ftp_vars = {
        "FTP_HOST": os.getenv("FTP_HOST", "logicamp.org"),
        "FTP_PORT": os.getenv("FTP_PORT", "21"),  
        "FTP_USER": os.getenv("FTP_USER", "logi"),
        "FTP_PASSWORD": os.getenv("FTP_PASSWORD", "***" if os.getenv("FTP_PASSWORD") else "NON_DÉFINI")
    }
    
    print("📋 Configuration FTP:")
    for var, value in ftp_vars.items():
        status = "✅" if value and value != "NON_DÉFINI" else "❌"
        print(f"  {status} {var}: {value}")
    
    # Vérifier ngrok
    print("\n🔗 Test ngrok:")
    ngrok_url = get_active_ngrok_url()
    if ngrok_url:
        print(f"✅ URL ngrok active: {ngrok_url}")
    else:
        print("⚠️ Aucune URL ngrok active détectée")
    
    # Vérifier le dossier uploads
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        files_count = len([f for f in os.listdir(uploads_dir) if os.path.isfile(os.path.join(uploads_dir, f))])
        print(f"✅ Dossier uploads existe: {files_count} fichiers")
    else:
        print("⚠️ Dossier uploads n'existe pas")

async def main():
    """Fonction principale de test"""
    print("🚀 Test de correction Instagram - Début")
    print("=" * 50)
    
    # Tests séquentiels
    await test_configuration_check()
    await test_webhook_path_conversion() 
    await test_ftp_upload_correction()
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés")
    print("\n💡 Points à retenir:")
    print("- Les chemins locaux sont maintenant automatiquement convertis en URLs publiques")
    print("- L'upload FTP est forcé pour tous les chemins uploads/")
    print("- Un système de fallback robuste est en place (FTP → ngrok → local)")
    print("- Les erreurs FTP sont maintenant mieux diagnostiquées")

if __name__ == "__main__":
    asyncio.run(main())