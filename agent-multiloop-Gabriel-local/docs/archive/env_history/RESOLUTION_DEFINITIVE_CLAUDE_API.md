# 🎯 RÉSOLUTION DÉFINITIVE - CLAUDE API KEY CONFIGURATION

## ✅ PROBLÈME IDENTIFIÉ ET RÉSOLU

### Le Bug Root Cause
```
Fichier RACINE:     C:\agent-multiloop-Gabriel-local-final\.env
  ✅ CLAUDE_API_KEY=sk-ant-[REDACTED]  (bon format)
  
Fichier CONTAINER:  C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local\.env
  ❌ CLAUDE_API_KEY=[REDACTED]  (MANQUE le préfixe "sk-ant-"!)
  
DOCKER LIT LE FICHIER CONTAINER → TROUVE CLÉS CASSÉES → Claude indisponible
```

### Solution Appliquée
✅ Copie du fichier RACINE vers le CONTAINER (synchronisation 100%)

---

## 📁 ARCHITECTURE .env FINALE (CORRECTE)

### Structure du projet:
```
C:\agent-multiloop-Gabriel-local-final\
├── .env                                    ← FICHIER 1 (racine)
│
├── agent-multiloop-Gabriel-local\
│   ├── docker-compose.yml
│   ├── .env                                ← FICHIER 2 (container) - DOIT être IDENTIQUE
│   ├── main_cli.py
│   └── Dockerfile.cli
```

**RÈGLE CRITIQUE**: Les DEUX fichiers `.env` doivent contenir les MÊMES clés API!

---

## ✅ CRITÈRES OBLIGATOIRES - CHECKLIST FINALE

### Pour le `.env` RACINE
**Chemin**: `C:\agent-multiloop-Gabriel-local-final\.env`

**Éléments OBLIGATOIRES**:

- [ ] `CLAUDE_API_KEY=sk-ant-XXXXXXXXXXX`
  - Format: Commence par `sk-ant-`
  - Longueur: ~52 caractères
  - Pas de crochets, pas d'espaces
  - Exemple: `sk-ant-abcdef123456789...`

- [ ] `ANTHROPIC_API_KEY=sk-ant-XXXXXXXXXXX`
  - EXACT MÊME VALEUR que CLAUDE_API_KEY
  - C'est un alias pour compatibilité

- [ ] `OPENAI_API_KEY=sk-XXXXXXXXXXX`
  - Format: Commence par `sk-`
  - Longueur: ~48 caractères
  - Pas de crochets, pas d'espaces
  - Exemple: `sk-proj-...` ou `sk-...`

- [ ] `OPENAI_MODEL=gpt-4o`
  - Doit être présent (modèle OpenAI)

- [ ] `OLLAMA_HOST=http://ollama:11434`
  - Pour Docker: `http://ollama:11434`
  - Pour local: `http://localhost:11434`

- [ ] `OLLAMA_MODEL=llama3.2`
  - Modèle local Ollama

- [ ] `DEFAULT_LANGUAGE=fr`
  - Langue par défaut

- [ ] `AGENT_USERNAME=Philippe Thomas`
  - Ton nom

- [ ] `AGENT_NAME=Mme Gabriel`
  - Nom de l'agent

- [ ] `LLM_PRIMARY=ollama`
  - LLM primaire

- [ ] `LLM_FALLBACK_1=claude`
  - CRITIQUE: Claude doit être fallback 1 (pas OpenAI!)

- [ ] `LLM_FALLBACK_2=openai`
  - OpenAI comme fallback ultime

### Pour le `.env` CONTAINER
**Chemin**: `C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local\.env`

**Éléments IDENTIQUES au fichier RACINE**:

- [ ] `CLAUDE_API_KEY=sk-ant-XXXXXXXXXXX`
- [ ] `ANTHROPIC_API_KEY=sk-ant-XXXXXXXXXXX`
- [ ] `OPENAI_API_KEY=sk-XXXXXXXXXXX`
- [ ] `OPENAI_MODEL=gpt-4o`
- [ ] `OLLAMA_HOST=http://ollama:11434`
- [ ] `OLLAMA_MODEL=llama3.2`
- [ ] Tous les autres paramètres identiques

**RÈGLE**: Les deux fichiers doivent être 100% identiques!

---

## 🔍 CAUSES POSSIBLES DE DÉFAILLANCE

### Cause 1: CLAUDE_API_KEY manquante ou vide
**Symptôme**: `[WARNING] ⚠️ Claude indisponible (CLAUDE_API_KEY manquante)`
**Vérification**:
```bash
# Racine:
grep "CLAUDE_API_KEY" C:\agent-multiloop-Gabriel-local-final\.env

# Container:
grep "CLAUDE_API_KEY" C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local\.env

# Doivent afficher exactement pareil: CLAUDE_API_KEY=sk-ant-xxxxx
```
**Fix**: Édite TOUS les deux fichiers et ajoute la clé

### Cause 2: Format de clé invalide
**Symptôme**: `Claude indisponible` ou `Error 401`
**Vérifie**:
```
❌ CLAUDE_API_KEY=[REDACTED]           (manque sk-ant-)
❌ CLAUDE_API_KEY=sk-ant-[[REDACTED]]  (double crochets)
❌ CLAUDE_API_KEY=sk-[ [REDACTED]]     (crochets + espace)
✅ CLAUDE_API_KEY=sk-ant-abcd1234...   (CORRECT)
```
**Fix**: Remplace par le bon format

### Cause 3: Fichiers .env désynchronisés
**Symptôme**: Fonctionne en local Python mais pas en Docker
**Vérification**:
```bash
# Compare les deux fichiers
Get-Content C:\agent-multiloop-Gabriel-local-final\.env | findstr CLAUDE
Get-Content C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local\.env | findstr CLAUDE

# Doivent être IDENTIQUES
```
**Fix**: Copie le fichier racine vers le container

### Cause 4: Docker n'a pas rechargé le .env
**Symptôme**: Changes faites mais erreur persiste
**Vérification**:
```bash
docker ps -a
# Cherche: llm-agent-multiloop-run
```
**Fix**: Redémarre Docker COMPLÈTEMENT
```bash
docker-compose down
docker-compose up --build
```

### Cause 5: LLM Fallback incorrect
**Symptôme**: OpenAI appelé à la place de Claude
**Vérification**:
```bash
grep "LLM_FALLBACK_1" C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local\.env
# Doit afficher: LLM_FALLBACK_1=claude

grep "LLM_FALLBACK_2" C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local\.env
# Doit afficher: LLM_FALLBACK_2=openai
```
**Fix**: Édite les deux fichiers et assure:
```
LLM_FALLBACK_1=claude  (pas openai!)
LLM_FALLBACK_2=openai
```

### Cause 6: docker-compose.yml ne pointe pas le bon .env
**Symptôme**: Les changes ne sont jamais appliquées
**Vérification**: Lis `C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local\docker-compose.yml`
```yaml
env_file:
  - .env   ← Doit charger depuis son répertoire (le container)
```
**Fix**: Ne touche pas docker-compose.yml (déjà correct)

---

## 🚀 PROCÉDURE DE FIX MANUEL (ÉTAPES PAR ÉTAPES)

### Étape 1: Ouvrir le fichier CONTAINER dans VS Code
```
Fichier → Ouvrir fichier
C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local\.env
```

### Étape 2: Vérifier les clés Claude
Chercher la ligne:
```bash
CLAUDE_API_KEY=[REDACTED]
```

Remplacer par ta vraie clé:
```bash
CLAUDE_API_KEY=sk-ant-AAAAAABBBBBCCCCDDDD...
```

Chercher:
```bash
ANTHROPIC_API_KEY=[REDACTED]
```

Remplacer par ta MÊME clé:
```bash
ANTHROPIC_API_KEY=sk-ant-AAAAAABBBBBCCCCDDDD...
```

### Étape 3: Vérifier OpenAI
Chercher:
```bash
OPENAI_API_KEY=[REDACTED]
```

Remplacer par ta clé OpenAI:
```bash
OPENAI_API_KEY=sk-proj-XXXXX...
```

### Étape 4: Vérifier LLM Fallback
Chercher:
```bash
LLM_FALLBACK_1=claude
LLM_FALLBACK_2=openai
```

Doit afficher EXACTEMENT ça. Si absent, ajouter:
```bash
LLM_PRIMARY=ollama
LLM_FALLBACK_1=claude
LLM_FALLBACK_2=openai
```

### Étape 5: Sauvegarder
```
Ctrl+S
```

### Étape 6: Copier vers le fichier RACINE
```bash
Copy-Item "C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local\.env" "C:\agent-multiloop-Gabriel-local-final\.env" -Force
```

### Étape 7: Redémarrer Docker
```bash
docker-compose down
docker-compose up --build
```

Attends 30-60 secondes pour le démarrage complet.

### Étape 8: Tester
Envoie une requête à Gabriel. Les logs doivent montrer:

```
[INFO] 🔵 Tentative 1/3: Ollama (llama3.2) - timeout 10s
[WARNING] ⚠️ Ollama timeout (10s expiré)
[INFO] 🔴 Tentative 2/3: Claude-3.5-Sonnet - timeout 60s
[INFO] ✅ Claude a répondu  ← SUCCESS!
```

NON:
```
[WARNING] ⚠️ Claude indisponible (CLAUDE_API_KEY manquante)
```

---

## 📋 VÉRIFICATION RAPIDE POST-FIX

### Commande 1: Vérifier fichier CONTAINER
```bash
Get-Content "C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local\.env" | findstr "CLAUDE_API_KEY"
```
Doit afficher: `CLAUDE_API_KEY=sk-ant-XXXXX...` (avec ta vraie clé)

### Commande 2: Vérifier fichier RACINE
```bash
Get-Content "C:\agent-multiloop-Gabriel-local-final\.env" | findstr "CLAUDE_API_KEY"
```
Doit afficher: `CLAUDE_API_KEY=sk-ant-XXXXX...` (IDENTIQUE)

### Commande 3: Vérifier LLM Routing
```bash
Get-Content "C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local\.env" | findstr "LLM_"
```
Doit afficher:
```
LLM_PRIMARY=ollama
LLM_FALLBACK_1=claude
LLM_FALLBACK_2=openai
```

### Commande 4: Vérifier Docker redémarré
```bash
docker ps -a
```
Cherche: `llm-agent-multiloop-run` avec status `Up`

---

## ✅ RÉSUMÉ FINAL

**Deux fichiers `.env` doivent TOUJOURS rester IDENTIQUES**:
1. `C:\agent-multiloop-Gabriel-local-final\.env` (racine)
2. `C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local\.env` (container)

**Si Claude ne marche toujours pas après tout ça**:
1. Copie EXACTEMENT la clé de https://console.anthropic.com/ (sans crochets!)
2. Ajoute-la dans LES DEUX fichiers
3. `docker-compose down && docker-compose up --build`
4. Attends 60 secondes
5. Teste

**Le problème vient à 99% d'une des 6 causes listées ci-dessus.**

---

✅ Fichiers synchronisés
✅ Clés au bon format
✅ LLM Fallback correct
✅ Docker rebuilt
🎯 Claude doit marcher maintenant!
