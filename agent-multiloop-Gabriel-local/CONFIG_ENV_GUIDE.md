# Guide unique — Configurer la clé API Anthropic (Claude) pour Gabriel

> **Ce fichier remplace les 12 anciens guides (archivés dans `docs/archive/env_history/`).**

## TL;DR — 30 secondes

1. **Ouvrir** : `agent-multiloop-Gabriel-local/.env`
2. **Chercher** la balise :
   ```
   >>>  COLLEZ VOTRE CLE ANTHROPIC CLAUDE ICI  <<<
   ```
3. **Remplacer** la ligne :
   ```
   CLAUDE_API_KEY=COLLEZ-VOTRE-CLE-ICI
   ```
   par :
   ```
   CLAUDE_API_KEY=sk-ant-api03-...votre-cle-reelle
   ```
4. **Redémarrer Docker** :
   ```
   docker-compose down
   docker-compose up --build
   ```
5. **Vérifier** dans Gabriel :
   ```
   Philippe > env-check
   ```

## Pourquoi il y a UN SEUL .env (et pas plusieurs)

Le code de Gabriel (`src/core/config.py`) cherche un fichier `.env` dans cet ordre :

| Priorité | Chemin                                                    | Statut |
|----------|-----------------------------------------------------------|--------|
| **1**    | `<dossier courant>/.env`                                  | utilisé si tu lances depuis ce dossier |
| **2**    | `agent-multiloop-Gabriel-local/.env`                      | **emplacement officiel et recommandé** ✅ |
| 3        | `/home/agent/app/.env`                                    | fallback ancien chemin Docker          |

Dès que **l'un** de ces fichiers existe, les autres sont **ignorés**.

`docker-compose.yml` utilise aussi `env_file: - .env` (chemin **relatif** au compose) → pointe sur le **même** fichier `agent-multiloop-Gabriel-local/.env`. Donc :

> **Un seul fichier suffit : `agent-multiloop-Gabriel-local/.env`**.

## Fichiers à NE PAS confondre

| Fichier                                       | Rôle                                               |
|-----------------------------------------------|----------------------------------------------------|
| `agent-multiloop-Gabriel-local/.env`          | ✅ **LE bon fichier — c'est ici qu'on met la clé**  |
| `agent-multiloop-Gabriel-local/.env.example`  | Template (versionné dans Git, sans clé réelle)      |
| `backend/.env`                                | Sans rapport — config de l'app web Emergent.sh      |
| `frontend/.env`                               | Sans rapport — config de l'app web Emergent.sh      |
| `.env_backup/*.backup_*`                      | Backups historiques (archive, ne sert plus)         |

## Vérifier que la clé est bien lue

Dans Gabriel CLI, tapez :

```
Philippe > env-check
```

Vous verrez :
- La liste de **tous les .env détectés** dans l'arborescence
- **Lequel** est actif (chargé en mémoire)
- Si `CLAUDE_API_KEY` est **valide** (commence par `sk-ant-` et longueur > 30)
- Si `OPENAI_API_KEY` est valide (fallback)
- **Instructions exactes** pour corriger si invalide

## Obtenir une clé Anthropic

1. Aller sur https://console.anthropic.com/settings/keys
2. Cliquer "Create Key"
3. Copier la clé (commence par `sk-ant-api03-...`)
4. La coller dans `agent-multiloop-Gabriel-local/.env` à la ligne `CLAUDE_API_KEY=`

## Chaîne LLM de Gabriel

```
1. Ollama (local, timeout 10s)
       ↓ si indisponible
2. Claude Anthropic (CLAUDE_API_KEY)   ← PRIORITAIRE pour HOL/maths
       ↓ si indisponible
3. OpenAI (OPENAI_API_KEY)             ← fallback ultime
```

Sans `CLAUDE_API_KEY` valide, Gabriel saute directement de Ollama à OpenAI.
