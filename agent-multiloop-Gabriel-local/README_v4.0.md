# Gabriel Multi-Loop Agent v4.0

## Vue d'ensemble

Gabriel v4.0 ajoute l'**intégration HTTP API et Isabelle CLI** pour permettre:

1. **Communication avec www.universestaucarre.com** (votre logiciel web sur emergent.sh)
2. **Mode CLI pour Isabelle** (batch processing, pas de GUI Jed it)
3. **Synchronisation des résultats** entre Gabriel local et Gabriel web
4. **Endpoints pour les 4 IAs** (GPT4, Claude, Gemini, Gabriel)

---

## Fichiers modifiés/créés

### Fichiers NEW (v4.0)

| Fichier | Description |
|---------|-------------|
| `src/api/gabriel_http_api.py` | **API HTTP Flask** - Endpoints pour requêtes externes |
| `scripts/isabelle-integration.sh` | **Script CLI Isabelle** - Traite les fichiers .thy en batch |
| `INTEGRATION_UNIVERSESTAUCARRE.md` | **Guide d'intégration complet** - Comment connecter www.universestaucarre.com |
| `main_cli.py` (modifié) | Support pour lancer CLI + API simultanément |
| `docker-compose.yml` (modifié) | Port 8000 exposé, Isabelle en mode CLI batch |
| `requirements.txt` (modifié) | Ajout de Flask + flask-cors + requests |

---

## Mode de lancement

### Avant (v3.x)

```bash
docker-compose up -d  # CLI interactif uniquement
```

### Maintenant (v4.0)

```bash
# Mode 1: CLI interactif + API HTTP en parallèle (DEFAUT)
docker-compose up -d

# Mode 2: API HTTP SEULE (pour www.universestaucarre.com)
export GABRIEL_HTTP_ONLY=1
docker-compose up -d

# Mode 3: CLI SEUL (ancien comportement)
export GABRIEL_HTTP_API=0
docker-compose up -d
```

---

## Endpoints HTTP

Gabriel écoute maintenant sur `http://localhost:8000` (ou votre IP):

### 1. POST /query - Poser une question

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quel est le 25eme nombre premier?",
    "source": "universestaucarre"
  }'
```

Réponse:
```json
{
  "answer": "Le 25ème nombre premier est 97.",
  "confidence": 0.95,
  "iterations": 3,
  "best_score": 9.0,
  "source": "Gabriel v4.0",
  "timestamp": "2025-01-15T14:35:00.000000"
}
```

### 2. POST /sync/universestaucarre - Synchroniser avec le site web

```bash
curl -X POST http://localhost:8000/sync/universestaucarre \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid-abc123",
    "question": "La physique quantique...",
    "results": {
      "gpt4": "...",
      "claude": "...",
      "gemini": "...",
      "gabriel_web": "..."
    }
  }'
```

### 3. GET /health - Vérifier l'état

```bash
curl http://localhost:8000/health
```

Réponse:
```json
{
  "status": "online",
  "service": "Gabriel v4.0",
  "pipeline": "active",
  "timestamp": "2025-01-15T14:35:00.000000"
}
```

---

## Isabelle CLI (v4.0)

### Avant: GUI Jed it (interactive)

```bash
docker exec -it isabelle bash
isabelle jedit
```

### Maintenant: Mode batch CLI

```bash
docker-compose --profile isabelle up -d

# Le script isabelle-integration.sh:
# 1. Surveille /theories pour les fichiers .thy
# 2. Les traite avec: isabelle process -o quick -T thy_check
# 3. Envoie les résultats à Gabriel via HTTP POST
```

Avantages du mode CLI:
- ✅ Pas de GUI nécessaire (fonctionnne sur serveurs headless)
- ✅ Communication directe avec Gabriel HTTP API
- ✅ Résultats stockés automatiquement
- ✅ Scalable pour www.universestaucarre.com

---

## Réseau Docker (v4.0)

### Architecture

```
HOST (Windows)
  ├─ Gabriel: localhost:8000 (exposé au host)
  └─ Ollama:  localhost:11434
      ↓
Docker Network (agent-network - bridge)
  ├─ llm-agent-multiloop (Gabriel - Python)
  ├─ isabelle (HOL - mode CLI)
  └─ ollama (LLM - Llama 3.2)
```

### Comment www.universestaucarre.com accède à Gabriel

**Option A: Même machine (localhost)**
```javascript
const url = "http://localhost:8000";
```

**Option B: Autre machine sur le réseau local**
```javascript
const url = "http://192.168.1.100:8000";  // IP locale
```

**Option C: Via un domaine personnalisé**
```javascript
const url = "http://gabriel-local.home:8000";
```

---

## Variables d'environnement (v4.0)

| Variable | Default | Description |
|----------|---------|-------------|
| `GABRIEL_HTTP_PORT` | 8000 | Port HTTP pour l'API |
| `GABRIEL_HOST` | 0.0.0.0 | Interface d'écoute (0.0.0.0 = accessible de l'extérieur) |
| `GABRIEL_HTTP_ONLY` | 0 | Si 1 = API seule (pas de CLI) |
| `GABRIEL_HTTP_API` | 1 | Si 1 = Activer l'API; 0 = CLI seul |

---

## Test rapide (v4.0)

```bash
# 1. Lancer Gabriel + Isabelle
cd C:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local
docker-compose --profile isabelle up -d

# 2. Attendre le démarrage (~30s)
sleep 30

# 3. Tester l'API
curl http://localhost:8000/health

# 4. Poser une question
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Qu'"'"'est-ce que l'"'"'univers au carré?", "source": "test"}'

# 5. Voir les logs
docker logs llm-agent-multiloop-run | tail -20
docker logs isabelle | tail -20
```

---

## Guide d'intégration www.universestaucarre.com

Voir: **INTEGRATION_UNIVERSESTAUCARRE.md**

Contient:
- Étapes de configuration
- Exemples de code JavaScript/Node.js
- Synchronisation des 4 IAs
- Troubleshooting et FAQ

---

## Changelog (v4.0)

### ✅ Nouveautés
- HTTP API Flask avec 5 endpoints
- Isabelle CLI (batch mode, pas de GUI)
- Support pour synchronisation avec www.universestaucarre.com
- Mode hybride: CLI + API en parallèle
- CORS activé pour accepter requêtes externes
- Docker network configuré pour communications inter-services
- Logging complet pour débug

### ⚠️ Breaking changes
- ~~Isabelle GUI (Jed it) remplacée par CLI~~ (optional sur profil)
- Port 8000 maintenant exposé par défaut

### 🔧 Corrections
- Seuil du debugger à -999999 (incidence ZERO)
- Décodage UTF-8 correct pour les fichiers
- Endpoints JSON bien formatés

---

## Architecture des services (docker-compose.yml v4.0)

```yaml
services:
  llm-agent-multiloop:
    # Gabriel - expose port 8000
    ports:
      - "8000:8000"
    environment:
      - GABRIEL_HTTP_PORT=8000
      - GABRIEL_HOST=0.0.0.0

  isabelle:
    # Mode CLI batch - communique avec Gabriel
    profiles: ["isabelle"]
    command: ["/scripts/isabelle-integration.sh"]
    environment:
      - GABRIEL_HOST=llm-agent-multiloop
      - GABRIEL_PORT=8000
```

---

## Dépannage

### Gabriel n'est pas accessible sur le port 8000

```bash
# Vérifier que le port est exposé
docker ps | grep 8000

# Tester depuis le conteneur
docker exec llm-agent-multiloop-run curl http://0.0.0.0:8000/health

# Vérifier les logs
docker logs llm-agent-multiloop-run | grep "8000"
```

### Isabelle CLI ne démarre pas

```bash
# Vérifier les logs
docker logs isabelle

# Le script isabelle-integration.sh utilise le polling si inotify n'est pas disponible
# C'est normal et fonctionne quand même
```

### www.universestaucarre.com ne peut pas atteindre Gabriel

```bash
# 1. Obtenir l'IP locale
ipconfig | grep "IPv4 Address"

# 2. Utiliser cette IP au lieu de localhost:
# const GABRIEL_URL = "http://192.168.1.100:8000";

# 3. Vérifier la firewall Windows
# Autoriser le port 8000 (ou le configurer avec reverse proxy)
```

---

## Prochaines étapes

- [ ] WebSocket pour streaming temps réel
- [ ] Cache Redis pour éviter recalculs
- [ ] Rate limiting pour www.universestaucarre.com
- [ ] Authentification JWT pour sécuriser l'API
- [ ] Dashboard web pour monitorer Gabriel

---

## Documentation

- `docker-compose.yml` - Configuration des services
- `scripts/isabelle-integration.sh` - Script Isabelle CLI
- `src/api/gabriel_http_api.py` - Code source de l'API
- `main_cli.py` - Point d'entrée avec support HTTP
- `INTEGRATION_UNIVERSESTAUCARRE.md` - Guide complet d'intégration

---

**Version:** 4.0 (2025-01-15)  
**Status:** Production-ready  
**Auteur:** Gordon (Docker Assistant)
