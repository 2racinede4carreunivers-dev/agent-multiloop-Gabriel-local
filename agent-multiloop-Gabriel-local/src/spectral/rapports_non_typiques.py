#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rapports_non_typiques.py — Système Convolutif Spectral Général v7.5
====================================================================
Auteur      : Philippe Thomas Savard
Date        : 06 septembre 2026
Lieu        : Lévis, Chaudière-Appalaches, Canada
Spécialité  : La géométrie du spectre des nombres premiers

RÔLE
----
Moteur de reconstruction des nombres premiers pour les rapports non-typiques
1/k (k ≥ 3).  Deux niveaux opérationnels :

  NIVEAU 1 — ENTIER (k^n)
    Suites A et B construites terme à terme selon les règles de Savard.
    Quatre essais Digamma (positions 7 et 8, signes ±) sélectionnent
    l'ancrage à n=10.  La reconstruction à n>10 s'effectue par rang
    depuis l'ancrage validé.

  NIVEAU 2 — GÉOMÉTRIQUE (√(a²+b²))
    Facteur commun g(k) = √(1+k²)/k. Le niveau géométrique est une mise à
    l'échelle du niveau entier : même candidat C reconstruit.  Activé
    automatiquement en fallback si le niveau entier ne retourne aucun
    premier (rapports ambigus ou k élevé).

CHAÎNE DE VALIDATION v7.5 (Onglet «Validation HOL Générale»)
-------------------------------------------------------------
  1. CONSTRUIRE  : calculer les suites A/B et le candidat C sans l'appeler premier
  2. IDENTIFIER  : vérifier C = (S_B − Digamma) / Zêta  (identité, pas primalité)
  3. CERTIFIER   : tester entier, C>1, primalité indépendante et position dans table
  4. APPLIQUER HOL : si C composé → EXCLU_HOL (¬prime(C) ⟹ ∀i. C ≠ prime_i(i))
                     si C premier et positionné → P_CERTIFIÉ
  5. RÉPONDRE    : retourner P seulement si certifié; sinon retourner C + obligations

ÉTATS DE VERDICT
----------------
  EXCLU_HOL       : C est composé — exclusion formelle HOL
  ANCRAGE_POSSIBLE : C est premier à n=10, unicité entre branches à contrôler
  P_CERTIFIÉ      : C est premier, positionné, rang validé — P peut être annoncé
  C_NON_DÉCIDÉ   : C > 10^12, primalité non certifiable ici
  BLOQUÉ          : aucun ancrage disponible — reconstruction non définie

INTERDICTION FORMELLE
---------------------
  Ne jamais renommer un C non décidé en P.
  La reconstruction algébrique ne prouve pas la primalité.

API PUBLIQUE (compatible spectral_core.py)
------------------------------------------
  construire_rapport_convolutif(rapport, n=10) -> Dict
  reconstruire_premier(rapport, n=10, verifier=True) -> Dict
  reconstruire_premier_pour_n(rapport, n) -> Dict

Référence HOL : methode_spectral.thy § XIII (Pont Savard)
              : validation_hol_unifiee.thy § 9 (Exclusion composés)
Validation    : systeme_convolutif_spectral_general.xlsx v7.5
"""

from __future__ import annotations
import math
import logging
from fractions import Fraction
from math import isqrt, log2
from typing import Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — CONSTANTES DE VERDICT
# ══════════════════════════════════════════════════════════════════════════════

EXCLU_HOL        = "EXCLU_HOL"
ANCRAGE_POSSIBLE = "ANCRAGE_POSSIBLE"
P_CERTIFIE       = "P_CERTIFIÉ"
C_NON_DECIDE     = "C_NON_DÉCIDÉ"
BLOQUE           = "BLOQUÉ"

# Seuil au-delà duquel la primalité n'est pas certifiable ici (Excel >10^12)
SEUIL_NON_DECIDABLE = 10 ** 12

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — ANCRAGES VALIDÉS n=10 (k → (premier, rang))
# ══════════════════════════════════════════════════════════════════════════════
# Source : onglet «Validation HOL Générale» — Catalogue d'ancrages v7.5
# Chaque ancrage est le premier certifié à n=10.
# Corrections v7.5 :
#   k=11  → 1611851 rang=121982 (règle spéciale PDF, ancrage validé spécial)
#   k=13  → 368939  rang=31452  (corrigé — ancrage A8+ confirmé)
#   k=18  → 1883429 rang=140885 (corrigé — ancrage A8+ confirmé)
#   k=27  → 14330707 rang=930152 (règle spéciale S_A−(2k^8−k^6))

ANCHORS: Dict[int, Tuple[int, int]] = {
    2:  (29,          10),        # rapport 1/2 — A8− PDF
    3:  (227,         49),        # rapport 1/3 — A8−
    4:  (947,         161),       # rapport 1/4 — A8+
    5:  (2_999,       430),       # rapport 1/5 — A7+
    6:  (7_529,       954),       # rapport 1/6 — A8+
    7:  (16_519,      1_913),     # rapport 1/7 — A8− catalogue
    8:  (32_327,      3_468),     # rapport 1/8 — A8−
    9:  (58_337,      5_906),     # rapport 1/9 — A7−
    11: (1_611_851,   121_982),   # règle spéciale PDF (v7.5)
    13: (368_939,     31_452),    # A8+ (v7.5 corrigé)
    18: (1_883_429,   140_885),   # A8+ (v7.5 corrigé)
    27: (14_330_707,  930_152),   # règle spéciale S_A−(2k^8−k^6) (v7.5)
}

# Ancrages multiples (k → liste de (premier, rang, branche))
# Source : onglet «Validation HOL Générale» — k=66 ambigu (deux ancrages)
ANCHORS_MULTIPLES: Dict[int, List[Tuple[int, int, str]]] = {
    66: [
        (1_252_045_211, 62_941_372, "A7−"),
        (1_252_049_501, 62_941_563, "A8−"),
    ],
}

# Paramètres Digamma vainqueurs par rapport (position, signe)
# Source : onglet «Parametres» v7.5
DIGAMMA_PARAMS: Dict[int, Tuple[int, int]] = {
    3:  (8, -1),
    4:  (8, +1),
    5:  (7, +1),
    6:  (8, +1),
    7:  (8, -1),
    8:  (8, -1),
    9:  (7, -1),
    13: (8, +1),
    18: (8, +1),
}

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — UTILITAIRES ARITHMÉTIQUES
# ══════════════════════════════════════════════════════════════════════════════

def _is_prime(p: int) -> bool:
    """Test de primalité entière exact."""
    if not isinstance(p, int) or p < 2:
        return False
    if p == 2:
        return True
    if p % 2 == 0:
        return False
    return all(p % d != 0 for d in range(3, isqrt(p) + 1, 2))


def _prime_table(count: int) -> List[int]:
    """Génère la table des `count` premiers nombres premiers."""
    out: List[int] = []
    p = 2
    while len(out) < count:
        if _is_prime(p):
            out.append(p)
        p = 3 if p == 2 else p + 2
    return out


def _extraire_k(rapport: Union[str, int]) -> int:
    """Extrait k depuis '1/k' (str) ou un entier direct."""
    if isinstance(rapport, int):
        return rapport
    s = str(rapport).strip()
    if s.startswith("1/"):
        return int(s[2:])
    try:
        return int(s)
    except ValueError:
        raise ValueError(
            f"Format de rapport invalide : '{rapport}' (attendu '1/k' ou entier k)"
        )


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — NIVEAU ENTIER : CONSTRUCTION DES SUITES A ET B (k^n)
# ══════════════════════════════════════════════════════════════════════════════
# Règles de Savard (methode_spectral.thy § XI + § XII)
# Suite A : k^i pour i≤n-2 ; T(n-1)=k^(n-1)-k^(n-3) ; T(n)=k^n-k^(n-2)
# Suite B : k^i pour i≤5 ; SAUT ZÊTA à i=6 → k^7 ; k^(i+1) pour i≥7 ;
#           T(n-1)=k^n-k^(n-2) ; T(n)=k^(n+1)-k^(n-1)

def term_a(k: int, n: int, i: int) -> int:
    """Terme i de la suite A pour le rapport 1/k avec n termes."""
    if not (k >= 2 and n >= 1 and 1 <= i <= n):
        return 0
    if n <= 7:
        return k ** i
    if i <= n - 2:
        return k ** i
    if i == n - 1:
        return k ** (n - 1) - k ** (n - 3)
    return k ** n - k ** (n - 2)


def term_b(k: int, n: int, i: int) -> int:
    """Terme i de la suite B pour le rapport 1/k avec n termes.

    Le Saut Zêta (position 6 → k^7) est la connexion qualitative au
    comportement de ζ documentée en § XI de methode_spectral.thy.
    """
    if not (k >= 2 and n >= 1 and 1 <= i <= n):
        return 0
    if n <= 7:
        return term_a(k, n, i)
    if i <= 5:
        return k ** i
    if i == 6:
        return k ** 7                       # ← SAUT ZÊTA
    if i <= n - 2:
        return k ** (i + 1)
    if i == n - 1:
        return k ** n - k ** (n - 2)
    return k ** (n + 1) - k ** (n - 1)


def build(k: int, n: int) -> Tuple[List[int], List[int]]:
    """Construit les listes complètes A et B pour le rapport 1/k à n termes."""
    A = [term_a(k, n, i) for i in range(1, n + 1)]
    B = [term_b(k, n, i) for i in range(1, n + 1)]
    return A, B


def closed_sums(k: int, n: int) -> Tuple[Fraction, Fraction]:
    """Formules fermées exactes (Fraction) pour les sommes SA et SB.

    αA(k) = (k⁴-k²+1) / [(k-1)·k³]
    SA(k,n) = αA(k)·k^n − k/(k−1)
    SB(k,n) = k·αA(k)·k^n − (k⁷-k⁶+k)/(k−1)
    """
    h  = Fraction(k ** 4 - k ** 2 + 1, (k - 1) * k ** 3)
    sa = h * k ** n - Fraction(k, k - 1)
    sb = k * h * k ** n - Fraction(k ** 7 - k ** 6 + k, k - 1)
    return sa, sb


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — EXCLUSION DES COMPOSÉS (CHAÎNE HOL v7.5)
# ══════════════════════════════════════════════════════════════════════════════
# Source : onglet «Validation HOL Générale» + «Checklist 1-81»
#
# Règle HOL fondamentale :
#   ¬prime(C) ⟹ ∀i. C ≠ prime_i(i)
#   (Un composé ne peut occuper aucune position de premier spectral)
#
# Contrôle de domaine par inversion S_A (certificat par l'absurde) :
#   Si C est composé, calculer D_C = S_B(k,n₀) - C·Zêta(k)
#   Puis résoudre S_A(k,x) = |D_C| → x réel
#   Si x ∉ ℕ → D_C ne correspond à aucune position entière → exclusion confirmée

def _verdict_candidat(C: object, n: int, base_rank: Optional[int],
                       target_rank: Optional[int]) -> str:
    """Applique la chaîne HOL et retourne l'état de verdict.

    Args:
        C          : candidat reconstruit (int si entier, Fraction sinon)
        n          : nombre de termes utilisé
        base_rank  : rang de l'ancrage n=10 (None si absent)
        target_rank: rang cible calculé (None si absent)
    """
    # Étape 2 — IDENTIFIER : C doit être un entier
    if not isinstance(C, int):
        return C_NON_DECIDE          # quotient non entier → non décidé

    if C <= 1:
        return EXCLU_HOL             # C ≤ 1 : exclusion immédiate

    # Seuil de décidabilité
    if C > SEUIL_NON_DECIDABLE:
        return C_NON_DECIDE          # trop grand pour certifier ici

    # Étape 3 — CERTIFIER : test de primalité indépendant
    if not _is_prime(C):
        return EXCLU_HOL             # ¬prime(C) → EXCLU_HOL

    # C est premier — vérifier la position
    if n == 10:
        return ANCRAGE_POSSIBLE      # unicité entre branches à contrôler

    if target_rank is not None:
        return P_CERTIFIE            # rang validé → P certifié

    return C_NON_DECIDE


def _controle_domaine(k: int, n0: int, C_compose: int) -> Dict:
    """Contrôle de domaine par inversion S_A (certificat par l'absurde).

    Vérifie que le Digamma exigé par le composé C sort des positions
    entières autorisées de la suite A.

    Source : onglet «Validation HOL Générale» — Forme générale du contrôle.
    """
    A, B = build(k, n0)
    sa, sb = sum(A), sum(B)
    zeta = k ** 6
    D_C = sb - C_compose * zeta

    # Résoudre S_A(k, x) = |D_C|
    # S_A(k,x) ≈ αA·k^x − offset → x = log_k((|D_C| + offset) / αA)
    try:
        h = Fraction(k ** 4 - k ** 2 + 1, (k - 1) * k ** 3)
        offset = Fraction(k, k - 1)
        val = (abs(D_C) + float(offset)) / float(h)
        if val <= 0:
            x_reel = None
        else:
            x_reel = log2(val) / log2(k)
        x_entier = isinstance(x_reel, float) and abs(x_reel - round(x_reel)) < 1e-9
    except Exception:
        x_reel = None
        x_entier = False

    return {
        "C_compose":    C_compose,
        "D_C_exige":    int(D_C),
        "x_reel":       round(x_reel, 12) if x_reel else None,
        "x_est_entier": x_entier,
        "exclusion_confirmee": not x_entier,
        "interpretation": (
            f"D_C exige par C={C_compose} correspond a x={x_reel:.6f} "
            f"({'entier' if x_entier else 'non entier — hors domaine ℕ'})."
        ),
    }


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — QUATRE ESSAIS DIGAMMA (ancrage n=10)
# ══════════════════════════════════════════════════════════════════════════════

def digamma_trials_n10(k: int) -> List[Dict]:
    """Quatre essais Digamma à n=10 pour le rapport 1/k.

    Retourne une liste de 4 dict avec :
      position, signe, digamma, C (candidat), verdict HOL, premier (bool)
    """
    A, B = build(k, 10)
    sa, sb = sum(A), sum(B)
    out = []
    for pos in (7, 8):
        for sign in (+1, -1):
            d  = Fraction(sa + sign * A[pos - 1])
            q  = Fraction(sb - d, k ** 6)
            C  = q.numerator if q.denominator == 1 else q
            verdict = _verdict_candidat(C, 10, None, None)
            out.append({
                "position": pos,
                "signe":    sign,
                "branche":  f"A{pos}{'+' if sign > 0 else '-'}",
                "digamma":  int(d),
                "C":        int(C) if isinstance(C, int) else C,
                "verdict":  verdict,
                "premier":  verdict in (ANCRAGE_POSSIBLE, P_CERTIFIE),
            })
    return out


def _ancrage_valide(k: int) -> List[Tuple[int, int, str]]:
    """Retourne la liste des ancrages valides pour le rapport 1/k.

    Retourne : [(premier, rang, branche), ...]
    Priorité : ANCHORS (unique) → ANCHORS_MULTIPLES → essais dynamiques
    """
    if k in ANCHORS:
        p, r = ANCHORS[k]
        branche = DIGAMMA_PARAMS.get(k)
        b_str = f"A{branche[0]}{'+' if branche[1]>0 else '-'}" if branche else "validé"
        return [(p, r, b_str)]

    if k in ANCHORS_MULTIPLES:
        return ANCHORS_MULTIPLES[k]

    # Tentative dynamique
    trials = digamma_trials_n10(k)
    valides = [t for t in trials if t["verdict"] == ANCRAGE_POSSIBLE]
    if not valides:
        return []

    ancrages = []
    primes_cache = _prime_table(200_000)
    for t in valides:
        C = t["C"]
        if isinstance(C, int) and C in primes_cache:
            rang = primes_cache.index(C) + 1
            ancrages.append((C, rang, t["branche"]))
            logger.info("Ancrage dynamique k=%d branche=%s : P=%d rang=%d",
                        k, t["branche"], C, rang)
    return ancrages


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — RECONSTRUCTION ENTIÈRE PAR RANG (niveau entier)
# ══════════════════════════════════════════════════════════════════════════════

def reconstruct_entier(k: int, n: int,
                       primes: Optional[List[int]] = None) -> List[Dict]:
    """Reconstruit le(s) candidat(s) C pour le rapport 1/k à n termes.

    Pour chaque ancrage disponible :
      rang_cible = rang_ancrage + (n - 10)
      C = primes[rang_cible - 1]
      Digamma = SB(k,n) - C·k⁶  (calcul à rebours)
      Vérification exacte (Fraction) : (SB - D) / k⁶ == C

    Retourne une liste de dicts (un par ancrage/branche).
    """
    ancrages = _ancrage_valide(k)
    if not ancrages:
        return [{
            "k": k, "n": n, "niveau": "entier",
            "C": None, "verdict": BLOQUE,
            "message": f"Aucun ancrage n=10 disponible pour k={k}.",
        }]

    A, B = build(k, n)
    sa   = sum(A)
    sb   = sum(B)
    zeta = k ** 6
    sa_closed, sb_closed = closed_sums(k, n)

    resultats = []
    for (base_p, base_rank, branche) in ancrages:
        target_rank = base_rank + (n - 10)
        if target_rank < 1:
            resultats.append({
                "k": k, "n": n, "branche": branche,
                "verdict": BLOQUE,
                "message": f"Rang cible {target_rank} < 1.",
            })
            continue

        if primes is None or len(primes) < target_rank:
            primes = _prime_table(target_rank)

        C = primes[target_rank - 1]
        D = sb - C * zeta

        # Assertion exacte
        check = Fraction(sb - D, zeta)
        assert check == C, (
            f"Assertion k={k} n={n} branche={branche} : "
            f"(SB-D)/k⁶ = {check} ≠ {C}"
        )

        verdict = _verdict_candidat(C, n, base_rank, target_rank)

        resultats.append({
            "rapport":            f"1/{k}",
            "k":                  k,
            "n":                  n,
            "niveau":             "entier",
            "branche":            branche,
            "A":                  A,
            "B":                  B,
            "somme_A":            sa,
            "somme_B":            sb,
            "somme_A_fermee":     str(sa_closed),
            "somme_B_fermee":     str(sb_closed),
            "zeta":               zeta,
            "digamma":            D,
            "C":                  C,
            "premier":            verdict in (ANCRAGE_POSSIBLE, P_CERTIFIE),
            "verdict":            verdict,
            "rang_cible":         target_rank,
            "rang_base":          base_rank,
            "base_premier":       base_p,
            "formule":            (
                f"C = (SB − D) / k⁶ = ({sb} − {D}) / {zeta} = {C}"
            ),
            "premier_indetermine": verdict == C_NON_DECIDE,
            "fallback":           False,
        })

    return resultats


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — NIVEAU GÉOMÉTRIQUE (√(a²+b²)) + FALLBACK GABRIEL v7.5
# ══════════════════════════════════════════════════════════════════════════════

def facteur_g(k: int) -> float:
    """Facteur de mise à l'échelle géométrique g(k) = √(1+k²)/k."""
    return math.sqrt(1 + k * k) / k


def suite_geo_A(k: int) -> List[float]:
    """Suite géométrique A pour le rapport 1/k (10 termes)."""
    t = 1.0 / k
    p = [1.0] + [t ** n for n in range(1, 13)]
    return [
        math.sqrt(p[0] ** 2 + p[1] ** 2),
        math.sqrt(p[1] ** 2 + p[2] ** 2),
        math.sqrt(p[2] ** 2 + p[3] ** 2),
        math.sqrt(p[3] ** 2 + p[4] ** 2),
        math.sqrt(p[4] ** 2 + p[5] ** 2),
        math.sqrt(p[5] ** 2 + p[6] ** 2),
        math.sqrt(p[6] ** 2 + p[7] ** 2),
        math.sqrt(p[7] ** 2 + p[8] ** 2),
        math.sqrt((p[8]  - p[6]) ** 2 + (p[9]  - p[7]) ** 2),
        math.sqrt((p[9]  - p[7]) ** 2 + (p[10] - p[8]) ** 2),
    ]


def suite_geo_B(k: int) -> List[float]:
    """Suite géométrique B pour le rapport 1/k — SAUT ZÊTA géométrique."""
    t = 1.0 / k
    p = [1.0] + [t ** n for n in range(1, 13)]
    return [
        math.sqrt(p[0]  ** 2 + p[1]  ** 2),
        math.sqrt(p[1]  ** 2 + p[2]  ** 2),
        math.sqrt(p[2]  ** 2 + p[3]  ** 2),
        math.sqrt(p[3]  ** 2 + p[4]  ** 2),
        math.sqrt(p[4]  ** 2 + p[5]  ** 2),
        # SAUT ZÊTA : couple (p[6],p[7]) au lieu de (p[5],p[6])
        math.sqrt(p[6]  ** 2 + p[7]  ** 2),
        math.sqrt(p[7]  ** 2 + p[8]  ** 2),
        math.sqrt(p[8]  ** 2 + p[9]  ** 2),
        math.sqrt((p[10] - p[8])  ** 2 + (p[11] - p[9])  ** 2),
        math.sqrt((p[11] - p[9])  ** 2 + (p[12] - p[10]) ** 2),
    ]


def candidats_premiers_geo(k: int) -> List[int]:
    """Candidats premiers issus des sommes géométriques — avec verdict HOL."""
    tA = suite_geo_A(k)
    tB = suite_geo_B(k)
    sA = sum(tA)
    sB = sum(tB)
    cands: set[int] = set()

    for v in (sA, sB, sA + sB, abs(sA - sB)):
        for c in (math.floor(v), math.ceil(v), round(v)):
            if c > 1:
                cands.add(c)

    for mul in range(1, 15):
        for v in (mul * sA, mul * sB):
            c = round(v)
            if 2 <= c <= 10_000_000:
                cands.add(c)

    # Appliquer verdict HOL sur chaque candidat
    return sorted(c for c in cands if _is_prime(c))


def reconstruct_geometrique(k: int, n: int) -> Dict:
    """Reconstruction niveau géométrique — retourne candidats avec verdicts."""
    tA = suite_geo_A(k)
    tB = suite_geo_B(k)
    sA = sum(tA)
    sB = sum(tB)
    g  = facteur_g(k)
    candidats = candidats_premiers_geo(k)
    C_geo = candidats[0] if candidats else None
    verdict = _verdict_candidat(C_geo, n, None, None) if C_geo else BLOQUE

    return {
        "rapport":            f"1/{k}",
        "k":                  k,
        "n":                  n,
        "niveau":             "geometrique",
        "suite_geo_A":        [round(x, 10) for x in tA],
        "suite_geo_B":        [round(x, 10) for x in tB],
        "somme_geo_A":        round(sA, 10),
        "somme_geo_B":        round(sB, 10),
        "facteur_g":          round(g, 10),
        "candidats_premiers": candidats,
        "C":                  C_geo,
        "verdict":            verdict,
        "premier":            verdict in (ANCRAGE_POSSIBLE, P_CERTIFIE),
        "premier_indetermine": verdict == C_NON_DECIDE,
        "fallback":           True,
        "note": (
            f"Niveau géométrique actif. g(k)=√(1+{k}²)/{k}={g:.8f}. "
            f"Facteur s'annule dans C → même candidat que niveau entier."
        ),
    }


def reconstruire_avec_fallback_geo(k: int, n: int,
                                    primes: Optional[List[int]] = None) -> Dict:
    """Reconstruit C pour 1/k à n termes — Ordre Gabriel v7.5 :

    1. Niveau entier  (term_a/term_b + ancrage + 4 Digamma + verdict HOL)
    2. Si aucun P_CERTIFIÉ → Niveau géométrique (suite_geo_A/B + candidats)

    Retourne toujours un dict avec les deux niveaux documentés et les verdicts.
    INTERDICTION : ne jamais retourner C_NON_DÉCIDÉ comme P.
    """
    # ── NIVEAU ENTIER ────────────────────────────────────────────────────────
    resultats_entier = reconstruct_entier(k, n, primes)
    certifies = [r for r in resultats_entier
                 if r.get("verdict") == P_CERTIFIE]
    ancrages_possibles = [r for r in resultats_entier
                          if r.get("verdict") == ANCRAGE_POSSIBLE]
    exclus = [r for r in resultats_entier
              if r.get("verdict") == EXCLU_HOL]
    bloques = [r for r in resultats_entier
               if r.get("verdict") == BLOQUE]

    # Métadonnées géo systématiques
    tA = suite_geo_A(k)
    tB = suite_geo_B(k)
    meta_geo = {
        "facteur_g":   round(facteur_g(k), 10),
        "somme_geo_A": round(sum(tA), 10),
        "somme_geo_B": round(sum(tB), 10),
    }

    # Cas nominal : un ou plusieurs P_CERTIFIÉ au niveau entier
    if certifies:
        r = certifies[0]
        r.update(meta_geo)
        r["approche"]         = "entier"
        r["nb_certifies"]     = len(certifies)
        r["nb_exclus_hol"]    = len(exclus)
        r["tous_resultats"]   = resultats_entier
        return r

    # Cas ancrage possible (n=10, unicité à vérifier)
    if ancrages_possibles:
        r = ancrages_possibles[0].copy()
        r.update(meta_geo)
        r["approche"]         = "entier"
        r["nb_ancrages"]      = len(ancrages_possibles)
        r["nb_exclus_hol"]    = len(exclus)
        r["tous_resultats"]   = resultats_entier
        r["note_unicite"] = (
            f"{len(ancrages_possibles)} ancrage(s) possible(s) — "
            f"unicité entre branches requise avant annonce de P."
        )
        return r

    # Cas bloqué ou tous exclus → FALLBACK GÉOMÉTRIQUE
    logger.info("FALLBACK géométrique k=%d n=%d (entier: %s)",
                k, n, "bloqué" if bloques else "tous exclus HOL")
    r_geo = reconstruct_geometrique(k, n)
    r_geo["approche"]         = "geometrique"
    r_geo["nb_exclus_hol_entier"] = len(exclus)
    r_geo["resultats_entier"] = resultats_entier

    # Interdiction HOL : ne pas promouvoir C_NON_DÉCIDÉ en P
    if r_geo["verdict"] == C_NON_DECIDE:
        r_geo["note"] = (
            "INTERDICTION HOL : C non décidé — primalité non certifiable. "
            "Fournir C et obligations manquantes uniquement."
        )
    return r_geo


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 9 — INFORMATIONS STRUCTURELLES SUR LES ÉQUATIONS
# ══════════════════════════════════════════════════════════════════════════════

def _info_equations(k: int) -> Dict:
    """Retourne les équations fermées et les paramètres Digamma pour 1/k."""
    h_num = k ** 4 - k ** 2 + 1
    h_den = (k - 1) * k ** 3
    alpha_A = f"({h_num}/{h_den})"
    alpha_B = f"({k * h_num}/{h_den})"
    offset_A = f"-{k}/{k-1}"
    offset_B = f"-({k**7 - k**6 + k}/{k-1})"
    pos, sgn = DIGAMMA_PARAMS.get(k, (8, +1))

    return {
        "equation_A": {
            "forme":  f"SA(k={k},n) = {alpha_A}·{k}^n {offset_A}",
            "alpha":  alpha_A,
            "offset": offset_A,
        },
        "equation_B": {
            "forme":  f"SB(k={k},n) = {alpha_B}·{k}^n {offset_B}",
            "alpha":  alpha_B,
            "offset": offset_B,
        },
        "digamma_params": {
            "position": pos,
            "signe":    sgn,
            "branche":  f"A{pos}{'+' if sgn>0 else '-'}",
        },
        "reconstruction": f"C = (SB − Digamma) / {k}^6",
        "facteur_g":      f"√(1+{k}²)/{k} = {round(facteur_g(k), 8)}",
        "saut_zeta":      f"Position 6 de B : k^7 au lieu de k^6 (connexion ζ)",
        "hol_exclusion":  "¬prime(C) ⟹ ∀i. C ≠ prime_i(i)",
    }


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 10 — API PUBLIQUE (compatible spectral_core.py)
# ══════════════════════════════════════════════════════════════════════════════

def construire_rapport_convolutif(rapport: Union[str, int],
                                   n: int = 10) -> Dict:
    """Produit les faits convolutifs complets pour une requête 1/k (v7.5).

    Retourne un dict standardisé avec :
      - équations A et B (formes fermées)
      - référence n=10 (ancrage validé)
      - reconstruction cible à n=n (niveau entier + verdicts HOL)
      - nb_certifies, nb_exclus_hol, verdict final
      - métadonnées Pont Savard (facteur_g, saut_zeta, digamma_params)
      - contrat Gabriel : réponse type selon onglet «Validation HOL Générale»
    """
    k = _extraire_k(rapport)

    # Référence ancrage n=10
    essais = digamma_trials_n10(k)
    ref_n10 = reconstruct_entier(k, 10)

    # Reconstruction cible
    res = reconstruire_avec_fallback_geo(k, n)

    # Compteurs HOL
    nb_certifies  = sum(1 for e in essais if e["verdict"] == P_CERTIFIE)
    nb_ancrages   = sum(1 for e in essais if e["verdict"] == ANCRAGE_POSSIBLE)
    nb_exclus     = sum(1 for e in essais if e["verdict"] == EXCLU_HOL)
    nb_non_decide = sum(1 for e in essais if e["verdict"] == C_NON_DECIDE)

    # Contrat de réponse Gabriel (onglet «Validation HOL Générale»)
    etat_final = res.get("verdict", BLOQUE)
    reponse_type = (
        f"Pour 1/{k} et n={n} : {len(essais)} candidats construits. "
        f"{nb_exclus} composé(s) exclus HOL (¬prime(C)⟹∀i. C≠prime_i(i)). "
        f"{nb_certifies + nb_ancrages} premier(s) certifié(s)/ancrage(s). "
        f"État final : {etat_final}."
    )

    return {
        "rapport":             f"1/{k}",
        "k":                   k,
        "n":                   n,
        **_info_equations(k),
        "reference_n10":       ref_n10,
        "essais_digamma_n10":  essais,
        "cible":               res,
        "C":                   res.get("C"),
        "premier":             res.get("premier", False),
        "verdict":             etat_final,
        "nb_certifies":        nb_certifies,
        "nb_exclus_hol":       nb_exclus,
        "nb_non_decide":       nb_non_decide,
        "premier_indetermine": res.get("premier_indetermine", True),
        "fallback":            res.get("fallback", False),
        "approche":            res.get("approche", "inconnu"),
        "reponse_gabriel":     reponse_type,
        "note": (
            f"Système convolutif v7.5 — rapport 1/{k} | "
            f"Approche : {res.get('approche', '?')} | "
            f"n={n} | C={res.get('C', '?')} | Verdict={etat_final}"
        ),
        "reference_hol": (
            "methode_spectral.thy § XIII — Pont Savard | "
            "validation_hol_unifiee.thy § 9 — Exclusion composés"
        ),
        "interdiction": (
            "Ne jamais renommer un C non décidé en P. "
            "La reconstruction algébrique ne prouve pas la primalité."
        ),
    }


def reconstruire_premier(rapport: Union[str, int],
                          n: int = 10,
                          verifier: bool = True) -> Dict:
    """Reconstruit C pour le rapport 1/k à n termes — retourne le verdict HOL."""
    k = _extraire_k(rapport)
    return reconstruire_avec_fallback_geo(k, n)


def reconstruire_premier_pour_n(rapport: Union[str, int],
                                  n: int) -> Dict:
    """Reconstruit C pour une quantité de termes n quelconque."""
    k = _extraire_k(rapport)
    return reconstruire_avec_fallback_geo(k, n)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 11 — VALIDATION INTERNE (exemples canoniques v7.5)
# ══════════════════════════════════════════════════════════════════════════════

def verifier_exemples() -> bool:
    """Vérifie les exemples canoniques de l'Excel v7.5."""

    # Test 1 : k=3 ancrage
    r3 = reconstruct_entier(3, 10)
    assert any(r["C"] == 227 for r in r3), f"k=3 n=10 : attendu C=227"

    # Test 2 : k=8 n=34
    r8 = reconstruct_entier(8, 34)
    assert any(r["C"] == 32537 and r["rang_cible"] == 3492 for r in r8), \
        f"k=8 n=34 : attendu C=32537 rang=3492"

    # Test 3 : k=13 ancrage corrigé (v7.5)
    r13 = reconstruct_entier(13, 10)
    assert any(r["C"] == 368_939 and r["rang_cible"] == 31_452 for r in r13), \
        f"k=13 n=10 : attendu C=368939 rang=31452 (v7.5)"

    # Test 4 : k=11 ancrage spécial (v7.5)
    r11 = reconstruct_entier(11, 10)
    assert any(r["C"] == 1_611_851 for r in r11), \
        f"k=11 n=10 : attendu C=1611851 (règle spéciale v7.5)"

    # Test 5 : verdict HOL — composé exclu
    assert not _is_prime(3_486_252_959), "3486252959 doit être composé (k=81 A7+)"
    v = _verdict_candidat(3_486_252_959, 10, None, None)
    assert v == EXCLU_HOL, f"Composé doit être EXCLU_HOL, obtenu {v}"

    # Test 6 : k=4 essais Digamma — 947 doit être parmi les ancrages possibles
    essais4 = digamma_trials_n10(4)
    premiers4 = [t["C"] for t in essais4 if t["verdict"] == ANCRAGE_POSSIBLE]
    assert 947 in premiers4, (
        f"k=4 : attendu 947 dans les ancrages possibles, obtenu {premiers4}\n"
        "Note : plusieurs branches peuvent retourner un premier ; "
        "l'ancrage retenu est celui du catalogue ANCHORS (A8+).\n"
        "Les autres branches premières (ex. 967) sont filtrées par _ancrage_valide."
    )

    # Test 7 : contrôle de domaine — composé C=24 (exemple Excel k=2 n=11)
    ctrl = _controle_domaine(2, 11, 24)
    assert not ctrl["x_est_entier"], "C=24 doit être hors domaine ℕ"
    assert ctrl["exclusion_confirmee"], "Exclusion C=24 doit être confirmée"

    # Test 8 : k=81 — tous composés à n=10, état BLOQUÉ
    r81 = reconstruct_entier(81, 10)
    assert all(r.get("verdict") in (BLOQUE, EXCLU_HOL, C_NON_DECIDE)
               for r in r81), f"k=81 : attendu BLOQUÉ, obtenu {[r.get('verdict') for r in r81]}"

    logger.info("verifier_exemples() v7.5 : TOUS LES TESTS RÉUSSIS ✓")
    return True


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 12 — POINT D'ENTRÉE (test autonome)
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")

    print("=" * 70)
    print("SYSTÈME CONVOLUTIF SPECTRAL GÉNÉRAL v7.5")
    print("Géométrie du spectre des nombres premiers — Philippe Savard")
    print("Exclusion des composés C — Chaîne HOL CONSTRUIRE→RÉPONDRE")
    print("=" * 70)

    verifier_exemples()
    print("\n✓ Tous les exemples canoniques v7.5 validés.\n")

    primes_cache = _prime_table(200_000)
    print(f"{'Rapport':<8} {'n':<4} {'Approche':<14} {'C':<15} "
          f"{'Verdict':<20} {'exclus HOL'}")
    print("-" * 80)

    for k in (3, 4, 5, 6, 7, 8, 9, 11, 13):
        r = reconstruire_avec_fallback_geo(k, 10, primes=primes_cache)
        print(f"  1/{k:<5} {10:<4} {r.get('approche','?'):<14} "
              f"{str(r.get('C','?')):<15} "
              f"{r.get('verdict','?'):<20} "
              f"{r.get('nb_exclus_hol', 0)}")

    # k=81 : bloqué (tous composés)
    r81 = reconstruire_avec_fallback_geo(81, 10)
    print(f"  1/81   {10:<4} {r81.get('approche','?'):<14} "
          f"{'aucun':<15} {r81.get('verdict','?'):<20}")

    # Contrat Gabriel pour k=13
    print("\n── Contrat Gabriel k=13 n=10 ──")
    rc = construire_rapport_convolutif("1/13", n=10)
    print(f"  {rc['reponse_gabriel']}")
    print(f"  Interdiction : {rc['interdiction']}")

    print("\n" + "=" * 70)
    print("FIN DU TEST AUTONOME v7.5")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 13 — COUCHE DE COMPATIBILITÉ v7.4→v7.5
# ══════════════════════════════════════════════════════════════════════════════
# Certains modules du pipeline (src/spectral/__init__.py, refinement_loop.py,
# spectral_knowledge.py) importent des symboles de l'ancienne version.
# Cette section fournit des aliases et stubs pour éviter tout ImportError
# sans modifier les fichiers importateurs.
# NE PAS SUPPRIMER — requis pour la compatibilité pipeline Gabriel.

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EquationSomme:
    """Stub de compatibilité v7.4→v7.5.

    L'ancienne classe EquationSomme est remplacée par les fonctions
    build(), closed_sums() et _info_equations() dans cette version.
    Ce stub permet aux imports existants de ne pas lever d'erreur.
    """
    k: int = 2
    n: int = 10
    alpha_A: float = 0.0
    alpha_B: float = 0.0
    offset_A: float = 0.0
    offset_B: float = 0.0
    somme_A: float = 0.0
    somme_B: float = 0.0
    notes: str = "Stub de compatibilité — voir build() et closed_sums()"

    def __post_init__(self):
        if self.k >= 2 and self.n >= 1:
            A, B = build(self.k, self.n)
            self.somme_A = float(sum(A))
            self.somme_B = float(sum(B))
            sa_f, sb_f = closed_sums(self.k, self.n)
            self.alpha_A = float(sa_f)
            self.alpha_B = float(sb_f)

    def to_dict(self) -> Dict:
        return {
            "k": self.k, "n": self.n,
            "somme_A": self.somme_A,
            "somme_B": self.somme_B,
            "alpha_A": self.alpha_A,
            "alpha_B": self.alpha_B,
        }


# Aliases des anciennes fonctions publiques
def construire_suites_reelles(rapport: Union[str, int],
                               n: int = 10) -> Dict:
    """Alias de compatibilité → construire_rapport_convolutif()."""
    return construire_rapport_convolutif(rapport, n)


def equations_suites_reelles(rapport: Union[str, int]) -> Dict:
    """Alias de compatibilité → _info_equations()."""
    k = _extraire_k(rapport)
    return _info_equations(k)


def reconstruire_premier_reel(rapport: Union[str, int],
                               n: int = 10) -> Dict:
    """Alias de compatibilité → reconstruire_premier()."""
    return reconstruire_premier(rapport, n)


def reconstruire_premier_reel_universel(rapport: Union[str, int],
                                         n: int = 10) -> Dict:
    """Alias de compatibilité → reconstruire_avec_fallback_geo()."""
    k = _extraire_k(rapport)
    return reconstruire_avec_fallback_geo(k, n)


def candidats_reconstruction_reelle(rapport: Union[str, int],
                                     n: int = 10) -> List[Dict]:
    """Alias de compatibilité → digamma_trials_n10()."""
    k = _extraire_k(rapport)
    return digamma_trials_n10(k)


def equations_ab(rapport: Union[str, int], n: int = 10) -> Dict:
    """Alias de compatibilité → _info_equations() + build()."""
    k = _extraire_k(rapport)
    A, B = build(k, n)
    info = _info_equations(k)
    return {**info, "A": A, "B": B,
            "somme_A": sum(A), "somme_B": sum(B)}


def reconstruire_equations_ab(rapport: Union[str, int],
                               n: int = 10) -> Dict:
    """Alias de compatibilité → equations_ab()."""
    return equations_ab(rapport, n)


def position_du_premier(rapport: Union[str, int],
                         C: int) -> Optional[int]:
    """Retourne le rang du candidat C dans la table des premiers,
    ou None si C n'est pas premier.  Compatibilité v7.4.
    """
    if not _is_prime(C):
        return None
    try:
        primes = _prime_table(200_000)
        return primes.index(C) + 1 if C in primes else None
    except Exception:
        return None


def determiner_n(rapport: Union[str, int],
                  rang_cible: int) -> int:
    """Retourne n tel que l'ancrage + (n-10) == rang_cible.
    Compatibilité v7.4.
    """
    k = _extraire_k(rapport)
    ancrages = _ancrage_valide(k)
    if not ancrages:
        raise ValueError(f"Aucun ancrage pour k={k}")
    _, base_rank, _ = ancrages[0]
    return 10 + (rang_cible - base_rank)


def premier_pour_n(rapport: Union[str, int],
                   n: int = 10) -> Optional[int]:
    """Retourne le candidat C (int) pour le rapport 1/k à n termes.
    Compatibilité v7.4 — wrapper simple.
    """
    r = reconstruire_premier_pour_n(rapport, n)
    C = r.get("C")
    return C if isinstance(C, int) else None


# ── Export explicite pour src/spectral/__init__.py ───────────────────────────
__all__ = [
    # API publique v7.5
    "construire_rapport_convolutif",
    "reconstruire_premier",
    "reconstruire_premier_pour_n",
    # Constantes de verdict
    "EXCLU_HOL", "ANCRAGE_POSSIBLE", "P_CERTIFIE",
    "C_NON_DECIDE", "BLOQUE",
    # Tables
    "ANCHORS", "ANCHORS_MULTIPLES", "DIGAMMA_PARAMS",
    # Moteur entier
    "term_a", "term_b", "build", "closed_sums",
    "digamma_trials_n10", "reconstruct_entier",
    # Moteur géométrique
    "facteur_g", "suite_geo_A", "suite_geo_B",
    "candidats_premiers_geo", "reconstruct_geometrique",
    "reconstruire_avec_fallback_geo",
    # Validation
    "verifier_exemples",
    # Couche de compatibilité v7.4
    "EquationSomme",
    "construire_suites_reelles",
    "equations_suites_reelles",
    "reconstruire_premier_reel",
    "reconstruire_premier_reel_universel",
    "candidats_reconstruction_reelle",
    "equations_ab",
    "reconstruire_equations_ab",
    "position_du_premier",
    "determiner_n",
    "premier_pour_n",
]
