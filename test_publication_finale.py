#!/usr/bin/env python3
"""
Test final de publication réelle avec vraie image et contenu neutre
"""

import requests
import json
import os
from PIL import Image
import io

# Configuration
API_BASE = "http://localhost:8001"

def create_real_test_image():
    """Créer une vraie image de test"""
    # Créer une image 500x500 simple
    img = Image.new('RGB', (500, 500), color='lightblue')
    
    # Sauvegarder comme JPG
    test_image_path = "/app/backend/test_image_finale.jpg"
    img.save(test_image_path, "JPEG", quality=85)
    
    return test_image_path

def test_publication_finale():
    """Test final de publication réelle avec contenu sûr"""
    
    print("🧪 TEST PUBLICATION FINALE - Contenu sûr et vraie image")
    print("=" * 60)
    
    # Créer une vraie image de test
    test_image_path = create_real_test_image()
    
    try:
        print(f"🖼️ Image créée: {test_image_path}")
        print(f"📏 Taille: {os.path.getsize(test_image_path)} bytes")
        
        # Préparer la requête multipart avec contenu neutre
        files = {
            'file': ('test_image_finale.jpg', open(test_image_path, 'rb'), 'image/jpeg')
        }
        
        # CONTENU SÛRE POUR ÉVITER LES FILTRES ANTI-SPAM
        data = {
            'store': 'gizmobbs',  # Le Berger Blanc Suisse
            'title': 'Belle journée ensoleillée',
            'url': 'https://example.com',
            'description': 'Quelle magnifique journée ! Le soleil brille et les oiseaux chantent. Parfait pour une promenade en nature.'
        }
        
        print(f"📝 Contenu sûr: {data}")
        
        # Envoyer la requête
        print("\n📡 Envoi publication avec vraie image...")
        response = requests.post(
            f"{API_BASE}/api/webhook",
            files=files,
            data=data,
            timeout=45
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ WEBHOOK TRAITÉ AVEC SUCCÈS")
            
            if result.get("success"):
                print("✅ Publication marquée comme réussie")
                print(f"📝 Store: {result.get('store')}")
                print(f"🎯 Plateformes: {result.get('platforms')}")
                print(f"📁 Type média: {result.get('media')}")
            else:
                print(f"❌ Publication échouée: {result.get('error')}")
                
            print(f"\n📄 Réponse complète:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ ERREUR WEBHOOK: {response.status_code}")
            print(f"📄 Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ ERREUR REQUÊTE: {e}")
    
    finally:
        # Nettoyer le fichier test
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
    
    print("\n" + "=" * 60)
    print("🎉 TEST FINAL TERMINÉ")

if __name__ == "__main__":
    test_publication_finale()