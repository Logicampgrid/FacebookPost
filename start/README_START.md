# 🚀 Scripts de Démarrage FacebookPost - Version Windows

> Répertoire contenant tous les scripts .bat optimisés pour Windows avec server_windows.py

## ⚡ Utilisation Rapide

### 🏠 Mode Local (Recommandé)
```bash
99_start_all.bat            # Démarrage complet local ⭐
```
- ✅ Accès via http://localhost:8001
- ✅ Économise les crédits (pas de ngrok)
- ✅ Performances optimales

### 🌐 Mode Internet (Avec Ngrok)
```bash
99_start_all_ngrok.bat      # Démarrage avec tunnel public
```
- ✅ Accès depuis n'importe où sur internet
- ✅ URL sécurisée générée automatiquement
- ⚠️ Nécessite ngrok installé

---

## 📜 Description Complète des Scripts

### 🔧 Installation
| Script | Fonction |
|--------|----------|
| `01_install_dependencies.bat` | Installation Python + Node.js + MongoDB |

### 🚀 Démarrage Services Individuels
| Script | Service | Port | Version |
|--------|---------|------|---------|
| `02_start_mongodb.bat` | Base de données | 27017 | Windows |
| `03_start_backend.bat` | Serveur API (local) | 8001 | server_windows.py |
| `03_start_backend_ngrok.bat` | Serveur API (tunnel) | 8001+ngrok | server_windows.py |
| `04_start_frontend.bat` | Interface web | Intégré | React build |

### ⚡ Automatisation Complète
| Script | Mode | Description |
|--------|------|-------------|
| `99_start_all.bat` | **Local** | Démarrage complet localhost |
| `99_start_all_ngrok.bat` | **Internet** | Démarrage avec tunnel ngrok |
| `stop_all.bat` | Arrêt | Arrêt de tous les services |

---

## 🎯 Ordre d'Exécution Recommandé

### 🏠 Usage Local (9/10 cas)
```bash
1. 01_install_dependencies.bat  # Une seule fois
2. 99_start_all.bat             # Usage quotidien ⭐
```

### 🌐 Usage Internet (cas spéciaux)
```bash
1. 01_install_dependencies.bat  # Une seule fois
2. Installer ngrok              # Depuis ngrok.com/download
3. 99_start_all_ngrok.bat       # Accès public
```

---

## 🔍 Améliorations Version Windows

### 🚀 Nouvelles Fonctionnalités
- ✅ **server_windows.py** : Serveur optimisé Windows
- ✅ **Chemins Windows** : Répertoires C:\FacebookPost\
- ✅ **Logs structurés** : Fichiers dans C:\FacebookPost\logs\
- ✅ **Auto-création** : Répertoires créés automatiquement
- ✅ **Ouverture navigateur** : Automatique avec ngrok
- ✅ **Gestion erreurs** : Messages clairs et diagnostics

### 📁 Structure Répertoires Windows
```
C:\FacebookPost\
├── data\                    # Base MongoDB
├── logs\                    # Logs serveur
├── backend\
│   ├── server_windows.py    # ⭐ Serveur Windows
│   └── uploads\            # Médias téléchargés
├── frontend\
│   └── build\              # Interface construite
└── start\                  # Scripts de lancement
```

---

## ⚠️ Instructions Importantes

### 🖥️ Fenêtres de Commande
- **MongoDB** : Reste ouverte (base de données active)
- **Backend** : Reste ouverte (serveur actif)
- **Frontend** : Se ferme après construction

### 🌐 URLs d'Accès
- **Local** : http://localhost:8001
- **Ngrok** : Généré automatiquement (ex: https://abc123.ngrok.io)
- **API Health** : http://localhost:8001/api/health
- **Ngrok URL** : http://localhost:8001/api/ngrok-url

### 💾 Stockage Windows
- **Configuration** : backend\.env
- **Base données** : C:\FacebookPost\data\
- **Logs serveur** : C:\FacebookPost\logs\
- **Médias** : C:\FacebookPost\backend\uploads\

---

## 🛠️ Résolution de Problèmes

### ❌ Serveur ne démarre pas
```bash
# Vérifier les prérequis
python --version
node --version  
mongod --version

# Réinstaller si nécessaire
01_install_dependencies.bat
```

### ❌ MongoDB ne répond pas
```bash
# Vérifier le service
net start MongoDB

# Ou créer le répertoire data
mkdir C:\FacebookPost\data
```

### ❌ Ngrok ne fonctionne pas
```bash
# Installer ngrok
1. Télécharger : https://ngrok.com/download
2. Décompresser ngrok.exe dans C:\Windows\System32\
3. Redémarrer l'invite de commande
4. Tester : ngrok version
```

### ❌ Frontend ne se charge pas
```bash
# Reconstruire le frontend
cd C:\FacebookPost\frontend
npm run build

# Ou utiliser le script
04_start_frontend.bat
```

---

## 📊 Monitoring et Diagnostics

### 🔍 Vérifications Automatiques
- ✅ Services actifs (MongoDB, Backend)
- ✅ Ports disponibles (27017, 8001)
- ✅ Build frontend existant
- ✅ Répertoires Windows créés
- ✅ Ngrok installé (si nécessaire)

### 📋 Commandes de Diagnostic
```bash
# Vérifier les ports
netstat -an | findstr "8001 27017"

# Vérifier les processus
tasklist | findstr "python mongod ngrok"

# Test API
curl http://localhost:8001/api/health

# Logs en temps réel
tail -f C:\FacebookPost\logs\backend_*.log
```

---

## 🎯 Avantages Version Windows

### 🚀 Performance
- **Chemins optimisés** : Répertoires Windows natifs
- **Logs centralisés** : Tous les logs dans C:\FacebookPost\logs\
- **Auto-création** : Répertoires créés automatiquement
- **Gestion mémoire** : Optimisée pour Windows

### 🔧 Facilité d'usage
- **Un seul clic** : 99_start_all.bat lance tout
- **Ouverture auto** : Navigateur ouvert automatiquement
- **Diagnostics** : Messages d'erreur clairs
- **Arrêt propre** : stop_all.bat nettoie tout

### 🌐 Flexibilité
- **Mode local** : Pour développement et tests
- **Mode ngrok** : Pour accès internet et webhooks
- **Configuration** : Variables d'environnement Windows
- **Portabilité** : Fonctionne sur tout Windows 10/11

---

*🎯 Pour l'utilisation complète, consultez le [Manuel d'Utilisation](../MANUEL_UTILISATION_LOCAL.md)*

**⭐ Recommandation : Utilisez `99_start_all.bat` pour un démarrage en un clic !**