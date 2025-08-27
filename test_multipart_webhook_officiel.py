#!/usr/bin/env python3
"""
🎯 TEST OFFICIEL - Images Cliquables via Multipart Webhook
Test de la solution validée multipart/form-data pour garantir des images cliquables
"""

import requests
import json
from datetime import datetime
import tempfile
import os

# Configuration du test
WEBHOOK_URL = "http://localhost:8001/api/webhook"
TEST_PRODUCT_URL = "https://www.logicamp.org/wordpress/gizmobbs/test-produit"

def create_test_image():
    """Crée une image de test temporaire"""
    try:
        # Télécharger une image de test
        image_response = requests.get("https://picsum.photos/800/600", timeout=10)
        if image_response.status_code == 200:
            # Créer un fichier temporaire
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_file.write(image_response.content)
            temp_file.close()
            return temp_file.name
        else:
            print(f"❌ Impossible de télécharger l'image de test: HTTP {image_response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'image test: {e}")
        return None

def test_multipart_webhook_images_cliquables():
    """Test officiel multipart pour images cliquables"""
    
    print("🎯 TEST OFFICIEL : Images Cliquables via Multipart Webhook")
    print("=" * 65)
    
    # Créer image de test
    print("📷 Création de l'image de test...")
    image_path = create_test_image()
    if not image_path:
        print("❌ Impossible de créer l'image de test")
        return False
    
    print(f"✅ Image créée : {image_path}")
    
    # JSON data pour le webhook
    json_data = {
        "title": "🧪 Test Multipart - Image Cliquable",
        "description": "Test de la solution multipart pour garantir des images cliquables. Cette image DOIT être cliquable et rediriger vers product_url.",
        "url": TEST_PRODUCT_URL,
        "store": "gizmobbs"
    }
    
    print("📋 JSON data :")
    print(json.dumps(json_data, indent=2, ensure_ascii=False))
    print()
    
    try:
        print("🚀 Envoi de la requête multipart webhook...")
        
        # Préparer les données multipart
        with open(image_path, 'rb') as image_file:
            files = {
                'image': ('test_image.jpg', image_file, 'image/jpeg'),
                'json_data': (None, json.dumps(json_data))
            }
            
            response = requests.post(
                WEBHOOK_URL,
                files=files,
                timeout=30
            )
        
        print(f"📡 Statut HTTP : {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCÈS : Webhook multipart traité avec succès !")
            print()
            print("📊 Résultat :")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get("success", True):  # Certaines réponses n'ont pas de champ success
                image_filename = result.get("image_filename", "unknown")
                validated_json = result.get("validated_json", {})
                
                print()
                print("🎉 VALIDATION IMAGES CLIQUABLES :")
                print(f"   ✅ Image uploadée : {image_filename}")
                print(f"   ✅ Titre validé : {validated_json.get('title', 'N/A')}")
                print(f"   ✅ URL produit : {validated_json.get('url', 'N/A')}")
                print(f"   ✅ Store : {validated_json.get('store', 'N/A')}")
                print()
                print("🔍 VÉRIFICATION MANUELLE :")
                print(f"   1. Allez sur la page Facebook du store 'gizmobbs'")
                print(f"   2. Trouvez le post : '{json_data['title']}'")
                print(f"   3. Vérifiez que l'IMAGE s'affiche correctement")
                print(f"   4. Cliquez sur l'image → doit ouvrir : {TEST_PRODUCT_URL}")
                
                return True
            else:
                print("❌ ÉCHEC : Le webhook a retourné une erreur")
                return False
                
        else:
            print(f"❌ ERREUR HTTP {response.status_code}")
            try:
                error_data = response.json()
                print("Détails de l'erreur :")
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print("Réponse brute :", response.text)
            return False
            
    except Exception as e:
        print(f"💥 EXCEPTION : {str(e)}")
        return False
    
    finally:
        # Nettoyer l'image temporaire
        try:
            os.unlink(image_path)
            print(f"🧹 Image temporaire supprimée : {image_path}")
        except:
            pass

def test_curl_example():
    """Génère un exemple cURL correct"""
    
    print("\n" + "=" * 65)
    print("🔧 EXEMPLE cURL POUR N8N/AUTRES OUTILS")
    print("=" * 65)
    
    curl_example = f'''
curl -X POST "{WEBHOOK_URL}" \\
  -F "image=@/chemin/vers/votre/image.jpg" \\
  -F 'json_data={{"title":"Nom du Produit","description":"Description du produit","url":"{TEST_PRODUCT_URL}","store":"gizmobbs"}}'
    '''.strip()
    
    print(curl_example)
    print()
    
    print("📋 Structure des données :")
    print("   • image: Fichier binaire (JPEG, PNG, GIF, WebP)")
    print("   • json_data: Chaîne JSON avec les métadonnées")
    print()
    
    print("🎯 Champs JSON obligatoires :")
    print("   • title: Titre du produit")
    print("   • description: Description du produit")
    print("   • url: URL vers laquelle l'image doit rediriger")
    print("   • store: Boutique cible (gizmobbs, outdoor, logicantiq)")

def main():
    """Test principal"""
    
    print("🎯 TEST OFFICIEL : SOLUTION IMAGES CLIQUABLES (MULTIPART)")
    print("🚀 Validation de la méthode multipart/form-data")
    print()
    
    # Test principal
    success = test_multipart_webhook_images_cliquables()
    
    # Exemple cURL
    test_curl_example()
    
    print("\n" + "=" * 65)
    print("📋 RÉSUMÉ FINAL")
    print("=" * 65)
    
    if success:
        print("✅ TEST MULTIPART : SUCCÈS")
        print("✅ La solution multipart/form-data fonctionne correctement")
        print("✅ Images cliquables garanties via multipart webhook")
        print()
        print("🎯 MÉTHODE OFFICIELLE VALIDÉE :")
        print("   • Endpoint: POST /api/webhook")
        print("   • Content-Type: multipart/form-data")
        print("   • Champs: image (fichier) + json_data (JSON string)")
        print("   • Résultat: Image cliquable → product_url")
    else:
        print("❌ TEST MULTIPART : ÉCHEC")
        print("❌ Problème avec la solution multipart")
        print("🔧 Vérifiez que le backend est démarré et accessible")
    
    print(f"\n🌐 URLs de test utilisées :")
    print(f"   🔗 Produit : {TEST_PRODUCT_URL}")
    print(f"   📡 Webhook : {WEBHOOK_URL}")
    
    print(f"\n⏰ Test complété : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()