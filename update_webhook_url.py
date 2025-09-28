#!/usr/bin/env python3
"""
SCRIPT DE MISE À JOUR AUTOMATIQUE WEBHOOK_URL
À exécuter après chaque redémarrage ngrok pour FacebookPost

Usage: python update_webhook_url.py
"""

import os
import sys
import requests
import time

def get_ngrok_url():
    """Récupère l'URL ngrok active"""
    try:
        print("🔍 Détection tunnel ngrok...")
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=10)
        
        if response.status_code == 200:
            tunnels = response.json().get('tunnels', [])
            
            # Chercher le tunnel pour le port 8001
            for tunnel in tunnels:
                config = tunnel.get('config', {})
                if config.get('addr') == "http://localhost:8001":
                    url = tunnel.get('public_url')
                    print(f"✅ Tunnel ngrok trouvé: {url}")
                    return url
            
            # Si pas de tunnel spécifique, prendre le premier
            if tunnels:
                url = tunnels[0].get('public_url')
                print(f"✅ Premier tunnel ngrok: {url}")
                return url
        
        print("❌ Aucun tunnel ngrok trouvé")
        return None
        
    except requests.exceptions.ConnectionError:
        print("❌ ngrok API non accessible - Vérifiez que ngrok est démarré")
        return None
    except Exception as e:
        print(f"❌ Erreur détection ngrok: {e}")
        return None

def update_env_file(file_path, key, new_value):
    """Met à jour une clé dans un fichier .env"""
    if not os.path.exists(file_path):
        print(f"⚠️ Fichier non trouvé: {file_path}")
        return False
    
    # Lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Mettre à jour ou ajouter la clé
    updated = False
    updated_lines = []
    
    for line in lines:
        if line.startswith(f"{key}="):
            old_value = line.split("=", 1)[1].strip() if "=" in line else ""
            updated_lines.append(f"{key}={new_value}\n")
            if old_value != new_value:
                print(f"✅ {key} mis à jour: {old_value} → {new_value}")
            else:
                print(f"ℹ️ {key} déjà à jour: {new_value}")
            updated = True
        else:
            updated_lines.append(line)
    
    if not updated:
        updated_lines.append(f"{key}={new_value}\n")
        print(f"✅ {key} ajouté: {new_value}")
    
    # Réécrire le fichier
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    return True

def test_webhook_url(webhook_url):
    """Test si l'URL webhook fonctionne"""
    test_url = f"{webhook_url}/api/webhook"
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "mon_token_secret_webhook", 
        "hub.challenge": "auto_update_test"
    }
    
    try:
        print(f"🧪 Test webhook: {test_url}")
        response = requests.get(test_url, params=params, timeout=15)
        
        if response.status_code == 200 and response.text == "auto_update_test":
            print("✅ Webhook accessible et fonctionnel")
            return True
        else:
            print(f"❌ Webhook non fonctionnel: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test webhook: {e}")
        return False

def main():
    """Mise à jour automatique WEBHOOK_URL"""
    print("🚀 MISE À JOUR AUTOMATIQUE WEBHOOK_URL")
    print("📋 FacebookPost - Synchronisation après redémarrage ngrok")
    print("=" * 55)
    
    # Étape 1: Détecter ngrok
    ngrok_url = get_ngrok_url()
    if not ngrok_url:
        print("\n❌ ÉCHEC: Impossible de détecter ngrok")
        print("💡 Solutions:")
        print("   1. Vérifiez que ngrok est démarré (ngrok http 8001)")
        print("   2. Vérifiez l'API ngrok: http://localhost:4040")
        print("   3. Redémarrez ngrok si nécessaire")
        return False
    
    # Étape 2: Mettre à jour .env backend
    print(f"\n📝 Mise à jour des fichiers .env avec: {ngrok_url}")
    
    backend_env = "/app/backend/.env"
    if update_env_file(backend_env, "WEBHOOK_URL", ngrok_url):
        print(f"✅ Backend .env mis à jour: {backend_env}")
    else:
        print(f"❌ Erreur mise à jour backend .env")
        return False
    
    # Étape 3: Mettre à jour .env frontend
    frontend_env = "/app/frontend/.env" 
    if update_env_file(frontend_env, "REACT_APP_BACKEND_URL", ngrok_url):
        print(f"✅ Frontend .env mis à jour: {frontend_env}")
    else:
        print(f"❌ Erreur mise à jour frontend .env")
        return False
    
    # Étape 4: Tester le webhook
    print(f"\n🧪 Test de fonctionnement...")
    webhook_works = test_webhook_url(ngrok_url)
    
    # Résultat final
    print("\n" + "=" * 55)
    if webhook_works:
        print("🎉 MISE À JOUR RÉUSSIE !")
        print(f"✅ WEBHOOK_URL configuré: {ngrok_url}")
        print("✅ Route /api/webhook fonctionnelle")
        print("\n📋 Prochaines étapes:")
        print("   • L'application est prête pour les publications")
        print("   • Store prioritaire: gizmobbs (@logicamp_berger)")
        print("   • Mode TEST activé pour économiser les crédits")
        return True
    else:
        print("⚠️ MISE À JOUR PARTIELLE")
        print(f"✅ URLs mises à jour dans .env")
        print(f"❌ Webhook non accessible")
        print("\n💡 Vérifications:")
        print("   • Le serveur FacebookPost est-il démarré ?")
        print("   • L'URL ngrok est-elle correcte ?")
        return False

if __name__ == "__main__":
    success = main()
    
    print(f"\n📝 RAPPEL IMPORTANT:")
    print(f"Exécutez ce script après chaque redémarrage ngrok:")
    print(f"  python {__file__}")
    
    exit(0 if success else 1)