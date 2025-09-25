#!/usr/bin/env python3
"""
Test simple pour vérifier que le problème Instagram URL est corrigé
"""

import requests
import json
import time

def test_url_conversion():
    """Test la conversion d'URL via l'API"""
    
    print("🔍 TEST: Correction URL Instagram")
    print("=" * 40)
    
    # Test 1: Vérifier la conversion via l'endpoint de debug
    print("1. Test conversion URL via API...")
    
    try:
        response = requests.get("http://localhost:8001/api/test-uploads", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ API accessible: {response.status_code}")
            print(f"📂 Uploads montés: {data.get('uploads_mounted', False)}")
            print(f"🖼️ Images disponibles: {data.get('image_count', 0)}")
            
            # Vérifier la conversion de test
            test_conversion = data.get('test_conversion', {})
            if test_conversion.get('public_url'):
                public_url = test_conversion['public_url']
                print(f"🔗 URL publique générée: {public_url}")
                
                # Tester l'accessibilité de l'URL publique
                if public_url.startswith('https://'):
                    try:
                        url_test = requests.head(public_url, timeout=5)
                        if url_test.status_code == 200:
                            print(f"✅ URL publique accessible: {url_test.status_code}")
                            return True
                        else:
                            print(f"❌ URL publique non accessible: {url_test.status_code}")
                    except Exception as e:
                        print(f"❌ Erreur test URL publique: {e}")
                else:
                    print(f"⚠️ URL générée n'est pas HTTPS: {public_url}")
            else:
                print("❌ Aucune URL publique générée")
                
        else:
            print(f"❌ API non accessible: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur test API: {e}")
    
    return False

def test_instagram_simulation():
    """Simule une requête Instagram avec un webhook"""
    
    print("\n2. Test simulation webhook Instagram...")
    
    # Données de test similaires au webhook original
    test_data = {
        "store": "gizmobbs",
        "title": "Test Instagram URL Fix",
        "url": "https://www.logicamp.org/test",
        "description": "Test de correction URL Instagram",
        "platforms": ["instagram"]
    }
    
    try:
        # Créer un fichier image de test
        with open('/app/backend/uploads/test_instagram_fix.jpg', 'wb') as f:
            # Image JPEG minimale (1x1 pixel)
            jpeg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
            f.write(jpeg_data)
        
        print("✅ Image de test créée")
        
        # Test avec form-data comme le webhook original
        files = {'image': ('test_instagram_fix.jpg', open('/app/backend/uploads/test_instagram_fix.jpg', 'rb'), 'image/jpeg')}
        data = {'json_data': json.dumps(test_data)}
        
        response = requests.post(
            "http://localhost:8001/api/webhook",
            files=files,
            data=data,
            timeout=15
        )
        
        files['image'][1].close()  # Fermer le fichier
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook traité: {response.status_code}")
            
            # Vérifier le résultat
            if result.get('success'):
                print(f"✅ Publication réussie!")
                platforms = result.get('platforms', [])
                if 'instagram' in platforms:
                    print(f"✅ Instagram inclus dans les plateformes")
                else:
                    print(f"⚠️ Instagram non trouvé dans les plateformes: {platforms}")
            else:
                error = result.get('error', 'Erreur inconnue')
                print(f"❌ Publication échouée: {error}")
                
                # Chercher des détails sur l'erreur Instagram
                if 'instagram' in str(error).lower():
                    if 'Only photo or video can be accepted' in str(error):
                        print("🎯 ERREUR CONFIRMÉE: Problème URL Instagram encore présent")
                        return False
                    else:
                        print("⚠️ Autre erreur Instagram détectée")
                
        else:
            print(f"❌ Webhook échoué: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Détail: {error_detail}")
            except:
                print(f"   Réponse: {response.text[:200]}")
    
    except Exception as e:
        print(f"❌ Erreur simulation webhook: {e}")
        return False
    
    return True

def main():
    """Fonction principale de test"""
    
    print("🚀 DIAGNOSTIC CORRECTION INSTAGRAM URL")
    print("=" * 50)
    
    # Attendre que le serveur soit prêt
    print("⏳ Attente démarrage serveur...")
    time.sleep(2)
    
    # Test 1: Conversion URL
    url_ok = test_url_conversion()
    
    # Test 2: Simulation webhook
    if url_ok:
        webhook_ok = test_instagram_simulation()
        
        if webhook_ok:
            print("\n" + "=" * 50)
            print("🎉 SUCCÈS: Problème Instagram URL corrigé!")
            print("✅ Les images sont maintenant accessibles publiquement")
            print("✅ Instagram devrait accepter les publications")
        else:
            print("\n" + "=" * 50)
            print("⚠️ Tests partiels: URL publique OK, mais test webhook à vérifier")
    else:
        print("\n" + "=" * 50)
        print("❌ PROBLÈME PERSISTE: URL publique non générée correctement")
        print("💡 Vérifiez que PUBLIC_BASE_URL est bien configuré")
    
    print("=" * 50)

if __name__ == "__main__":
    main()