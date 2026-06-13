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

### Feb 2026 - Silent Audit Loop (anti-hallucination actif)
- **2026-02-13** : Implementation du **mode audit silencieux** post-pipeline
- Nouveau fichier `src/multiloop/silent_audit.py` : classe `SilentAuditLoop`
- `AntiHallucinationValidator.audit()` enrichi avec 3 regles :
  1. Prime correct doit apparaitre dans la reponse si une position est citee
  2. INVARIANT 1/2 : si rapport 1/2, alors n = position (sinon violation)
  3. Vocabulaire dismissif interdit (incoherent, absurde, faux, etc.)
- Re-prompt silencieux automatique avec verite terrain injectee (max_retries configurable)
- Config dans `config.yaml` : section `audit:` avec enabled/max_retries/temperature
- 11 nouveaux tests `tests/test_silent_audit.py` couvrant audit() + SilentAuditLoop avec LLM mock

### Feb 2026 - Slow-Motion Debugger (mode ralenti anti-incoherence)
- **2026-02-13** : Implementation du **mode debugger ralenti automatique**
- Remplacement de `geometrie_spectre_premier.thy` par la v2 (317 lignes : comparaisons 1x1, nxn, asym ordonnee/chaotique, SA/SB signes)
- Nouveau **CertaintyKernel** (`src/adapters/corpus/certainty_kernel.py`) : noyau distillant 31 certitudes depuis les 3 sources (methode_spectral.thy + geometrie_spectre_premier.thy + plan cognitif) avec PROVENANCE traçable
- Nouveau **CoherenceDetector** (`src/multiloop/coherence_detector.py`) : analyse les candidats multiloop selon 5 signaux (scores bas, variance, vocabulaire interdit, audit anti-hallucination, contradiction interne)
- Nouveau **RequestDecomposer** (`src/multiloop/request_decomposer.py`) : decoupe la requete en segments logiques (position, ratio, nombres, intent) et flag ceux qui violent l'INVARIANT 1/2
- Nouveau **SlowMotionDebugger** (`src/multiloop/slow_motion_debugger.py`) : orchestre la procedure 8 etapes (REQUETE_RECUE -> INCOHERENCE_DETECTEE -> DECOMPOSITION -> BYPASS_SEGMENTS -> REQUETE_CANONIQUE -> RESOLUTION_CERTIFIEE -> REFORMULATIONS -> REPONSE_CERTIFIEE), avec timeline ASCII traçable
- Resolution **sans LLM** (uniquement spectral_core + kernel) garantissant zero hallucination
- Integration pipeline : si coherence < 0.55 -> slow-motion debugger, sinon silent_audit classique
- Config dans `config.yaml` : section `slow_motion:` avec enabled/coherence_threshold
- 18 nouveaux tests `tests/test_slow_motion_debugger.py` couvrant CertaintyKernel + Decomposer + Detector + Debugger end-to-end

### Feb 2026 - Mode Debugger Manuel Pedagogique (terminal interactif)
- **2026-02-13** : Implementation de la **commande CLI `debug "<question>"`**
- Nouveau **DebugSession** (`src/ui/debug_session.py`) : session interactive en mode terminal
- **Limites de longueur strictes** :
  - Requete initiale : **1600 caracteres** max
  - Commentaire (ajout en cours de session) : **400 caracteres** max
  - Total combine : **2000 caracteres** max (empeche un commentaire de changer le sens de la requete au point de re-declencher une boucle d'incoherence)
- **UX terminal pedagogique** :
  - Tableau Rich avec lettres **A-Z** pour chaque segment + etat (GARDE ✓ / BYPASS ✗) + type + valeur + raison
  - Compteurs `requete=N/1600ch` et `commentaire=N/400ch` en temps reel
  - Apercu de la requete canonique mise a jour en direct
  - Menu : **[A-Z]** toggle segment (majuscule strict), **c** commentaire, **r** re-decompose, **e** execute, **q** annule
  - Commandes en minuscules / segments en majuscules pour eviter les ambiguites
- Validation strict des longueurs avec messages d'erreur clairs en francais
- Limite globale appliquee aussi aux requetes normales (max 2000 caracteres)
- 15 nouveaux tests `tests/test_debug_session.py` couvrant validations, toggle, commentaires, annulation, execution

## Tests (Feb 2026)
- **66/66 pytest passent** (22 originaux + 11 silent_audit + 18 slow_motion + 15 debug_session)
- 5/5 test_spectral_gabriel.py passent
- Contexte Docker simule : 340 Ko (< 5 Mo cible)
- 0 fichier .vhdx detecte dans le workspace

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
