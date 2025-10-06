#!/usr/bin/env python3
"""
Test PATCH 40 - Vérification fonctionnement publications
"""
import asyncio
import sys
import os
import requests
import json

# Ajouter le backend au path
sys.path.append('/app/backend')
from server import process_webhook_publication

async def test_patch40():
    print("🧪 TEST PATCH 40 - CORRECTION PUBLICATIONS")
    print("=" * 50)
    
    # Test 1: Structure webhook_handler (comme dans vos logs)
    webhook_data_gizmobbs = {
        "data": {
            "store": "gizmobbs",
            "title": "Harnais de ceinture de sécurité de voiture réglable pour chiens",
            "url": "https://www.logicamp.org/wordpress/produit/harnais-chien/", 
            "description": "variable"
        },
        "file": {
            "filename": "webhook_test_1759772886.png",
            "is_image": True,
            "is_video": False,
            "public_url": "https://logicamp.org/wordpress/uploads/webhook_test.png"
        },
        "webhook_id": "test_patch40"
    }
    
    # Test 2: Structure logicantiq avec image
    webhook_data_logicantiq = {
        "data": {
            "store": "logicantiq", 
            "title": "🏷️ Assiette XVIIIᵉ siècle — Faïence des Islettes",
            "url": "https://www.logicamp.org/wordpress/produit/assiette-faience/",
            "description": "simple"
        },
        "file": {
            "filename": "img01-3.jpg", 
            "is_image": True,
            "is_video": False,
            "public_url": "https://logicamp.org/wordpress/uploads/img01-3.jpg"
        },
        "webhook_id": "test_patch40_logicantiq"
    }
    
    # Test 3: Structure outdoor avec vidéo
    webhook_data_outdoor = {
        "data": {
            "store": "outdoor",
            "title": "Tente d'hiver ignifuge pour 2 personnes", 
            "url": "https://www.logicamp.org/wordpress/produit/tente-hiver/",
            "description": "variable"
        },
        "file": {
            "filename": "video_demo.mp4",
            "is_image": False,
            "is_video": True,
            "public_url": "https://logicamp.org/wordpress/uploads/video_demo.mp4"
        },
        "webhook_id": "test_patch40_outdoor"
    }
    
    tests = [
        ("📱 Gizmobbs → @logicamp_berger (avec image)", webhook_data_gizmobbs),
        ("🏺 LogicAntiq (avec image)", webhook_data_logicantiq), 
        ("🏕️ Outdoor (avec vidéo)", webhook_data_outdoor)
    ]
    
    results = []
    
    for test_name, webhook_data in tests:
        print(f"\n🔬 Test: {test_name}")
        print("-" * 40)
        
        try:
            # Simuler le traitement comme dans vos logs réels
            result = await process_webhook_publication(webhook_data)
            
            if result:
                print(f"   ✅ SUCCÈS - Publication lancée")
                print(f"   📊 Store: {webhook_data['data']['store']}")
                print(f"   🎯 Titre: {webhook_data['data']['title'][:40]}...")
                if webhook_data.get('file'):
                    file_type = "Vidéo" if webhook_data['file']['is_video'] else "Image"
                    print(f"   🖼️ Média: {file_type}")
                results.append((test_name, "✅ SUCCÈS"))
            else:
                print(f"   ❌ ÉCHEC - Pas de publication")
                results.append((test_name, "❌ ÉCHEC"))
                
        except Exception as e:
            print(f"   💥 ERREUR: {str(e)}")
            results.append((test_name, f"💥 ERREUR: {str(e)[:50]}"))
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS PATCH 40")
    print("=" * 60)
    
    for test_name, status in results:
        print(f"{status} {test_name}")
    
    success_count = sum(1 for _, status in results if "✅" in status)
    print(f"\n🎯 Résultat global: {success_count}/{len(results)} tests réussis")
    
    if success_count == len(results):
        print("🎉 PATCH 40 VALIDÉ - Publications fonctionnelles !")
    else:
        print("⚠️ Certains tests ont échoué - Vérifiez la configuration")

if __name__ == "__main__":
    asyncio.run(test_patch40())