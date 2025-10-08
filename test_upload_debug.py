#!/usr/bin/env python3
"""
Test de debug d'upload d'images vs vidéos
"""

import os
import sys
import tempfile
from PIL import Image
from datetime import datetime

# Ajouter le backend au path
sys.path.append('/app/backend')

try:
    from ftp_manager_patch29 import init_ftp_manager, upload_for_publication
    FTP_AVAILABLE = True
except Exception as e:
    print(f"❌ FTP Manager non disponible: {e}")
    FTP_AVAILABLE = False

def log_test(message: str, level: str = "INFO"):
    """Logging pour les tests"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [DEBUG] {message}")

def create_test_image(format_type="PNG"):
    """Crée une image de test"""
    
    # Créer une image simple 100x100
    image = Image.new('RGB', (100, 100), color='red')
    
    # Fichier temporaire
    temp_dir = tempfile.mkdtemp()
    if format_type.upper() == "PNG":
        filename = f"test_image_{int(datetime.now().timestamp())}.png"
        temp_path = os.path.join(temp_dir, filename)
        image.save(temp_path, 'PNG')
    elif format_type.upper() == "JPG":
        filename = f"test_image_{int(datetime.now().timestamp())}.jpg"
        temp_path = os.path.join(temp_dir, filename)
        image.save(temp_path, 'JPEG')
    elif format_type.upper() == "WEBP":
        filename = f"test_image_{int(datetime.now().timestamp())}.webp"
        temp_path = os.path.join(temp_dir, filename)
        image.save(temp_path, 'WEBP')
    
    return temp_path, filename

def create_test_video():
    """Crée un fichier vidéo de test (simple fichier texte avec extension .mp4)"""
    temp_dir = tempfile.mkdtemp()
    filename = f"test_video_{int(datetime.now().timestamp())}.mp4"
    temp_path = os.path.join(temp_dir, filename)
    
    # Créer un faux fichier MP4 (juste pour tester l'upload)
    test_content = b"FAKE MP4 FOR TESTING " * 1000  # 20KB de données
    
    with open(temp_path, 'wb') as f:
        f.write(test_content)
    
    return temp_path, filename

def test_ftp_upload_comparison():
    """Compare l'upload d'images vs vidéos"""
    
    if not FTP_AVAILABLE:
        log_test("FTP Manager non disponible - impossible de tester", "ERROR")
        return
    
    # Initialiser le gestionnaire FTP
    log_test("Initialisation du gestionnaire FTP...", "INFO")
    init_ftp_manager()
    
    # Tester différents formats d'image
    formats_to_test = [
        ("PNG", create_test_image, "PNG"),
        ("JPG", create_test_image, "JPG"),  
        ("WEBP", create_test_image, "WEBP"),
        ("MP4", create_test_video, None),
    ]
    
    results = {}
    
    for format_name, creator_func, format_arg in formats_to_test:
        log_test(f"\n🧪 Test upload {format_name}:", "INFO")
        
        try:
            # Créer le fichier de test
            if format_arg:
                test_path, filename = creator_func(format_arg)
            else:
                test_path, filename = creator_func()
            
            log_test(f"Fichier créé: {filename} ({os.path.getsize(test_path)} bytes)", "INFO")
            
            # Tester l'upload FTP
            log_test(f"Upload FTP en cours...", "INFO")
            success, url, error = upload_for_publication(test_path, filename)
            
            if success and url:
                log_test(f"✅ SUCCÈS: {url}", "SUCCESS")
                results[format_name] = {"success": True, "url": url, "error": None}
                
                # Test HTTP
                import requests
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        log_test(f"✅ HTTP OK: {response.status_code}", "SUCCESS")
                    else:
                        log_test(f"❌ HTTP ÉCHEC: {response.status_code}", "ERROR")
                except Exception as http_error:
                    log_test(f"❌ HTTP ERROR: {http_error}", "ERROR")
                    
            else:
                log_test(f"❌ ÉCHEC: {error}", "ERROR")
                results[format_name] = {"success": False, "url": None, "error": error}
            
            # Nettoyer
            try:
                os.remove(test_path)
                os.rmdir(os.path.dirname(test_path))
            except:
                pass
                
        except Exception as e:
            log_test(f"❌ ERREUR GÉNÉRALE: {e}", "ERROR")
            results[format_name] = {"success": False, "url": None, "error": str(e)}
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for format_name, result in results.items():
        if result["success"]:
            print(f"✅ {format_name}: SUCCÈS - {result['url']}")
        else:
            print(f"❌ {format_name}: ÉCHEC - {result['error']}")
    
    return results

if __name__ == "__main__":
    print("=" * 60)
    print("DEBUG UPLOAD FTP - IMAGES vs VIDÉOS")
    print("=" * 60)
    
    test_ftp_upload_comparison()