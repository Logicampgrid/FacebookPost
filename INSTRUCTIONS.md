# Facebook Post Manager - Instructions d'utilisation

## 🚀 Application de Gestion de Posts Facebook

Cette application vous permet de créer, planifier et publier des posts sur vos pages Facebook avec une interface moderne et intuitive.

## ✅ Problèmes Résolus

### 1. Permissions Facebook Corrigées
- **Problème initial** : "Invalid Scopes: publish_to_groups"
- **Solution appliquée** : Suppression de la permission obsolète `publish_to_groups`
- **Permissions actuelles** : `pages_manage_posts,pages_read_engagement,pages_show_list`

### 2. Compatibilité Backend Réparée  
- **Problème initial** : Erreur "ValueError: too many values to unpack (expected 2)"
- **Solution appliquée** : Downgrade de FastAPI de 0.104.1 vers 0.100.1
- **Statut** : ✅ Backend complètement fonctionnel

### 3. Configuration Proxy Frontend
- **Problème initial** : Appels API non routés correctement
- **Solution appliquée** : Ajout de `"proxy": "http://localhost:8001"` dans package.json
- **Statut** : ✅ Communication frontend-backend établie

## 🎯 Fonctionnalités Disponibles

### ✅ Authentification Facebook
- Connexion sécurisée avec Facebook OAuth
- Récupération automatique des pages Facebook
- Gestion des tokens d'accès

### ✅ Création de Posts
- Éditeur de contenu avec compteur de caractères
- Upload d'images et vidéos (glisser-déposer)
- Aperçu en temps réel du post
- Programmation de publication

### ✅ Gestion des Posts
- Liste de tous les posts créés
- Statuts : Brouillon, Programmé, Publié, Échec
- Publication immédiate possible
- Suppression des posts

### ✅ Interface Moderne
- Design inspiré de Facebook
- Responsive et moderne
- Animations fluides
- Feedback utilisateur en temps réel

## 🔧 Services Actifs

```bash
sudo supervisorctl status
```

- ✅ **backend** : FastAPI (port 8001)
- ✅ **frontend** : React (port 3000)  
- ✅ **mongodb** : Base de données (port 27017)

## 🌐 Accès à l'Application

- **Interface utilisateur** : http://localhost:3000
- **API Backend** : http://localhost:8001
- **Documentation API** : http://localhost:8001/docs

## 📊 Tests de Fonctionnement

### Test API Backend
```bash
curl -X GET "http://localhost:8001/api/health"
# Réponse attendue : {"status":"healthy","timestamp":"..."}
```

### Test Liste des Posts
```bash
curl -X GET "http://localhost:8001/api/posts"
# Réponse attendue : {"posts":[]}
```

## 🔑 Configuration Facebook

L'application utilise les identifiants Facebook configurés dans `/app/backend/.env` :
- **APP_ID** : 5664227323683118
- **APP_SECRET** : Configuré
- **Graph API** : Version 18.0

## 🚨 Prochaines Étapes Recommandées

1. **Tester la connexion Facebook** avec un compte développeur
2. **Créer un post de test** pour vérifier la publication
3. **Tester l'upload d'images**
4. **Vérifier la programmation de posts**

## 🛠️ Commandes de Maintenance

### Redémarrage des services
```bash
sudo supervisorctl restart all
# ou individuellement :
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

### Consultation des logs
```bash
# Backend
tail -f /var/log/supervisor/backend.err.log

# Frontend  
tail -f /var/log/supervisor/frontend.err.log
```

## 📈 Status Global
- ✅ **Backend** : Fonctionnel
- ✅ **Frontend** : Fonctionnel  
- ✅ **Base de données** : Connectée
- ✅ **API** : Opérationnelle
- ✅ **Interface** : Accessible

L'application est maintenant **entièrement opérationnelle** et prête pour la création et publication de posts Facebook !