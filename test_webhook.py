#!/usr/bin/env python3
"""
Script de test complet pour le nouveau webhook multipart/form-data
"""
import requests
import json
import os

BASE_URL = "http://localhost:8001"
WEBHOOK_URL = f"{BASE_URL}/api/webhook"

def test_webhook_info():
    """Test l'endpoint GET pour les informations"""
    print("🔍 Test de l'endpoint GET /api/webhook...")
    response = requests.get(WEBHOOK_URL)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Message: {data['message']}")
        print(f"✅ Stores disponibles: {', '.join(data['available_stores'])}")
    print()

def test_valid_webhook():
    """Test avec des données valides"""
    print("🔍 Test webhook avec données valides...")
    
    # Préparer les données
    json_data = {
        "title": "Mon Super Produit",
        "description": "Une description complète de mon produit avec tous les détails nécessaires.",
        "url": "https://mon-site.com/produit-123"
    }
    
    # Vérifier que l'image de test existe
    image_path = "/app/backend/test_image.jpg"
    if not os.path.exists(image_path):
        print(f"❌ Image de test non trouvée: {image_path}")
        return
    
    with open(image_path, 'rb') as image_file:
        files = {'image': ('test_image.jpg', image_file, 'image/jpeg')}
        data = {'json_data': json.dumps(json_data)}
        
        response = requests.post(WEBHOOK_URL, files=files, data=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Succès: {result['message']}")
            print(f"✅ Nom de fichier image: {result['data']['image_filename']}")
            print(f"✅ URL image: {result['data']['image_url']}")
            print(f"✅ Taille image: {result['data']['image_size_bytes']} bytes")
            print(f"✅ Données JSON validées: {result['data']['json_data']}")
        else:
            print(f"❌ Erreur: {response.text}")
    print()

def test_with_store():
    """Test avec publication automatique sur un store"""
    print("🔍 Test webhook avec store (publication automatique)...")
    
    json_data = {
        "title": "Produit Test Store",
        "description": "Test de publication automatique sur les réseaux sociaux du store.",
        "url": "https://logicampoutdoor.com/produit-test",
        "store": "outdoor"
    }
    
    image_path = "/app/backend/test_image.jpg"
    with open(image_path, 'rb') as image_file:
        files = {'image': ('test_image.jpg', image_file, 'image/jpeg')}
        data = {'json_data': json.dumps(json_data)}
        
        response = requests.post(WEBHOOK_URL, files=files, data=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Succès: {result['message']}")
            print(f"✅ Store: {result['data']['json_data']['store']}")
            
            if 'publication_results' in result['data']:
                pub_results = result['data']['publication_results']
                for pub_result in pub_results:
                    print(f"✅ Publication: {pub_result['status']} - {pub_result['message']}")
        else:
            print(f"❌ Erreur: {response.text}")
    print()

def test_invalid_json():
    """Test avec JSON invalide"""
    print("🔍 Test webhook avec JSON invalide (validation)...")
    
    # JSON invalide: titre vide et URL sans protocole
    json_data = {
        "title": "",  # Vide
        "description": "Description",
        "url": "www.exemple.com"  # Sans http://
    }
    
    image_path = "/app/backend/test_image.jpg"
    with open(image_path, 'rb') as image_file:
        files = {'image': ('test_image.jpg', image_file, 'image/jpeg')}
        data = {'json_data': json.dumps(json_data)}
        
        response = requests.post(WEBHOOK_URL, files=files, data=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 400:
            error = response.json()
            print(f"✅ Validation échouée comme prévu: {error['detail']}")
        else:
            print(f"❌ Erreur inattendue: {response.text}")
    print()

def test_invalid_image():
    """Test avec type d'image invalide"""
    print("🔍 Test webhook avec type d'image invalide...")
    
    json_data = {
        "title": "Test",
        "description": "Description",
        "url": "https://example.com/test"
    }
    
    # Créer un fichier texte temporaire
    temp_file = "/tmp/test.txt"
    with open(temp_file, "w") as f:
        f.write("Ce n'est pas une image")
    
    with open(temp_file, 'rb') as text_file:
        files = {'image': ('test.txt', text_file, 'text/plain')}
        data = {'json_data': json.dumps(json_data)}
        
        response = requests.post(WEBHOOK_URL, files=files, data=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 400:
            error = response.json()
            print(f"✅ Type d'image rejeté comme prévu: {error['detail']}")
        else:
            print(f"❌ Erreur inattendue: {response.text}")
    
    # Nettoyer
    os.remove(temp_file)
    print()

if __name__ == "__main__":
    print("🚀 Test complet du webhook multipart/form-data")
    print("=" * 50)
    
    try:
        test_webhook_info()
        test_valid_webhook()
        test_with_store()
        test_invalid_json()
        test_invalid_image()
        
        print("✅ Tous les tests terminés!")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")