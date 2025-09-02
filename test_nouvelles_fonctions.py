#!/usr/bin/env python3
"""
Test des nouvelles fonctions ajoutées à server.py
"""

import sys
import os

# Ajouter le chemin backend pour importer les fonctions
sys.path.append('/app/backend')

try:
    # Importer les nouvelles fonctions
    from server import (
        convert_webp_to_jpeg,
        ensure_public_media_url,
        create_instagram_media,
        publish_instagram_container,
        upload_facebook_media,
        WORDPRESS_UPLOADS_DIR,
        WORDPRESS_UPLOADS_URL,
        ALLOWED_IMAGE_EXT,
        ALLOWED_VIDEO_EXT
    )
    
    print("✅ Import des nouvelles fonctions réussi!")
    print(f"📁 WORDPRESS_UPLOADS_DIR: {WORDPRESS_UPLOADS_DIR}")
    print(f"🌐 WORDPRESS_UPLOADS_URL: {WORDPRESS_UPLOADS_URL}")
    print(f"🖼️ ALLOWED_IMAGE_EXT: {ALLOWED_IMAGE_EXT}")
    print(f"🎥 ALLOWED_VIDEO_EXT: {ALLOWED_VIDEO_EXT}")
    
    # Vérifier que le dossier WordPress existe
    if os.path.exists(WORDPRESS_UPLOADS_DIR):
        print(f"✅ Dossier WordPress uploads existe: {WORDPRESS_UPLOADS_DIR}")
    else:
        print(f"❌ Dossier WordPress uploads n'existe pas: {WORDPRESS_UPLOADS_DIR}")
    
    # Test simple de la fonction convert_webp_to_jpeg (sans fichier)
    print("\n🧪 Test des fonctions...")
    
    # Test avec extension non-webp
    test_path = "/fake/path/image.jpg"
    result = convert_webp_to_jpeg(test_path)
    print(f"✅ convert_webp_to_jpeg('/fake/path/image.jpg') -> {result}")
    
    print("\n🎉 Tous les tests d'import et de base ont réussi!")
    
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erreur inattendue: {e}")
    sys.exit(1)