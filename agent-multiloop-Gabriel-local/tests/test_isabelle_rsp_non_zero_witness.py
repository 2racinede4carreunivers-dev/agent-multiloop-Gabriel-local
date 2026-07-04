"""
Tests v3.22 : verifie que les 4 theoremes RsP (RsP_un_demi_general,
RsP_un_tiers_constant, RsP_un_quart_constant, RsP_k_egale_un_sur_k_pos)
ont bien le TEMOIN DE NON-NULLITE explicite pour `base^n1 - base^n2`,
signale par Philippe le 2026-02 (3 erreurs de compilation Isabelle).

Cause : la tactique `by (simp add: field_simps)` ne peut pas simplifier
`(x * D) / (y * D) = x / y` sans savoir que `D != 0`. Il fallait
fournir explicitement le temoin via `power_strict_increasing` et une
disjonction sur `n1 < n2` vs `n2 < n1`.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="module")
def thy_content() -> str:
    thy = ROOT / "theories" / "methode_spectral.thy"
    return thy.read_text(encoding="utf-8")


class TestRsPTheoremsHaveNonZeroWitness:
    """Chaque theoreme RsP doit contenir un `have hne_pow_X` prouvant
    que `X^n1 - X^n2 != 0` (via power_strict_increasing)."""

    @pytest.mark.parametrize("theorem_name,base", [
        ("RsP_un_demi_general",       "2"),
        ("RsP_un_tiers_constant",     "3"),
        ("RsP_un_quart_constant",     "4"),
    ])
    def test_witness_present_for_single_base_theorem(
            self, thy_content, theorem_name, base):
        # Extraire le bloc du theoreme
        m = re.search(
            rf"(lemma|theorem) {theorem_name}:(.*?)qed",
            thy_content, re.DOTALL,
        )
        assert m is not None, f"Le theoreme {theorem_name} doit exister"
        block = m.group(2)

        # Le temoin doit contenir "hne_pow_{base}"
        assert f"hne_pow_{base}" in block, (
            f"{theorem_name} doit contenir un temoin `hne_pow_{base}` "
            f"prouvant que ({base}::real)^n1 - {base}^n2 != 0"
        )
        # Il doit utiliser power_strict_increasing
        assert "power_strict_increasing" in block, (
            f"{theorem_name} doit invoquer `power_strict_increasing` "
            f"pour prouver la stricte monotonie de {base}^_"
        )

    def test_RsP_k_egale_un_sur_k_pos_has_all_3_witnesses(self, thy_content):
        """Le theoreme parametrique doit contenir 3 temoins (k=2, k=3, k=4)."""
        m = re.search(
            r"theorem RsP_k_egale_un_sur_k_pos:(.*?)qed\nqed",
            thy_content, re.DOTALL,
        )
        assert m is not None
        block = m.group(1)
        for base in ("2", "3", "4"):
            assert f"hne_pow_{base}" in block, (
                f"RsP_k_egale_un_sur_k_pos doit avoir un temoin hne_pow_{base}"
            )
        # power_strict_increasing doit apparaitre au moins 6 fois
        # (2 fois par cas x 3 cas)
        n_uses = block.count("power_strict_increasing")
        assert n_uses >= 6, (
            f"RsP_k_egale_un_sur_k_pos doit invoquer power_strict_increasing "
            f"au moins 6 fois (2/cas x 3 cas), trouve : {n_uses}"
        )


class TestNoBareFieldSimpsInRsPProofs:
    """Regression : plus aucune ligne `using assms by (simp add: field_simps)`
    dans les proofs RsP (elle echouait sans le temoin de non-nullite)."""

    @pytest.mark.parametrize("theorem_name", [
        "RsP_un_demi_general",
        "RsP_un_tiers_constant",
        "RsP_un_quart_constant",
    ])
    def test_no_bare_assms_field_simps(self, thy_content, theorem_name):
        m = re.search(
            rf"(lemma|theorem) {theorem_name}:(.*?)qed",
            thy_content, re.DOTALL,
        )
        assert m is not None
        block = m.group(2)
        # L'ancien pattern buggue "using assms by (simp add: field_simps)"
        # doit avoir disparu — remplace par "using hne_pow_X by (simp ...)"
        assert "using assms by (simp add: field_simps)" not in block, (
            f"{theorem_name} contient encore le pattern buggue "
            f"`using assms by (simp add: field_simps)` — il doit etre "
            f"remplace par `using hne_pow_X by (simp add: field_simps)`."
        )
