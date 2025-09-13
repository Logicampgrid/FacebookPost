#!/usr/bin/env python3
"""
Démonstration du Tunnel Instagram Gratuit
Script simple qui montre comment utiliser le tunnel une fois configuré
"""

import requests
import json
import tempfile
import os
from PIL import Image
from datetime import datetime

API_BASE = "http://localhost:8001"
WEBHOOK_URL = "https://ngrok-uri-sync.preview.emergentagent.com/api/webhook"

def create_demo_image():
    """Crée une image de démonstration pour le test"""
    # Créer une image simple avec PIL
    img = Image.new('RGB', (800, 600), color='lightblue')
    
    # Sauvegarder dans un fichier temporaire
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    img.save(temp_file.name, 'JPEG')
    temp_file.close()
    
    return temp_file.name

def test_webhook_publication():
    """Test une publication via webhook avec image générée"""
    print("🚀 DÉMONSTRATION TUNNEL INSTAGRAM GRATUIT")
    print("=" * 50)
    
    # Vérifier si utilisateur connecté
    try:
        response = requests.get(f"{API_BASE}/api/health")
        data = response.json()
        users_count = data['database']['users_count']
        
        if users_count == 0:
            print("❌ Aucun utilisateur connecté")
            print("🔑 Connectez-vous d'abord sur http://localhost:3000")
            return False
            
        print(f"✅ {users_count} utilisateur(s) connecté(s)")
        
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False
    
    # Créer une image de test
    print("🖼️ Création d'une image de test...")
    demo_image = create_demo_image()
    
    try:
        # Préparer les données
        json_data = {
            "title": "🧪 Test Tunnel Instagram Gratuit",
            "description": f"Test automatique du tunnel Instagram le {datetime.now().strftime('%d/%m/%Y à %H:%M')}. Si vous voyez ce post sur @logicamp_berger, le tunnel fonctionne parfaitement ! 🎉",
            "url": "https://gizmobbs.com/tunnel-test",
            "store": "gizmobbs"  # Publiera sur @logicamp_berger
        }
        
        print(f"📝 Données de test:")
        print(f"   Store: {json_data['store']} → @logicamp_berger")
        print(f"   Title: {json_data['title']}")
        
        # Faire la requête webhook
        print(f"🌐 Envoi vers webhook: {WEBHOOK_URL}")
        
        with open(demo_image, 'rb') as img_file:
            files = {'image': img_file}
            data = {'json_data': json.dumps(json_data)}
            
            response = requests.post(WEBHOOK_URL, files=files, data=data, timeout=30)
        
        print(f"📡 Réponse webhook: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCÈS - Webhook traité!")
            
            # Afficher les détails
            if 'data' in result:
                webhook_data = result['data']
                print(f"   Image: {webhook_data.get('image_filename')}")
                print(f"   Taille: {webhook_data.get('image_size_bytes')} bytes")
                
                # Résultats de publication
                if 'publication_results' in webhook_data:
                    pub_results = webhook_data['publication_results']
                    for pub_result in pub_results:
                        status = pub_result.get('status', 'unknown')
                        message = pub_result.get('message', 'No message')
                        print(f"   Publication: {status} - {message}")
                        
                        if status == 'success':
                            platforms = pub_result.get('platforms', [])
                            for platform in platforms:
                                platform_name = platform.get('platform', 'unknown')
                                post_id = platform.get('post_id', 'N/A')
                                print(f"      ✅ {platform_name}: {post_id}")
            
            return True
            
        else:
            print(f"❌ Erreur webhook: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Détail: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Réponse: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️ Timeout - La publication peut prendre du temps")
        print("   Vérifiez Instagram dans quelques minutes")
        return True
        
    except Exception as e:
        print(f"❌ Erreur publication: {e}")
        return False
        
    finally:
        # Nettoyer l'image temporaire
        if os.path.exists(demo_image):
            os.unlink(demo_image)

def show_tunnel_info():
    """Affiche les informations du tunnel"""
    print("\n📋 INFORMATIONS DU TUNNEL:")
    print(f"   URL: {WEBHOOK_URL}")
    print("   Méthode: POST (multipart/form-data)")
    print("   Champs: image (fichier) + json_data (JSON)")
    print("   Target: @logicamp_berger sur Instagram")
    
    print("\n🎯 MAGASINS DISPONIBLES:")
    stores = ["outdoor", "gizmobbs", "gimobbs", "logicantiq", "ma-boutique"]
    for store in stores:
        print(f"   - {store} → @logicamp_berger")
    
    print(f"\n🌐 Interface web: http://localhost:3000")

def main():
    """Démonstration principale"""
    show_tunnel_info()
    
    print("\n" + "=" * 50)
    response = input("Voulez-vous tester le tunnel maintenant ? (y/N): ")
    
    if response.lower() in ['y', 'yes', 'o', 'oui']:
        success = test_webhook_publication()
        
        if success:
            print("\n🎉 TUNNEL INSTAGRAM OPÉRATIONNEL!")
            print("   Vérifiez @logicamp_berger sur Instagram")
            print("   pour voir votre post de test")
        else:
            print("\n⚠️ Problème détecté")
            print("   Exécutez: python3 instagram_tunnel_fix.py")
            print("   pour diagnostiquer")
    else:
        print("\n💡 Pour tester plus tard:")
        print("   python3 demo_tunnel_instagram.py")

if __name__ == "__main__":
    main()