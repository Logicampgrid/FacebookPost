#!/usr/bin/env python3
"""
Script de test pour l'API de publication Facebook/Instagram
Utilise les nouvelles fonctionnalités implémentées dans server.py
"""

import requests
import json
import time
from typing import List, Dict, Any

# Configuration
BASE_URL = "http://localhost:8001/api"

def print_result(title: str, result: Dict[Any, Any]):
    """Affiche le résultat d'une requête de manière formatée"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print('='*60)
    print(json.dumps(result, indent=2, ensure_ascii=False))

def test_health():
    """Test du health check"""
    print("🔍 Test du health check...")
    response = requests.get(f"{BASE_URL}/health")
    print_result("Health Check", response.json())
    return response.status_code == 200

def test_stores():
    """Test de la liste des stores"""
    print("🏪 Test de la liste des stores...")
    response = requests.get(f"{BASE_URL}/stores")
    print_result("Liste des Stores", response.json())
    return response.status_code == 200

def test_publication(store: str, message: str, product_url: str, image_url: str = None, platforms: List[str] = None):
    """Test d'une publication"""
    if platforms is None:
        platforms = ["facebook", "instagram"]
    
    payload = {
        "store": store,
        "message": message,
        "product_url": product_url,
        "platforms": platforms
    }
    if image_url:
        payload["image_url"] = image_url
    
    print(f"📢 Test publication pour {store} sur {platforms}...")
    response = requests.post(f"{BASE_URL}/publish", json=payload)
    print_result(f"Publication {store}", response.json())
    return response.status_code == 200

def test_publications_history():
    """Test de l'historique des publications"""
    print("📜 Test de l'historique des publications...")
    response = requests.get(f"{BASE_URL}/publications")
    print_result("Historique Publications", response.json())
    return response.status_code == 200

def test_store_config(store: str):
    """Test de la configuration d'un store"""
    print(f"⚙️ Test configuration pour {store}...")
    response = requests.post(f"{BASE_URL}/test-config?store={store}")
    print_result(f"Configuration {store}", response.json())
    return response.status_code == 200

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests de l'API Publication Facebook/Instagram")
    print("Mode TEST activé - Aucune vraie publication ne sera effectuée\n")
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Health check
    total_tests += 1
    if test_health():
        success_count += 1
    
    time.sleep(1)
    
    # Test 2: Liste des stores
    total_tests += 1
    if test_stores():
        success_count += 1
    
    time.sleep(1)
    
    # Test 3: Publication complète avec image
    total_tests += 1
    if test_publication(
        store="logicantiq",
        message="🏺 Magnifique vase ancien du 18ème siècle ! Pièce unique authentique.",
        product_url="https://logicantiq.com/produit/vase-ancien-18eme",
        image_url="https://logicantiq.com/wp-content/uploads/vase-18eme.jpg"
    ):
        success_count += 1
    
    time.sleep(1)
    
    # Test 4: Publication Facebook seulement
    total_tests += 1
    if test_publication(
        store="logicampoutdoor",
        message="🏕️ Nouveau matériel de camping ! Parfait pour vos aventures outdoor.",
        product_url="https://logicampoutdoor.com/produit/tente-4-saisons",
        platforms=["facebook"]
    ):
        success_count += 1
    
    time.sleep(1)
    
    # Test 5: Publication avec extraction d'image automatique (va échouer sur example.com)
    total_tests += 1
    if test_publication(
        store="bergerblancsuisse",
        message="🐕 Adorable chiot Berger Blanc Suisse disponible !",
        product_url="https://example.com/chiot"  # URL factice pour tester l'extraction
    ):
        success_count += 1
    
    time.sleep(1)
    
    # Test 6: Publication Instagram seulement
    total_tests += 1
    if test_publication(
        store="gizmobbs",
        message="🎮 Nouveau gadget gaming ! Level up ton setup.",
        product_url="https://gizmobbs.com/produit/clavier-gaming",
        image_url="https://gizmobbs.com/images/clavier-rgb.jpg",
        platforms=["instagram"]
    ):
        success_count += 1
    
    time.sleep(1)
    
    # Test 7: Historique des publications
    total_tests += 1
    if test_publications_history():
        success_count += 1
    
    time.sleep(1)
    
    # Test 8: Configuration d'un store (va échouer avec de faux tokens)
    total_tests += 1
    if test_store_config("logicantiq"):
        success_count += 1
    
    # Résumé
    print(f"\n{'='*60}")
    print(f"📊 RÉSUMÉ DES TESTS")
    print('='*60)
    print(f"✅ Tests réussis: {success_count}/{total_tests}")
    print(f"📝 Mode: TEST (aucune vraie publication)")
    print(f"🔧 Backend: {BASE_URL}")
    
    if success_count == total_tests:
        print("🎉 Tous les tests sont passés ! L'API est fonctionnelle.")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")
    
    print("\n💡 Pour passer en mode PRODUCTION:")
    print("   1. Remplacez les tokens placeholders par les vrais tokens")
    print("   2. Définissez PUBLICATION_TEST_MODE=false dans .env")
    print("   3. Redémarrez le backend")

if __name__ == "__main__":
    main()