# 🚀 Guide d'utilisation du Webhook n8n

## Configuration réussie ✅

Votre token ngrok `30KVU5Oxya5afdPt46syFR1KD65_3kxesHED2kbcHpDNW6VhT` a été configuré avec succès !

## URLs disponibles

### URL ngrok publique
```
https://ba142aa0c7fc.ngrok-free.app
```

### Endpoints webhook
- **Endpoint n8n spécialisé** : `https://ba142aa0c7fc.ngrok-free.app/api/webhook/n8n`
- **Endpoint webhook général** : `https://ba142aa0c7fc.ngrok-free.app/api/webhook`

## 📤 Configuration n8n

### 1. Créer un workflow n8n

Dans votre workflow n8n, ajoutez un nœud **HTTP Request** avec les paramètres suivants :

```
URL: https://ba142aa0c7fc.ngrok-free.app/api/webhook/n8n
Method: POST
Content-Type: application/json
```

### 2. Structure des données

Envoyez vos données au format JSON avec les champs suivants :

#### Champs obligatoires
- `message` ou `content` ou `text` : Le message à publier
- `product_url` ou `url` ou `link` : L'URL du produit

#### Champs optionnels
- `store` ou `shop` : Le magasin cible (`gizmobbs`, `logicantiq`, `outdoor`)
- `platforms` : Liste des plateformes (`["facebook"]`, `["instagram"]`, `["facebook", "instagram"]`)
- `image_url` ou `image` ou `media` : URL de l'image (requis pour Instagram)

### 3. Exemples de payloads n8n

#### Publication Facebook simple
```json
{
  "message": "🎯 Nouveau produit disponible !",
  "product_url": "https://monsite.com/produit-123",
  "store": "gizmobbs",
  "platforms": ["facebook"]
}
```

#### Publication multi-plateformes (Facebook + Instagram)
```json
{
  "message": "🚀 Découvrez notre nouveau produit !",
  "product_url": "https://monsite.com/produit-456",
  "image_url": "https://monsite.com/images/produit.jpg",
  "store": "logicantiq",
  "platforms": ["facebook", "instagram"]
}
```

#### Avec noms de champs alternatifs
```json
{
  "content": "📦 Produit en stock maintenant !",
  "link": "https://monsite.com/produit-789",
  "shop": "outdoor"
}
```

## 🏪 Stores disponibles

- **gizmobbs** : Le Berger Blanc Suisse (Page ID: 102401876209415)
- **logicantiq** : LogicAntiq (Page ID: 210654558802531)  
- **outdoor** : Logicamp Outdoor (Page ID: 236260991673388)

## 📊 Réponses du webhook

### Succès
```json
{
  "status": "received",
  "source": "n8n", 
  "message": "Données n8n traitées avec succès"
}
```

### Erreur
```json
{
  "detail": "Description de l'erreur"
}
```

## 🔍 Monitoring et logs

### Vérifier l'URL ngrok
```bash
python3 /app/get_ngrok_url.py
```

### Tester le webhook
```bash
python3 /app/test_n8n_webhook.py
```

### Consulter les logs
```bash
tail -f /var/log/supervisor/backend.out.log
```

## ⚙️ Configuration technique

### Backend
- **Port local** : 8001
- **Mode test** : Désactivé (publications réelles)
- **Base de données** : MongoDB (événements n8n sauvegardés)

### Ngrok
- **Token** : Configuré avec `30KVU5Oxya5afdPt46syFR1KD65_3kxesHED2kbcHpDNW6VhT`
- **Tunnel** : Actif sur le port 8001
- **URL publique** : Mise à jour automatiquement

## 🚨 Points importants

1. **URL dynamique** : L'URL ngrok change à chaque redémarrage
2. **Sauvegarde** : Tous les événements n8n sont sauvegardés en base de données
3. **Publications réelles** : Le mode test est désactivé, les publications sont effectives
4. **Gestion d'erreurs** : Les erreurs sont loggées et retournées dans la réponse

## 🧪 Test rapide

Testez votre configuration avec curl :

```bash
curl -X POST https://ba142aa0c7fc.ngrok-free.app/api/webhook/n8n \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test depuis n8n",
    "product_url": "https://example.com/test",
    "store": "gizmobbs"
  }'
```

## ✅ Statut de la configuration

- ✅ Token ngrok configuré
- ✅ Tunnel ngrok actif  
- ✅ Endpoint `/api/webhook/n8n` fonctionnel
- ✅ Publication Facebook testée et réussie
- ✅ Base de données MongoDB connectée
- ✅ Logs et monitoring actifs

**Votre configuration est prête pour recevoir les données de n8n !** 🎉