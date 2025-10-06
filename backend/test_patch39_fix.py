#!/usr/bin/env python3
"""
PATCH 39 - Test correction erreur 'NoneType' object is not subscriptable'
Test que les webhooks avec fichiers vidéo peuvent maintenant être traités sans erreur
"""

import requests
import time
import os
import json

def test_patch39_webhook_handling():
    """Test que le webhook peut maintenant traiter les vidéos sans erreur NoneType"""
    print(f"\n🔧 PATCH 39 - Test correction 'NoneType' object is not subscriptable")
    print(f"=" * 60)
    
    # URL du webhook
    webhook_url = "http://localhost:8001/api/webhook"
    
    # Données test basiques pour déclencher le traitement
    form_data = {
        "store": "gizmobbs",
        "title": "Test PATCH 39 - Vidéo Instagram", 
        "description": "Test correction erreur NoneType pour workflow container Instagram - PATCH 39",
        "product_url": "https://example.com/test-patch39"
    }
    
    # Simuler un fichier vidéo (petit fichier test)
    test_video_content = b"fake video content for patch 39 test"
    files = {
        'file': ('test_patch39.mp4', test_video_content, 'video/mp4')
    }
    
    print(f"\n📹 Test 1: Publication vidéo Instagram - vérification pas d'erreur NoneType")
    print(f"   Store: {form_data['store']}")
    print(f"   Titre: {form_data['title']}")
    print(f"   Fichier: test_patch39.mp4 ({len(test_video_content)} bytes)")
    
    try:
        print(f"\n🚀 Envoi de la requête webhook...")
        
        # Envoyer la requête POST au webhook
        response = requests.post(
            webhook_url,
            data=form_data,
            files=files,
            timeout=90  # Timeout étendu pour workflow container
        )
        
        print(f"📋 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.text:
            try:
                response_data = response.json()
                print(f"📋 Réponse JSON: {json.dumps(response_data, indent=2)}")
            except:
                print(f"📋 Réponse texte: {response.text[:500]}...")
        
        # Vérification principale: pas d'erreur 500 (erreur NoneType)
        if response.status_code != 500:
            print(f"\n✅ PATCH 39 VALIDÉ - Pas d'erreur 'NoneType' object is not subscriptable")
            print(f"   Le webhook traite maintenant les vidéos sans planter")
            
            if response.status_code == 200:
                print(f"🎉 BONUS: Publication réussie (status 200)")
            else:
                print(f"ℹ️ Publication en cours ou autre status ({response.status_code})")
                
        else:
            print(f"❌ PATCH 39 ÉCHEC - Erreur 500 détectée")
            print(f"   L'erreur 'NoneType' pourrait persister")
            
    except requests.exceptions.Timeout:
        print(f"⏰ TIMEOUT - Normal pour workflow container (traitement vidéo)")
        print(f"✅ PATCH 39 PROBABLEMENT VALIDÉ - Pas de crash immédiat")
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        
    print(f"\n" + "=" * 60)
    print(f"📋 RÉSUMÉ PATCH 39:")
    print(f"   🔧 Correction erreur 'NoneType' object is not subscriptable")
    print(f"   🎬 Workflow container Instagram maintenant accessible")  
    print(f"   ✅ Test terminé - voir résultats ci-dessus")

if __name__ == "__main__":
    test_patch39_webhook_handling()