# 🔧 PATCH 60 + Configuration Store Logicamp

## ⚠️ PROBLÈME IDENTIFIÉ

### Problème 1 : Store "logicamp" manquant
```
❌ [21:41:02] Store inconnu dans webhook: logicamp 
   (disponibles: ['gizmobbs', 'logicantiq', 'outdoor'])
```

### Problème 2 : Token écrasé (quand store existe)
Même si le store "logicamp" existait, la fonction `get_store_config()` écraserait le FACEBOOK_DIRECT_TOKEN avec un token sans permissions vidéo.

---

## ✅ SOLUTION COMPLÈTE

Cette solution comprend **2 modifications** :

### A. Ajouter le store "logicamp" dans STORES
### B. Protéger le token avec PATCH 60

---

## 📋 ÉTAPE 1 : VÉRIFIER LE .ENV

Avant toute modification, vérifier que ces variables existent dans `.env` :

```cmd
notepad C:\FacebookPost\backend\.env
```

**Variables requises pour logicamp** :
```env
# Token utilisateur avec permissions vidéo Facebook
FACEBOOK_DIRECT_TOKEN=EAABwzLixnjY...  # Votre token utilisateur complet

# ID de la page Facebook Logicamp
FB_PAGE_ID_LOGICAMP=174450429258625

# ID du compte Instagram Logicamp
IG_USER_ID_LOGICAMP=17841461492706552
```

⚠️ **IMPORTANT** : Si ces variables manquent, contactez votre administrateur ou récupérez-les depuis Facebook Business Manager.

---

## 📋 ÉTAPE 2 : ARRÊTER LE SERVEUR

```cmd
# Fermer la fenêtre du serveur ou CTRL+C
```

---

## 📋 ÉTAPE 3 : MODIFIER server.py

```cmd
notepad C:\FacebookPost\backend\server.py
```

---

## 🔧 MODIFICATION A : Ajouter le store "logicamp"

### Chercher (CTRL+F) : `STORES = {`

Vous devriez trouver autour de la ligne **200-250** :

```python
STORES = {
    "gizmobbs": {
        "name": "Gizmo BBS",
        "fb_page_id": os.getenv("FB_PAGE_ID_GIZMOBBS"),
        "ig_user_id": os.getenv("IG_USER_ID_GIZMOBBS"),
        "access_token": os.getenv("FB_ACCESS_TOKEN_GIZMOBBS"),
        "business_account_id": os.getenv("BUSINESS_MANAGER_ID_GIZMOBBS", "1715327795564432")
    },
    "logicantiq": {
        "name": "LogicAntiq",
        "fb_page_id": os.getenv("FB_PAGE_ID_LOGICANTIQ"),
        "ig_user_id": os.getenv("IG_USER_ID_LOGICANTIQ"),
        "access_token": os.getenv("FB_ACCESS_TOKEN_LOGICANTIQ")
    },
    "outdoor": {
        "name": "Logicamp Outdoor",
        "fb_page_id": os.getenv("FB_PAGE_ID_OUTDOOR"),
        "ig_user_id": os.getenv("IG_USER_ID_OUTDOOR"),
        "access_token": os.getenv("FB_ACCESS_TOKEN_OUTDOOR")
    }
}
```

### Ajouter le store "logicamp" (APRÈS "outdoor", AVANT la fermeture `}`) :

```python
STORES = {
    "gizmobbs": {
        "name": "Gizmo BBS",
        "fb_page_id": os.getenv("FB_PAGE_ID_GIZMOBBS"),
        "ig_user_id": os.getenv("IG_USER_ID_GIZMOBBS"),
        "access_token": os.getenv("FB_ACCESS_TOKEN_GIZMOBBS"),
        "business_account_id": os.getenv("BUSINESS_MANAGER_ID_GIZMOBBS", "1715327795564432")
    },
    "logicantiq": {
        "name": "LogicAntiq",
        "fb_page_id": os.getenv("FB_PAGE_ID_LOGICANTIQ"),
        "ig_user_id": os.getenv("IG_USER_ID_LOGICANTIQ"),
        "access_token": os.getenv("FB_ACCESS_TOKEN_LOGICANTIQ")
    },
    "outdoor": {
        "name": "Logicamp Outdoor",
        "fb_page_id": os.getenv("FB_PAGE_ID_OUTDOOR"),
        "ig_user_id": os.getenv("IG_USER_ID_OUTDOOR"),
        "access_token": os.getenv("FB_ACCESS_TOKEN_OUTDOOR")
    },
    # PATCH 60: Configuration store Logicamp avec FACEBOOK_DIRECT_TOKEN
    "logicamp": {
        "name": "Logicamp",
        "fb_page_id": os.getenv("FB_PAGE_ID_LOGICAMP"),
        "ig_user_id": os.getenv("IG_USER_ID_LOGICAMP"),
        "access_token": os.getenv("FACEBOOK_DIRECT_TOKEN")  # Token utilisateur avec permissions vidéo
    }
}
```

⚠️ **ATTENTION à la virgule** : Ajoutez une virgule après `}` de "outdoor" si ce n'est pas déjà fait !

---

## 🔧 MODIFICATION B : Protéger le token (PATCH 60)

### Chercher (CTRL+F) : `def get_store_config`

Vous devriez trouver autour de la ligne **449-467** :

### Localiser ce code (AVANT PATCH 60) :

```python
def get_store_config(store: str) -> dict:
    """Récupère la configuration d'un store (tokens dynamiques prioritaires sur statiques)"""
    if store not in STORES:
        raise ValueError(f"Store inconnu: {store}")
    
    # Commencer avec la configuration statique
    config = STORES[store].copy()
    
    # Surcharger avec les tokens dynamiques si disponibles
    if store in TOKENS and TOKENS[store]:
        dynamic_config = TOKENS[store]
        if dynamic_config.get("access_token"):
            config["access_token"] = dynamic_config["access_token"]
        if dynamic_config.get("fb_page_id"):
            config["fb_page_id"] = dynamic_config["fb_page_id"]
        if dynamic_config.get("ig_user_id"):
            config["ig_user_id"] = dynamic_config["ig_user_id"]
    
    return config
```

### Remplacer par (APRÈS PATCH 60) :

```python
def get_store_config(store: str) -> dict:
    """Récupère la configuration d'un store (tokens dynamiques prioritaires sur statiques)"""
    if store not in STORES:
        raise ValueError(f"Store inconnu: {store}")
    
    # Commencer avec la configuration statique
    config = STORES[store].copy()
    
    # Surcharger avec les tokens dynamiques si disponibles
    if store in TOKENS and TOKENS[store]:
        dynamic_config = TOKENS[store]
        # PATCH 60: Pour logicamp, JAMAIS écraser access_token (FACEBOOK_DIRECT_TOKEN requis pour vidéos)
        if dynamic_config.get("access_token") and store != "logicamp":
            config["access_token"] = dynamic_config["access_token"]
            log_app(f"🔄 PATCH 60: Token dynamique utilisé pour {store}", "INFO")
        elif store == "logicamp" and dynamic_config.get("access_token"):
            log_app(f"✅ PATCH 60: Token dynamique ignoré pour logicamp - FACEBOOK_DIRECT_TOKEN préservé", "SUCCESS")
        if dynamic_config.get("fb_page_id"):
            config["fb_page_id"] = dynamic_config["fb_page_id"]
        if dynamic_config.get("ig_user_id"):
            config["ig_user_id"] = dynamic_config["ig_user_id"]
    
    return config
```

---

## 🚀 ÉTAPE 4 : SAUVEGARDER

**CTRL+S** pour sauvegarder le fichier `server.py`

---

## 🚀 ÉTAPE 5 : REDÉMARRER LE SERVEUR

```cmd
cd C:\FacebookPost\backend
02_start_server_only.bat
```

---

## ✅ VÉRIFICATION

### Au démarrage, vous devriez voir :

```
✅ MongoDB connecté avec succès
✅ Application démarrée avec succès!
```

### Lors d'une publication logicamp, vous devriez voir :

```
ℹ️ Publication webhook - Store: logicamp
✅ PATCH 60: Token dynamique ignoré pour logicamp - FACEBOOK_DIRECT_TOKEN préservé
📢 Début publication multi-plateforme pour logicamp sur ['facebook', 'instagram']
✅ Publication Facebook réussie: ID 12345...
✅ Publication Instagram réussie: ID 17890...
```

---

## 🎯 RÉSULTAT ATTENDU

### ✅ Store logicamp fonctionnel :
- Accepte les webhooks pour store "logicamp"
- Plus d'erreur "Store inconnu"

### ✅ Vidéos Facebook logicamp :
- FACEBOOK_DIRECT_TOKEN utilisé (token utilisateur)
- Permissions vidéo complètes (CREATE_CONTENT)
- Plus d'erreur "(#100) No permission to publish the video"

### ✅ Instagram logicamp :
- Publications images fonctionnelles
- Publications vidéos fonctionnelles (avec PATCH 56)

---

## 🆘 DÉPANNAGE

### Erreur "Store inconnu: logicamp"
→ Vérifier que le store "logicamp" est bien ajouté dans STORES (Modification A)
→ Vérifier qu'il n'y a pas d'erreur de syntaxe (virgules manquantes)

### Erreur "(#100) No permission to publish the video"
→ Vérifier que PATCH 60 est appliqué (Modification B)
→ Vérifier que FACEBOOK_DIRECT_TOKEN existe dans `.env`
→ Chercher dans les logs : "✅ PATCH 60: Token dynamique ignoré pour logicamp"

### Variables .env manquantes
→ Ouvrir `.env` et ajouter :
```env
FACEBOOK_DIRECT_TOKEN=votre_token_utilisateur
FB_PAGE_ID_LOGICAMP=174450429258625
IG_USER_ID_LOGICAMP=17841461492706552
```

---

## 📊 RÉCAPITULATIF

| Composant | Avant | Après |
|-----------|-------|-------|
| **Store logicamp** | ❌ Manquant | ✅ Configuré |
| **Token logicamp** | ❌ Écrasé | ✅ Protégé (PATCH 60) |
| **Vidéos Facebook** | ❌ Erreur #100 | ✅ Fonctionnelles |
| **Images Facebook/Instagram** | ✅ OK | ✅ OK |
| **Vidéos Instagram** | ⚠️ Timeout 60s | ✅ OK (avec PATCH 56) |

---

## 🔗 COMPLÉMENTS

Pour corriger les vidéos Instagram (timeout + détection FINISHED), consulter :
→ `/app/PATCH_56_INSTRUCTIONS_WINDOWS.md`

Ensemble, **PATCH 56 + PATCH 60 + Store logicamp** = Système 100% opérationnel ! 🚀
