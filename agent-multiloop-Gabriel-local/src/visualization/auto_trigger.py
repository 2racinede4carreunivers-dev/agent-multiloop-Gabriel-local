"""Detecteur d'intention de visualisation pour Gabriel.

Analyse une question en francais (sans LLM) et determine si l'utilisateur
demande implicitement un graphique. Si oui, identifie :
  - le type de courbe (SA, SB, digamma, ratio, gap, etc.)
  - l'intervalle [n_min, n_max]
  - le souhait d'export PNG

Approche : 100% deterministe (regex + mots-cles). Aucun appel LLM,
zero hallucination, latence quasi nulle.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Optional

from .curves import CurveKind


@dataclass
class VisualizationIntent:
    """Resultat de la detection d'intention de visualisation."""
    kind: CurveKind
    n_min: int
    n_max: int
    want_png: bool = False
    confidence: float = 1.0  # 0..1
    reasoning: str = ""      # Pourquoi cette detection (pour audit)
    matched_keywords: list[str] = None  # type: ignore

    def __post_init__(self):
        if self.matched_keywords is None:
            self.matched_keywords = []


# --------------------------------------------------------------------------
# Mots-cles
# --------------------------------------------------------------------------
# Verbes/noms qui signalent une volonte de visualisation
_VIZ_KEYWORDS = {
    "courbe", "courbes", "graphique", "graphiques", "graphe", "graphes",
    "trace", "tracer", "traces", "tracerais",
    "dessine", "dessiner", "dessines",
    "illustre", "illustrer", "illustres", "illustrant",
    "visualise", "visualiser", "visualises",
    "evolution", "evolue", "evoluent", "evoluer",
    "convergence", "converge", "convergent",
    "comportement", "comporte", "comportent",
    "represente", "representer", "represente",
    "affiche", "afficher", "affichant",
    "montre", "montrer", "voir",
    "diagramme", "schema", "plot",
    "trajectoire", "progression",
    "allure", "forme",
}

# Mots qui suggerent l'export PNG (article scientifique, etc.)
_PNG_KEYWORDS = {
    "png", "image", "fichier", "pdf",
    "article", "scientifique", "publication", "papier",
    "exporte", "exporter", "exportation", "sauvegarde", "sauvegarder",
    "citer", "citable", "cite",
    "rapport", "document",
}

# Mots qui suggerent un tableau de donnees
_TABLE_KEYWORDS = {
    "tableau", "table", "tableaux", "tabule", "tabuler",
    "valeurs", "chiffres", "donnees",
}

# Map mots-cles -> CurveKind
# L'ordre importe : on cherche les expressions composees en premier.
# Chaque pattern peut etre :
#   - une string -> matched as 'word' avec bornes \b (regex)
#   - une string finissant par espace = matche comme substring brut (pour compatibilite)
_KIND_PATTERNS: list[tuple[CurveKind, list[str]]] = [
    # SA_SB doit etre teste AVANT SA et SB seuls
    (CurveKind.SA_SB, [
        r"sa\s+et\s+sb", r"sb\s+et\s+sa", r"sa\s*\+\s*sb",
        r"suites?\s+a\s+et\s+b", r"suite\s+a\s+et\s+suite\s+b",
        r"sommes?\s+a\s+et\s+b", r"sa\s+puis\s+sb",
        r"superposer?\s+sa\s+sb",
    ]),
    (CurveKind.RATIO_SA_SB, [
        r"ratio\s+sa\s*/\s*sb", r"ratio\s+sa\s+sb",
        r"rapport\s+sa\s*/\s*sb", r"rapport\s+sa\s+sb",
        r"\bratio\b", r"rapport\s+spectral", r"rapport\s+asymptotique",
        r"\bsa\s*/\s*sb\b", r"convergence\s+vers\s+1\s*/\s*2",
        r"convergence\s+asymptotique",
    ]),
    (CurveKind.SA, [
        r"\bsa\s*\(\s*n\s*\)", r"\bsa\s+de\s+n", r"somme\s+alternee\s+a",
        r"\bsomme\s+a\b", r"suite\s+alternee\s+a", r"\bsuite\s+a\b",
        r"\bsa\b",
    ]),
    (CurveKind.SB, [
        r"\bsb\s*\(\s*n\s*\)", r"\bsb\s+de\s+n", r"somme\s+alternee\s+b",
        r"\bsomme\s+b\b", r"suite\s+alternee\s+b", r"\bsuite\s+b\b",
        r"\bsb\b",
    ]),
    (CurveKind.DIGAMMA, [
        r"\bdigamma\b", r"\bpsi\b", r"ψ", r"fonction\s+psi",
        r"fonction\s+digamma",
    ]),
    (CurveKind.INVARIANT, [
        r"\binvariant\b", r"d\s*\(\s*n\s*,\s*p\s*\)", r"d\s+de\s+n",
        r"sb\s*-\s*sa\s*-\s*z\s*\*\s*p", r"\bsb\s*-\s*sa\b",
        r"ecart\s+structurel",
    ]),
    (CurveKind.GAP, [
        r"\bgap\b", r"\bgaps\b", r"\becart\b", r"\becarts\b", r"\becartement\b",
        r"delta[_\s]p", r"p\s*\(\s*n\s*\+\s*1\s*\)\s*-\s*p\s*\(\s*n\s*\)",
        r"premiers\s+consecutifs", r"primes\s+consecutifs",
    ]),
    (CurveKind.PRIME, [
        r"\bpremiers\b", r"\bprimes\b", r"\bp\s*\(\s*n\s*\)",
        r"nombres?\s+premiers?", r"croissance\s+des\s+premiers",
        r"n[-\s]ieme\s+premier",
    ]),
]

# Patterns d'intervalle (regex). Tous capturent (n_min, n_max).
# On teste du plus specifique au moins specifique.
_RANGE_PATTERNS = [
    # "n=1..50" / "n=1 a 50" / "1..1000"
    re.compile(r"n\s*=\s*(\d+)\s*(?:\.\.|a|à|jusqu['e]\s*a|jusqu['e]\s*à)\s*(\d+)", re.IGNORECASE),
    re.compile(r"(?<!\d)(\d{1,4})\s*\.\.\s*(\d{1,4})(?!\d)"),
    # "de 1 a 50" / "de 1 à 50"
    re.compile(r"de\s+(\d+)\s+(?:a|à)\s+(\d+)", re.IGNORECASE),
    # "entre 1 et 50"
    re.compile(r"entre\s+(\d+)\s+et\s+(\d+)", re.IGNORECASE),
    # "n entre 1 et 50"
    re.compile(r"n\s+entre\s+(\d+)\s+et\s+(\d+)", re.IGNORECASE),
    # "sur l'intervalle [1, 50]" / "[1,50]"
    re.compile(r"\[\s*(\d+)\s*[,;]\s*(\d+)\s*\]"),
    # "sur 1..50"
    re.compile(r"sur\s+(\d+)\s*\.\.\s*(\d+)", re.IGNORECASE),
    # "pour les N premiers" / "premiers 100 termes" -> 1..N
]

# Pattern "premiers N" / "N premiers" -> 1..N
_FIRST_N_PATTERNS = [
    re.compile(r"(?:les\s+)?(\d+)\s+(?:premiers|premieres|premiers\s+termes|premiers\s+nombres)", re.IGNORECASE),
    re.compile(r"premiers?\s+(\d+)", re.IGNORECASE),
]

# Limites strictes
_N_MIN_ABS = 1
_N_MAX_ABS = 1000
_DEFAULT_N_MIN = 1
_DEFAULT_N_MAX = 50  # Defaut raisonnable si pas d'intervalle precise


def _strip_accents(s: str) -> str:
    """Retire les accents pour faciliter le matching."""
    nfd = unicodedata.normalize("NFD", s)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")


def _normalize(question: str) -> str:
    """Normalise : minuscules + sans accents + espaces simples."""
    q = _strip_accents(question.lower())
    q = re.sub(r"\s+", " ", q).strip()
    return q


def _detect_kind(qnorm: str) -> tuple[Optional[CurveKind], list[str]]:
    """Identifie le type de courbe demande, retourne (kind, mots-cles matches)."""
    matched: list[str] = []
    for kind, patterns in _KIND_PATTERNS:
        for pat in patterns:
            m = re.search(pat, qnorm, re.IGNORECASE)
            if m:
                matched.append(m.group(0).strip())
                return kind, matched
    return None, matched


def _detect_range(qnorm: str) -> Optional[tuple[int, int]]:
    """Extrait [n_min, n_max] depuis la question. Retourne None si non trouve."""
    # Patterns "n_min..n_max"
    for pat in _RANGE_PATTERNS:
        m = pat.search(qnorm)
        if m:
            try:
                a, b = int(m.group(1)), int(m.group(2))
                if a > b:
                    a, b = b, a
                a = max(_N_MIN_ABS, a)
                b = min(_N_MAX_ABS, b)
                if a <= b:
                    return (a, b)
            except (ValueError, IndexError):
                continue
    # Pattern "N premiers" -> 1..N
    for pat in _FIRST_N_PATTERNS:
        m = pat.search(qnorm)
        if m:
            try:
                n = int(m.group(1))
                if 2 <= n <= _N_MAX_ABS:
                    return (1, n)
            except (ValueError, IndexError):
                continue
    return None


def _detect_png_intent(qnorm: str) -> bool:
    """Detecte si l'utilisateur souhaite un PNG citable."""
    for kw in _PNG_KEYWORDS:
        if kw in qnorm:
            return True
    return False


def detect_visualization_intent(question: str) -> Optional[VisualizationIntent]:
    """Analyse une question et retourne un VisualizationIntent si une visualisation est demandee.

    Args:
        question: question utilisateur en francais (peut contenir accents).

    Returns:
        VisualizationIntent si une visualisation est detectee, None sinon.
    """
    if not question or not question.strip():
        return None
    qnorm = _normalize(question)

    # 1) Verifier qu'il y a un mot-cle de visualisation
    viz_hits = [kw for kw in _VIZ_KEYWORDS if kw in qnorm]
    if not viz_hits:
        return None

    # 2) Identifier le type de courbe
    kind, kind_matches = _detect_kind(qnorm)
    if kind is None:
        return None

    # 3) Identifier l'intervalle (defaut 1..50)
    rng = _detect_range(qnorm)
    if rng is None:
        n_min, n_max = _DEFAULT_N_MIN, _DEFAULT_N_MAX
        range_source = "defaut (1..50)"
    else:
        n_min, n_max = rng
        range_source = f"detecte ({n_min}..{n_max})"

    # 4) Detection PNG
    want_png = _detect_png_intent(qnorm)

    # 5) Confidence (heuristique simple)
    # +0.4 pour mot-cle viz, +0.4 pour type identifie, +0.2 si intervalle explicite
    confidence = 0.4 + 0.4 + (0.2 if rng is not None else 0.0)

    matched = viz_hits[:3] + kind_matches[:2]
    reasoning = (
        f"Mots-cles visualisation : {', '.join(viz_hits[:3])}. "
        f"Type identifie : {kind.value} (matches : {', '.join(kind_matches[:2])}). "
        f"Intervalle : {range_source}. "
        f"PNG demande : {'oui' if want_png else 'non'}."
    )

    return VisualizationIntent(
        kind=kind,
        n_min=n_min,
        n_max=n_max,
        want_png=want_png,
        confidence=confidence,
        reasoning=reasoning,
        matched_keywords=matched,
    )
