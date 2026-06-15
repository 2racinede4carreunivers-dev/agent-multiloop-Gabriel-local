# PRD - Agent Multi-Loop Gabriel Local

## Problème initial
Construction d'une application Python CLI (Dockerisée) multi-loop avec 7 moteurs cognitifs pour assister Philippe Thomas Savard dans ses démonstrations mathématiques sur la "Méthode Spectrale" de reconstruction des nombres premiers, avec intégration Isabelle/HOL et garde-fous anti-hallucination LLM.

## Statut Global
**Production-Ready v2.0 — Certifié 8/8 tests de capacité par l'utilisateur (oct 2026)**

## Architecture
```
/app/agent-multiloop-Gabriel-local/
├── .github/workflows/tests.yml   ← NOUVEAU (CI automatique)
├── docker-compose.yml
├── Dockerfile.cli
├── main_cli.py
├── start-agent.ps1
├── src/
│   ├── adapters/ (corpus, hol_isabelle, llm, wolfram)
│   ├── audit/ (audit_store.py - JSON signés)
│   ├── core/ (pipeline, llm_manager, orchestrator)
│   ├── debug_toolkit/ (sympy, mpmath, z3)
│   ├── engines/ (7 moteurs cognitifs)
│   ├── learning/ (meta_learning, slowmotion_recorder)
│   ├── multiloop/ (critic, refinement, silent_audit, slow_motion)
│   ├── spectral/ (spectral_core, gaps, rsp, prime_table 1000 primes)
│   └── ui/
│       ├── cli.py
│       ├── ci_status.py        ← NOUVEAU
│       └── debug_session.py
└── tests/ (165 tests Pytest)
```

## Capacités certifiées (8/8)
- **Q1** Rapport spectral : 1×1, n×n symétrique, asymétrique chaotique, ordonnée
- **Q2** Reconstruction du N-ième nombre premier (jusqu'à N=1000)
- **Q3** Calcul de gap : 3 cas (+,+), (−,−), (−,+)
- Corpus mathématique intégré + Slow Motion Debugging + Meta-Learning

## Changelog session 15 fév 2026 (E1 fork)

### [2026-02-15] CI / Tests automatisés
- Création de `.github/workflows/tests.yml` : exécution automatique de la suite pytest à chaque push/PR sur `main` (Python 3.11, Ubuntu, déclenchement manuel possible)
- Création de `src/ui/ci_status.py` : utilitaire `run_pytest_local()` + dataclass `CISummary` qui parse robustement la sortie pytest
- Intégration dans la **bannière d'ouverture CLI** : statut CI affiché juste après le logo ASCII (ex : `165/165 OK (pytest local, 1.03s)`)
- Ajout commande chat `ci` (alias `tests`, `pytest`) : affiche un Panel Rich détaillé avec compteurs + queue de sortie
- Ajout de la commande dans `HELP_TEXT`
- 4 nouveaux tests dans `tests/test_ci_status.py`
- **Total tests : 165/165 ✅** (161 anciens + 4 nouveaux, 0 régression)

### Synchronisation depuis GitHub
- Pull du commit `647ee40` (Test Gabriel 8/8 + mise à jour README.md)
- Nouveaux modules importés : `src/learning/` (debugging_expertise, meta_learning_integration, slowmotion_recorder), `gap_solver_final.py`, `pipeline_with_gap_detection.py`, `slowmotion_trigger.py`
- Nouveaux tests importés : `test_mandatory_questions.py`, `test_spectral_ratio_configurations.py`, `test_verification_loop.py`

## Backlog / Futures tâches
- **P1** : Refactoring — il existe plusieurs versions parallèles (`gap_solver.py` / `gap_solver_corrected.py` / `gap_solver_final.py`, `pipeline.py` / `pipeline_fixed.py` / `pipeline_with_gap_detection.py`). Un nettoyage est pertinent.
- **P1** : Correction `UnicodeEncodeError` (caractère `\udcc3` sur input PowerShell) — bug reporté lors d'une session précédente mais non encore reproduit.
- **P2** : Badge GitHub Actions à ajouter dans le README.md une fois le workflow exécuté la première fois.
- **P3** : Extension au-delà de 1000 primes (si pertinent).

## 3rd Party Integrations
- OpenAI GPT-4o-mini (fallback) — clé utilisateur
- Ollama local (Llama3.2)
- Wolfram Alpha — clé utilisateur
- GitHub Actions (CI) — gratuit

## Test Credentials
N/A (pas d'authentification, app CLI locale).

## Health Status
✅ **Production-Ready** — 165/165 tests passent, CI GitHub Actions configurée.
