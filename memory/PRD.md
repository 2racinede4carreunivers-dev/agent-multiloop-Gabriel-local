# Multi-Loop Math Agent Gabriel Local - PRD

## Problem Statement
Agent IA multi-loop pour les mathematiques (Methode Spectrale Philippe Thomas Savard) avec Isabelle/HOL, Ollama, OpenAI fallback. 3 questions critiques + self-critique multi-loop.

## Implementations done

### Jan 2026 - Foundation
- Module spectral complet (SA, SB, A_1_3, B_1_3, A_1_4, B_1_4, suites mixtes/negatives, digamma, gap, ratio)
- 6 moteurs cognitifs + multi-loop self-critique + LLM manager Ollama->OpenAI fallback
- Docker compose + Dockerfile.cli slim (sans Isabelle inclus, image ~300 MB)
- .dockerignore strict (contexte build = ~232 KB)
- start-agent.ps1 + clean-docker.ps1 PowerShell
- Wolfram integration (6e moteur verification)
- Table des premiers PRIMES[1..1000] (resout bug "26eme premier" -> p=101)
- Connaissance spectrale gravee dans prompt systeme : formules vedettes, regle n=position pour 1/2
- Penalite -1.5 si vocabulaire interdit ("incoherent", "absurde", etc.)
- Critique bienveillant
- Timeouts reduits Ollama 60s->10s, OpenAI 90s->30s

### Feb 2026 - Sync GitHub + refonte spectral_core
- **2026-02-13** : Workspace Emergent realigne sur github/main (source de verite : `https://github.com/2racinede4carreunivers-dev/agent-multiloop-Gabriel-local.git`)
- Refonte cognitive_alignment -> `src/core/spectral_core.py` (SpectralMethodCore + AntiHallucinationValidator)
- Ajout fichiers d'optimisation : `config_optimized.yaml`, `apply_optimization.py`, `OPTIMIZATION_SUMMARY.md`, `README_FINAL.md`, `test_spectral_gabriel.py`
- Suppression `src/engines/cognitive_alignment/` (remplace par spectral_core)
- Mini-fix `explain_reconstruction()` pour inclure "INVARIANT" (test_spectral_gabriel test 5)
- **Protection .vhdx renforcee** : .dockerignore + .gitignore bloquent explicitement `*.vhdx`, `*.vhd`, `**/DockerDesktopWSL/**`, `**/data.vhdx`, `**/ext4.vhdx` pour eviter les contextes Docker >> 200 Go

## Tests (Feb 2026)
- 22/22 pytest passent
- 5/5 test_spectral_gabriel.py passent (Sieve, Invariant 1/2, Anti-hallucination, Ratio, Explanation)
- Contexte Docker simule : 232 Ko (< 5 Mo cible)

## Pour le user
- Pull depuis GitHub propre
- `.env` avec OPENAI_API_KEY et WOLFRAM_APP_ID
- `.\start-agent.ps1 -Rebuild`
- Posez "Peux-tu reconstruire le 26eme premier en rapport 1/2 ?" -> p=101 + chiffres exacts

## Backlog
- P1 : Boucle automatique de compilation Isabelle/HOL (Wolfram -> Gabriel -> Isabelle : generer, ecrire, compiler, rapporter)
- P2 : Commande CLI `gap <p1> <p2>` pour calculer ecart spectral sans LLM
- P2 : Tester avec Ollama reel sur Docker user
- P3 : Validation Isabelle automatique via service container
