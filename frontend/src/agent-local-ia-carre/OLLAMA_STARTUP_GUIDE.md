# Guide de Démarrage Ollama - Agent Multi-Loop & Local

## **⚠️ Situation actuelle**

- ✅ Docker Desktop est installé et fonctionne
- ❌ **Ollama n'est PAS démarré** → Port 11434 fermé → `Connection refused`
- ✅ Fallback OpenAI fonctionne correctement (d'où les réponses en logs)

---

## **🚀 PROCÉDURE RAPIDE (Windows)**

### **Option 1 : Lancement via le Script (Recommandé)**

```powershell
# 1. Ouvrir PowerShell EN TANT QU'ADMINISTRATEUR
# 2. Naviguer vers le dossier local_ai_agent
cd C:\agent-local-ia-carre\local_ai_agent

# 3. Lancer le script de démarrage interactif
.\docker-start.bat
```

**Menu interactif :**
```
1. Lancer l'agent (mode GUI)
2. Lancer l'agent (mode CLI) ← CHOISIR CETTE OPTION
3. Arrêter tous les services
4. Voir les logs
5. Reconstruire les images
6. Quitter
```

**Sélectionner : `2` (mode CLI)**

### **Option 2 : Commandes directes Docker**

```powershell
# 1. Démarrer les services Ollama + init
cd C:\agent-local-ia-carre\local_ai_agent

docker compose -f docker-compose.cli.yml up -d ollama ollama-init

# 2. Vérifier que les conteneurs démarrent
docker compose -f docker-compose.cli.yml ps

# 3. Attendre 30-45 secondes (téléchargement du modèle llama3.2)
# Vous verrez dans docker stats la consommation de CPU/RAM

# 4. Vérifier qu'Ollama répond
curl http://localhost:11434/api/tags

# 5. Lancer l'agent multi-loop
cd C:\agent-local-ia-carre\agent-multiloop-local
python -m src.main --goal "Calculer SA(5) et SB(5)"
```

---

## **🔍 Diagnostic - Tester si Ollama répond**

### **Script PowerShell de diagnostic**

```powershell
# Vérifier la disponibilité d'Ollama
function Test-Ollama {
    Write-Host "Vérification de la disponibilité d'Ollama..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" `
                                      -TimeoutSec 5 `
                                      -ErrorAction Stop
        Write-Host "✅ Ollama est DISPONIBLE!" -ForegroundColor Green
        Write-Host "Modèles disponibles:" -ForegroundColor Green
        $response.Content | ConvertFrom-Json | Select -ExpandProperty models | ForEach-Object { 
            Write-Host "  - $($_.name) (size: $($_.size / 1GB)GB)" 
        }
        return $true
    } catch {
        Write-Host "❌ Ollama n'est PAS disponible!" -ForegroundColor Red
        Write-Host "Erreur: $_" -ForegroundColor Red
        return $false
    }
}

Test-Ollama
```

### **Vérification par Docker**

```bash
# Voir l'état des conteneurs
docker ps

# Voir les logs d'Ollama
docker logs ollama -f

# Vérifier la connexion au service ollama
docker compose exec ollama ollama list
```

---

## **⏱️ Temps d'attente attendus**

| Étape | Durée | Note |
|-------|-------|------|
| Démarrage Docker Desktop | ~5-10 sec | Automatique |
| Création images Docker | ~30 sec | Première fois seulement |
| Démarrage conteneur Ollama | ~10 sec | - |
| **Téléchargement modèle llama3.2** | **~5-10 min** | ⚠️ **Longue ! Dépend de votre connexion** |
| Initialisation complète | ~2 min | Services prêts |
| **TEMPS TOTAL** | **~15-25 min** | **Première fois** |

**Les fois suivantes :** ~30 secondes (modèle déjà téléchargé)

---

## **📊 Configuration système recommandée**

Pour **agent-multiloop-local** + **Ollama llama3.2** :

- **RAM** : 16 GB minimum (8 GB pour Ollama + 4 GB pour l'agent)
- **Stockage** : 30 GB libres (modèles Ollama ~8 GB)
- **CPU** : 4 cores minimum
- **Docker Desktop** : Allouer **8 GB de RAM** minimum

**Comment vérifier/augmenter :**
```
Docker Desktop → Settings → Resources → Memory
```

---

## **🛠️ Commandes utiles une fois démarré**

```bash
# Voir les logs en temps réel
docker compose logs -f ollama

# Voir les stats (RAM/CPU)
docker stats

# Redémarrer Ollama
docker compose restart ollama

# Arrêter tous les services
docker compose down

# Voir les modèles disponibles
docker compose exec ollama ollama list

# Télécharger un autre modèle (ex: Mistral)
docker compose exec ollama ollama pull mistral

# Supprimer un modèle
docker compose exec ollama ollama rm llama3.2
```

---

## **🔴 Dépannage**

### **Problème : "Connection refused" sur 11434**

```bash
# 1. Vérifier que le conteneur tourne
docker ps | grep ollama

# 2. Si absent, redémarrer
docker compose -f docker-compose.cli.yml up -d ollama ollama-init

# 3. Voir les erreurs
docker logs ollama
```

### **Problème : "Out of Memory"**

```bash
# 1. Augmenter la RAM dans Docker Desktop
Docker Desktop → Settings → Resources → Memory → 16 GB

# 2. Redémarrer Docker Desktop
```

### **Problème : Le modèle ne se télécharge pas**

```bash
# 1. Vérifier la connexion Internet
ping 8.8.8.8

# 2. Vérifier l'espace disque
docker system df

# 3. Relancer le téléchargement
docker compose exec ollama ollama pull llama3.2 --verbose
```

---

## **📝 Architecture actuellement active**

```
┌─ Docker Desktop ────────────────────────┐
│                                         │
│  ┌─ agent-multiloop-local              │
│  │  (Python 3.11 - votre code)         │
│  │  ↓                                   │
│  │  Ollama client: http://localhost:11434
│  │                                      │
│  └─ Fallback: OpenAI GPT-4o-mini      │
│                                         │
│  ┌─ Conteneur Ollama                  │
│  │  Port: 11434                        │
│  │  Modèle: llama3.2:latest           │
│  │  Stockage: /root/.ollama (volume)  │
│  └────────────────────────────────────│
│                                         │
└─────────────────────────────────────────┘
```

---

## **✅ Vérification finale**

Une fois démarré, tester :

```powershell
# 1. Ollama répond
curl http://localhost:11434/api/tags

# 2. Agent reçoit une réponse
cd C:\agent-local-ia-carre\agent-multiloop-local
python -m src.main --goal "Quelle est la valeur de SA(3)?" --verbose

# 3. Vérifier que vous ne voyez PLUS "Connection refused"
# mais plutôt les réponses du modèle local Ollama
```

---

## **📚 Ressources**

- [Docker Desktop Download](https://www.docker.com/products/docker-desktop/)
- [Ollama Documentation](https://ollama.ai/library)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
