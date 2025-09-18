#!/usr/bin/env python3
"""
Vérification finale que les 3 boutiques fonctionnent identiquement
"""
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8001"

def test_boutique(store_name, store_display_name):
    """Test complet d'une boutique"""
    print(f"\n🔍 Test complet de {store_name} ({store_display_name})")
    print("-" * 60)
    
    results = {
        'facebook': False,
        'instagram': False,
        'store_name': store_display_name
    }
    
    # Test Facebook
    print("📘 Test Facebook...")
    try:
        facebook_data = {
            "store": store_name,
            "message": f"✅ Test automatique Facebook pour {store_display_name} - Tout fonctionne parfaitement !",
            "product_url": "https://www.example.com/test-facebook",
            "platforms": ["facebook"]
        }
        
        response = requests.post(f"{API_BASE}/api/publish", json=facebook_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('facebook_result'):
                fb_id = result['facebook_result'].get('id', 'N/A')
                print(f"   ✅ Facebook: Publication réussie (ID: {fb_id})")
                results['facebook'] = True
            else:
                print(f"   ❌ Facebook: {result.get('error', 'Erreur inconnue')}")
        else:
            print(f"   ❌ Facebook: Erreur HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Facebook: Exception → {str(e)}")
    
    # Test Instagram
    print("📸 Test Instagram...")
    try:
        instagram_data = {
            "store": store_name,
            "message": f"✅ Test automatique Instagram pour {store_display_name} - Tout fonctionne parfaitement ! #{store_name} #test",
            "product_url": "https://www.example.com/test-instagram",
            "image_url": "https://images.unsplash.com/photo-1551717743-49959800b1f6?w=800",
            "platforms": ["instagram"]
        }
        
        response = requests.post(f"{API_BASE}/api/publish", json=instagram_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('instagram_result'):
                ig_id = result['instagram_result'].get('id', 'N/A')
                print(f"   ✅ Instagram: Publication réussie (ID: {ig_id})")
                results['instagram'] = True
            else:
                print(f"   ❌ Instagram: {result.get('error', 'Erreur inconnue')}")
        else:
            print(f"   ❌ Instagram: Erreur HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Instagram: Exception → {str(e)}")
    
    return results

def main():
    """Test principal"""
    print("🚀 VÉRIFICATION FINALE - LES 3 BOUTIQUES FONCTIONNENT-ELLES COMME OUTDOOR ?")
    print("=" * 80)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configuration des boutiques
    boutiques = {
        "gizmobbs": "Le Berger Blanc Suisse",
        "logicantiq": "LogicAntiq", 
        "outdoor": "Logicamp Outdoor"
    }
    
    # Test de l'API
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Backend accessible")
        else:
            print("❌ API Backend non accessible")
            return
    except Exception as e:
        print(f"❌ Impossible de contacter l'API: {e}")
        return
    
    # Tests des boutiques
    all_results = {}
    
    for store_code, store_name in boutiques.items():
        results = test_boutique(store_code, store_name)
        all_results[store_code] = results
    
    # Résumé final
    print(f"\n{'='*25} RÉSUMÉ FINAL {'='*25}")
    
    facebook_working = []
    instagram_working = []
    fully_working = []
    
    for store_code, results in all_results.items():
        store_name = results['store_name']
        
        # Status par plateforme
        if results['facebook']:
            facebook_working.append(store_code)
        if results['instagram']:
            instagram_working.append(store_code)
        if results['facebook'] and results['instagram']:
            fully_working.append(store_code)
        
        # Status global
        if results['facebook'] and results['instagram']:
            status = "✅ PARFAITEMENT FONCTIONNEL"
        elif results['facebook'] or results['instagram']:
            status = "⚠️ PARTIELLEMENT FONCTIONNEL"
        else:
            status = "❌ NON FONCTIONNEL"
        
        print(f"{status} {store_code} ({store_name})")
        if not results['facebook']:
            print(f"   → Facebook: Problème")
        if not results['instagram']:
            print(f"   → Instagram: Problème")
    
    print(f"\n📊 STATISTIQUES:")
    print(f"   📘 Facebook fonctionnel: {len(facebook_working)}/3 boutiques ({', '.join(facebook_working)})")
    print(f"   📸 Instagram fonctionnel: {len(instagram_working)}/3 boutiques ({', '.join(instagram_working)})")
    print(f"   🎯 Complètement fonctionnel: {len(fully_working)}/3 boutiques ({', '.join(fully_working)})")
    
    if len(fully_working) == 3:
        print(f"\n🎉 MISSION ACCOMPLIE !")
        print(f"✅ Les 3 boutiques (gizmobbs, logicantiq, outdoor) fonctionnent identiquement")
        print(f"✅ Facebook ET Instagram marchent pour toutes les boutiques")
        print(f"✅ Vous pouvez maintenant publier sur n'importe quelle boutique")
        
        print(f"\n💡 UTILISATION:")
        print(f"   - Interface web: http://localhost:8001")
        print(f"   - Sélectionnez votre boutique dans l'interface")
        print(f"   - Créez vos publications Facebook/Instagram")
        print(f"   - Toutes les boutiques ont les mêmes fonctionnalités maintenant !")
        
    elif len(fully_working) > 0:
        print(f"\n⚠️ PARTIELLEMENT RÉUSSI")
        print(f"✅ {len(fully_working)} boutique(s) fonctionnent complètement")
        print(f"⚠️ {3 - len(fully_working)} boutique(s) ont encore des problèmes")
        
    else:
        print(f"\n❌ PROBLÈMES DÉTECTÉS")
        print(f"Aucune boutique ne fonctionne complètement")
    
    return len(fully_working) == 3

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)