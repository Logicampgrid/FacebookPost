# 🚀 GUIDE D'INSTALLATION FACEBOOKPOST - WINDOWS

## 📋 CHECKLIST PRÉREQUIS

Avant de commencer, assurez-vous d'avoir :

- [ ] **Windows 10 ou 11** (64-bit recommandé)
- [ ] **Droits administrateur** sur votre machine
- [ ] **Connexion Internet** stable
- [ ] **Au moins 2 GB** d'espace disque libre

---

## 🛠️ ÉTAPE 1 : INSTALLATION DES LOGICIELS

### 1.1 MongoDB 8.0

1. **Téléchargement :**
   - Allez sur : https://www.mongodb.com/try/download/community
   - Sélectionnez "Windows x64" et téléchargez

2. **Installation :**
   ```cmd
   # Lancer l'installateur téléchargé
   # Choisir "Complete" installation
   # Cocher "Install MongoDB as a Service"
   # Cocher "Install MongoDB Compass" (optionnel)
   ```

3. **Vérification :**
   ```cmd
   # Ouvrir CMD en tant qu'administrateur
   cd "C:\Program Files\MongoDB\Server\8.0\bin"
   mongod.exe --version
   ```

4. **Création du dossier de données :**
   ```cmd
   mkdir C:\data\db
   ```

### 1.2 Node.js (LTS)

1. **Téléchargement :**
   - Allez sur : https://nodejs.org
   - Téléchargez la version "LTS" (Long Term Support)

2. **Installation :**
   - Lancez l'installateur
   - Acceptez tous les paramètres par défaut
   - ✅ Cochez "Automatically install necessary tools"

3. **Vérification :**
   ```cmd
   node --version
   npm --version
   ```

### 1.3 Python 3.8+

1. **Téléchargement :**
   - Allez sur : https://python.org/downloads
   - Téléchargez la dernière version stable

2. **Installation :**
   - ⚠️ **IMPORTANT** : Cochez "Add Python to PATH"
   - Choisissez "Install Now"

3. **Vérification :**
   ```cmd
   python --version
   pip --version
   ```

### 1.4 ngrok

1. **Téléchargement :**
   - Allez sur : https://ngrok.com/download
   - Téléchargez la version Windows

2. **Installation :**
   ```cmd
   # Extraire le fichier zip
   # Copier ngrok.exe dans C:\Windows\System32\
   # Ou ajouter le dossier au PATH
   ```

3. **Vérification :**
   ```cmd
   ngrok version
   ```

4. **Configuration optionnelle (recommandée) :**
   ```cmd
   # Si vous avez un compte ngrok (gratuit)
   ngrok authtoken VOTRE_TOKEN_ICI
   ```

---

## 📁 ÉTAPE 2 : CRÉATION DE L'ARBORESCENCE

### 2.1 Création des dossiers

```cmd
# Ouvrir CMD en tant qu'administrateur
mkdir C:\FacebookPost
mkdir C:\FacebookPost\backend
mkdir C:\FacebookPost\frontend
mkdir C:\FacebookPost\logs

# Vérification
dir C:\FacebookPost
```

### 2.2 Structure finale attendue

```
C:\FacebookPost\
├── backend\
├── frontend\
├── logs\
├── start_full.bat
├── backend_restart.bat
├── frontend_restart.bat
└── start_full.log (sera créé automatiquement)
```

---

## 📋 ÉTAPE 3 : DÉPLOIEMENT DES FICHIERS

### 3.1 Fichiers backend

Copiez dans `C:\FacebookPost\backend\` :
- `server_windows.py`
- `requirements.txt`
- `.env.windows` → renommer en `.env`

### 3.2 Fichiers frontend

Copiez dans `C:\FacebookPost\frontend\` :
- Tout le contenu du dossier frontend source
- `.env.windows` → renommer en `.env`
- `package.json`

### 3.3 Scripts de démarrage

Copiez dans `C:\FacebookPost\` :
- `start_full.bat`
- `backend_restart.bat`  
- `frontend_restart.bat`

---

## ⚙️ ÉTAPE 4 : CONFIGURATION

### 4.1 Configuration Backend

Éditez `C:\FacebookPost\backend\.env` :

```env
# === TOKENS FACEBOOK (OBLIGATOIRE) ===
FB_ACCESS_TOKEN_LOGICANTIQ=REMPLACER_PAR_VOTRE_TOKEN
FB_ACCESS_TOKEN_LOGICAMPOUTDOOR=REMPLACER_PAR_VOTRE_TOKEN
FB_ACCESS_TOKEN_BERGER=REMPLACER_PAR_VOTRE_TOKEN
FB_ACCESS_TOKEN_GIZMO=REMPLACER_PAR_VOTRE_TOKEN

# === IDS PAGES FACEBOOK ===
FB_PAGE_ID_LOGICANTIQ=REMPLACER_PAR_VOTRE_PAGE_ID
FB_PAGE_ID_LOGICAMPOUTDOOR=REMPLACER_PAR_VOTRE_PAGE_ID
FB_PAGE_ID_BERGER=REMPLACER_PAR_VOTRE_PAGE_ID
FB_PAGE_ID_GIZMO=REMPLACER_PAR_VOTRE_PAGE_ID

# === IDS INSTAGRAM BUSINESS ===
IG_USER_ID_LOGICANTIQ=REMPLACER_PAR_VOTRE_IG_ID
IG_USER_ID_LOGICAMPOUTDOOR=REMPLACER_PAR_VOTRE_IG_ID
IG_USER_ID_BERGER=REMPLACER_PAR_VOTRE_IG_ID
IG_USER_ID_GIZMO=REMPLACER_PAR_VOTRE_IG_ID

# === MODE TEST (RECOMMANDÉ POUR COMMENCER) ===
PUBLICATION_TEST_MODE=true
```

### 4.2 Comment obtenir vos tokens Facebook

1. **Accédez à Facebook Developers :**
   - https://developers.facebook.com/
   - Connectez-vous avec votre compte Facebook Business

2. **Créez une application (si pas déjà fait) :**
   - "Créer une app" → "Business" 
   - Remplissez les informations

3. **Configurez les permissions :**
   - Ajoutez les produits : "Facebook Login", "Pages API", "Instagram API"
   - Permissions requises : `pages_manage_posts`, `instagram_manage_comments`

4. **Générez les tokens :**
   - Outils Graph API Explorer
   - Sélectionnez votre app et les permissions
   - Générez le token d'accès

---

## 🚀 ÉTAPE 5 : PREMIER DÉMARRAGE

### 5.1 Test de démarrage

```cmd
# Ouvrir CMD en tant qu'administrateur
cd C:\FacebookPost
start_full.bat
```

### 5.2 Ce qui se passe automatiquement

1. ✅ **Vérification des prérequis** - Le script vérifie Node.js, Python, MongoDB, ngrok
2. 🗄️ **Démarrage MongoDB** - Lance MongoDB si pas déjà actif
3. 🐍 **Environnement Python** - Crée et active l'environnement virtuel
4. 📦 **Installation dépendances** - Installe automatiquement toutes les dépendances
5. 🏗️ **Build frontend** - Compile l'interface React
6. 🚀 **Lancement backend** - Démarre le serveur Python avec ngrok
7. 🎨 **Lancement frontend** - Démarre l'interface utilisateur
8. 🌐 **Ouverture navigateur** - Ouvre automatiquement l'application

### 5.3 Vérification du succès

**Indicateurs de succès dans la console :**
```
✅ Node.js détecté
✅ Python détecté  
✅ Ngrok détecté
✅ MongoDB détecté
✅ MongoDB démarré avec succès
✅ Backend opérationnel
✅ URL Ngrok obtenue: https://abc123.ngrok.io
✅ Frontend opérationnel
🚀 Ouverture: https://abc123.ngrok.io
```

---

## 🔍 ÉTAPE 6 : VÉRIFICATION ET TESTS

### 6.1 Tests de connectivité

1. **Backend Health Check :**
   ```
   http://localhost:8001/api/health
   ```

2. **Frontend local :**
   ```
   http://localhost:3000
   ```

3. **URL ngrok (principale) :**
   ```
   https://VOTRE_URL_NGROK.com
   ```

### 6.2 Test des services

```cmd
# Vérifier les processus actifs
tasklist | findstr "mongod"
tasklist | findstr "python"  
tasklist | findstr "node"
tasklist | findstr "ngrok"
```

### 6.3 Test de l'interface

1. Ouvrir l'URL ngrok dans le navigateur
2. Se connecter avec Facebook Business
3. Vérifier que les Business Managers sont détectés
4. Tester la création d'un post en mode test

---

## 🛠️ ÉTAPE 7 : DÉPANNAGE INSTALLATION

### 7.1 MongoDB ne démarre pas

**Symptôme :** Erreur "MongoDB crashé"

**Solutions :**
```cmd
# Solution 1 : Démarrer le service Windows
net start MongoDB

# Solution 2 : Démarrage manuel
cd "C:\Program Files\MongoDB\Server\8.0\bin"
mongod.exe --dbpath "C:\data\db"

# Solution 3 : Vérifier les permissions sur C:\data\db
```

### 7.2 ngrok ne se connecte pas

**Symptôme :** "Timeout ngrok"

**Solutions :**
```cmd
# Vérifier ngrok
ngrok version

# Tester manuellement
ngrok http 8001

# Vérifier les processus
tasklist | findstr "ngrok"
```

### 7.3 Port déjà utilisé

**Symptôme :** "Port 8001 occupé"

**Solutions :**
```cmd
# Trouver qui use le port
netstat -ano | findstr :8001

# Tuer le processus (remplacer XXXX par le PID)
taskkill /F /PID XXXX
```

### 7.4 Erreurs Python/Node

**Symptômes :** "Module not found", "Command not found"

**Solutions :**
```cmd
# Backend Python
cd C:\FacebookPost\backend
python -m pip install --upgrade pip
pip install -r requirements.txt

# Frontend Node  
cd C:\FacebookPost\frontend
npm cache clean --force
npm install
```

---

## ✅ ÉTAPE 8 : VALIDATION FINALE

### 8.1 Checklist de validation

- [ ] MongoDB démarre et reste actif
- [ ] Backend répond sur http://localhost:8001/api/health
- [ ] Frontend accessible sur http://localhost:3000
- [ ] ngrok génère une URL publique fonctionnelle
- [ ] L'URL ngrok sert correctement l'interface
- [ ] La connexion Facebook fonctionne
- [ ] Les Business Managers sont détectés
- [ ] Un post test peut être créé (mode simulation)

### 8.2 Configuration webhook Facebook

Une fois tout opérationnel :

1. **URL Webhook :** `https://VOTRE_URL_NGROK.com/api/webhook`
2. **Token de vérification :** `mon_token_secret_webhook_windows`
3. **Méthode :** POST
4. **Événements :** `messages`, `feed`, `messaging_postbacks`

---

## 🎉 FÉLICITATIONS !

Votre installation FacebookPost Windows est maintenant opérationnelle !

### Prochaines étapes :
1. **Configurez vos vrais tokens** Facebook dans `.env`
2. **Testez en mode simulation** avant la production
3. **Configurez les webhooks** Facebook
4. **Passez en mode production** (`PUBLICATION_TEST_MODE=false`)

### Scripts utiles au quotidien :
- **Démarrage complet :** `start_full.bat`
- **Redémarrage backend :** `backend_restart.bat`  
- **Redémarrage frontend :** `frontend_restart.bat`

---

*Pour toute question, consultez le `MANUEL_UTILISATION_WINDOWS.md` ou les logs dans `start_full.log`*