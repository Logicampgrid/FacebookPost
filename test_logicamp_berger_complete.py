#!/usr/bin/env python3
"""
Test complet du webhook gizmobbs → @logicamp_berger
"""

import requests
import json
import base64
import os
from datetime import datetime

API_BASE = "https://insta-uploader.preview.emergentagent.com"
# API_BASE = "http://localhost:8001"  # Pour tests locaux

def test_1_configuration_logicamp_berger():
    """Test 1: Vérifier que la configuration @logicamp_berger est correcte"""
    print("🧪 TEST 1: Configuration @logicamp_berger")
    print("=" * 60)
    
    try:
        response = requests.post(f"{API_BASE}/api/debug/test-logicamp-berger-webhook")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("✅ SUCCÈS: Configuration @logicamp_berger fonctionnelle!")
                print(f"📱 Instagram trouvé: @{data['instagram_account']['username']}")
                print(f"🏢 Business Manager: {data['business_manager']['name']} ({data['business_manager']['id']})")
                return True
            else:
                error = data.get('error', 'Erreur inconnue')
                print(f"⚠️ Configuration incomplète: {error}")
                
                if "authentifié" in error:
                    print("\n🔧 SOLUTION:")
                    print("1. Allez sur https://insta-uploader.preview.emergentagent.com")
                    print("2. Connectez-vous avec le compte ayant accès au Business Manager 1715327795564432")
                    print("3. Relancez ce test")
                    
                return False
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"💥 Erreur: {e}")
        return False

def test_2_webhook_json_gizmobbs():
    """Test 2: Webhook JSON avec shop_type gizmobbs"""
    print("\n🧪 TEST 2: Webhook JSON gizmobbs → @logicamp_berger")
    print("=" * 60)
    
    test_data = {
        "title": f"Test Webhook Gizmobbs {datetime.now().strftime('%H:%M')}",
        "description": "Test automatique de publication sur @logicamp_berger via webhook JSON avec shop_type gizmobbs. Ce test vérifie que la nouvelle configuration fonctionne correctement.",
        "image_url": f"https://picsum.photos/1080/1080?gizmobbs_test={int(datetime.now().timestamp())}",
        "product_url": "https://gizmobbs.com/test-logicamp-berger-webhook",
        "shop_type": "gizmobbs"
    }
    
    try:
        print(f"📤 Envoi webhook JSON...")
        print(f"   shop_type: {test_data['shop_type']}")
        print(f"   title: {test_data['title']}")
        
        response = requests.post(
            f"{API_BASE}/api/publishProduct",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('status') == 'success':
                print("✅ SUCCÈS: Publication webhook JSON réussie!")
                print(f"📱 Publié sur: {result.get('page_name')}")
                print(f"🆔 Post Instagram ID: {result.get('instagram_post_id')}")
                print(f"🏢 Business Manager: {result.get('business_manager_id')}")
                
                # Vérifier que c'est bien Instagram
                platforms = result.get('platforms_published', {})
                if platforms.get('instagram') and not platforms.get('facebook'):
                    print("✅ EXCELLENT: Publication Instagram uniquement (comme souhaité)")
                    return True
                else:
                    print("⚠️ Attention: Publication non conforme aux attentes")
                    print(f"   Instagram: {platforms.get('instagram')}")
                    print(f"   Facebook: {platforms.get('facebook')}")
                    return False
            else:
                print(f"❌ Échec publication: {result}")
                return False
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"💥 Erreur: {e}")
        return False

def test_3_webhook_multipart_gizmobbs():
    """Test 3: Webhook multipart avec shop_type gizmobbs"""
    print("\n🧪 TEST 3: Webhook Multipart gizmobbs → @logicamp_berger")
    print("=" * 60)
    
    # Créer une image de test simple
    test_image_content = create_test_image()
    
    json_data = {
        "title": f"Test Multipart Gizmobbs {datetime.now().strftime('%H:%M')}",
        "description": "Test automatique multipart/form-data sur @logicamp_berger via shop_type gizmobbs. Validation du nouveau système de publication Instagram priority.",
        "url": "https://gizmobbs.com/test-multipart-logicamp-berger",
        "store": "gizmobbs"
    }
    
    try:
        print(f"📤 Envoi webhook multipart...")
        print(f"   store: {json_data['store']}")
        print(f"   title: {json_data['title']}")
        
        files = {
            'image': ('test_gizmobbs.jpg', test_image_content, 'image/jpeg'),
            'json_data': (None, json.dumps(json_data), 'application/json')
        }
        
        response = requests.post(f"{API_BASE}/api/webhook", files=files)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("✅ SUCCÈS: Webhook multipart réussi!")
                
                pub_results = result.get('data', {}).get('publication_results', [])
                for pub in pub_results:
                    if pub.get('status') == 'success':
                        print(f"📱 Publié sur: {pub.get('details', {}).get('page_name')}")
                        print(f"🆔 Instagram ID: {pub.get('details', {}).get('instagram_post_id')}")
                        
                        # Vérifier que c'est bien @logicamp_berger
                        if '@logicamp_berger' in pub.get('details', {}).get('page_name', ''):
                            print("✅ PARFAIT: Publication sur @logicamp_berger confirmée!")
                            return True
                
                print("⚠️ Publication réussie mais pas sur @logicamp_berger")
                return False
            else:
                print(f"❌ Échec webhook: {result}")
                return False
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"💥 Erreur: {e}")
        return False

def create_test_image():
    """Créer une image de test simple en base64"""
    # Image 1x1 pixel en JPEG (minimal pour test)
    return base64.b64decode(
        "/9j/4AAQSkZJRgABAQEAYABgAAD//gA7Q1JFQVRPUjogZ2QtanBlZyB2MS4wICh1c2luZyBJSkcgSlBFRyB2NjIpLCBxdWFsaXR5ID0gOTAK/9sAQwADAgIDAgIDAwMDBAMDBAUIBQUEBAUKBwcGCAwKDAwLCgsLDQ4SEA0OEQ4LCxAWEBETFBUVFQwPFxgWFBgSFBUU/9sAQwEDBAQFBAUJBQUJFA0LDRQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQU/8AAEQgAAQABAwEiAAIRAQMRAf/EAB8AAAEFAQEBAQEBAAAAAAAAAAABAgMEBQYHCAkKC//EALUQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+v/EAB8BAAMBAQEBAQEBAQEAAAAAAAABAgMEBQYHCAkKC//EALURAAIBAgQEAwQHBQQEAAECdwABAgMRBAUhMQYSQVEHYXETIjKBkQhCobHB0fAjM1LhFe/xQm6A4qKSs8PgJuHg7n7/2gAMAwEAAhEDEQA/AMqiiig//9k="
    )

def check_health():
    """Vérifier l'état général du système"""
    print("\n🏥 VÉRIFICATION SANTÉ DU SYSTÈME")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE}/api/health")
        
        if response.status_code == 200:
            health = response.json()
            
            print(f"🟢 Backend: {health.get('status')}")
            print(f"🔗 MongoDB: {health.get('mongodb')}")
            print(f"👥 Utilisateurs: {health.get('database', {}).get('users_count', 0)}")
            print(f"📄 Posts: {health.get('database', {}).get('posts_count', 0)}")
            
            instagram_diag = health.get('instagram_diagnosis', {})
            print(f"📱 Instagram: {instagram_diag.get('message', 'Non configuré')}")
            
            if health.get('database', {}).get('users_count', 0) > 0:
                print("✅ Système prêt pour tests")
                return True
            else:
                print("⚠️ Authentification requise")
                return False
        else:
            print(f"❌ Erreur santé: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Erreur: {e}")
        return False

def run_comprehensive_test():
    """Lancer la suite complète de tests"""
    print("🎯 TESTS COMPLETS WEBHOOK @logicamp_berger")
    print("=" * 80)
    print(f"⏰ Démarré à: {datetime.now().strftime('%H:%M:%S')}")
    print(f"🌐 API Base: {API_BASE}")
    
    tests = [
        ("Santé Système", check_health),
        ("Configuration @logicamp_berger", test_1_configuration_logicamp_berger),
        ("Webhook JSON gizmobbs", test_2_webhook_json_gizmobbs),
        ("Webhook Multipart gizmobbs", test_3_webhook_multipart_gizmobbs)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        print("-" * 50)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: RÉUSSI")
            else:
                print(f"❌ {test_name}: ÉCHEC")
                
        except Exception as e:
            print(f"💥 {test_name}: ERREUR - {e}")
            results.append((test_name, False))
    
    # Résumé final
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 80)
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{status:12} {test_name}")
    
    print(f"\n📈 Résultat global: {success_count}/{total_count} tests réussis")
    
    if success_count == total_count:
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("🚀 Webhook gizmobbs → @logicamp_berger est OPÉRATIONNEL!")
    elif success_count >= 2:
        print("\n⚠️ Configuration partielle - Authentification requise")
        print("🔧 Connectez-vous via l'interface web pour finaliser")
    else:
        print("\n❌ Problèmes de configuration détectés")
        print("🆘 Vérifiez les logs et la documentation")

if __name__ == "__main__":
    run_comprehensive_test()