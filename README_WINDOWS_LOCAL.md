# 🎉 Tunnel Instagram Gratuit - Installation Windows Locale

## 🚀 Démarrage Rapide

**Pour lancer l'application localement :**

1. **Double-cliquez sur** `start_local_windows.bat`
2. **Attendez** que tous les services démarrent
3. **Ouvrez** votre navigateur sur `http://localhost:3000`

---

## 🔧 Si vous avez l'erreur JSON

### ❌ Problème
```
Connexion échouée
Erreur: JSON.parse: unexpected character at line 1 column 1 of the JSON data
Endpoint: http://localhost:8001/api/health
```

### ✅ Solution
1. **Lancez** `fix_local_connection.bat` pour diagnostiquer
2. **Vérifiez** que le backend est démarré sur le port 8001
3. **Assurez-vous** que `frontend/.env` contient :
   ```
   REACT_APP_BACKEND_URL=http://localhost:8001
   ```

---

## 📁 Structure des Fichiers

```
📦 Tunnel Instagram Gratuit/
├── 🚀 start_local_windows.bat     ← Script de démarrage principal
├── 🔧 fix_local_connection.bat    ← Diagnostic et correction
├── 🌐 99_start_all_ngrok.bat       ← Votre script ngrok (si existant)
├── 📂 backend/
│   ├── server.py                   ← Serveur FastAPI
│   ├── .env                        ← Configuration backend
│   └── requirements.txt            ← Dépendances Python
├── 📂 frontend/
│   ├── src/App.js                  ← Interface principale
│   ├── .env                        ← Configuration frontend
│   └── package.json                ← Dépendances React
```

---

## 🎯 Configuration Token Manuel

Une fois l'application lancée :

1. **Allez sur** `http://localhost:3000`
2. **Cliquez** sur "Ou utiliser un token manuel"
3. **Obtenez un token** sur https://developers.facebook.com/tools/explorer/
   - **App ID** : `5664227323683118`
   - **Permissions** : `business_management`, `pages_manage_posts`, `instagram_content_publish`
4. **Collez le token** et connectez-vous

---

## 🌐 Configuration Ngrok

### Avec votre script existant
Si vous avez `99_start_all_ngrok.bat`, il sera utilisé automatiquement.

### Sans script ngrok
L'application créera un tunnel automatique avec :
```bash
ngrok http 8001
```

### URL Webhook
Une fois ngrok actif, utilisez l'URL publique pour vos webhooks :
- **Format** : `https://abc123.ngrok.io/api/webhook`
- **Vérification** : Consultez `http://127.0.0.1:4040` pour voir l'URL active

---

## 🛠️ Prérequis

### Logiciels requis
- ✅ **Python 3.8+** 
- ✅ **Node.js 16+**
- ✅ **MongoDB** (démarré)
- ✅ **Ngrok** (dans votre PATH)

### Vérification rapide
```batch
python --version
node --version
mongod --version
ngrok version
```

---

## 🐛 Dépannage

### 🔴 Backend ne démarre pas
```batch
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

### 🔴 Frontend ne se connecte pas
```batch
cd frontend
npm install
npm start
```

### 🔴 MongoDB non démarré
```batch
net start MongoDB
```

### 🔴 Port 8001 occupé
```batch
netstat -ano | findstr :8001
taskkill /F /PID [PID_NUMBER]
```

---

## ✅ Vérification du Bon Fonctionnement

### Tests à effectuer :

1. **Backend Health Check**
   ```
   http://localhost:8001/api/health
   ```
   ✅ Doit retourner du JSON avec `"status": "healthy"`

2. **Frontend Interface**
   ```
   http://localhost:3000
   ```
   ✅ Doit afficher "Tunnel Instagram Gratuit"

3. **Token Manuel**
   ✅ Le bouton "Ou utiliser un token manuel" doit ouvrir un champ de saisie

4. **Ngrok Tunnel**
   ```
   http://127.0.0.1:4040
   ```
   ✅ Doit afficher l'interface ngrok avec l'URL publique

---

## 🎊 Une fois tout configuré

Votre **Tunnel Instagram Gratuit** sera prêt pour :

- 📱 **Publication automatique** sur @logicamp_berger
- 🏪 **Multi-magasins** (gizmobbs, logicantiq, outdoor)
- 🌐 **Webhooks externes** via ngrok
- 🔑 **Connexion par token** Facebook Business Manager

---

## 📞 Support

Si des problèmes persistent :

1. **Lancez** `fix_local_connection.bat` pour un diagnostic complet
2. **Vérifiez** les logs dans les fenêtres de commande ouvertes
3. **Consultez** les URL de test mentionnées ci-dessus

---

**🚀 Bon développement avec votre Tunnel Instagram Gratuit !**