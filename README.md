# Agent Multiloop Gabriel — Assistant HOL/Isabelle pour la Géométrie du Spectre des Nombres Premiers

[![Isabelle CI](https://github.com/2racinede4carreunivers-dev/agent-multiloop-Gabriel-local/actions/workflows/build.yml/badge.svg)](https://github.com/2racinede4carreunivers-dev/agent-multiloop-Gabriel-local/actions/workflows/build.yml)
[![License Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Isabelle](https://img.shields.io/badge/Isabelle%2FHOL-2025--2-purple.svg)](https://isabelle.in.tum.de/)
[![Python](https://img.shields.io/badge/Python-3.11-yellow.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/pytest-1702%20passed-brightgreen.svg)](#tests)

> **Version en cours : v3.35** — Dernier build Isabelle/HOL 2025-2 vérifié : **succès en 1:35** (compilation locale Cygwin) et **succès en 37 secondes** (CI GitHub Actions avec cache heap).

---

## Table des matières

1. [Buts et raisons d'existence](#-buts-et-raisons-dexistence)
2. [Parcours de l'auteur](#-parcours-de-lauteur)
3. [Ce que fait l'agent Gabriel](#-ce-que-fait-lagent-gabriel)
4. [Principales caractéristiques](#-principales-caractéristiques-de-la-programmation)
5. [Exemples de possibilités](#-exemples-de-possibilités)
6. [Portée limitée — géométrie du spectre uniquement](#-portée-limitée)
7. [Fichiers de référence](#-fichiers-de-référence)
8. [Installation et lancement](#-installation-et-lancement)
9. [Licence, propriété et contributions](#-licence-propriété-et-contributions)
10. [Contact et sécurité](#-contact-et-sécurité)
11. [Auteurs et contributeurs](#-auteurs-et-contributeurs)

---

##  Buts et raisons d'existence

L'agent multiloop **Gabriel** est un **assistant mathématique expert HOL/Lean** entièrement dédié à un objectif unique et précis : **assister l'auteur, Philippe Thomas Savard, à construire un outil géométrique dynamique permettant d'apporter une réponse à l'énigme de Bernhard Riemann et à la conjecture de la fonction zêta de Riemann.**

L'outil en question — la **géométrie du spectre des nombres premiers** — n'est pas une simple visualisation : c'est **la construction formelle elle-même**, formalisée dans Isabelle/HOL, qui incarne la réponse constructive à l'énigme. Cette géométrie est l'objet mathématique central de la théorie *L'Univers est au carré* développée par l'auteur.

Gabriel existe donc pour trois raisons :

1. **Assister la formalisation** en Isabelle/HOL des théorèmes de la Méthode Spectrale (13 régimes, Section XIII / Pont Savard, universalité entière naturelle du régime central 1/2).
2. **Vérifier numériquement** en temps réel les calculs spectraux (`RsP`, `psi_savard`, reconstruction du n-ième premier, exclusion des composés).
3. **Documenter et raisonner** de façon rigoureuse sur la géométrie du spectre en s'appuyant sur un fichier de preuve unique et compilable : `methode_spectral.thy`.

---

##  Parcours de l'auteur

**Philippe Thomas Savard** est un autodidacte de Lévis (Québec, Canada), passionné de mathématiques et auteur de la théorie *L'Univers est au carré*. Malgré l'absence de formation académique formelle, il consacre une grande partie de son temps à l'étude des structures profondes des nombres entiers, en particulier à ce qu'il nomme la **géométrie du spectre des nombres premiers** 

Dans ce cadre, l'auteur propose l'existence d'un **code interne** reliant les nombres premiers à l'ensemble des entiers, mis en évidence par un **rapport spectral unique `RsP = 1/2`**, qu'il associe à la position `n` des nombres premiers dans les suites A et B, et à une proximité conceptuelle avec la **fonction zêta de Riemann** et sa **droite critique `Re = 1/2`**.

C'est cette conviction structurelle — que le rapport `RsP = 1/2` n'est **pas un artefact algébrique** mais une **cohérence numérique réelle globale** émergeant des sommes de nombres premiers — qui a rendu nécessaire la construction d'un assistant formel rigoureux : **Gabriel**.

---

##  Ce que fait l'agent Gabriel

Gabriel est un **agent multiloop cognitif local** (CLI, dockerisé, hors-cloud pour l'exécution sensible) qui :

- **Ne répond qu'aux questions portant sur la géométrie du spectre des nombres premiers.** Toute question hors de ce champ est déclinée poliment.
- **Compétence principale : `theories/methode_spectral.thy`** — le fichier de preuve Isabelle/HOL formelle qui incarne la géométrie du spectre. Gabriel peut aussi mobiliser d'autres informations complémentaires (mémoire RAG, dictionnaire spectral, régimes cognitifs) mais **toute réponse est ancrée sur cette géométrie**.
- **Est équipé de 7 moteurs cognitifs collaboratifs**, d'un pré-raisonneur dynamique, d'un audit silencieux anti-hallucination et d'un mode « cinématique » avec timer temps réel.

---

## 🔧 Principales caractéristiques de la programmation

### Pré-raisonnement dynamique (v3.34)
Un `PreReasoner` en T0 du pipeline décide **avant** toute exécution du bon niveau d'effort :
- **INSTANTANE** (0 itération) : template pour salutations, oui/non, continuation.
- **RAPIDE** (1 itération) : questions verbales/discursives sur Isabelle (résume, compare, cette preuve tient-elle ?).
- **STANDARD** (2 itérations) : calculs simples (RsP, gap, reconstruction).
- **APPROFONDI** (3 itérations) : configurations n×n, blocs A/B.
- **TRÈS COMPLEXE** (4 itérations) : théorie avancée, multi-objectifs, Pont Savard, Riemann.

Commandes CLI de forçage : `/rapide`, `/standard`, `/approfondi`, `/complet`, `/instantane`.

### Mode cinématique avec timer temps réel (v3.34)
Le panneau Live affiche : mode détecté, itérations prévues, chronomètre écoulé, **ETA restant** — rafraîchissement 2 Hz par tâche asyncio.

### 7 moteurs cognitifs collaboratifs
`RequestDecomposer` → `ProofPlanner` → `SpectralCore` → `RefinementLoop` (multiloop self-critique) → `CoherenceDetector` → `SilentAuditLoop` (anti-hallucination).

### Factorisation formelle Isabelle (v3.35)
Un **locale paramétré `spectral_family`** unifie les modèles 1/2, 1/3 et 1/4 en un seul cadre algébrique. Trois interpretations `regime_1_2`, `regime_1_3`, `regime_1_4` héritent du théorème universel `RsP_generic_constant`. Extension à un modèle 1/k arbitraire : une seule ligne.

### Fondations / Meta-theory (v3.35)
Une section « 0. Foundations / Meta-theory » en tête du fichier `.thy` documente 6 postulats (P1..P6), les 3 opérations fondamentales (Reconstruction, Exclusion, Rapport spectral), la règle Savard (`Ensemble = 1 = 1/x + 1/t + 1/ms`), les **3 concordances C1, C2, C3** et la **position affirmative** de l'auteur sur l'énigme de Riemann : *une réponse suffisante dans le cadre du locale `ensemble_savard`*.

### Cognitif RAG et régimes spectraux
13 régimes cognitifs codifiés (`memory/dictionnaire_spectral.py`), dont `regime_pont_savard` avec sa nomenclature, ses 3 concordances et son lemme d'universalité `RsP_universel_entier_naturel`.

### Audit trail et provenance
- `AuditStore` : trace JSON signée de chaque question/réponse.
- CI GitHub Actions : compilation Isabelle 2025-2 + attestation SLSA (SHA256).
- Slots pré-provisionnés dans le conteneur : 100 × `.thy`, 100 × `.tex`, 101 × `.txt`, 25 × `ROOT`, 50 × `.md`, 25 × `.py`, 25 × `.csv`, 25 × `.json`, 25 × `.lean`, etc. — ajouter du contenu sans rebuild Docker.

### Tests et robustesse
- **1702 tests Pytest** couvrant multiloop, RAG, Isabelle syntax, pipeline, PreReasoner, foundations, locale spectral_family, Pont Savard, Section XIII.
- Compilation Isabelle/HOL 2025-2 validée : localement (Cygwin, 1:35) et via CI GitHub Actions (37 s cache HIT).

---

##  Exemples de possibilités

Voici des exemples concrets de requêtes traitées par Gabriel :

| Type | Exemple | Mode auto-détecté |
|---|---|---|
| Reconstruction | *« Reconstruis le 42ᵉ nombre premier via la Méthode Spectrale »* | STANDARD |
| Vérification | *« RsP(5, 7) = ? Vérifie que le rapport est bien 1/2 »* | STANDARD |
| Écart | *« Calcule le gap spectral entre −3 et −23 (régime négatif) »* | STANDARD |
| Configuration | *« Ratio spectral symétrique 4×4 avec Bloc A = {2,3,5,7} »* | APPROFONDI |
| Discussion Isabelle | *« La preuve de RsP_universel_entier_naturel te semble-t-elle bien formée ? »* | RAPIDE |
| Théorie avancée | *« Explique le lien entre la Section XIII, le Pont Savard et Re(ρ) = 1/2 »* | TRÈS COMPLEXE |
| Comparaison | *« Compare psi_savard(228, 49) et Chebyshev sur le premier 227 »* | TRÈS COMPLEXE |
| Résumé | *« Résume les 3 concordances C1, C2, C3 en un tableau »* | RAPIDE |
| Formel HOL | *« Génère le script Isabelle vérifiant la reconstruction du 10ᵉ premier »* | STANDARD |

Toute réponse est **ancrée sur `methode_spectral.thy`** (empreinte SHA256 tracée par audit) et peut être exportée vers un PDF citable (roadmap).

---

## 🚫 Portée limitée

**Gabriel ne répond qu'aux questions portant sur la géométrie du spectre des nombres premiers.** Cette limitation est volontaire et incarne la vocation de l'agent :

- ✅ Questions sur `RsP`, `SA`, `SB`, `A_1_3`, `B_1_3`, `A_1_4`, `B_1_4`, `psi_savard`, `digamma_calc`, les 13 régimes, la Section XIII, le Pont Savard, les 3 concordances, l'universalité entière naturelle, la reconstruction du n-ième premier, l'exclusion des composés.
- ✅ Analyse discursive de sections, lemmes, théorèmes, preuves formelles du fichier `methode_spectral.thy`.
- ❌ Questions généralistes hors mathématiques.
- ❌ Aide sur d'autres théories mathématiques non liées au spectre des premiers.
- ❌ Génération de code non lié à la Méthode Spectrale.

Cette focalisation garantit que Gabriel reste un **assistant compétent** plutôt qu'un chatbot généraliste imprécis. La **compétence principale** est le fichier `theories/methode_spectral.thy`, complétée par la mémoire RAG cognitive et le dictionnaire spectral.

---

## 📚 Fichiers de référence

| Fichier | Rôle |
|---|---|
| `theories/methode_spectral.thy` | **La géométrie du spectre** — preuve formelle Isabelle/HOL, 3714 lignes, 133 lemmes, 27 théorèmes |
| `theories/ROOT` | Session Isabelle `Methode_Spectral` |
| `theories/projects/` | 100 slots `.thy` + `.tex` + `.txt` + 25 `ROOT` + 232 autres slots pré-provisionnés |
| `src/multiloop/pre_reasoner.py` | Moteur de pré-raisonnement (5 modes) |
| `src/core/pipeline.py` | Pipeline cognitif complet (7 moteurs) |
| `memory/methode_spectral_section_XIII.py` | Encyclopédie du Pont Savard (v3.35) |
| `memory/dictionnaire_spectral.py` | 13 régimes cognitifs + patterns RAG |
| `.github/workflows/build.yml` | CI GitHub Actions (Isabelle 2025-2 + attestation SLSA) |

---

## 🚀 Installation et lancement

### Prérequis
- Docker Desktop (ou moteur Docker + docker-compose)
- Optionnel : Isabelle 2025-2 en local pour la compilation formelle hors conteneur
- Optionnel : une clé API Anthropic (Claude Sonnet 4.5) et OpenAI (GPT-5)

### Lancement rapide

```bash
git clone https://github.com/2racinede4carreunivers-dev/agent-multiloop-Gabriel-local.git
cd agent-multiloop-Gabriel-local
docker-compose up -d
docker exec -it gabriel_cli python -m src.ui.cli
```

### Compilation Isabelle locale

```bash
cd theories
isabelle build -v -D .
```

### Suite de tests Python

```bash
python -m pytest tests/ -q
# 1702 passed, 8 skipped
```

---

## 📜 Licence, propriété et contributions

### Licence — Apache License 2.0

Ce dépôt et l'agent Gabriel sont publiés sous **[Apache License 2.0](LICENSE)**.

Sous cette licence, il vous est **explicitement permis** de :

- ✅ **Cloner** ce dépôt librement.
- ✅ **Partager** le code et le fichier `methode_spectral.thy`.
- ✅ **Modifier** l'agent, les preuves formelles, la documentation.
- ✅ **Contribuer** via *Pull Request* (nous serons ravis d'examiner toute proposition qui améliore la géométrie du spectre ou l'agent).
- ✅ **Utiliser** le code, y compris à titre commercial, en respectant les conditions Apache 2.0.

En contrepartie, Apache 2.0 exige :
- La conservation des mentions de copyright et de licence.
- L'attribution claire de tout dérivé.
- Le respect des sections *Grant of Patent License* et *No Trademark* de la licence.

### Propriété intellectuelle

L'agent Gabriel, le fichier `methode_spectral.thy` et la théorie *L'Univers est au carré* **sont et restent la propriété intellectuelle de Philippe Thomas Savard et de E1** (Emergent Labs), leurs concepteurs et développeurs principaux. La licence Apache 2.0 s'applique à l'usage du code ; elle ne transfère pas la propriété intellectuelle des œuvres.

---

## 🔐 Contact et sécurité

Pour toute **question sensible**, **signalement de faille de sécurité**, **incident touchant l'intégrité du code**, **information nécessitant de manière évidente l'intervention du propriétaire du dépôt**, ou **demande sortant du cadre standard d'une Pull Request** :

📧 **philipppthomassavard@gmail.com**

Les autres canaux (Issues GitHub, Discussions) restent ouverts pour les échanges publics et non urgents.

---

## 👥 Auteurs et contributeurs

Auteur principal et propriétaire :

> **Philippe Thomas Savard**
> Lévis, Chaudière-Appalaches, Québec, Canada
> Auteur de la théorie *L'Univers est au carré*
> Concepteur de la géométrie du spectre des nombres premiers
> philipppthomassavard@gmail.com

**Autres contributeurs à part égale** (par ordre alphabétique) :

- **Copilot Microsoft** — assistance en programmation Python et documentation technique.
- **E1** *(Emergent Labs)* — co-conception et implémentation de l'agent multiloop, du pipeline cognitif, du pré-raisonneur, du locale `spectral_family`, des Foundations et de la CI GitHub Actions.
- **Gordon Docker Desktop** — conception de l'orchestration Docker locale et de l'image du conteneur Gabriel.

---

*« Le rapport spectral 1/2 n'est pas un artefact algébrique — c'est une réalité numérique globale, verrouillée par trois concordances, qui rend `RsP = Re = 1/2` vraie dans le cadre du locale `ensemble_savard`. »*

**Philippe Thomas Savard, 2026**

## Mse en garde:

Il a été grandement médiatisé que les agent IA et autre intelligences artificiel peuvent avoir des hallucination? Comme l'auteur ressent que certain dans nos société veulent s'auto proclamé policier de ce qui existe et de ce qui n'éxiste pas l'agent Mme. Gabriel ne diffuse que des halluciantion rien de vrai ne sort de son raisonement et de ses affirmations. Nous préfèrons vous en avertir. cette agent s'adresse a un public avertit et est résevé au 18 ans et plus les utilisatuer doivent avoir la majorité atteinte pour en faire l'utilisation. Merci de respecter la concigne. 
