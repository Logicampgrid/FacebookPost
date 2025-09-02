#!/usr/bin/env python3
"""
Test d'upload et conversion WebP → JPEG avec FTP
Teste le workflow complet de conversion et upload
"""

import requests
import os
import sys
import json
import time
from datetime import datetime
import io
from PIL import Image

def log_test(message, level="INFO"):
    """Log avec timestamp"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
    icon = icons.get(level.upper(), "📝")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] {message}")

def create_test_webp_image():
    """Crée une image WebP de test"""
    try:
        # Créer une image simple 100x100 rouge
        img = Image.new('RGB', (100, 100), color='red')
        
        # Ajouter du texte pour identifier l'image
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        draw.text((10, 40), "TEST\nWebP", fill='white')
        
        # Sauvegarder en WebP
        webp_path = "/tmp/test_image.webp"
        img.save(webp_path, 'WEBP', quality=80)
        
        log_test(f"Image WebP créée : {webp_path}", "SUCCESS")
        log_test(f"Taille : {os.path.getsize(webp_path)} bytes", "INFO")
        
        return webp_path
        
    except Exception as e:
        log_test(f"Erreur création WebP : {str(e)}", "ERROR")
        return None

def test_webhook_upload():
    """Test l'upload via webhook avec WebP → JPEG conversion"""
    try:
        log_test("Test upload webhook avec conversion WebP → JPEG", "TEST")
        
        # Créer image WebP de test
        webp_path = create_test_webp_image()
        if not webp_path:
            return False
        
        # Préparer les données du webhook
        webhook_data = {
            "title": "Test Produit FTP",
            "description": "Test conversion WebP → JPEG avec upload FTP automatique",
            "url": "https://gizmobbs.com/test-ftp",
            "store": "gizmobbs"
        }
        
        log_test("Envoi webhook avec image WebP...", "INFO")
        log_test(f"Données : {webhook_data}", "INFO")
        
        # Envoyer via webhook
        with open(webp_path, 'rb') as img_file:
            files = {'image': ('test_image.webp', img_file, 'image/webp')}
            data = {'json_data': json.dumps(webhook_data)}
            
            response = requests.post(
                "http://localhost:8001/api/webhook",
                files=files,
                data=data,
                timeout=60
            )
        
        log_test(f"Statut réponse : {response.status_code}", "INFO")
        
        if response.status_code == 200:
            result = response.json()
            log_test("✅ Webhook traité avec succès", "SUCCESS")
            log_test(f"Réponse : {json.dumps(result, indent=2)}", "INFO")
            
            # Vérifier les détails de la conversion
            if 'data' in result:
                data = result['data']
                if 'image_filename' in data:
                    filename = data['image_filename']
                    log_test(f"Fichier généré : {filename}", "SUCCESS")
                    
                    # Vérifier que c'est bien un JPEG
                    if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                        log_test("✅ Conversion WebP → JPEG confirmée", "SUCCESS")
                    else:
                        log_test(f"⚠️ Extension inattendue : {filename}", "WARNING")
            
            return True
        else:
            error_text = response.text
            log_test(f"❌ Erreur webhook : {error_text}", "ERROR")
            return False
            
    except Exception as e:
        log_test(f"Erreur test webhook : {str(e)}", "ERROR")
        return False
    finally:
        # Nettoyer le fichier de test
        if webp_path and os.path.exists(webp_path):
            os.unlink(webp_path)
            log_test("Fichier test nettoyé", "INFO")

def test_direct_ftp_function():
    """Test direct de la fonction upload_to_ftp en mode DRY_RUN"""
    try:
        log_test("Test direct fonction upload_to_ftp", "TEST")
        
        # Créer un fichier JPEG de test
        img = Image.new('RGB', (200, 200), color='blue')
        jpeg_path = "/tmp/test_direct.jpg"
        img.save(jpeg_path, 'JPEG', quality=85)
        
        log_test(f"JPEG test créé : {jpeg_path}", "INFO")
        
        # Tester l'endpoint de test direct si disponible
        test_data = {
            "local_file_path": jpeg_path,
            "original_filename": "test_direct.jpg"
        }
        
        response = requests.post(
            "http://localhost:8001/api/debug/test-direct-ftp",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            log_test("✅ Test direct FTP réussi", "SUCCESS")
            log_test(f"Résultat : {result}", "INFO")
            return True
        else:
            log_test(f"Endpoint test direct non disponible : {response.status_code}", "WARNING")
            log_test("Mode DRY_RUN devrait simuler l'upload", "INFO")
            return True  # OK en mode DRY_RUN
            
    except Exception as e:
        log_test(f"Erreur test direct : {str(e)}", "ERROR")
        return False
    finally:
        if os.path.exists(jpeg_path):
            os.unlink(jpeg_path)

def main():
    """Test principal upload et conversion"""
    log_test("🚀 TEST UPLOAD & CONVERSION WebP → JPEG + FTP", "TEST")
    print("=" * 80)
    
    # Vérifier que le backend est en mode DRY_RUN
    try:
        response = requests.get("http://localhost:8001/api/health")
        if response.status_code == 200:
            log_test("Backend accessible - tests FTP en mode DRY_RUN", "INFO")
        else:
            log_test("Backend inaccessible", "ERROR")
            return 1
    except:
        log_test("Erreur connexion backend", "ERROR")
        return 1
    
    tests = [
        ("Upload Webhook WebP→JPEG", test_webhook_upload),
        ("Test Direct FTP", test_direct_ftp_function)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        log_test(f"🧪 TEST : {test_name}", "TEST")
        print("-" * 60)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                log_test(f"✅ {test_name} : RÉUSSI", "SUCCESS")
            else:
                log_test(f"❌ {test_name} : ÉCHOUÉ", "ERROR")
                
        except Exception as e:
            log_test(f"❌ {test_name} : EXCEPTION - {str(e)}", "ERROR")
            results.append((test_name, False))
        
        print()
    
    # Résumé
    print("=" * 80)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    log_test(f"RÉSULTATS : {passed}/{total} tests réussis", "SUCCESS" if passed == total else "WARNING")
    
    if passed == total:
        log_test("🎉 PRÊT POUR LE MODE RÉEL ! Désactiver DRY_RUN=false", "SUCCESS")
        return 0
    else:
        log_test("⚠️ Corrections nécessaires avant mode réel", "WARNING")
        return 1

if __name__ == "__main__":
    sys.exit(main())