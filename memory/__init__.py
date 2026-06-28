"""
Memory system for Gabriel v7
"""

from .memoire_conceptuelle import (
    rechercher_concept_par_theme,
    obtenir_contexte_regime,
    generer_prompt_conceptuel,
    AXIOMES_FONDAMENTAUX,
    DEFINITIONS_GEOMETRIQUES,
    PROPRIETES_ETABLIES,
    CONCEPTS_CLES
)

from .memoire_technique import (
    PATTERNS_PREUVE_REUSSIS,
    LEMMES_VALIDES,
    ANTIPATTERNS_PREUVE,
    trouver_pattern,
    trouver_lemme_pertinent,
    eviter_antipattern,
    PatternPreuve
)

from .gestionnaire_erreurs import (
    CacheErreursPersistent,
    ErreurPreuve,
    TypeErreur,
    StrategieEvitementErreurs,
    AnalyseurPatternErreurs,
    ERREURS_PERSISTEES
)

__all__ = [
    # Conceptual
    'rechercher_concept_par_theme',
    'obtenir_contexte_regime',
    'generer_prompt_conceptuel',
    'AXIOMES_FONDAMENTAUX',
    'DEFINITIONS_GEOMETRIQUES',
    'PROPRIETES_ETABLIES',
    'CONCEPTS_CLES',
    # Technical
    'PATTERNS_PREUVE_REUSSIS',
    'LEMMES_VALIDES',
    'ANTIPATTERNS_PREUVE',
    'trouver_pattern',
    'trouver_lemme_pertinent',
    'eviter_antipattern',
    'PatternPreuve',
    # Errors
    'CacheErreursPersistent',
    'ErreurPreuve',
    'TypeErreur',
    'StrategieEvitementErreurs',
    'AnalyseurPatternErreurs',
    'ERREURS_PERSISTEES',
]
