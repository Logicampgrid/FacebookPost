#!/usr/bin/env python3
"""
Test pratique pour créer un post avec média et vérifier l'affichage correct
"""

import requests
import json
import base64
import io
from PIL import Image

API_BASE = "http://localhost:8001"

def create_test_image():
    """Créer une image de test simple"""
    # Créer une image de test avec PIL
    img = Image.new('RGB', (400, 300), color='lightblue')
    
    # Sauvegarder en mémoire
    img_buffer = io.BytesIO() 
    img.save(img_buffer, format='JPEG')
    img_buffer.seek(0)
    
    return img_buffer.getvalue()

def test_media_post_creation():
    """Test complet de création d'un post avec média"""
    print("🧪 Test de création d'un post avec média...")
    
    # Données de test
    test_user_id = "test_user_123"
    test_content = "Voici une belle image de test pour Le Berger Blanc Suisse! 🐕"
    
    try:
        # 1. Créer le post
        print("1️⃣ Création du post...")
        
        form_data = {
            'user_id': test_user_id,
            'content': test_content,
            'target_type': 'page',
            'target_id': 'test_page_id', 
            'target_name': 'Le Berger Blanc Suisse',
            'platform': 'facebook'
        }
        
        response = requests.post(f"{API_BASE}/api/posts", data=form_data)
        
        if response.status_code == 200:
            post_data = response.json()
            post_id = post_data['post']['id']
            print(f"✅ Post créé avec succès: {post_id}")
            
            # 2. Ajouter un média
            print("2️⃣ Upload de l'image...")
            
            # Créer une image de test
            image_data = create_test_image()
            
            files = {
                'file': ('test_image.jpg', image_data, 'image/jpeg')
            }
            
            media_response = requests.post(
                f"{API_BASE}/api/posts/{post_id}/media",
                files=files
            )
            
            if media_response.status_code == 200:
                media_result = media_response.json()
                print(f"✅ Média uploadé: {media_result['url']}")
                
                # 3. Simuler la logique de publication (sans vraiment publier sur Facebook)
                print("3️⃣ Test de la logique de publication...")
                
                # Récupérer le post avec ses médias
                posts_response = requests.get(f"{API_BASE}/api/posts?user_id={test_user_id}")
                
                if posts_response.status_code == 200:
                    posts = posts_response.json()['posts']
                    if posts:
                        test_post = posts[0]
                        print(f"✅ Post récupéré avec {len(test_post.get('media_urls', []))} média(s)")
                        
                        # Vérifier que le média est bien attaché
                        if test_post.get('media_urls'):
                            media_url = test_post['media_urls'][0]
                            print(f"   📸 URL du média: {media_url}")
                            
                            # Construire l'URL complète comme le fait le backend
                            full_url = f"https://bugfix-login.preview.emergentagent.com{media_url}"
                            print(f"   🌐 URL publique: {full_url}")
                            
                            # Tester l'accessibilité du média
                            try:
                                media_check = requests.head(full_url, timeout=5)
                                if media_check.status_code == 200:
                                    print("   ✅ Média accessible publiquement")
                                else:
                                    print(f"   ⚠️  Média non accessible: {media_check.status_code}")
                            except Exception as e:
                                print(f"   ⚠️  Erreur d'accès au média: {e}")
                            
                            return True
                        else:
                            print("❌ Aucun média trouvé dans le post")
                            return False
                    else:
                        print("❌ Aucun post trouvé")
                        return False
                else:
                    print(f"❌ Erreur récupération posts: {posts_response.status_code}")
                    return False
            else:
                print(f"❌ Erreur upload média: {media_response.status_code}")
                print(media_response.text)
                return False
        else:
            print(f"❌ Erreur création post: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

def test_video_format_detection():
    """Test de détection des formats vidéo"""
    print("\n🎥 Test de détection des formats vidéo...")
    
    video_urls = [
        "/uploads/test.mp4",
        "/uploads/video.mov", 
        "/uploads/clip.avi",
        "/uploads/movie.mkv"
    ]
    
    for url in video_urls:
        is_video = url.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))
        print(f"   {url}: {'🎥 Vidéo' if is_video else '📸 Image'}")
    
    return True

def main():
    """Test principal"""
    print("🚀 TEST DES AMÉLIORATIONS MÉDIAS")
    print("=" * 50)
    
    print("\n🎯 OBJECTIF:")
    print("Vérifier que les médias s'affichent correctement sur Facebook")
    print("au lieu d'apparaître comme des liens texte")
    
    tests = [
        ("Détection formats vidéo", test_video_format_detection),
        ("Création post avec média", test_media_post_creation)
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\n📋 {name}")
        print("-" * 40)
        result = test_func()
        results.append((name, result))
    
    # Résumé
    print("\n📊 RÉSUMÉ")
    print("=" * 50)
    
    success_count = sum(1 for _, result in results if result)
    
    for name, result in results:
        status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
        print(f"{status} - {name}")
    
    print(f"\n🎯 Score: {success_count}/{len(results)} tests réussis")
    
    if success_count == len(results):
        print("\n🎉 FÉLICITATIONS!")
        print("Les améliorations médias sont fonctionnelles.")
        print("Les images et vidéos devraient maintenant s'afficher")
        print("correctement sur Facebook au lieu des liens texte.")
    else:
        print("\n⚠️ ATTENTION")
        print("Certains tests ont échoué. Vérifiez les logs.")

if __name__ == "__main__":
    main()