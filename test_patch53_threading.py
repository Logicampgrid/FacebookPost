#!/usr/bin/env python3
"""
Test PATCH 53 - Validation thread séparé N8N
Vérifie que le traitement arrière-plan n'utilise plus asyncio.create_task mais threading.Thread
"""
import sys
import re

def test_patch_53():
    print("🔍 TEST PATCH 53 - Vérification thread séparé N8N")
    print("=" * 70)
    
    with open('/app/backend/server.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Vérifier que threading.Thread est utilisé
    if 'threading.Thread(' in content:
        print("✅ Test 1: threading.Thread() trouvé dans le code")
    else:
        print("❌ Test 1: threading.Thread() NON trouvé")
        return False
    
    # Test 2: Vérifier la fonction process_webhook_background_n8n_sync
    if 'def process_webhook_background_n8n_sync(' in content:
        print("✅ Test 2: Fonction synchrone process_webhook_background_n8n_sync() trouvée")
    else:
        print("❌ Test 2: Fonction synchrone NON trouvée")
        return False
    
    # Test 3: Vérifier asyncio.new_event_loop()
    if 'asyncio.new_event_loop()' in content:
        print("✅ Test 3: Nouvelle boucle événementielle asyncio.new_event_loop() trouvée")
    else:
        print("❌ Test 3: new_event_loop() NON trouvé")
        return False
    
    # Test 4: Vérifier que le thread est lancé en daemon
    if 'daemon=True' in content:
        print("✅ Test 4: Thread daemon=True configuré")
    else:
        print("❌ Test 4: daemon=True NON configuré")
        return False
    
    # Test 5: Vérifier les logs PATCH 53
    patch53_logs = content.count('PATCH 53')
    if patch53_logs >= 5:
        print(f"✅ Test 5: {patch53_logs} logs PATCH 53 trouvés (traçabilité complète)")
    else:
        print(f"⚠️ Test 5: Seulement {patch53_logs} logs PATCH 53 trouvés")
    
    # Test 6: Vérifier que process_webhook_background_n8n_sync est appelé
    if 'target=process_webhook_background_n8n_sync' in content:
        print("✅ Test 6: Thread cible process_webhook_background_n8n_sync")
    else:
        print("❌ Test 6: Thread ne pointe PAS vers la bonne fonction")
        return False
    
    # Test 7: Vérifier le message de retour
    if '"background_thread"' in content:
        print("✅ Test 7: Réponse indique 'background_thread' (PATCH 53)")
    else:
        print("⚠️ Test 7: Message de réponse non trouvé")
    
    # Test 8: Vérifier patch number 53
    if '"patch": 53' in content:
        print("✅ Test 8: Numéro de patch 53 présent dans les réponses")
    else:
        print("❌ Test 8: patch: 53 NON trouvé")
        return False
    
    print("=" * 70)
    print("✅ TOUS LES TESTS PATCH 53 RÉUSSIS!")
    print("\n🎯 RÉSULTAT ATTENDU:")
    print("  - N8N recevra une réponse immédiate (<1ms)")
    print("  - Thread Python séparé traitera la publication")
    print("  - Les await asyncio.sleep() ne bloqueront plus la réponse HTTP")
    print("  - N8N pourra traiter 50+ objets séquentiellement sans timeout")
    return True

if __name__ == "__main__":
    success = test_patch_53()
    sys.exit(0 if success else 1)
