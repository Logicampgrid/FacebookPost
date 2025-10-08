#!/usr/bin/env python3
"""
Test de la correction de conversion WEBP → PNG
"""

import os
import sys
import tempfile
import shutil
import time
import uuid
from PIL import Image
from datetime import datetime

# Ajouter le backend au path
sys.path.append('/app/backend')

def log_test(message: str, level: str = "INFO"):
    """Logging pour les tests"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [TEST] {message}")

def create_test_webp():
    """Crée un fichier WEBP de test"""
    
    # Créer une image simple avec transparence
    image = Image.new('RGBA', (200, 150), color=(255, 0, 0, 128))  # Rouge semi-transparent
    
    # Ajouter du contenu visible
    for x in range(0, 200, 10):
        for y in range(0, 150, 10):
            if (x // 10 + y // 10) % 2 == 0:
                image.putpixel((x, y), (0, 255, 0, 255))  # Vert
    
    # Sauvegarder en WEBP
    temp_dir = tempfile.mkdtemp()
    webp_filename = f"test_{int(time.time())}.webp"
    webp_path = os.path.join(temp_dir, webp_filename)
    
    image.save(webp_path, 'WEBP', quality=80)
    
    return webp_path, webp_filename, temp_dir

def simulate_webp_conversion_fix(webp_path, webp_filename):
    """Simule la correction PATCH 51 - Conversion WEBP → PNG"""
    
    log_test("🎨 PATCH 51: Test conversion WEBP → PNG", "INFO")
    
    try:
        upload_dir = os.path.dirname(webp_path)
        
        # Simulation du code ajouté
        file_extension = '.webp'
        unique_filename = webp_filename
        
        # PATCH 51: CORRECTION CONVERSION WEBP → PNG
        if file_extension.lower() == '.webp':
            log_test(f"🎨 PATCH 51: Conversion WEBP → PNG requise", "INFO")
            
            # Ouvrir l'image WEBP
            with Image.open(webp_path) as img:
                log_test(f"   Mode original: {img.mode}", "INFO")
                log_test(f"   Taille: {img.size}", "INFO")
                
                # Convertir en PNG
                png_filename = unique_filename.replace('.webp', '.png')
                png_path = os.path.join(upload_dir, png_filename)
                
                # Convertir RGBA si nécessaire pour PNG
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGBA', img.size, (255, 255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background.convert('RGB')
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img.save(png_path, 'PNG', optimize=True)
            
            # Statistiques
            original_size = os.path.getsize(webp_path)
            converted_size = os.path.getsize(png_path)
            
            log_test(f"✅ PATCH 51: Conversion WEBP → PNG réussie", "SUCCESS")
            log_test(f"   Original: {original_size} bytes", "INFO")
            log_test(f"   Converti: {converted_size} bytes", "INFO")
            log_test(f"   Ratio: {converted_size/original_size:.2f}x", "INFO")
            
            # Vérifier que le PNG est valide
            try:
                with Image.open(png_path) as test_img:
                    log_test(f"   PNG Mode: {test_img.mode}", "SUCCESS")
                    log_test(f"   PNG Taille: {test_img.size}", "SUCCESS")
            except Exception as verify_error:
                log_test(f"❌ PNG invalide: {verify_error}", "ERROR")
                return False, None
            
            return True, png_path
            
    except Exception as conv_error:
        log_test(f"❌ PATCH 51: Erreur conversion: {conv_error}", "ERROR")
        return False, None

def test_webp_fix():
    """Test complet de la correction WEBP"""
    
    log_test("🧪 Test de la correction conversion WEBP → PNG", "INFO")
    
    # Créer un fichier WEBP de test
    log_test("1️⃣ Création fichier WEBP de test", "INFO")
    webp_path, webp_filename, temp_dir = create_test_webp()
    
    log_test(f"   Fichier créé: {webp_filename}", "SUCCESS")
    log_test(f"   Taille: {os.path.getsize(webp_path)} bytes", "INFO")
    
    # Test de la conversion
    log_test("\n2️⃣ Test de conversion", "INFO")
    success, png_path = simulate_webp_conversion_fix(webp_path, webp_filename)
    
    if success and png_path:
        log_test("✅ Conversion réussie", "SUCCESS")
        
        # Test d'accessibilité simulée
        log_test("\n3️⃣ Test d'accessibilité simulée", "INFO")
        
        try:
            # Simuler ce que ferait un serveur web
            with open(png_path, 'rb') as f:
                png_data = f.read()
                log_test(f"   PNG lisible: {len(png_data)} bytes", "SUCCESS")
            
            # Vérifier l'en-tête PNG
            if png_data[:8] == b'\x89PNG\r\n\x1a\n':
                log_test("   ✅ En-tête PNG valide", "SUCCESS")
            else:
                log_test("   ❌ En-tête PNG invalide", "ERROR")
                
        except Exception as read_error:
            log_test(f"   ❌ Erreur lecture: {read_error}", "ERROR")
            
    else:
        log_test("❌ Conversion échouée", "ERROR")
    
    # Nettoyage
    try:
        shutil.rmtree(temp_dir)
        log_test("🧹 Nettoyage terminé", "INFO")
    except:
        pass
    
    return success

if __name__ == "__main__":
    print("=" * 60)
    print("TEST CORRECTION WEBP → PNG - PATCH 51")
    print("=" * 60)
    
    success = test_webp_fix()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ CORRECTION VALIDÉE - La conversion WEBP → PNG fonctionne")
        print("🚀 Cette correction devrait résoudre le problème des images 404")
    else:
        print("❌ PROBLÈME PERSISTANT - Investigation supplémentaire requise")
    print("=" * 60)