# PRD - Agent Multi-Loop Gabriel Local

## Problème initial
Construction d'une application Python CLI (Dockerisée) multi-loop avec 7 moteurs cognitifs pour assister Philippe Thomas Savard dans ses démonstrations mathématiques sur la "Méthode Spectrale" de reconstruction des nombres premiers, avec intégration Isabelle/HOL et garde-fous anti-hallucination LLM.

## Statut Global
**Production-Ready v2.1 — 186/186 tests Pytest ✅ — Certifié 8/8 capacités utilisateur**

## Architecture
```
/app/agent-multiloop-Gabriel-local/
├── .github/workflows/tests.yml   (CI automatique, 165+ tests)
├── docker-compose.yml
├── Dockerfile.cli
├── main_cli.py
├── start-agent.ps1
├── data/
│   ├── audits/    (JSON signés)
│   └── graphs/    (PNG exportés via --png, gitignored)
├── src/
│   ├── adapters/ (corpus, hol_isabelle, llm, wolfram, hol_integration)
│   ├── audit/
│   ├── core/ (pipeline, pipeline_with_gap_detection, llm_manager)
│   ├── debug_toolkit/
│   ├── engines/ (7 moteurs)
│   ├── learning/ (meta_learning, slowmotion_recorder, debugging_expertise)
│   ├── multiloop/
│   ├── spectral/ (spectral_core, gaps, rsp, prime_table 1000 primes, hol_script_generator)
│   ├── ui/
│   │   ├── cli.py
│   │   ├── ci_status.py
│   │   └── debug_session.py
│   └── visualization/   ← NOUVEAU (15 fev 2026)
│       ├── curves.py         (compute_curve : SA/SB/digamma/invariant/ratio/gap/prime)
│       ├── ascii_renderer.py
│       ├── rich_renderer.py
│       └── png_renderer.py   (matplotlib)
└── tests/ (186 tests Pytest)
```

## Capacités certifiées
- **Q1** Rapport spectral : 1×1, n×n symétrique, asymétrique chaotique, ordonnée
- **Q2** Reconstruction du N-ième nombre premier (jusqu'à N=1000)
- **Q3** Calcul de gap : 3 cas (+,+), (−,−), (−,+)
- **Visualisations** : ASCII + Rich Table + PNG matplotlib (qualité publication)
- Corpus mathématique intégré + Slow Motion Debugging + Meta-Learning + CI

## Changelog

### [2026-02-15] Module Visualisation (3 formats combinés)
- Nouveau module `src/visualization/` (data-centric)
  - `curves.py` : 8 types calculés en entiers exacts — SA, SB, SA_SB, digamma, invariant D(n,P), ratio SA/SB, gap, prime
  - `ascii_renderer.py` : courbes ASCII avec axes, légende, target_line
  - `rich_renderer.py` : tableaux Rich avec troncature intelligente (max_rows centrés)
  - `png_renderer.py` : export matplotlib haute résolution (150 dpi par défaut, footer scientifique avec formule + timestamp)
- Auto-scale intelligent (linear/log10) selon les données (signes mixtes → linear ; croissance > 100x → log10)
- Nouvelle commande CLI : `courbe <type> <n1>..<n2> [--table] [--png] [--scale=X]`
  - Génère ASCII (toujours) + Tableau Rich (--table) + PNG (--png)
  - Crée un audit JSON signé citable pour chaque graphique
  - 21 tests pytest ajoutés (`tests/test_visualization.py`)
- Ajout `matplotlib>=3.8.0` à `requirements.txt`
- **Fix critique** : `PipelineWithGapDetection.__getattr__` ajouté pour déléguer `spectral_core`, `audit_store`, `corpus`, etc. au pipeline de base (sans cette correction, plusieurs commandes CLI existantes — `gap`, `verifier`, `audit`, `corpus` — étaient **cassées** par le commit Isabelle 695c64e)

### [2026-02-15] CI / Tests automatisés
- Création de `.github/workflows/tests.yml` : exécution automatique de la suite pytest à chaque push/PR sur `main` (Python 3.11, Ubuntu, déclenchement manuel possible)
- Création de `src/ui/ci_status.py` : utilitaire `run_pytest_local()` + dataclass `CISummary` qui parse la sortie pytest
- Intégration dans la **bannière d'ouverture CLI** : statut CI affiché juste après le logo ASCII (ex : `186/186 OK (pytest local, 1.7s)`)
- Ajout commande chat `ci` (alias `tests`, `pytest`) : Panel Rich détaillé
- 4 tests dans `tests/test_ci_status.py`

### Synchronisations GitHub
- `647ee40` — Test Gabriel 8/8 + README v2.0
- `695c64e` — Mise à jour fonctions Isabelle (HOL_ISABELLE_FIX.md, hol_integration.py, hol_script_generator.py, verif_p103_n27_CORRECT.thy)

## Backlog / Futures tâches
- **P1** : Refactoring des versions parallèles (`gap_solver.py` vs `gap_solver_final.py`, `pipeline.py` vs `pipeline_fixed.py`)
- **P1** : `UnicodeEncodeError` (caractère `\udcc3` sur input PowerShell) — non reproduit récemment
- **P2** : Badge GitHub Actions dans README.md (à ajouter après le 1er run distant)
- **P2** : Permettre à Gabriel de **décider lui-même** d'insérer un graphique dans sa réponse LLM (auto-trigger sur "explique la convergence", "trace l'évolution", etc.)
- **P3** : Comparaison via API GitHub Actions distante (local vs remote CI dans la bannière)

## 3rd Party Integrations
- OpenAI GPT-4o-mini (fallback) — clé utilisateur
- Ollama local (Llama3.2)
- Wolfram Alpha — clé utilisateur
- GitHub Actions (CI) — gratuit
- matplotlib (graphiques PNG) — gratuit, hors-ligne

## Test Credentials
N/A (pas d'authentification, app CLI locale).

## Health Status
✅ **Production-Ready v2.1** — 186/186 tests, CI configurée, visualisations citables opérationnelles.
