#!/usr/bin/env python3
"""
PATCH 33: Diagnostic FTP avancé
Analyse en profondeur des problèmes de connexion et upload FTP
"""

import os
import sys
import time
import socket
import ftplib
import tempfile
from datetime import datetime

# Ajouter le répertoire backend au path
sys.path.append('/app/backend')

def log_diag(message: str, level: str = "INFO"):
    """Logging pour les diagnostics"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "DIAG": "🔍"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [DIAG PATCH 33] {message}")

def test_network_connectivity():
    """Teste la connectivité réseau de base"""
    log_diag("=== TEST CONNECTIVITÉ RÉSEAU ===", "DIAG")
    
    # Configuration FTP depuis .env
    from dotenv import load_dotenv
    load_dotenv('/app/backend/.env')
    
    ftp_host = os.getenv("FTP_HOST", "logicamp.org")
    ftp_port = int(os.getenv("FTP_PORT", "21"))
    
    # Test 1: Résolution DNS
    try:
        import socket
        ip_address = socket.gethostbyname(ftp_host)
        log_diag(f"Résolution DNS: {ftp_host} -> {ip_address}", "SUCCESS")
    except Exception as e:
        log_diag(f"Erreur résolution DNS: {e}", "ERROR")
        return False
    
    # Test 2: Connectivité TCP de base
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            start_time = time.time()
            result = s.connect_ex((ftp_host, ftp_port))
            connect_time = time.time() - start_time
            
            if result == 0:
                log_diag(f"TCP connexion OK en {connect_time:.2f}s", "SUCCESS")
                return True
            else:
                log_diag(f"TCP connexion échouée (code: {result})", "ERROR")
                return False
    except Exception as e:
        log_diag(f"Erreur test TCP: {e}", "ERROR")
        return False

def test_ftp_modes():
    """Teste différents modes FTP en détail"""
    log_diag("=== TEST MODES FTP DÉTAILLÉ ===", "DIAG")
    
    from dotenv import load_dotenv
    load_dotenv('/app/backend/.env')
    
    ftp_host = os.getenv("FTP_HOST", "logicamp.org")
    ftp_port = int(os.getenv("FTP_PORT", "21"))
    ftp_user = os.getenv("FTP_USER", "logi")
    ftp_password = os.getenv("FTP_PASSWORD", "6837")
    ftp_directory = os.getenv("FTP_DIRECTORY", "/www/wordpress/uploads/")
    
    modes = [
        {"pasv": True, "timeout": 15, "name": "Mode Passif"},
        {"pasv": False, "timeout": 15, "name": "Mode Actif"},
    ]
    
    for mode in modes:
        log_diag(f"Test {mode['name']}...", "INFO")
        
        try:
            ftp = ftplib.FTP()
            ftp.set_debuglevel(1)  # Mode debug pour voir les commandes
            ftp.set_pasv(mode["pasv"])
            
            # Étapes de connexion détaillées
            log_diag("Étape 1: Connexion TCP...", "INFO")
            ftp.connect(ftp_host, ftp_port, timeout=mode["timeout"])
            
            log_diag("Étape 2: Authentification...", "INFO")
            ftp.login(ftp_user, ftp_password)
            
            log_diag("Étape 3: Test PWD...", "INFO")
            current_dir = ftp.pwd()
            log_diag(f"Répertoire actuel: {current_dir}", "INFO")
            
            log_diag(f"Étape 4: Navigation vers {ftp_directory}...", "INFO")
            ftp.cwd(ftp_directory)
            log_diag("Navigation réussie!", "SUCCESS")
            
            log_diag("Étape 5: Test LIST...", "INFO")
            files = ftp.nlst()
            log_diag(f"Fichiers trouvés: {len(files)}", "INFO")
            
            log_diag("Étape 6: Test upload minimal...", "INFO")
            # Créer un fichier de test très petit
            test_content = b"PATCH33TEST"
            test_filename = f"test_patch33_{int(time.time())}.txt"
            
            # Utiliser STOR pour upload
            from io import BytesIO
            ftp.storbinary(f'STOR {test_filename}', BytesIO(test_content))
            log_diag("Upload test réussi!", "SUCCESS")
            
            # Nettoyage
            try:
                ftp.delete(test_filename)
                log_diag("Fichier test supprimé", "INFO")
            except:
                log_diag("Nettoyage optionnel échoué (pas grave)", "WARNING")
            
            ftp.quit()
            log_diag(f"{mode['name']}: SUCCÈS COMPLET", "SUCCESS")
            return True
            
        except Exception as e:
            log_diag(f"{mode['name']}: ÉCHEC - {e}", "ERROR")
            try:
                ftp.quit()
            except:
                pass
    
    return False

def test_firewall_issues():
    """Teste les problèmes liés au firewall"""
    log_diag("=== TEST PROBLÈMES FIREWALL ===", "DIAG")
    
    # Test ports communs
    from dotenv import load_dotenv
    load_dotenv('/app/backend/.env')
    
    ftp_host = os.getenv("FTP_HOST", "logicamp.org")
    
    test_ports = [21, 22, 80, 443, 990, 989]  # FTP, SSH, HTTP, HTTPS, FTPS
    
    for port in test_ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                result = s.connect_ex((ftp_host, port))
                if result == 0:
                    log_diag(f"Port {port}: OUVERT", "SUCCESS")
                else:
                    log_diag(f"Port {port}: fermé/filtré", "WARNING")
        except Exception as e:
            log_diag(f"Port {port}: erreur - {e}", "ERROR")

def test_environment_info():
    """Affiche les informations sur l'environnement"""
    log_diag("=== INFORMATIONS ENVIRONNEMENT ===", "DIAG")
    
    # Informations système
    import platform
    log_diag(f"OS: {platform.system()} {platform.release()}", "INFO")
    log_diag(f"Python: {platform.python_version()}", "INFO")
    
    # Informations réseau
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    log_diag(f"Hostname: {hostname}", "INFO")
    log_diag(f"IP locale: {local_ip}", "INFO")
    
    # Variables d'environnement FTP
    from dotenv import load_dotenv
    load_dotenv('/app/backend/.env')
    
    ftp_vars = ["FTP_HOST", "FTP_PORT", "FTP_USER", "FTP_DIRECTORY", "FTP_BASE_URL"]
    for var in ftp_vars:
        value = os.getenv(var, "NON DÉFINI")
        # Masquer le password
        if "PASSWORD" in var and value != "NON DÉFINI":
            value = "***"
        log_diag(f"{var}: {value}", "INFO")

def suggest_solutions():
    """Suggère des solutions aux problèmes détectés"""
    log_diag("=== SUGGESTIONS DE SOLUTIONS ===", "DIAG")
    
    log_diag("Si les timeouts persistent:", "INFO")
    log_diag("1. Vérifiez que le serveur FTP supporte le mode passif", "INFO") 
    log_diag("2. Augmentez les timeouts dans la configuration", "INFO")
    log_diag("3. Vérifiez les règles firewall sur le serveur", "INFO")
    log_diag("4. Testez depuis un autre réseau", "INFO")
    
    log_diag("Si la connexion initiale échoue:", "INFO")
    log_diag("1. Vérifiez les credentials FTP", "INFO")
    log_diag("2. Vérifiez que le répertoire /www/wordpress/uploads/ existe", "INFO")
    log_diag("3. Testez avec un client FTP standard (FileZilla)", "INFO")

def main():
    """Fonction principale de diagnostic"""
    log_diag("🔍 DIAGNOSTIC AVANCÉ FTP PATCH 33", "DIAG")
    
    # Test 1: Informations environnement
    test_environment_info()
    
    # Test 2: Connectivité réseau de base
    if not test_network_connectivity():
        log_diag("❌ Connectivité réseau échouée - arrêt diagnostic", "ERROR")
        return False
    
    # Test 3: Problèmes firewall
    test_firewall_issues()
    
    # Test 4: Modes FTP détaillés
    ftp_success = test_ftp_modes()
    
    # Test 5: Suggestions
    if not ftp_success:
        suggest_solutions()
    
    # Résumé
    log_diag("=== RÉSUMÉ DIAGNOSTIC ===", "DIAG")
    if ftp_success:
        log_diag("✅ FTP fonctionne - le problème était temporaire", "SUCCESS")
    else:
        log_diag("❌ FTP ne fonctionne pas - intervention requise", "ERROR")
    
    return ftp_success

if __name__ == "__main__":
    main()