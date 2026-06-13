"""Tests du 7e moteur : Adaptateur Cognitif Spectral."""
from __future__ import annotations

import pytest

from src.engines.cognitive_alignment import AdaptateurCognitifSpectral


def test_traduction_SA_vers_wolfram():
    a = AdaptateurCognitifSpectral()
    req = a.aligner_requete_vers_wolfram("SA(n) = 1662")
    assert "(3.25/2) * 2^n - 2" in req


def test_traduction_SB_vers_wolfram():
    a = AdaptateurCognitifSpectral()
    req = a.aligner_requete_vers_wolfram("verifier SB(n)")
    assert "(6.5/2) * 2^n - 66" in req


def test_constante_Sr2_remplacee():
    a = AdaptateurCognitifSpectral()
    req = a.aligner_requete_vers_wolfram("evaluer ratio Sr2 dans la suite")
    assert "1.5" in req
    assert "Sr2" not in req.replace("Sr2", "", 0).split()  # remplace effectif


def test_formaliser_isabelle_genere_bloc_valide():
    a = AdaptateurCognitifSpectral()
    block = a.formaliser_isabelle(
        concept_nom="tangence_spectrale",
        resultat_numerique="1.5",
        contexte_theorie="rapport spectral 1/2 valide pour SA et SB",
    )
    assert "theory adaptateur_tangence_spectrale" in block
    assert "imports Complex_Main methode_spectral" in block
    assert "definition ratio_Sr2" in block
    assert "lemma ratio_Sr2_value" in block
    assert "end" in block


def test_traduction_modele_1_4():
    a = AdaptateurCognitifSpectral()
    req = a.aligner_requete_vers_wolfram("calculer A_1_4(n)")
    assert "((241/16)/12) * 4^n" in req


@pytest.mark.asyncio
async def test_formaliser_et_ecrire_fichier(tmp_path):
    """formaliser_et_ecrire_fichier doit creer un .thy valide dans theories/generated/."""
    a = AdaptateurCognitifSpectral()
    info = await a.formaliser_et_ecrire_fichier(
        concept_nom="tangence_Sr2_test",
        theories_dir=str(tmp_path),
        contexte_theorie="rapport 1/2",
    )
    from pathlib import Path
    p = Path(info["file_path"])
    assert p.exists()
    content = p.read_text(encoding="utf-8")
    assert "theory adaptateur_tangence_Sr2_test" in content
    assert "imports Complex_Main methode_spectral" in content
    assert "definition ratio_Sr2" in content
    assert info["theory_name"] == "adaptateur_tangence_Sr2_test"
