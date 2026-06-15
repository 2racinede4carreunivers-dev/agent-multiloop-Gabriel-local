"""
RequestDecomposer CORRECTED — Decoupe une requete utilisateur en segments logiques.

CORRECTION MAJEURE : Capturer les nombres NÉGATIFS
  Avant : regex r"\b(\d+)\b" → capture 23 mais pas -23
  Après : regex r"-?\d+" → capture -23 aussi

Cela fix le bug où "écart entre -3 et -23" était converti en "écart entre 3 et 23".
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Segment:
    """Un segment logique d'une requete."""
    kind: str          # "position" | "ratio" | "number" | "constraint" | "intent" | "noise"
    text: str          # le bout de texte original
    value: Any = None  # valeur typee si applicable (int, float, str)
    coherent: bool = True
    reason: str = ""   # raison d'incoherence si coherent=False

    def __repr__(self) -> str:
        flag = "✓" if self.coherent else "✗"
        return f"<{flag} {self.kind}={self.value!r} ({self.text!r})>"


@dataclass
class DecomposedRequest:
    """Resultat de la decomposition d'une requete."""
    original: str
    segments: list[Segment] = field(default_factory=list)
    detected_intent: str = "unknown"   # "reconstruction" | "ratio_spectral" | "ratio_spectral_nxn" | "gap" | "unknown"
    detected_ratio: Optional[str] = None  # "1/2" | "1/3" | "1/4"
    # NOUVEAU : tuples (A, B) extraits pour les requetes de rapport spectral n*n
    tuple_A: Optional[list[int]] = None
    tuple_B: Optional[list[int]] = None
    config_size: Optional[int] = None  # 3 pour 3*3, etc.

    @property
    def coherent_segments(self) -> list[Segment]:
        return [s for s in self.segments if s.coherent]

    @property
    def incoherent_segments(self) -> list[Segment]:
        return [s for s in self.segments if not s.coherent]

    @property
    def has_anomaly(self) -> bool:
        return len(self.incoherent_segments) > 0


class RequestDecomposer:
    """Decoupe une requete en segments et detecte les anomalies."""

    # Detecteurs de l'intention
    INTENT_PATTERNS = {
        "reconstruction": [
            r"reconstrui[rs]", r"reconstituer", r"retrouve[rz]",
            r"\d+\s*(?:eme|ieme|ième|ème|e|th)\s*(?:nombre\s+)?(?:premier|prime)",
            r"position\s+\d+", r"rang\s+\d+",
        ],
        "ratio_spectral_nxn": [
            r"rapport\s+spectral\s+(?:symétrique)?\s*\d+\s*[x*]\s*\d+",
            r"symétrique\s+\d+\s*[x*]\s*\d+",
            r"configuration\s+\d+\s*[x*]\s*\d+",
            r"comparaison\s+(?:asymétrique|symétrique)",
        ],
        "ratio_spectral": [
            r"rapport\s+spectral", r"calcul.*ratio",
            r"\bRsP\b", r"calcul.*rapport",
        ],
        "gap": [r"\bgap\b", r"ecart", r"écart"],
    }

    RATIO_PATTERNS = {
        "1/2": [r"1/2", r"\bdemi\b", r"un\s+demi"],
        "1/3": [r"1/3", r"\btiers\b", r"un\s+tiers"],
        "1/4": [r"1/4", r"\bquart\b", r"un\s+quart"],
    }

    def decompose(self, question: str) -> DecomposedRequest:
        """Decompose la requete en segments logiques."""
        result = DecomposedRequest(original=question)
        q_low = question.lower()

        # 1. Detecter l'intention
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, q_low):
                    result.detected_intent = intent
                    break
            if result.detected_intent != "unknown":
                break

        # 2. Detecter le rapport
        for ratio, patterns in self.RATIO_PATTERNS.items():
            if any(re.search(p, q_low) for p in patterns):
                result.detected_ratio = ratio
                break

        # 2bis. Pour les requetes de rapport spectral, extraire les tuples
        if result.detected_intent in ("ratio_spectral_nxn", "ratio_spectral"):
            tuples = self._extract_tuples(question)
            if len(tuples) >= 2:
                result.tuple_A = tuples[0]
                result.tuple_B = tuples[1]
                if len(tuples[0]) == len(tuples[1]):
                    result.config_size = len(tuples[0])
                    result.detected_intent = "ratio_spectral_nxn"
            if result.detected_ratio is None:
                result.detected_ratio = "1/2"

        # 3. Extraire les segments
        # 3a. Position citee
        position = self._extract_position(question)
        if position is not None:
            # CORRECTION : position peut être négative (-3, -23, etc.)
            result.segments.append(Segment(
                kind="position", text=f"{position}e premier", value=position,
                coherent=(-1000 <= position <= 1000),  # table couvre ±1000
                reason="" if (-1000 <= position <= 1000) else f"position {position} hors limites",
            ))

        # 3b. Rapport
        if result.detected_ratio:
            result.segments.append(Segment(
                kind="ratio", text=result.detected_ratio,
                value=result.detected_ratio, coherent=True,
            ))

        # 3c. Tuples (A, B) si presents
        if result.tuple_A is not None and result.tuple_B is not None:
            result.segments.append(Segment(
                kind="tuple_A", text=str(tuple(result.tuple_A)),
                value=result.tuple_A, coherent=True,
            ))
            result.segments.append(Segment(
                kind="tuple_B", text=str(tuple(result.tuple_B)),
                value=result.tuple_B, coherent=True,
            ))
        else:
            # 3d. Tous les autres nombres
            # CORRECTION MAJEURE : utiliser -?\d+ pour capturer les NÉGATIFS
            masked = question
            for ratio in ("1/2", "1/3", "1/4"):
                masked = masked.replace(ratio, " RATIO ")
            # FIX : -?\d+ capture aussi les nombres négatifs
            numbers_found = [int(m) for m in re.findall(r"-?\d+", masked)]
            position_val = position if position else None
            for num in numbers_found:
                if num == position_val:
                    continue
                seg = self._classify_number(num, position_val, result.detected_ratio)
                result.segments.append(seg)

        # 3e. Intention en segment
        if result.detected_intent != "unknown":
            result.segments.append(Segment(
                kind="intent", text=result.detected_intent,
                value=result.detected_intent, coherent=True,
            ))

        # 3f. Si l'intention est inconnue : flag "noise"
        if result.detected_intent == "unknown" and not result.segments:
            result.segments.append(Segment(
                kind="noise", text=question, value=None,
                coherent=False, reason="aucune intention spectrale detectee",
            ))

        return result

    @staticmethod
    def _extract_tuples(text: str) -> list[list[int]]:
        """
        Extrait les tuples entre parentheses : (a,b,c) -> [a, b, c].
        CORRECTION : capturer aussi les nombres NÉGATIFS
        """
        tuples = []
        for match in re.finditer(r"\(([^)]+)\)", text):
            content = match.group(1)
            # FIX : -?\d+ pour capturer les négatifs
            nums = re.findall(r"-?\d+", content)
            if nums:
                tuples.append([int(n) for n in nums])
        return tuples

    @staticmethod
    def _extract_position(text: str) -> Optional[int]:
        """
        Extrait une position citée.
        CORRECTION : capturer aussi les positions NÉGATIVES
        """
        patterns = [
            # FIX : (-?\d+) capture les positions négatives
            r"(-?\d+)\s*(?:eme|ieme|ième|ème|e|th|st|nd|rd)\s*(?:nombre\s+)?(?:premier|prime)",
            r"position\s+(-?\d+)",
            r"rang\s+(-?\d+)",
        ]
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                try:
                    return int(m.group(1))
                except ValueError:
                    pass
        return None

    @staticmethod
    def _classify_number(num: int, position: Optional[int], ratio: Optional[str]) -> Segment:
        """
        Classifie un nombre annexe.
        """
        if ratio == "1/2" and position is not None and num != position:
            if 1 <= abs(num) <= 50 and num != position:
                return Segment(
                    kind="number", text=str(num), value=num,
                    coherent=False,
                    reason=(
                        f"nombre {num} suspect : pour rapport 1/2 avec position {position}, "
                        f"l'INVARIANT impose n=num_termes={position}, pas {num}."
                    ),
                )
        return Segment(
            kind="number", text=str(num), value=num,
            coherent=True,
        )
