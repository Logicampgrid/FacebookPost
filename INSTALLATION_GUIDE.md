# 🔧 Guide d'Installation FacebookPost - Version Locale Windows

## ⚡ Installation Express (5 minutes)

### 1️⃣ Prérequis Système
Téléchargez et installez dans cet ordre :

1. **Python 3.8+** 
   - 🔗 [python.org](https://python.org)
   - ⚠️ **IMPORTANT** : Cocher "Add Python to PATH" lors de l'installation

2. **Node.js 16+**
   - 🔗 [nodejs.org](https://nodejs.org) 
   - Choisir la version LTS (recommandée)

3. **MongoDB Community**
   - 🔗 [mongodb.com](https://mongodb.com/try/download/community)
   - Installer avec les options par défaut

### 2️⃣ Installation Automatique
```bash
1. Copier le dossier FacebookPost vers C:\FacebookPost
2. Ouvrir C:\FacebookPost\start\
3. Double-cliquer sur "01_install_dependencies.bat"
4. Attendre la fin de l'installation (2-3 minutes)
```

### 3️⃣ Configuration
```bash
1. Copier backend\.env.local vers backend\.env
2. Copier frontend\.env.local vers frontend\.env
3. Double-cliquer sur "99_start_all.bat"
4. L'application s'ouvre à http://localhost:8001
```

---

## 🎯 Premier Lancement

### Démarrage Rapide
```bash
C:\FacebookPost\start\99_start_all.bat
```
✅ Lance automatiquement :
- MongoDB (base de données)
- Backend (serveur API) 
- Frontend (interface web)
- Ouverture du navigateur

### Première Connexion Facebook
1. Page d'accueil : **"Tunnel Instagram Gratuit"**
2. Cliquer : **"Connecter Business Manager"**
3. Se connecter avec votre compte Facebook Business
4. Autoriser l'accès aux pages/groupes/Instagram
5. Sélectionner votre Business Manager

---

## 📁 Structure des Fichiers

```
C:\FacebookPost\
├── start\                     # 🚀 Scripts de lancement
│   ├── 01_install_dependencies.bat
│   ├── 02_start_mongodb.bat
│   ├── 03_start_backend.bat  
│   ├── 04_start_frontend.bat
│   ├── 99_start_all.bat      # ⭐ Démarrage express
│   └── stop_all.bat          # 🛑 Arrêt complet
├── backend\                  # 🔧 Serveur API
│   ├── server.py            # Serveur principal
│   ├── requirements.txt     # Dépendances Python
│   ├── .env.local          # Configuration locale
│   └── uploads\            # Stockage médias
├── frontend\               # 🎨 Interface web
│   ├── src\               # Code React
│   ├── package.json       # Dépendances Node.js
│   └── .env.local        # Configuration locale
├── data\                 # 💾 Base MongoDB (créé auto)
├── MANUEL_UTILISATION_LOCAL.md
└── INSTALLATION_GUIDE.md
```

---

## 🔍 Vérification Installation

### Tests de Fonctionnement
1. **MongoDB** : 
   ```bash
   netstat -an | findstr 27017
   # Doit afficher une ligne avec :27017
   ```

2. **Backend** :
   ```bash
   Ouvrir : http://localhost:8001/api/health
   # Doit afficher : {"status": "healthy"}
   ```

3. **Frontend** :
   ```bash
   Ouvrir : http://localhost:8001
   # Doit afficher la page "Tunnel Instagram"
   ```

---

## ⚠️ Résolution de Problèmes

### Erreur "Python not found"
```bash
1. Réinstaller Python depuis python.org
2. ✅ Cocher "Add Python to PATH"
3. Redémarrer l'invite de commande
4. Tester : python --version
```

### Erreur "Node not found"  
```bash
1. Réinstaller Node.js depuis nodejs.org
2. Choisir la version LTS
3. Redémarrer l'invite de commande
4. Tester : node --version
```

### MongoDB ne démarre pas
```bash
1. Vérifier l'installation MongoDB
2. Créer manuellement : mkdir C:\FacebookPost\data
3. Relancer : start\02_start_mongodb.bat
```

### Port déjà utilisé
```bash
# Arrêter les services existants
start\stop_all.bat

# Ou arrêter manuellement
taskkill /f /im python.exe
taskkill /f /im node.exe  
taskkill /f /im mongod.exe
```

---

## 🎮 Utilisation Quotidienne

### Démarrer l'Application
```bash
Double-clic : C:\FacebookPost\start\99_start_all.bat
```

### Arrêter l'Application
```bash
Double-clic : C:\FacebookPost\start\stop_all.bat
```

### Accéder à l'Interface
```bash
Navigateur : http://localhost:8001
```

---

## 💰 Gestion du Budget (9,80€)

### 🆓 Gratuit (Usage illimité)
- Installation et configuration
- Mode test des publications
- Authentification Facebook
- Prévisualisation des contenus
- Navigation dans l'interface

### 💳 Payant (Consomme crédits)
- Publications réelles sur Facebook/Instagram
- Appels répétés à l'API Facebook
- Upload de médias volumineux

### 🎯 Optimisation Budget
1. **Mode test activé** : `PUBLICATION_TEST_MODE=true` dans backend\.env
2. **Tester avant publier** : Utiliser les prévisualisations
3. **Grouper les actions** : Éviter les appels API multiples
4. **Surveiller les logs** : Vérifier les consommations

---

## 🔄 Mise à Jour

### Mise à jour des Dépendances
```bash
1. cd C:\FacebookPost\backend
2. pip install -r requirements.txt --upgrade

3. cd C:\FacebookPost\frontend  
4. npm update
```

### Sauvegarde Configuration
```bash
Sauvegarder ces fichiers :
- backend\.env (vos tokens)
- data\ (base de données)
```

---

## 📞 Support Technique

### Logs de Diagnostic
- **Backend** : Visible dans la fenêtre de commande
- **Frontend** : F12 > Console dans le navigateur  
- **MongoDB** : Visible dans la fenêtre MongoDB

### URLs de Test
- **Application** : http://localhost:8001
- **API Health** : http://localhost:8001/api/health
- **Webhook Test** : http://localhost:8001/api/webhook

### Commandes Utiles
```bash
# Vérifier les ports utilisés
netstat -an | findstr "8001 27017 3000"

# Vérifier les processus
tasklist | findstr "python node mongod"

# Nettoyer complètement
start\stop_all.bat
rmdir /s C:\FacebookPost\data
```

---

*🚀 Installation réussie ? Consultez MANUEL_UTILISATION_LOCAL.md pour l'utilisation détaillée*