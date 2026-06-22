# PRD - Agent Multi-Loop Gabriel Local

## Problème initial
Construction d'une application Python CLI (Dockerisée) multi-loop avec 7 moteurs cognitifs pour assister Philippe Thomas Savard dans ses démonstrations mathématiques sur la "Méthode Spectrale" de reconstruction des nombres premiers, avec intégration Isabelle/HOL et garde-fous anti-hallucination LLM.

## Statut Global
**Production-Ready v3.0 — 487/487 tests Pytest ✅ — Slow-Motion "Kit de réparation" (6 cadrans aérés) + Décomposeur intelligent + 5 Axes cognitifs + Plan Trifocal**

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

### [2026-02-16] Slow-Motion Debugger — Kit de réparation spectrale (UX + logique)

**Suite au feedback Philippe sur l'écran "REPONSE CERTIFIEE" écrasé et T4/T7 vides.**

#### A. Visuel — "Kit de réparation métrique"
- Nouveau rendu CLI dédié `_display_slow_motion(answer)` (route automatique quand `slow_motion_triggered=True`)
- **6 cadrans aérés** au lieu d'un seul panneau écrasé :
  - **HEADER** "KIT DE REPARATION SPECTRALE — MODE INSTRUMENT DE PRECISION" (cyan vif + signaux déclencheurs)
  - **CADRAN 1** — REFERENCE CERTIFIEE : lecture de l'instrument, chaque mesure sur sa propre ligne avec label aligné (A, B, RsP, Configuration, Méthode...)
  - **CADRAN 2** — SOURCES DE CERTITUDE : axiomes de calibration numérotés `[1]`, `[2]`, `[3]` avec aération entre eux
  - **CADRAN 3** — SEGMENTS REJETÉS : quarantaine avec `[X]` + motif italique (rouge, uniquement si bypass)
  - **CADRAN 4** — SUGGESTIONS DE REFORMULATION : recalibrage `->` (vert)
  - **CADRAN 5** — TIMELINE DEBUGGER : chaque step avec respiration entre étapes
  - **CADRAN 6** — Niveau de certitude (Axe 4) intégré dans le thème
- Thème : turquoise/cyan profond (précision) + accents ambre/jaune (gauges) + rouge (alerte) + vert (recalibrage)
- `padding=(1, 3)` partout pour aération critique

#### B. Logique — Décomposeur + Slow-Motion plus intelligents
- **Décomposeur** détecte le mismatch "annoncé vs réel" :
  - "rapport spectral **symétrique 4×4**" + tuples `(7,23,79,31)` (4) et `(17,11,3)` (3) → tuples flaggés INCOHÉRENTS avec motif explicite "Annonce symetrique 4*4 mais A=4 != B=3 (ASYMETRIQUE en realite)"
  - Nouveau champ `announced_size` + `announced_symmetric` dans `DecomposedRequest`
  - Détecte aussi "asymétrique NxN" / "configuration NxN" (regex avec lookbehind pour éviter `sym` match dans `asym`)
- **`_build_reformulations`** étendue à `ratio_spectral_nxn` :
  - Cas mismatch : propose la reformulation ASYMETRIQUE + suggestion de compléter B pour rester SYMETRIQUE
  - Cas normal : propose la reformulation canonique avec tuples
  - Toujours propose le cas élémentaire `RsP_1x1(a, b)` comme retour aux fondamentaux
  - Branches `reconstruction` et `gap` aussi améliorées
- **Timeline T1-T7** : chaque step **explique son raisonnement** (plus de "aucun segment à ignorer" sec) :
  - T2 mentionne pourquoi on bascule vers le kit déterministe
  - T3 montre "annoncé vs réel" en cas de mismatch
  - T4 explique soit la quarantaine, soit "syntaxiquement valide → incohérence vient du LLM"
  - T5 précise "seuls les segments cohérents sont utilisés"
  - T6 mentionne la méthode (`spectral_core.analyze_spectral_ratio` etc.)
  - T7 dit combien de suggestions + lesquelles (ou explique pourquoi 0)
- **`structured_data` nettoyé** : les champs obsolètes (`ratio_float`, `expected_float`, `matches_expected`) hérités du multiloop pré-slow-motion sont effacés pour éviter la contradiction visuelle avec la réponse certifiée

#### Tests
- `tests/test_slow_motion_improvements.py` : **10 nouveaux tests**
- Total : **487/487 ✅** (0 régression)

### [2026-02-16] Plan Trifocal FZg/HyRi/MsP (P1) + Fix UnicodeEncodeError (P1) + Refactor src/ (P2)

#### Plan Trifocal — Section X methode_spectral.thy
- Nouveau module `src/spectral/plan_trifocal.py` :
  - 3 axes : **FZg** (Fonction Zêta globale), **HyRi** (Hypothèse de Riemann), **MsP** (Méthode spectrale + position)
  - 5 postulats épipolaires (P1-P5) : coïncidence des positions, constante 1/2, équation d'aires, sur-combinatoire mixte, courbure de droite critique
  - `PlanTrifocal.validate(n, model)` : validation déterministe (Fraction) — P2 OK uniquement pour modèle 1/2 (1/3 et 1/4 ne touchent pas Riemann directement)
  - `riemann_link_statement()` : texte citable expliquant le lien MsP↔Riemann
  - `epistemic_claim(validation)` : produit une `EpistemicClaim` CERTAIN/CONJECTURE/HORS_DOMAINE
- Nouvelle commande CLI : `trifocal [axes|postulats|valider <n> [m]|riemann]`
- 19 nouveaux tests (`tests/test_plan_trifocal.py`)

#### Fix UnicodeEncodeError (bug original du handoff)
- `src/core/llm_manager.py` : sanitization UTF-8 systématique de `prompt`/`system` dans `generate()` et de chaque `content` dans `chat()` via `UTF8Sanitizer`
- `src/audit/audit_store.py` : déjà sanitizé (vérifié et confirmé)
- 9 nouveaux tests (`tests/test_unicode_surrogate_fix.py`) — reproduit le surrogate `\udcc3` Windows PowerShell, vérifie AuditStore + LLMManager

#### Refactor src/ (P2)
- Supprimé **11 fichiers Python orphelins** (0 import dans src/, tests/, main_cli.py) :
  - `src/spectral/gap_solver.py`, `gap_solver_final.py` (v_corrected est la version live)
  - `src/core/pipeline_fixed.py`, `llm_manager_v2.py`, `llm_manager_old_backup.py`
  - `src/gabriel_v6_2_rag.py`, `gabriel_llm_integration.py`
  - `src/hol_proof_generator.py`, `spectral_ratio_analyzer.py`, `multiloop_validation_engine.py`, `gabriel_gap_mixed_handler.py`
- Déplacé **20 fichiers .md flottants** depuis `/app/` vers `/app/agent-multiloop-Gabriel-local/docs/archive/`
- Total : **477/477 tests ✅** (+28 nouveaux tests, 0 régression)

### [2026-02-16] Axe 2 - Ponts cognitifs intégrés au pipeline live (P0)
- Nouveau module `src/cognitive/engine_bridge.py` : pont entre les 4 briques cognitives et le moteur live
  - `CognitiveResult` : enveloppe `value + ProofTrace + EpistemicClaim + categorie + regime`
  - `build_gap_result(p1, p2)` : trace + claim CERTAIN/HORS_DOMAINE, catégorie auto (gap_pos_pos/neg_neg/mixed), régime ontologique (regime_positif/negatif/mixte)
  - `build_reconstruct_result(n, actual_prime, model)` : trace + claim sur les 3 modèles (1/2, 1/3, 1/4)
  - `build_rsp_1x1_result(n1, n2, model)` : trace + invariants `ratio_exact_1x1`, `denominateur_non_nul`
  - `get_meta_reasoner()` singleton + `record_cognitive_result()` enregistrement auto
- Nouveau wrapper `traced_rsp_1x1` dans `src/cognitive/traced_calculations.py`
- `FinalAnswer` étendu (`src/core/types.py`) : champs optionnels `epistemic_claim: dict` + `proof_traces: list[dict]`
- `Pipeline._annotate_epistemic` (`src/core/pipeline.py`) :
  - Attache une `EpistemicClaim` à chaque `FinalAnswer` (CERTAIN si calcul spectral_core validé, HORS_DOMAINE si erreur, CONJECTURE si pur-LLM)
  - Appelle `meta.record(category, success)` en fin de pipeline pour Axe 5
  - Singleton `MetaReasoner` instancié dans `Pipeline.__init__` (stocke stats à `data/learning/stats.json`)
- CLI (`src/ui/cli.py`) :
  - Nouvelle commande `cognitive [report|reset]` : tableau Rich des statistiques d'auto-évaluation par catégorie (Axe 5)
  - Commandes `gap`, `modele gap`, `modele reconstruct`, `modele rsp1x1` produisent désormais un panneau Rich "Axe cognitif" avec invariants + claim (Axes 2/3/4)
  - `_display_answer` affiche un panneau "Niveau de certitude (Axe 4)" pour les réponses LLM
  - Tab completion et `HELP_TEXT` mis à jour
- Tests :
  - `tests/test_engine_bridge.py` : 17 tests (build_gap/reconstruct/rsp_1x1, mapping régime, intégration MetaReasoner)
  - `tests/test_pipeline_epistemic.py` : 4 tests (CERTAIN/HORS_DOMAINE/CONJECTURE + record MetaReasoner)
  - `tests/test_traced_calculations.py` : +5 tests pour `traced_rsp_1x1`
- **Total : 449/449 tests ✅ (+27 nouveaux)**

### [2026-02-15] Ask Gabriel - 3 commandes d'aide contextuelle
- Nouveau module `src/ui/ask_gabriel.py` (deterministe, zero LLM) :
  - 3 sous-commandes : `ask`, `ask type`, `ask rules`
  - `ASK_MAIN_SECTIONS` : 4 facons d'interpeller Gabriel + commandes par categorie
  - `ASK_TYPE_SECTIONS` : 3 modeles + 8 questions canoniques + 7 moteurs + visualisations + audit + HOL
  - `ASK_RULES_SECTIONS` : 10 regles d'or + capacites + limites + en cas de probleme
- Integration CLI : commande `ask` dans `_handle_special` avec navigation entre les 3 modes
- Banniere d'ouverture enrichie : encart vert ">>> Pour decouvrir Gabriel : ask | ask type | ask rules"
- Tab completion : 'ask', 'ask type', 'ask rules' ajoutees a `DEFAULT_COMMANDS`
- 14 nouveaux tests dans `tests/test_ask_gabriel.py`
- Total : **346/346 tests ✅**

### [2026-02-15] GeometrieSpectraleEngine — 3 modeles, 8 questions canoniques
- Nouveau module `src/spectral/spectral_models.py` :
  - Classe abstraite `SpectralModel` + 3 implementations (`Model_1_2`, `Model_1_3`, `Model_1_4`)
  - Calcul en `fractions.Fraction` (exactitude infinie)
  - Conforme `theories/methode_spectral.thy` (A_1_3, A_1_4, B_1_3, B_1_4)
  - Facteurs : 64 (1/2), 729 (1/3), 4096 (1/4)
- Nouveau module `src/engines/geometrie_spectrale_engine.py` :
  - 8 questions canoniques : Q1.a (1x1), Q1.b (n×n sym), Q1.c (chaos), Q1.d (ord), Q2 (recon), Q3.a/b/c (gaps)
  - `answer_all_questions()` retourne 8 rapports comparatifs sur les 3 modeles
- Nouvelle commande CLI `modele <action>` :
  - `modele list | questions | all`
  - `modele rsp1x1 <n1> <n2>` / `modele rsp <A>|<B> [sym|chaos|ord]`
  - `modele reconstruct <N>` / `modele gap <p1> <p2>`
  - Audit JSON signe pour chaque calcul
- `AuditStore` etendu : supporte `1/2`, `1/3`, `1/4`, `1/2,1/3,1/4`
- 70 nouveaux tests (Total : **325/325 ✅**)
- **Verification mathematique end-to-end** : les 3 modeles reconstruisent exactement le N-ieme premier pour n ∈ {1, 5, 10, 26, 50, 100}

### [2026-02-15] Commande `commandes` + Raccourcis clavier
- Nouveau module `src/ui/keybindings.py` (`readline` natif Linux/Docker, `pyreadline3` pour Windows si besoin)
  - Historique persistant entre sessions : `data/.gabriel_history` (1000 entrees max)
  - Auto-completion `Tab` des commandes Gabriel (29 commandes)
  - Navigation historique avec fleches Up/Down + recherche inversee `Ctrl+R`
  - Singleton `install_keybindings()` idempotent + `save_history()` automatique a la sortie
- Nouvelle commande `commandes` (alias `cmd`, `commands`) dans `_show_full_commands()` :
  - 9 panels Rich categorises (general / corpus / calculs / viz / validation / audit / debug / CI / langage naturel)
  - Panel dedie "RACCOURCIS CLAVIER" avec 12 raccourcis documentes et statut actif/inactif
  - Panel "FICHIERS DE REFERENCE" pointant vers la documentation et fichiers generes
- Documentation utilisateur creee dans `commande-gabriel/` :
  - `COMMANDES.md` (378 lignes, 10 sections, exemples concrets)
  - `AIDE-MEMOIRE.txt` (cheatsheet 153 lignes a imprimer)
  - `README.md` (guide d'index)
- Mise a jour `HELP_TEXT` (mentionne `commandes` comme commande recommandee)
- Mise a jour `interactive_mode()` :
  - Installation auto des keybindings au demarrage
  - Affichage statut clavier dans la banniere
  - Sauvegarde historique a la sortie (EOF/quitter/Ctrl+D/Ctrl+C)
- 6 nouveaux tests dans `tests/test_keybindings.py`

### [2026-02-15] Auto-trigger LLM Visualisation
- Nouveau module `src/visualization/auto_trigger.py`
  - `detect_visualization_intent(question) -> VisualizationIntent | None`
  - **100% deterministe** (regex + mots-cles), aucun appel LLM, zero hallucination
  - Detection en francais : verbes (trace/dessine/illustre/visualise/evolue/converge...), types (SA/SB/digamma/ratio/gap/invariant/prime), intervalles ("n=1..50", "de 1 a 100", "entre 5 et 25", "100 premiers", "[1,200]"), intention PNG ("article scientifique", "exporte", "image")
  - Gere les accents, casse, ponctuation
- Integration dans `PipelineWithGapDetection.process()` AVANT detection gap et pipeline standard
  - Si visualisation detectee : courbe calculee + ASCII inclus dans la reponse + PNG optionnel + audit JSON citable signe
  - Si non : flux normal (gap detection puis multiloop)
- Exemple end-to-end teste :
  - Question : "Peux-tu tracer la convergence du ratio SA/SB sur 1..50 et exporter un PNG pour mon article scientifique ?"
  - Reponse : courbe ASCII + chiffres + PNG cree + audit `aa41c24a` (0 LLM consomme)
- **44 tests pytest ajoutes** (`test_auto_trigger.py`) — 35 cas positifs, 9 cas negatifs, robustesse accents/casse

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
- **P2** : Refactor avancé — fusionner les versions parallèles encore actives (`pipeline.py` + `pipeline_with_gap_detection.py`, `llm_router.py` + `llm_router_v2.py`, `gabriel_llm_integration_safe.py` + `gabriel_llm_integration_v2.py`) en une seule classe canonique (nécessite tests d'intégration approfondis)
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
✅ **Production-Ready v3.0** — 487/487 tests, CI configurée, Slow-Motion "Kit métrique" en 6 cadrans aérés, décomposeur détecte les mismatches annoncé/réel, T4/T7 expliquent leur raisonnement, Axes cognitifs 2-5 + Plan Trifocal + Unicode-safe.
