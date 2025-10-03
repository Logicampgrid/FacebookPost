#!/usr/bin/env python3
"""
Script de test pour valider la correction PATCH 19 - Webhook n8n
"""

import json
import requests
from datetime import datetime
import os

def test_webhook_n8n():
    """Teste le webhook n8n avec des données multipart"""
    
    print("🧪 Test PATCH 19 - Correction webhook n8n")
    print("=" * 50)
    
    # URL du webhook (utiliser ngrok ou localhost selon configuration)
    webhook_url = "http://localhost:8001/api/webhook"
    
    # Données de test pour publication
    test_data = {
        "store": "logicantiq",
        "title": "Test PATCH 19 - Produit correctionœ",
        "description": "Test de la correction du webhook n8n avec multipart",
        "url": "https://example.com/product-test-patch19"
    }
    
    print(f"📦 Données de test: {test_data}")
    
    # Test 1: Format n8n avec jsonData
    print("\n🧪 Test 1: Format n8n avec jsonData")
    print("-" * 30)
    
    try:
        # Simuler le format n8n avec jsonData
        form_data = {
            'jsonData': json.dumps(test_data)
        }
        
        response = requests.post(webhook_url, data=form_data, timeout=30)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Test 1 réussi")
        else:
            print("❌ Test 1 échoué")
            
    except Exception as e:
        print(f"❌ Erreur Test 1: {e}")
    
    # Test 2: Format direct multipart
    print("\n🧪 Test 2: Format direct multipart")
    print("-" * 30)
    
    try:
        response = requests.post(webhook_url, data=test_data, timeout=30)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Test 2 réussi")
        else:
            print("❌ Test 2 échoué")
            
    except Exception as e:
        print(f"❌ Erreur Test 2: {e}")
    
    # Test 3: Avec fichier image simulé (si un fichier test existe)
    print("\n🧪 Test 3: Avec fichier image (si disponible)")
    print("-" * 30)
    
    # Chercher un fichier image de test dans uploads
    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    test_image = None
    
    if os.path.exists(uploads_dir):
        for filename in os.listdir(uploads_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_image = os.path.join(uploads_dir, filename)
                break
    
    if test_image and os.path.exists(test_image):
        try:
            print(f"📁 Fichier test trouvé: {os.path.basename(test_image)}")
            
            form_data = {
                'jsonData': json.dumps(test_data)
            }
            
            with open(test_image, 'rb') as f:
                files = {'file': f}
                response = requests.post(webhook_url, data=form_data, files=files, timeout=30)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200:
                print("✅ Test 3 réussi")
            else:
                print("❌ Test 3 échoué")
                
        except Exception as e:
            print(f"❌ Erreur Test 3: {e}")
    else:
        print("⚠️ Pas de fichier image de test disponible")
    
    print(f"\n🎯 Tests terminés - {datetime.now().strftime('%H:%M:%S')}")
    print("💡 Vérifiez les logs du serveur pour les messages PATCH 19")

def show_correction_summary():
    """Affiche le résumé de la correction PATCH 19"""
    
    print("🔧 PATCH 19 - CORRECTION WEBHOOK N8N")
    print("=" * 50)
    print()
    
    print("✅ PROBLÈME CORRIGÉ:")
    print("   Erreur 'Stream consumed' lors du traitement des webhooks n8n")
    print("   Les produits et vidéos n'étaient pas traités correctement")
    print()
    
    print("🛠️ SOLUTION IMPLÉMENTÉE:")
    print("   • Fonction handle_n8n_publication_corrected() créée")
    print("   • Évite la consommation multiple du stream FastAPI")
    print("   • Détection intelligente des requêtes n8n vs Facebook")
    print("   • Traitement robuste des fichiers médias")
    print()
    
    print("🎯 RÉSULTAT ATTENDU:")
    print("   • Plus d'erreur 'Stream consumed'")
    print("   • Publications n8n fonctionnelles")  
    print("   • Support images et vidéos")
    print("   • Logs détaillés avec 'PATCH 19'")

if __name__ == "__main__":
    show_correction_summary()
    print("\n" + "="*50)
    print("💡 Pour tester les webhooks n8n:")
    print("   1. Redémarrez le serveur pour charger la correction PATCH 19")
    print("   2. Envoyez des requêtes multipart à /api/webhook")  
    print("   3. Vérifiez que les logs n'affichent plus 'Stream consumed'")
    print("   4. Confirmez que les publications n8n fonctionnent")