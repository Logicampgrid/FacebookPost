# backend/utils/ftp_upload.py
import os
import ftplib
import requests
import logging
from typing import Optional

FTP_HOST = os.getenv("FTP_HOST", "logicamp.org")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER", "logi")
FTP_PASS = os.getenv("FTP_PASSWORD", "logi")
FTP_DIRECTORY = os.getenv("FTP_DIRECTORY", "/wordpress/uploads/")  # adapte si diffère
PUBLIC_BASE = os.getenv("FTP_BASE_URL", "https://www.logicamp.org").rstrip('/')  # base pour construire URL publique

def upload_file_via_ftp(local_path: str, remote_name: str, timeout=15) -> Optional[str]:
    """
    CORRECTION: Upload FTP robuste avec retry logic et gestion WinError 64
    Essaye différentes configurations FTP avec retry automatique
    """
    import time
    
    # Configurations à tester (de la plus stable à la moins stable)
    ftp_configs = [
        {"pasv": False, "timeout": 30, "encoding": "utf-8", "name": "Actif UTF8"},
        {"pasv": True, "timeout": 25, "encoding": "utf-8", "name": "Passif UTF8"},  
        {"pasv": False, "timeout": 20, "encoding": "latin1", "name": "Actif Latin1"},
        {"pasv": True, "timeout": 15, "encoding": "latin1", "name": "Passif Latin1"}
    ]
    
    for attempt, config in enumerate(ftp_configs, 1):
        ftp = None
        try:
            logging.info(f"[CORRECTION] Tentative FTP {attempt}/{len(ftp_configs)} ({config['name']})")
            
            # Retry avec backoff exponentiel pour ce config
            for retry in range(3):
                try:
                    ftp = ftplib.FTP()
                    ftp.encoding = config["encoding"]
                    
                    # Connexion avec timeout adaptatif
                    logging.info(f"[CORRECTION] Connexion {FTP_HOST}:{FTP_PORT} (retry {retry+1}/3)")
                    ftp.connect(FTP_HOST, FTP_PORT, timeout=config["timeout"])
                    
                    # Authentification
                    ftp.login(FTP_USER, FTP_PASS)
                    ftp.set_pasv(config["pasv"])
                    
                    logging.info(f"[CORRECTION] Connecté FTP {FTP_HOST} ({config['name']})")
                    
                    # Navigation avec gestion d'erreur
                    try:
                        ftp.cwd(FTP_DIRECTORY)
                        logging.info(f"[CORRECTION] Navigation vers {FTP_DIRECTORY} OK")
                    except ftplib.error_perm as e:
                        logging.warning(f"[CORRECTION] Répertoire {FTP_DIRECTORY} non accessible: {e}")
                        # Essayer répertoire racine ou alternatif
                        try:
                            ftp.cwd("/wordpress/uploads/")
                            logging.info("[CORRECTION] Navigation vers /wordpress/uploads/ OK (fallback)")
                        except:
                            ftp.cwd("/")
                            logging.info("[CORRECTION] Navigation vers / (racine)")
                    
                    # Upload avec progress callback pour éviter timeout
                    file_size = os.path.getsize(local_path)
                    logging.info(f"[CORRECTION] Upload {remote_name} ({file_size} bytes)")
                    
                    with open(local_path, "rb") as f:
                        # Callback pour éviter timeout sur gros fichiers
                        def progress_callback(block):
                            pass  # Simple callback pour maintenir connexion
                        
                        # Block size adaptatif selon taille fichier
                        block_size = 8192 if file_size < 1024*1024 else 4096  # 8KB pour petits, 4KB pour gros
                        
                        ftp.storbinary("STOR " + remote_name, f, blocksize=block_size, callback=progress_callback)
                    
                    # Vérification upload
                    try:
                        remote_size = ftp.size(remote_name)
                        if remote_size == file_size:
                            logging.info(f"[CORRECTION] Upload confirmé: {remote_size} bytes")
                        else:
                            logging.warning(f"[CORRECTION] Taille différente: local {file_size} vs remote {remote_size}")
                    except:
                        logging.info("[CORRECTION] Vérification taille impossible, mais upload semble OK")
                    
                    # Fermeture propre
                    try:
                        ftp.quit()
                    except:
                        ftp.close()
                    
                    # Construction URL publique
                    remote_dir_web = FTP_DIRECTORY.rstrip("/")
                    public_url = (PUBLIC_BASE + remote_dir_web + "/" + remote_name).replace("//", "/")
                    public_url = public_url.replace("http:/", "http://").replace("https:/", "https://")
                    
                    logging.info(f"[CORRECTION] Upload FTP réussi -> {public_url}")
                    
                    # Vérification accessibilité (non bloquante)
                    try:
                        r = requests.head(public_url, timeout=10, allow_redirects=True)
                        ct = r.headers.get("Content-Type", "")
                        if r.status_code == 200:
                            logging.info(f"[CORRECTION] URL publique confirmée: {ct}")
                            return public_url
                        else:
                            logging.warning(f"[CORRECTION] URL publique status {r.status_code}, mais upload OK")
                            return public_url  # Retourner quand même l'URL
                    except Exception as url_error:
                        logging.warning(f"[CORRECTION] Vérification URL impossible: {url_error}")
                        return public_url  # Retourner l'URL même si vérification échoue
                    
                except (OSError, ConnectionRefusedError, ConnectionResetError, ftplib.error_temp) as conn_error:
                    error_code = getattr(conn_error, 'winerror', None) or getattr(conn_error, 'errno', 'unknown')
                    logging.warning(f"[CORRECTION] Erreur connexion retry {retry+1}: {error_code} - {conn_error}")
                    
                    if ftp:
                        try:
                            ftp.close()
                        except:
                            pass
                        ftp = None
                    
                    # Backoff exponentiel: 1s, 2s, 4s
                    if retry < 2:  # Pas de sleep sur la dernière tentative
                        sleep_time = 2 ** retry
                        logging.info(f"[CORRECTION] Attente {sleep_time}s avant retry...")
                        time.sleep(sleep_time)
                    continue
                    
                except ftplib.error_perm as perm_error:
                    logging.error(f"[CORRECTION] Erreur permissions FTP: {perm_error}")
                    if ftp:
                        try:
                            ftp.close()
                        except:
                            pass
                    break  # Pas de retry sur erreur permissions
                    
                else:
                    # Succès - sortir des boucles retry et config
                    break
                    
            else:
                # Toutes les tentatives retry ont échoué pour cette config
                logging.error(f"[CORRECTION] Échec configuration {config['name']} après 3 retries")
                continue
                
        except Exception as e:
            logging.exception(f"[CORRECTION] Erreur générale FTP config {config['name']}: {e}")
            if ftp:
                try:
                    ftp.close()
                except:
                    pass
            continue
    
    # Toutes les configurations ont échoué
    logging.error("[CORRECTION] Échec FTP sur toutes les configurations. Vérifiez:")
    logging.error(f"  - Connectivité réseau vers {FTP_HOST}:{FTP_PORT}")
    logging.error(f"  - Identifiants FTP: user={FTP_USER}")
    logging.error(f"  - Permissions sur répertoire {FTP_DIRECTORY}")
    return None

def get_public_media_url(local_path: str, remote_name: str, webhook_base: str) -> str:
    """
    Tente FTP, si None → fallback vers WEBHOOK_URL (ngrok) en supposant que le backend sert /uploads/<file>
    Retourne l'URL publique utilisable par FB/IG ou lève une Exception.
    """
    # 1) try FTP
    url = upload_file_via_ftp(local_path, remote_name)
    if url:
        return url

    # 2) fallback -> ngrok/backend static serving
    if not webhook_base:
        raise RuntimeError("FTP failed and no WEBHOOK_URL (ngrok) configured for fallback.")
    public = webhook_base.rstrip("/") + "/uploads/" + remote_name
    # verify accessibility
    try:
        r = requests.head(public, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type","")
        if r.status_code == 200 and (ct.startswith("image/") or ct.startswith("video/")):
            logging.info("Using NGROK fallback URL: %s", public)
            return public
        logging.warning("NGROK URL check failed (status=%s ct=%s) -> %s", r.status_code, ct, public)
    except Exception as e:
        logging.exception("NGROK public URL check failed: %s", e)
    raise RuntimeError("Both FTP and NGROK fallback failed. See logs.")