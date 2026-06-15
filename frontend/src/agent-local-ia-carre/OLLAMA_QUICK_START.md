# ⚡ DÉMARRAGE ULTRA-RAPIDE - Ollama

## **3 étapes pour que Ollama réponde**

### **ÉTAPE 1 : Exécuter le script de démarrage**

Sur Windows, **double-cliquez** :
```
C:\agent-local-ia-carre\ollama-start.bat
```

Ou en **PowerShell** :
```powershell
cd C:\agent-local-ia-carre
.\ollama-start.bat
```

**Résultat attendu :**
```
[OK] Docker detecte
[OK] Docker Compose detecte
[OK] Repertoire: C:\agent-local-ia-carre\local_ai_agent

Demarrage d'Ollama (docker compose)...
ATTENTION: Cela peut prendre 15-25 minutes la PREMIERE FOIS

✅ OLLAMA OPERATIONNEL!
Modeles:
  • llama3.2:latest
```

---

### **ÉTAPE 2 : Attendre le téléchargement (première fois)**

- ⏱️ **Première exécution :** 15-25 minutes (le modèle llama3.2 ~8 GB se télécharge)
- 🚀 **Exécutions suivantes :** ~30 secondes

**Comment monitorer :**
```powershell
# Voir les logs en temps réel
docker logs ollama -f

# Voir l'utilisation CPU/RAM
docker stats

# Vérifier les conteneurs actifs
docker compose ps
```

---

### **ÉTAPE 3 : Lancer vos agents**

Une fois Ollama **OPÉRATIONNEL**, exécutez vos agents :

```powershell
# Agent Multi-Loop
cd C:\agent-local-ia-carre\agent-multiloop-local
python -m src.main --goal "Calculer SA(5) et SB(5)" --verbose

# OU Agent Local
cd C:\agent-local-ia-carre\local_ai_agent
python math-agent-cli.py
```

**Résultat attendu :**
```
[INFO] Ollama response in 2341ms (1250 chars)
[INFO] === OUTER LOOP iteration 1/5 ===
[INFO] ReAct THOUGHT [step 1]: Calculer SA(5), SB(5)...
✅ Vous verrez les réponses du modèle local Ollama
```

---

## **🆘 Si ça ne marche pas**

### **A. Ollama reste en "Connection refused"**

```powershell
# Tester manuellement
docker compose -f docker-compose.cli.yml up -d ollama ollama-init

# Attendre 30 sec
Start-Sleep -Seconds 30

# Vérifier les logs
docker logs ollama -f

# Voir l'état des conteneurs
docker compose ps
```

### **B. Message "Out of Memory"**

Docker n'a pas assez de RAM alloué.

**Correction :**
1. Ouvrir **Docker Desktop**
2. Aller à **Settings** → **Resources**
3. Augmenter **Memory** à **16 GB** (ou 12 minimum)
4. Cliquer **Apply & Restart**
5. Relancer le script `ollama-start.bat`

### **C. Vérifier rapidement si Ollama répond**

```powershell
# Depuis PowerShell
curl http://localhost:11434/api/tags

# Résultat attendu:
# {"models":[{"name":"llama3.2:latest","size":..., ...}]}
```

---

## **📋 Checklist avant de démarrer**

- ✅ Docker Desktop est **installé** et **en cours d'exécution**
- ✅ Vous avez **au moins 8 GB de RAM libre** (en plus du système)
- ✅ Vous avez **20 GB d'espace disque libre**
- ✅ Votre **connexion Internet fonctionne** (pour télécharger le modèle)
- ✅ Le fichier `.env` est configuré (`OPENAI_API_KEY` optionnel)

---

## **📚 Configuration actuelle**

```
Agent Multi-Loop          Agent Local
     ↓                         ↓
  localhost:11434    ←    Ollama
     ↑
  Docker Container (llama3.2)
```

- **Ollama Host :** `http://localhost:11434`
- **Modèle :** `llama3.2:latest` (~8 GB)
- **Mode :** Docker Compose
- **Fallback :** OpenAI GPT-4o-mini (si Ollama indisponible)

---

## **⏰ Temps de réponse estimés**

Une fois Ollama prêt :

| Agent | Premier appel | Appels suivants | Utilité |
|-------|---------------|-----------------|---------|
| **Agent Multi-Loop** | 2-5 sec | 1-3 sec | Calculs spectraux (SA, SB, D, etc) |
| **Agent Local** | 3-8 sec | 2-5 sec | Mathématiques complètes + GitHub |

---

## **🔗 Ressources**

- [Docker Desktop Download](https://www.docker.com/products/docker-desktop/)
- [Ollama Models](https://ollama.ai/library)
- [Guide complet : OLLAMA_STARTUP_GUIDE.md](./OLLAMA_STARTUP_GUIDE.md)
- [Diagnostic complet : ollama-diagnostic.ps1](./ollama-diagnostic.ps1)

---

## **✅ Vous êtes prêt !**

Exécutez simplement :
```bash
.\ollama-start.bat
```

Et attendez le message ✅ **OLLAMA OPERATIONNEL!**
