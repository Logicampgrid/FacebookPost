# Configuration Automatique Ngrok Unifiée et Facebook OAuth

## 🎯 AMÉLIORATION : Architecture Ngrok Unifiée

### ✅ URL Ngrok Unique
- **URL Active** : `https://e4de51969ba9.ngrok-free.app`
- **Frontend & Backend** : Servis par la même URL
- **Architecture Simplifiée** : Un seul tunnel ngrok (port 8001)
- **Performance Optimisée** : Pas de CORS, appels API directs

## 🎯 Fonctionnalités Implementées

### ✅ Synchronisation Automatique au Démarrage
- Le backend détecte automatiquement l'URL ngrok active au démarrage
- Synchronisation du fichier `frontend/.env` avec la nouvelle URL
- Configuration automatique des paramètres Facebook OAuth
- Logs détaillés pour suivre le processus

### ✅ Sources de Détection Ngrok (Priorité)
1. **API Ngrok locale** (`http://127.0.0.1:4040/api/tunnels`) - En temps réel
2. **Frontend .env** (`REACT_APP_BACKEND_URL`) - URL configurée manuellement  
3. **Fichier ngrok_url.txt** - Sauvegarde locale

### ✅ Configuration Facebook OAuth Automatique
- Mise à jour automatique des domaines autorisés
- Configuration des URIs de redirection OAuth multiples
- Test de connectivité Facebook
- Validation complète de la configuration

## 🚀 Séquence de Démarrage

```
🚀 Meta Publishing Platform - Architecture Ngrok Unifiée
🔍 Configuration ngrok: URL unique
🌐 Application accessible via : https://e4de51969ba9.ngrok-free.app
🔄 Frontend intégré au backend FastAPI
✅ URL ngrok unifiée configurée
🔧 Configuration automatique Facebook OAuth...
✅ Configuration Facebook OAuth mise à jour complètement (4/4)
🔐 URIs de redirection configurées:
   • https://e4de51969ba9.ngrok-free.app/
   • https://e4de51969ba9.ngrok-free.app/auth/callback
   • https://e4de51969ba9.ngrok-free.app/auth/callb
✅ Facebook OAuth configuré automatiquement
✅ Application démarrée avec succès!
```

## 🛠️ API Endpoints Disponibles

### Status OAuth Complet (URL Unifiée)
```bash
GET https://e4de51969ba9.ngrok-free.app/api/config/oauth-status-complete
```
**Réponse:**
```json
{
  "ngrok_active": true,
  "ngrok_url": "https://e4de51969ba9.ngrok-free.app",
  "redirect_uri": "https://e4de51969ba9.ngrok-free.app/",
  "facebook_config": {
    "app_id_configured": true,
    "app_secret_configured": true,
    "client_token_configured": true,
    "direct_token_configured": true
  },
  "facebook_connectivity": true,
  "oauth_ready": true,
  "auto_config_completed": true,
  "redirect_uris_configured": [
    "https://xxx.ngrok-free.app/",
    "https://xxx.ngrok-free.app/auth/callback",
    "https://xxx.ngrok-free.app/auth/callb"
  ]
}
```

### Configuration OAuth Forcée
```bash
POST /api/config/force-oauth-setup
```
Force la reconfiguration OAuth avec l'URL du frontend `.env`

## 🔧 Script Utilitaire

### Utilisation de `setup_ngrok_oauth.py`

```bash
# Configuration automatique (détection ngrok)
python backend/setup_ngrok_oauth.py

# Configuration forcée (sans ngrok actif)
python backend/setup_ngrok_oauth.py --force

# Configuration avec URL spécifique
python backend/setup_ngrok_oauth.py --url https://nouvelle-url.ngrok-free.app
```

## 📝 Configuration Manuelle

### 1. Nouvelle URL Ngrok
```bash
# 1. Démarrer ngrok
ngrok http 8001

# 2. Copier l'URL générée (ex: https://abc123.ngrok-free.app)

# 3. Mettre à jour frontend/.env
REACT_APP_BACKEND_URL=https://abc123.ngrok-free.app

# 4. Redémarrer le backend pour auto-configuration
sudo supervisorctl restart backend
```

### 2. Configuration Facebook Developer Console

Les paramètres suivants sont configurés **automatiquement** :

- **App Domains**: `abc123.ngrok-free.app`
- **Site URL**: `https://abc123.ngrok-free.app`
- **OAuth Redirect URIs**:
  - `https://abc123.ngrok-free.app/`
  - `https://abc123.ngrok-free.app/auth/callback`
  - `https://abc123.ngrok-free.app/auth/callb`
- **Web Origins**: `https://abc123.ngrok-free.app`

## 🔍 Diagnostics et Résolution de Problèmes

### Vérification du Status
```bash
# Status complet
curl http://localhost:8001/api/config/oauth-status-complete | python -m json.tool

# Status basique
curl http://localhost:8001/api/config/oauth-status | python -m json.tool
```

### Logs Backend
```bash
# Logs en temps réel
tail -f /var/log/supervisor/backend.out.log

# Logs d'erreur
tail -f /var/log/supervisor/backend.err.log
```

### Problèmes Courants

#### ❌ "ngrok_active": false
- **Cause**: Ngrok n'est pas en cours d'exécution
- **Solution**: Démarrer ngrok ou utiliser `--force` avec URL manuelle

#### ❌ "oauth_ready": false  
- **Cause**: Configuration Facebook incomplète
- **Solution**: Vérifier `FACEBOOK_APP_ID` et `FACEBOOK_APP_SECRET` dans `.env`

#### ❌ "facebook_connectivity": false
- **Cause**: Problème de connexion à l'API Facebook
- **Solution**: Vérifier les credentials Facebook et la connectivité internet

## 🎯 Fonctionnalités Avancées

### Synchronisation en Temps Réel
- Le système détecte automatiquement les changements d'URL ngrok
- Met à jour la configuration Facebook en arrière-plan
- Logs détaillés pour le monitoring

### Multi-Sources de Configuration
- Support des URLs ngrok statiques (frontend .env)
- Détection automatique des tunnels actifs
- Fallback intelligent entre les sources

### Sécurité
- Validation des URLs HTTPS pour OAuth
- Test de connectivité avant configuration
- Gestion d'erreurs robuste

## 📊 Monitoring

### Indicateurs de Santé
- ✅ **Ngrok Active**: URL tunnel disponible
- ✅ **Facebook Config**: Credentials configurés  
- ✅ **Facebook Connectivity**: API accessible
- ✅ **OAuth Ready**: Configuration complète
- ✅ **Auto Config Completed**: Processus automatique réussi

### Alertes
- ⚠️ URL ngrok non détectée
- ⚠️ Configuration Facebook partielle
- ❌ Échec de connectivité Facebook
- ❌ Erreur de synchronisation .env

## 🔄 Processus de Mise à Jour

1. **Nouvelle URL Ngrok Détectée**
2. **Synchronisation Frontend .env**
3. **Configuration Facebook OAuth**
4. **Validation et Test**
5. **Confirmation de Réussite**

---

## 💡 Conseils d'Utilisation

- Utiliser le mode `detect` pour la détection automatique
- Vérifier les logs après chaque redémarrage
- Tester la configuration avec `/api/config/oauth-status-complete`
- Utiliser le script utilitaire pour les mises à jour manuelles