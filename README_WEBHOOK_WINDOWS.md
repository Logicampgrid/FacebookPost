# 🚀 Facebook Webhook Automation - Windows

## ✅ Corrections appliquées pour fonctionnement en local

### 1. **Backend corrigé (`server.py`)**
- ✅ Endpoint `/api/webhook` supporte **GET** (validation Facebook) et **POST** (messages)
- ✅ GET vérifie `hub.verify_token` et retourne `hub.challenge` comme **string** (pas int)
- ✅ POST parse le JSON et retourne `{"status": "received"}`
- ✅ Gestion d'erreurs robuste (403, 400, 500)

### 2. **Interface graphique Windows (`facebook_webhook_windows_gui.py`)**
- ✅ Détection automatique du backend sur port 8001
- ✅ Lancement ngrok avec récupération URL publique
- ✅ Tests automatiques GET/POST avec validation Facebook
- ✅ Configuration webhook Facebook intégrée
- ✅ Interface GUI avec logs temps réel
- ✅ Logs persistants dans `webhook_log.txt`
- ✅ Compatible Windows 11 + Python 3.11

### 3. **Script batch amélioré (`start_webhook.bat`)**
- ✅ Vérifications Python 3.11+ et ngrok
- ✅ Gestion d'erreurs complète
- ✅ Support Unicode (émojis)
- ✅ Installation automatique dépendances

### 4. **Tests validés (`test_webhook_simple.py`)**
- ✅ Test GET retourne challenge exact
- ✅ Test POST retourne `{"status": "received"}`
- ✅ Commandes curl Windows
- ✅ Gestion d'erreurs avec conseils debug

## 🔧 Installation & Usage

### Prérequis Windows:
```bash
# Python 3.11+
python --version

# Ngrok installé
ngrok version
```

### Configuration:
1. **Placez les fichiers dans `C:\FacebookPost\`**
2. **Configurez vos clés Facebook dans `facebook_webhook_windows_gui.py`:**
   ```python
   self.FACEBOOK_APP_ID = "VOTRE_APP_ID"
   self.FACEBOOK_APP_SECRET = "VOTRE_APP_SECRET"  
   self.FACEBOOK_ACCESS_TOKEN = "VOTRE_ACCESS_TOKEN"
   self.FACEBOOK_PAGE_ID = "VOTRE_PAGE_ID"
   ```

### Lancement:
```batch
# Méthode 1: Double-clic sur le batch
start_webhook.bat

# Méthode 2: Python direct
python facebook_webhook_windows_gui.py

# Méthode 3: Tests uniquement
cd backend
python test_webhook_simple.py
```

## 🧪 Tests automatiques

### Tests locaux (port 8001):
```bash
# GET - Validation Facebook
curl "http://localhost:8001/api/webhook?hub.mode=subscribe&hub.verify_token=mon_token_secret_webhook&hub.challenge=12345"
# Doit retourner: "12345"

# POST - Message webhook  
curl -X POST "http://localhost:8001/api/webhook" ^
  -H "Content-Type: application/json" ^
  -d "{\"object\":\"page\",\"entry\":[{\"messaging\":[{\"sender\":{\"id\":\"test\"},\"message\":{\"text\":\"Hello\"}}]}]}"
# Doit retourner: {"status": "received", "timestamp": "..."}
```

### Configuration Facebook:
```bash
# Commande générée automatiquement par l'interface
curl -X POST "https://graph.facebook.com/v18.0/VOTRE_PAGE_ID/subscriptions" ^
  -d "callback_url=https://VOTRE_URL_NGROK.ngrok-free.app/api/webhook" ^
  -d "verify_token=mon_token_secret_webhook" ^
  -d "fields=messages,messaging_postbacks,messaging_optins" ^
  -d "access_token=VOTRE_ACCESS_TOKEN"
```

## 🛠️ Dépannage

### Backend ne démarre pas:
```bash
# Vérifier les dépendances
cd C:\FacebookPost\backend
pip install -r requirements.txt

# Lancer manuellement
python server.py
```

### Ngrok ne fonctionne pas:
```bash
# Vérifier installation
ngrok version

# Télécharger si nécessaire
# https://ngrok.com/download
```

### Tests échouent:
1. **GET retourne 403**: Vérifiez le token `mon_token_secret_webhook`
2. **GET retourne 500**: Erreur serveur, vérifiez les logs
3. **POST échoue**: Format JSON incorrect
4. **Ngrok inaccessible**: Firewall ou proxy

## 📁 Structure finale:
```
C:\FacebookPost\
├── start_webhook.bat                    # ← Script de lancement
├── facebook_webhook_windows_gui.py      # ← Interface graphique
├── webhook_log.txt                      # ← Logs persistants
├── backend\
│   ├── server.py                        # ← Backend corrigé
│   ├── test_webhook_simple.py           # ← Tests validés
│   ├── requirements.txt                 # ← Dépendances
│   └── ngrok_url.txt                    # ← URL ngrok active
└── README_WEBHOOK_WINDOWS.md            # ← Ce fichier
```

## 🎯 Workflow complet:

1. **Lancer `start_webhook.bat`**
2. **Interface s'ouvre → Clic "🚀 Démarrer Automatisation"**
3. **Backend détecté → Ngrok lancé → Tests réussis**
4. **Choisir "Oui" pour configurer Facebook automatiquement**
5. **✅ Webhook opérationnel!**

---

## 🔑 Points clés des corrections:

### ✅ Challenge Facebook:
- Facebook envoie `hub.challenge=12345`
- Backend doit retourner exactement `"12345"` (string)
- ❌ Avant: `return int(challenge)` → Erreur 500
- ✅ Après: `return challenge` → Succès

### ✅ Gestion d'erreurs:
- Token incorrect → 403 Verification failed
- JSON invalide → 400 Invalid JSON  
- Erreur serveur → 500 avec message détaillé

### ✅ Interface Windows:
- GUI native avec logs temps réel
- Détection automatique processus
- Tests intégrés avec validation
- Configuration Facebook simplifiée

**🎉 Le webhook est maintenant 100% compatible Facebook et prêt pour la production!**