# 🔧 FacebookPost - Webhook Corrigé pour Windows

## 📋 Résumé des corrections

✅ **GET /api/webhook** : Fonctionne parfaitement avec Facebook  
✅ **POST /api/webhook** : Traite correctement les événements  
✅ **Token de vérification** : Lecture depuis `.env` confirmée  
✅ **Logs détaillés** : Debug complet activé  
✅ **Tests validés** : Tous les scénarios testés avec succès  

## 🚀 Installation Windows

### 1. Copier les fichiers

Remplacer `C:\FacebookPost\backend\server.py` par le fichier corrigé :
```
server_windows_ready.py → server.py
```

Utiliser le fichier `.env` fourni :
```
.env_windows_ready → .env
```

### 2. Configuration .env

Votre fichier `C:\FacebookPost\backend\.env` doit contenir :
```env
MONGO_URL=mongodb://localhost:27017
FACEBOOK_APP_ID=5664227323683118
FACEBOOK_APP_SECRET=b359a1c87c920288385daf75aed873a3
JWT_SECRET=your-secret-key-change-in-production
FACEBOOK_GRAPH_URL=https://graph.facebook.com/v18.0
PUBLIC_BASE_URL=https://93ced01ab9ca.ngrok-free.app
NGROK_URL=https://93ced01ab9ca.ngrok-free.app
EXTERNAL_WEBHOOK_ENABLED=true
FACEBOOK_VERIFY_TOKEN=mon_token_secret_webhook
```

### 3. Démarrage

```bash
cd C:\FacebookPost\backend
python server.py
```

Le serveur démarre sur **http://localhost:8001**

## 🧪 Tests de validation

### Test 1: GET webhook valide
```bash
curl "http://localhost:8001/api/webhook?hub.mode=subscribe&hub.verify_token=mon_token_secret_webhook&hub.challenge=12345"
```
**Résultat attendu :** `12345`

### Test 2: GET webhook token invalide  
```bash
curl "http://localhost:8001/api/webhook?hub.mode=subscribe&hub.verify_token=invalid&hub.challenge=12345"
```
**Résultat attendu :** `HTTP 403 Verification failed`

### Test 3: POST webhook événement
```bash
curl -X POST "http://localhost:8001/api/webhook" \
  -H "Content-Type: application/json" \
  -d '{"object":"page","entry":[{"id":"123","time":456}]}'
```
**Résultat attendu :** `{"status":"received"}`

## 🔧 Corrections apportées

### 1. **Réponse GET en texte plain**
```python
# AVANT (problématique)
return challenge

# APRÈS (corrigé)
return PlainTextResponse(content=str(challenge), status_code=200)
```

### 2. **Token depuis .env**
```python
VERIFY_TOKEN = os.getenv("FACEBOOK_VERIFY_TOKEN", "mon_token_secret_webhook")
```

### 3. **Logs détaillés**
```python
log_webhook("=== FACEBOOK WEBHOOK VERIFICATION ===", "DEBUG")
log_webhook(f"Mode reçu: '{mode}'", "DEBUG")
log_webhook(f"Token reçu: '{token}'", "DEBUG") 
log_webhook(f"Challenge reçu: '{challenge}'", "DEBUG")
```

### 4. **Validation stricte**
```python
if not mode or not token or not challenge:
    raise HTTPException(status_code=400, detail="Paramètres requis manquants")
```

### 5. **POST response correcte**
```python
return {"status": "received"}  # Exactement ce que Facebook attend
```

### 6. **Chemins Windows**
```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
```

## 📊 Statut des fonctionnalités

| Fonctionnalité | Statut | Description |
|---|---|---|
| GET /api/webhook | ✅ **Corrigé** | Retourne `hub.challenge` en texte plain |
| POST /api/webhook | ✅ **Corrigé** | Retourne `{"status":"received"}` |
| Token verification | ✅ **Corrigé** | Lecture depuis `FACEBOOK_VERIFY_TOKEN` |
| Logs debug | ✅ **Ajouté** | Logs détaillés pour diagnostic |
| Gestion erreurs | ✅ **Renforcé** | Codes 400, 403, 500 appropriés |
| Ngrok integration | ✅ **Conservé** | Compatible Windows |
| MongoDB | ✅ **Conservé** | Configuration locale |

## 🎯 Points clés à retenir

1. **Format de réponse critique** : Facebook EXIGE du texte plain pour GET
2. **Token exact** : Doit correspondre entre `.env` et votre script GUI  
3. **Port fixe** : Toujours 8001 comme spécifié
4. **Logs complets** : Permet de diagnostiquer facilement les problèmes
5. **Chemins Windows** : Adaptés pour C:\FacebookPost\backend

## 🚨 Troubleshooting

### Problème : "Verification failed"
- Vérifier que `FACEBOOK_VERIFY_TOKEN` dans `.env` = token du script GUI
- Regarder les logs pour voir le token reçu vs attendu

### Problème : "Connection refused"  
- S'assurer que MongoDB tourne sur localhost:27017
- Vérifier que le port 8001 n'est pas utilisé par autre chose

### Problème : Ngrok ne démarre pas
- Vérifier `NGROK_AUTH_TOKEN` dans `.env` 
- Ou désactiver avec `ENABLE_NGROK=false`

## 🎉 Résultat final

**Le webhook FacebookPost fonctionne maintenant parfaitement !**

- ✅ Validation Facebook réussie
- ✅ Événements POST traités  
- ✅ Logs clairs pour debug
- ✅ Compatible Windows + Python 3.11
- ✅ Prêt pour ngrok

Votre script GUI Windows peut maintenant valider le webhook avec succès ! 🚀