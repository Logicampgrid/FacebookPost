# Tests pour /api/auth/facebook/exchange-code

## ✅ Correction effectuée

L'endpoint `/api/auth/facebook/exchange-code` a été modifié pour accepter **les deux formats** :

1. **JSON** : `{"code": "...", "state": "..."}`
2. **Form-data** : `code=...&state=...`

## 🧪 Exemples de test

### Format 1: JSON

```bash
curl -X POST http://localhost:8001/api/auth/facebook/exchange-code \
  -H "Content-Type: application/json" \
  -d '{
    "code": "AQD123456789",
    "state": "csrf_protection_123"
  }'
```

**Avec paramètres optionnels :**
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

### Format 2: Form-data

```bash
curl -X POST http://localhost:8001/api/auth/facebook/exchange-code \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "code=AQD123456789&state=csrf_protection_123"
```

**Avec paramètres optionnels :**
```bash
curl -X POST http://localhost:8001/api/auth/facebook/exchange-code \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "code=AQD123456789&state=csrf_protection_123&store=logicantiq&redirect_uri=https://yourapp.com/callback"
```

### Format 3: Multipart form-data

```bash
curl -X POST http://localhost:8001/api/auth/facebook/exchange-code \
  -F "code=AQD123456789" \
  -F "state=csrf_protection_123"
```

## 📋 Réponse attendue (200 OK)

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
  "formats_supported": [
    "application/json",
    "application/x-www-form-urlencoded", 
    "multipart/form-data"
  ],
  "timestamp": "2024-01-15T10:30:45.123456"
}
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

## ⚠️ Cas d'erreur

### Paramètre manquant (400)
```bash
curl -X POST http://localhost:8001/api/auth/facebook/exchange-code \
  -H "Content-Type: application/json" \
  -d '{"code": "AQD123456789"}'
# Erreur: "Paramètre 'state' requis"
```

### Format invalide (400)
```bash
curl -X POST http://localhost:8001/api/auth/facebook/exchange-code \
  -H "Content-Type: application/json" \
  -d 'invalid json'
# Erreur: "Format JSON invalide"
```

## 🔄 Compatibilité

L'ancien endpoint est toujours disponible sur `/api/auth/facebook/exchange-code-legacy` pour les applications qui utilisent le format original avec `store` et `redirect_uri` obligatoires.

## ✅ Validation

Pour valider la correction :
1. Lancer le serveur : `python server_windows.py`
2. Tester avec l'un des exemples curl ci-dessus
3. Vérifier que la réponse est un 200 OK avec le JSON attendu