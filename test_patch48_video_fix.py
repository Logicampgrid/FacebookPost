#!/usr/bin/env python3
"""
Test PATCH 48 - Validation Upload Direct Vidéos Facebook
"""
import requests
import json
import sys

# Configuration
BACKEND_URL = "http://localhost:8001"
TEST_VIDEO_URL = "https://logicamp.org/wordpress/uploads/webhook_3821c617_1759947009.mp4"  # Vidéo des logs

def test_video_publication():
    """Test publication vidéo avec le PATCH 48"""
    print("🧪 Test PATCH 48 - Upload Direct Vidéos Facebook\n")
    
    # Test 1: Vérifier que le serveur est accessible
    print("1️⃣ Test connexion backend...")
    try:
        health = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if health.status_code == 200:
            print("   ✅ Backend accessible\n")
        else:
            print(f"   ❌ Backend erreur: {health.status_code}\n")
            return False
    except Exception as e:
        print(f"   ❌ Impossible de se connecter au backend: {e}\n")
        return False
    
    # Test 2: Simuler une publication vidéo webhook
    print("2️⃣ Test publication vidéo via webhook...")
    print(f"   📹 URL vidéo test: {TEST_VIDEO_URL}")
    
    webhook_data = {
        "store": "logicamp",
        "title": "🧪 Test PATCH 48 - Upload Direct Vidéo",
        "url": "https://logicamp.org/wordpress/test-patch48",
        "description": "Test automatique pour valider l'upload direct des vidéos Facebook"
    }
    
    # Créer un fichier vidéo fictif pour le test (multipart)
    files = {
        'json_data': (None, json.dumps(webhook_data), 'application/json'),
        'video_file': ('test.mp4', b'test_video_content', 'video/mp4')
    }
    
    try:
        print("   📤 Envoi webhook multipart...")
        response = requests.post(
            f"{BACKEND_URL}/api/webhook",
            files=files,
            timeout=120  # Timeout long pour traitement vidéo
        )
        
        print(f"   📊 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Webhook accepté: {result.get('status', 'N/A')}")
            print(f"   ℹ️  Traitement: {result.get('processing', 'N/A')}")
            
            # Vérifier les logs pour PATCH 48
            print("\n3️⃣ Vérification présence PATCH 48 dans le code...")
            import subprocess
            grep_result = subprocess.run(
                ["grep", "-n", "PATCH 48", "/app/backend/server.py"],
                capture_output=True,
                text=True
            )
            
            if grep_result.stdout:
                patch_lines = grep_result.stdout.strip().split('\n')
                print(f"   ✅ PATCH 48 trouvé: {len(patch_lines)} lignes")
                for line in patch_lines[:5]:  # Afficher les 5 premières lignes
                    print(f"      • {line}")
            else:
                print("   ⚠️  PATCH 48 non trouvé dans le code")
            
            print("\n4️⃣ Instructions pour test complet:")
            print("   1. Envoyer une vraie vidéo via n8n")
            print("   2. Vérifier les logs backend pour:")
            print("      • '🔄 PATCH 48: Téléchargement vidéo pour upload direct'")
            print("      • '✅ PATCH 48: Vidéo téléchargée (XXX bytes, video/mp4)'")
            print("      • '✅ Publication Facebook réussie: ID XXX'")
            print("   3. Confirmer que la vidéo apparaît sur la page Facebook")
            
            return True
        else:
            print(f"   ❌ Erreur webhook: {response.status_code}")
            print(f"   📄 Réponse: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur lors du test: {e}")
        return False

def check_patch48_implementation():
    """Vérifier que le PATCH 48 est bien implémenté"""
    print("\n🔍 Vérification implémentation PATCH 48...\n")
    
    with open("/app/backend/server.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    checks = {
        "Upload direct vidéos": "PATCH 48: Téléchargement vidéo pour upload direct" in content,
        "Détection MIME": "content_type = media_response.headers.get('Content-Type', 'video/mp4')" in content,
        "Files multipart": "files = {'source': (f'video.{extension}'" in content,
        "Timeout vidéo": "timeout=60" in content,
        "Fallback file_url": 'data["file_url"] = media_url' in content,
        "Logs PATCH 48": "log_app(f\"✅ PATCH 48:" in content
    }
    
    all_ok = True
    for check_name, check_result in checks.items():
        status = "✅" if check_result else "❌"
        print(f"   {status} {check_name}")
        if not check_result:
            all_ok = False
    
    print()
    return all_ok

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 TEST PATCH 48 - UPLOAD DIRECT VIDÉOS FACEBOOK")
    print("=" * 70)
    print()
    
    # Vérifier l'implémentation
    impl_ok = check_patch48_implementation()
    
    if not impl_ok:
        print("❌ Implémentation PATCH 48 incomplète\n")
        sys.exit(1)
    
    print("✅ Implémentation PATCH 48 complète\n")
    
    # Exécuter les tests
    test_ok = test_video_publication()
    
    print("\n" + "=" * 70)
    if test_ok:
        print("✅ PATCH 48 - TESTS RÉUSSIS")
        print("=" * 70)
        print("\n📋 Prochaines étapes:")
        print("   1. Tester avec une vraie vidéo via n8n")
        print("   2. Vérifier les logs pour 'PATCH 48'")
        print("   3. Confirmer publication Facebook vidéo réussie")
        print()
        sys.exit(0)
    else:
        print("❌ PATCH 48 - TESTS ÉCHOUÉS")
        print("=" * 70)
        sys.exit(1)
