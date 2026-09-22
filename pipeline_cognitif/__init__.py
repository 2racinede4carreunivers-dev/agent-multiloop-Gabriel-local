#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pipeline cognitif Gabriel — niveaux 1 et 2 du systeme convolutif spectral.

Reconstruction des nombres premiers a partir des rapports 1/k, conforme a la
Section XIV de `methode_spectral.thy` (constantes universelles, formes fermees,
regles Savard terme a terme, ancrages n=10, decalage de rang, validation
k=8 / n=34).

Usage (package) :
    from pipeline_cognitif import PipelineCognitifNiveaux, CalculateurNiveau1Entiers

Usage (validation de conformite a la Section XIV) :
    python -m pipeline_cognitif.validation_section_xiv

Dependance tierce unique : numpy (metaphore_geometrique).
"""

from .suites_geometriques_niveau2 import (
    ANCRAGES_XIV,
    CalculateurNiveau1Entiers,
    CalculateurNiveau2Geometrique,
    MethodeDigamma,
    MethodeDigammaGeometrique,
    PipelineNiveau2Geometrique,
    ResultatNiveau1Entiers,
    ResultatNiveau2Geometrique,
    construire_termes_savard,
    construire_termes_savard_geometrique,
    digamma_calcule,
    est_premier,
    nieme_premier,
    premier_cible,
    preuve_absurde_generique,
    rang_cible,
    valider_n,
)
from .reconstruction_premiers_1_sur_k import (
    Reconstructeur1Sur7,
    ResultatReconstruction1Sur7,
)
from .Suites_geometriques_AB import (
    PipelineSuitesGeometriques,
    ResultatSuiteGeo,
)
from .fallback_geometrique import (
    GestionnaireFallbackGeometrique,
    ResultatReconstruction,
    TypeApproche,
)
from .gabriel_geometric_wrapper_v74 import (
    GabrielGeometricResponseWrapper,
    PipelineCognitifNiveaux,
    enrichir_reponse_gabriel,
)

__version__ = "7.5"

__all__ = [
    # Niveau 1 (entiers) et Niveau 2 (geometrique)
    "ANCRAGES_XIV",
    "CalculateurNiveau1Entiers",
    "CalculateurNiveau2Geometrique",
    "MethodeDigamma",
    "MethodeDigammaGeometrique",
    "PipelineNiveau2Geometrique",
    "ResultatNiveau1Entiers",
    "ResultatNiveau2Geometrique",
    "construire_termes_savard",
    "construire_termes_savard_geometrique",
    "digamma_calcule",
    "est_premier",
    "nieme_premier",
    "premier_cible",
    "preuve_absurde_generique",
    "rang_cible",
    "valider_n",
    # Reconstruction 1/k (reference 1/7)
    "Reconstructeur1Sur7",
    "ResultatReconstruction1Sur7",
    # Suites A/B et fallback geometrique
    "PipelineSuitesGeometriques",
    "ResultatSuiteGeo",
    "GestionnaireFallbackGeometrique",
    "ResultatReconstruction",
    "TypeApproche",
    # Wrapper Gabriel
    "GabrielGeometricResponseWrapper",
    "PipelineCognitifNiveaux",
    "enrichir_reponse_gabriel",
]
