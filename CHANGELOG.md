# Changelog — Gabriel Multi-Loop

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/)
et ce projet adhère au versionnement sémantique [SemVer](https://semver.org/lang/fr/).

**Auteur du projet :** Philippe Thomas Savard
**Dépôt :** [`agent-multiloop-Gabriel-local`](https://github.com/2racinede4carreunivers-dev/agent-multiloop-Gabriel-local)

---

## [Unreleased]

### En cours
- Documentation communautaire GitHub : `CONTRIBUTING.md`, `AUTHORS`, `CHANGELOG.md`, `SECURITY.md`, `declaration_securite.md`
- Intégration de la branche `mise_jour_E1_01A` (Section XI.A + renommage `A_suite` → `A_suite_ZeroZeta`)

### À venir
- `CITATION.cff` pour bouton "Cite this repository"
- `LICENSE` (choix pending entre MIT / Apache-2.0 / CC-BY-4.0)
- `CODE_OF_CONDUCT.md`
- Issue / PR templates
- Dependabot pour mises à jour de sécurité automatiques

---

## [3.38.0] — 2026-02-25

### Ajouté
- **Formule pure du digamma d'Euler** (`src/spectral/digamma_pure.py`)
  - `digamma_pure(n) = -γ + H_{n-1}` avec `H_{n-1}` en Fraction rationnelle exacte
  - Précision ≤ 2×10⁻¹⁵ face à `scipy.special.digamma` pour tout n jusqu'à 10 000
  - 4 API : `digamma_pure`, `digamma_pure_exact`, `digamma_pure_asymptotic`, `digamma_high_precision` (Decimal 50 chiffres)
  - **Aucune dépendance à la valeur du n-ième premier** — répond à la demande de Philippe
- Commande CLI `psi <N>` (alias `digamma <N>`) affichant H_{n-1} exact + valeurs float exacte et asymptotique
- 16 nouveaux tests Pytest (`test_digamma_pure_v338.py`)
- `spectral_signature_pure(n)` : signature spectrale pure exposant ψ(n), H_{n-1}, écart à ln(n), résidu asymptotique

### Testé
- **1732 / 1732 tests Pytest passent** (1716 baseline + 16 nouveaux)

---

## [3.37.0] — 2026-02-25

### Ajouté
- **7 traductions internationales complètes de `methode_spectral.thy`**
  - `methode_spectral_en.thy` (English, 3739 lignes)
  - `methode_spectral_es.thy` (Español, 3740 lignes)
  - `methode_spectral_de.thy` (Deutsch, 3741 lignes)
  - `methode_spectral_pt.thy` (Português, 3740 lignes)
  - `methode_spectral_ru.thy` (Русский, 3746 lignes)
  - `methode_spectral_zh.thy` (中文, 3671 lignes)
  - `methode_spectral_ja.thy` (日本語, 3668 lignes)
- Pipeline de traduction `scripts/translate_thy.py` :
  - Parser à balances équilibrées pour `\<open>/\<close>` imbriqués
  - Extraction JSON robuste en 3 stratégies (json → json5 → regex line-by-line)
  - Validateur structurel post-traduction (fallback FR si markers cassés)
  - Batch de 40 segments via Claude Sonnet 4.6 (Emergent Universal Key)
- **Entête bilingue standardisé** (16 lignes) présent en tête de chaque fichier :
  - Libellés traduits dans la langue cible
  - Transcriptions API/IPA universelles (prononciation française préservée)

### Corrigé
- Test `test_starts_with_theory` adapté pour accepter les commentaires d'en-tête (grammaire Isabelle native)

### Vérifié
- **Code HOL strictement identique bit-à-bit** entre les 8 versions linguistiques (vérifié programmatiquement)
- 95 `\<open>` = 95 `\<close>` équilibrés dans chaque fichier

---

## [3.36.0] — 2026-02-24

### Ajouté
- **Auto-adaptive scale** sur les graphiques RsP (`src/visualization/png_renderer.py`)
  - Nouveau champ `CurveData.adaptive_scale` (défaut `False`, activé automatiquement pour courbes RsP)
  - Nouveau champ `CurveData.zoom_y_window` (défaut ±0.02)
  - Détecteur `_should_use_dual_panel()` : 5 critères cumulatifs déterministes
  - Rendu `_render_dual_panel()` : vue complète (haut) + zoom convergence (bas)
- `_build_rsp_curve_data` ajuste `n_max` effectif au dernier k valide (utile pour `ord` plafonné à k=499 par la table 1000-primes)
- Titre multi-lignes explicite quand la table de primes limite le calcul
- 14 nouveaux tests (`test_adaptive_scale_v336.py`)

### Résolu
- Bug visuel signalé par Philippe : le graphique "comparaison asymétrique ordonnée" pour n=1..100 écrasait la convergence vers 1/2 à cause des outliers mathématiquement corrects à k=1 (RsP=-0.17) et k=2 (RsP=+1.05)

### Testé
- 1716 / 1716 tests Pytest passent (1702 baseline + 14 nouveaux)

---

## [3.35.0] — 2026-02 (fusionné avec v3.36)

### Ajouté
- Section XIII actualisée : `RsP = Re = 1/2` comme théorème dans la locale `ensemble_savard`
- Factorisation des modèles `1/k` via la locale `spectral_family`
- Section "Foundations / Meta-theory" avec vision affirmative de l'Hypothèse de Riemann
- 232 slots pré-provisionnés dans `theories/projects/` (ROOT files, .thy blank, README templates)
- Site GitHub Pages (`docs/index.html`)
- Nouveau `RELEASE_NOTES_v3.35.md` en style éditorial

### Corrigé
- CI GitHub Actions (`build.yml`) : Isabelle 2025-2, miroir Cambridge, upload d'artefacts, suppression de Lean
- RAG cognitif aligné avec la vision affirmative et les 3 concordances (Chebyshev-Riemann, Riemann-Savard, Chebyshev-Savard)

---

## [3.34.0] — 2026-02

### Ajouté
- **PreReasoner dynamique** (`src/multiloop/pre_reasoner.py`)
  - 5 modes selon complexité de la requête (skip, minimal, standard, deep, deep+math)
  - Skip du multiloop pour requêtes conversationnelles/textuelles
- **Timer cinéma temps réel** pendant les appels LLM (Rich Live)
- Itérations dynamiques ajustées selon la classe de complexité

---

## [3.33.0] — 2026-06

### Ajouté
- Apprentissage automatique de la Section XIII par Gabriel via RAG
- Intégration des 3 concordances dans la mémoire cognitive

---

## [3.32.0] — 2026-06

### Ajouté
- Section XIII professionnellement rédigée avec preuve du Pont Savard
- Sync GitHub avec la branche parallèle de Philippe

---

## [3.31.0] — 2026-02

### Ajouté
- **Formule `ψ_savard`** (Pont Savard) : lien entre ψ classique de Chebyshev et le régime spectral 1/2
- Documentation du lien entre ψ_savard et les 3 piliers de la Méthode Spectrale

---

## [3.30.0] — 2026-02

### Ajouté
- Parsing des configurations "bloc chaotique" et "bloc ordonné" dans les requêtes CLI
- Contexte d'opinion : Gabriel exprime maintenant explicitement son alignement mathématique quand pertinent

---

## [3.23.0] — 2026-02

### Corrigé
- Preuve Isabelle `preuve_rapport_spectral_limite_savard` (ligne 2556)

---

## [3.22.0] — 2026-02

### Corrigé
- Bugs Isabelle 9 & 10 oubliés lors du fix de v3.21

---

## [3.20.0] — 2026-07

### Ajouté
- Timeout Claude étendu à 90 secondes
- Génération automatique de PNG pour les configurations RsP
- Extension de la preuve des 3 piliers

---

## [3.19.0] — 2026-07

### Corrigé
- 2 bugs critiques signalés par Philippe (audit + trace de reconstruction)

---

## [3.18.0] — 2026-07

### Ajouté
- **Idée originale de Philippe** : preuve machine par l'absurde du postulat spectral
- Nouveau module `composite_absurdity_prover.py`

---

## [3.17.0] — 2026-02

### Corrigé
- Pipeline CI GitHub Actions
- Refonte esthétique du CLI (couleurs, badges, séparateurs)

---

## [3.16.0] — 2026-02

### Ajouté
- Intégration RAG des 15 Q&R validées par Philippe

---

## [3.15.0] — 2026-02

### Ajouté
- Banque de Q&R Méthode Spectrale (fondation du RAG cognitif)

---

## Format des entrées

- **`### Ajouté`** — nouvelles fonctionnalités
- **`### Modifié`** — changements dans des fonctionnalités existantes
- **`### Corrigé`** — corrections de bugs
- **`### Supprimé`** — fonctionnalités retirées
- **`### Sécurité`** — vulnérabilités corrigées
- **`### Testé`** — bilan des tests après release
- **`### Résolu`** — résolution d'un problème utilisateur spécifique
- **`### Vérifié`** — invariants et propriétés validées

---

*Ce fichier est maintenu manuellement par l'auteur. Toute contribution majeure via Pull Request doit ajouter une entrée dans la section `[Unreleased]` (voir [`CONTRIBUTING.md`](./CONTRIBUTING.md) §10).*
