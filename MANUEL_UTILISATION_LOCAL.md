# 📖 Manuel d'Utilisation - FacebookPost Local

## 🚀 Installation Rapide

### Prérequis
- **Python 3.8+** : [Télécharger ici](https://python.org) ⚠️ Cocher "Add to PATH"
- **Node.js 16+** : [Télécharger ici](https://nodejs.org)
- **MongoDB Community** : [Télécharger ici](https://mongodb.com)

### Installation Automatique
1. Ouvrir le dossier `C:\FacebookPost\start\`
2. Double-cliquer sur `01_install_dependencies.bat`
3. Suivre les instructions à l'écran

---

## 🎯 Démarrage Express (Recommandé)

### Option 1 : Démarrage Automatique
```bash
Double-cliquer sur : start\99_start_all.bat
```
✅ Lance tous les services et ouvre l'application à http://localhost:8001

### Option 2 : Démarrage Manuel (3 étapes)
1. `start\02_start_mongodb.bat` - Démarrer MongoDB
2. `start\03_start_backend.bat` - Démarrer le serveur 
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
1. Ouvrir http://localhost:8001
2. Cliquer sur **"Connecter Business Manager"**
3. Autoriser l'accès à vos pages/groupes/Instagram
4. Sélectionner votre Business Manager

### 3. Budget Crédits Emergent (9,80€)
- ✅ **Authentification Facebook** : Gratuite
- ✅ **Stockage local** : Gratuit  
- ✅ **Publications test** : Gratuites
- ⚠️ **Publications réelles** : Consomment des crédits API Facebook

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

### Désactiver le Mode Test
Dans `backend\.env` :
```env
PUBLICATION_TEST_MODE=false
```

### URLs Disponibles
- **Application** : http://localhost:8001
- **API Backend** : http://localhost:8001/api/
- **Diagnostic** : http://localhost:8001/api/health

---

## 🛠️ Dépannage

### MongoDB ne démarre pas
```bash
# Vérifier le port 27017
netstat -an | findstr 27017

# Créer le dossier data manuellement
mkdir C:\FacebookPost\data
```

### Backend ne démarre pas
```bash
# Vérifier les dépendances Python
cd C:\FacebookPost\backend
pip install -r requirements.txt
```

### Page blanche dans le navigateur
1. Vérifier que le backend tourne (port 8001)
2. Reconstruire le frontend :
```bash
cd C:\FacebookPost\frontend
npm run build
```

### Problèmes de token Facebook
1. **Tokens expirés** : Se reconnecter via l'interface
2. **Permissions manquantes** : Vérifier dans Business Manager
3. **Pages non visibles** : Autoriser l'accès dans les paramètres Facebook

---

## 🔍 Vérifications de Santé

### Services Actifs
- **MongoDB** : Port 27017 (fenêtre cmd ouverte)
- **Backend** : Port 8001 (fenêtre cmd ouverte)  
- **Frontend** : Intégré dans le backend

### Test de Fonctionnement
1. Ouvrir http://localhost:8001/api/health
2. Vérifier le statut "healthy" 
3. Contrôler les configurations des stores

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

### Gratuit
- ✅ Installation et configuration
- ✅ Mode test illimité
- ✅ Authentification Facebook
- ✅ Prévisualisation des publications

### Payant (Crédits Facebook API)
- ⚠️ Publications réelles Facebook/Instagram
- ⚠️ Appels API répétés

### Conseils d'Économie
1. **Utiliser le mode test** pendant la configuration
2. **Grouper les publications** pour réduire les appels API
3. **Vérifier les prévisualisations** avant publication
4. **Désactiver les publications automatiques** en développement

---

## 📞 Support

### Logs et Diagnostics
- **Backend** : Affichés dans la fenêtre de commande
- **Frontend** : Console du navigateur (F12)
- **API Health** : http://localhost:8001/api/health

### Fichiers Importants
- `backend\server.py` : Serveur principal
- `backend\.env` : Configuration serveur
- `frontend\.env` : Configuration interface

---

*Version : 1.0 - Usage Local Windows - Budget Optimisé*