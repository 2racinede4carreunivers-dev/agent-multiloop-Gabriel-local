"""
Tests v3.22 : verifie l'existence et la structure du portage Lean 4 de
`theories/MethodeSpectrale.lean` (portage 1:1 depuis methode_spectral.thy).

Ces tests sont STRUCTURELS uniquement : ils verifient que toutes les
definitions et theoremes cles du fichier Isabelle sont bien presents
dans la version Lean 4. Ils N'EXECUTENT PAS Lean (non installe dans
l'environnement Docker de Gabriel — la compilation doit etre faite
cote utilisateur avec `lake build` + Mathlib).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="module")
def lean_content() -> str:
    lean = ROOT / "theories" / "MethodeSpectrale.lean"
    assert lean.exists(), (
        "Le fichier Lean 4 theories/MethodeSpectrale.lean doit exister"
    )
    return lean.read_text(encoding="utf-8")


# ============================================================================
# Structure Lean 4 : imports Mathlib et namespace
# ============================================================================


class TestLeanFileStructure:
    def test_imports_mathlib(self, lean_content):
        assert "import Mathlib.Data.Real.Basic" in lean_content
        assert "import Mathlib.Data.Nat.Prime.Basic" in lean_content

    def test_namespace_declared(self, lean_content):
        assert "namespace MethodeSpectrale" in lean_content
        assert "end MethodeSpectrale" in lean_content


# ============================================================================
# Section 1 & 2 : SA, SB, RsP
# ============================================================================


class TestSuitesAndRsP:
    def test_SA_definition(self, lean_content):
        assert "def SA (n : ℕ) : ℝ :=" in lean_content

    def test_SB_definition(self, lean_content):
        assert "def SB (n : ℕ) : ℝ :=" in lean_content

    def test_RsP_definition(self, lean_content):
        assert "def RsP (n1 n2 : ℕ) : ℝ :=" in lean_content

    def test_RsP_un_demi_theorem(self, lean_content):
        assert "theorem RsP_un_demi_general" in lean_content


# ============================================================================
# Section 3 : digamma_calc et prime_equation
# ============================================================================


class TestDigammaAndPrimeEquation:
    def test_digamma_calc_defined(self, lean_content):
        assert "def digamma_calc (n : ℕ) (p : ℕ) : ℝ :=" in lean_content

    def test_prime_equation_defined(self, lean_content):
        assert "def prime_equation (n : ℕ) (p : ℕ) : ℝ :=" in lean_content

    def test_prime_equation_identity(self, lean_content):
        assert "lemma prime_equation_identity" in lean_content


# ============================================================================
# Section 5 : Exemples numeriques 29, 31, 37, 41
# ============================================================================


class TestNumericalExamples:
    @pytest.mark.parametrize("name,value", [
        ("n29", "10"),
        ("n31", "11"),
        ("n37", "12"),
        ("n41", "13"),
    ])
    def test_prime_positions_defined(self, lean_content, name, value):
        assert f"def {name} : ℕ := {value}" in lean_content

    @pytest.mark.parametrize("lemma_name,expected", [
        ("SA_10", "1662"),
        ("SB_10", "3262"),
        ("SA_11", "3326"),
        ("SB_11", "6590"),
        ("SA_12", "6654"),
        ("SB_12", "13246"),
        ("SA_13", "13310"),
        ("SB_13", "26558"),
    ])
    def test_numerical_lemmas_present(self, lean_content, lemma_name, expected):
        assert f"lemma {lemma_name}" in lean_content
        assert expected in lean_content


# ============================================================================
# Section 7 : prime_i (i-ieme premier via choix classique)
# ============================================================================


class TestPrimeI:
    def test_position_axiom(self, lean_content):
        assert "axiom position" in lean_content

    def test_prime_position_exists_axiom(self, lean_content):
        assert "axiom prime_position_exists" in lean_content

    def test_prime_i_definition(self, lean_content):
        assert "def prime_i (i : ℕ) : ℕ" in lean_content
        assert "Classical.choose" in lean_content

    def test_prime_i_is_prime(self, lean_content):
        assert "lemma prime_i_is_prime" in lean_content

    def test_prime_i_position(self, lean_content):
        assert "lemma prime_i_position" in lean_content


# ============================================================================
# Section 8-11 : LES 3 PILIERS DE LA METHODE SPECTRALE
# ============================================================================


class TestThreePillars:
    """Verifie que les 3 piliers sont bien formalises en Lean."""

    def test_pilier_1_composite_not_prime_i(self, lean_content):
        """Pilier 1 - Aucun compose n'est un prime_i."""
        assert "theorem composite_not_prime_i" in lean_content

    def test_pilier_2_composite_no_reconstruction(self, lean_content):
        """Pilier 2 - Aucun compose ne peut etre reconstruit."""
        assert "theorem composite_no_reconstruction_position" in lean_content

    def test_pilier_3_composite_pair_no_rsp(self, lean_content):
        """Pilier 3 - Aucun couple de composes ne peut occuper des positions RsP."""
        assert "theorem composite_pair_no_rsp_positions" in lean_content
        assert "theorem composite_single_no_rsp_position" in lean_content

    def test_synthese_documented(self, lean_content):
        """La synthese des 3 piliers doit etre documentee."""
        assert "PILIER 1" in lean_content
        assert "PILIER 2" in lean_content
        assert "PILIER 3" in lean_content
        assert "CONSEQUENCE DEFINITIVE" in lean_content


# ============================================================================
# Section 9-10 : 6 composes canoniques (4, 9, 15, 51, 91, 121)
# ============================================================================


class TestSixCompositesCanonical:
    @pytest.mark.parametrize("value", [4, 9, 15, 51, 91, 121])
    def test_composite_not_prime_lemma(self, lean_content, value):
        assert f"lemma composite_{value}_not_prime" in lean_content

    @pytest.mark.parametrize("value", [4, 9, 15, 51, 91, 121])
    def test_no_spectral_position(self, lean_content, value):
        assert f"theorem no_spectral_position_for_{value}" in lean_content

    @pytest.mark.parametrize("value", [4, 9, 15, 51, 91, 121])
    def test_no_reconstruction(self, lean_content, value):
        assert f"theorem no_reconstruction_for_{value}" in lean_content


# ============================================================================
# Section XI : Regles de construction (bugs 9 & 10 des .thy)
# ============================================================================


class TestSectionXI:
    """Verifie que la Section XI est correctement portee, avec les
    corrections des bugs 9 (fun -> def) et 10 (sorry -> conditionnels)."""

    def test_terme_progression_simple(self, lean_content):
        assert "def terme_progression_simple" in lean_content

    def test_avant_dernier(self, lean_content):
        assert "def avant_dernier" in lean_content

    def test_dernier_terme(self, lean_content):
        assert "def dernier_terme" in lean_content

    def test_terme_suite_A_uses_def(self, lean_content):
        """Bug 9 : terme_suite_A doit etre `def` (pas de recursion)."""
        assert "def terme_suite_A" in lean_content

    def test_terme_suite_B_uses_def(self, lean_content):
        """Bug 9 : terme_suite_B doit etre `def` (pas de recursion)."""
        assert "def terme_suite_B" in lean_content

    def test_somme_suite_defined(self, lean_content):
        assert "def somme_suite" in lean_content
        assert "Finset.Icc 1 n" in lean_content

    def test_somme_A_close(self, lean_content):
        assert "def somme_A_close" in lean_content

    def test_somme_B_close(self, lean_content):
        assert "def somme_B_close" in lean_content

    def test_rapport_spectral_AB(self, lean_content):
        assert "def rapport_spectral_AB" in lean_content

    def test_no_sorry_in_lean_file(self, lean_content):
        """Bug 10 : aucun `sorry` actif dans le fichier Lean."""
        for i, line in enumerate(lean_content.splitlines(), start=1):
            stripped = line.strip()
            # `sorry` isole (comme tactique complete de preuve)
            assert stripped != "sorry", (
                f"Ligne {i} : `sorry` actif detecte (bug 10 non corrige)"
            )

    def test_somme_A_lemma_conditional(self, lean_content):
        """Bug 10 : somme_A_construction_eq_formule enonce conditionnellement."""
        assert "lemma somme_A_construction_eq_formule" in lean_content
        assert "savard_A :" in lean_content

    def test_somme_B_lemma_conditional(self, lean_content):
        """Bug 10 : somme_B_construction_eq_formule enonce conditionnellement."""
        assert "lemma somme_B_construction_eq_formule" in lean_content
        assert "savard_B :" in lean_content

    def test_conjecture_documented(self, lean_content):
        """Les formules fermees Savard sont documentees comme CONJECTURES."""
        assert "CONJECTURE" in lean_content.upper()
