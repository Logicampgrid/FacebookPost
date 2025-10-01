#!/usr/bin/env python3
"""
Outil de Diagnostic et Correction FTP
Analyse les problèmes FTP et propose des solutions automatiques
"""
import os
import ftplib
import socket
import time
import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json

class FTPDiagnosticTool:
    def __init__(self):
        # Configuration FTP depuis les variables d'environnement
        self.ftp_host = os.getenv("FTP_HOST", "logicamp.org")
        self.ftp_port = int(os.getenv("FTP_PORT", "21"))
        self.ftp_user = os.getenv("FTP_USER", "logi")
        self.ftp_password = os.getenv("FTP_PASSWORD", "logi")
        self.ftp_directory = os.getenv("FTP_DIRECTORY", "/wordpress/uploads/")
        self.ftp_initial_directory = os.getenv("FTP_INITIAL_DIRECTORY", "/")
        self.ftp_base_url = os.getenv("FTP_BASE_URL", f"https://{self.ftp_host}/wordpress/uploads/")
        
    def log_ftp(self, message: str, level: str = "INFO"):
        """Logging spécialisé pour FTP"""
        icons = {"INFO": "📡", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "DIAGNOSTIC": "🔍"}
        icon = icons.get(level.upper(), "📡")
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{icon} [{timestamp}] [FTP-DIAG] {message}")
    
    def test_network_connectivity(self) -> Dict:
        """Test de connectivité réseau de base"""
        self.log_ftp("Test de connectivité réseau...", "DIAGNOSTIC")
        
        result = {
            "host_resolvable": False,
            "port_reachable": False,
            "ping_time_ms": None,
            "error": None
        }
        
        try:
            # Test résolution DNS
            try:
                socket.gethostbyname(self.ftp_host)
                result["host_resolvable"] = True
                self.log_ftp(f"✅ DNS: {self.ftp_host} résolu", "SUCCESS")
            except socket.gaierror as e:
                result["error"] = f"Résolution DNS échouée: {e}"
                self.log_ftp(f"❌ DNS: {result['error']}", "ERROR")
                return result
            
            # Test connectivité TCP
            try:
                start_time = time.time()
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(10)
                    s.connect((self.ftp_host, self.ftp_port))
                    result["ping_time_ms"] = round((time.time() - start_time) * 1000, 2)
                    result["port_reachable"] = True
                    self.log_ftp(f"✅ TCP: Port {self.ftp_port} accessible ({result['ping_time_ms']}ms)", "SUCCESS")
            except (socket.timeout, ConnectionRefusedError, OSError) as e:
                result["error"] = f"Port {self.ftp_port} inaccessible: {e}"
                self.log_ftp(f"❌ TCP: {result['error']}", "ERROR")
                return result
                
        except Exception as e:
            result["error"] = f"Erreur test réseau: {e}"
            self.log_ftp(f"❌ Réseau: {result['error']}", "ERROR")
        
        return result
    
    def test_ftp_authentication(self) -> Dict:
        """Test d'authentification FTP avec différentes méthodes"""
        self.log_ftp("Test d'authentification FTP...", "DIAGNOSTIC")
        
        result = {
            "login_success": False,
            "method_used": None,
            "error": None,
            "ftp_banner": None
        }
        
        # Configurations à tester
        configs = [
            {"pasv": True, "timeout": 30, "name": "Passif"},
            {"pasv": False, "timeout": 30, "name": "Actif"},
            {"pasv": True, "timeout": 60, "name": "Passif long"},
        ]
        
        for config in configs:
            try:
                self.log_ftp(f"Tentative {config['name']}...", "DIAGNOSTIC")
                
                ftp = ftplib.FTP()
                ftp.set_pasv(config["pasv"])
                
                # Connexion avec timeout
                ftp.connect(self.ftp_host, self.ftp_port, timeout=config["timeout"])
                result["ftp_banner"] = ftp.getwelcome()
                
                # Authentification
                ftp.login(self.ftp_user, self.ftp_password)
                
                result["login_success"] = True
                result["method_used"] = config["name"]
                
                self.log_ftp(f"✅ Authentification réussie ({config['name']})", "SUCCESS")
                if result["ftp_banner"]:
                    self.log_ftp(f"📡 Banner: {result['ftp_banner'][:100]}...", "INFO")
                
                ftp.quit()
                break
                
            except ftplib.error_perm as e:
                result["error"] = f"Erreur permissions: {e}"
                self.log_ftp(f"❌ {config['name']}: {result['error']}", "ERROR")
            except (ftplib.error_temp, socket.timeout, OSError) as e:
                self.log_ftp(f"⚠️ {config['name']}: {e}", "WARNING")
                continue
            except Exception as e:
                self.log_ftp(f"❌ {config['name']}: Erreur inattendue: {e}", "ERROR")
                continue
        
        return result
    
    def test_directory_navigation(self) -> Dict:
        """Test de navigation dans les répertoires FTP"""
        self.log_ftp("Test de navigation des répertoires...", "DIAGNOSTIC")
        
        result = {
            "initial_dir_accessible": False,
            "target_dir_accessible": False,
            "current_working_directory": None,
            "alternative_paths": [],
            "error": None
        }
        
        try:
            ftp = ftplib.FTP()
            ftp.set_pasv(True)
            ftp.connect(self.ftp_host, self.ftp_port, timeout=30)
            ftp.login(self.ftp_user, self.ftp_password)
            
            # Répertoire de démarrage
            result["current_working_directory"] = ftp.pwd()
            self.log_ftp(f"📁 Répertoire initial: {result['current_working_directory']}", "INFO")
            
            # Test répertoire initial
            if self.ftp_initial_directory and self.ftp_initial_directory != "/":
                try:
                    ftp.cwd(self.ftp_initial_directory)
                    result["initial_dir_accessible"] = True
                    self.log_ftp(f"✅ Répertoire initial accessible: {self.ftp_initial_directory}", "SUCCESS")
                except ftplib.error_perm as e:
                    self.log_ftp(f"❌ Répertoire initial inaccessible: {e}", "ERROR")
            
            # Test répertoire cible
            try:
                ftp.cwd(self.ftp_directory)
                result["target_dir_accessible"] = True
                self.log_ftp(f"✅ Répertoire cible accessible: {self.ftp_directory}", "SUCCESS")
                
                # Lister quelques fichiers pour vérifier les permissions
                try:
                    files = ftp.nlst()[:5]  # Premier 5 fichiers
                    self.log_ftp(f"📋 Exemples de fichiers trouvés: {len(files)} fichier(s)", "INFO")
                except Exception as e:
                    self.log_ftp(f"⚠️ Impossible de lister les fichiers: {e}", "WARNING")
                    
            except ftplib.error_perm as e:
                self.log_ftp(f"❌ Répertoire cible inaccessible: {e}", "ERROR")
                
                # Tenter des chemins alternatifs
                alternative_paths = [
                    "/uploads/",
                    "/public_html/uploads/",
                    "/www/uploads/",
                    "/htdocs/uploads/",
                    "uploads/",
                    "/wordpress/wp-content/uploads/"
                ]
                
                for alt_path in alternative_paths:
                    try:
                        ftp.cwd("/")  # Retour à la racine
                        ftp.cwd(alt_path)
                        result["alternative_paths"].append(alt_path)
                        self.log_ftp(f"✅ Chemin alternatif trouvé: {alt_path}", "SUCCESS")
                    except:
                        continue
            
            ftp.quit()
            
        except Exception as e:
            result["error"] = f"Erreur navigation: {e}"
            self.log_ftp(f"❌ Navigation: {result['error']}", "ERROR")
        
        return result
    
    def test_upload_permissions(self) -> Dict:
        """Test des permissions d'upload"""
        self.log_ftp("Test des permissions d'upload...", "DIAGNOSTIC")
        
        result = {
            "can_upload": False,
            "test_file_created": False,
            "test_file_deleted": False,
            "error": None
        }
        
        try:
            ftp = ftplib.FTP()
            ftp.set_pasv(True)
            ftp.connect(self.ftp_host, self.ftp_port, timeout=30)
            ftp.login(self.ftp_user, self.ftp_password)
            
            # Naviguer vers le répertoire cible
            try:
                if self.ftp_initial_directory != "/":
                    ftp.cwd(self.ftp_initial_directory)
                ftp.cwd(self.ftp_directory)
            except ftplib.error_perm:
                ftp.cwd("/")  # Fallback racine
            
            # Créer un fichier de test
            test_filename = f"diagnostic_test_{int(time.time())}.txt"
            test_content = f"Test FTP diagnostic - {datetime.now().isoformat()}"
            
            try:
                # Upload du fichier de test
                from io import BytesIO
                test_file = BytesIO(test_content.encode('utf-8'))
                ftp.storbinary(f'STOR {test_filename}', test_file)
                result["can_upload"] = True
                result["test_file_created"] = True
                self.log_ftp(f"✅ Fichier de test créé: {test_filename}", "SUCCESS")
                
                # Vérifier la taille
                try:
                    remote_size = ftp.size(test_filename)
                    if remote_size == len(test_content.encode('utf-8')):
                        self.log_ftp(f"✅ Taille confirmée: {remote_size} bytes", "SUCCESS")
                    else:
                        self.log_ftp(f"⚠️ Taille différente: {remote_size} bytes", "WARNING")
                except:
                    self.log_ftp("⚠️ Impossible de vérifier la taille", "WARNING")
                
                # Supprimer le fichier de test
                try:
                    ftp.delete(test_filename)
                    result["test_file_deleted"] = True
                    self.log_ftp(f"✅ Fichier de test supprimé", "SUCCESS")
                except Exception as e:
                    self.log_ftp(f"⚠️ Impossible de supprimer le fichier de test: {e}", "WARNING")
                    
            except ftplib.error_perm as e:
                result["error"] = f"Permissions insuffisantes: {e}"
                self.log_ftp(f"❌ Upload: {result['error']}", "ERROR")
            
            ftp.quit()
            
        except Exception as e:
            result["error"] = f"Erreur test upload: {e}"
            self.log_ftp(f"❌ Upload: {result['error']}", "ERROR")
        
        return result
    
    def test_public_url_accessibility(self) -> Dict:
        """Test l'accessibilité des URLs publiques"""
        self.log_ftp("Test d'accessibilité des URLs publiques...", "DIAGNOSTIC")
        
        result = {
            "base_url_accessible": False,
            "test_url_accessible": False,
            "response_time_ms": None,
            "http_status": None,
            "error": None
        }
        
        try:
            # Test URL de base
            start_time = time.time()
            response = requests.head(self.ftp_base_url, timeout=10, allow_redirects=True)
            result["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
            result["http_status"] = response.status_code
            
            if response.status_code < 400:
                result["base_url_accessible"] = True
                self.log_ftp(f"✅ URL de base accessible (HTTP {response.status_code}, {result['response_time_ms']}ms)", "SUCCESS")
            else:
                self.log_ftp(f"⚠️ URL de base retourne HTTP {response.status_code}", "WARNING")
            
            # Test avec un fichier existant (si possible)
            # On va chercher dans le dossier uploads pour un fichier existant
            try:
                uploads_path = "/app/backend/uploads"
                if os.path.exists(uploads_path):
                    image_files = [f for f in os.listdir(uploads_path) 
                                 if f.lower().endswith(('.jpg', '.png', '.gif'))]
                    if image_files:
                        test_file = image_files[0]
                        test_url = f"{self.ftp_base_url}{test_file}"
                        
                        test_response = requests.head(test_url, timeout=10)
                        if test_response.status_code < 400:
                            result["test_url_accessible"] = True
                            self.log_ftp(f"✅ Fichier test accessible: {test_file}", "SUCCESS")
                        else:
                            self.log_ftp(f"⚠️ Fichier test non accessible (HTTP {test_response.status_code})", "WARNING")
            except Exception as e:
                self.log_ftp(f"⚠️ Impossible de tester fichier existant: {e}", "WARNING")
                
        except requests.exceptions.ConnectionError as e:
            result["error"] = f"Connexion refusée vers {self.ftp_base_url}: {e}"
            self.log_ftp(f"❌ URL: {result['error']}", "ERROR")
        except requests.exceptions.Timeout as e:
            result["error"] = f"Timeout vers {self.ftp_base_url}: {e}"
            self.log_ftp(f"❌ URL: {result['error']}", "ERROR")
        except Exception as e:
            result["error"] = f"Erreur test URL: {e}"
            self.log_ftp(f"❌ URL: {result['error']}", "ERROR")
        
        return result
    
    def run_full_diagnostic(self) -> Dict:
        """Exécute un diagnostic complet FTP"""
        self.log_ftp("🔍 Début diagnostic FTP complet...", "DIAGNOSTIC")
        
        diagnostic_result = {
            "timestamp": datetime.now().isoformat(),
            "ftp_config": {
                "host": self.ftp_host,
                "port": self.ftp_port,
                "user": self.ftp_user,
                "directory": self.ftp_directory,
                "initial_directory": self.ftp_initial_directory,
                "base_url": self.ftp_base_url
            },
            "tests": {
                "network": self.test_network_connectivity(),
                "authentication": self.test_ftp_authentication(),
                "navigation": self.test_directory_navigation(),
                "upload": self.test_upload_permissions(),
                "public_url": self.test_public_url_accessibility()
            },
            "overall_status": "unknown",
            "recommendations": []
        }
        
        # Analyser les résultats et générer des recommandations
        tests = diagnostic_result["tests"]
        recommendations = []
        
        # Analyse réseau
        if not tests["network"]["host_resolvable"]:
            recommendations.append("❌ CRITIQUE: Vérifiez la résolution DNS pour " + self.ftp_host)
            diagnostic_result["overall_status"] = "critical"
        elif not tests["network"]["port_reachable"]:
            recommendations.append(f"❌ CRITIQUE: Port {self.ftp_port} inaccessible. Vérifiez firewall/NAT")
            diagnostic_result["overall_status"] = "critical"
        
        # Analyse authentification
        if not tests["authentication"]["login_success"]:
            recommendations.append("❌ CRITIQUE: Authentification FTP échouée. Vérifiez identifiants")
            diagnostic_result["overall_status"] = "critical"
        else:
            recommendations.append(f"✅ Authentification OK ({tests['authentication']['method_used']})")
        
        # Analyse navigation
        if not tests["navigation"]["target_dir_accessible"]:
            if tests["navigation"]["alternative_paths"]:
                alt_paths = ", ".join(tests["navigation"]["alternative_paths"])
                recommendations.append(f"⚠️ Répertoire cible inaccessible. Chemins alternatifs: {alt_paths}")
            else:
                recommendations.append("❌ Aucun répertoire d'upload trouvé")
        else:
            recommendations.append("✅ Navigation répertoires OK")
        
        # Analyse upload
        if not tests["upload"]["can_upload"]:
            recommendations.append("❌ Upload impossible. Vérifiez permissions écriture")
        else:
            recommendations.append("✅ Permissions upload OK")
        
        # Analyse URL publique
        if not tests["public_url"]["base_url_accessible"]:
            recommendations.append(f"⚠️ URL publique non accessible: {self.ftp_base_url}")
        else:
            recommendations.append("✅ URLs publiques accessibles")
        
        # Déterminer le statut global
        if diagnostic_result["overall_status"] == "unknown":
            critical_issues = sum(1 for r in recommendations if r.startswith("❌"))
            warning_issues = sum(1 for r in recommendations if r.startswith("⚠️"))
            
            if critical_issues > 0:
                diagnostic_result["overall_status"] = "critical"
            elif warning_issues > 0:
                diagnostic_result["overall_status"] = "warning"
            else:
                diagnostic_result["overall_status"] = "healthy"
        
        diagnostic_result["recommendations"] = recommendations
        
        # Log du résumé
        self.log_ftp(f"🏁 Diagnostic terminé - Statut: {diagnostic_result['overall_status']}", "DIAGNOSTIC")
        for recommendation in recommendations:
            level = "ERROR" if recommendation.startswith("❌") else \
                   "WARNING" if recommendation.startswith("⚠️") else "SUCCESS"
            self.log_ftp(recommendation, level)
        
        return diagnostic_result
    
    def generate_fix_suggestions(self, diagnostic: Dict) -> List[str]:
        """Génère des suggestions de correction basées sur le diagnostic"""
        suggestions = []
        tests = diagnostic.get("tests", {})
        
        # Suggestions réseau
        if not tests.get("network", {}).get("host_resolvable"):
            suggestions.append("🌐 Vérifiez la connexion internet et la résolution DNS")
            suggestions.append("🌐 Testez: ping " + self.ftp_host)
        
        # Suggestions authentification
        if not tests.get("authentication", {}).get("login_success"):
            suggestions.append("🔐 Vérifiez les identifiants FTP dans le fichier .env")
            suggestions.append("🔐 Variables: FTP_HOST, FTP_USER, FTP_PASSWORD")
        
        # Suggestions répertoire
        if not tests.get("navigation", {}).get("target_dir_accessible"):
            alt_paths = tests.get("navigation", {}).get("alternative_paths", [])
            if alt_paths:
                suggestions.append(f"📁 Utilisez un chemin alternatif: {alt_paths[0]}")
                suggestions.append("📁 Modifiez FTP_DIRECTORY dans .env")
        
        # Suggestions upload
        if not tests.get("upload", {}).get("can_upload"):
            suggestions.append("📤 Contactez l'hébergeur pour vérifier les permissions d'écriture")
            suggestions.append("📤 Vérifiez que l'utilisateur FTP a accès en écriture au répertoire")
        
        # Suggestions URL publique
        if not tests.get("public_url", {}).get("base_url_accessible"):
            suggestions.append("🌍 Vérifiez que FTP_BASE_URL pointe vers le bon domaine")
            suggestions.append("🌍 Testez manuellement: " + self.ftp_base_url)
        
        return suggestions

# Instance globale
ftp_diagnostic = FTPDiagnosticTool()

def main():
    """Fonction principale pour utilisation en ligne de commande"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "full":
            # Diagnostic complet
            result = ftp_diagnostic.run_full_diagnostic()
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif sys.argv[1] == "fix":
            # Suggestions de correction
            result = ftp_diagnostic.run_full_diagnostic()
            suggestions = ftp_diagnostic.generate_fix_suggestions(result)
            print("\n🔧 SUGGESTIONS DE CORRECTION:")
            for suggestion in suggestions:
                print(f"  • {suggestion}")
    else:
        print("Usage:")
        print("  python ftp_diagnostic_tool.py full  # Diagnostic complet")
        print("  python ftp_diagnostic_tool.py fix   # Suggestions de correction")

if __name__ == "__main__":
    main()