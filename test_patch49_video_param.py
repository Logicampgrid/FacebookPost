#!/usr/bin/env python3
"""
Test PATCH 49 - Validation Paramètre 'file' pour Vidéos Facebook
Vérifie que le changement source → file est bien appliqué
"""
import subprocess

def check_patch49_implementation():
    """Vérifier que PATCH 49 est correctement implémenté"""
    print("=" * 70)
    print("🔍 VÉRIFICATION PATCH 49 - Paramètre 'file' pour vidéos")
    print("=" * 70)
    print()
    
    with open("/app/backend/server.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Vérifications critiques
    checks = {
        "✅ PATCH 49 présent": "PATCH 49:" in content,
        "✅ Paramètre 'file' pour vidéos": "files = {'file':" in content and "video" in content.lower(),
        "✅ Logs PATCH 49": "log_app(f\"✅ PATCH 49:" in content or "log_app(f\"🔄 PATCH 49:" in content,
        "❌ Ancien 'source' pour vidéos supprimé": "{'source': (f'video." not in content,
        "✅ 'source' pour images maintenu": "{'source': ('image.jpg'" in content
    }
    
    all_ok = True
    for check_name, check_result in checks.items():
        status = "✅" if check_result else "❌"
        print(f"   {status} {check_name}")
        if not check_result:
            all_ok = False
    
    print()
    
    # Compter les occurrences
    patch49_count = content.count("PATCH 49")
    file_param_count = content.count("{'file':")
    source_param_count = content.count("{'source':")
    
    print(f"📊 Statistiques:")
    print(f"   • PATCH 49 mentions: {patch49_count}")
    print(f"   • Paramètre 'file': {file_param_count} occurrences")
    print(f"   • Paramètre 'source': {source_param_count} occurrences (images uniquement)")
    print()
    
    if all_ok and patch49_count >= 5:
        print("✅ PATCH 49 correctement implémenté!")
        return True
    else:
        print("❌ PATCH 49 incomplet ou mal appliqué")
        return False

def show_code_diff():
    """Afficher les lignes modifiées PATCH 49"""
    print("\n" + "=" * 70)
    print("📝 CODE MODIFIÉ - PATCH 49")
    print("=" * 70)
    print()
    
    result = subprocess.run(
        ["grep", "-n", "-A", "2", "-B", "2", "PATCH 49", "/app/backend/server.py"],
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        lines = result.stdout.strip().split('\n')
        for line in lines[:30]:  # Afficher les 30 premières lignes
            print(f"   {line}")
        
        if len(lines) > 30:
            print(f"\n   ... ({len(lines) - 30} lignes supplémentaires)")
    
    print()

def compare_with_patch48():
    """Comparer PATCH 48 vs PATCH 49"""
    print("=" * 70)
    print("🔄 COMPARAISON PATCH 48 vs PATCH 49")
    print("=" * 70)
    print()
    
    with open("/app/backend/server.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    print("📋 Changements:")
    print()
    
    if "PATCH 48" in content:
        print("   ⚠️  PATCH 48: Utilisait {'source': ...} pour vidéos")
        print("      → Facebook refusait avec erreur 6000")
        print()
    
    if "PATCH 49" in content and "{'file':" in content:
        print("   ✅ PATCH 49: Utilise {'file': ...} pour vidéos")
        print("      → Format correct pour l'API Facebook /videos")
        print()
    
    print("📊 Différences clés:")
    print()
    print("   Images (/photos):")
    print("      files = {'source': ('image.jpg', content, 'image/jpeg')}")
    print()
    print("   Vidéos (/videos):")
    print("      files = {'file': ('video.mp4', content, 'video/mp4')}")
    print()

if __name__ == "__main__":
    print("\n🧪 TEST PATCH 49 - FORMAT UPLOAD VIDÉO FACEBOOK\n")
    
    # Vérifier l'implémentation
    impl_ok = check_patch49_implementation()
    
    if impl_ok:
        # Afficher le code modifié
        show_code_diff()
        
        # Comparer avec PATCH 48
        compare_with_patch48()
        
        print("=" * 70)
        print("✅ PATCH 49 - PRÊT POUR TEST")
        print("=" * 70)
        print()
        print("📋 Prochaines étapes:")
        print("   1. Envoyer une vidéo via n8n")
        print("   2. Vérifier logs backend pour 'PATCH 49'")
        print("   3. Confirmer: Plus d'erreur 6000/1363042")
        print("   4. Vérifier: Vidéo publiée sur Facebook")
        print()
    else:
        print("\n❌ PATCH 49 nécessite corrections\n")

