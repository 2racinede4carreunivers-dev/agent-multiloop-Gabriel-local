# Multi-Loop Math Agent Gabriel Local - PRD

## Problem Statement
Agent IA multi-loop pour les mathematiques (Methode Spectrale Philippe Thomas Savard) avec Isabelle/HOL, Ollama, OpenAI fallback. 3 questions critiques + self-critique multi-loop.

## Implementations done (Jan 2026)
- Module spectral complet (SA, SB, A_1_3, B_1_3, A_1_4, B_1_4, suites mixtes/negatives, digamma, gap, ratio)
- 6 moteurs cognitifs + multi-loop self-critique + LLM manager Ollama->OpenAI fallback
- Docker compose + Dockerfile.cli slim (sans Isabelle inclus, image ~300 MB)
- .dockerignore strict (contexte build = 101 KB)
- start-agent.ps1 + clean-docker.ps1 PowerShell
- Wolfram integration (6e moteur verification)
- **Table des premiers PRIMES[1..100]** (resout bug "26eme premier" -> p=101)
- Connaissance spectrale gravee dans prompt systeme : formules vedettes, regle n=position pour 1/2, table n->p
- Detection intent "Neme premier" + lookup automatique p via nth_prime(n)
- Penalite -1.5 si vocabulaire interdit ("incoherent", "absurde", etc.)
- Critique bienveillant (4e critere : ton respectueux)
- Timeouts reduits Ollama 60s->10s, OpenAI 90s->30s (worst case 2 min vs 12 min)
- geometrie_spectre_premier.thy charge dans theories/ (monte en volume Docker)
- Regex extraction nombres ameliore : capte "26ieme", "11eme" sans capter 1/2

## Tests
- 22/22 tests passent
- Test critique : test_reconstruction_26eme_premier (SA, SB, digamma exacts, p=101)
- Test table : test_table_premiers_lookup (nth_prime(26)=101)

## Pour le user
- Pull depuis GitHub propre
- .env avec OPENAI_API_KEY et WOLFRAM_APP_ID
- .\start-agent.ps1 -Rebuild
- Posez "Peux-tu reconstruire le 26eme premier en rapport 1/2 ?" -> p=101 + chiffres exacts

## Backlog
- P1 : tester avec Ollama reel sur Docker user
- P2 : enrichir prime_table PRIMES au-dela de 100 si demande
- P3 : validation Isabelle automatique via service container
