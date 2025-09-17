#!/usr/bin/env python3
"""
Script pour mettre à jour automatiquement le fichier .env du frontend
avec l'URL ngrok fournie en paramètre
"""
import sys
import os
from pathlib import Path

def update_frontend_env(ngrok_url):
    """Met à jour le fichier .env du frontend avec l'URL ngrok"""
    try:
        # Chemin vers le fichier .env du frontend
        script_dir = Path(__file__).parent
        env_file = script_dir / "frontend" / ".env"
        
        if not env_file.exists():
            print(f"❌ Fichier .env frontend non trouvé: {env_file}")
            return False
        
        # Lire le fichier actuel
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Mettre à jour REACT_APP_BACKEND_URL
        updated_lines = []
        backend_url_updated = False
        
        for line in lines:
            if line.startswith("REACT_APP_BACKEND_URL="):
                old_url = line.split("=", 1)[1].strip()
                if old_url != ngrok_url:
                    updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}\n")
                    print(f"✅ REACT_APP_BACKEND_URL mis à jour: {old_url} → {ngrok_url}")
                else:
                    updated_lines.append(line)
                    print(f"ℹ️ REACT_APP_BACKEND_URL déjà à jour: {ngrok_url}")
                backend_url_updated = True
            else:
                updated_lines.append(line)
        
        # Si REACT_APP_BACKEND_URL n'existe pas, l'ajouter
        if not backend_url_updated:
            updated_lines.append(f"REACT_APP_BACKEND_URL={ngrok_url}\n")
            print(f"✅ REACT_APP_BACKEND_URL ajouté: {ngrok_url}")
        
        # Créer une sauvegarde
        backup_file = env_file.with_suffix('.env.backup')
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # Écrire le fichier mis à jour
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        print(f"🎯 Frontend .env synchronisé avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur mise à jour frontend .env: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python update_frontend_env.py <ngrok_url>")
        print("Exemple: python update_frontend_env.py https://abc123.ngrok.io")
        sys.exit(1)
    
    ngrok_url = sys.argv[1].strip()
    
    # Validation de l'URL
    if not ngrok_url.startswith(('http://', 'https://')):
        print(f"❌ URL invalide: {ngrok_url}")
        print("L'URL doit commencer par http:// ou https://")
        sys.exit(1)
    
    print(f"🔧 Mise à jour de la configuration frontend avec: {ngrok_url}")
    
    success = update_frontend_env(ngrok_url)
    
    if success:
        print("✅ Configuration mise à jour avec succès!")
        sys.exit(0)
    else:
        print("❌ Échec de la mise à jour de la configuration")
        sys.exit(1)

if __name__ == "__main__":
    main()