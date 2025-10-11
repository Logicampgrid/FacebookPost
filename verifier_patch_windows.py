#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification automatique des PATCH appliqués sur serveur Windows
Vérifie que tous les PATCH 45-60 sont présents dans server.py
"""

import os
import sys
import re

def verifier_patch(filepath):
    """Vérifie la présence de tous les PATCH dans le fichier server.py"""
    
    if not os.path.exists(filepath):
        print(f"❌ ERREUR: Fichier non trouvé: {filepath}")
        print(f"   Vérifiez le chemin: C:\\FacebookPost\\backend\\server.py")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    patches_requis = {
        "PATCH 58": {
            "recherche": r'access_token.*FACEBOOK_DIRECT_TOKEN.*logicamp',
            "description": "Permissions vidéo Facebook Logicamp (token utilisateur)",
            "ligne_approx": 234
        },
        "PATCH 60": {
            "recherche": r'PATCH 60.*logicamp.*FACEBOOK_DIRECT_TOKEN.*préservé',
            "description": "Protection get_store_config() pour logicamp",
            "ligne_approx": 460
        },
        "PATCH 59": {
            "recherche": r'PATCH 59.*access_token.*préservé.*FACEBOOK_DIRECT_TOKEN',
            "description": "Token non écrasé par setup-instagram",
            "ligne_approx": 3846
        },
        "PATCH 56": {
            "recherche": r'PATCH 56.*max_wait.*180',
            "description": "Timeout vidéo Instagram 180s",
            "ligne_approx": 6549
        },
        "PATCH 55": {
            "recherche": r'PATCH 55.*Thread.*pymongo.*sync',
            "description": "MongoDB pymongo sync dans thread séparé",
            "ligne_approx": 5256
        },
        "PATCH 53": {
            "recherche": r'threading\.Thread.*N8N',
            "description": "Thread séparé pour N8N",
            "ligne_approx": 4993
        },
        "PATCH 51": {
            "recherche": r'PATCH 51.*Upload.*image.*FTP',
            "description": "Upload FTP images avec upload_for_publication()",
            "ligne_approx": 4680
        },
        "PATCH 52": {
            "recherche": r'PATCH 52.*image.*True',
            "description": "Upload FTP images obligatoire",
            "ligne_approx": 4671
        },
        "PATCH 45": {
            "recherche": r'PATCH 45.*arrière-plan|background',
            "description": "Traitement arrière-plan webhooks",
            "ligne_approx": 5224
        }
    }
    
    print("\n" + "="*80)
    print("🔍 VÉRIFICATION DES PATCH - Serveur Windows")
    print("="*80 + "\n")
    print(f"📁 Fichier analysé: {filepath}")
    print(f"📏 Taille fichier: {len(content)} caractères")
    print(f"📝 Lignes: {content.count(chr(10)) + 1}")
    print("\n" + "-"*80 + "\n")
    
    patches_trouves = []
    patches_manquants = []
    
    for patch_name, patch_info in patches_requis.items():
        pattern = patch_info["recherche"]
        description = patch_info["description"]
        ligne_approx = patch_info["ligne_approx"]
        
        if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
            patches_trouves.append(patch_name)
            print(f"✅ {patch_name}: TROUVÉ")
            print(f"   📋 {description}")
            print(f"   📍 Ligne approximative: ~{ligne_approx}")
            
            # Compter occurrences
            occurrences = len(re.findall(patch_name, content))
            if occurrences > 0:
                print(f"   🔢 Occurrences: {occurrences}")
        else:
            patches_manquants.append(patch_name)
            print(f"❌ {patch_name}: MANQUANT")
            print(f"   📋 {description}")
            print(f"   📍 Devrait être ligne: ~{ligne_approx}")
        
        print()
    
    print("-"*80 + "\n")
    
    # Résumé
    total_patches = len(patches_requis)
    nb_trouves = len(patches_trouves)
    nb_manquants = len(patches_manquants)
    
    print("📊 RÉSUMÉ DE VÉRIFICATION:\n")
    print(f"   ✅ PATCH trouvés:   {nb_trouves}/{total_patches}")
    print(f"   ❌ PATCH manquants: {nb_manquants}/{total_patches}")
    
    if nb_manquants == 0:
        print("\n🎉 SUCCÈS: Tous les PATCH sont correctement appliqués!")
        print("\n✅ Prochaine étape:")
        print("   1. Redémarrer le serveur: C:\\FacebookPost\\02_start_server_only.bat")
        print("   2. Vérifier les logs de démarrage")
        print("   3. Tester les publications N8N")
        return True
    else:
        print("\n⚠️ ATTENTION: Certains PATCH sont manquants!")
        print("\n📖 Prochaines étapes:")
        print("   1. Consulter: /app/GUIDE_APPLICATION_PATCH_WINDOWS.md")
        print("   2. Appliquer les PATCH manquants:")
        for patch in patches_manquants:
            print(f"      - {patch}: {patches_requis[patch]['description']}")
        print("   3. Relancer ce script pour vérifier")
        return False
    
    print("\n" + "="*80 + "\n")

def verifications_supplementaires(filepath):
    """Vérifications supplémentaires importantes"""
    print("🔧 VÉRIFICATIONS SUPPLÉMENTAIRES:\n")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # Check 1: Import threading
    if "import threading" in content:
        checks.append("✅ Import threading présent")
    else:
        checks.append("⚠️ Import threading MANQUANT (requis pour PATCH 53/55)")
    
    # Check 2: Import pymongo
    if "from pymongo import MongoClient" in content or "import pymongo" in content:
        checks.append("✅ Import pymongo présent")
    else:
        checks.append("⚠️ Import pymongo MANQUANT (requis pour PATCH 55)")
    
    # Check 3: FACEBOOK_DIRECT_TOKEN dans STORES
    if 'FACEBOOK_DIRECT_TOKEN' in content and 'logicamp' in content:
        checks.append("✅ FACEBOOK_DIRECT_TOKEN configuré pour logicamp")
    else:
        checks.append("⚠️ FACEBOOK_DIRECT_TOKEN manquant pour logicamp")
    
    # Check 4: Timeout 180s
    if "max_wait = 180" in content or "max_wait=180" in content:
        checks.append("✅ Timeout Instagram 180s configuré")
    else:
        checks.append("⚠️ Timeout Instagram pourrait être à 60s (ancien)")
    
    # Check 5: Thread séparé
    if "threading.Thread" in content and "N8N" in content:
        checks.append("✅ Thread séparé N8N implémenté")
    else:
        checks.append("⚠️ Thread séparé N8N manquant")
    
    for check in checks:
        print(f"   {check}")
    
    print()

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║          🔍 VÉRIFICATEUR DE PATCH - Serveur Windows                      ║
║                                                                           ║
║  Ce script vérifie que tous les PATCH 45-60 sont correctement appliqués  ║
║  dans le fichier C:\\FacebookPost\\backend\\server.py                       ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Détecter le chemin du fichier
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        # Chemin par défaut Windows
        filepath = r"C:\FacebookPost\backend\server.py"
        
        # Si on est sur Linux/Emergent, utiliser le chemin local
        if not os.path.exists(filepath):
            filepath = "/app/backend/server.py"
    
    print(f"🎯 Fichier à analyser: {filepath}\n")
    
    # Vérification principale
    success = verifier_patch(filepath)
    
    # Vérifications supplémentaires
    if os.path.exists(filepath):
        verifications_supplementaires(filepath)
    
    # Code de sortie
    sys.exit(0 if success else 1)
