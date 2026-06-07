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
