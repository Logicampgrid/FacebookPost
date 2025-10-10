# 🔧 PATCH 60 - Instructions d'application pour Windows

## ⚠️ PROBLÈME IDENTIFIÉ
L'erreur "(#100) No permission to publish the video" persiste pour les vidéos Facebook Logicamp car la fonction `get_store_config()` écrase le **FACEBOOK_DIRECT_TOKEN** avec un token dynamique sans permissions vidéo.

## ✅ SOLUTION - PATCH 60

### Fichier à modifier : `/app/backend/server.py`

### Localiser la fonction (lignes 449-467)
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

### Remplacer par (PATCH 60) :
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

## 📋 ÉTAPES D'APPLICATION

1. **Arrêter le serveur backend**
   - Fermer la fenêtre du serveur ou CTRL+C

2. **Ouvrir le fichier**
   ```cmd
   notepad C:\FacebookPost\backend\server.py
   ```
   Ou utiliser votre éditeur préféré (VS Code, Sublime, etc.)

3. **Chercher la fonction** (CTRL+F)
   - Rechercher : `def get_store_config`
   - Aller à la ligne ~449

4. **Appliquer les modifications**
   - Modifier la ligne qui contenait :
     ```python
     if dynamic_config.get("access_token"):
         config["access_token"] = dynamic_config["access_token"]
     ```
   
   - Par :
     ```python
     # PATCH 60: Pour logicamp, JAMAIS écraser access_token (FACEBOOK_DIRECT_TOKEN requis pour vidéos)
     if dynamic_config.get("access_token") and store != "logicamp":
         config["access_token"] = dynamic_config["access_token"]
         log_app(f"🔄 PATCH 60: Token dynamique utilisé pour {store}", "INFO")
     elif store == "logicamp" and dynamic_config.get("access_token"):
         log_app(f"✅ PATCH 60: Token dynamique ignoré pour logicamp - FACEBOOK_DIRECT_TOKEN préservé", "SUCCESS")
     ```

5. **Sauvegarder le fichier**
   - CTRL+S

6. **Redémarrer le serveur backend**
   ```cmd
   cd C:\FacebookPost\backend
   02_start_server_only.bat
   ```

## ✅ VÉRIFICATION

Après redémarrage, dans les logs vous devriez voir :
```
✅ [HH:MM:SS] [WIN] ✅ PATCH 60: Token dynamique ignoré pour logicamp - FACEBOOK_DIRECT_TOKEN préservé
```

Lors d'une publication vidéo logicamp, vous devriez voir :
- ✅ Upload FTP réussi
- ✅ Publication Facebook réussie (plus d'erreur #100)
- ✅ Publication Instagram réussie

## 🎯 RÉSULTAT ATTENDU

- ✅ **Vidéos Facebook Logicamp** : Fonctionnelles avec FACEBOOK_DIRECT_TOKEN
- ✅ **Plus d'erreur (#100)** : "No permission to publish the video" éliminée
- ✅ **Autres stores** : gizmobbs, logicantiq, outdoor continuent de fonctionner normalement

## 📝 NOTE TECHNIQUE

Le PATCH 60 crée une **exception unique** pour le store "logicamp" afin de préserver le FACEBOOK_DIRECT_TOKEN (token utilisateur avec permissions vidéo complètes) même si un token OAuth dynamique existe dans TOKENS.

Cette protection est essentielle car :
1. Les vidéos Facebook nécessitent des permissions CREATE_CONTENT
2. Le FACEBOOK_DIRECT_TOKEN (token utilisateur) a ces permissions
3. Les tokens OAuth de page n'ont généralement pas ces permissions
4. Sans cette protection, le token OAuth écrase le bon token

## 🆘 SUPPORT

Si le problème persiste après application du PATCH 60 :
1. Vérifier que FACEBOOK_DIRECT_TOKEN est bien défini dans `.env`
2. Vérifier que les logs montrent "PATCH 60: Token dynamique ignoré pour logicamp"
3. Vérifier qu'aucun autre code n'utilise directement `STORES["logicamp"]["access_token"]` sans passer par `get_store_config()`
