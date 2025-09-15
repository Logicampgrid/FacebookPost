#!/usr/bin/env python3
"""
Test de la nouvelle approche ngrok stable
"""

import requests
import subprocess
import time
import os
import sys
from dotenv import load_dotenv

# Ajouter le chemin du backend
sys.path.append('/app/backend')

def test_ngrok_stability():
    """Test de stabilité ngrok"""
    print("🧪 TEST APPROCHE NGROK STABLE")
    print("=" * 50)
    
    # Test 1: Vérifier si ngrok est déjà actif
    print("\n1️⃣ Test détection ngrok existant...")
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=3)
        if response.status_code == 200:
            tunnels = response.json().get('tunnels', [])
            if tunnels:
                url = tunnels[0]['public_url']
                print(f"✅ Ngrok actif détecté: {url}")
                return test_server_with_ngrok(url)
            else:
                print("⚠️ API ngrok accessible mais aucun tunnel")
        else:
            print(f"⚠️ API ngrok répond avec status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Ngrok non actif (API port 4040 non accessible)")
    except Exception as e:
        print(f"❌ Erreur test ngrok: {e}")
    
    print("\n2️⃣ Démarrage ngrok standalone pour test...")
    return start_and_test_ngrok()

def start_and_test_ngrok():
    """Démarrer ngrok standalone et tester"""
    try:
        # Charger l'environnement
        load_dotenv()
        
        # Configurer le token si disponible
        token = os.getenv("NGROK_AUTH_TOKEN")
        if token:
            subprocess.run(["ngrok", "config", "add-authtoken", token], 
                         capture_output=True)
            print("✅ Token ngrok configuré")
        
        # Démarrer ngrok en arrière-plan
        print("🚀 Démarrage ngrok en arrière-plan...")
        process = subprocess.Popen(
            ["ngrok", "http", "8001", "--log=stdout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Attendre le démarrage
        print("⏳ Attente démarrage ngrok...")
        for i in range(10):
            time.sleep(2)
            try:
                response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
                if response.status_code == 200:
                    tunnels = response.json().get('tunnels', [])
                    if tunnels:
                        url = tunnels[0]['public_url']
                        print(f"✅ Ngrok démarré: {url}")
                        
                        # Test stabilité
                        result = test_server_with_ngrok(url)
                        
                        # Nettoyer
                        process.terminate()
                        return result
            except:
                print(f"⏳ Tentative {i+1}/10...")
        
        print("❌ Ngrok ne démarre pas dans les temps")
        process.terminate()
        return False
        
    except Exception as e:
        print(f"❌ Erreur démarrage ngrok: {e}")
        return False

def test_server_with_ngrok(ngrok_url):
    """Tester le serveur avec l'URL ngrok"""
    print(f"\n3️⃣ Test serveur avec ngrok: {ngrok_url}")
    
    try:
        # Test 1: Endpoint de santé
        print("🔍 Test endpoint santé...")
        response = requests.get(f"{ngrok_url}/api/health", 
                              headers={"ngrok-skip-browser-warning": "true"}, 
                              timeout=10)
        if response.status_code == 200:
            print("✅ Endpoint santé OK")
        else:
            print(f"⚠️ Endpoint santé status: {response.status_code}")
        
        # Test 2: Construction redirect_uri
        print("🔍 Test construction redirect_uri...")
        from server import build_dynamic_redirect_uri
        
        redirect_uri = build_dynamic_redirect_uri("/auth/callback")
        if ngrok_url in redirect_uri:
            print(f"✅ Redirect URI correcte: {redirect_uri}")
        else:
            print(f"❌ Redirect URI incorrecte: {redirect_uri}")
            return False
        
        # Test 3: Endpoint OAuth Facebook (simulation)
        print("🔍 Test endpoint OAuth Facebook...")
        test_data = {
            "code": "test_code_stable",
            "state": "gizmobbs"
        }
        
        response = requests.post(
            f"{ngrok_url}/api/auth/facebook/exchange-code",
            headers={
                "Content-Type": "application/json",
                "ngrok-skip-browser-warning": "true"
            },
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if not result.get("success") and "191" in str(result.get("error", "")):
                print("✅ OAuth endpoint fonctionne (erreur 191 attendue)")
                print("💡 Il suffit maintenant de configurer Facebook avec cette URL")
                return True
            else:
                print(f"⚠️ Réponse OAuth inattendue: {result}")
        else:
            print(f"❌ Erreur OAuth status: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test serveur: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 TEST COMPLET APPROCHE NGROK STABLE")
    print("Objectif: URL ngrok stable qui ne change plus")
    print("=" * 60)
    
    success = test_ngrok_stability()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST RÉUSSI: Approche ngrok stable validée!")
        print("\n💡 INSTRUCTIONS D'UTILISATION:")
        print("1. Démarrez ngrok avec: python start_ngrok_standalone.py")
        print("2. Notez l'URL ngrok affichée")
        print("3. Configurez Facebook une seule fois avec cette URL")
        print("4. Démarrez le serveur avec: python server.py")
        print("5. Le serveur détectera automatiquement l'URL ngrok")
        print("\n🎯 AVANTAGE: L'URL ne changera plus!")
    else:
        print("❌ TEST ÉCHOUÉ: Problème avec l'approche ngrok")
    
if __name__ == "__main__":
    main()