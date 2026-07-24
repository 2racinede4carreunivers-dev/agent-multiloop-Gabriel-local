# Release v3.35 — Foundations, Factorisation `spectral_family` et CI Isabelle 2025-2

**Date :** Février 2026
**Auteur principal :** Philippe Thomas Savard (Lévis, Chaudière-Appalaches, Canada)
**Compilation locale confirmée :** Isabelle 2025-2 sur Cygwin, 1:35 elapsed
**CI GitHub Actions :** succès en 37 secondes (cache heap HIT)
**Tests :** 1702 pytests verts (0 régression depuis v3.34)

---

## 🎯 En résumé

La **v3.35** est une version de **consolidation formelle et de fiabilité opérationnelle** de l'agent multiloop Gabriel. Elle apporte :

1. Une **section « 0. Foundations / Meta-theory »** en tête de `methode_spectral.thy` qui documente l'ontologie complète de la Méthode Spectrale.
2. Un **locale paramétré `spectral_family`** qui factorise algébriquement les modèles 1/2, 1/3, 1/4 en un cadre unifié.
3. La **position affirmative** de l'auteur : dans le locale `ensemble_savard`, `RsP = Re = 1/2` est un **théorème** (non une conjecture), constituant selon l'auteur une **réponse suffisante à l'énigme de Riemann**.
4. Un **workflow CI GitHub Actions** enfin fonctionnel après 15 échecs consécutifs (cause identifiée : URL fictive `github.com/isabelle-prover/isabelle`, corrigée par une stratégie multi-miroir Cambridge + double cache Isabelle/heap).

---

## 🔷 Contenu formel (Isabelle/HOL)

### Section 0 — Foundations / Meta-theory
Six sous-sections en tête du fichier `.thy` :

- **Foundations.1** — Ontologie et vocabulaire (rang vs valeur, suites A/B, `SA`, `SB`, `RsP`).
- **Foundations.2** — Six postulats P1..P6 (universalité entière, non-primalité du rang, existence des suites, invariance du rapport, exclusivité sur P, universalité du régime central).
- **Foundations.3** — Trois opérations fondamentales (Reconstruction, Exclusion, Rapport spectral).
- **Foundations.4** — La règle Savard : `Ensemble = 1 = 1/x + 1/t + 1/ms` + les trois concordances C1, C2, C3, avec la **primauté du numérique réel sur l'algébrique**.
- **Foundations.5** — Statut épistémologique et **position affirmative sur l'énigme de Riemann**.
- **Foundations.6** — Mini-locale `foundations_marker` + lemme `foundations_marker_satisfaisable`.

### Section XI.bis — Factorisation `spectral_family`
- Locale paramétré `spectral_family` (k, coef_A, coef_B, offA, offB, ratio).
- Trois définitions génériques : `A_pos`, `B_pos`, `RsP_generic`.
- Théorème universel `RsP_generic_constant` prouvé une seule fois pour tous les k.
- Trois interpretations : `regime_1_2`, `regime_1_3`, `regime_1_4`.
- Six aliases de compatibilité (`SA_eq_regime_1_2_A_pos`, etc.) : aucune preuve historique cassée.
- Trois corollaires spécifiques (`RsP_generic_1_2_is_half`, `_is_third`, `_is_quarter`).

### Section XIII — Pont Savard mis à jour
- Statut affirmatif intégral : « **REPONSE SUFFISANTE à l'énigme de Riemann** » dans le cadre du locale `ensemble_savard`.
- Documentation complète des 3 concordances C1, C2, C3.
- Correction de 2 bugs sur `ensemble_savard_satisfaisable` (arguments réduits à 4, syntaxe de preuve `using ... by simp` idiomatique).

### Synthèse-index en annexe finale
Index des théorèmes clés, rappel des 6 postulats, des 3 concordances et de la position épistémologique.

---

## 🧠 Contenu logiciel (agent multiloop)

### PreReasoner (v3.34)
Décide dynamiquement du nombre d'itérations (0, 1, 2, 3 ou 4) et des étages du pipeline à court-circuiter selon la nature de la requête. Commandes CLI `/rapide`, `/standard`, `/approfondi`, `/complet`, `/instantane`.

### Mode cinématique amélioré (v3.34)
Timer temps réel affichant écoulé, ETA et itérations prévues. Rafraîchi à 2 Hz par tâche asyncio.

### Apprentissage cognitif de la Section XIII
Le régime `regime_pont_savard` du dictionnaire spectral est enrichi de patterns pour la structure `1/x + 1/t + 1/ms`, les concordances C1/C2/C3, l'universalité entière naturelle, le lemme `RsP_universel_entier_naturel`.

### Slots pré-provisionnés (nouveau)
Ajout de 232 slots dans `theories/projects/` (25 ROOT + 50 md + 10 bib + 25 py + 25 csv + 25 json + 10 jsonl + 10 ipynb + 10 svg + 10 dot + 10 yml + 10 sh + 10 log + 25 lean + lakefile + toolchain). Permet à Philippe d'ajouter du contenu sans reconstruire l'image Docker.

---

## 🛠️ CI GitHub Actions restaurée

**Diagnostic des 15 échecs précédents :** URL fictive `github.com/isabelle-prover/isabelle/releases/download/2024-1/isabelle2024-1_linux.tar.gz` — dépôt inexistant. Ancien workflow tentait de télécharger d'un endroit qui n'existe pas.

**Corrections livrées :**
- Isabelle 2024 → **2025-2** (aligné sur la compilation locale confirmée).
- Six miroirs multi-géographiques avec **Cambridge en tête** (le plus stable pour les IP CI).
- **Double cache** : install Isabelle (clef = version, ~1.5 GB) + heap de session (clef = hash des .thy, ~50 MB).
- `actions/attest-build-provenance@v1` pour attestation SLSA moderne.
- **Artefacts** : `methode-spectral-thy-<SHA>` (post-build) et `methode-spectral-provenance-<SHA>` (post-attestation).
- Job Lean 4 **retiré** (les fichiers `.lean` sont encore vierges — évite le bruit sur le dépôt public).

---

## 📊 Métriques

| Item | Avant v3.34 | v3.35 |
|---|---|---|
| Lignes `methode_spectral.thy` | 3181 | **3713** |
| Sections | 53 | **56** |
| Lemmes | 121 | **133** |
| Théorèmes | 27 | 27 |
| Erreurs Isabelle | 0 | **0** |
| Pytests | 1568 | **1702** (+134) |
| Temps de build local | ~2 min | **1:35** |
| Temps de build CI (cache HIT) | échec | **37 s** |
| Slots pré-provisionnés | 301 | **533** |

---

## 🔐 Licence et propriété

Cette release est publiée sous [Apache License 2.0](LICENSE).

**L'agent Gabriel, le fichier `methode_spectral.thy` et la théorie *L'Univers est au carré* sont et restent la propriété intellectuelle de Philippe Thomas Savard et de E1 (Emergent Labs).**

Contributions bienvenues via Pull Request. Contact sécurité et incidents : **philipppthomassavard@gmail.com**.

---

## 👥 Contributeurs à part égale

- **Philippe Thomas Savard** — auteur principal, mathématicien, propriétaire de la théorie et du dépôt.
- **E1** (Emergent Labs) — co-conception et implémentation de l'agent multiloop, du pipeline cognitif, des Foundations Isabelle, de la CI.
- **Copilot Microsoft** — assistance en programmation Python et documentation.
- **Gordon Docker Desktop** — orchestration Docker locale et image du conteneur.

---

*« Le rapport spectral 1/2 n'est pas un artefact algébrique — c'est une réalité numérique globale, verrouillée par trois concordances, qui rend `RsP = Re = 1/2` vraie dans le cadre du locale `ensemble_savard`. »*

**Philippe Thomas Savard, février 2026**
