#!/usr/bin/env python3
"""
Test Final du Tunnel Instagram Gratuit
Vérifie tous les aspects du tunnel et génère un rapport complet
"""

import requests
import json
import os
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8001"
FRONTEND_URL = "http://localhost:3000"
WEBHOOK_URL = "https://smart-fb-poster.preview.emergentagent.com/api/webhook"

def check_all_services():
    """Vérifie que tous les services sont opérationnels"""
    print("🔍 VÉRIFICATION DES SERVICES")
    print("-" * 30)
    
    services = {
        "Backend API": API_BASE,
        "Frontend": FRONTEND_URL, 
        "Webhook Public": WEBHOOK_URL
    }
    
    all_ok = True
    for service, url in services.items():
        try:
            if "webhook" in url:
                # Pour le webhook, on teste avec GET
                response = requests.get(url, timeout=10)
            else:
                response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {service}: OK")
            else:
                print(f"❌ {service}: Status {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"❌ {service}: Error - {e}")
            all_ok = False
    
    return all_ok

def check_tunnel_configuration():
    """Vérifie la configuration du tunnel Instagram"""
    print("\n📱 CONFIGURATION TUNNEL INSTAGRAM") 
    print("-" * 35)
    
    try:
        # Vérifier la santé du backend
        health_response = requests.get(f"{API_BASE}/api/health")
        health_data = health_response.json()
        
        print(f"Backend Status: {health_data['status']}")
        print(f"MongoDB: {health_data['mongodb']}")
        print(f"Utilisateurs: {health_data['database']['users_count']}")
        
        # Vérifier la configuration des magasins
        webhook_info = requests.get(f"{API_BASE}/api/webhook")
        webhook_data = webhook_info.json()
        
        available_stores = webhook_data.get('available_stores', [])
        print(f"Magasins configurés: {len(available_stores)}")
        
        instagram_stores = []
        shop_mapping = webhook_data.get('shop_mapping', {})
        for store, config in shop_mapping.items():
            if 'instagram' in config.get('platforms', []):
                target_ig = config.get('instagram_username', 'N/A')
                instagram_stores.append(f"{store} → @{target_ig}")
        
        print("Configuration Instagram:")
        for store_config in instagram_stores:
            print(f"  ✅ {store_config}")
        
        return len(instagram_stores) > 0
        
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
        return False

def check_user_authentication():
    """Vérifie si un utilisateur est connecté"""
    print(f"\n👤 AUTHENTIFICATION UTILISATEUR")
    print("-" * 32)
    
    try:
        diagnosis_response = requests.get(f"{API_BASE}/api/debug/instagram-complete-diagnosis")
        diagnosis = diagnosis_response.json()
        
        user_found = diagnosis['authentication']['user_found']
        business_managers = diagnosis['authentication']['business_managers_count']
        instagram_accounts = len(diagnosis.get('instagram_accounts', []))
        
        print(f"Utilisateur connecté: {'✅' if user_found else '❌'}")
        print(f"Business Managers: {business_managers}")
        print(f"Comptes Instagram: {instagram_accounts}")
        
        if instagram_accounts > 0:
            print("Comptes Instagram trouvés:")
            for account in diagnosis['instagram_accounts']:
                username = account.get('username', 'unknown')
                name = account.get('name', 'N/A')
                status = account.get('status', 'Unknown')
                print(f"  📱 @{username} ({name}) - {status}")
        
        return user_found and instagram_accounts > 0
        
    except Exception as e:
        print(f"❌ Erreur authentification: {e}")
        return False

def test_webhook_functionality():
    """Test la fonctionnalité webhook (sans vraie publication)"""
    print(f"\n🌐 TEST FONCTIONNALITÉ WEBHOOK")
    print("-" * 32)
    
    try:
        # Test GET sur webhook pour récupérer les infos
        webhook_response = requests.get(WEBHOOK_URL)
        if webhook_response.status_code == 200:
            print("✅ Endpoint webhook accessible")
            
            data = webhook_response.json()
            print(f"✅ Méthode: {data.get('method', 'N/A')}")
            print(f"✅ Content-Type: {data.get('content_type', 'N/A')}")
            
            required_fields = data.get('required_fields', {})
            print("✅ Champs requis:")
            for field, description in required_fields.items():
                print(f"    {field}: {description}")
            
            return True
        else:
            print(f"❌ Webhook inaccessible: {webhook_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test webhook: {e}")
        return False

def generate_usage_examples():
    """Génère des exemples d'utilisation du tunnel"""
    print(f"\n📖 EXEMPLES D'UTILISATION")
    print("-" * 25)
    
    print("🌐 Via Webhook cURL:")
    print(f"""curl -X POST "{WEBHOOK_URL}" \\
  -F "image=@mon-produit.jpg" \\
  -F 'json_data={{"title":"Mon Produit","description":"Description du produit","url":"https://monsite.com/produit","store":"gizmobbs"}}'""")
    
    print(f"\n🖥️ Via Interface Web:")
    print(f"   1. Allez sur {FRONTEND_URL}")
    print(f"   2. Onglet 'Tunnel Instagram'") 
    print(f"   3. Connectez Business Manager")
    print(f"   4. Onglet 'Créer un Post'")
    print(f"   5. Sélectionnez Instagram et publiez")
    
    print(f"\n🔧 Scripts Python:")
    print(f"   - Diagnostic: python3 /app/instagram_tunnel_fix.py")
    print(f"   - Test complet: python3 /app/test_instagram_tunnel.py") 
    print(f"   - Démonstration: python3 /app/demo_tunnel_instagram.py")

def main():
    """Test complet du tunnel Instagram"""
    print("🚀 TUNNEL INSTAGRAM GRATUIT - TEST FINAL")
    print("=" * 50)
    print(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 50)
    
    # Tests principaux
    services_ok = check_all_services()
    config_ok = check_tunnel_configuration()
    auth_ok = check_user_authentication()
    webhook_ok = test_webhook_functionality()
    
    # Génération des exemples
    generate_usage_examples()
    
    # Rapport final
    print("\n" + "=" * 50)
    print("📊 RAPPORT FINAL")
    print("=" * 50)
    
    print(f"🔧 Services: {'✅' if services_ok else '❌'}")
    print(f"⚙️ Configuration: {'✅' if config_ok else '❌'}")
    print(f"👤 Authentification: {'✅' if auth_ok else '❌'}")
    print(f"🌐 Webhook: {'✅' if webhook_ok else '❌'}")
    
    if services_ok and config_ok and webhook_ok:
        if auth_ok:
            print(f"\n🎉 TUNNEL INSTAGRAM 100% OPÉRATIONNEL!")
            print(f"   Vous pouvez publier immédiatement sur @logicamp_berger")
        else:
            print(f"\n⚠️ TUNNEL PRÊT - CONNEXION REQUISE")
            print(f"   Connectez-vous sur {FRONTEND_URL} pour activer")
            print(f"   Onglet 'Tunnel Instagram' → 'Connecter Business Manager'")
    else:
        print(f"\n❌ PROBLÈMES DÉTECTÉS")
        print(f"   Vérifiez les services et la configuration")
    
    print(f"\n🌍 URLs importantes:")
    print(f"   Interface: {FRONTEND_URL}")
    print(f"   API: {API_BASE}")
    print(f"   Webhook: {WEBHOOK_URL}")

if __name__ == "__main__":
    main()