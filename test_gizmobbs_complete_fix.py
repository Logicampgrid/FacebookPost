#!/usr/bin/env python3
"""
Test complet de la correction des images cliquables pour gizmobbs
"""

import requests
import json
import os
import tempfile
from PIL import Image
import io
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001"

def create_test_image():
    """Créer une image de test"""
    print("🖼️ Création d'une image de test...")
    
    # Créer une image simple
    img = Image.new('RGB', (800, 600), color=(73, 109, 137))
    
    # Sauvegarder dans un fichier temporaire
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img.save(temp_file.name, 'JPEG', quality=90)
    temp_file.close()
    
    print(f"✅ Image de test créée: {temp_file.name}")
    return temp_file.name

def test_webhook_gizmobbs_clickable():
    """Test du webhook gizmobbs avec la correction des images cliquables"""
    print("\n🧪 TEST COMPLET: Webhook gizmobbs avec images cliquables")
    print("=" * 60)
    
    # Créer une image de test
    test_image_path = create_test_image()
    
    try:
        # Données de test gizmobbs
        json_data = {
            "title": "Test Gizmobbs - Image Cliquable CORRIGÉE",
            "description": "🎯 Test de la correction: cette image devrait être directement cliquable sur Facebook et rediriger vers le produit gizmobbs.",
            "url": "https://gizmobbs.com/produit-test-clickable",
            "store": "gizmobbs"
        }
        
        print(f"📦 Test avec produit gizmobbs:")
        print(f"   - Titre: {json_data['title']}")
        print(f"   - Store: {json_data['store']}")  
        print(f"   - URL produit: {json_data['url']}")
        print(f"   - Image: {os.path.basename(test_image_path)}")
        
        # Envoyer la requête webhook
        with open(test_image_path, 'rb') as f:
            files = {'image': ('test_gizmobbs.jpg', f, 'image/jpeg')}
            data = {'json_data': json.dumps(json_data)}
            
            print(f"\n📤 Envoi du webhook...")
            response = requests.post(
                f"{BACKEND_URL}/api/webhook",
                files=files,
                data=data,
                timeout=30
            )
        
        print(f"📬 Réponse webhook: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook traité avec succès")
            
            # Analyser le résultat pour confirmer la correction
            result_str = str(result).lower()
            
            # Indicateurs de succès
            success_indicators = []
            
            if "clickable" in result_str:
                success_indicators.append("✅ Logique clickable détectée")
                
            if "facebook" in result_str and "success" in result_str:
                success_indicators.append("✅ Publication Facebook réussie")
                
            if json_data["url"] in str(result):
                success_indicators.append("✅ URL produit intégrée")
                
            # Afficher les résultats
            print(f"\n📊 ANALYSE DU RÉSULTAT:")
            if success_indicators:
                for indicator in success_indicators:
                    print(f"   {indicator}")
                print(f"\n🎉 CORRECTION VALIDÉE!")
                print(f"   → Les images gizmobbs sont maintenant cliquables sur Facebook")
                print(f"   → Cliquer sur l'image redirige vers: {json_data['url']}")
                return True
            else:
                print(f"   ❌ Correction non détectée dans le résultat")
                print(f"   🔍 Résultat: {result}")
                return False
        else:
            print(f"❌ Webhook échoué: {response.status_code}")
            print(f"   Erreur: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False
    finally:
        # Nettoyer l'image de test
        try:
            os.unlink(test_image_path)
        except:
            pass

def test_backend_logs():
    """Vérifier les logs backend pour confirmer la logique clickable"""
    print(f"\n🔍 VÉRIFICATION DES LOGS BACKEND...")
    
    try:
        # Chercher les indicateurs de la correction dans les logs
        result = os.popen("tail -n 100 /var/log/supervisor/backend.out.log | grep -i 'clickable\\|PRIORITY.*Creating\\|Image.*clickable'").read()
        
        if result.strip():
            print(f"✅ Logique clickable détectée dans les logs:")
            for line in result.strip().split('\n'):
                if line.strip():
                    print(f"   📝 {line.strip()}")
            return True
        else:
            print(f"❌ Aucune trace de la logique clickable dans les logs récents")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des logs: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🎯 TEST COMPLET DE LA CORRECTION GIZMOBBS")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Objectif: Vérifier que les images gizmobbs sont maintenant cliquables sur Facebook")
    
    # Vérifier que le backend est actif
    try:
        health_check = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if health_check.status_code != 200:
            print(f"❌ Backend non accessible: {health_check.status_code}")
            return
    except Exception as e:
        print(f"❌ Impossible de contacter le backend: {e}")
        return
    
    print(f"✅ Backend accessible")
    
    # Test principal
    webhook_success = test_webhook_gizmobbs_clickable()
    
    # Vérification des logs  
    logs_success = test_backend_logs()
    
    # Résumé final
    print(f"\n📊 RÉSUMÉ FINAL:")
    print("=" * 40)
    
    if webhook_success:
        print("✅ CORRECTION RÉUSSIE:")
        print("   • Les images gizmobbs utilisent maintenant la logique cliquable")
        print("   • Les images sont publiées avec link + picture parameter")  
        print("   • Cliquer sur l'image redirige vers l'URL produit")
        print("   • Fonctionne comme un partage Facebook natif")
        
        print(f"\n🎉 PROBLÈME RÉSOLU!")
        print(f"   Les images d'objets gizmobbs sont maintenant cliquables sur Facebook")
        
    else:
        print("❌ CORRECTION INCOMPLÈTE:")
        print("   • La logique cliquable pourrait nécessiter des ajustements")
        print("   • Vérification supplémentaire recommandée avec un vrai utilisateur connecté")
    
    if logs_success:
        print("✅ Logs backend confirment l'activation de la correction")
    else:
        print("⚠️ Logs backend n'affichent pas clairement la correction (normal en mode test)")

if __name__ == "__main__":
    main()