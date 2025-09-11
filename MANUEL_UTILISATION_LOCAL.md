# 📖 Manuel d'Utilisation - FacebookPost Local Windows

## 🚀 Installation Rapide

### Prérequis
- **Python 3.8+** : [Télécharger ici](https://python.org) ⚠️ Cocher "Add to PATH"
- **Node.js 16+** : [Télécharger ici](https://nodejs.org)
- **MongoDB Community** : [Télécharger ici](https://mongodb.com)
- **Ngrok** (optionnel) : [Télécharger ici](https://ngrok.com) pour accès internet

### Installation Automatique
1. Ouvrir le dossier `C:\FacebookPost\start\`
2. Double-cliquer sur `01_install_dependencies.bat`
3. Suivre les instructions à l'écran

---

## 🎯 Démarrage Express (Recommandé)

### Option 1 : Mode Local (⭐ Recommandé)
```bash
Double-cliquer sur : start\99_start_all.bat
```
✅ Lance tous les services et ouvre l'application à http://localhost:8001
✅ Utilise **server_windows.py** optimisé pour Windows
✅ Économise les crédits (pas de tunnel internet)

### Option 2 : Mode Internet (Avec Ngrok)
```bash
Double-cliquer sur : start\99_start_all_ngrok.bat
```
✅ Lance l'application avec tunnel internet public
✅ Accès depuis n'importe où (mobile, autres PC)
✅ URL sécurisée générée automatiquement

### Option 3 : Démarrage Manuel (3 étapes)
1. `start\02_start_mongodb.bat` - Démarrer MongoDB
2. `start\03_start_backend.bat` - Démarrer le serveur Windows
3. `start\04_start_frontend.bat` - Construire l'interface

---

## 🔧 Configuration Initiale

### 1. Fichiers de Configuration
Copiez les fichiers de configuration :
```
backend\.env.local → backend\.env
frontend\.env.local → frontend\.env
```

### 2. Authentification Facebook Business
1. Ouvrir http://localhost:8001 (ou l'URL ngrok)
2. Cliquer sur **"Connecter Business Manager"**
3. Autoriser l'accès à vos pages/groupes/Instagram
4. Sélectionner votre Business Manager

### 3. Budget Crédits Emergent (9,80€)
- ✅ **Authentification Facebook** : Gratuite
- ✅ **Stockage local** : Gratuit  
- ✅ **Publications test** : Gratuites
- ⚠️ **Publications réelles** : Consomment des crédits API Facebook

---

## 🖥️ Fonctionnalités Version Windows

### 🚀 Optimisations Windows
- **server_windows.py** : Serveur spécialement conçu pour Windows
- **Chemins Windows** : Répertoires C:\FacebookPost\ automatiques
- **Logs structurés** : Tous les logs dans C:\FacebookPost\logs\
- **Auto-création** : Répertoires créés automatiquement
- **Ouverture navigateur** : Automatique avec ngrok

### 📁 Structure Répertoires
```
C:\FacebookPost\
├── data\                    # Base de données MongoDB
├── logs\                    # Logs du serveur (horodatés)
├── backend\
│   ├── server_windows.py    # ⭐ Serveur Windows optimisé
│   ├── uploads\            # Médias téléchargés
│   └── .env                # Configuration locale
├── frontend\
│   ├── build\              # Interface construite
│   └── .env                # Configuration frontend
└── start\                  # Scripts de démarrage
```

---

## 📱 Utilisation

### Première Connexion
1. **Page d'accueil** : "Tunnel Instagram Gratuit"
2. **Cliquer** : "Connecter Business Manager" 
3. **Sélectionner** : Votre Business Manager dans la liste
4. **Choisir** : Page/Groupe/Instagram cible

### Créer une Publication
1. **Onglet** : "Créer un Post"
2. **Saisir** : Texte du message
3. **Ajouter** : Image (optionnel)
4. **Sélectionner** : Plateforme(s) cible
5. **Publier** : En test ou réel

### Fonctionnalités Principales
- **📄 Publications Facebook** : Pages et groupes
- **📷 Publications Instagram** : Avec images obligatoires  
- **🔄 Mode Test** : Pour valider sans publier
- **📊 Historique** : Suivi des publications
- **🏪 Multi-boutiques** : 5 magasins supportés

---

## ⚙️ Configuration Avancée

### Mode Local vs Mode Internet

#### 🏠 Mode Local (99_start_all.bat)
- ✅ **Performance maximale**
- ✅ **Aucun coût de bande passante** 
- ✅ **Sécurité renforcée** (accès localhost uniquement)
- ✅ **Idéal pour** : Tests, développement, usage personnel

#### 🌐 Mode Internet (99_start_all_ngrok.bat)
- ✅ **Accès depuis partout** (mobile, bureau, collaborateurs)
- ✅ **URL publique sécurisée**
- ✅ **Webhooks possibles** (intégrations tierces)
- ✅ **Idéal pour** : Démo, collaboration, webhooks

### Désactiver le Mode Test
Dans `backend\.env` :
```env
PUBLICATION_TEST_MODE=false
```

### URLs Disponibles
- **Application** : http://localhost:8001
- **API Backend** : http://localhost:8001/api/
- **Diagnostic** : http://localhost:8001/api/health
- **URL Ngrok** : http://localhost:8001/api/ngrok-url (si activé)

---

## 🛠️ Dépannage

### MongoDB ne démarre pas
```bash
# Vérifier le service Windows
net start MongoDB

# Créer le répertoire data manuellement
mkdir C:\FacebookPost\data

# Vérifier le port
netstat -an | findstr 27017
```

### Backend ne démarre pas
```bash
# Vérifier Python et les dépendances
python --version
cd C:\FacebookPost\backend
pip install -r requirements.txt

# Vérifier les logs
type C:\FacebookPost\logs\backend_*.log
```

### Frontend ne se charge pas
```bash
# Reconstruire le frontend
cd C:\FacebookPost\frontend
npm run build

# Ou utiliser le script
start\04_start_frontend.bat
```

### Ngrok ne fonctionne pas
```bash
# Installer ngrok
1. Télécharger https://ngrok.com/download
2. Extraire ngrok.exe dans C:\Windows\System32\
3. Redémarrer l'invite de commande
4. Tester : ngrok version
```

### Problèmes de token Facebook
1. **Tokens expirés** : Se reconnecter via l'interface
2. **Permissions manquantes** : Vérifier dans Business Manager
3. **Pages non visibles** : Autoriser l'accès dans les paramètres Facebook

---

## 🔍 Vérifications de Santé

### Services Actifs Windows
- **MongoDB** : Port 27017 (fenêtre cmd minimisée)
- **Backend** : Port 8001 (fenêtre cmd visible avec logs)
- **Ngrok** : URL publique (si activé)
- **Frontend** : Intégré dans le backend

### Test de Fonctionnement
1. Ouvrir http://localhost:8001/api/health
2. Vérifier le statut "healthy" 
3. Contrôler les configurations des stores
4. Vérifier les logs dans C:\FacebookPost\logs\

### Logs et Monitoring
- **Logs serveur** : C:\FacebookPost\logs\backend_YYYYMMDD_HHMMSS.log
- **Logs en temps réel** : Visibles dans la fenêtre backend
- **Diagnostic API** : http://localhost:8001/api/health

---

## 🛑 Arrêt de l'Application

### Arrêt Automatique
```bash
Double-cliquer sur : start\stop_all.bat
```

### Arrêt Manuel  
- Fermer toutes les fenêtres de commande ouvertes
- Ou Ctrl+C dans chaque fenêtre

---

## 💰 Optimisation Budget (9,80€)

### Gratuit (Usage Illimité)
- ✅ Installation et configuration
- ✅ Mode test illimité
- ✅ Authentification Facebook
- ✅ Prévisualisation des publications
- ✅ Mode local (pas de bande passante)

### Payant (Crédits Facebook API)
- ⚠️ Publications réelles Facebook/Instagram
- ⚠️ Appels API répétés
- ⚠️ Webhooks externes (si utilisés)

### Conseils d'Économie
1. **Utiliser le mode test** pendant la configuration
2. **Privilégier le mode local** (99_start_all.bat)
3. **Grouper les publications** pour réduire les appels API
4. **Vérifier les prévisualisations** avant publication
5. **Désactiver les publications automatiques** en développement

---

## 🔄 Maintenance Windows

### Mise à jour des Dépendances
```bash
# Arrêter l'application
start\stop_all.bat

# Mettre à jour
start\01_install_dependencies.bat

# Redémarrer
start\99_start_all.bat
```

### Sauvegarde Configuration
```bash
# Sauvegarder ces éléments importants :
- C:\FacebookPost\backend\.env (tokens et configuration)
- C:\FacebookPost\data\ (base de données)
- C:\FacebookPost\logs\ (historique des actions)
```

### Nettoyage Complet
```bash
# Arrêter tous les services
start\stop_all.bat

# Nettoyer les données (ATTENTION : perte définitive)
rmdir /s C:\FacebookPost\data
rmdir /s C:\FacebookPost\logs

# Réinstaller
start\01_install_dependencies.bat
start\99_start_all.bat
```

---

## 📞 Support

### Logs et Diagnostics
- **Backend** : C:\FacebookPost\logs\backend_*.log
- **Serveur temps réel** : Fenêtre de commande backend
- **Frontend** : Console du navigateur (F12)
- **API Health** : http://localhost:8001/api/health

### Fichiers Importants Version Windows
- `backend\server_windows.py` : Serveur principal Windows
- `backend\.env` : Configuration serveur
- `frontend\.env` : Configuration interface
- `start\99_start_all.bat` : Démarrage automatique

### Diagnostic Rapide
```bash
# Services actifs
tasklist | findstr "python mongod ngrok"

# Ports ouverts
netstat -an | findstr "8001 27017"

# Test API
curl http://localhost:8001/api/health

# Logs récents
type C:\FacebookPost\logs\backend_*.log
```

---

## 🎯 Workflow Recommandé

### Usage Quotidien
1. **Démarrer** : `start\99_start_all.bat`
2. **Naviguer** : http://localhost:8001
3. **Connecter** : Facebook Business Manager
4. **Publier** : Créer des posts
5. **Arrêter** : `start\stop_all.bat`

### Première Installation
1. **Installer prérequis** : Python, Node.js, MongoDB
2. **Configurer** : `start\01_install_dependencies.bat`
3. **Copier configuration** : .env.local → .env
4. **Tester** : `start\99_start_all.bat`
5. **Connecter Facebook** : Via l'interface web

### Mode Production
1. **Désactiver mode test** : `PUBLICATION_TEST_MODE=false`
2. **Utiliser mode local** : Économise les crédits
3. **Sauvegarder régulièrement** : Configuration et données
4. **Surveiller logs** : Pour détecter les problèmes

---

*Version Windows : 1.0 - Utilise server_windows.py optimisé - Budget optimisé*

**🎯 Prêt à utiliser ? Le serveur Windows optimisé vous attend !**