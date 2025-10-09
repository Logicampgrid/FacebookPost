#!/usr/bin/env python3
"""
Diagnostic approfondi - Vidéos Facebook page Logicamp
Erreur 6000/1363042: "Vous n'avez pas l'autorisation d'importer une vidéo ici"
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

# Configuration
PAGE_ID = "174450429258625"  # Page Facebook Logicamp
TOKEN_KEY = "FB_ACCESS_TOKEN_LOGICAMP"
ACCESS_TOKEN = os.getenv(TOKEN_KEY)

if not ACCESS_TOKEN:
    print(f"❌ Token non trouvé: {TOKEN_KEY}")
    print(f"💡 Vérifiez /app/backend/.env")
    exit(1)

print("=" * 80)
print("🔍 DIAGNOSTIC VIDÉO FACEBOOK LOGICAMP")
print("=" * 80)
print(f"📘 Page ID: {PAGE_ID}")
print(f"🔑 Token: {ACCESS_TOKEN[:20]}...")
print()

# 1. Informations de la page
print("1️⃣ INFORMATIONS PAGE FACEBOOK")
print("-" * 80)
url = f"https://graph.facebook.com/v21.0/{PAGE_ID}"
params = {
    "fields": "id,name,category,fan_count,is_published,is_verified,verification_status",
    "access_token": ACCESS_TOKEN
}
response = requests.get(url, params=params)
if response.status_code == 200:
    data = response.json()
    print(f"✅ Nom: {data.get('name')}")
    print(f"✅ Catégorie: {data.get('category')}")
    print(f"✅ Fans: {data.get('fan_count')}")
    print(f"✅ Publiée: {data.get('is_published')}")
    print(f"✅ Vérifiée: {data.get('is_verified')}")
else:
    print(f"❌ Erreur récupération page: {response.status_code}")
    print(f"❌ {response.text}")

print()

# 2. Permissions du token
print("2️⃣ PERMISSIONS DU TOKEN")
print("-" * 80)
url = f"https://graph.facebook.com/v21.0/me/permissions"
params = {"access_token": ACCESS_TOKEN}
response = requests.get(url, params=params)
if response.status_code == 200:
    permissions = response.json().get('data', [])
    video_perms = [p for p in permissions if 'video' in p.get('permission', '').lower() or 'publish' in p.get('permission', '').lower()]
    
    print("📋 Permissions liées aux vidéos/publications:")
    for perm in video_perms:
        status = "✅" if perm.get('status') == 'granted' else "❌"
        print(f"{status} {perm.get('permission')}: {perm.get('status')}")
    
    if not video_perms:
        print("⚠️ Aucune permission vidéo spécifique trouvée")
        print("\n📋 Toutes les permissions:")
        for perm in permissions:
            status = "✅" if perm.get('status') == 'granted' else "❌"
            print(f"{status} {perm.get('permission')}: {perm.get('status')}")
else:
    print(f"❌ Erreur récupération permissions: {response.status_code}")
    print(f"❌ {response.text}")

print()

# 3. Vérifier les vidéos existantes
print("3️⃣ VIDÉOS EXISTANTES SUR LA PAGE")
print("-" * 80)
url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/videos"
params = {
    "fields": "id,created_time,description,length",
    "limit": 5,
    "access_token": ACCESS_TOKEN
}
response = requests.get(url, params=params)
if response.status_code == 200:
    videos = response.json().get('data', [])
    if videos:
        print(f"✅ {len(videos)} vidéos trouvées (dernières):")
        for video in videos:
            print(f"  • ID: {video.get('id')} - Créée: {video.get('created_time')} - Durée: {video.get('length')}s")
    else:
        print("⚠️ Aucune vidéo trouvée sur cette page")
        print("💡 Cela peut indiquer que la page n'a jamais publié de vidéos")
else:
    print(f"❌ Erreur récupération vidéos: {response.status_code}")
    print(f"❌ {response.text}")

print()

# 4. Tester l'accès à l'endpoint /videos
print("4️⃣ TEST D'ACCÈS ENDPOINT /videos")
print("-" * 80)
url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/videos"
params = {"access_token": ACCESS_TOKEN}
response = requests.get(url, params=params)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ Endpoint /videos accessible")
else:
    print(f"❌ Endpoint /videos NON accessible")
    print(f"❌ {response.text}")

print()

# 5. Vérifier le type de page
print("5️⃣ TYPE ET RESTRICTIONS DE PAGE")
print("-" * 80)
url = f"https://graph.facebook.com/v21.0/{PAGE_ID}"
params = {
    "fields": "category_list,page_token,restriction_info",
    "access_token": ACCESS_TOKEN
}
response = requests.get(url, params=params)
if response.status_code == 200:
    data = response.json()
    categories = data.get('category_list', [])
    print("📋 Catégories de la page:")
    for cat in categories:
        print(f"  • {cat.get('name')} (ID: {cat.get('id')})")
    
    restriction = data.get('restriction_info')
    if restriction:
        print(f"\n⚠️ Restrictions détectées:")
        print(f"  {restriction}")
    else:
        print(f"\n✅ Aucune restriction détectée")
else:
    print(f"❌ Erreur: {response.status_code}")

print()

# 6. Diagnostic final
print("6️⃣ DIAGNOSTIC FINAL")
print("-" * 80)
print("\n🔍 ANALYSE:")

# Vérifier si c'est un problème de permissions
url = f"https://graph.facebook.com/v21.0/me/accounts"
params = {"access_token": ACCESS_TOKEN}
response = requests.get(url, params=params)
if response.status_code == 200:
    pages = response.json().get('data', [])
    logicamp_page = next((p for p in pages if p.get('id') == PAGE_ID), None)
    
    if logicamp_page:
        print(f"✅ Page Logicamp trouvée dans les pages gérées")
        print(f"   Nom: {logicamp_page.get('name')}")
        print(f"   Tasks: {logicamp_page.get('tasks', [])}")
        
        tasks = logicamp_page.get('tasks', [])
        if 'CREATE_CONTENT' in tasks:
            print(f"   ✅ Permission CREATE_CONTENT présente")
        else:
            print(f"   ❌ Permission CREATE_CONTENT ABSENTE")
            print(f"   💡 C'est probablement la cause du problème!")
            
        if 'MODERATE' in tasks:
            print(f"   ✅ Permission MODERATE présente")
        else:
            print(f"   ⚠️ Permission MODERATE absente")
    else:
        print(f"❌ Page Logicamp NON trouvée dans les pages gérées")
        print(f"💡 Le token utilisé n'a pas accès à cette page")
else:
    print(f"❌ Impossible de vérifier les pages gérées")

print()
print("=" * 80)
print("📊 RÉSUMÉ")
print("=" * 80)
print("\n🎯 PROBLÈME IDENTIFIÉ:")
print("L'erreur 6000/1363042 indique généralement:")
print("  1. Page non vérifiée pour publier des vidéos")
print("  2. Token sans permission CREATE_CONTENT")
print("  3. Page avec restrictions de contenu vidéo")
print("  4. Business Manager sans rôle approprié")
print()
print("💡 SOLUTIONS POSSIBLES:")
print("  A. Vérifier dans Meta Business Suite que la page peut publier des vidéos")
print("  B. Régénérer le token avec toutes les permissions vidéo")
print("  C. Vérifier que le Business Manager a le rôle approprié")
print("  D. Utiliser l'upload vidéo initié (container) au lieu de l'upload direct")
print("=" * 80)
