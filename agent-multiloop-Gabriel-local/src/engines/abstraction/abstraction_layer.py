"""
Moteur d'Abstraction (PROFOND).
Extrait les concepts spectraux d'une question en langage naturel.
"""
from __future__ import annotations

import logging
import re
from typing import Any

from ...core.types import CognitiveConcept, QuestionContext, SpectralModel


logger = logging.getLogger(__name__)


# Patterns lexicaux pour le corpus de Philippe Thomas Savard
SPECTRAL_PATTERNS: dict[str, list[str]] = {
    "rapport_spectral": [
        r"rapport\s+spectr",
        r"\bRsP\b",
        r"1\s*/\s*[234]",
    ],
    "digamma_calc": [
        r"digamma",
        r"\bdgm\b",
    ],
    "prime_equation": [
        r"prime[\s_]?equation",
        r"reconstr.*premier",
        r"P-?[èe]me\s+premier",
        r"p[-\s]?ieme\s+premier",
    ],
    "gap_equation": [
        r"\becart\b", r"\bgap\b", r"quantit[eé]\s+(?:de\s+)?(?:terme|nombre|entier)",
        r"distance\s+entre\s+(?:deux\s+)?premier",
    ],
    "suites_AB": [
        r"\bsuite[s]?\s+A\b", r"\bsuite[s]?\s+B\b",
        r"\bSA\b", r"\bSB\b",
    ],
    "asymetrie": [
        r"asym[ée]trique", r"chaotique", r"ordonn[ée]e",
    ],
    "plan_trifocal": [
        r"plan\s+trifocal", r"[ée]pipolaire", r"trifocal",
    ],
    "riemann": [
        r"riemann", r"hypoth[èe]se", r"z[êe]ta", r"\bRH\b",
    ],
    "suites_mixtes": [
        r"\(-\s*,\s*\+\)", r"mixt", r"n[ée]gatif",
    ],
}


# Detection du modele spectral
def _detect_model(text: str) -> SpectralModel | None:
    text_low = text.lower()
    if "1/2" in text or "un demi" in text_low or "1 sur 2" in text_low:
        return SpectralModel.RATIO_1_2
    if "1/3" in text or "un tiers" in text_low or "1 sur 3" in text_low:
        return SpectralModel.RATIO_1_3
    if "1/4" in text or "un quart" in text_low or "1 sur 4" in text_low:
        return SpectralModel.RATIO_1_4
    return None


def _detect_intent(text: str) -> str:
    """Categorise l'intention : reconstruction / ratio / gap / autre."""
    t = text.lower()
    if re.search(r"reconstr|p-?i[èe]me|p\s+i[èe]me|determine.*digamma", t):
        return "reconstruction"
    if re.search(r"rapport|ratio|asym[ée]trique|sym[ée]trique|chaotique", t):
        return "ratio"
    if re.search(r"\becart\b|\bgap\b|quantit[eé].*(?:terme|entier|nombre)", t):
        return "gap"
    if re.search(r"riemann|hypoth[èe]se|z[êe]ta", t):
        return "riemann_link"
    return "general"


class ConceptExtractor:
    """Extrait concepts mathematiques avec regex et signatures."""

    def extract(self, text: str) -> list[CognitiveConcept]:
        concepts: list[CognitiveConcept] = []
        for concept_name, patterns in SPECTRAL_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, text, re.IGNORECASE):
                    concepts.append(
                        CognitiveConcept(
                            name=concept_name,
                            category="spectral",
                            keywords=[pat],
                            confidence=0.9,
                        )
                    )
                    break
        return concepts


class AbstractionLayer:
    """Couche d'abstraction : transforme question -> contexte structure."""

    def __init__(self):
        self.extractor = ConceptExtractor()

    def abstract(self, question_id: str, raw_question: str) -> QuestionContext:
        concepts = self.extractor.extract(raw_question)
        model = _detect_model(raw_question)
        intent = _detect_intent(raw_question)
        domain = "methode_spectrale_savard" if concepts else "general"

        # Extraction des nombres mentionnes (p, n, indices)
        numbers = [int(m) for m in re.findall(r"\b\d+\b", raw_question)]

        ctx = QuestionContext(
            question_id=question_id,
            raw_question=raw_question,
            detected_domain=domain,
            detected_model=model,
            concepts=concepts,
            metadata={
                "intent": intent,
                "numbers_mentioned": numbers,
                "language": "fr",
            },
        )
        logger.debug("Abstraction : domain=%s model=%s intent=%s concepts=%d",
                     domain, model, intent, len(concepts))
        return ctx
