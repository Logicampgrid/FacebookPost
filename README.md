# 📱 FacebookPost - Publication Automatique Multi-Plateformes

> Application locale Windows pour publier automatiquement sur Facebook et Instagram via l'API Meta Business

## 🚀 Démarrage Rapide (2 minutes)

### Installation Express
1. **Prérequis** : Python 3.8+, Node.js 16+, MongoDB
2. **Installation** : `start\01_install_dependencies.bat`
3. **Démarrage** : `start\99_start_all.bat` 
4. **Ouverture** : http://localhost:8001

### Première Utilisation
1. Connecter votre Business Manager Facebook
2. Sélectionner vos pages/groupes/Instagram  
3. Créer et publier vos premiers posts

---

## 📂 Structure du Projet

```
C:\FacebookPost\
├── 📁 start\              # Scripts de lancement Windows
├── 📁 backend\            # Serveur API (FastAPI + Python)
├── 📁 frontend\           # Interface web (React)
├── 📁 data\              # Base de données locale MongoDB
├── 📖 INSTALLATION_GUIDE.md
├── 📖 MANUEL_UTILISATION_LOCAL.md
└── 📖 README.md
```

---

## ⚡ Scripts de Lancement

| Script | Description |
|--------|-------------|
| `01_install_dependencies.bat` | 📦 Installation des dépendances |
| `02_start_mongodb.bat` | 💾 Démarrage MongoDB |
| `03_start_backend.bat` | 🔧 Démarrage serveur API |
| `04_start_frontend.bat` | 🎨 Construction interface |
| `99_start_all.bat` | 🚀 **Démarrage complet automatique** |
| `stop_all.bat` | 🛑 Arrêt de tous les services |

---

## 🎯 Fonctionnalités

### Publication Multi-Plateformes
- ✅ **Facebook Pages** : Pages d'entreprise
- ✅ **Facebook Groups** : Groupes publics/privés
- ✅ **Instagram Business** : Comptes professionnels
- ✅ **Multi-boutiques** : 5 magasins supportés

### Gestion des Médias
- 🖼️ **Images optimisées** : Redimensionnement automatique
- 📱 **Formats compatibles** : JPEG, PNG, WebP
- 🔄 **Conversion automatique** : Orientation et qualité
- ☁️ **Stockage FTP** : Upload automatique

### Modes de Publication  
- 🧪 **Mode Test** : Simulation sans publication réelle
- 🎯 **Mode Production** : Publications réelles
- ⏰ **Publication immédiate** : Direct sur les plateformes
- 📊 **Historique complet** : Suivi des publications

---

## 💰 Budget Optimisé (9,80€)

### 🆓 Utilisation Gratuite
- Installation et configuration complète
- Mode test illimité
- Authentification Facebook Business
- Interface et navigation
- Prévisualisation des publications

### 💳 Consommation Crédits
- Publications réelles Facebook/Instagram
- Appels répétés à l'API Meta
- Gestion des webhooks externes

### 🎯 Conseils d'Économie
1. **Mode test par défaut** : `PUBLICATION_TEST_MODE=true`
2. **Validation préalable** : Vérifier avant de publier
3. **Grouper les publications** : Batch des opérations
4. **Monitoring actif** : Surveiller les consommations

---

## 🔧 Configuration

### Fichiers de Configuration
- `backend\.env` : Variables serveur et tokens
- `frontend\.env` : Variables interface  
- `data\` : Base de données MongoDB locale

### URLs Importantes
- **Application** : http://localhost:8001
- **API Health** : http://localhost:8001/api/health
- **Documentation** : Intégrée dans l'interface

---

## 📖 Documentation

| Guide | Description |
|-------|-------------|
| [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) | 🔧 Installation complète |
| [MANUEL_UTILISATION_LOCAL.md](MANUEL_UTILISATION_LOCAL.md) | 📚 Guide utilisateur détaillé |

---

## 🛠️ Support Technique

### Diagnostic Rapide
```bash
# Vérifier les services actifs
netstat -an | findstr "8001 27017"

# Tester la santé de l'API
curl http://localhost:8001/api/health

# Arrêter tous les services
start\stop_all.bat
```

### Logs et Debugging
- **Backend** : Logs dans la fenêtre de commande
- **Frontend** : Console navigateur (F12)
- **MongoDB** : Logs dans la fenêtre MongoDB

---

## 🔄 Mise à Jour

### Dépendances
```bash
# Backend Python
cd backend && pip install -r requirements.txt --upgrade

# Frontend Node.js  
cd frontend && npm update
```

### Sauvegarde
```bash
# Sauvegarder la configuration et les données
xcopy backend\.env backup\
xcopy data\ backup\data\ /E
```

---

## 📊 Tableau de Bord

### Services Locaux
- **MongoDB** : Base de données (Port 27017)
- **Backend API** : Serveur FastAPI (Port 8001)  
- **Frontend** : Interface React (Intégrée)

### Boutiques Supportées
- `logicantiq` - LogicAntiq  
- `logicampoutdoor` - Logicamp Outdoor
- `bergerblancsuisse` - Berger Blanc Suisse
- `gizmobbs` - GizmoBBS

---

## 🚀 Démarrage Express

```bash
# Installation (première fois)
start\01_install_dependencies.bat

# Lancement quotidien  
start\99_start_all.bat

# Accès application
http://localhost:8001
```

---

*Version 1.0 - Application locale Windows optimisée pour un budget de 9,80€ de crédits Emergent*

**🎯 Prêt à utiliser ? Consultez [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) pour commencer !**