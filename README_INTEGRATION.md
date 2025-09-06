# FacebookPost - Intégration Backend + Frontend 🚀

## ✅ Configuration Réalisée

Votre serveur FastAPI a été configuré avec succès pour combiner backend + frontend :

### 🎯 Objectifs Atteints

1. **✅ Fichiers statiques du frontend servis à la racine `/`**
   - Frontend React accessible sur `http://localhost:8001/`
   - Fichiers CSS/JS servis sur `/static/*`

2. **✅ Endpoints API conservés intacts**
   - Tous les endpoints préfixés avec `/api`
   - `/api/health`, `/api/posts`, `/api/upload`, `/api/webhook`, etc.

3. **✅ CORS activé pour toutes les origines**
   - Header `Access-Control-Allow-Origin: *`
   - Support des requêtes cross-origin

## 🏗️ Architecture

```
FastAPI Server (Port 8001)
├── / (Root)                    -> Frontend React (SPA)
├── /static/*                   -> Fichiers CSS, JS, images
├── /api/health                 -> Status serveur
├── /api/posts                  -> Gestion des posts
├── /api/upload                 -> Upload de fichiers
├── /api/webhook                -> Webhooks Facebook
└── /{any-route}                -> Frontend React (SPA routing)
```

## 🚀 Démarrage

### Méthode 1: Script de démarrage (Recommandé)
```bash
cd /app
python start_server.py
```

### Méthode 2: Avec options
```bash
cd /app
python start_server.py --port 8765 --no-ngrok
```

### Méthode 3: Mode Supervisor (Production)
```bash
sudo supervisorctl restart backend
```

### Méthode 4: Standalone sur port 8765
```bash
cd /app/backend  
python server_standalone.py
```

## 🧪 Tests de Validation

### Test automatique complet
```bash
cd /app
python test_integration.py
```

### Tests manuels
```bash
# Frontend React
curl http://localhost:8001/

# API Health
curl http://localhost:8001/api/health

# Fichiers statiques
curl http://localhost:8001/static/css/main.90f3d3a2.css

# CORS
curl -H "Origin: https://example.com" http://localhost:8001/api/health

# Webhook verification
curl "http://localhost:8001/api/webhook?hub.mode=subscribe&hub.verify_token=mon_token_secret_webhook&hub.challenge=test123"
```

## 📁 Structure des Fichiers

```
/app/
├── backend/
│   ├── server.py                 # ✅ Serveur principal (modifié)
│   ├── server_standalone.py      # 🆕 Version standalone port 8765
│   ├── requirements.txt          # Dépendances Python
│   └── .env                      # Variables d'environnement
├── frontend/
│   ├── build/                    # 🆕 Build de production React
│   │   ├── index.html
│   │   └── static/               # CSS, JS optimisés
│   ├── src/                      # Code source React
│   ├── package.json
│   └── .env                      # Variables frontend
├── start_server.py               # 🆕 Script de démarrage
├── test_integration.py           # 🆕 Tests d'intégration
└── README_INTEGRATION.md         # 📖 Cette documentation
```

## 🔧 Configuration Actuelle

### Backend (server.py)
- **Port**: 8001 (configurable)
- **CORS**: Activé pour `*`
- **Static Files**: `/static` -> `/app/frontend/build/static`
- **Frontend**: Route catch-all pour SPA
- **API Routes**: Préfixe `/api`

### Frontend (.env)
- **REACT_APP_BACKEND_URL**: Configuration automatique
- **Build**: Production optimisé (Webpack + Babel)
- **Routing**: React Router compatible

## 🎉 Résultats des Tests

**✅ 8/8 tests réussis**

1. ✅ API Health endpoint
2. ✅ Frontend React à la racine
3. ✅ Fichiers statiques CSS
4. ✅ Fichiers statiques JS
5. ✅ CORS Headers
6. ✅ SPA Routing
7. ✅ API Posts endpoint
8. ✅ Webhook verification

## 🌐 URLs Disponibles

| URL | Description | Type |
|-----|-------------|------|
| `http://localhost:8001/` | Application React | Frontend |
| `http://localhost:8001/static/*` | CSS, JS, images | Static |
| `http://localhost:8001/api/health` | Status serveur | API |
| `http://localhost:8001/api/posts` | Gestion posts | API |
| `http://localhost:8001/api/upload` | Upload fichiers | API |
| `http://localhost:8001/api/webhook` | Webhooks Facebook | API |

## 🔄 Redémarrage

Si vous modifiez le code:

```bash
# Backend seulement
sudo supervisorctl restart backend

# Rebuild frontend (si changements)
cd /app/frontend && yarn build

# Redémarrage complet
sudo supervisorctl restart all
```

## ✨ Fonctionnalités

- 🌐 **SPA (Single Page Application)**: Toutes les routes non-API servent l'index.html
- 🔗 **API REST**: Endpoints FastAPI préservés
- 📁 **Static Files**: CSS/JS optimisés servis efficacement  
- 🌍 **CORS**: Cross-Origin configuré
- 🔄 **Hot Reload**: Support du développement
- 📱 **Responsive**: Interface mobile-friendly
- 🚀 **Production Ready**: Build optimisé

---

**🎯 Mission Accomplie !** Votre serveur FastAPI combine maintenant parfaitement backend + frontend sur le port 8001.