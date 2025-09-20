# 🪟 GUIDE COMPLET WINDOWS - FacebookPost Application

## 🎯 DÉMARRAGE SIMPLE - 3 OPTIONS

### 🚀 **OPTION 1 : Démarrage Automatique (RECOMMANDÉ)**
```batch
# Double-cliquez sur le fichier :
start_complete_application.bat

# Le script détecte automatiquement :
# ✅ Si ngrok est installé → Choix local/tunnel
# ✅ Si ngrok n'est pas installé → Mode local automatique
```

### 🏠 **OPTION 2 : Mode Local Forcé**
```batch
# Double-cliquez sur :
start_complete_application_local.bat

# Force le mode local (sans ngrok)
# ✅ Configuration automatique
# ✅ Accès http://localhost:3000
```

### 🌐 **OPTION 3 : Mode Tunnel (si ngrok installé)**
```batch
# Double-cliquez sur :
start_complete_application_tunnel.bat

# Force le mode tunnel avec ngrok
# ✅ URL publique générée
# ✅ Accès depuis Internet
```

---

## ⚙️ PRÉREQUIS WINDOWS

### **Obligatoires :**
- ✅ **Python 3.8+** : https://python.org/downloads
- ✅ **Node.js 16+** : https://nodejs.org/download

### **Optionnel (pour accès externe) :**
- 🌐 **Ngrok** : https://ngrok.com/download

### **Vérification automatique :**
```batch
# Les scripts vérifient automatiquement les prérequis
# Message d'erreur si quelque chose manque
```

---

## 📋 QUE FONT LES SCRIPTS ?

### **start_complete_application.bat** :
1. ✅ Vérifie Python, Node.js, Ngrok
2. 🤔 Détecte le mode optimal
3. ⚙️ Configure les fichiers .env automatiquement
4. 📦 Installe les dépendances si nécessaire
5. 🚀 Lance Backend + Frontend + Ngrok (si choisi)
6. 🌐 Ouvre l'application dans le navigateur

### **Fenêtres ouvertes après démarrage :**
- 🚀 **Backend FastAPI** : API sur port 8001
- ⚛️ **Frontend React** : Interface sur port 3000
- 🌐 **Ngrok Tunnel** : URL publique (si mode tunnel)

---

## 🔧 MODES DE FONCTIONNEMENT

### 🏠 **MODE LOCAL**
- **Accès** : `http://localhost:3000`
- **Avantages** :
  - ✅ Pas de dépendance externe
  - ✅ Démarrage rapide
  - ✅ Stable et fiable
- **Limitations** :
  - ❌ Pas d'accès depuis Internet
  - ❌ Webhooks N8N en local uniquement

### 🌐 **MODE TUNNEL (Ngrok)**
- **Accès** : `https://[random].ngrok-free.app`
- **Avantages** :
  - ✅ Accès depuis Internet
  - ✅ Webhooks externes possibles
  - ✅ Tests en conditions réelles
- **Limitations** :
  - ⚠️ URL change à chaque redémarrage
  - ⚠️ Configuration Facebook à refaire

---

## 🛠️ STRUCTURE DES FICHIERS CRÉÉS

```
/app/
├── start_complete_application.bat          # 🎯 Principal (détection auto)
├── start_complete_application_local.bat    # 🏠 Mode local forcé
├── start_complete_application_tunnel.bat   # 🌐 Mode tunnel forcé
├── windows_helper.py                       # 🐍 Utilitaires Python
└── GUIDE_WINDOWS_COMPLET.md               # 📖 Ce guide
```

---

## 🚀 UTILISATION ÉTAPE PAR ÉTAPE

### **Première utilisation :**

1. **Télécharger/Cloner** le projet FacebookPost
2. **Ouvrir** l'Explorateur Windows dans le dossier du projet
3. **Double-cliquer** sur `start_complete_application.bat`
4. **Suivre** les instructions à l'écran
5. **Attendre** que l'application s'ouvre automatiquement

### **Utilisations suivantes :**
- Double-clic sur le même fichier `.bat`
- L'application se souvient de votre configuration

---

## 📱 URLS D'ACCÈS

### **Mode Local :**
- 🌐 **Application** : http://localhost:3000
- 🔗 **API Backend** : http://localhost:8001
- 🩺 **Health Check** : http://localhost:8001/api/health
- 📡 **Webhook N8N** : http://localhost:8001/api/webhook

### **Mode Tunnel :**
- 🌐 **Application** : https://[random].ngrok-free.app
- 🔗 **API Backend** : https://[random].ngrok-free.app/api/
- 📱 **Interface Ngrok** : http://127.0.0.1:4040
- 📡 **Webhook N8N** : https://[random].ngrok-free.app/api/webhook

---

## 🔐 CONFIGURATION FACEBOOK (Mode Tunnel)

### **Si vous utilisez le mode tunnel, configurez :**

1. **App Domains** : https://developers.facebook.com/apps/[APP_ID]/settings/basic/
   ```
   [random].ngrok-free.app
   ```

2. **OAuth Redirect URIs** : https://developers.facebook.com/apps/[APP_ID]/fb-login/settings/
   ```
   https://[random].ngrok-free.app/auth/callback
   ```

3. **Webhooks** : https://developers.facebook.com/apps/[APP_ID]/webhooks/
   ```
   https://[random].ngrok-free.app/api/webhook
   ```

### **⚠️ Important :**
- L'URL ngrok change à chaque redémarrage
- Vous devez reconfigurer Facebook à chaque fois
- Pour une URL stable, utilisez ngrok payant

---

## 🎯 FONCTIONNALITÉS DISPONIBLES

### ✅ **Publications Facebook :**
- Posts texte + image
- Pages multiples configurées
- Tokens d'accès inclus

### ✅ **Publications Instagram :**
- Posts avec images
- Comptes business configurés
- IDs utilisateur inclus

### ✅ **Interface Utilisateur :**
- React moderne et responsive
- Gestion multi-comptes
- Prévisualisation des posts

### ✅ **API Webhook :**
- Compatible N8N
- Format WooCommerce
- Multi-boutiques supportées

### ✅ **OAuth Facebook :**
- Authentification intégrée
- Gestion des tokens
- Rafraîchissement automatique

---

## 🛑 ARRÊT DE L'APPLICATION

### **Méthode Propre :**
1. Fermer les fenêtres de commande Backend et Frontend
2. Fermer la fenêtre Ngrok (si ouverte)
3. L'application s'arrête automatiquement

### **Méthode Force (si bloqué) :**
```batch
# Ouvrir une nouvelle invite de commande en Admin et taper :
taskkill /f /im python.exe
taskkill /f /im node.exe
taskkill /f /im ngrok.exe
```

---

## 🔧 DÉPANNAGE WINDOWS

### **❌ "Python n'est pas reconnu"**
- Installez Python depuis https://python.org
- ✅ Cochez "Add to PATH" lors de l'installation

### **❌ "Node n'est pas reconnu"**
- Installez Node.js depuis https://nodejs.org
- Redémarrez l'invite de commande après installation

### **❌ "Ngrok n'est pas reconnu"**
- Téléchargez ngrok depuis https://ngrok.com/download
- Décompressez dans C:\Windows\System32 ou ajoutez au PATH

### **❌ "Port 8001 déjà utilisé"**
```batch
# Trouver et arrêter le processus :
netstat -ano | findstr :8001
taskkill /f /pid [PID_NUMBER]
```

### **❌ "L'application ne s'ouvre pas"**
- Vérifiez que les services sont démarrés (fenêtres ouvertes)
- Attendez 30 secondes après le lancement
- Ouvrez manuellement http://localhost:3000

### **❌ "Page blanche dans le navigateur"**
- Vérifiez la console du navigateur (F12)
- Redémarrez l'application complètement
- Vérifiez que le backend répond : http://localhost:8001/api/health

---

## 💡 CONSEILS D'UTILISATION

### **Pour un usage quotidien :**
- Utilisez le mode LOCAL (plus stable)
- Créez un raccourci du .bat sur le bureau
- Configurez les tokens Facebook une seule fois

### **Pour des démonstrations :**
- Utilisez le mode TUNNEL
- Partagez l'URL ngrok générée
- Reconfigurez Facebook si nécessaire

### **Pour la production :**
- Déployez sur un serveur dédié
- Utilisez un nom de domaine fixe
- Configurez SSL/HTTPS

---

## 📞 SUPPORT

### **Si vous rencontrez des problèmes :**

1. **Vérifiez les prérequis** (Python, Node.js)
2. **Consultez les messages d'erreur** dans les fenêtres
3. **Redémarrez** l'application complètement
4. **Testez en mode local** d'abord

### **Fichiers de log :**
- Fenêtre Backend : Erreurs API et base de données
- Fenêtre Frontend : Erreurs interface utilisateur
- Fenêtre Ngrok : Problèmes de tunnel

---

## 🎉 RÉCAPITULATIF

✅ **3 scripts .bat** pour tous les besoins  
✅ **Détection automatique** des prérequis  
✅ **Configuration automatique** des environnements  
✅ **Mode local et tunnel** disponibles  
✅ **Interface moderne** React + FastAPI  
✅ **Publication Facebook/Instagram** prête  
✅ **Webhook N8N** configuré  
✅ **Guide complet** Windows  

**🚀 Double-cliquez sur `start_complete_application.bat` et c'est parti !**