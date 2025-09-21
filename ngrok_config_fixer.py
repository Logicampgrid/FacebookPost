#!/usr/bin/env python3
"""
Outil de réparation automatique de la configuration ngrok
Résout le problème de page blanche en synchronisant les URLs
"""

import requests
import os
import re
import time
import json
from pathlib import Path

class NgrokConfigFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_env = self.project_root / "backend" / ".env"
        self.frontend_env = self.project_root / "frontend" / ".env"
        self.main_env = self.project_root / ".env"
        self.ngrok_url_file = self.project_root / "backend" / "ngrok_url.txt"
        
    def log(self, level, message):
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "FIX": "🔧"}
        icon = icons.get(level, "📋")
        print(f"{icon} [NGROK-FIX] {message}")
    
    def get_active_ngrok_url(self):
        """Récupère l'URL ngrok active depuis l'API locale"""
        try:
            self.log("INFO", "Recherche d'un tunnel ngrok actif...")
            
            response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
            
            if response.status_code == 200:
                tunnels_data = response.json()
                tunnels = tunnels_data.get('tunnels', [])
                
                if tunnels:
                    # Priorité aux tunnels HTTPS
                    for tunnel in tunnels:
                        public_url = tunnel.get('public_url')
                        if public_url and public_url.startswith('https://'):
                            self.log("SUCCESS", f"Tunnel HTTPS trouvé: {public_url}")
                            return public_url
                    
                    # Sinon prendre le premier tunnel
                    first_url = tunnels[0].get('public_url')
                    if first_url:
                        self.log("SUCCESS", f"Tunnel trouvé: {first_url}")
                        return first_url
                
                self.log("WARNING", "Aucun tunnel actif trouvé")
                return None
                
        except requests.exceptions.ConnectionError:
            self.log("WARNING", "API ngrok non accessible (port 4040)")
            return None
        except Exception as e:
            self.log("ERROR", f"Erreur récupération ngrok: {e}")
            return None
    
    def update_env_file(self, file_path, key, value):
        """Met à jour une variable dans un fichier .env"""
        try:
            if not file_path.exists():
                self.log("WARNING", f"Fichier non trouvé: {file_path}")
                return False
            
            # Lire le contenu
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            # Mettre à jour ou ajouter la ligne
            updated = False
            new_lines = []
            
            for line in lines:
                if line.startswith(f"{key}="):
                    new_lines.append(f"{key}={value}")
                    updated = True
                    self.log("FIX", f"{key} mis à jour dans {file_path.name}")
                else:
                    new_lines.append(line)
            
            # Si la clé n'existait pas, l'ajouter
            if not updated:
                new_lines.append(f"{key}={value}")
                self.log("FIX", f"{key} ajouté dans {file_path.name}")
            
            # Réécrire le fichier
            file_path.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')
            return True
            
        except Exception as e:
            self.log("ERROR", f"Erreur mise à jour {file_path.name}: {e}")
            return False
    
    def save_ngrok_url(self, url):
        """Sauvegarde l'URL ngrok dans le fichier de référence"""
        try:
            self.ngrok_url_file.write_text(url, encoding='utf-8')
            self.log("SUCCESS", f"URL sauvegardée: {url}")
            return True
        except Exception as e:
            self.log("ERROR", f"Erreur sauvegarde URL: {e}")
            return False
    
    def fix_configuration(self, ngrok_url):
        """Corrige tous les fichiers de configuration avec la nouvelle URL"""
        self.log("FIX", "Correction de la configuration...")
        
        fixes = []
        
        # Mettre à jour le frontend .env
        if self.update_env_file(self.frontend_env, "REACT_APP_BACKEND_URL", ngrok_url):
            fixes.append("Frontend .env")
        
        # Mettre à jour le backend .env
        if self.update_env_file(self.backend_env, "WEBHOOK_URL", ngrok_url):
            fixes.append("Backend .env")
        
        # Mettre à jour le .env principal
        if self.update_env_file(self.main_env, "WEBHOOK_URL", ngrok_url):
            fixes.append("Main .env")
        
        # Sauvegarder l'URL
        if self.save_ngrok_url(ngrok_url):
            fixes.append("URL de référence")
        
        self.log("SUCCESS", f"Configuration corrigée dans: {', '.join(fixes)}")
        return len(fixes) > 0
    
    def get_old_urls_from_config(self):
        """Récupère les anciennes URLs des fichiers de configuration"""
        old_urls = {}
        
        try:
            # Frontend .env
            if self.frontend_env.exists():
                content = self.frontend_env.read_text()
                match = re.search(r'REACT_APP_BACKEND_URL=(.+)', content)
                if match:
                    old_urls['frontend'] = match.group(1).strip()
            
            # Backend .env
            if self.backend_env.exists():
                content = self.backend_env.read_text()
                match = re.search(r'WEBHOOK_URL=(.+)', content)
                if match:
                    old_urls['backend'] = match.group(1).strip()
                    
        except Exception as e:
            self.log("WARNING", f"Erreur lecture anciennes URLs: {e}")
        
        return old_urls
    
    def diagnose_and_fix(self):
        """Diagnostique le problème et applique la correction"""
        self.log("INFO", "🔍 Diagnostic de la configuration ngrok...")
        
        # 1. Vérifier les anciennes URLs
        old_urls = self.get_old_urls_from_config()
        if old_urls:
            self.log("INFO", "URLs actuelles dans la configuration:")
            for source, url in old_urls.items():
                self.log("INFO", f"  {source}: {url}")
        
        # 2. Chercher l'URL ngrok active
        active_url = self.get_active_ngrok_url()
        
        if not active_url:
            self.log("ERROR", "❌ Aucun tunnel ngrok actif trouvé")
            self.log("INFO", "Solutions possibles:")
            self.log("INFO", "1. Démarrez ngrok: ngrok http 8001")
            self.log("INFO", "2. Vérifiez que ngrok est installé")
            self.log("INFO", "3. Ou utilisez le mode local: http://localhost:8001")
            
            # Mode local de secours
            local_url = "http://localhost:8001"
            self.log("FIX", f"Application du mode local: {local_url}")
            return self.fix_configuration(local_url)
        
        # 3. Comparer avec les URLs configurées
        needs_fix = False
        for source, old_url in old_urls.items():
            if old_url != active_url:
                self.log("WARNING", f"URL incorrecte dans {source}: {old_url} ≠ {active_url}")
                needs_fix = True
        
        if not needs_fix and old_urls:
            self.log("SUCCESS", "✅ Configuration déjà correcte!")
            return True
        
        # 4. Appliquer la correction
        self.log("FIX", f"Correction avec l'URL active: {active_url}")
        return self.fix_configuration(active_url)
    
    def test_backend_connectivity(self):
        """Test la connectivité du backend"""
        try:
            self.log("INFO", "Test de connectivité backend...")
            response = requests.get("http://localhost:8001/api/health", timeout=5)
            
            if response.status_code == 200:
                self.log("SUCCESS", "✅ Backend accessible sur localhost:8001")
                return True
            else:
                self.log("WARNING", f"Backend répond avec le code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log("ERROR", f"Backend non accessible: {e}")
            return False
    
    def run_full_check(self):
        """Exécute un check complet et corrige si nécessaire"""
        self.log("INFO", "🚀 Démarrage du correcteur automatique ngrok")
        
        # Test backend
        if not self.test_backend_connectivity():
            self.log("ERROR", "⚠️ Backend non accessible - démarrez-le d'abord")
            return False
        
        # Diagnostic et correction
        success = self.diagnose_and_fix()
        
        if success:
            self.log("SUCCESS", "🎉 Configuration ngrok corrigée avec succès!")
            self.log("INFO", "🔄 Redémarrez votre navigateur ou actualisez la page")
            return True
        else:
            self.log("ERROR", "❌ Échec de la correction")
            return False

def main():
    """Point d'entrée principal"""
    fixer = NgrokConfigFixer()
    return fixer.run_full_check()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)