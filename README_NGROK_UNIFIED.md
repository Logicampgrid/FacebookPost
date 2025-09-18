# 🚀 Meta Publishing Platform - Configuration Ngrok Unifiée

## 📋 Vue d'ensemble

Cette configuration restaure l'approche qui fonctionnait dans les versions précédentes : **un seul tunnel ngrok** qui pointe vers FastAPI, lequel sert à la fois l'API et le build React.

## 🏗️ Architecture

```
Internet (ngrok) → FastAPI (port 8001) → {
    /api/* → Endpoints API
    /*     → Frontend React (build)
}
```

### Avantages de cette approche :
- ✅ **Un seul tunnel ngrok** (plus simple et économique)
- ✅ **URLs cohérentes** (même domaine pour API et frontend)
- ✅ **OAuth Facebook** fonctionne correctement
- ✅ **Pas de problèmes CORS**
- ✅ **Configuration simplifiée**

## 🔧 Fichiers de configuration

### 1. **Serveur unifié** : `/app/backend/server_unified.py`
- FastAPI qui sert l'API ET les fichiers statiques React
- Gestion automatique de ngrok
- Routes API sous `/api/*`
- Frontend servi sur toutes les autres routes

### 2. **Script de démarrage** : `/app/start_unified.py`
- Construit le frontend React
- Démarre ngrok automatiquement
- Met à jour les variables d'environnement
- Lance le serveur unifié

### 3. **Script supervisor** : `/app/start_unified_supervisor.py`
- Version optimisée pour supervisor
- Gestion propre des processus
- Logging approprié

## 🚀 Comment démarrer

### Option 1 : Démarrage interactif
```bash
cd /app
python start_unified.py
```

### Option 2 : Avec supervisor (recommandé)
```bash
cd /app
python start_unified_supervisor.py
```

### Option 3 : Script batch Windows
```batch
start_unified.bat
```

## 📱 URLs de l'application

Une fois démarré, l'application sera accessible via :

- **🌍 URL externe (ngrok)** : `https://[id-unique].ngrok-free.app`
- **🌐 URL locale** : `http://localhost:8001`
- **📱 Interface ngrok** : `http://127.0.0.1:4040`

## 🔑 Configuration OAuth Facebook

La configuration OAuth est **automatiquement synchronisée** avec l'URL ngrok :

- **URL de base** : `https://[id-unique].ngrok-free.app`
- **Redirect URIs configurées** :
  - `https://[id-unique].ngrok-free.app/`
  - `https://[id-unique].ngrok-free.app/auth/callback`
  - `https://[id-unique].ngrok-free.app/auth/callb`

## 📂 Structure des fichiers

```
/app/
├── backend/
│   ├── server_unified.py         # 🎯 Serveur principal unifié
│   ├── database.py              # Base de données MongoDB
│   ├── .env                     # Variables d'environnement backend
│   └── requirements.txt         # Dépendances Python
├── frontend/
│   ├── build/                   # 📦 Build React (servi par FastAPI)
│   ├── .env                     # 🔄 Variables frontend (auto-màj)
│   └── package.json            # Dépendances Node.js
├── start_unified.py            # 🚀 Script de démarrage interactif
├── start_unified_supervisor.py # 🔧 Script pour supervisor
└── start_unified.bat          # 🪟 Script Windows
```

## ⚙️ Variables d'environnement importantes

### Backend `.env`:
```env
# Ngrok
NGROK_AUTH_TOKEN=your_ngrok_token
ENABLE_NGROK=detect

# Facebook OAuth
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret

# MongoDB
MONGO_URL=mongodb://localhost:27017
```

### Frontend `.env` (auto-généré):
```env
REACT_APP_BACKEND_URL=https://[id-unique].ngrok-free.app
```

## 🔍 Endpoints disponibles

### API Endpoints (`/api/*`):
- `GET /api/health` - Statut de l'application
- `GET /api/config/ngrok-status` - Statut ngrok
- `POST /api/auth/facebook` - Authentification Facebook
- `GET /api/posts` - Récupérer les posts
- `POST /api/posts` - Créer un post

### Frontend:
- `/*` - Application React (toutes les routes non-API)

## 🐛 Dépannage

### Ngrok ne démarre pas :
```bash
# Vérifier que ngrok est installé
ngrok version

# Configurer le token
ngrok config add-authtoken YOUR_TOKEN
```

### Frontend non accessible :
```bash
# Reconstruire le frontend
cd /app/frontend
yarn build
```

### API non accessible :
```bash
# Vérifier que le serveur tourne sur le bon port
curl http://localhost:8001/api/health
```

## 🎯 Points clés de cette configuration

1. **Un seul processus** : FastAPI sert tout
2. **Un seul tunnel** : ngrok pointe vers FastAPI uniquement
3. **Synchronisation automatique** : Les .env sont mis à jour automatiquement 
4. **OAuth fonctionnel** : Configuration Facebook automatique
5. **Compatibilité** : Fonctionne avec la configuration existante

## 📞 Support

Cette configuration restaure le fonctionnement stable des versions précédentes. Si vous rencontrez des problèmes :

1. Vérifiez que ngrok est installé et configuré
2. Assurez-vous que le frontend est construit (`yarn build`)
3. Vérifiez les logs pour les erreurs de configuration
4. Testez l'accès local avant l'accès externe

---

✅ **Configuration testée et fonctionnelle** - Prête pour la production !