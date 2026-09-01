"""Tests des équations exactes A/B pour les rapports non-typiques."""
from __future__ import annotations

from fractions import Fraction

import pytest

from src.spectral.rapports_non_typiques import (
    equations_ab,
    reconstruire_equations_ab,
    suite_A,
    suite_B,
)


@pytest.mark.parametrize("k", [3, 4, 5, 6, 7, 11])
@pytest.mark.parametrize("n", [7, 10, 14])
def test_equations_universelles_reproduisent_les_sommes_par_blocs(k: int, n: int) -> None:
    equation_a, equation_b = equations_ab(f"1/{k}")

    assert equation_a.somme(n) == suite_A(k, n)
    assert equation_b.somme(n) == suite_B(k, n)


@pytest.mark.parametrize("k", [3, 5, 6, 11])
def test_reconstruction_deux_sommes_retrouve_equations_exactes(k: int) -> None:
    attendue_a, attendue_b = equations_ab(k)
    reconstruite_a, reconstruite_b = reconstruire_equations_ab(k, 10, 12)

    assert reconstruite_a == attendue_a
    assert reconstruite_b == attendue_b


def test_convolution_geometrique_propage_la_somme_sans_arrondi() -> None:
    equation_a, equation_b = equations_ab("1/5")

    assert equation_a.convoluer(equation_a.somme(10), 10, 14) == suite_A(5, 14)
    assert equation_b.convoluer(equation_b.somme(10), 10, 14) == suite_B(5, 14)
    assert isinstance(equation_b.somme(10), Fraction)


def test_rapport_typique_est_refuse_explicitement() -> None:
    with pytest.raises(ValueError, match="non-typique"):
        equations_ab("1/2")
