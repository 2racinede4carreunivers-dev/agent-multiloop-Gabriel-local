# Multi-Loop Mathematical Agent — Gabriel Local

Agent IA multi-loop pour les mathématiques, particulièrement la **Méthode Spectrale de Philippe Thomas Savard** et Isabelle/HOL.

## 🎯 Principe Multi-Loop

L'agent **se critique lui-même** et ajuste ses réponses :
1. Génère plusieurs candidats de réponse
2. Critique chacun selon : correction mathématique, ancrage corpus, complétude, clarté
3. Si score < 8/10, génère une nouvelle itération en intégrant la critique
4. Retourne la meilleure réponse finale

## 🧠 5 Moteurs Cognitifs

| Moteur | Rôle | Implémentation |
|---|---|---|
| **Abstraction** | Détecte concepts Savard (RsP, digamma, gap_equation...) | Profonde (regex + signatures) |
| **Méta-raisonnement** | Sélectionne la stratégie selon l'intent | Profonde (planner) |
| **Navigation conceptuelle** | Graphe de concepts du corpus | networkx |
| **Généralisation** | Patterns 1/2 → 1/k, positif → négatif → mixte | Solide |
| **Découverte théorèmes** | Conjectures sur nouveaux rapports | Squelette |

## 🔬 Module spectral (vérité mathématique)

Implémentation directe du corpus `methode_spectral.thy` :
- `SA(n) = (3.25/2)·2^n - 2`, `SB(n) = (6.5/2)·2^n - 66`
- `A_1_3, B_1_3, A_1_4, B_1_4` (rapports 1/3, 1/4)
- `digamma_calc(n,p)`, `prime_equation(n,p)`
- `compute_spectral_ratio` — 4 configurations (1×1, n×n, asym. ordonnée, asym. chaotique)
- `compute_gap` — 3 cas (+,+), (-,-), (-,+)
- `reconstruct_pth_prime_full` — reconstruction complète avec SA, SB, digamma

✅ **18 tests automatisés** : tous les exemples du corpus (29, 31, 37, 41, 227, 947) sont reproduits exactement.

## 🐳 Architecture Docker

```
docker-compose.yml
├── llm-agent-multiloop  # Python 3.11 + Isabelle + agent
├── ollama               # LLM local primaire (llama3.2)
├── ollama-init          # télécharge le modèle au 1er démarrage
└── isabelle             # makarius/isabelle pour validation HOL
```

## 🚀 Démarrage rapide (Windows)

1. **Configurez votre .env** :
   ```powershell
   Copy-Item .env.example .env
   # Éditez .env et ajoutez votre OPENAI_API_KEY (fallback)
   ```

2. **Placez vos fichiers .thy** dans `theories/` (ex: `methode_spectral.thy`)

3. **Lancez l'agent** :
   ```powershell
   .\start-agent.ps1
   ```

   Le script :
   - Démarre Docker Desktop si nécessaire
   - Build l'image
   - Lance ollama + isabelle + ollama-init
   - Ouvre un nouveau terminal PowerShell avec l'agent multiloop

4. **Autres commandes utiles** :
   ```powershell
   .\start-agent.ps1 -Rebuild     # rebuild complet --no-cache
   .\start-agent.ps1 -Logs        # streaming des logs
   .\start-agent.ps1 -Status      # état des conteneurs
   .\start-agent.ps1 -Stop        # arrêt
   ```

## 💬 Exemples de questions que l'agent sait résoudre

### Q1 — Reconstruction du P-ième premier
> *« Pour n=10 termes dans les suites A et B et p=29, donne-moi SA, SB, Digamma et Digamma calculé. »*

L'agent renvoie : `SA=1662, SB=3262, digamma_calc=1406, p reconstruit=29 ✓`

### Q2 — Rapport spectral
> *« Calcule le rapport spectral 1×1 pour n1=3 et n2=7 modèle 1/3. »*
> *« Donne-moi le rapport asymétrique chaotique avec A=[5,1,10] B=[3,7]. »*

L'agent détecte la configuration et retourne `1/3` (vérité du corpus).

### Q3 — Écart entre deux premiers
> *« Quelle quantité de nombres y a-t-il entre 227 et 173 ? »*
> *« Calcule l'écart entre -19 et -5 (suites négatives). »*
> *« Détermine l'écart mixte entre -31 et 17. »*

L'agent retourne exactement `-53`, `-13`, `-47` (comme dans le corpus HOL).

## 🧪 Tests

```bash
PYTHONPATH=. python -m pytest tests/ -v
```

18 tests couvrent les 3 questions obligatoires de Gabriel.

## 📁 Structure du projet

```
agent-multiloop-Gabriel-local/
├── main.py / main_cli.py        # Points d'entrée
├── config.yaml                  # Configuration agent
├── .env.example                 # Modèle de variables d'environnement
├── docker-compose.yml           # Services Docker
├── Dockerfile.cli               # Image agent
├── start-agent.ps1              # Lanceur PowerShell Windows
├── requirements.txt
├── src/
│   ├── core/                    # types, config, pipeline, orchestrator, llm_manager
│   ├── spectral/                # SUITES, DIGAMMA, RATIOS, GAPS (cœur math)
│   ├── multiloop/               # critic, refinement_loop
│   ├── engines/
│   │   ├── abstraction/         # extraction de concepts
│   │   ├── meta_reasoning/      # stratégie, planificateur
│   │   ├── concept_navigation/  # graphe de concepts (networkx)
│   │   ├── generalization/      # patterns 1/k
│   │   └── theorem_discovery/   # conjectures
│   ├── adapters/
│   │   ├── llm/                 # Ollama + OpenAI
│   │   ├── corpus/              # chargeur .thy
│   │   └── hol_isabelle/        # generateur scripts HOL
│   └── ui/                      # CLI Rich
├── theories/                    # Vos .thy (methode_spectral.thy)
├── tests/                       # Tests des 3 questions critiques
└── docs/                        # Documentation
```

## ⚙️ Configuration LLM

`config.yaml` :
```yaml
llm:
  primary: "ollama"          # tente d'abord Ollama (local, gratuit)
  fallback: "openai"         # bascule sur OpenAI si Ollama échoue
  ollama:
    model: "llama3.2"
  openai:
    model: "gpt-5.4"
```

L'agent essaie **automatiquement** Ollama → si timeout/erreur → OpenAI (votre clé).

## 📖 Corpus mathématique supporté

- Méthode Spectrale Savard (modèles 1/2, 1/3, 1/4)
- Suites positives, négatives, mixtes (-,+)
- Géométrie spectrale (asymétrie ordonnée/chaotique)
- Plan trifocal (FZg, HyRi, MsP), validation épipolaire
- Lien Riemann (formule explicite, hypothèse RH)
- Isabelle/HOL preuves formelles
