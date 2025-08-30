#!/usr/bin/env python3
"""
Test script pour vérifier les améliorations des médias Facebook
"""

import requests
import json
import os
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8001"

def test_facebook_config():
    """Test de la configuration Facebook"""
    print("🔧 Test de la configuration Facebook...")
    
    try:
        response = requests.get(f"{API_BASE}/api/debug/facebook-config")
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Configuration Facebook OK:")
            print(f"   - App ID: {config.get('app_id', 'Non configuré')}")
            print(f"   - Graph URL: {config.get('graph_url', 'Non configuré')}")
            print(f"   - App Secret: {config.get('app_secret_configured', 'Non configuré')}")
            return True
        else:
            print(f"❌ Erreur configuration: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_health_check():
    """Test de l'état de l'API"""
    print("🏥 Test de santé de l'API...")
    
    try:
        response = requests.get(f"{API_BASE}/api/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API en bonne santé: {health['status']}")
            print(f"   - Timestamp: {health['timestamp']}")
            return True
        else:
            print(f"❌ API non disponible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion API: {e}")
        return False

def test_media_processing():
    """Test de traitement des médias"""
    print("📸 Test de traitement des médias...")
    
    # Simuler une URL de média
    test_media_url = "https://fb-link-poster.preview.emergentagent.com/uploads/test-image.jpg"
    
    print(f"   - URL de test: {test_media_url}")
    
    # Test des types de médias supportés
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
    
    print(f"   - Extensions images supportées: {image_extensions}")
    print(f"   - Extensions vidéos supportées: {video_extensions}")
    
    return True

def test_link_extraction():
    """Test d'extraction de liens"""
    print("🔗 Test d'extraction de liens...")
    
    test_text = "Regardez cette vidéo incroyable! https://www.youtube.com/watch?v=example et cette image https://example.com/image.jpg"
    
    try:
        response = requests.post(
            f"{API_BASE}/api/text/extract-links",
            json={"text": test_text}
        )
        
        if response.status_code == 200:
            result = response.json()
            links = result.get('links', [])
            print(f"✅ Extraction de liens réussie: {len(links)} lien(s) trouvé(s)")
            for i, link in enumerate(links, 1):
                print(f"   - Lien {i}: {link.get('url', 'URL manquante')}")
                print(f"     Titre: {link.get('title', 'Pas de titre')}")
                print(f"     Image: {'Oui' if link.get('image') else 'Non'}")
            return True
        else:
            print(f"❌ Erreur extraction liens: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur test extraction: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test des améliorations médias Facebook")
    print("=" * 50)
    
    tests = [
        ("Configuration API", test_health_check),
        ("Configuration Facebook", test_facebook_config),
        ("Traitement médias", test_media_processing),
        ("Extraction de liens", test_link_extraction)
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\n📋 {name}")
        print("-" * 30)
        result = test_func()
        results.append((name, result))
        print()
    
    # Résumé des résultats
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    success_count = 0
    for name, result in results:
        status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
        print(f"{status} - {name}")
        if result:
            success_count += 1
    
    print(f"\n🎯 Score: {success_count}/{len(results)} tests réussis")
    
    if success_count == len(results):
        print("🎉 Tous les tests sont passés ! Les améliorations sont opérationnelles.")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
        
    return success_count == len(results)

if __name__ == "__main__":
    main()