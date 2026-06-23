# 🚀 SCRIPT D'INJECTION DES CLÉS API

## Comment utiliser

### Étape 1: Prépare tes clés

Avant de lancer le script, prépare:

1. **Clé Claude** depuis https://console.anthropic.com/
   - Format: `sk-ant-XXXXXXXXXXXXX...`
   - Copie-la quelque part accessible

2. **Clé OpenAI** depuis https://platform.openai.com/api-keys
   - Format: `sk-XXXXXXXXXXXXX...` ou `sk-proj-XXXXXXXXXXXXX...`
   - Copie-la quelque part accessible

### Étape 2: Exécute le script

Ouvre PowerShell et tape:

```powershell
cd "C:\agent-multiloop-Gabriel-local-final"
python inject_api_keys.py
```

### Étape 3: Suis les instructions

Le script va:

1. **Te demander ta clé Claude**
   - Colle la clé (elle sera cachée à l'écran)
   - Appuie sur Entrée

2. **Te demander ta clé OpenAI**
   - Colle la clé (elle sera cachée à l'écran)
   - Appuie sur Entrée

3. **Te demander confirmation**
   - Tape: `oui` puis Entrée

4. **Injecter les clés automatiquement**
   - Les clés restent SUR TON ORDINATEUR
   - Elles sont placées dans les deux fichiers `.env`

5. **Redémarrer Docker**
   - Automatique

### Étape 4: Attend 60 secondes

Docker relance. Les services mettent du temps à démarrer.

### Étape 5: Teste

Envoie une requête à Gabriel:

```
"Quel est le rapport spectral entre les nombres premiers 7, 13 et 19, 47?"
```

### Résultat attendu

Les logs doivent montrer:

```
[INFO] 🔴 Tentative 2/3: Claude-3.5-Sonnet - timeout 60s
[INFO] ✅ Claude a répondu
```

✅ Claude marche!

---

## ✅ Avantages de cette approche

- ✅ Ta clé ne quitte JAMAIS ton ordinateur
- ✅ Aucune transmission via Internet
- ✅ Tout se fait en local
- ✅ Complètement sécurisé
- ✅ Automatisé (pas de risque d'erreur manuelle)

---

## ⚠️ Si quelque chose échoue

### Erreur: "Fichier non trouvé"
- Vérifie que tu es dans le bon dossier
- Le script doit être exécuté depuis: `C:\agent-multiloop-Gabriel-local-final`

### Erreur: "La clé Claude doit commencer par sk-ant-"
- Tu n'as pas copié la bonne clé
- Va sur https://console.anthropic.com/ et récupère une vraie clé

### Erreur: "docker-compose non trouvé"
- Docker n'est pas installé ou pas dans le PATH
- Redémarre manuellement: 
  ```powershell
  cd "C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local"
  docker-compose down
  docker-compose up
  ```

---

## 🎯 C'est la meilleure approche!

Ce script:
1. Teste que les clés ont le bon format
2. Les place aux DEUX endroits (racine + container)
3. Redémarre Docker automatiquement
4. Garde tout LOCAL et SÉCURISÉ

Exécute-le maintenant! 🚀
