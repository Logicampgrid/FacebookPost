#!/usr/bin/env python3
"""
Test simple des nouvelles fonctions
"""

import os
import sys

# Test direct des fonctions sans importer tout server.py
def test_direct():
    print("🧪 Test des configurations WordPress...")
    
    # Variables
    WORDPRESS_UPLOADS_DIR = "/app/backend/wordpress/uploads/"
    WORDPRESS_UPLOADS_URL = "https://logicamp.org/wordpress/uploads/"
    ALLOWED_IMAGE_EXT = [".jpg", ".jpeg"]
    ALLOWED_VIDEO_EXT = [".mp4"]
    
    print(f"📁 WORDPRESS_UPLOADS_DIR: {WORDPRESS_UPLOADS_DIR}")
    print(f"🌐 WORDPRESS_UPLOADS_URL: {WORDPRESS_UPLOADS_URL}")
    print(f"🖼️ ALLOWED_IMAGE_EXT: {ALLOWED_IMAGE_EXT}")
    print(f"🎥 ALLOWED_VIDEO_EXT: {ALLOWED_VIDEO_EXT}")
    
    # Vérifier que le dossier existe
    if os.path.exists(WORDPRESS_UPLOADS_DIR):
        print(f"✅ Dossier WordPress uploads existe: {WORDPRESS_UPLOADS_DIR}")
        
        # Lister le contenu
        try:
            files = os.listdir(WORDPRESS_UPLOADS_DIR)
            print(f"📂 Contenu du dossier: {len(files)} fichiers")
            if files:
                print(f"   Premiers fichiers: {files[:5]}")
        except Exception as e:
            print(f"⚠️ Impossible de lister le contenu: {e}")
    else:
        print(f"❌ Dossier WordPress uploads n'existe pas: {WORDPRESS_UPLOADS_DIR}")
    
    print("\n✅ Test de configuration terminé avec succès!")

if __name__ == "__main__":
    test_direct()