# 🚀 FacebookPost - Version Windows

## 📋 DESCRIPTION

**FacebookPost** est une application complète de publication automatique sur les plateformes Meta (Facebook et Instagram). Cette version Windows offre une installation et un démarrage entièrement automatisés avec tolérance aux pannes.

## ✨ FONCTIONNALITÉS PRINCIPALES

### 🎯 Publication Multi-Plateformes
- **Facebook Pages** : Publication de texte, images, liens avec aperçu automatique
- **Facebook Groupes** : Publication dans vos groupes gérés
- **Instagram Business** : Publication d'images avec légendes optimisées
- **Publication simultanée** : Facebook + Instagram en un seul clic

### 🖼️ Gestion Avancée des Médias
- **Upload drag & drop** : Interface intuitive pour les images
- **Optimisation automatique** : Redimensionnement et compression pour les réseaux sociaux
- **Support multi-formats** : JPG, PNG, GIF, MP4
- **Hébergement FTP** : Upload automatique avec URLs accessibles

### 🔗 Détection Intelligente de Liens
- **Aperçu automatique** : Récupération des métadonnées Open Graph
- **Prévisualisation** : Affichage du titre, description et image
- **Liens cliquables** : Transformation automatique des URLs

### 📊 Monitoring et Historique
- **Historique complet** : Liste de tous les posts avec statuts
- **Webhook History** : Suivi des événements reçus de Facebook
- **Republication** : Possibilité de republier les posts échoués
- **Statistiques** : Métriques par plateforme et boutique

### 🛠️ Configuration Entreprise
- **Multi-boutiques** : Support de 4 boutiques configurées (Logicantiq, LogicampOutdoor, BergerBlancSuisse, GizmoBBS)
- **Business Manager** : Intégration complète avec Facebook Business
- **Mode test/production** : Simulation avant publication réelle
- **Authentification sécurisée** : OAuth Facebook avec permissions granulaires

## 🏗️ ARCHITECTURE TECHNIQUE

### Backend (FastAPI + Python)
- **Serveur asynchrone** : Performance optimisée avec FastAPI
- **Base de données** : MongoDB pour stockage persistant
- **APIs Meta** : Intégration officielle Facebook Graph API v18.0
- **Webhook** : Réception d'événements Facebook en temps réel
- **FTP automatique** : Upload et hébergement d'images

### Frontend (React + Tailwind CSS)
- **Interface moderne** : Design responsive inspiré de Facebook
- **Gestion d'état** : React Hooks pour performance optimale
- **Upload intuitif** : Drag & drop avec prévisualisation
- **Temps réel** : Mise à jour automatique des statuts

### Infrastructure Windows
- **Scripts automatisés** : Démarrage complet en un clic (.bat)
- **Monitoring continu** : Redémarrage automatique en cas de crash
- **Logs détaillés** : Traçabilité complète des opérations
- **Ngrok intégré** : Exposition publique automatique avec une seule URL

## 📁 STRUCTURE WINDOWS

```
C:\FacebookPost\
├── backend\                    # 🐍 Serveur Python FastAPI
│   ├── server_windows.py       # Serveur principal adapté Windows
│   ├── requirements.txt        # Dépendances Python
│   ├── .env                   # Configuration (tokens, IDs, etc.)
│   ├── venv\                  # Environnement virtuel Python
│   ├── uploads\               # Fichiers uploadés et traités
│   └── ngrok_url.txt          # URL ngrok actuelle
├── frontend\                  # ⚛️ Interface React
│   ├── src\                   # Code source React
│   ├── build\                 # Version compilée pour production
│   ├── .env                   # Configuration frontend
│   ├── package.json           # Dépendances Node.js
│   └── node_modules\          # Modules Node.js installés
├── logs\                      # 📋 Logs applicatifs horodatés
├── start_full.bat             # 🚀 Démarrage complet automatique
├── backend_restart.bat        # 🔄 Redémarrage backend seul
├── frontend_restart.bat       # 🎨 Redémarrage frontend seul
├── check_system.bat           # 🔍 Vérification système
├── stop_all.bat              # 🛑 Arrêt propre de tous les services
└── start_full.log            # 📝 Log principal des opérations
```

## 🚀 DÉMARRAGE RAPIDE

### 1. Installation Automatique
```cmd
# Exécuter la vérification système
check_system.bat

# Si tout est OK, démarrer l'application
start_full.bat
```

### 2. Ce qui se passe automatiquement
1. ✅ **Vérification prérequis** : Node.js, Python, MongoDB, ngrok
2. 🗄️ **Démarrage MongoDB** : Automatique si pas déjà lancé
3. 📦 **Installation dépendances** : Python venv + npm install
4. 🏗️ **Build frontend** : Compilation React pour production
5. 🚀 **Lancement backend** : Serveur Python + ngrok
6. 🎨 **Lancement frontend** : Interface React
7. 🌐 **Ouverture navigateur** : URL ngrok automatique
8. 👁️ **Monitoring continu** : Redémarrage automatique si crash

### 3. Première utilisation
1. Le navigateur s'ouvre automatiquement sur votre URL ngrok
2. Connectez-vous avec votre compte Facebook Business
3. Sélectionnez votre Business Manager
4. Choisissez la plateforme (Page/Groupe/Instagram)
5. Créez votre premier post !

## ⚙️ CONFIGURATION

### Tokens Facebook requis (dans `backend\.env`)
```env
# Tokens d'accès pour chaque boutique
FB_ACCESS_TOKEN_LOGICANTIQ=votre_token_ici
FB_ACCESS_TOKEN_LOGICAMPOUTDOOR=votre_token_ici
FB_ACCESS_TOKEN_BERGER=votre_token_ici
FB_ACCESS_TOKEN_GIZMO=votre_token_ici

# IDs des pages Facebook
FB_PAGE_ID_LOGICANTIQ=votre_page_id
FB_PAGE_ID_LOGICAMPOUTDOOR=votre_page_id
FB_PAGE_ID_BERGER=votre_page_id
FB_PAGE_ID_GIZMO=votre_page_id

# IDs des comptes Instagram Business
IG_USER_ID_LOGICANTIQ=votre_ig_id
IG_USER_ID_LOGICAMPOUTDOOR=votre_ig_id
IG_USER_ID_BERGER=votre_ig_id
IG_USER_ID_GIZMO=votre_ig_id
```

### Configuration Webhook Facebook
- **URL** : `https://votre-url-ngrok.com/api/webhook`
- **Token** : `mon_token_secret_webhook_windows`
- **Événements** : `messages`, `feed`, `messaging_postbacks`

## 🛠️ SCRIPTS DE GESTION

### Scripts principaux
- `start_full.bat` - **Démarrage complet** avec installation automatique
- `backend_restart.bat` - **Redémarrage backend** seul (après config)
- `frontend_restart.bat` - **Redémarrage frontend** seul
- `check_system.bat` - **Vérification** prérequis et configuration
- `stop_all.bat` - **Arrêt propre** de tous les services

### Utilisation quotidienne
```cmd
# Démarrage normal
start_full.bat

# Redémarrage après modification config backend
backend_restart.bat

# Redémarrage après modification frontend
frontend_restart.bat

# Vérification système en cas de problème
check_system.bat

# Arrêt propre avant extinction PC
stop_all.bat
```

## 🌐 URLs D'ACCÈS

### URLs principales
- **Application principale** : URL ngrok affichée dans les logs (ex: `https://abc123.ngrok.io`)
- **Backend local** : `http://localhost:8001`
- **Frontend local** : `http://localhost:3000`
- **API Health Check** : `https://votre-url-ngrok.com/api/health`
- **Interface ngrok** : `http://localhost:4040` (dashboard ngrok)

### Endpoints API principaux
- `GET /api/health` - État des services
- `POST /api/webhook` - Réception webhooks Facebook
- `GET /api/ngrok-url` - URL ngrok actuelle
- `POST /api/auth/facebook` - Authentification Facebook
- `POST /api/posts` - Création de posts
- `GET /api/posts` - Liste des posts

## 🔧 TOLÉRANCE AUX PANNES

### Redémarrage automatique
- **Backend crash** : Redémarrage automatique du serveur Python
- **Frontend crash** : Redémarrage automatique du serveur React
- **MongoDB crash** : Redémarrage automatique de la base
- **Ngrok déconnexion** : Reconnexion automatique avec nouvelle URL

### Monitoring continu
- **Health check** : Vérification toutes les 10 secondes
- **Logs détaillés** : Horodatage de toutes les opérations
- **Alertes visuelles** : Affichage des erreurs dans la console
- **Récupération** : Tentatives de reconnexion automatiques

## 📊 LOGS ET MONITORING

### Fichiers de logs
- `start_full.log` - Log principal de tous les scripts
- `logs/backend_*.log` - Logs détaillés du serveur Python
- Console Windows - Logs temps réel pendant l'exécution

### Informations monitorées
- État des services (MongoDB, Backend, Frontend, ngrok)
- URLs actives et changements
- Erreurs et récupérations automatiques
- Statistiques de publication par boutique
- Performance et utilisation mémoire

## 🛡️ SÉCURITÉ ET BONNES PRATIQUES

### Sécurité
- **Tokens sécurisés** : Stockage dans fichiers .env non versionnés
- **HTTPS automatique** : ngrok fournit SSL/TLS automatiquement
- **Webhook signature** : Vérification signature Facebook
- **Permissions minimales** : Tokens avec droits restreints

### Bonnes pratiques
- **Mode test** : Testez toujours en mode simulation d'abord
- **Backup tokens** : Sauvegardez vos tokens en lieu sûr
- **Monitoring** : Surveillez les logs pour détecter anomalies
- **Mise à jour** : Renouvelez les tokens Facebook régulièrement

## 📚 DOCUMENTATION COMPLÈTE

### Guides disponibles
- `GUIDE_INSTALLATION_WINDOWS.md` - Installation pas à pas détaillée
- `MANUEL_UTILISATION_WINDOWS.md` - Manuel utilisateur complet
- `README_WINDOWS.md` - Ce fichier (vue d'ensemble)

### Support technique
1. **Logs** : Consultez `start_full.log` pour diagnostiquer
2. **Health check** : Vérifiez `/api/health` pour l'état des services
3. **Vérification** : Lancez `check_system.bat` pour valider la config
4. **Documentation** : Référez-vous aux guides détaillés

## 🎯 ROADMAP ET ÉVOLUTIONS

### Version actuelle (1.0)
- ✅ Support complet Windows 10/11
- ✅ Scripts de démarrage automatisés
- ✅ Tolérance aux pannes
- ✅ Multi-boutiques (4 boutiques)
- ✅ Publication Facebook + Instagram
- ✅ Interface utilisateur complète
- ✅ Webhook Facebook intégré
- ✅ Ngrok automatique

### Évolutions prévues
- 📱 Support mobile responsive amélioré
- 🔄 Programmation de posts
- 📈 Analytics et statistiques avancées
- 🎨 Templates de posts personnalisables
- 🤖 IA pour optimisation de contenu
- 🔗 Intégration autres plateformes (Twitter, LinkedIn)

---

## 🎉 FÉLICITATIONS !

Vous disposez maintenant d'une plateforme de publication professionnelle complètement automatisée pour Windows !

### Support
- 📧 **Documentation** : Guides complets inclus
- 🔍 **Dépannage** : Scripts de vérification automatiques
- 📋 **Logs** : Traçabilité complète des opérations

**Bonne publication ! 🚀**