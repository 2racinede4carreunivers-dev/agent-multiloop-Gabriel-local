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
  - Menu : **[A-Z]** toggle segment (majuscule strict), **c** commentaire, **r** re-decompose, **t** toolkit, **e** execute, **q** annule
  - Commandes en minuscules / segments en majuscules pour eviter les ambiguites
- Validation strict des longueurs avec messages d'erreur clairs en francais
- Limite globale appliquee aussi aux requetes normales (max 2000 caracteres)
- 15 nouveaux tests `tests/test_debug_session.py` couvrant validations, toggle, commentaires, annulation, execution

### Feb 2026 - Debug Toolkit (vrais outils de verification embarques dans Docker)
- **2026-02-13** : Trois vrais outils de debugging scientifique installes via `requirements.txt`
- Nouveau module **`src/debug_toolkit/`** :
  - `registry.py` : detecte les outils installes au runtime
  - `sympy_validator.py` : validation **symbolique exacte** des formules SA, SB, digamma (fractions Rational, pas flottants)
  - `mpmath_validator.py` : recalcul a **precision arbitraire 100 chiffres** (critique pour grandes positions)
  - `z3_prover.py` : **preuve formelle SMT** de l'INVARIANT 1/2 et de l'identite de reconstruction
- Packages ajoutes a `requirements.txt` : `mpmath>=1.3.0`, `z3-solver>=4.12.0` (sympy etait deja la)
- Wheels precompiles manylinux disponibles -> aucun build natif requis dans Docker
- Commande `t` ajoutee au menu de DebugSession : lance les 3 validateurs sur la position courante avec rendu Rich code par couleur (vert/bleu/magenta)
- Cross-validation prouvee sur position=26 -> les 3 outils confirment p=101 independamment
- 16 nouveaux tests `tests/test_debug_toolkit.py` (registry, chaque validateur isole, accord 3-outils)
- Impact taille image Docker : +41 Mo (z3 wheel) ; image totale attendue ~330-450 Mo (toujours < 500 Mo)

### Feb 2026 - AuditStore : base d'audits JSON signes citables (rapport 1/2 v1)
- **2026-02-13** : Implementation d'une base d'audits citables pour archivage et reference scientifique
- Nouveau module **`src/audit/`** :
  - `AuditRecord` : dataclass avec id (8 hex), timestamp UTC, intervention_type, question, position, prime_value, decomposition, timeline, citations_thy, toolkit_reports, user_comment, forced_bypass, signature_sha256
  - `AuditStore` : persistance JSON dans `/home/agent/app/data/audits/YYYY-MM-DD_HHMMSS_<id>.json`
  - Signature **SHA-256** sur JSON canonique (cles triees) -> detection de toute modification ulterieure (test `test_verify_detects_tampering`)
  - Citations Markdown / LaTeX / texte prets a coller dans un article scientifique
  - Filtrage par position, ratio, intervention_type
- **PERIMETRE STRICT v1** : rapport 1/2 uniquement (decision utilisateur pour faciliter l'assimilation par les critiques)
- **Branchement automatique** aux 3 points clefs :
  - `SlowMotionDebugger.debug()` -> audit auto type `slow_motion_auto`
  - `DebugSession._execute()` (touche `e`) -> audit type `debug_manual` avec commentaire et bypass forces
  - `DebugSession.verifier_position()` -> audit type `verifier`
- **4 nouvelles commandes CLI** :
  - `verifier <N> [ratio]` -> lance le toolkit + cree un audit (commande rapide)
  - `historique [filtre]` -> liste les 20 derniers audits (filtre par position ou ratio)
  - `audit <id>` -> affiche le JSON complet
  - `citer <id> [markdown|latex|text]` -> genere un bloc citable (Markdown par defaut)
- Aucun nouveau package requis (`hashlib`, `json`, `uuid` sont dans la stdlib)
- 19 nouveaux tests `tests/test_audit_store.py` (signature deterministe, detection de tampering, filtres, citations 3 formats, integration debugger + session + verifier)

### Feb 2026 - P1 : Boucle automatique Wolfram <-> Gabriel <-> Isabelle
- **2026-02-13** : Implementation du triptyque de validation autonome
- Nouveau module **`src/multiloop/verification_loop.py`** :
  - `AutomaticVerificationLoop` orchestre les 5 etapes :
    1. **Wolfram** : verification numerique externe (nth_prime) - resilient si AppID absent
    2. **Gabriel** : generation autonome des valeurs SA/SB/digamma depuis spectral_core
    3. **Isabelle** : ecriture du .thy + compilation via `isabelle process`
    4. **Analyse** : si echec, parse stderr (markers "Failed to finish proof", etc.) et retry avec tactique suivante (`simp` -> `auto` -> `force` -> `(simp add: algebra_simps)`)
    5. **Audit** : sauvegarde JSON signe type `verification_loop` avec tous les rapports
  - Mode **mock resilient** si Isabelle absent : check syntaxique local du .thy genere (theory/imports/begin/end/lemmas/by) avec rapport d'erreur si invalide
  - 4 lemmes generes automatiquement par .thy : `SA_n_<n>_valeur`, `SB_n_<n>_valeur`, `digamma_calc_n_<n>_p_<p>`, `prime_equation_<p>_n_<n>`
- Nouvelle commande CLI **`valider <N> [ratio]`** : lance la boucle complete, affiche 3 panneaux (Wolfram/Gabriel/Isabelle), cree un audit citable
- 13 nouveaux tests `tests/test_verification_loop.py` couvrant : flux complet, contenu .thy, gestion d'erreurs, syntax check local, audit cree

### Feb 2026 - P2 : Commande `gap <p1> <p2>` (ecart spectral direct sans LLM)
- **2026-02-13** : Calcul direct de l'ecart spectral entre deux primes/positions
- Nouveau module **`src/spectral/gap_compute.py`** :
  - `compute_gap(v1, v2, ratio="1/2")` : accepte positions OU primes (auto-detection par reverse lookup)
  - Calcule : `delta_n`, `delta_p`, `delta_SA`, `delta_SB`, `RsP` (en fraction exacte via `Fraction`), `D(n,p)`, `delta_D`, `invariant_ok`
  - Formules pures (SA/SB) -> fonctionne pour TOUTE position (pas limite a la table de 168 du spectral_core)
- **AUCUN appel LLM** : pure execution Python en quelques millisecondes
- Nouvelle commande CLI **`gap <v1> <v2>`** : tableau Rich + audit automatique citable
- 10 nouveaux tests `tests/test_gap_compute.py` (INVARIANT 1/2 verifie sur 5 paires, positions/primes auto-detect, .thy citations)

## Tests (Feb 2026)
- **124/124 pytest passent** (22 originaux + 11 silent_audit + 18 slow_motion + 15 debug_session + 16 debug_toolkit + 19 audit_store + 13 verification_loop + 10 gap_compute)
- 5/5 test_spectral_gabriel.py passent
- Contexte Docker simule : 460 Ko (< 5 Mo cible)
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
