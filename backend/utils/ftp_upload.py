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
    Essaye d'uploader en active mode (set_pasv(False)), si échec retente en passive mode.
    Retourne l'URL publique si accessible (status 200 + bon content-type), sinon None.
    """
    for pasv in (False, True):
        ftp = ftplib.FTP()
        try:
            ftp.connect(FTP_HOST, FTP_PORT, timeout=timeout)
            ftp.login(FTP_USER, FTP_PASS)
            ftp.set_pasv(pasv)
            logging.info("Connected to FTP %s (pasv=%s)", FTP_HOST, pasv)
            # navigation
            ftp.cwd(FTP_DIRECTORY)
            with open(local_path, "rb") as f:
                # use binary stor
                ftp.storbinary("STOR " + remote_name, f)
            ftp.quit()
            # public url
            remote_dir_web = FTP_REMOTE_DIR.rstrip("/")
            public_url = (PUBLIC_BASE + remote_dir_web + "/" + remote_name).replace("//", "/")
            public_url = public_url.replace("http:/", "http://").replace("https:/", "https://")
            logging.info("FTP upload OK -> %s", public_url)
            # verify accessibility from server
            try:
                r = requests.head(public_url, timeout=10, allow_redirects=True)
                ct = r.headers.get("Content-Type", "")
                if r.status_code == 200 and (ct.startswith("image/") or ct.startswith("video/")):
                    return public_url
                logging.warning("Public URL check failed (status=%s ct=%s)", r.status_code, ct)
            except Exception as e:
                logging.exception("Failed to HEAD public URL: %s", e)
            return None
        except Exception as e:
            logging.exception("FTP upload failed (pasv=%s): %s", pasv, e)
            try:
                ftp.close()
            except:
                pass
            # continue to try next mode
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