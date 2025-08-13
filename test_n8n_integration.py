#!/usr/bin/env python3
"""
Script de test pour l'intégration N8N - FacebookPost
Simule l'envoi de données de produits depuis N8N
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://just-ok-3.preview.emergentagent.com"
CONFIG_ENDPOINT = f"{BASE_URL}/api/publishProduct/config"
TEST_ENDPOINT = f"{BASE_URL}/api/publishProduct/test"
PROD_ENDPOINT = f"{BASE_URL}/api/publishProduct"

# Exemples de produits à tester
TEST_PRODUCTS = [
    {
        "title": "Chaise Scandinave Premium",
        "description": "Chaise au design scandinave moderne avec pieds en bois massif et assise rembourrée pour un confort optimal. Parfaite pour votre salle à manger ou bureau.",
        "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "product_url": "https://monsite.com/chaise-scandinave-premium"
    },
    {
        "title": "Table Basse Design Industriel", 
        "description": "Table basse au style industriel alliant métal noir et plateau en bois recyclé. Idéale pour apporter une touche moderne à votre salon.",
        "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "product_url": "https://monsite.com/table-basse-industrielle"
    },
    {
        "title": "Étagère Murale Minimaliste",
        "description": "Étagère murale au design épuré, parfaite pour organiser vos livres et objets déco. Installation facile et style intemporel.",
        "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "product_url": "https://monsite.com/etagere-murale-minimaliste"
    }
]

def print_header(title):
    """Affiche un en-tête formaté"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_success(message):
    """Affiche un message de succès"""
    print(f"✅ {message}")

def print_error(message):
    """Affiche un message d'erreur"""
    print(f"❌ {message}")

def print_info(message):
    """Affiche un message d'information"""
    print(f"ℹ️  {message}")

def test_configuration():
    """Teste l'endpoint de configuration"""
    print_header("TEST DE CONFIGURATION")
    
    try:
        response = requests.get(CONFIG_ENDPOINT, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Configuration récupérée avec succès")
            print_info(f"Utilisateurs trouvés: {len(data['users'])}")
            print_info(f"Pages Facebook disponibles: {data['total_pages']}")
            
            # Afficher les pages disponibles
            for user in data['users']:
                print(f"\n👤 Utilisateur: {user['name']}")
                for page in user['pages'][:3]:  # Afficher seulement les 3 premières
                    print(f"   📄 {page['name']} ({page['id']}) - {page['type']}")
            
            return True
        else:
            print_error(f"Erreur configuration: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Erreur lors du test de configuration: {e}")
        return False

def test_product_publishing(product, test_mode=True):
    """Teste la publication d'un produit"""
    endpoint = TEST_ENDPOINT if test_mode else PROD_ENDPOINT
    mode = "TEST" if test_mode else "PRODUCTION"
    
    print(f"\n📦 Test {mode}: {product['title']}")
    
    try:
        response = requests.post(
            endpoint,
            headers={"Content-Type": "application/json"},
            json=product,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Publication {mode} réussie!")
            
            if test_mode:
                print_info(f"Mode: {data.get('test_mode', 'Unknown')}")
                print_info(f"Post simulé: {data['data']['facebook_post_id']}")
            else:
                print_info(f"Post Facebook: {data['data']['facebook_post_id']}")
            
            print_info(f"Page: {data['data']['page_name']}")
            print_info(f"Image: {data['data'].get('media_url', 'N/A')}")
            
            return True
            
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print_error(f"Erreur {mode}: {response.status_code}")
            print_error(f"Détails: {error_data}")
            return False
            
    except Exception as e:
        print_error(f"Erreur lors du test {mode}: {e}")
        return False

def test_validation_errors():
    """Teste la validation des erreurs"""
    print_header("TEST DE VALIDATION DES ERREURS")
    
    # Test avec données manquantes
    invalid_products = [
        {
            "title": "",  # Titre vide
            "description": "Description valide",
            "image_url": "https://example.com/image.jpg",
            "product_url": "https://example.com/product"
        },
        {
            "title": "Titre valide",
            "description": "Description valide", 
            "image_url": "invalid-url",  # URL invalide
            "product_url": "https://example.com/product"
        },
        {
            "title": "Titre valide",
            "description": "Description valide",
            "image_url": "https://example.com/image.jpg",
            "product_url": "invalid-url"  # URL invalide
        }
    ]
    
    for i, invalid_product in enumerate(invalid_products, 1):
        print(f"\n🔍 Test validation #{i}")
        
        try:
            response = requests.post(
                TEST_ENDPOINT,
                headers={"Content-Type": "application/json"},
                json=invalid_product,
                timeout=10
            )
            
            if response.status_code == 400:
                print_success("Validation d'erreur fonctionne correctement")
                error_detail = response.json().get('detail', 'Erreur inconnue')
                print_info(f"Message d'erreur: {error_detail}")
            else:
                print_error(f"Validation inattendue: {response.status_code}")
                
        except Exception as e:
            print_error(f"Erreur lors du test de validation: {e}")

def main():
    """Fonction principale"""
    print_header("TESTS D'INTÉGRATION N8N - FACEBOOKPOST")
    print_info(f"Date du test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"URL de base: {BASE_URL}")
    
    # 1. Test de configuration
    config_success = test_configuration()
    
    if not config_success:
        print_error("Tests interrompus - problème de configuration")
        return
    
    # 2. Test de validation des erreurs
    test_validation_errors()
    
    # 3. Tests de publication en mode test
    print_header("TESTS DE PUBLICATION EN MODE TEST")
    
    success_count = 0
    for i, product in enumerate(TEST_PRODUCTS, 1):
        print(f"\n--- Test Produit #{i} ---")
        if test_product_publishing(product, test_mode=True):
            success_count += 1
        
        # Pause entre les tests
        if i < len(TEST_PRODUCTS):
            time.sleep(2)
    
    # 4. Résumé
    print_header("RÉSUMÉ DES TESTS")
    print_info(f"Tests de configuration: {'✅ Réussi' if config_success else '❌ Échoué'}")
    print_info(f"Tests de produits: {success_count}/{len(TEST_PRODUCTS)} réussis")
    
    if success_count == len(TEST_PRODUCTS):
        print_success("🎉 Tous les tests sont passés avec succès!")
        print_info("L'intégration N8N est prête à être utilisée.")
    else:
        print_error("⚠️ Certains tests ont échoué.")
        print_info("Vérifiez les logs pour plus de détails.")
    
    print_header("INSTRUCTIONS POUR N8N")
    print("""
🔧 Configuration N8N:
1. Créez un nœud HTTP Request
2. Method: POST
3. URL: https://just-ok-3.preview.emergentagent.com/api/publishProduct
4. Headers: Content-Type: application/json
5. Body: Votre JSON de produit

📝 Exemple de Body N8N:
{
  "title": "{{$json.product_title}}",
  "description": "{{$json.product_description}}", 
  "image_url": "{{$json.product_image}}",
  "product_url": "{{$json.product_link}}"
}

🎯 Pour utiliser en production:
- Utilisez /api/publishProduct (au lieu de /test)
- Assurez-vous que les tokens Facebook sont valides
- Configurez la gestion d'erreurs dans N8N
    """)

if __name__ == "__main__":
    main()