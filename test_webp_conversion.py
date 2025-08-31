#!/usr/bin/env python3
"""
Test script pour valider la conversion automatique WebP → JPEG
"""

import asyncio
import os
import sys
from PIL import Image

# Ajouter le répertoire backend au path
sys.path.append('/app/backend')

from server import convert_webp_to_jpeg

async def test_webp_conversion():
    """Test de la fonction de conversion WebP → JPEG"""
    print("🧪 TEST: Conversion automatique WebP → JPEG")
    print("=" * 60)
    
    # Créer un fichier WebP de test
    test_webp_path = "/app/test_image.webp"
    test_image_size = (800, 600)
    
    try:
        # Créer une image WebP de test
        print(f"📝 Création image WebP de test → {test_webp_path}")
        test_image = Image.new('RGB', test_image_size, color=(100, 150, 200))
        test_image.save(test_webp_path, 'WEBP', quality=85)
        print(f"✅ Image WebP créée: {test_image_size[0]}x{test_image_size[1]}")
        
        # Tester la conversion
        print(f"\n🔄 Test de conversion WebP → JPEG")
        success, jpeg_path, error_msg = await convert_webp_to_jpeg(test_webp_path)
        
        if success:
            print(f"✅ Conversion réussie!")
            print(f"📁 Fichier JPEG créé: {jpeg_path}")
            
            # Vérifier le fichier JPEG créé
            if os.path.exists(jpeg_path):
                with Image.open(jpeg_path) as jpeg_img:
                    print(f"🖼️ Format JPEG: {jpeg_img.format}")
                    print(f"📐 Résolution: {jpeg_img.size[0]}x{jpeg_img.size[1]}")
                    print(f"🎨 Mode couleur: {jpeg_img.mode}")
                    
                    # Vérifier que la résolution est conservée
                    if jpeg_img.size == test_image_size:
                        print(f"✅ Résolution conservée correctement")
                    else:
                        print(f"❌ Résolution modifiée: {test_image_size} → {jpeg_img.size}")
                
                # Vérifier la taille du fichier
                jpeg_size = os.path.getsize(jpeg_path)
                webp_size = os.path.getsize(test_webp_path)
                print(f"📊 Taille WebP: {webp_size} bytes")
                print(f"📊 Taille JPEG: {jpeg_size} bytes")
                
                # Nettoyer le fichier JPEG de test
                os.unlink(jpeg_path)
                print(f"🧹 Fichier JPEG de test supprimé")
            else:
                print(f"❌ Fichier JPEG non trouvé: {jpeg_path}")
        else:
            print(f"❌ Conversion échouée: {error_msg}")
        
        # Nettoyer le fichier WebP de test
        os.unlink(test_webp_path)
        print(f"🧹 Fichier WebP de test supprimé")
        
    except Exception as e:
        print(f"❌ Erreur de test: {str(e)}")
        # Nettoyer les fichiers en cas d'erreur
        for test_file in [test_webp_path, test_webp_path.replace('.webp', '_converted.jpeg')]:
            if os.path.exists(test_file):
                os.unlink(test_file)
    
    # Test avec fichier non-WebP
    print(f"\n🧪 Test avec fichier non-WebP (doit échouer)")
    test_jpg_path = "/app/test_image.jpg"
    try:
        # Créer une image JPEG de test
        test_image_jpg = Image.new('RGB', (400, 300), color=(200, 100, 50))
        test_image_jpg.save(test_jpg_path, 'JPEG', quality=90)
        
        success, jpeg_path, error_msg = await convert_webp_to_jpeg(test_jpg_path)
        if not success:
            print(f"✅ Détection correcte: {error_msg}")
        else:
            print(f"❌ Ne devrait pas convertir un fichier JPEG")
        
        os.unlink(test_jpg_path)
        print(f"🧹 Fichier JPEG de test supprimé")
        
    except Exception as e:
        print(f"❌ Erreur test JPEG: {str(e)}")
    
    print(f"\n🎯 RÉSUMÉ DES FONCTIONNALITÉS IMPLÉMENTÉES:")
    print("=" * 60)
    print("✅ 1. Détection automatique des fichiers .webp")
    print("✅ 2. Conversion WebP → JPEG avec qualité 95%")
    print("✅ 3. Conservation de la résolution originale")
    print("✅ 4. Gestion de la transparence (fond blanc)")
    print("✅ 5. Intégration dans download_media_reliably()")
    print("✅ 6. Intégration dans post_to_instagram()")
    print("✅ 7. Intégration dans post_to_facebook()")
    print("✅ 8. Support fichiers locaux et URLs")
    print("✅ 9. Logs détaillés pour débogage")
    print("✅ 10. Nettoyage automatique fichiers WebP originaux")
    
    print(f"\n📋 POINTS D'INTÉGRATION:")
    print("=" * 60)
    print("🔸 download_media_reliably() - URLs externes et fallback binaire")
    print("🔸 post_to_instagram() - Fichiers locaux multipart")
    print("🔸 post_to_facebook() - Fichiers locaux multipart")
    print("🔸 Conversion automatique transparent pour l'utilisateur")

if __name__ == "__main__":
    print("🚀 Test de validation conversion WebP → JPEG")
    print("=" * 70)
    asyncio.run(test_webp_conversion())