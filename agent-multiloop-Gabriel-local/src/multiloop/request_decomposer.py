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
    # NOUVEAU : taille annoncee par l'utilisateur dans la requete ("symétrique 4*4" -> 4)
    announced_size: Optional[int] = None
    # NOUVEAU : type de configuration annoncee ("symétrique" / "asymétrique")
    announced_symmetric: Optional[bool] = None
    # NOUVEAU (v3.23) : requete generique sur le i-ieme/n-ieme premier
    # (sans valeur numerique concrete). Ex: "reconstruis le i-ieme premier"
    # -> renvoie a la definition prime_i + theoreme prime_equation_prime_i
    # au lieu de basculer sur kernel_emergency_summary.
    is_generic_prime_i_query: bool = False

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

        # 0. Detecter les requetes GENERIQUES sur le i-ieme premier
        # (sans valeur numerique). Ex: "reconstruis le i-ème premier",
        # "peux-tu construire le n-ième nombre premier?", "prime_i", etc.
        # Ces patterns utilisent une LETTRE symbolique (i, n, k, N) au lieu
        # d'un chiffre concret. Sans ce flag, position=None et le pipeline
        # basculait sur kernel_emergency_summary (perte de contexte).
        # (?:^|\s) : la lettre doit etre precedee d'un espace ou debut de phrase
        # [-‐]     : le tiret est OBLIGATOIRE (evite "12-ieme" ou i dans "ieme")
        generic_prime_patterns = [
            r"(?:^|\s|\()(?:i|n|k|N)[-‐]\s*(?:eme|ieme|ième|ème)\s+(?:nombre\s+)?(?:premier|prime)",
            r"(?:^|\s|\()(?:i|n|k)[-‐]\s*(?:eme|ieme|ième|ème)(?![a-zA-Z])",
            r"\bprime[_\s]?i\b",
            r"(?:^|\s)p_i(?![a-zA-Z\d])",
        ]
        for pat in generic_prime_patterns:
            if re.search(pat, q_low):
                result.is_generic_prime_i_query = True
                break

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
            # Capter la taille annoncee + le qualificatif (symétrique/asymétrique)
            announced = self._extract_announced_config(question)
            if announced is not None:
                result.announced_size, result.announced_symmetric = announced
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
            # Detecter le mismatch annonce vs reel
            mismatch_reason = ""
            sizes_equal = (len(result.tuple_A) == len(result.tuple_B))
            if result.announced_size is not None:
                if (result.announced_symmetric is True
                        and result.announced_size != len(result.tuple_A)):
                    mismatch_reason = (
                        f"Annonce 'symetrique {result.announced_size}*{result.announced_size}'"
                        f" mais A a {len(result.tuple_A)} elements (mismatch taille)."
                    )
                if (result.announced_symmetric is True and not sizes_equal):
                    mismatch_reason = (
                        f"Annonce 'symetrique {result.announced_size}*{result.announced_size}'"
                        f" mais A={len(result.tuple_A)} elements != B={len(result.tuple_B)}"
                        " (configuration ASYMETRIQUE en realite)."
                    )
            tuple_a_coherent = (mismatch_reason == "")
            tuple_b_coherent = (mismatch_reason == "")
            result.segments.append(Segment(
                kind="tuple_A", text=str(tuple(result.tuple_A)),
                value=result.tuple_A,
                coherent=tuple_a_coherent,
                reason=mismatch_reason,
            ))
            result.segments.append(Segment(
                kind="tuple_B", text=str(tuple(result.tuple_B)),
                value=result.tuple_B,
                coherent=tuple_b_coherent,
                reason=mismatch_reason,
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
    def _extract_announced_config(text: str) -> Optional[tuple[int, bool]]:
        """Extrait la taille et la symetrie annoncees dans la requete.

        Exemples reconnus :
          "rapport spectral symetrique 4*4"  -> (4, True)
          "configuration symetrique 3x3"     -> (3, True)
          "rapport asymetrique 5*3"          -> (5, False) (premiere taille)

        Returns: (size_announced, is_symmetric) ou None si rien d'annonce.
        """
        t = text.lower()
        # IMPORTANT: chercher "asymetrique" AVANT "symetrique"
        # (sinon "symetrique" matche en sous-chaine de "asymetrique")
        m = re.search(
            r"asym[ée]trique\s*(\d+)\s*[x*]\s*(\d+)",
            t,
        )
        if m:
            return (int(m.group(1)), False)
        # Cherche "symetrique N*N" ou "symetrique NxN"
        m = re.search(
            r"(?<![a-z])sym[ée]trique\s*(\d+)\s*[x*]\s*(\d+)",
            t,
        )
        if m:
            return (int(m.group(1)), True)
        # "configuration NxN" sans qualificatif explicite -> symetrique par defaut
        m = re.search(
            r"configuration\s*(\d+)\s*[x*]\s*(\d+)",
            t,
        )
        if m and m.group(1) == m.group(2):
            return (int(m.group(1)), True)
        return None

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
