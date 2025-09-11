# 🚀 Scripts de Démarrage FacebookPost

> Répertoire contenant tous les scripts .bat pour Windows

## ⚡ Utilisation Rapide

### Première Installation
```bash
01_install_dependencies.bat  # Une seule fois
```

### Démarrage Quotidien  
```bash
99_start_all.bat            # Tout en automatique ⭐
```

### Arrêt Complet
```bash
stop_all.bat                # Arrête tous les services
```

---

## 📜 Description des Scripts

### 🔧 Installation
| Script | Fonction |
|--------|----------|
| `01_install_dependencies.bat` | Installation Python + Node.js + MongoDB |

### 🚀 Démarrage Services
| Script | Service | Port | Remarque |
|--------|---------|------|----------|
| `02_start_mongodb.bat` | Base de données | 27017 | Laissez ouvert |
| `03_start_backend.bat` | Serveur API | 8001 | Laissez ouvert |
| `04_start_frontend.bat` | Interface web | 3000 | Construit puis intègre |

### ⚡ Automatisation
| Script | Description |
|--------|-------------|
| `99_start_all.bat` | **Démarrage complet automatique** |
| `stop_all.bat` | Arrêt de tous les services |

---

## 🎯 Ordre d'Exécution Normal

### Première fois
```bash
1. 01_install_dependencies.bat  # Installation
2. 99_start_all.bat             # Démarrage complet
```

### Usage quotidien
```bash
99_start_all.bat                # Un seul clic !
```

### Arrêt
```bash
stop_all.bat                    # Arrêt propre
```

---

## ⚠️ Instructions Importantes

### Fenêtres de Commande
- **MongoDB** : Laissez la fenêtre ouverte pendant l'utilisation
- **Backend** : Laissez la fenêtre ouverte pendant l'utilisation  
- **Frontend** : Peut être fermée après construction

### Ports Utilisés
- **27017** : MongoDB (base de données)
- **8001** : Backend API (serveur principal)
- **3000** : Frontend (si mode développement)

### Accès Application
- **URL principale** : http://localhost:8001
- **Test santé** : http://localhost:8001/api/health

---

## 🛠️ Résolution de Problèmes

### Script ne démarre pas
```bash
# Vérifier les prérequis
python --version
node --version  
mongod --version

# Réinstaller si nécessaire
01_install_dependencies.bat
```

### Service ne répond pas
```bash
# Arrêter tous les services
stop_all.bat

# Vérifier les ports libres
netstat -an | findstr "8001 27017 3000"

# Redémarrer
99_start_all.bat
```

### Permissions Windows
```bash
# Exécuter en tant qu'administrateur si nécessaire
Clic droit > "Exécuter en tant qu'administrateur"
```

---

## 📊 Monitoring

### Vérifier les Services Actifs
```bash
# Processus en cours
tasklist | findstr "python node mongod"

# Ports ouverts
netstat -an | findstr "8001 27017"

# Test application
curl http://localhost:8001/api/health
```

---

## 🔄 Maintenance

### Mise à jour des Dépendances
```bash
# Arrêter l'application
stop_all.bat

# Réinstaller les dépendances
01_install_dependencies.bat

# Redémarrer
99_start_all.bat
```

### Nettoyage Complet
```bash
# Arrêter tout
stop_all.bat

# Supprimer le dossier data (sauvegardez avant !)
rmdir /s C:\FacebookPost\data

# Réinstaller
01_install_dependencies.bat
99_start_all.bat
```

---

*🎯 Pour l'utilisation complète, consultez le [Manuel d'Utilisation](../MANUEL_UTILISATION_LOCAL.md)*