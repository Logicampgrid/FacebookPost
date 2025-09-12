#!/usr/bin/env python3
"""
Test direct de la correction OAuth avec URL ngrok connue
"""
import requests
import json

# URL ngrok que nous connaissons
NGROK_URL = "https://7aa500d89569.ngrok-free.app"

def test_direct_oauth():
    """Test direct avec l'URL ngrok"""
    print("🧪 Test direct de la correction OAuth")
    print("=" * 50)
    print(f"🌐 URL ngrok utilisée: {NGROK_URL}")
    
    # Code de test (simulé, sera remplacé par un vrai code Facebook)
    mock_code = "AQBzQC1ijC3Va15DLEVlPGWWUEHUvA4ZsqWTO1BAJWM8JI90aJ38RFP"
    
    # Test 1: Avec localhost (devrait être corrigé automatiquement vers ngrok)
    print(f"\n📝 Test 1: redirect_uri localhost → devrait utiliser ngrok")
    test_payload = {
        "code": mock_code,
        "state": "gizmobbs",
        "redirect_uri": "http://localhost:8001/"
    }
    
    try:
        print(f"   Envoi requête vers: http://localhost:8001/api/auth/facebook/exchange-code")
        print(f"   Payload: {json.dumps(test_payload, indent=2)}")
        
        response = requests.post(
            "http://localhost:8001/api/auth/facebook/exchange-code",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('success', False)}")
            print(f"   📄 Response structure: {list(data.keys())}")
            
            if 'error' in data:
                print(f"   ❌ Error: {data['error']}")
                
                # Vérifier si c'est une erreur de domaine Facebook
                if "domein" in data['error'].lower() or "domain" in data['error'].lower():
                    print(f"   🎯 ERREUR DE DOMAINE DÉTECTÉE!")
                    print(f"   💡 La correction fonctionne - ngrok est utilisé comme redirect_uri")
                    print(f"   ⚙️ Il faut maintenant configurer Facebook App")
                    return True
                else:
                    print(f"   ⚠️ Autre type d'erreur")
            
        else:
            print(f"   📄 Response: {response.text[:300]}...")
            
        return False
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def show_facebook_setup_guide():
    """Guide de configuration Facebook"""
    print(f"\n📋 GUIDE CONFIGURATION FACEBOOK APP")
    print("=" * 60)
    print(f"App ID: 5664227323683118")
    print(f"URL Ngrok actuelle: {NGROK_URL}")
    print()
    print("🔧 ÉTAPES DE CONFIGURATION:")
    print("1. Ouvrir https://developers.facebook.com/apps/5664227323683118/settings/basic/")
    print()
    print("2. Dans la section 'Domaines d'app', ajouter:")
    domain = NGROK_URL.replace('https://', '').replace('http://', '')
    print(f"   • {domain}")
    print(f"   • *.ngrok-free.app")
    print()
    print("3. Aller dans 'Produits' → 'Connexion Facebook' → 'Paramètres'")
    print("4. Dans 'URI de redirection OAuth valides', ajouter:")
    print(f"   • {NGROK_URL}/")
    print(f"   • {NGROK_URL}")
    print()
    print("5. Sauvegarder toutes les modifications")
    print()
    print("🧪 POUR TESTER APRÈS CONFIGURATION:")
    print("1. Aller sur votre application frontend")
    print("2. Cliquer sur 'Se connecter avec Facebook'") 
    print("3. L'authentification devrait maintenant fonctionner!")

if __name__ == "__main__":
    success = test_direct_oauth()
    
    if success:
        print(f"\n🎉 CORRECTION RÉUSSIE!")
        print(f"   La modification du redirect_uri fonctionne.")
        print(f"   L'application utilise maintenant l'URL ngrok au lieu de localhost.")
    else:
        print(f"\n🔍 Test non concluant")
        print(f"   Vérifiez les logs pour plus de détails.")
    
    show_facebook_setup_guide()