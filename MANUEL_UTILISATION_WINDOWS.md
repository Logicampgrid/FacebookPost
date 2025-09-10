# 📋 MANUEL D'UTILISATION FACEBOOKPOST - VERSION WINDOWS

## 🎯 OBJECTIF
Ce manuel décrit l'installation, la configuration et l'utilisation complète de l'application FacebookPost sur environnement Windows.

---

## 📁 STRUCTURE DE L'APPLICATION

```
C:\FacebookPost\
├── backend\                    # Serveur FastAPI Python
│   ├── server_windows.py       # Serveur principal Windows
│   ├── requirements.txt        # Dépendances Python
│   ├── .env                   # Configuration backend
│   ├── venv\                  # Environnement virtuel Python
│   ├── uploads\               # Fichiers uploadés
│   └── ngrok_url.txt          # URL ngrok actuelle
├── frontend\                  # Interface React
│   ├── src\                   # Code source React
│   ├── build\                 # Version compilée
│   ├── .env                   # Configuration frontend
│   ├── package.json           # Dépendances Node.js
│   └── node_modules\          # Modules Node.js
├── logs\                      # Logs applicatifs
├── start_full.bat             # 🚀 Script de démarrage complet
├── backend_restart.bat        # 🔄 Redémarrage backend seul
├── frontend_restart.bat       # 🎨 Redémarrage frontend seul
└── start_full.log            # 📋 Log principal
```

---

## 🛠️ PRÉREQUIS SYSTÈME

### Logiciels requis :

1. **Windows 10/11** (recommandé)
2. **MongoDB 8.0** 
   - Chemin d'installation : `C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe`
   - Dossier de données : `C:\data\db`
3. **Node.js** (version 16 ou supérieure)
   - Télécharger : https://nodejs.org
4. **Python 3.8+**
   - Télécharger : https://python.org
5. **ngrok** (version gratuite suffisante)
   - Télécharger : https://ngrok.com/download
   - Ajouter à votre PATH système

---

## 🚀 INSTALLATION INITIALE

### Étape 1 : Création de l'arborescence
```cmd
mkdir C:\FacebookPost
mkdir C:\FacebookPost\backend
mkdir C:\FacebookPost\frontend
mkdir C:\FacebookPost\logs
mkdir C:\data\db
```

### Étape 2 : Installation des fichiers
1. Copiez tous les fichiers dans `C:\FacebookPost\`
2. Copiez le contenu backend dans `C:\FacebookPost\backend\`
3. Copiez le contenu frontend dans `C:\FacebookPost\frontend\`

### Étape 3 : Configuration
1. **Backend** : Renommez `.env.windows` en `.env` dans le dossier backend
2. **Frontend** : Renommez `.env.windows` en `.env` dans le dossier frontend
3. Modifiez les tokens dans `backend\.env` (voir section Configuration)

---

## ⚙️ CONFIGURATION

### Configuration Backend (`backend\.env`)

```env
# Tokens Facebook (OBLIGATOIRE)
FB_ACCESS_TOKEN_LOGICANTIQ=VOTRE_TOKEN_ICI
FB_ACCESS_TOKEN_LOGICAMPOUTDOOR=VOTRE_TOKEN_ICI
FB_ACCESS_TOKEN_BERGER=VOTRE_TOKEN_ICI
FB_ACCESS_TOKEN_GIZMO=VOTRE_TOKEN_ICI

# IDs Pages Facebook
FB_PAGE_ID_LOGICANTIQ=VOTRE_PAGE_ID_ICI
FB_PAGE_ID_LOGICAMPOUTDOOR=VOTRE_PAGE_ID_ICI
FB_PAGE_ID_BERGER=VOTRE_PAGE_ID_ICI
FB_PAGE_ID_GIZMO=VOTRE_PAGE_ID_ICI

# IDs Instagram Business
IG_USER_ID_LOGICANTIQ=VOTRE_IG_ID_ICI
IG_USER_ID_LOGICAMPOUTDOOR=VOTRE_IG_ID_ICI
IG_USER_ID_BERGER=VOTRE_IG_ID_ICI
IG_USER_ID_GIZMO=VOTRE_IG_ID_ICI

# Mode test (true = simulation, false = réel)
PUBLICATION_TEST_MODE=true
```

### Configuration Webhook Facebook

1. **URL Webhook** : `https://VOTRE_URL_NGROK.com/api/webhook`
2. **Token de vérification** : `mon_token_secret_webhook_windows`
3. **Événements à souscrire** : 
   - `messages`
   - `messaging_postbacks`
   - `feed`

---

## 🎮 UTILISATION

### Démarrage Complet
```cmd
# Double-cliquez ou exécutez :
C:\FacebookPost\start_full.bat
```

**Ce script fait automatiquement :**
1. ✅ Vérification des prérequis (Node.js, Python, MongoDB, ngrok)
2. 🗄️ Démarrage de MongoDB (si pas déjà lancé)
3. 📦 Installation des dépendances
4. 🚀 Lancement du backend avec ngrok
5. 🎨 Compilation et lancement du frontend
6. 🌐 Ouverture automatique du navigateur
7. 👁️ Monitoring continu avec redémarrage automatique

### Redémarrage Backend Seul
```cmd
C:\FacebookPost\backend_restart.bat
```
Utile après modification de la configuration backend.

### Redémarrage Frontend Seul
```cmd
C:\FacebookPost\frontend_restart.bat
```
Utile après modification du code frontend.

---

## 🌐 ACCÈS À L'APPLICATION

### URLs d'accès :
- **URL principale** : L'URL ngrok affichée dans les logs (ex: `https://abc123.ngrok.io`)
- **Backend local** : `http://localhost:8001`
- **Frontend local** : `http://localhost:3000`
- **API Health** : `https://VOTRE_URL_NGROK.com/api/health`

### Première utilisation :
1. Le navigateur s'ouvre automatiquement sur l'URL ngrok
2. Connectez-vous avec votre compte Facebook Business
3. Sélectionnez votre Business Manager
4. Choisissez la plateforme de publication (Page/Groupe/Instagram)
5. Créez votre premier post !

---

## 📱 FONCTIONNALITÉS

### ✨ Publication Multi-Plateformes
- **Facebook Pages** : Publication de texte, images, liens
- **Facebook Groupes** : Publication dans vos groupes gérés
- **Instagram Business** : Publication d'images avec légendes
- **Publication simultanée** : Facebook + Instagram en un clic

### 🖼️ Gestion des Médias
- **Upload d'images** : Formats JPG, PNG, GIF
- **Optimisation automatique** : Redimensionnement pour les réseaux sociaux
- **Hébergement FTP** : Upload automatique sur serveur externe
- **Aperçu en temps réel** : Prévisualisation avant publication

### 🔗 Détection Automatique de Liens
- **Aperçu de lien** : Récupération automatique du titre, description, image
- **Open Graph** : Support complet des métadonnées
- **Liens cliquables** : Transformation automatique des URLs en liens

### 📊 Historique et Suivi
- **Liste des posts** : Historique complet avec statuts
- **Webhook History** : Suivi des événements reçus
- **Republication** : Possibilité de republier les posts
- **Statistiques** : Nombre de publications par plateforme

### 🛠️ Configuration Avancée
- **Business Manager** : Support multi-comptes
- **Authentification sécurisée** : OAuth Facebook
- **Mode test** : Simulation avant publication réelle
- **Logs détaillés** : Monitoring complet des opérations

---

## 🔧 DÉPANNAGE

### Problèmes courants :

#### 1. MongoDB ne démarre pas
```cmd
# Vérifier le service MongoDB
net start MongoDB

# Ou démarrer manuellement
"C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe" --dbpath "C:\data\db"
```

#### 2. Ngrok ne se connecte pas
```cmd
# Vérifier ngrok
ngrok version

# Tester manuellement
ngrok http 8001
```

#### 3. Port 8001 occupé
```cmd
# Trouver le processus
netstat -ano | findstr :8001

# Tuer le processus (remplacer PID)
taskkill /F /PID XXXX
```

#### 4. Erreur "Module not found"
```cmd
# Backend
cd C:\FacebookPost\backend
pip install -r requirements.txt

# Frontend  
cd C:\FacebookPost\frontend
npm install
```

### Logs de débogage :
- **Log principal** : `C:\FacebookPost\start_full.log`
- **Logs backend** : `C:\FacebookPost\logs\backend_*.log`
- **Console ngrok** : Visible dans la fenêtre de commande

---

## 🛡️ SÉCURITÉ

### Recommandations :
1. **Changez les secrets** dans `.env` pour la production
2. **Tokens d'accès** : Utilisez des tokens avec permissions minimales
3. **Webhook** : Vérifiez toujours la signature Facebook
4. **Firewall** : Configurez pour autoriser ports 8001 et 3000
5. **HTTPS** : ngrok fournit automatiquement HTTPS

### Tokens Facebook :
- Obtenez vos tokens via Facebook Developers
- Configurez les permissions : `pages_manage_posts`, `instagram_manage_comments`
- Renouvelez régulièrement les tokens

---

## 📈 MONITORING

### Surveillance automatique :
- **Redémarrage automatique** : En cas de crash des services
- **Health check** : Vérification toutes les 10 secondes  
- **Logs rotatifs** : Conservation 30 jours par défaut
- **Alertes** : Affichage des erreurs dans les logs

### Métriques disponibles :
- Status des services (MongoDB, Backend, Frontend, ngrok)
- URLs actives
- Nombre de publications par boutique
- Utilisation des API Facebook/Instagram

---

## 🆘 SUPPORT

### En cas de problème :
1. Consultez le fichier `start_full.log`
2. Vérifiez que tous les prérequis sont installés
3. Testez l'URL ngrok directement dans le navigateur
4. Vérifiez la configuration `.env`

### URLs utiles :
- **Documentation Facebook** : https://developers.facebook.com/docs/
- **ngrok Documentation** : https://ngrok.com/docs
- **MongoDB Documentation** : https://docs.mongodb.com/

---

## 📝 CHANGELOG

### Version Windows 1.0
- ✅ Support complet Windows 10/11
- ✅ Scripts de démarrage automatique (.bat)
- ✅ Intégration ngrok avec URL unique
- ✅ Tolérance aux pannes et redémarrage automatique
- ✅ Configuration multi-boutiques
- ✅ Monitoring continu
- ✅ Ouverture automatique du navigateur
- ✅ Logs détaillés avec rotation

---

*Ce manuel est maintenu à jour avec chaque version de l'application. Pour toute question, consultez les logs ou le code source.*