# Guide OAuth Facebook avec Ngrok - Configuration Automatique

## 🎯 Objectif
Ce guide vous explique comment utiliser les nouveaux scripts pour que l'authentification OAuth Facebook fonctionne parfaitement avec ngrok.

## 🚀 Démarrage Rapide

### Méthode 1: Script Tout-en-Un (Recommandé)
```bash
# Exécutez simplement ce script qui fait tout automatiquement
start_oauth_ready.bat
```

### Méthode 2: Étape par Étape
```bash
# 1. Démarrer ngrok
99_start_all_ngrok.bat

# 2. Synchroniser les configurations
python sync_ngrok_config.py

# 3. Démarrer le serveur
python server_windows.py

# 4. Vérifier la configuration
python check_oauth_config.py
```

## 📋 Ce que font les nouveaux scripts

### `99_start_all_ngrok.bat`
- Démarre ngrok sur le port 8001
- Récupère automatiquement l'URL ngrok générée
- Met à jour le fichier `.env` du frontend
- Sauvegarde l'URL pour le backend

### `server_windows.py`
- Démarre le serveur FastAPI avec support ngrok
- Synchronise automatiquement les URLs
- Configure l'environnement pour OAuth

### `sync_ngrok_config.py`
- Synchronise toutes les configurations avec l'URL ngrok active
- Met à jour frontend et backend
- Crée un résumé de configuration

### `check_oauth_config.py`
- Vérifie que tout est correctement configuré
- Teste les endpoints OAuth
- Génère les URLs pour Facebook Developer

## 🔧 Configuration Facebook Developer

Après avoir exécuté les scripts, consultez le fichier `oauth_config_summary.txt` généré automatiquement.

### URLs à configurer dans Facebook Developer Console:

1. **Valid OAuth Redirect URIs:**
   ```
   https://votre-url-ngrok.ngrok.io/
   ```

2. **Webhook URL:**
   ```
   https://votre-url-ngrok.ngrok.io/webhook/facebook
   ```

3. **Permissions requises:**
   - `pages_show_list`
   - `pages_read_engagement` 
   - `instagram_basic`
   - `instagram_content_publish`

## 🔍 Vérification et Tests

### Test rapide des endpoints:
```bash
# Santé du backend
curl https://votre-url-ngrok.ngrok.io/api/health

# Status OAuth
curl https://votre-url-ngrok.ngrok.io/api/config/oauth-status

# Diagnostic Instagram
curl https://votre-url-ngrok.ngrok.io/api/debug/instagram-complete-diagnosis
```

### Interface web:
- Application: `https://votre-url-ngrok.ngrok.io`
- Interface ngrok: `http://127.0.0.1:4040`

## 🔄 Cycle de développement

1. **Démarrage:** `start_oauth_ready.bat`
2. **Développement:** Modifiez votre code normalement
3. **Nouveau tunnel:** Si vous redémarrez ngrok, relancez `sync_ngrok_config.py`
4. **Vérification:** `check_oauth_config.py` pour s'assurer que tout fonctionne

## 🛠️ Dépannage

### Ngrok ne démarre pas
- Vérifiez que ngrok est installé et dans le PATH
- Contrôlez votre token d'authentification ngrok

### URLs non synchronisées
```bash
# Forcer la synchronisation
python sync_ngrok_config.py
```

### Backend non accessible
```bash
# Vérifier les services
python check_oauth_config.py
```

### OAuth Facebook ne fonctionne pas
1. Vérifiez que les URLs sont correctes dans Facebook Developer
2. Contrôlez que `FACEBOOK_APP_ID` et `FACEBOOK_APP_SECRET` sont configurés
3. Testez avec `curl` les endpoints OAuth

## 📁 Fichiers générés automatiquement

- `oauth_config_summary.txt` - Résumé de configuration OAuth
- `frontend/.env.backup` - Sauvegarde de la configuration frontend
- `backend/ngrok_url.txt` - URL ngrok active pour le backend

## 🔐 Sécurité

- Les URLs ngrok changent à chaque redémarrage
- Gardez vos clés Facebook en sécurité dans les fichiers `.env`
- Utilisez le mode test (`PUBLICATION_TEST_MODE=true`) pour les développements

## 💡 Conseils

1. **Gardez les fenêtres ouvertes** pendant le développement
2. **Utilisez `start_oauth_ready.bat`** pour un démarrage simple
3. **Consultez `oauth_config_summary.txt`** pour les URLs à configurer
4. **Exécutez `check_oauth_config.py`** en cas de doute

## 🆘 Support

Si vous rencontrez des problèmes:
1. Exécutez `check_oauth_config.py` pour un diagnostic complet
2. Consultez les logs dans les fenêtres de commande
3. Vérifiez le fichier `oauth_config_summary.txt` pour les URLs actuelles