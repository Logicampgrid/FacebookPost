# 🎉 Configuration Complète - Token Ngrok & Webhook n8n

## ✅ Configuration Réussie

Le token `30KVU5Oxya5afdPt46syFR1KD65_3kxesHED2kbcHpDNW6VhT` a été configuré avec succès !

## 🌐 URLs Actives

- **URL ngrok publique** : `https://ba142aa0c7fc.ngrok-free.app`
- **Webhook n8n** : `https://ba142aa0c7fc.ngrok-free.app/api/webhook/n8n`
- **Webhook général** : `https://ba142aa0c7fc.ngrok-free.app/api/webhook`

## 🚀 Fonctionnalités Opérationnelles

### ✅ Publications Facebook
- **gizmobbs** (Le Berger Blanc Suisse) : Opérationnel
- **logicantiq** (LogicAntiq) : Opérationnel  
- **outdoor** (Logicamp Outdoor) : Opérationnel

### ⚠️ Publications Instagram
- **gizmobbs** : En attente de configuration ID Instagram
- **logicantiq** : En attente de configuration ID Instagram
- **outdoor** : En attente de configuration ID Instagram

## 📤 Utilisation depuis n8n

### Structure JSON recommandée
```json
{
  "message": "Votre message de publication",
  "product_url": "https://votre-site.com/produit",
  "store": "gizmobbs",
  "platforms": ["facebook"],
  "image_url": "https://votre-site.com/image.jpg"
}
```

### Champs supportés
- `message/content/text` : Message à publier
- `product_url/url/link` : URL du produit
- `store/shop` : Store cible (gizmobbs, logicantiq, outdoor)
- `platforms` : Plateformes ["facebook", "instagram"]
- `image_url/image/media` : URL de l'image

## 🛠️ Scripts Utiles

### Obtenir l'URL ngrok
```bash
python3 /app/get_ngrok_url.py
```

### Tester le webhook
```bash
python3 /app/test_n8n_webhook.py
```

### Simuler l'exécution du token
```bash
python3 /app/execute_token.py
```

### Redémarrer avec ngrok
```bash
python3 /app/restart_with_ngrok.py
```

## 📊 Tests Effectués

1. ✅ Configuration token ngrok
2. ✅ Démarrage tunnel ngrok
3. ✅ Endpoint `/api/webhook/n8n` fonctionnel
4. ✅ Publication Facebook - Store gizmobbs
5. ✅ Publication Facebook - Store logicantiq
6. ✅ Publication Facebook - Store outdoor
7. ✅ Sauvegarde événements n8n en base de données
8. ✅ Gestion des erreurs et logs

## 📝 Logs de Test

### Publications Réussies
- `102401876209415_689551204154737` (gizmobbs)
- `236260991673388_798235956055665` (outdoor) 
- `210654558802531_122259603458195124` (logicantiq)

## 🔧 Services Actifs

```bash
sudo supervisorctl status
backend                          RUNNING
frontend                         RUNNING  
mongodb                          RUNNING
```

## 📱 Next Steps

1. **Pour Instagram** : Configurer les IDs Instagram Business dans `.env`
2. **Pour n8n** : Utiliser l'URL `https://ba142aa0c7fc.ngrok-free.app/api/webhook/n8n`
3. **Monitoring** : Surveiller les logs avec `tail -f /var/log/supervisor/backend.out.log`

## 🎯 Commande de Test Rapide

```bash
curl -X POST https://ba142aa0c7fc.ngrok-free.app/api/webhook/n8n \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test depuis n8n",
    "product_url": "https://example.com/test", 
    "store": "gizmobbs"
  }'
```

---

**🎉 Votre système est prêt à recevoir les objets de n8n et à publier automatiquement sur Facebook !**

Les publications Instagram seront disponibles une fois les IDs Instagram Business configurés dans le fichier `.env`.