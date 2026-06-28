"""
Rapport spectral : 4 configurations.

1. Symetrique 1x1 (P1 * P2)         : (A(n1) - A(n2)) / (B(n1) - B(n2))
2. Symetrique n*n (Pn * Pn)         : (sum A(indices_A)) / (sum B(indices_B))
3. Asymetrique ordonnee             : longueur(B) = longueur(A) + 1, indices croissants
4. Asymetrique chaotique            : longueur differente, pas d'ordre impose

Retourne theoriquement 1/k ou k est le modele (2, 3, 4).
"""
from __future__ import annotations

from fractions import Fraction

from .suites import get_suite_functions
from ..core.types import AsymmetryKind


# =============================================================
# 1. Rapport symetrique 1x1
# =============================================================

def ratio_1x1(n1: int, n2: int, model: str = "1/2") -> Fraction:
    """RsP(n1, n2) = (A(n1) - A(n2)) / (B(n1) - B(n2))"""
    fns = get_suite_functions(model)
    return (fns["A"](n1) - fns["A"](n2)) / (fns["B"](n1) - fns["B"](n2))


# =============================================================
# 2. Rapport symetrique n*n (sommes de blocs)
# =============================================================

def ratio_nxn(A_indices: list[int], B_indices: list[int], model: str = "1/2") -> Fraction:
    """RsP_nn = sum_A(indices_A) / sum_B(indices_B)"""
    fns = get_suite_functions(model)
    sum_a = fns["sumA"](A_indices)
    sum_b = fns["sumB"](B_indices)
    if sum_b == 0:
        raise ValueError("Somme des B nulle : division impossible.")
    return sum_a / sum_b


# =============================================================
# 3. Asymetrique ordonnee
# =============================================================

def is_asymmetric_ordered(A_indices: list[int], B_indices: list[int]) -> bool:
    """
    A et B strictement croissants, indices > 0,
    A et B non vides, last(A) < hd(B), len(B) = len(A) + 1.
    """
    if not A_indices or not B_indices:
        return False
    if any(i <= 0 for i in A_indices + B_indices):
        return False
    if A_indices != sorted(set(A_indices)) or B_indices != sorted(set(B_indices)):
        return False
    if A_indices[-1] >= B_indices[0]:
        return False
    return len(B_indices) == len(A_indices) + 1


def ratio_asymmetric_ordered(A_indices: list[int], B_indices: list[int], model: str = "1/2") -> Fraction:
    """Rapport asymetrique ordonne (utilise sommes de blocs A et B)."""
    if not is_asymmetric_ordered(A_indices, B_indices):
        raise ValueError(
            "Configuration non asymetrique ordonnee. Exige : indices > 0, strictement croissants, "
            "last(A) < hd(B), len(B) = len(A) + 1."
        )
    return ratio_nxn(A_indices, B_indices, model)


# =============================================================
# 4. Asymetrique chaotique
# =============================================================

def is_asymmetric_chaotic(A_indices: list[int], B_indices: list[int]) -> bool:
    """
    Longueurs differentes ET pas en configuration ordonnee.
    Tous les indices > 0.
    """
    if not A_indices or not B_indices:
        return False
    if any(i <= 0 for i in A_indices + B_indices):
        return False
    if len(A_indices) == len(B_indices):
        return False
    return not is_asymmetric_ordered(A_indices, B_indices)


def ratio_asymmetric_chaotic(A_indices: list[int], B_indices: list[int], model: str = "1/2") -> Fraction:
    """Rapport asymetrique chaotique (utilise sommes de blocs A et B)."""
    if not is_asymmetric_chaotic(A_indices, B_indices):
        raise ValueError(
            "Configuration non asymetrique chaotique. Exige : longueurs differentes et configuration desordonnee."
        )
    return ratio_nxn(A_indices, B_indices, model)


# =============================================================
# 5. Chaos-Savard (convention alternee Philippe Thomas Savard)
# =============================================================
#
# Convention specifique observee par Philippe Thomas Savard pour la
# convergence de l'asymetrie chaotique vers 1/2 :
#
#   alt(X) = X[0] - X[1] - X[2] - ... - X[n]
#          = X[0] - sum(X[1:])
#
#   RsP_chaos_savard(A, B) = (alt_SA(A) - alt_SA(B)) / (alt_SB(A) - alt_SB(B))
#
# Construction canonique des blocs A et B pour la courbe k=1..K :
#   A = [p_{k+1}, p_{k+2}, ..., p_{2k}]                  (k primes intermediaires)
#   B = [p_{2k+1}, p_1, p_2, ..., p_k]                   (le suivant + k initiaux)
#   |A| = k, |B| = k+1
#
# La courbe montre une divergence (-0.072 a k=1) qui converge tres vite
# vers 1/2 (0.5015 a k=5, ~1/2 pour k >= 6).
# =============================================================


def _alternating_diff(values: list[Fraction]) -> Fraction:
    """alt([x0, x1, x2, ...]) = x0 - x1 - x2 - ... - xn = x0 - sum(x[1:])."""
    if not values:
        raise ValueError("Liste vide pour alternating_diff")
    return values[0] - sum(values[1:], Fraction(0))


def ratio_chaos_savard(
    A_indices: list[int],
    B_indices: list[int],
    model: str = "1/2",
) -> Fraction:
    """Rapport spectral selon la convention alternee chaos-Savard.

    RsP = (alt_SA(A) - alt_SA(B)) / (alt_SB(A) - alt_SB(B))
    avec alt(X) = X[0] - X[1] - ... - X[n].

    Necessite |A| >= 1 et |B| >= 1.
    Leve ValueError si le denominateur est nul.
    """
    if not A_indices or not B_indices:
        raise ValueError("A et B doivent etre non vides.")
    fns = get_suite_functions(model)
    alt_sa_A = _alternating_diff([Fraction(fns["A"](i)) for i in A_indices])
    alt_sa_B = _alternating_diff([Fraction(fns["A"](i)) for i in B_indices])
    alt_sb_A = _alternating_diff([Fraction(fns["B"](i)) for i in A_indices])
    alt_sb_B = _alternating_diff([Fraction(fns["B"](i)) for i in B_indices])
    num = alt_sa_A - alt_sa_B
    den = alt_sb_A - alt_sb_B
    if den == 0:
        raise ValueError(
            "Denominateur alterne nul (alt_SB(A) - alt_SB(B) = 0) : "
            "division impossible."
        )
    return num / den


def build_chaos_savard_blocks(
    k: int,
    primes_positions: list[int] | None = None,
) -> tuple[list[int], list[int]]:
    """Construit les blocs A et B canoniques pour la courbe chaos-Savard a l'index k.

    Convention Philippe Thomas Savard :
      A = [p_{k+1}, ..., p_{2k}]      (positions k+1 .. 2k)
      B = [p_{2k+1}, p_1, ..., p_k]   (position 2k+1 + positions 1..k)

    Args:
        k: index de la courbe (k >= 1). Le triplet (|A|, |B|) = (k, k+1).
        primes_positions: liste optionnelle de positions a utiliser. Si None,
                          retourne directement les positions [k+1..2k] et
                          [2k+1, 1, 2, .., k].

    Returns:
        (A_positions, B_positions) en termes de position 1-indexee.
    """
    if k < 1:
        raise ValueError(f"k doit etre >= 1, recu {k}")
    A = list(range(k + 1, 2 * k + 1))           # positions k+1 .. 2k
    B = [2 * k + 1] + list(range(1, k + 1))      # position 2k+1 + positions 1..k
    return A, B


# =============================================================
# Dispatcher unifie
# =============================================================

def detect_configuration(A_indices: list[int], B_indices: list[int]) -> AsymmetryKind:
    """Detecte automatiquement la configuration d'apres les indices."""
    if len(A_indices) == 1 and len(B_indices) == 1:
        return AsymmetryKind.SYM_1x1
    if len(A_indices) == len(B_indices):
        return AsymmetryKind.SYM_NxN
    if is_asymmetric_ordered(A_indices, B_indices):
        return AsymmetryKind.ASYM_ORDERED
    return AsymmetryKind.ASYM_CHAOTIC


def compute_spectral_ratio(
    A_indices: list[int],
    B_indices: list[int],
    model: str = "1/2",
) -> dict:
    """
    Calcule le rapport spectral pour n'importe laquelle des 4 configurations.
    Retourne dict avec configuration detectee, rapport calcule, et valeur attendue.
    """
    config = detect_configuration(A_indices, B_indices)
    fns = get_suite_functions(model)

    if config == AsymmetryKind.SYM_1x1:
        ratio = ratio_1x1(A_indices[0], B_indices[0], model)
    elif config == AsymmetryKind.SYM_NxN:
        ratio = ratio_nxn(A_indices, B_indices, model)
    elif config == AsymmetryKind.ASYM_ORDERED:
        ratio = ratio_asymmetric_ordered(A_indices, B_indices, model)
    else:
        ratio = ratio_asymmetric_chaotic(A_indices, B_indices, model)

    # Valeur attendue : 1/k (k = denominateur du modele)
    k = int(model.split("/")[1])
    expected = Fraction(1, k)

    return {
        "model": model,
        "configuration": config.value,
        "A_indices": A_indices,
        "B_indices": B_indices,
        "sum_A": fns["sumA"](A_indices) if len(A_indices) > 1 else fns["A"](A_indices[0]),
        "sum_B": fns["sumB"](B_indices) if len(B_indices) > 1 else fns["B"](B_indices[0]),
        "ratio": ratio,
        "ratio_float": float(ratio),
        "expected": expected,
        "expected_float": float(expected),
        "matches_expected": ratio == expected,
    }
