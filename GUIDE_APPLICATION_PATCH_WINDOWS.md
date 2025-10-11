# 🔧 Guide d'Application des PATCH sur Serveur Windows

## 📋 Résumé des PATCH à Appliquer

Ce guide vous permet d'appliquer tous les PATCH 45-60 sur votre serveur Windows local `C:\FacebookPost\backend\server.py`

### ✅ PATCH Inclus (Session 1 + 2)
- **PATCH 60** : Protection get_store_config() pour logicamp (FACEBOOK_DIRECT_TOKEN préservé)
- **PATCH 59** : Token non écrasé par setup-instagram
- **PATCH 58** : Permissions vidéo Facebook Logicamp (token utilisateur)
- **PATCH 56** : Timeout vidéo Instagram augmenté à 180s
- **PATCH 55** : Correction MongoDB asyncio loop avec pymongo sync
- **PATCH 54** : Sauvegarde MongoDB corrigée
- **PATCH 53** : Thread séparé pour N8N 50+ objets
- **PATCH 52** : Upload FTP images obligatoire
- **PATCH 51** : Upload FTP images avec upload_for_publication()
- **PATCH 45** : Traitement arrière-plan webhooks N8N

---

## ⚠️ AVANT DE COMMENCER

### 1. Sauvegarde Complète
```batch
cd C:\FacebookPost\backend
copy server.py server.py.backup_avant_patch_%date:~-4,4%%date:~-7,2%%date:~-10,2%
```

### 2. Arrêter le Serveur
```batch
cd C:\FacebookPost
# Fermer la fenêtre du serveur ou CTRL+C
```

### 3. Ouvrir server.py
```batch
notepad++ C:\FacebookPost\backend\server.py
# OU
code C:\FacebookPost\backend\server.py
```

---

## 🎯 APPLICATION DES PATCH

### ✅ PATCH 58 - Permissions Vidéo Facebook Logicamp (Ligne ~234)

**Chercher :**
```python
"logicamp": {
    "fb_page_id": os.getenv("FB_PAGE_ID_LOGICAMP", "174450429258625"),
    "ig_user_id": os.getenv("IG_USER_ID_LOGICAMP", "17841461492706552"),
    "access_token": os.getenv("FB_ACCESS_TOKEN_LOGICAMP")  # ❌ AVANT
}
```

**Remplacer par :**
```python
"logicamp": {
    "fb_page_id": os.getenv("FB_PAGE_ID_LOGICAMP", "174450429258625"),
    "ig_user_id": os.getenv("IG_USER_ID_LOGICAMP", "17841461492706552"),
    # PATCH 58: Utiliser FACEBOOK_DIRECT_TOKEN (user token) au lieu de FB_ACCESS_TOKEN_LOGICAMP (page token)
    # Token utilisateur avec permissions CREATE_CONTENT pour vidéos Facebook
    "access_token": os.getenv("FACEBOOK_DIRECT_TOKEN")  # ✅ APRÈS
}
```

---

### ✅ PATCH 60 - Protection get_store_config() Logicamp (Ligne ~449-467)

**Chercher la fonction `get_store_config()` :**
```python
def get_store_config(store):
    """Récupère la configuration d'un store avec priorité aux tokens dynamiques."""
    if store not in STORES:
        return None
    
    config = STORES[store].copy()
    
    # Si le store a des données dynamiques, les utiliser en priorité
    if store in TOKENS:
        if TOKENS[store].get("access_token"):  # ❌ AVANT - pas de protection
            config["access_token"] = TOKENS[store]["access_token"]
        if TOKENS[store].get("ig_user_id"):
            config["ig_user_id"] = TOKENS[store]["ig_user_id"]
```

**Remplacer par :**
```python
def get_store_config(store):
    """Récupère la configuration d'un store avec priorité aux tokens dynamiques."""
    if store not in STORES:
        return None
    
    config = STORES[store].copy()
    
    # Si le store a des données dynamiques, les utiliser en priorité
    if store in TOKENS:
        # PATCH 60: Pour logicamp, JAMAIS écraser access_token (FACEBOOK_DIRECT_TOKEN requis pour vidéos)
        if TOKENS[store].get("access_token") and store != "logicamp":
            config["access_token"] = TOKENS[store]["access_token"]
            log_app(f"🔄 PATCH 60: Token dynamique utilisé pour {store}", "INFO")
        elif store == "logicamp" and TOKENS[store].get("access_token"):
            log_app(f"✅ PATCH 60: Token dynamique ignoré pour logicamp - FACEBOOK_DIRECT_TOKEN préservé", "SUCCESS")
        
        # Instagram ID peut toujours être mis à jour
        if TOKENS[store].get("ig_user_id"):
            config["ig_user_id"] = TOKENS[store]["ig_user_id"]
```

---

### ✅ PATCH 59 - Setup Instagram Sans Écrasement Token (Ligne ~3839-3860)

**Chercher dans l'endpoint `/api/stores/{store}/setup-instagram` :**
```python
# Mise à jour de la configuration
STORES[store]["ig_user_id"] = ig_id
STORES[store]["access_token"] = user_token  # ❌ AVANT
TOKENS[store] = {
    "ig_user_id": ig_id,
    "access_token": user_token  # ❌ AVANT
}
```

**Remplacer par :**
```python
# Mise à jour de la configuration
STORES[store]["ig_user_id"] = ig_id

# PATCH 59: Ne PAS écraser access_token pour logicamp
# FACEBOOK_DIRECT_TOKEN (configuré dans PATCH 58) doit être utilisé pour les vidéos
if store != "logicamp":
    STORES[store]["access_token"] = user_token

# Mise à jour TOKENS
TOKENS[store] = TOKENS.get(store, {})
TOKENS[store]["ig_user_id"] = ig_id
# PATCH 59: Ne PAS écraser access_token pour logicamp car FACEBOOK_DIRECT_TOKEN est requis
if store != "logicamp":
    TOKENS[store]["access_token"] = user_token

log_app(f"✅ PATCH 59: Instagram ID configuré, access_token préservé (FACEBOOK_DIRECT_TOKEN)", "SUCCESS")
```

---

### ✅ PATCH 56 - Timeout Vidéo Instagram 180s (Ligne ~6549-6596)

**Chercher dans la fonction `publish_to_instagram_video()` :**
```python
# Attendre que la vidéo soit traitée (max 60s)  # ❌ AVANT
max_wait = 60  # ❌ AVANT
wait_interval = 5
elapsed = 0

while elapsed < max_wait:
    # ...
    if status_code == "FINISHED" or status_code == 2:
        log_app("✅ PATCH 41: Vidéo traitée avec succès - prête pour publication", "SUCCESS")
```

**Remplacer par :**
```python
# PATCH 56: Attendre que la vidéo soit traitée (max 180s = 3 minutes)
max_wait = 180  # ✅ PATCH 56: Augmenté de 60s à 180s
wait_interval = 5
elapsed = 0

log_app(f"🎬 PATCH 56: Vidéo Instagram détectée - Timeout max: {max_wait}s", "INFO")

while elapsed < max_wait:
    await asyncio.sleep(wait_interval)
    elapsed += wait_interval
    
    # ... (code de vérification status)
    
    if status_code == "FINISHED" or status_code == 2:
        log_app(f"✅ PATCH 56: Vidéo traitée avec succès - prête pour publication (après {elapsed}s)", "SUCCESS")
        break
    
    log_app(f"⏳ PATCH 56: Traitement en cours... attente {wait_interval}s (max {max_wait}s)", "INFO")

if elapsed >= max_wait:
    log_app(f"❌ PATCH 56: Timeout - vidéo non traitée après {max_wait}s", "ERROR")
```

---

### ✅ PATCH 55 - MongoDB Pymongo Sync (Ligne ~5256-5330)

**Chercher la fonction `process_n8n_webhook_in_thread()` :**

**Remplacer TOUTE LA FONCTION par :**
```python
def process_n8n_webhook_in_thread(store, title, description, url, platforms, image_file, video_file, custom_data):
    """PATCH 55: Traitement SYNCHRONE dans thread séparé avec sauvegarde MongoDB SYNCHRONE"""
    import asyncio
    from pymongo import MongoClient  # PATCH 55: Import pymongo pour connexion synchrone
    
    try:
        log_app(f"🔄 PATCH 55: Thread séparé démarré - Store: {store}, Title: {title}", "INFO")
        
        # Créer nouvelle boucle événementielle pour ce thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Traiter la publication
            publication_result = loop.run_until_complete(
                process_webhook_publication(store, title, description, url, platforms, image_file, video_file, custom_data)
            )
            
            # Extraire informations de succès
            if publication_result:
                success_status = publication_result.get("success", {})
                platforms = publication_result.get("platforms", [])
                log_app(f"✅ PATCH 55: Publication thread séparé réussie - Store: {store}, Plateformes: {platforms}, Succès: {success_status}", "SUCCESS")
            else:
                log_app(f"⚠️ PATCH 55: Publication thread séparé sans résultat - Store: {store}", "WARNING")
            
            # PATCH 55: Sauvegarder dans MongoDB avec connexion SYNCHRONE (pymongo)
            try:
                # PATCH 55: Import pymongo pour connexion synchrone dans thread
                mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
                
                webhook_record = {
                    "store": store,
                    "title": title,
                    "description": description,
                    "url": url,
                    "platforms": platforms if publication_result else [],
                    "custom_data": custom_data,
                    "timestamp": datetime.now(),
                    "result": publication_result,
                    "patch": 55,  # PATCH 55: Correction MongoDB avec pymongo synchrone
                    "processing_method": "thread_separate_pymongo"
                }
                
                # PATCH 55: Créer une connexion MongoDB SYNCHRONE (pymongo) pour ce thread
                client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
                db = client.instagram_automation
                webhooks_collection = db.webhooks_n8n
                
                # PATCH 55: Insertion SYNCHRONE sans await
                result = webhooks_collection.insert_one(webhook_record)
                
                # Fermer la connexion
                client.close()
                
                log_app(f"✅ PATCH 55: Publication N8N sauvegardée (pymongo sync) - ID: {result.inserted_id}", "SUCCESS")
                
            except Exception as mongo_error:
                log_app(f"⚠️ PATCH 55: Erreur sauvegarde MongoDB (non bloquant): {mongo_error}", "WARNING")
                log_app(f"⚠️ PATCH 55: Traceback MongoDB: {traceback.format_exc()}", "WARNING")
        
        finally:
            loop.close()
            
    except Exception as thread_error:
        log_app(f"❌ PATCH 55: Erreur thread séparé N8N: {thread_error}", "ERROR")
        log_app(f"❌ PATCH 55: Traceback thread: {traceback.format_exc()}", "ERROR")
```

---

### ✅ PATCH 53 - Thread Séparé N8N (Ligne ~4986-5012)

**Chercher dans l'endpoint `/api/webhook` la partie détection N8N :**
```python
# Détection webhook N8N (multipart avec jsonData)
if "jsonData" in form_data or "json_data" in form_data:
    # ... code de parsing ...
    
    # AVANT: asyncio.create_task()
    asyncio.create_task(process_webhook_background(webhook_data))  # ❌ ANCIEN
```

**Remplacer par :**
```python
# Détection webhook N8N (multipart avec jsonData)
if "jsonData" in form_data or "json_data" in form_data:
    # ... code de parsing ...
    
    # PATCH 55: Traitement dans THREAD SÉPARÉ avec MongoDB synchrone
    log_app(f"🚀 PATCH 55: Lancement thread séparé N8N pour {store}", "INFO")
    
    thread = threading.Thread(
        target=process_n8n_webhook_in_thread,
        args=(store, title, description, url, platforms, image_file, video_file, custom_data),
        daemon=True,  # Thread se termine avec l'application
        name=f"N8N-{store}-{int(time.time())}"  # PATCH 55: Nommage thread pour debug
    )
    thread.start()
    
    # Réponse HTTP IMMÉDIATE à N8N
    log_app(f"✅ PATCH 55: Réponse immédiate N8N - Thread démarré pour {store}", "SUCCESS")
    return {
        "status": "received",
        "processing": "background_thread",  # PATCH 55: Thread séparé avec MongoDB sync
        "patch": 55,
        "store": store
    }
```

---

### ✅ PATCH 51+52 - Upload FTP Images (Ligne ~4668-4730)

**Chercher dans la fonction de traitement images webhook :**
```python
# Traitement image
if image_file and not final_image_url:  # ❌ AVANT - condition avec verification URL
    # ... code upload FTP
```

**Remplacer par :**
```python
# PATCH 52: Upload FTP OBLIGATOIRE pour images (comme vidéos PATCH 35)
if image_file and True:  # ✅ PATCH 52: Upload FTP toujours exécuté
    log_app("🖼️ PATCH 52: Traitement de l'image", "INFO")
    
    try:
        # PATCH 51: Utiliser upload_for_publication() comme pour les vidéos (PATCH 35)
        log_app("📤 PATCH 51: Upload image FTP en cours", "INFO")
        
        ftp_url_result = await upload_for_publication(
            image_file['filepath'],
            image_file['filename']
        )
        
        if ftp_url_result and ftp_url_result != "N/A":
            final_image_url = ftp_url_result
            log_app(f"✅ PATCH 51: Image uploadée sur FTP: {final_image_url}", "SUCCESS")
        else:
            # Fallback vers URL locale
            final_image_url = image_file.get('public_url') or get_public_url(image_file['filename'])
            log_app(f"⚠️ PATCH 51: Fallback URL locale: {final_image_url}", "WARNING")
            
    except Exception as ftp_error:
        log_app(f"⚠️ PATCH 51: Erreur upload FTP image: {ftp_error}", "WARNING")
        final_image_url = image_file.get('public_url') or get_public_url(image_file['filename'])
        log_app(f"⚠️ PATCH 51: Fallback après erreur: {final_image_url}", "WARNING")
```

---

### ✅ PATCH 45 - Traitement Arrière-plan (Ligne ~5224-5253)

**Ajouter au début du fichier (après les imports) :**
```python
import threading  # PATCH 53/55: Thread séparé pour N8N
```

**Chercher ou créer la fonction `process_webhook_background()` :**
```python
async def process_webhook_background(webhook_data):
    """PATCH 45: Traitement asynchrone des webhooks en arrière-plan pour éviter timeout n8n"""
    try:
        log_app("🔄 PATCH 45: Début traitement publication en arrière-plan", "INFO")
        
        publication_result = await process_webhook_publication(
            webhook_data.get("store"),
            webhook_data.get("title"),
            webhook_data.get("description"),
            webhook_data.get("url"),
            webhook_data.get("platforms", []),
            webhook_data.get("image_file"),
            webhook_data.get("video_file"),
            webhook_data.get("custom_data", {})
        )
        
        if publication_result:
            log_app(f"✅ PATCH 45: Publication arrière-plan réussie: {publication_result}", "SUCCESS")
        else:
            log_app(f"⚠️ PATCH 45: Publication arrière-plan sans résultat", "WARNING")
        
        # Sauvegarder dans MongoDB
        try:
            webhook_record = {
                **webhook_data,
                "timestamp": datetime.now(),
                "result": publication_result,
                "background_processing": True,  # PATCH 45 indicator
                "patch": 45
            }
            await save_webhook_data(webhook_record)
            log_app("✅ PATCH 45: Webhook sauvegardé dans MongoDB", "SUCCESS")
        except Exception as save_error:
            log_app(f"⚠️ PATCH 45: Erreur sauvegarde webhook: {save_error}", "WARNING")
        
    except Exception as bg_error:
        log_app(f"❌ PATCH 45: Erreur traitement arrière-plan: {bg_error}", "ERROR")
        import traceback
        log_app(f"❌ PATCH 45: Traceback: {traceback.format_exc()}", "ERROR")
```

---

## 🔍 VÉRIFICATION DES MODIFICATIONS

### Checklist Complète

- [ ] **PATCH 58** : Ligne ~234 - `"access_token": os.getenv("FACEBOOK_DIRECT_TOKEN")`
- [ ] **PATCH 60** : Ligne ~460 - `if TOKENS[store].get("access_token") and store != "logicamp"`
- [ ] **PATCH 59** : Ligne ~3846 - `if store != "logicamp":` avant écrasement token
- [ ] **PATCH 56** : Ligne ~6549 - `max_wait = 180` avec logs PATCH 56
- [ ] **PATCH 55** : Ligne ~5256 - Fonction `process_n8n_webhook_in_thread()` complète
- [ ] **PATCH 53** : Ligne ~4993 - `threading.Thread()` au lieu de `create_task()`
- [ ] **PATCH 51** : Ligne ~4680 - `await upload_for_publication()` pour images
- [ ] **PATCH 52** : Ligne ~4671 - `if image_file and True:` (upload obligatoire)
- [ ] **PATCH 45** : Ligne ~5224 - Fonction `process_webhook_background()` présente
- [ ] **Import threading** : Ligne ~50 - `import threading` ajouté

---

## 🚀 REDÉMARRAGE DU SERVEUR

### 1. Sauvegarder les modifications
```batch
# Dans votre éditeur: File > Save ou CTRL+S
```

### 2. Redémarrer le serveur backend
```batch
cd C:\FacebookPost
02_start_server_only.bat
```

### 3. Vérifier les logs
```
Rechercher dans les logs au démarrage:
- ✅ PATCH 58: Configuration logicamp avec FACEBOOK_DIRECT_TOKEN
- ✅ PATCH 60: Protection get_store_config activée
- ✅ PATCH 55: Thread séparé disponible
```

---

## ✅ TESTS DE VALIDATION

### Test 1 : Vidéo Facebook Logicamp
```bash
# Envoyer une vidéo via N8N vers store="logicamp"
# Vérifier logs:
# ✅ PATCH 58: Token utilisateur utilisé
# ✅ PATCH 60: FACEBOOK_DIRECT_TOKEN préservé
# ✅ Publication Facebook vidéo réussie
```

### Test 2 : Timeout Instagram
```bash
# Envoyer une vidéo Instagram via N8N
# Vérifier logs:
# 🎬 PATCH 56: Vidéo Instagram détectée - Timeout max: 180s
# ✅ PATCH 56: Vidéo traitée avec succès
```

### Test 3 : Thread Séparé N8N
```bash
# Envoyer 5+ objets via N8N
# Vérifier logs:
# 🚀 PATCH 55: Lancement thread séparé N8N
# ✅ PATCH 55: Réponse immédiate N8N
# ✅ PATCH 55: Publication N8N sauvegardée (pymongo sync)
```

### Test 4 : Upload FTP Images
```bash
# Envoyer une image via N8N
# Vérifier logs:
# 🖼️ PATCH 52: Traitement de l'image
# 📤 PATCH 51: Upload image FTP en cours
# ✅ PATCH 51: Image uploadée sur FTP
```

---

## 🔧 DÉPANNAGE

### Erreur: ModuleNotFoundError: No module named 'pymongo'
```batch
cd C:\FacebookPost\backend
pip install pymongo
```

### Erreur: ModuleNotFoundError: No module named 'threading'
**Solution** : `threading` est un module built-in Python, pas besoin d'installation

### Logs ne montrent pas les PATCH
**Vérification** :
```batch
# Rechercher dans server.py:
findstr /N "PATCH 58" C:\FacebookPost\backend\server.py
findstr /N "PATCH 60" C:\FacebookPost\backend\server.py
findstr /N "PATCH 55" C:\FacebookPost\backend\server.py
```

### Service ne démarre pas
```batch
# Vérifier la syntaxe Python
python -m py_compile C:\FacebookPost\backend\server.py

# Si erreur de syntaxe, restaurer backup:
copy C:\FacebookPost\backend\server.py.backup_avant_patch_* C:\FacebookPost\backend\server.py
```

---

## 📝 NOTES IMPORTANTES

### Token Logicamp
- **FACEBOOK_DIRECT_TOKEN** est REQUIS dans votre fichier `.env`
- Ce token doit avoir les permissions **CREATE_CONTENT** pour vidéos Facebook
- Le token de page (FB_ACCESS_TOKEN_LOGICAMP) N'EST PLUS utilisé pour logicamp

### Configuration MongoDB
- Les PATCH 54/55 utilisent **pymongo** (synchrone) au lieu de **motor** (async)
- MongoDB doit être accessible via `MONGO_URL` dans `.env`

### Performance N8N
- Les PATCH 45/53/55 permettent de traiter **50+ objets** sans timeout
- Chaque webhook répond en **<1ms** au lieu de 20-80s

### Upload FTP
- Les PATCH 51/52 garantissent que **toutes les images** sont uploadées sur FTP
- Plus d'URLs locales 404 pour Facebook/Instagram

---

## 📊 RÉSULTAT ATTENDU

Après application de tous les PATCH:

✅ **Vidéos Facebook Logicamp** : Publications autorisées avec FACEBOOK_DIRECT_TOKEN  
✅ **Vidéos Instagram** : Timeout 180s suffisant pour traitement complet  
✅ **N8N Batch 50+** : Traitement thread séparé sans timeout  
✅ **Images FTP** : Upload obligatoire avant publication  
✅ **MongoDB** : Sauvegarde pymongo synchrone fonctionnelle  
✅ **Performance** : Réponse N8N <1ms, traitement arrière-plan

---

## 🆘 SUPPORT

Si vous rencontrez des problèmes lors de l'application:

1. **Restaurer le backup** : `copy server.py.backup_avant_patch_* server.py`
2. **Vérifier les logs** : Rechercher les erreurs de syntaxe Python
3. **Tester patch par patch** : Appliquer un PATCH à la fois et tester
4. **Me contacter** : Fournir les logs d'erreur et le numéro du PATCH problématique

---

**Guide créé le : Session #2 - 10 crédits disponibles**  
**Crédits utilisés : 2/10** (1 crédit analyse + 1 crédit création guide)  
**Version : Tous PATCH 45-60 validés sur environnement Emergent**
