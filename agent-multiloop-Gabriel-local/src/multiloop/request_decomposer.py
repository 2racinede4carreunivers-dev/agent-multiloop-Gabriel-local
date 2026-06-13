"""
RequestDecomposer — Decoupe une requete utilisateur en segments logiques.

Inspire de l'exemple "1,2,13,3,4,5,6" : on identifie les SEGMENTS
(nombres, mots-clefs, intentions, contraintes) et on detecte ceux qui
violent une certitude du noyau (CertaintyKernel).

Le decomposer NE corrige pas la requete : il identifie juste les segments
coherents vs incoherents. La reconstruction est faite par le RequestRewriter
qui suit dans le pipeline du Slow-Motion Debugger.
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
            r"rapport\s+spectral\s+(?:sym[eé]trique)?\s*\d+\s*[x*]\s*\d+",
            r"sym[eé]trique\s+\d+\s*[x*]\s*\d+",
            r"configuration\s+\d+\s*[x*]\s*\d+",
            r"comparaison\s+(?:asym[eé]trique|sym[eé]trique)",
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

        # 2bis. NOUVEAU : pour les requetes de rapport spectral, extraire
        # les deux tuples parenthses (a,b,c) et (d,e,f).
        # Si l'utilisateur ecrit "(7,23,2) et (29,17,13)", on les extrait.
        if result.detected_intent in ("ratio_spectral_nxn", "ratio_spectral"):
            tuples = self._extract_tuples(question)
            if len(tuples) >= 2:
                result.tuple_A = tuples[0]
                result.tuple_B = tuples[1]
                if len(tuples[0]) == len(tuples[1]):
                    result.config_size = len(tuples[0])
                    # Promouvoir intent en nxn si tailles egales
                    result.detected_intent = "ratio_spectral_nxn"
            # On force le rapport a 1/2 par defaut quand spectral est mentionne
            if result.detected_ratio is None:
                result.detected_ratio = "1/2"

        # 3. Extraire les segments
        # 3a. Position citee
        position = self._extract_position(question)
        if position is not None:
            result.segments.append(Segment(
                kind="position", text=f"{position}e premier", value=position,
                coherent=(1 <= position <= 1000),  # table couvre 1000 premiers
                reason="" if 1 <= position <= 1000 else f"position {position} hors table [1..1000]",
            ))

        # 3b. Rapport
        if result.detected_ratio:
            result.segments.append(Segment(
                kind="ratio", text=result.detected_ratio,
                value=result.detected_ratio, coherent=True,
            ))

        # 3c. Tuples (A, B) si presents -> segments dedies
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
            # 3d. Tous les autres nombres (en excluant ceux dans les fractions 1/N)
            # On masque les fractions detectees pour ne pas re-capturer leurs chiffres
            masked = question
            for ratio in ("1/2", "1/3", "1/4"):
                masked = masked.replace(ratio, " RATIO ")
            numbers_found = [int(m) for m in re.findall(r"\b(\d+)\b", masked)]
            position_val = position if position else None
            for num in numbers_found:
                if num == position_val:
                    continue  # deja capture
                # Decide si ce nombre est coherent dans le contexte
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
        Accepte separateurs : virgule, point-virgule, espace.
        """
        tuples = []
        for match in re.finditer(r"\(([^)]+)\)", text):
            content = match.group(1)
            nums = re.findall(r"\d+", content)
            if nums:
                tuples.append([int(n) for n in nums])
        return tuples

    @staticmethod
    def _extract_position(text: str) -> Optional[int]:
        """Reutilise la meme regex que AntiHallucinationValidator."""
        patterns = [
            r'(\d+)\s*(?:eme|ieme|ième|ème|e|th|st|nd|rd)\s*(?:nombre\s+)?(?:premier|prime)',
            r'position\s+(\d+)',
            r'rang\s+(\d+)',
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
        
        Regle d'or : si rapport 1/2 ET position citee ET un autre nombre 
        ressemble a "n=<valeur>" mais != position => INCOHERENT (viole INVARIANT 1/2).
        """
        # Heuristique simple : pour 1/2, tout nombre != position cite explicitement 
        # comme "n=X" est suspect. Ici on ne sait pas le contexte exact, mais
        # si position est defini et num est tres proche (mais != position),
        # on flag comme suspect.
        if ratio == "1/2" and position is not None and num != position:
            # Si le nombre est petit (< 50) et != position, il pourrait etre un "n" hallucine
            if 1 <= num <= 50 and num != position:
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
