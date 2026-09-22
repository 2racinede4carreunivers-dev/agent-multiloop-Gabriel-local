# Pipeline Cognitif Gabriel — Niveaux 1 et 2

Reconstruction des nombres premiers a partir des rapports `1/k`, par le
systeme convolutif spectral :

- **Niveau 1 (entier)** : suites A et B a termes entiers (`k^i`), regles
  Savard terme a terme, 4 possibilites Digamma, division par `k^6`.
- **Niveau 2 (geometrique)** : memes suites en forme `sqrt(a^2 + b^2)` avec
  `a1 = sqrt(1 + k^2)`. Chaque terme geometrique vaut exactement
  `a1 x terme entier`, donc le facteur s'annule dans
  `(Somme_B - Digamma) / k^6` : **les deux niveaux ont les memes utilites**.

Dossier autonome : il suffit de le copier tel quel. Seule dependance
tierce : `numpy` (utilisee par `metaphore_geometrique.py`).

## Contenu

| Fichier | Role |
|---|---|
| `suites_geometriques_niveau2.py` | Coeur : calculateurs niveaux 1 et 2, Digamma, formes fermees, ancrages XIV |
| `reconstruction_premiers_1_sur_k.py` | Reconstructeur de reference 1/7 (16519 via `S_A - 7^8`) |
| `gabriel_geometric_wrapper_v74.py` | `PipelineCognitifNiveaux` : wrapper unifie (typique 1/2, non typiques 1/k) |
| `Suites_geometriques_AB.py` | Suites A/B geometriques generales |
| `fallback_geometrique.py` | Repli geometrique si l'approche algebrique echoue |
| `metaphore_geometrique.py` | Bloc « Structure Geometrique Spatiale » des reponses |
| `validation_section_xiv.py` | Validation de conformite a la Section XIV (exit 0 = conforme) |

## Usage

```python
from pipeline_cognitif import (
    PipelineCognitifNiveaux, CalculateurNiveau1Entiers,
    CalculateurNiveau2Geometrique, Reconstructeur1Sur7,
)

# Pipeline unifie : typique 1/2 (n = position dans P) ou non typique 1/k
p = PipelineCognitifNiveaux(k=7)
r = p.reconstruire(10)     # premier = 16519, ancre rang 1913
r = p.reconstruire(12)     # premier = 16547 (rang 1913 + 2)

# Rapport ordonne suivant l'ordre prescrit (7 etapes) :
print(p.rapport_pipeline(12))
#   [1] sommes A/B a n=10          [2] 4 possibilites Digamma
#   [3] sommes A/B a n=9           [4] coefficients (S(10)-S(9))/k^8
#   [5] (Reste+x) -> blocs A/B     [6] equations generalisees (n > 0)
#   [7] sommes A/B au n demande + premier consequent

# Cles principales du dict retourne par reconstruire(n) :
#   ancrage_n10, sommes_n9, coefficients_niveau_1, niveau_1, niveau_2,
#   premier, position_dans_P (typique) / position_ancre_dans_P (non typique),
#   digamma_calcule_n, verification_equations_au_n, ordre_pipeline

# Niveau 1 direct
calc = CalculateurNiveau1Entiers(k=7)
res = calc.calculer(10)    # S_A = 322966112, S_B = 2260645142

# Validation de conformite (0 ecart attendu)
#   python -m pipeline_cognitif.validation_section_xiv
# ou, en execution directe :
#   python pipeline_cognitif/validation_section_xiv.py
```


## Conformite a la Section XIV de `methode_spectral.thy`

Verifiee par `validation_section_xiv.py` (**0 ecart**, code de sortie 0) :

| Controle | Reference | Resultat |
|---|---|---|
| Ancrages n=10 : rangs officiels = rangs reels dans P | XIV.6 | k=2..9 conformes (29, 227, 947, 2999, 7529, 16519, 32327, 58337) |
| Formes fermees universelles `S_A`, `S_B` | XIV.2 | exactes pour n >= 8 (arithmetique `Fraction`) |
| Construction terme a terme | XIV.4 | niveau 1 exact pour tout n ; niveau 2 = `a1 x XIV.4` |
| Validation exacte k=8, n=34 | XIV.7 | `S_A`, `S_B`, Digamma conformes au chiffre pres ; P = 32537 (rang 3492) |
| Decalage de rang `rang(n) = rang_ancre + (n - 10)` | XIV.6 | k=3, n=9..17 : 223, 227, 229, 233, 239, 241, 251, 257, 263 |
| Niveau 2 : memes ancrages que le niveau 1 | XIV.5 | 8/8 conformes |

### Constantes universelles (XIV.1)

```
C = k^4 - k^2 + 1            m = k^6 - k^5 + 1
alphaA = 2C / ((k-1) k^3)    alphaB = k * alphaA
offsetA = k / (k-1)          offsetB = m k / (k-1)
S_A(n) = (alphaA/2) k^n - offsetA      S_B(n) = (alphaB/2) k^n - offsetB
```

### Domaine des formes fermees (XIV.2 vs XIV.4)

XIV.2 et XIV.4 coincident exactement a partir de **n = 8** (seuil ou les
deux termes terminaux Savard et le saut Zeta s'appliquent). Pour **n <= 7**,
XIV.4 impose `terme_b = terme_a` (progression simple sans condition
terminale) et fait foi : l'implementation retourne la construction XIV.4
telle quelle (`SEUIL_FORMES_FERMEES = 8` dans `suites_geometriques_niveau2.py`).

### Convention Digamma (XIV.5)

Ordre d'ancrage unifie aux deux niveaux : `(8,-1), (8,+1), (7,+1), (7,-1)`
— le premier candidat entier premier dans cet ordre reproduit les huit
ancrages du tableau XIV.6.

## Notes

- `n` est toujours un entier strictement positif (`valider_n` le garantit).
- Toute l'arithmetique du niveau 1 est exacte (`int` / `Fraction`) ; le
  niveau 2 calcule le Digamma sur les composantes zeta entieres pour eviter
  toute erreur d'arrondi flottant.
- Les imports internes sont relatifs avec repli absolu : le dossier
  fonctionne comme package (`from pipeline_cognitif import ...`) et en
  execution directe des scripts.
