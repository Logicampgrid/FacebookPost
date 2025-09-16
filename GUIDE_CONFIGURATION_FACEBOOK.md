# 🔧 Guide de Configuration Facebook App - FacebookPost

## 🚨 PROBLÈME RÉSOLU

L'erreur d'authentification Facebook est maintenant **corrigée** ! Voici le guide complet pour configurer votre application.

## ⚡ Solution Rapide

### 1. Démarrer ngrok
```bash
# Dans un terminal séparé
ngrok http 8001
```

### 2. Synchroniser automatiquement
```bash
# Dans le dossier backend
curl -X POST http://localhost:8001/api/sync/ngrok
```

Cette commande vous donnera toutes les informations nécessaires pour configurer Facebook.

## 📋 Configuration Facebook App Détaillée

### Étape 1: Accéder à Facebook Developer Console
1. Allez sur [Facebook Developer Console](https://developers.facebook.com/apps/5664227323683118/settings/basic/)
2. Connectez-vous avec votre compte Facebook

### Étape 2: App Domains (Settings > Basic)
Ajoutez le domaine ngrok (sans https://) :
```
VOTRE_DOMAINE_NGROK.ngrok-free.app
```

### Étape 3: OAuth Redirect URIs (Facebook Login > Settings)
Ajoutez ces deux URLs complètes :
```
https://VOTRE_DOMAINE_NGROK.ngrok-free.app/auth/callback
https://VOTRE_DOMAINE_NGROK.ngrok-free.app/
```

### Étape 4: Webhooks (si utilisés)
URL de callback :
```
https://VOTRE_DOMAINE_NGROK.ngrok-free.app/api/webhook
```

## 🔄 Automatisation avec le Script ngrok_sync.py

### Utilisation Manuelle
```bash
cd /app/backend
python ngrok_sync.py
```

### Surveillance Continue
```bash
cd /app/backend
python ngrok_sync.py --watch 30
```

## 🛠️ Endpoints Ajoutés

### Synchronisation Ngrok
```bash
POST /api/sync/ngrok
```
Retourne les instructions complètes pour Facebook App.

### Health Check Amélioré
```bash
GET /api/health
```
Inclut maintenant le statut ngrok détaillé.

## 🔧 Corrections Effectuées

### 1. ✅ Endpoint de Callback Ajouté
- Route : `GET /auth/callback`
- Gère la redirection OAuth Facebook
- Transfère tous les paramètres au frontend

### 2. ✅ Synchronisation Automatique
- Détection automatique de l'URL ngrok
- Mise à jour du frontend `.env`
- Génération d'instructions Facebook

### 3. ✅ Gestion d'Erreurs Améliorée
- Messages d'erreur plus clairs
- Logging détaillé pour debugging
- Fallbacks robustes

## 🎯 Test de l'Authentification

Une fois Facebook configuré :

```bash
# Tester l'échange de code
curl -X POST http://localhost:8001/api/auth/facebook/exchange-code \
  -H "Content-Type: application/json" \
  -d '{"code": "VOTRE_CODE_FACEBOOK", "state": "test", "store": "gizmobbs"}'
```

## 📊 Statut des Services

Vérifiez que tout fonctionne :
```bash
# Status des services
sudo supervisorctl status

# Health check complet
curl http://localhost:8001/api/health

# Frontend accessible
curl http://localhost:3000
```

## 🚀 Démarrage Complet

1. **Services** : `sudo supervisorctl start all`
2. **Ngrok** : `ngrok http 8001` (terminal séparé)
3. **Sync** : `curl -X POST http://localhost:8001/api/sync/ngrok`
4. **Config Facebook** : Suivre les instructions affichées
5. **Test** : Ouvrir http://localhost:3000

## 💡 Conseils

### URLs Ngrok Dynamiques
- L'URL ngrok change à chaque redémarrage
- Utilisez le script de synchronisation après chaque restart
- Pour une URL fixe, utilisez un compte ngrok payant

### Debugging
- Logs backend : `tail -f /var/log/supervisor/backend*.log`
- Console browser : F12 > Console
- API health : `curl http://localhost:8001/api/health`

### Production
Pour la production, remplacez ngrok par :
- Un domaine fixe (recommandé)
- Un serveur VPS avec nom de domaine
- Un service cloud (Heroku, Vercel, etc.)

## 🆘 Support

Si vous rencontrez des problèmes :
1. Vérifiez que ngrok est démarré
2. Exécutez la synchronisation
3. Vérifiez la configuration Facebook
4. Consultez les logs backend
5. Testez l'endpoint health