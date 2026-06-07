# Agent Multi-Loop Gabriel Local — PRD

## Problem Statement
Gabriel possède un agent IA multi-loop mathématique local (Méthode Spectrale Philippe Thomas Savard + Isabelle/HOL). Il a demandé à E1 de générer un nouvel agent en s'appuyant sur l'architecture existante + corpus HOL fourni, qui se critique lui-même (multi-loop), fonctionne dans Docker, et répond à 3 questions critiques.

## Stack
- Python 3.11 + asyncio
- Ollama (llama3.2) primary + OpenAI (clé utilisateur) fallback
- Isabelle/HOL via image makarius/isabelle
- Docker Desktop + docker-compose
- PowerShell launcher (Windows)
- Tests pytest

## Implementations done (Jan 2026)
- Module spectral : SA, SB, A_1_3, B_1_3, A_1_4, B_1_4, suites mixtes/négatives, digamma_calc, prime_equation, 4 configurations de ratio, 3 cas de gap, reconstructor
- 5 moteurs cognitifs : abstraction (profond), méta-raisonnement (profond), navigation (graphe 31 nœuds), généralisation, théorèmes-discovery (squelettes solides)
- Multi-loop self-critique : Critic + RefinementLoop avec scoring 0-10, comparaison de candidats, refinement intégrant la critique
- LLM Manager : Ollama-first avec fallback automatique OpenAI
- Adapter Isabelle : génération de scripts .thy de vérification + chargeur de corpus
- CLI Rich avec banner, panels colorés, commandes spéciales
- Docker : Dockerfile.cli avec Isabelle 2025-2, docker-compose 4 services (agent, ollama, ollama-init, isabelle)
- start-agent.ps1 : lanceur PowerShell complet (build, up, terminal interactif, modes -Rebuild/-Logs/-Stop/-Status)
- 18 tests pytest tous au vert sur les 3 questions critiques

## 3 questions critiques (toutes ✅ validées)
- Q1. Reconstruction du P-ième premier : SA, SB, digamma, p reconstruit (29, 31, 37, 41, ...)
- Q2. Rapport spectral : 4 configurations (1x1, n*n, asym ordonnée, asym chaotique) × 3 modèles (1/2, 1/3, 1/4)
- Q3. Écart entre 2 premiers : 3 cas (+,+), (-,-), (-,+) avec reproduction exemples corpus (-53, -65, -13, -47)

## Backlog
- P1 : Tester avec Ollama réel (nécessite Docker Desktop local Gabriel)
- P1 : Charger geometrie_spectre_premier.thy quand Gabriel l'enverra
- P2 : Étoffer logique du moteur theorem_discovery (conjectures plus riches)
- P2 : Validation HOL automatique via isabelle process
- P3 : Interface web optionnelle (FastAPI)
