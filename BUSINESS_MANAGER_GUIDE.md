# Guide de Configuration Business Manager Facebook

## 🏢 Configuration pour "Entreprise de Didier Preud'homme"

Ce guide vous explique comment connecter votre application Facebook Post Manager à votre Business Manager spécifique pour gérer uniquement les pages professionnelles.

### ✅ Modifications Effectuées

1. **Backend mis à jour** avec support Business Manager :
   - Nouvelles permissions : `business_management`, `read_insights`
   - API pour récupérer les Business Managers
   - API pour récupérer les pages de chaque Business Manager
   - Sélection et sauvegarde du Business Manager préféré

2. **Frontend mis à jour** avec interface dédiée :
   - Composant `BusinessManagerSelector` pour choisir le portefeuille
   - Interface de configuration étape par étape
   - Séparation claire entre pages personnelles et professionnelles
   - Auto-sélection de "Entreprise de Didier Preud'homme"

### 📋 Étapes de Configuration

#### Étape 1: Vérification des Permissions Facebook App

Votre App Facebook (ID: 5664227323683118) doit avoir les permissions suivantes :

**Permissions requises :**
- ✅ `pages_manage_posts` - Publier sur les pages
- ✅ `pages_read_engagement` - Lire les engagements
- ✅ `pages_show_list` - Afficher la liste des pages
- ✅ `business_management` - **NOUVEAU** - Accès aux Business Managers
- ✅ `read_insights` - **NOUVEAU** - Lire les statistiques

#### Étape 2: Configuration dans Facebook Developer Console

1. **Allez sur** [Facebook Developer Console](https://developers.facebook.com/apps/5664227323683118)

2. **Vérifiez les permissions** :
   - App Review > Permissions and Features
   - Assurez-vous que `business_management` est approuvé

3. **Ajoutez votre domaine** (si nécessaire) :
   - App Settings > Basic
   - App Domains: ajoutez votre domaine de production

4. **Configurez OAuth Settings** :
   - Products > Facebook Login > Settings
   - Valid OAuth Redirect URIs: ajoutez vos URLs de callback

#### Étape 3: Vérification des Droits Business Manager

1. **Connectez-vous à** [Business Manager](https://business.facebook.com/)

2. **Vérifiez l'accès** à "Entreprise de Didier Preud'homme" :
   - Sélectionnez le bon Business Manager dans le menu déroulant
   - Vérifiez que vous avez les permissions administrateur

3. **Vérifiez les pages** :
   - Business Settings > Pages
   - Assurez-vous que toutes les pages sont bien associées au Business Manager

4. **Permissions utilisateur** :
   - Business Settings > Users
   - Vérifiez que votre compte a les permissions nécessaires

#### Étape 4: Test de Connexion

1. **Ouvrez l'application** : http://localhost:3000

2. **Connexion** :
   - Utilisez de préférence la méthode "Token manuel" pour les tests
   - Ou "Redirection" si le domaine est configuré

3. **Vérification** :
   - L'application devrait auto-détecter "Entreprise de Didier Preud'homme"
   - Les pages du Business Manager devraient apparaître

### 🔧 Méthodes de Test

#### Option A: Token Manuel Développeur

1. **Allez sur** [Graph API Explorer](https://developers.facebook.com/tools/explorer/)

2. **Configuration** :
   - App ID: `5664227323683118`
   - Générez un "User Access Token"
   - Permissions: `pages_manage_posts,pages_read_engagement,pages_show_list,business_management,read_insights`

3. **Test** :
   - Collez le token dans l'application
   - Cliquez sur "Tester le Token"

#### Option B: Authentification Redirect

1. **Configuration domaine** requise dans Facebook App
2. **URL de redirection** : http://localhost:3000 (ou votre domaine)
3. **Cliquez** sur "Se connecter avec Facebook"

### 🎯 Flux d'Utilisation

1. **Connexion** → L'app détecte vos Business Managers
2. **Sélection** → Choisissez "Entreprise de Didier Preud'homme"
3. **Configuration** → L'onglet Configuration vous montre le statut
4. **Sélection page** → Choisissez une page du Business Manager
5. **Création posts** → Créez vos posts pour cette page uniquement

### ⚠️ Résolution de Problèmes

#### "Aucun Business Manager trouvé"
- Vérifiez que la permission `business_management` est accordée
- Vérifiez vos droits sur le Business Manager Facebook

#### "Pages vides"
- Vérifiez que les pages sont bien associées au Business Manager
- Vérifiez les permissions de votre compte sur ces pages

#### "Token invalide"
- Régénérez un nouveau token avec toutes les permissions
- Vérifiez que l'App ID est correct

#### "Erreur domaine"
- Pour la méthode redirect, ajoutez votre domaine dans Facebook App Settings
- Utilisez la méthode "Token manuel" pour les tests locaux

### 📊 Interface de Configuration

L'application propose maintenant 3 onglets :

1. **Configuration** : Statut et sélection du Business Manager
2. **Créer un Post** : Actif seulement après configuration
3. **Mes Posts** : Historique des publications

### 🔐 Sécurité

- Les tokens sont stockés temporairement en base de données
- Seules les pages du Business Manager sélectionné sont accessibles
- Séparation claire entre comptes personnels et professionnels

### 📞 Support

Si vous rencontrez des difficultés :

1. **Vérifiez les logs backend** : `tail -f /var/log/supervisor/backend.*.log`
2. **Vérifiez la console browser** : F12 > Console
3. **Testez l'API directement** : http://localhost:8001/api/debug/facebook-config

---

**Félicitations !** Votre application est maintenant configurée pour gérer exclusivement les pages de votre Business Manager "Entreprise de Didier Preud'homme" ! 🎉