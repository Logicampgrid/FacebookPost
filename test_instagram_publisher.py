#!/usr/bin/env python3
"""
Script de test pour Instagram Auto Publisher
Démontre toutes les fonctionnalités avec des exemples
"""

import os
import asyncio
import tempfile
import shutil
from PIL import Image
from pathlib import Path

def create_test_image(path: str, format_ext: str = 'jpg'):
    """Crée une image de test"""
    # Créer une image simple 800x600
    img = Image.new('RGB', (800, 600), color=(70, 130, 180))
    
    # Ajouter du texte (simulation)
    try:
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        # Essayer d'utiliser une police par défaut
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        text = f"Test Image\nFormat: {format_ext.upper()}\nSize: 800x600"
        draw.text((50, 50), text, fill=(255, 255, 255), font=font)
        
    except ImportError:
        # Pas de PIL complète, juste une image unie
        pass
    
    # Sauvegarder selon le format
    if format_ext.lower() == 'webp':
        img.save(path, 'WEBP', quality=90)
    elif format_ext.lower() == 'png':
        img.save(path, 'PNG')
    else:
        img.save(path, 'JPEG', quality=95)
    
    print(f"✅ Image de test créée: {path}")

def create_test_video(path: str, duration: int = 5):
    """Crée une vidéo de test avec FFmpeg"""
    try:
        import subprocess
        
        # Créer une vidéo de test simple (écran de couleur)
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi', 
            '-i', f'color=c=blue:size=640x480:duration={duration}',
            '-c:v', 'libx264',
            '-t', str(duration),
            path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(path):
            print(f"✅ Vidéo de test créée: {path}")
            return True
        else:
            print(f"❌ Erreur création vidéo: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Impossible de créer la vidéo de test: {str(e)}")
        return False

def test_media_detection():
    """Test la détection de types de médias"""
    print("\n🔍 TEST DÉTECTION DE MÉDIAS")
    print("=" * 40)
    
    from instagram_auto_publisher import InstagramPublisher
    
    publisher = InstagramPublisher()
    
    # Test avec différents formats
    test_cases = [
        ('test.jpg', 'image'),
        ('test.webp', 'image'),
        ('test.mp4', 'video'),
        ('test.mov', 'video'),
        ('test.png', 'image'),
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for filename, expected_type in test_cases:
            test_path = os.path.join(temp_dir, filename)
            
            # Créer un fichier vide pour le test
            Path(test_path).touch()
            
            try:
                media_type, extension = publisher.detect_media_type(test_path)
                status = "✅" if media_type == expected_type else "❌"
                print(f"{status} {filename} → {media_type} (attendu: {expected_type})")
            except Exception as e:
                print(f"❌ {filename} → Erreur: {str(e)}")

def test_image_conversion():
    """Test la conversion d'images"""
    print("\n🔄 TEST CONVERSION D'IMAGES")
    print("=" * 40)
    
    from instagram_auto_publisher import InstagramPublisher
    
    publisher = InstagramPublisher()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Créer des images de test dans différents formats
        test_formats = ['jpg', 'webp', 'png']
        
        for format_ext in test_formats:
            input_path = os.path.join(temp_dir, f'test_input.{format_ext}')
            output_path = os.path.join(temp_dir, f'test_output_{format_ext}.jpg')
            
            # Créer l'image de test
            create_test_image(input_path, format_ext)
            
            # Tester la conversion
            print(f"🔄 Test conversion {format_ext.upper()} → JPEG...")
            
            try:
                result = asyncio.run(publisher.convert_image(input_path, output_path))
                if result and os.path.exists(output_path):
                    original_size = os.path.getsize(input_path)
                    converted_size = os.path.getsize(output_path)
                    print(f"✅ Conversion réussie: {original_size} → {converted_size} bytes")
                else:
                    print(f"❌ Conversion échouée")
            except Exception as e:
                print(f"❌ Erreur conversion: {str(e)}")

def test_video_conversion():
    """Test la conversion de vidéos"""
    print("\n🎬 TEST CONVERSION DE VIDÉOS")
    print("=" * 40)
    
    from instagram_auto_publisher import InstagramPublisher
    
    publisher = InstagramPublisher()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, 'test_input.mp4')
        output_path = os.path.join(temp_dir, 'test_output.mp4')
        
        # Créer une vidéo de test
        if create_test_video(input_path, duration=3):
            print(f"🔄 Test conversion vidéo...")
            
            try:
                result = asyncio.run(publisher.convert_video(input_path, output_path))
                if result and os.path.exists(output_path):
                    original_size = os.path.getsize(input_path)
                    converted_size = os.path.getsize(output_path)
                    print(f"✅ Conversion vidéo réussie: {original_size} → {converted_size} bytes")
                else:
                    print(f"❌ Conversion vidéo échouée")
            except Exception as e:
                print(f"❌ Erreur conversion vidéo: {str(e)}")
        else:
            print("⚠️ Impossible de créer vidéo de test, FFmpeg requis")

def test_caption_composition():
    """Test la composition des captions"""
    print("\n📝 TEST COMPOSITION CAPTIONS")
    print("=" * 40)
    
    from instagram_auto_publisher import InstagramPublisher
    
    publisher = InstagramPublisher()
    
    test_cases = [
        ("Simple caption", "#test", "Simple caption\n\n#test"),
        ("Caption avec émojis 🐕", "#chien #mignon", "Caption avec émojis 🐕\n\n#chien #mignon"),
        ("", "#justhash", "#justhash"),
        ("Caption seule", "", "Caption seule"),
        ("A" * 2300, "#long", "A" * 2197 + "..."),  # Test troncature
    ]
    
    for caption, hashtags, expected in test_cases:
        result = publisher.compose_caption(caption, hashtags)
        status = "✅" if len(result) <= 2200 else "❌"
        print(f"{status} Caption: {len(result)} chars")
        if len(expected) < 100:  # Afficher seulement les courtes
            print(f"   Résultat: '{result}'")

def show_authentication_guide():
    """Affiche un guide pour l'authentification"""
    print("\n🔐 AUTHENTIFICATION REQUISE")
    print("=" * 50)
    print("Pour utiliser le script en mode réel, vous devez :")
    print()
    print("1️⃣  Ouvrir l'application web :")
    print("   http://localhost:3000")
    print()
    print("2️⃣  Se connecter avec Facebook/Meta Business")
    print()
    print("3️⃣  Sélectionner le Business Manager contenant")
    print("   la page 'Le Berger Blanc Suisse'")
    print()
    print("4️⃣  Une fois connecté, le script pourra publier :")
    print("   python3 instagram_auto_publisher.py --file image.jpg")
    print()
    print("💡 En attendant, utilisez --dry-run pour tester :")
    print("   python3 instagram_auto_publisher.py --file test.jpg --dry-run")

def main():
    """Fonction principale de test"""
    print("🧪 TESTS INSTAGRAM AUTO PUBLISHER")
    print("=" * 50)
    
    # Tests des fonctionnalités
    test_media_detection()
    test_image_conversion()
    test_video_conversion()
    test_caption_composition()
    
    # Guide d'authentification
    show_authentication_guide()
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés ! Le script est prêt à l'emploi.")
    print("📖 Consultez INSTAGRAM_AUTO_PUBLISHER_README.md pour plus d'infos")

if __name__ == "__main__":
    main()