"""
Tests des 3 questions critiques de Gabriel.

Q1. Reconstruction du P-ieme nombre premier
Q2. Rapport spectral (4 configurations)
Q3. Ecart entre deux premiers (3 cas)
"""
from fractions import Fraction

import pytest

from src.spectral import (
    SA, SB,
    compute_gap,
    compute_spectral_ratio,
    detect_configuration,
    detect_gap_kind,
    reconstruct_pth_prime_full,
    verify_prime_equation,
)
from src.core.types import AsymmetryKind, GapKind


# =============================================================
# Q1 - Reconstruction du P-ieme premier
# =============================================================

@pytest.mark.parametrize("n,p,SA_exp,SB_exp,dgm_exp", [
    (10, 29, 1662, 3262, 1406),
    (11, 31, 3326, 6590, 4606),
    (12, 37, 6654, 13246, 10878),
    (13, 41, 13310, 26558, 23934),
])
def test_reconstruction_modele_1_2(n, p, SA_exp, SB_exp, dgm_exp):
    r = verify_prime_equation(n, p, "1/2")
    assert r["SA"] == Fraction(SA_exp)
    assert r["SB"] == Fraction(SB_exp)
    assert r["digamma_calc"] == Fraction(dgm_exp)
    assert r["reconstructed_p"] == Fraction(p)
    assert r["equation_holds"] is True


def test_reconstruction_explicative_29():
    r = reconstruct_pth_prime_full(n=10, p=29, model="1/2")
    assert r["equation_holds"]
    assert "P = 29" in r["explanation"]
    assert "SA(n=10)   = 1662" in r["explanation"]


# =============================================================
# Q2 - Rapport spectral (4 configurations)
# =============================================================

def test_ratio_symmetric_1x1_modele_1_2():
    r = compute_spectral_ratio([3], [7], "1/2")
    assert r["configuration"] == AsymmetryKind.SYM_1x1.value
    assert r["ratio"] == Fraction(1, 2)
    assert r["matches_expected"]


def test_ratio_symmetric_nxn_modele_1_2():
    # n*n symetrique : meme nb d'indices des deux cotes
    r = compute_spectral_ratio([2, 5, 8], [3, 6, 9], "1/2")
    assert r["configuration"] == AsymmetryKind.SYM_NxN.value


def test_ratio_asymmetric_ordered_modele_1_2():
    # asym ordonnee : len(B) = len(A)+1, croissant, last(A) < hd(B)
    r = compute_spectral_ratio([1, 2, 3], [4, 5, 6, 7], "1/2")
    assert r["configuration"] == AsymmetryKind.ASYM_ORDERED.value


def test_ratio_asymmetric_chaotic_modele_1_2():
    # asym chaotique : longueurs differentes ET pas en config ordonnee
    r = compute_spectral_ratio([5, 1, 10], [3, 7], "1/2")
    assert r["configuration"] == AsymmetryKind.ASYM_CHAOTIC.value


def test_ratio_modele_1_3_egal_1_sur_3():
    r = compute_spectral_ratio([3], [7], "1/3")
    assert r["ratio"] == Fraction(1, 3)


def test_ratio_modele_1_4_egal_1_sur_4():
    r = compute_spectral_ratio([2], [6], "1/4")
    assert r["ratio"] == Fraction(1, 4)


# =============================================================
# Q3 - Ecart entre deux premiers (3 cas)
# =============================================================

def test_gap_positive_227_173_1_3():
    """Exemple corpus : gap entre 227 et 173, modele 1/3 = -53."""
    r = compute_gap(
        p_high=227, p_low=173,
        A_next=Fraction(96, 9),
        B_high=Fraction(238746),
        D_high=Fraction(73263),
        D_low=Fraction(-1141518, 9),
        model="1/3",
    )
    assert r["kind"] == GapKind.POS_POS.value
    assert r["gap"] == Fraction(-53)


def test_gap_positive_947_881_1_4():
    """Exemple corpus : gap entre 947 et 881, modele 1/4 = -65."""
    r = compute_gap(
        p_high=947, p_low=881,
        A_next=Fraction(75, 4),
        B_high=Fraction(5260628),
        D_high=Fraction(1381716),
        D_low=Fraction(-14450613, 4),
        model="1/4",
    )
    assert r["kind"] == GapKind.POS_POS.value
    assert r["gap"] == Fraction(-65)


def test_detect_gap_kind_pos_pos():
    assert detect_gap_kind(227, 173) == GapKind.POS_POS


def test_detect_gap_kind_neg_neg():
    assert detect_gap_kind(-19, -5) == GapKind.NEG_NEG


def test_detect_gap_kind_neg_pos():
    assert detect_gap_kind(-31, 17) == GapKind.NEG_POS


def test_gap_negative_neg_neg():
    """Cas (-,-) : -19 et -5. Resultat attendu corpus = -13."""
    from src.spectral.gaps import gap_negative
    r = gap_negative(
        A_next=Fraction(-10110, 5120),
        B_high=Fraction(-20860, 320),
        D_high=Fraction(81540, 320),
        D_low=Fraction(5888130, 5120),
        factor=64,
    )
    assert r == Fraction(-13)


def test_gap_mixed_neg_pos():
    """Cas (-,+) : -31 et 17. Resultat attendu corpus = -47."""
    from src.spectral.gaps import gap_mixed
    r = gap_mixed(
        A_next=Fraction(-40895, 20480),
        B_high=Fraction(350),
        D_high=Fraction(-738),
        D_low=Fraction(39280705, 20480),
        factor=64,
    )
    assert r == Fraction(-47)
