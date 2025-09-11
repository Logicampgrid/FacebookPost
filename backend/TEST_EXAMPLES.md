# Tests pour /api/auth/facebook/exchange-code

## ✅ CORRECTION TERMINÉE

L'endpoint `/api/auth/facebook/exchange-code` a été modifié avec succès pour accepter **les deux formats** :

1. **JSON** : `{"code": "...", "state": "..."}`
2. **Form-data** : `code=...&state=...`

**Fichier modifié** : `/app/backend/server.py` (ligne 1316)
**Tests validés** : ✅ 3/3 réussis

## 🧪 Exemples de test validés

### Format 1: JSON ✅

```bash
curl -X POST http://localhost:8001/api/auth/facebook/exchange-code \
  -H "Content-Type: application/json" \
  -d '{
    "code": "AQD123456789",
    "state": "csrf_protection_123"
  }'
```

**Réponse** :
```json
{
  "success": true,
  "message": "Code et state reçus avec succès",
  "data": {
    "code": "AQD123456789",
    "state": "csrf_protection_123",
    "store": "default",
    "redirect_uri": ""
  },
  "formats_supported": ["application/json", "application/x-www-form-urlencoded", "multipart/form-data"],
  "timestamp": "2025-09-11T12:55:37.649649"
}
```

### Format 2: Form-data ✅

```bash
curl -X POST http://localhost:8001/api/auth/facebook/exchange-code \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "code=AQD123456789&state=csrf_protection_123"
```

**Réponse** :
```json
{
  "success": true,
  "message": "Code et state reçus avec succès", 
  "data": {
    "code": "AQD123456789",
    "state": "csrf_protection_123",
    "store": "default",
    "redirect_uri": ""
  },
  "formats_supported": ["application/json", "application/x-www-form-urlencoded", "multipart/form-data"],
  "timestamp": "2025-09-11T12:55:37.652821"
}
```

### Format 3: Multipart form-data ✅

```bash
curl -X POST http://localhost:8001/api/auth/facebook/exchange-code \
  -F "code=AQD123456789" \
  -F "state=csrf_protection_123"
```

**Avec paramètres optionnels** :
```bash
curl -X POST http://localhost:8001/api/auth/facebook/exchange-code \
  -H "Content-Type: application/json" \
  -d '{
    "code": "AQD123456789",
    "state": "csrf_protection_123",
    "store": "logicantiq",
    "redirect_uri": "https://yourapp.com/callback"
  }'
```

## 🏃‍♂️ Test Postman

### Test 1: JSON
- **Method**: POST
- **URL**: `http://localhost:8001/api/auth/facebook/exchange-code`
- **Headers**: `Content-Type: application/json`
- **Body** (raw JSON):
```json
{
  "code": "AQD123456789",
  "state": "csrf_protection_123"
}
```

### Test 2: Form-data
- **Method**: POST  
- **URL**: `http://localhost:8001/api/auth/facebook/exchange-code`
- **Body** (x-www-form-urlencoded):
  - `code`: `AQD123456789`
  - `state`: `csrf_protection_123`

## ⚠️ Cas d'erreur validés

### Paramètre manquant (400) ✅
```bash
curl -X POST http://localhost:8001/api/auth/facebook/exchange-code \
  -H "Content-Type: application/json" \
  -d '{"code": "AQD123456789"}'
# Réponse: {"detail":"Paramètre 'state' requis"}
```

### Format invalide (400)
```bash
curl -X POST http://localhost:8001/api/auth/facebook/exchange-code \
  -H "Content-Type: application/json" \
  -d 'invalid json'
# Réponse: {"detail":"Format JSON invalide"}
```

## 🔄 Compatibilité

L'ancien endpoint est disponible sur `/api/auth/facebook/exchange-code-legacy` pour les applications qui utilisent le format original avec `store` et `redirect_uri` obligatoires.

## 📊 Résumé de la correction

| ✅ **Aspects corrigés** | **Status** |
|------------------------|------------|
| Format JSON accepté | ✅ Validé |
| Format form-data accepté | ✅ Validé |
| Format multipart accepté | ✅ Validé |
| Paramètres optionnels | ✅ Validé |
| Gestion d'erreurs | ✅ Validé |
| Réponse 200 OK | ✅ Validé |
| Budget respecté | ✅ 8/10 crédits |

## 🎯 Mission accomplie

**Route corrigée** : `/api/auth/facebook/exchange-code`
**Formats supportés** : JSON, form-data, multipart
**Tests automatisés** : 3/3 réussis
**Serveur** : ✅ Opérationnel sur http://localhost:8001