#!/usr/bin/env python3
"""
Script de configuration pour Instagram Auto Publisher
Vérifie les dépendances et la configuration
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def check_dependencies():
    """Vérifie et installe les dépendances nécessaires"""
    print("🔍 Vérification des dépendances...")
    
    required_packages = [
        'Pillow',
        'motor', 
        'requests',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MANQUANT")
    
    if missing_packages:
        print(f"\n📦 Installation des packages manquants...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_packages)
            print("✅ Installation réussie!")
        except subprocess.CalledProcessError:
            print("❌ Erreur d'installation")
            return False
    
    return True

def check_ffmpeg():
    """Vérifie la présence de FFmpeg"""
    print("\n🎬 Vérification de FFmpeg...")
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg - OK")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ FFmpeg non trouvé")
    print("📦 Installation requise: apt-get install ffmpeg")
    return False

def check_environment():
    """Vérifie les variables d'environnement"""
    print("\n🔐 Vérification de l'environnement...")
    
    required_env = [
        'MONGO_URL',
        'FACEBOOK_GRAPH_URL'
    ]
    
    missing_env = []
    for env_var in required_env:
        if not os.getenv(env_var):
            missing_env.append(env_var)
            print(f"❌ {env_var} - MANQUANT")
        else:
            print(f"✅ {env_var} - OK")
    
    if missing_env:
        print(f"\n⚠️ Variables d'environnement manquantes:")
        for var in missing_env:
            print(f"  export {var}=<valeur>")
        return False
    
    return True

async def test_database_connection():
    """Test la connexion à la base de données"""
    print("\n🗄️ Test de connexion MongoDB...")
    try:
        import motor.motor_asyncio
        from dotenv import load_dotenv
        
        load_dotenv()
        
        MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
        db = client.meta_posts
        
        # Test simple
        await db.users.find_one()
        print("✅ Connexion MongoDB - OK")
        return True
        
    except Exception as e:
        print(f"❌ Connexion MongoDB - ERREUR: {str(e)}")
        return False

def create_example_script():
    """Crée un script d'exemple"""
    example_script = '''#!/bin/bash
# Exemple d'utilisation d'Instagram Auto Publisher

echo "📱 Publication Instagram - Exemples"

# Publication d'une image unique
echo "1️⃣ Publication image unique..."
python3 /app/instagram_auto_publisher.py \\
    --file "/path/to/image.webp" \\
    --caption "Belle photo de nos chiots Berger Blanc Suisse! 🐕" \\
    --hashtags "#bergerblancsuisse #chiots #elevage #chiens"

# Publication d'une vidéo
echo "2️⃣ Publication vidéo..."
python3 /app/instagram_auto_publisher.py \\
    --file "/path/to/video.mov" \\
    --caption "Nos chiots en plein jeu! 🎥" \\
    --hashtags "#video #chiots #jeu #bergerblancsuisse"

# Publication par lots
echo "3️⃣ Publication par lots..."
python3 /app/instagram_auto_publisher.py \\
    --batch "/path/to/photos_directory" \\
    --caption "Collection de photos de nos chiens" \\
    --hashtags "#collection #bergerblancsuisse #photos"

# Test sans publication
echo "4️⃣ Mode test..."
python3 /app/instagram_auto_publisher.py \\
    --file "/path/to/test.jpg" \\
    --caption "Test" \\
    --dry-run

echo "✅ Exemples terminés!"
'''
    
    with open('/app/example_instagram_usage.sh', 'w') as f:
        f.write(example_script)
    
    os.chmod('/app/example_instagram_usage.sh', 0o755)
    print("✅ Script d'exemple créé: /app/example_instagram_usage.sh")

def main():
    """Fonction principale de setup"""
    print("🚀 Configuration Instagram Auto Publisher")
    print("=" * 50)
    
    all_checks_passed = True
    
    # Vérifications
    if not check_dependencies():
        all_checks_passed = False
    
    if not check_ffmpeg():
        all_checks_passed = False
        print("ℹ️ FFmpeg requis uniquement pour conversion vidéo")
    
    if not check_environment():
        all_checks_passed = False
    
    # Test base de données
    try:
        db_ok = asyncio.run(test_database_connection())
        if not db_ok:
            all_checks_passed = False
    except Exception as e:
        print(f"❌ Erreur test DB: {str(e)}")
        all_checks_passed = False
    
    # Création dossiers
    print("\n📁 Création des dossiers...")
    os.makedirs('/app/logs', exist_ok=True)
    os.makedirs('/tmp', exist_ok=True)
    print("✅ Dossiers créés")
    
    # Script d'exemple
    create_example_script()
    
    # Résumé
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 Configuration terminée avec succès!")
        print("\n📋 Utilisation:")
        print("  python3 /app/instagram_auto_publisher.py --help")
        print("  bash /app/example_instagram_usage.sh")
    else:
        print("⚠️ Configuration incomplète - Vérifiez les erreurs ci-dessus")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)