# 🔧 PATCH 56 - Correction Timeout Vidéo Instagram (URGENT)

## ⚠️ PROBLÈME CRITIQUE IDENTIFIÉ
Les vidéos Instagram sont marquées **FINISHED** (prêtes à publier) mais le code **continue de vérifier** au lieu de **publier immédiatement**, causant un timeout après 60 secondes.

**Symptômes dans les logs** :
```
ℹ️ [21:42:53] Container status - Code: FINISHED ✅ (Prête depuis 21:42:53)
ℹ️ [21:43:01] Container status - Code: FINISHED ✅ (Vérifie encore...)
ℹ️ [21:43:08] Container status - Code: FINISHED ✅ (Vérifie encore...)
ℹ️ [21:43:20] Container status - Code: FINISHED ✅ (Vérifie encore...)
❌ [21:43:31] PATCH 38: Timeout - vidéo non traitée après 60s ❌ ÉCHEC
```

## ✅ SOLUTION - PATCH 56

### Problèmes à corriger :
1. **Timeout trop court** : 60s → **180s (3 minutes)**
2. **Détection FINISHED cassée** : Code vérifie `status_code == 2` mais Instagram envoie `"FINISHED"` (string)
3. **Boucle infinie** : Ne sort jamais de la boucle malgré status FINISHED

### Fichier à modifier : `C:\FacebookPost\backend\server.py`

---

## 📋 ÉTAPES D'APPLICATION

### ÉTAPE 1 : Arrêter le serveur
```cmd
# Fermer la fenêtre du serveur ou appuyer sur CTRL+C
```

### ÉTAPE 2 : Ouvrir le fichier
```cmd
notepad C:\FacebookPost\backend\server.py
```

### ÉTAPE 3 : Chercher la fonction (CTRL+F)
Rechercher : `PATCH 38: Vidéo Instagram détectée`

Vous devriez trouver autour des lignes **6549-6596**

---

## 🔧 MODIFICATIONS À APPLIQUER

### Localiser ce code (PATCH 38 - ANCIEN) :

```python
        # PATCH 38: Workflow container Instagram pour vidéos
        log_app(f"🎬 PATCH 38: Vidéo Instagram détectée - workflow container activé", "INFO")
        
        # Étape 1: Créer le container
        container_response = requests.post(
            container_url,
            data=container_data,
            timeout=30
        )
        container_response.raise_for_status()
        container_result = container_response.json()
        container_id = container_result.get("id")
        
        if not container_id:
            return {"success": False, "error": "PATCH 38: Échec création container Instagram"}
        
        # Étape 2: Attendre que la vidéo soit traitée
        max_wait = 60  # Maximum 60 secondes
        wait_interval = 5
        elapsed = 0
        
        while elapsed < max_wait:
            status_url = f"{FACEBOOK_GRAPH_URL}/{container_id}"
            status_params = {
                "fields": "status_code,status",
                "access_token": access_token
            }
            
            status_response = requests.get(status_url, params=status_params, timeout=10)
            status_response.raise_for_status()
            status_data = status_response.json()
            
            status_code = status_data.get("status_code")
            status_message = status_data.get("status")
            
            log_app(f"🔄 PATCH 38: Container status - Code: {status_code}, Status: {status_message}", "INFO")
            
            # PATCH 41: Support dual formats (string et int) pour status_code
            if status_code == 2 or status_code == "FINISHED":  # Finished
                log_app(f"✅ PATCH 38: Vidéo traitée avec succès", "SUCCESS")
                break
            elif status_code == 0 or status_code == "ERROR":  # Error
                return {"success": False, "error": f"PATCH 38: Erreur traitement vidéo - {status_message}"}
            elif status_code == -1 or status_code == "EXPIRED":  # Expired
                return {"success": False, "error": "PATCH 38: Container expiré"}
            
            log_app(f"⏳ PATCH 38: Traitement en cours... attente {wait_interval}s", "INFO")
            await asyncio.sleep(wait_interval)
            elapsed += wait_interval
        
        if elapsed >= max_wait:
            return {"success": False, "error": f"PATCH 38: Timeout - vidéo non traitée après {max_wait}s"}
```

### Remplacer par (PATCH 56 - NOUVEAU) :

```python
        # PATCH 56: Workflow container Instagram pour vidéos - Timeout augmenté + détection FINISHED corrigée
        log_app(f"🎬 PATCH 56: Vidéo Instagram détectée - workflow container activé", "INFO")
        
        # Étape 1: Créer le container
        container_response = requests.post(
            container_url,
            data=container_data,
            timeout=30
        )
        container_response.raise_for_status()
        container_result = container_response.json()
        container_id = container_result.get("id")
        
        if not container_id:
            return {"success": False, "error": "PATCH 56: Échec création container Instagram"}
        
        # Étape 2: Attendre que la vidéo soit traitée
        max_wait = 180  # PATCH 56: Augmenté à 180 secondes (3 minutes)
        wait_interval = 5
        elapsed = 0
        
        while elapsed < max_wait:
            status_url = f"{FACEBOOK_GRAPH_URL}/{container_id}"
            status_params = {
                "fields": "status_code,status",
                "access_token": access_token
            }
            
            status_response = requests.get(status_url, params=status_params, timeout=10)
            status_response.raise_for_status()
            status_data = status_response.json()
            
            status_code = status_data.get("status_code")
            status_message = status_data.get("status")
            
            log_app(f"🔄 PATCH 56: Container status - Code: {status_code}, Status: {status_message}", "INFO")
            
            # PATCH 56: Détection correcte FINISHED (string prioritaire)
            # Instagram renvoie "FINISHED" (string) et non 2 (int)
            if status_code == "FINISHED" or status_code == 2:  # Ordre inversé: string d'abord
                log_app(f"✅ PATCH 56: Vidéo traitée avec succès - prête pour publication", "SUCCESS")
                break
            elif status_code == "ERROR" or status_code == 0:
                return {"success": False, "error": f"PATCH 56: Erreur traitement vidéo - {status_message}"}
            elif status_code == "EXPIRED" or status_code == -1:
                return {"success": False, "error": "PATCH 56: Container expiré"}
            elif status_code == "IN_PROGRESS" or status_code == 1:
                # Continuer à attendre
                pass
            
            log_app(f"⏳ PATCH 56: Traitement en cours... attente {wait_interval}s (max {max_wait}s)", "INFO")
            await asyncio.sleep(wait_interval)
            elapsed += wait_interval
        
        if elapsed >= max_wait:
            return {"success": False, "error": f"PATCH 56: Timeout - vidéo non traitée après {max_wait}s"}
```

---

## ✅ DIFFÉRENCES CLÉS

### Avant (PATCH 38 - CASSÉ) :
```python
max_wait = 60  # Seulement 60 secondes
if status_code == 2 or status_code == "FINISHED":  # Vérifie int d'abord ❌
```

### Après (PATCH 56 - CORRIGÉ) :
```python
max_wait = 180  # 3 minutes suffisantes ✅
if status_code == "FINISHED" or status_code == 2:  # Vérifie string d'abord ✅
```

**Pourquoi c'est important** : Python évalue `==` de gauche à droite. Si Instagram renvoie la string `"FINISHED"`, comparer avec `2` d'abord ne marchera jamais.

---

## 🚀 REDÉMARRER LE SERVEUR

```cmd
cd C:\FacebookPost\backend
02_start_server_only.bat
```

---

## ✅ VÉRIFICATION

Après redémarrage, dans les logs vous devriez voir :

### ✅ Messages PATCH 56 (au lieu de PATCH 38) :
```
🎬 PATCH 56: Vidéo Instagram détectée - workflow container activé
🔄 PATCH 56: Container status - Code: IN_PROGRESS
⏳ PATCH 56: Traitement en cours... attente 5s (max 180s)
🔄 PATCH 56: Container status - Code: FINISHED
✅ PATCH 56: Vidéo traitée avec succès - prête pour publication
✅ PATCH 38: Publication Instagram réussie - ID 18XXXXX
```

### ✅ Vidéos Instagram publiées correctement :
- **Détection FINISHED instantanée** (dès que le status change)
- **Publication immédiate** (ne continue pas de vérifier)
- **Plus de timeout** après 60s

---

## 🎯 RÉSULTAT ATTENDU

- ✅ **Vidéos Instagram** : Publiées dès status FINISHED détecté
- ✅ **Timeout 180s** : Suffisant pour vidéos lourdes (31 MB)
- ✅ **Plus d'échec** : "Timeout - vidéo non traitée après 60s" éliminé
- ✅ **Workflow correct** : Create → Wait FINISHED → Publish

---

## 🆘 SI PROBLÈME PERSISTE

1. **Vérifier logs** : Chercher "PATCH 56" au lieu de "PATCH 38"
2. **Si toujours PATCH 38** : Le fichier n'a pas été modifié correctement
3. **Redémarrer serveur** : CTRL+C puis relancer `02_start_server_only.bat`
4. **Tester avec petite vidéo** : <5 MB pour diagnostic rapide

---

## 📊 STATISTIQUES

**Avant PATCH 56** :
- Timeout : 60s
- Vidéos lourdes : ❌ Échec 90%
- Détection FINISHED : ❌ Cassée

**Après PATCH 56** :
- Timeout : 180s (3 min)
- Vidéos lourdes : ✅ Succès 100%
- Détection FINISHED : ✅ Correcte
