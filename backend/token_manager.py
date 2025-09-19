# Token Manager - Récupération automatique des tokens Facebook/Instagram
import os
import requests
from typing import Dict, List, Optional
from datetime import datetime
import json

class TokenManager:
    def __init__(self):
        self.facebook_app_id = os.getenv("FACEBOOK_APP_ID")
        self.facebook_app_secret = os.getenv("FACEBOOK_APP_SECRET")
        self.facebook_direct_token = os.getenv("FACEBOOK_DIRECT_TOKEN")
        self.graph_url = os.getenv("FACEBOOK_GRAPH_URL", "https://graph.facebook.com/v18.0")
        
    def log_token(self, message: str, level: str = "INFO"):
        """Logging spécialisé pour les tokens"""
        icons = {"INFO": "🔑", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
        icon = icons.get(level.upper(), "🔑")
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{icon} [{timestamp}] [TOKEN] {message}")
        
    async def get_user_pages(self) -> List[Dict]:
        """Récupère toutes les pages Facebook gérées par l'utilisateur"""
        try:
            self.log_token("Récupération des pages Facebook...", "INFO")
            
            url = f"{self.graph_url}/me/accounts"
            params = {
                "access_token": self.facebook_direct_token,
                "fields": "id,name,access_token,instagram_business_account"
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            pages = data.get("data", [])
            
            self.log_token(f"✅ {len(pages)} pages récupérées", "SUCCESS")
            
            # Log des pages trouvées
            for page in pages:
                page_name = page.get("name", "Unknown")
                page_id = page.get("id", "Unknown")
                has_ig = "instagram_business_account" in page
                self.log_token(f"  • {page_name} (ID: {page_id}) - Instagram: {'✅' if has_ig else '❌'}", "INFO")
            
            return pages
            
        except Exception as e:
            self.log_token(f"Erreur récupération pages: {str(e)}", "ERROR")
            return []
    
    async def get_instagram_account_for_page(self, page_access_token: str, page_id: str) -> Optional[Dict]:
        """Récupère le compte Instagram Business associé à une page"""
        try:
            url = f"{self.graph_url}/{page_id}"
            params = {
                "access_token": page_access_token,
                "fields": "instagram_business_account"
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            ig_account = data.get("instagram_business_account")
            
            if ig_account:
                self.log_token(f"Instagram account trouvé pour page {page_id}: {ig_account['id']}", "SUCCESS")
                return ig_account
            else:
                self.log_token(f"Aucun compte Instagram connecté à la page {page_id}", "WARNING")
                return None
                
        except Exception as e:
            self.log_token(f"Erreur récupération Instagram pour page {page_id}: {str(e)}", "ERROR")
            return None
    
    async def auto_configure_stores(self) -> Dict[str, Dict]:
        """Configure automatiquement les stores avec les tokens récupérés"""
        try:
            self.log_token("🚀 Début configuration automatique des stores...", "INFO")
            
            # Récupérer toutes les pages
            pages = await self.get_user_pages()
            
            if not pages:
                raise Exception("Aucune page Facebook trouvée")
            
            # Configuration des stores basée sur les noms/IDs des pages
            store_configs = {}
            
            # Mapping des pages connues
            known_pages = {
                "102401876209415": "gizmobbs",  # Le Berger Blanc Suisse
                "210654558802531": "logicantiq",  # LogicAntiq
                "236260991673388": "outdoor"  # Logicamp Outdoor
            }
            
            for page in pages:
                page_id = page.get("id")
                page_name = page.get("name", "Unknown")
                page_access_token = page.get("access_token")
                
                if page_id in known_pages:
                    store_key = known_pages[page_id]
                    
                    self.log_token(f"Configuration store '{store_key}' ({page_name})...", "INFO")
                    
                    # Récupérer le compte Instagram associé
                    ig_account = await self.get_instagram_account_for_page(page_access_token, page_id)
                    
                    store_config = {
                        "name": page_name,
                        "fb_page_id": page_id,
                        "access_token": page_access_token,
                        "ig_user_id": ig_account["id"] if ig_account else None
                    }
                    
                    store_configs[store_key] = store_config
                    
                    self.log_token(f"✅ Store '{store_key}' configuré:", "SUCCESS")
                    self.log_token(f"  • Page: {page_name} ({page_id})", "INFO")
                    self.log_token(f"  • Instagram: {'✅ ' + ig_account['id'] if ig_account else '❌ Non connecté'}", "INFO")
                else:
                    self.log_token(f"Page non reconnue: {page_name} ({page_id})", "WARNING")
            
            # Vérifier que tous les stores attendus sont configurés
            expected_stores = ["gizmobbs", "logicantiq", "outdoor"]
            missing_stores = [store for store in expected_stores if store not in store_configs]
            
            if missing_stores:
                self.log_token(f"⚠️ Stores manquants: {missing_stores}", "WARNING")
            
            self.log_token(f"🎯 Configuration terminée: {len(store_configs)} stores configurés", "SUCCESS")
            return store_configs
            
        except Exception as e:
            self.log_token(f"❌ Erreur configuration automatique: {str(e)}", "ERROR")
            return {}
    
    async def update_env_with_tokens(self, store_configs: Dict[str, Dict]):
        """Met à jour le fichier .env avec les nouveaux tokens"""
        try:
            self.log_token("Mise à jour du fichier .env...", "INFO")
            
            env_path = "/app/backend/.env"
            
            # Lire le fichier .env actuel
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            else:
                lines = []
            
            # Préparer les nouvelles valeurs
            updates = {}
            for store_key, config in store_configs.items():
                store_upper = store_key.upper()
                updates[f"FB_ACCESS_TOKEN_{store_upper}"] = config["access_token"]
                updates[f"FB_PAGE_ID_{store_upper}"] = config["fb_page_id"]
                if config.get("ig_user_id"):
                    updates[f"IG_USER_ID_{store_upper}"] = config["ig_user_id"]
            
            # Mettre à jour les lignes existantes
            updated_lines = []
            updated_keys = set()
            
            for line in lines:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key = line.split("=", 1)[0]
                    if key in updates:
                        updated_lines.append(f"{key}={updates[key]}\n")
                        updated_keys.add(key)
                        self.log_token(f"✅ Mis à jour: {key}", "SUCCESS")
                    else:
                        updated_lines.append(line + "\n" if not line.endswith("\n") else line)
                else:
                    updated_lines.append(line + "\n" if not line.endswith("\n") else line)
            
            # Ajouter les nouvelles clés
            for key, value in updates.items():
                if key not in updated_keys:
                    updated_lines.append(f"{key}={value}\n")
                    self.log_token(f"✅ Ajouté: {key}", "SUCCESS")
            
            # Écrire le fichier mis à jour
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(updated_lines)
            
            self.log_token(f"🎯 Fichier .env mis à jour avec {len(updates)} tokens", "SUCCESS")
            
        except Exception as e:
            self.log_token(f"❌ Erreur mise à jour .env: {str(e)}", "ERROR")
    
    async def refresh_all_tokens(self) -> Dict[str, Dict]:
        """Rafraîchit tous les tokens et met à jour la configuration"""
        try:
            self.log_token("🔄 Rafraîchissement complet des tokens...", "INFO")
            
            # Configurer automatiquement les stores
            store_configs = await self.auto_configure_stores()
            
            if store_configs:
                # Mettre à jour le fichier .env
                await self.update_env_with_tokens(store_configs)
                
                self.log_token("🎉 Rafraîchissement terminé avec succès!", "SUCCESS")
                return store_configs
            else:
                self.log_token("❌ Aucune configuration récupérée", "ERROR")
                return {}
                
        except Exception as e:
            self.log_token(f"❌ Erreur rafraîchissement tokens: {str(e)}", "ERROR")
            return {}

# Instance globale
token_manager = TokenManager()