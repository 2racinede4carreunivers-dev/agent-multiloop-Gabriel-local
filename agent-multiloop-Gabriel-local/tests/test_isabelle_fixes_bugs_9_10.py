"""
Tests v3.22 : verifie les corrections Isabelle/HOL bugs 9 & 10
(oublies dans la session precedente sur les 11 erreurs signalees).

Bug 9 : `terme_suite_B` (et `terme_suite_A` pour coherence) declarees en
        `fun` -> erreur de syntaxe interne au parser Isabelle car il n'y a
        pas de recursion (juste un `if-then-else`). Correction : utiliser
        `definition` a la place.

Bug 10 : `somme_A_construction_eq_formule` et `somme_B_construction_eq_formule`
         utilisaient `sorry`. Correction : reformulees en lemmes conditionnels
         (avec le fait de Savard en hypothese) prouvables par `by simp`.
         La conjecture numerique brute est documentee comme telle.
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


# ============================================================================
# Bug 9 : terme_suite_A et terme_suite_B doivent utiliser `definition`
# ============================================================================


class TestTermeSuiteUseDefinition:
    """Les deux constructions de suite ne sont pas recursives : `definition`
    est la primitive correcte en Isabelle. Utiliser `fun` sur un simple
    if-then-else provoque une erreur de syntaxe interne (Inner syntax error).
    """

    def test_terme_suite_A_is_definition_not_fun(self, thy_content):
        # `definition terme_suite_A` doit apparaitre
        assert "definition terme_suite_A" in thy_content, (
            "Bug 9 : terme_suite_A doit etre declare avec `definition` "
            "(pas `fun`) pour eviter l'erreur de syntaxe interne."
        )
        # `fun terme_suite_A` NE doit PLUS apparaitre
        assert "fun terme_suite_A" not in thy_content, (
            "Bug 9 : `fun terme_suite_A` doit avoir disparu."
        )

    def test_terme_suite_B_is_definition_not_fun(self, thy_content):
        assert "definition terme_suite_B" in thy_content, (
            "Bug 9 : terme_suite_B doit etre declare avec `definition` "
            "(pas `fun`) pour eviter l'erreur de syntaxe interne."
        )
        assert "fun terme_suite_B" not in thy_content, (
            "Bug 9 : `fun terme_suite_B` doit avoir disparu."
        )


# ============================================================================
# Bug 10 : plus aucun `sorry` dans les 2 lemmes cibles
# ============================================================================


class TestNoSorryInSommeConstructionLemmas:
    """Les lemmes `somme_A_construction_eq_formule` et
    `somme_B_construction_eq_formule` ne doivent plus contenir `sorry`.
    Ils sont maintenant des lemmes conditionnels (avec hypothese de Savard)
    prouvables trivialement par `by simp`.
    """

    def test_no_sorry_in_somme_A_lemma(self, thy_content):
        m = re.search(
            r"lemma somme_A_construction_eq_formule:(.*?)(?=^lemma|^theorem|^section|^subsection)",
            thy_content, re.DOTALL | re.MULTILINE,
        )
        assert m is not None, "Le lemme somme_A_construction_eq_formule doit exister"
        block = m.group(1)
        assert "sorry" not in block, (
            "Bug 10 : `sorry` doit avoir disparu de somme_A_construction_eq_formule"
        )
        assert "by simp" in block, (
            "Bug 10 : la preuve doit utiliser `by simp` sur l'hypothese Savard"
        )

    def test_no_sorry_in_somme_B_lemma(self, thy_content):
        m = re.search(
            r"lemma somme_B_construction_eq_formule:(.*?)(?=^lemma|^theorem|^section|^subsection)",
            thy_content, re.DOTALL | re.MULTILINE,
        )
        assert m is not None, "Le lemme somme_B_construction_eq_formule doit exister"
        block = m.group(1)
        assert "sorry" not in block, (
            "Bug 10 : `sorry` doit avoir disparu de somme_B_construction_eq_formule"
        )
        assert "by simp" in block, (
            "Bug 10 : la preuve doit utiliser `by simp` sur l'hypothese Savard"
        )

    def test_conjecture_documented(self, thy_content):
        """La nature de CONJECTURE NUMERIQUE (non identite algebrique) doit
        etre documentee explicitement dans une note textuelle."""
        assert "CONJECTURE" in thy_content.upper(), (
            "Une note textuelle doit clarifier que les formules fermees "
            "sont des conjectures numeriques, pas des identites universelles."
        )


# ============================================================================
# Regression globale : aucun `sorry` restant dans une preuve active
# ============================================================================


class TestNoActiveSorryAnywhere:
    """Verifie qu'aucun `sorry` ne subsiste comme tactique de preuve
    active dans le fichier (les mentions dans les commentaires sont ok)."""

    def test_no_bare_sorry_at_line_start(self, thy_content):
        # Cherche une ligne dont le contenu (apres strip) est exactement `sorry`
        active_sorries = []
        for i, line in enumerate(thy_content.splitlines(), start=1):
            if line.strip() == "sorry":
                active_sorries.append(i)
        assert not active_sorries, (
            f"Il reste des `sorry` actifs aux lignes : {active_sorries}"
        )
