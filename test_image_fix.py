#!/usr/bin/env python3
"""
Test pour vérifier que les images s'affichent correctement dans les posts Facebook
"""

import requests
import json
import os
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8001"
PUBLIC_BASE_URL = "https://file-webhook-api.preview.emergentagent.com"

def test_image_display_fix():
    """Test the image display fix"""
    print("🧪 Test de correction d'affichage d'images Facebook")
    print("=" * 60)
    
    # Test data - votre exemple de harnais pour chien
    test_data = {
        "title": "Harnais réfléchissant pour chien - Toutes saisons",
        "description": """Lifestage: Chiot
Chimique High-concerné: Aucun
Type de harnais de chien: Harnais de base
Est dispositif intelligent: no
Personnalisé: Pas de
Caractéristique: Réfléchissant
Saison: Toutes les saisons
Matériau: Nylon
Motif: Rayé
Type: Harnais
Origine: CN (Origine)
CN: Guangdong
Type: Chiens

Features:
1. Reflective stitching maintains high visibility at night for safety
2. Soft Mesh Cat Vest Harness and Nylon Leash Set for Walking Escape Proof No Pull & No Choke Design
3. The harness will make your kitty safe and comfortable
4. The size fits most pets, cat, small, medium breed dog
5. Material: mesh fabric, reflective strip, plastic closure and O-ring
6. Color: yellow, green, pink

Size:
XS Pet Chest 28 cm--32 cm, Neck 25 cm--30 cm, fit for 1.5-2.5 kg pet
S Pet Chest 36 cm--40 cm, Neck 30 cm--35 cm, fit for 2.5-4 kg pet
M Pet Chest 46 cm--50 cm, Neck 40 cm--45 cm, fit for 4-6 kg pet
L Pet Chest 48 cm--54 cm, Neck 44 cm--48 cm, fit for 8-11 kg pet""",
        "image_url": "https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=800&h=800&fit=crop&crop=center",
        "product_url": "https://logicamp.org/product/harnais-reflechissant-chien",
        "shop_type": "outdoor"
    }
    
    print(f"📋 Données de test:")
    print(f"   Titre: {test_data['title']}")
    print(f"   Image: {test_data['image_url']}")
    print(f"   Lien produit: {test_data['product_url']}")
    print(f"   Shop type: {test_data['shop_type']}")
    print()
    
    # Étape 1: Vérifier que l'API backend fonctionne
    print("🔍 Étape 1: Vérification de l'API backend...")
    try:
        health_response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Backend accessible")
        else:
            print(f"❌ Backend inaccessible: {health_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion backend: {e}")
        return False
    
    # Étape 2: Tester l'endpoint de publication de produit
    print("\n📤 Étape 2: Test de publication de produit...")
    try:
        response = requests.post(
            f"{API_BASE}/api/publishProduct",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📡 Réponse HTTP: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Publication réussie!")
            print(f"   Facebook Post ID: {result.get('data', {}).get('facebook_post_id', 'N/A')}")
            print(f"   Page: {result.get('data', {}).get('page_name', 'N/A')}")
            print(f"   Media URL: {result.get('data', {}).get('media_url', 'N/A')}")
            print(f"   Message: {result.get('message', 'N/A')}")
            
            # Afficher l'URL publique de l'image si disponible
            media_url = result.get('data', {}).get('media_url', '')
            if media_url and not media_url.startswith('http'):
                public_image_url = f"{PUBLIC_BASE_URL}{media_url}"
                print(f"   Image publique: {public_image_url}")
            
            return True
            
        else:
            error_data = response.json() if response.content else {}
            print(f"❌ Échec de publication: {response.status_code}")
            print(f"   Erreur: {error_data}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def test_direct_image_access():
    """Test direct access to uploaded images"""
    print("\n🖼️  Étape 3: Test d'accès direct aux images...")
    
    # Vérifier si nous avons des images dans uploads/
    uploads_dir = "/app/uploads"
    if os.path.exists(uploads_dir):
        image_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if image_files:
            test_image = image_files[0]
            public_url = f"{PUBLIC_BASE_URL}/api/uploads/{test_image}"
            
            print(f"📸 Test d'image: {test_image}")
            print(f"🌐 URL publique: {public_url}")
            
            try:
                img_response = requests.get(public_url, timeout=10)
                if img_response.status_code == 200:
                    print("✅ Image accessible publiquement")
                    print(f"   Taille: {len(img_response.content)} bytes")
                    print(f"   Type: {img_response.headers.get('content-type', 'unknown')}")
                    return True
                else:
                    print(f"❌ Image non accessible: {img_response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ Erreur d'accès à l'image: {e}")
                return False
        else:
            print("⚠️ Aucune image trouvée dans uploads/")
            return False
    else:
        print("⚠️ Directory uploads/ non trouvé")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test de correction d'affichage d'images Facebook")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test de publication
    publication_success = test_image_display_fix()
    
    # Test d'accès direct aux images
    image_access_success = test_direct_image_access()
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"✅ Publication de produit: {'SUCCÈS' if publication_success else 'ÉCHEC'}")
    print(f"✅ Accès images publiques: {'SUCCÈS' if image_access_success else 'ÉCHEC'}")
    
    if publication_success and image_access_success:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("\n💡 AMÉLIORATIONS APPLIQUÉES:")
        print("   1. Upload direct d'images vers Facebook (plus fiable)")
        print("   2. Intégration du lien produit dans le message")
        print("   3. Fallback amélioré avec paramètre 'picture'")
        print("   4. Gestion d'erreurs renforcée")
        print("\n📋 STRATÉGIES FACEBOOK UTILISÉES:")
        print("   - Direct multipart upload (PRIORITÉ)")
        print("   - Enhanced link posting avec picture URL")
        print("   - Text fallback avec liens intégrés")
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("Vérifiez les logs backend pour plus de détails")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()