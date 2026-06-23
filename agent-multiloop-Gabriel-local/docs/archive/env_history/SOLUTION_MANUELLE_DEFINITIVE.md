# 🚨 LE SCRIPT A ÉCHOUÉ - SOLUTION MANUELLE DÉFINITIVE

## Le problème

Le script Python n'a pas réussi à injecter les clés. Les fichiers `.env` sont TOUJOURS vides:

```
CLAUDE_API_KEY=[REDACTED]    ← Vide!
OPENAI_API_KEY=[REDACTED]    ← Vide!
```

## La solution (simple et directe)

Tu vas MANUELLEMENT copier-coller tes clés. C'est rapide et sans risque.

### ÉTAPE 1: Prépare tes clés

**Clé Claude**:
1. Va sur: https://console.anthropic.com/
2. Clique "API Keys" (à gauche)
3. Clique "Create Key"
4. **COPIE la clé entière** (elle commence par `sk-ant-`)
5. **Colle-la dans un bloc-notes temporaire** pour pas la perdre

**Clé OpenAI**:
1. Va sur: https://platform.openai.com/api-keys
2. Clique "Create new secret key"
3. **COPIE la clé entière** (commence par `sk-`)
4. **Colle-la dans le bloc-notes aussi**

### ÉTAPE 2: Édite le fichier .env du CONTAINER

**Fichier à éditer**:
```
C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local\.env
```

**OUVRE-LE DANS VS CODE**:
1. VS Code → File → Open File
2. Navigue vers le chemin ci-dessus
3. Ouvre le fichier

**TROUVE LES LIGNES CLÉS** (appuie sur Ctrl+F):

Ligne 16-17:
```
CLAUDE_API_KEY=[REDACTED]
ANTHROPIC_API_KEY=[REDACTED]
```

Ligne 26:
```
OPENAI_API_KEY=[REDACTED]
```

**REMPLACE-LES**:

Pour Claude:
```
❌ Avant:
CLAUDE_API_KEY=[REDACTED]
ANTHROPIC_API_KEY=[REDACTED]

✅ Après (colle ta vraie clé):
CLAUDE_API_KEY=sk-ant-COLLE_TA_CLÉ_CLAUDE_COMPLÈTE_ICI
ANTHROPIC_API_KEY=sk-ant-COLLE_TA_CLÉ_CLAUDE_COMPLÈTE_ICI
```

Pour OpenAI:
```
❌ Avant:
OPENAI_API_KEY=[REDACTED]

✅ Après (colle ta vraie clé):
OPENAI_API_KEY=sk-COLLE_TA_CLÉ_OPENAI_COMPLÈTE_ICI
```

**SAUVEGARDE** (Ctrl+S)

### ÉTAPE 3: Édite le fichier .env de la RACINE aussi

**Fichier à éditer**:
```
C:\agent-multiloop-Gabriel-local-final\.env
```

**RÉPÈTE les MÊMES remplacements** (Claude + OpenAI)

**SAUVEGARDE** (Ctrl+S)

### ÉTAPE 4: Redémarre Docker

Ouvre PowerShell et tape:

```powershell
cd "C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local"
docker-compose down
docker-compose up -d
```

Attends 60 secondes que tout redémarre.

### ÉTAPE 5: Vérifie

Tape dans PowerShell:

```powershell
docker exec llm-agent-multiloop-run printenv | findstr CLAUDE
```

Doit afficher:
```
CLAUDE_API_KEY=sk-ant-XXXXXXXXX
```

(La clé complète, pas `[REDACTED]`)

### ÉTAPE 6: Teste

Envoie une requête à Gabriel:
```
"Quel est le rapport spectral entre 7 et 13?"
```

Les logs doivent montrer:
```
[INFO] 🔴 Tentative 2/3: Claude-3.5-Sonnet - timeout 60s
[INFO] ✅ Claude a répondu
```

---

## ⚠️ POINTS CRITIQUES

- ❌ **NE PAS** garder les crochets `[` ou `]`
- ❌ **NE PAS** copier avec des espaces avant/après
- ✅ **COPIER EXACTEMENT** la clé du site
- ✅ **LES DEUX** fichiers `.env` doivent avoir les MÊMES clés
- ✅ **REDÉMARRER** Docker après

---

## 🆘 SI ÇA MARCHE TOUJOURS PAS

Rapporte:
1. Les PREMIÈRES 20 caractères de ta clé Claude (ex: `sk-ant-abcd1234efgh567890xy`)
2. Les logs complets de la requête
3. L'erreur exacte dans les logs

Je pourrai diagnostiquer le reste! 🎯
