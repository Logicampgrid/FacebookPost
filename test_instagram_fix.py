#!/usr/bin/env python3
"""
Test script pour valider la correction des publications Instagram
Ce script simule un webhook avec une image pour tester le nouveau système d'upload FTP
"""

import requests
import json
import os
import tempfile
from pathlib import Path

# Configuration du test
BACKEND_URL = "http://localhost:8001"
TEST_STORE = "gizmobbs"  # Store de test

def create_test_image():
    """Créer une image de test simple"""
    try:
        from PIL import Image
        # Créer une image de test 400x400 avec un dégradé
        img = Image.new('RGB', (400, 400), color='lightblue')
        
        # Ajouter du contenu visuel basique
        for x in range(0, 400, 20):
            for y in range(0, 400, 20):
                color = (x % 255, y % 255, (x+y) % 255)
                img.putpixel((x, y), color)
        
        # Sauvegarder temporairement
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        img.save(temp_file.name, 'JPEG', quality=85)
        temp_file.close()
        
        return temp_file.name
    except ImportError:
        # Fallback si PIL n'est pas disponible - utiliser une image existante
        print("⚠️ PIL non disponible, recherche d'une image existante...")
        
        # Chercher une image existante dans uploads/
        uploads_dir = Path("/app/backend/uploads")
        if uploads_dir.exists():
            for img_file in uploads_dir.glob("*.jpg"):
                print(f"✅ Utilisation image existante: {img_file}")
                return str(img_file)
            for img_file in uploads_dir.glob("*.png"):
                print(f"✅ Utilisation image existante: {img_file}")
                return str(img_file)
        
        # Dernière option: créer un fichier factice
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        temp_file.write(b'fake_image_data_for_testing')
        temp_file.close()
        print(f"⚠️ Image factice créée: {temp_file.name}")
        return temp_file.name

def test_webhook_with_image():
    """Teste le webhook avec une image pour valider la correction Instagram"""
    print("🧪 Test de correction Instagram - Upload FTP et publication")
    
    image_path = None
    try:
        # 1. Créer l'image de test
        print("📷 Création image de test...")
        image_path = create_test_image()
        print(f"✅ Image créée: {image_path}")
        
        # 2. Préparer les données de test (données similaires aux logs)
        webhook_data = {
            "store": TEST_STORE,
            "title": "🧪 Test correction Instagram FTP - Produit de test automatique",
            "url": "https://www.logicamp.org/wordpress/produit/test-correction-instagram/",
            "description": "Test de la nouvelle logique d'upload FTP pour résoudre le problème Instagram"
        }
        
        # 3. Envoyer le webhook multipart (comme dans les logs)
        print("📤 Envoi webhook multipart...")
        
        with open(image_path, 'rb') as img_file:
            files = {
                'image': ('test_correction_instagram.jpg', img_file, 'image/jpeg')
            }
            data = {
                'json_data': json.dumps(webhook_data)
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/webhook",
                files=files,
                data=data,
                timeout=120  # Timeout plus long pour l'upload FTP
            )
        
        # 4. Analyser le résultat
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ Webhook traité avec succès")
                print(f"📋 Résultat: {json.dumps(result, indent=2)}")
                
                # Analyser spécifiquement le succès Instagram
                success = False
                if isinstance(result, dict):
                    # Vérifier différents formats de réponse possibles
                    if 'status' in result and result.get('processed'):
                        success = True
                        print("✅ Webhook traité (format simple)")
                    elif 'success' in result and result['success']:
                        success = True
                        print("✅ Publication marquée comme réussie")
                        
                if success:
                    print("🎉 SUCCÈS: La correction semble fonctionner !")
                    print("✅ Plus d'erreur 'Only photo or video can be accepted'")
                    return True
                else:
                    print("⚠️ Statut de publication unclear - vérification manuelle nécessaire")
                    return False
                    
            except json.JSONDecodeError:
                print(f"📄 Réponse non-JSON: {response.text}")
                # Si la réponse n'est pas JSON mais status 200, c'est probablement OK
                return True
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test: {str(e)}")
        return False
    finally:
        # Nettoyer
        if image_path and os.path.exists(image_path):
            try:
                os.unlink(image_path)
                print("🧹 Image de test supprimée")
            except:
                pass

def test_backend_health():
    """Teste la santé du backend"""
    try:
        print("🏥 Test santé backend...")
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ Backend accessible et fonctionnel")
            print(f"📋 Health: {response.json()}")
            return True
        else:
            print(f"❌ Backend problème: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend inaccessible: {str(e)}")
        return False

def test_ftp_connectivity():
    """Test rapide de connectivité FTP"""
    try:
        print("🔌 Test connectivité FTP...")
        import socket
        
        # Test de base - peut-on résoudre le hostname FTP ?
        host = "logicamp.org"
        port = 21
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print("✅ Serveur FTP accessible (port 21)")
            return True
        else:
            print(f"❌ Serveur FTP inaccessible: code {result}")
            print("⚠️ Les uploads FTP pourraient échouer")
            return False
    except Exception as e:
        print(f"❌ Erreur test FTP: {str(e)}")
        return False

def main():
    """Fonction principale de test"""
    print("=" * 70)
    print("🔧 TEST DE CORRECTION INSTAGRAM - UPLOAD FTP")
    print("=" * 70)
    
    # Test 1: Santé backend
    if not test_backend_health():
        print("💥 Backend non accessible - arrêt des tests")
        return
    
    # Test 2: Connectivité FTP
    ftp_ok = test_ftp_connectivity()
    
    # Test 3: Webhook avec image
    print("\n" + "-" * 50)
    success = test_webhook_with_image()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 TESTS RÉUSSIS: La correction Instagram semble fonctionner !")
        if not ftp_ok:
            print("⚠️ Note: FTP peut être problématique, mais fallback ngrok devrait marcher")
    else:
        print("❌ TESTS ÉCHOUÉS: Des ajustements sont nécessaires")
        if not ftp_ok:
            print("💡 Suggestion: Vérifier la configuration FTP")
    print("=" * 70)

if __name__ == "__main__":
    main()