#!/usr/bin/env python3
"""
Démonstration pratique : Comment publier sur Instagram et Groupes
Meta Publishing Platform API Demo
"""

import requests
import json
from datetime import datetime

# Configuration de base
API_BASE = "https://crosspost-oauth.preview.emergentagent.com"

def test_backend_connection():
    """Test de connexion au backend"""
    print("🔧 Test de connexion au backend...")
    
    try:
        response = requests.get(f"{API_BASE}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend connecté: {data['status']}")
            print(f"📊 Base de données: {data['mongodb']}")
            print(f"👥 Utilisateurs: {data['database']['users_count']}")
            print(f"📝 Posts: {data['database']['posts_count']}")
            return True
        else:
            print(f"❌ Erreur backend: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False

def demo_instagram_publication():
    """Démonstration de publication Instagram"""
    print("\n📱 === DÉMONSTRATION INSTAGRAM ===")
    
    # Exemple de contenu pour Instagram
    post_data = {
        "content": """Découvrez notre nouveau produit outdoor ! 🏕️ 
Parfait pour vos aventures en pleine nature.

🔗 Lien en bio pour plus d'infos

#outdoor #camping #aventure #nature #nouveauté""",
        
        "target_type": "instagram",
        "target_id": "instagram_business_account_id",
        "target_name": "@logicampoutdoor",
        "platform": "instagram",
        "user_id": "user_id_here"
    }
    
    print("📝 Contenu Instagram préparé :")
    print(f"   Caption: {post_data['content'][:100]}...")
    print(f"   Compte cible: {post_data['target_name']}")
    print(f"   Type: {post_data['platform']}")
    
    # Spécificités Instagram
    print("\n📋 Spécificités Instagram automatiques :")
    print("   ✅ Image obligatoire (sera optimisée)")
    print("   ✅ Lien transformé en 'lien en bio'")
    print("   ✅ Hashtags intégrés dans la caption")
    print("   ✅ Format optimisé 4:5 à 1.91:1")
    
    return post_data

def demo_groupe_publication():
    """Démonstration de publication Groupe"""
    print("\n👥 === DÉMONSTRATION GROUPE FACEBOOK ===")
    
    # Exemple de contenu pour Groupe
    post_data = {
        "content": """Salut la communauté ! 👋

Voici notre dernier produit camping qui pourrait vous intéresser pour vos prochaines sorties !

Qu'est-ce que vous en pensez ? Des retours d'expérience à partager ?""",
        
        "target_type": "group",
        "target_id": "facebook_group_id",
        "target_name": "Passionnés de Camping & Outdoor",
        "platform": "facebook",
        "user_id": "user_id_here",
        "comment_link": "https://logicampoutdoor.com/nouveau-produit",
        "comment_text": "Découvrez tous nos produits sur notre site ! 🔗"
    }
    
    print("📝 Contenu Groupe préparé :")
    print(f"   Message: {post_data['content'][:100]}...")
    print(f"   Groupe cible: {post_data['target_name']}")
    print(f"   Lien produit: {post_data['comment_link']}")
    print(f"   Commentaire auto: {post_data['comment_text']}")
    
    # Avantages des groupes
    print("\n📋 Avantages Groupes Facebook :")
    print("   ✅ Liens directement cliquables")
    print("   ✅ Images deviennent cliquables avec lien")
    print("   ✅ Commentaire automatique pour engagement")
    print("   ✅ Pas de restriction sur les liens")
    print("   ✅ Audience ciblée et engagée")
    
    return post_data

def demo_cross_posting():
    """Démonstration de cross-posting"""
    print("\n🔄 === DÉMONSTRATION CROSS-POSTING ===")
    
    # Configuration cross-posting
    cross_targets = [
        {
            "id": "page_facebook_id",
            "name": "Logicamp Outdoor",
            "platform": "facebook",
            "type": "page"
        },
        {
            "id": "instagram_account_id", 
            "name": "@logicampoutdoor",
            "platform": "instagram",
            "type": "instagram"
        },
        {
            "id": "group1_id",
            "name": "Camping France",
            "platform": "facebook",
            "type": "group"
        },
        {
            "id": "group2_id",
            "name": "Outdoor & Randonnée", 
            "platform": "facebook",
            "type": "group"
        }
    ]
    
    post_data = {
        "content": """Nouvelle tente 4 saisons disponible ! 🏕️
Résistante aux intempéries et ultra-légère.
https://logicampoutdoor.com/tente-4-saisons""",
        
        "target_type": "cross-post",
        "target_id": "cross-post",
        "target_name": f"Cross-post ({len(cross_targets)} plateformes)",
        "platform": "meta",
        "cross_post_targets": cross_targets,
        "user_id": "user_id_here"
    }
    
    print("📝 Cross-posting configuré :")
    print(f"   Contenu original: {post_data['content'][:80]}...")
    print(f"   Plateformes cibles: {len(cross_targets)}")
    
    for target in cross_targets:
        print(f"   - {target['name']} ({target['platform']} {target['type']})")
    
    print("\n📋 Adaptation automatique par plateforme :")
    print("   📘 Page Facebook: Lien avec preview automatique")
    print("   📱 Instagram: Caption adaptée + 'lien en bio'")
    print("   👥 Groupes: Message contextuel + image cliquable")
    
    return post_data

def demo_api_calls():
    """Démonstration des appels API"""
    print("\n🔌 === APPELS API DÉMONSTRATIFS ===")
    
    # Test création d'un post (sans publier réellement)
    demo_post = {
        "user_id": "demo_user",
        "content": "Post de démonstration",
        "target_type": "page",
        "target_id": "demo_page",
        "target_name": "Page Démo",
        "platform": "facebook"
    }
    
    print("📤 Exemple d'appel API pour création de post :")
    print(f"POST {API_BASE}/api/posts")
    print("Headers: Content-Type: application/json")
    print(f"Body: {json.dumps(demo_post, indent=2, ensure_ascii=False)}")
    
    print("\n📥 Réponse API attendue :")
    expected_response = {
        "success": True,
        "message": "Post créé avec succès",
        "post": {
            "id": "post_id_generated",
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "platform": "facebook"
        }
    }
    print(json.dumps(expected_response, indent=2, ensure_ascii=False))

def main():
    """Fonction principale de démonstration"""
    print("🎯 === DÉMONSTRATION META PUBLISHING PLATFORM ===")
    print("Publication Instagram & Groupes Facebook")
    print("=" * 60)
    
    # Test connexion
    if not test_backend_connection():
        print("❌ Impossible de continuer sans connexion backend")
        return
    
    # Démonstrations
    instagram_post = demo_instagram_publication()
    groupe_post = demo_groupe_publication() 
    cross_post = demo_cross_posting()
    demo_api_calls()
    
    print("\n" + "=" * 60)
    print("🎉 RÉSUMÉ DE LA DÉMONSTRATION")
    print("=" * 60)
    
    print("\n📱 INSTAGRAM :")
    print("   • Image obligatoire + caption adaptée")
    print("   • Liens convertis en 'lien en bio'")
    print("   • Optimisation automatique des images")
    print("   • Hashtags intégrés")
    
    print("\n👥 GROUPES FACEBOOK :")
    print("   • Liens directement cliquables")
    print("   • Images deviennent cliquables")
    print("   • Commentaires automatiques")
    print("   • Engagement naturel élevé")
    
    print("\n🔄 CROSS-POSTING :")
    print("   • Adaptation automatique du contenu")
    print("   • Publication simultanée multi-plateformes")
    print("   • Gestion des spécificités par plateforme")
    print("   • Suivi centralisé des publications")
    
    print(f"\n🔗 Pour publier réellement :")
    print(f"   1. Connectez-vous à : {API_BASE}")
    print(f"   2. Autorisez les permissions Facebook")
    print(f"   3. Sélectionnez votre Business Manager")
    print(f"   4. Créez votre premier post !")
    
    print("\n✨ L'application gère automatiquement toute la complexité technique !")

if __name__ == "__main__":
    main()