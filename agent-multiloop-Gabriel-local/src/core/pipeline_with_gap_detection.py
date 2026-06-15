"""
PIPELINE INTEGRATION FIX - Détecter les écarts AVANT le multiloop.
"""
from __future__ import annotations

import logging
import re
import uuid
from typing import Any, Optional

from ..core.types import FinalAnswer, QuestionContext
from ..spectral.gap_solver_corrected import GapSolver, GapResult
from ..spectral.prime_table import prime_position, nth_prime


logger = logging.getLogger(__name__)


def detect_gap_from_question(question: str) -> tuple[bool, Optional[str], list[int]]:
    """
    Détecte si la question demande un écart (GAP) entre DEUX premiers.
    
    CRUCIAL : Distinguer entre :
      - "écart entre 3 et 23" → GAP (deux nombres)
      - "rapport spectral... bloc A (3,23,31) bloc B (17,11,29)" → RATIO (deux blocs)
    
    Returns:
        (is_gap, gap_type, [p1, p2])
    """
    q_low = question.lower()
    
    # Si c'est un rapport spectral (bloc), ne pas détecter comme gap
    if "rapport spectral" in q_low or "bloc" in q_low:
        return False, None, []
    
    # Vérifier les mots-clés d'écart
    if not any(kw in q_low for kw in ["écart", "gap", "entre"]):
        return False, None, []
    
    # S'assurer qu'on a exactement 2 nombres
    numbers = re.findall(r'-?\d+', question)
    
    if len(numbers) != 2:
        return False, None, []
    
    try:
        p1, p2 = int(numbers[0]), int(numbers[1])
    except ValueError:
        return False, None, []
    
    # Classifier le type
    if p1 > 0 and p2 > 0:
        gap_type = "positive_positive"
    elif p1 < 0 and p2 < 0:
        gap_type = "negative_negative"
    elif (p1 < 0 and p2 > 0) or (p1 > 0 and p2 < 0):
        gap_type = "mixed"
    else:
        gap_type = None
    
    if gap_type:
        logger.info(f"ÉCART détecté : {gap_type} (p1={p1}, p2={p2})")
        return True, gap_type, [p1, p2]
    
    return False, None, []


class PipelineWithGapDetection:
    """
    Wrapper du Pipeline qui détecte et résout les écarts AVANT multiloop.
    """
    
    def __init__(self, base_pipeline):
        self.pipeline = base_pipeline
        self.gap_solver = GapSolver(spectral_core=base_pipeline.spectral_core)
        logger.info("✓ PipelineWithGapDetection initialized")

    def __getattr__(self, name):
        """Delegation transparente vers le pipeline de base.

        Permet a l'UI / aux autres modules d'acceder a `spectral_core`,
        `audit_store`, `corpus`, `verification_loop`, etc. sans connaitre
        ce wrapper. Toute commande historique du CLI continue de fonctionner.
        """
        # __getattr__ n'est appele que si l'attribut n'existe pas sur self.
        # On evite la recursion infinie si self.pipeline n'est pas encore set.
        if name == "pipeline":
            raise AttributeError(name)
        try:
            return getattr(self.pipeline, name)
        except AttributeError:
            raise AttributeError(
                f"'PipelineWithGapDetection' et son base_pipeline n'ont pas d'attribut '{name}'"
            )
    
    async def process(
        self,
        question: str,
        previous_answer: Optional[FinalAnswer] = None,
    ) -> FinalAnswer:
        """
        Processus amélioré :
          1. Détecter si c'est une question d'écart
          2. Si OUI : résoudre directement via GapSolver (pas multiloop)
          3. Si NON : exécuter pipeline standard
        """
        qid = uuid.uuid4().hex[:8]
        
        is_gap, gap_type, numbers = detect_gap_from_question(question)
        
        if is_gap and gap_type and len(numbers) >= 2:
            logger.info(f"Q[{qid}] ÉCART DÉTECTÉ : {gap_type}")
            
            p1, p2 = numbers[0], numbers[1]
            gap_result = self.gap_solver.solve_gap(p1, p2)
            
            if gap_result is not None:
                logger.info(f"Q[{qid}] Écart résolu : {gap_result.gap_count} nombres")
                answer = self._build_gap_answer(qid, question, gap_result)
                return answer
            else:
                logger.error(f"Q[{qid}] GapSolver échoué pour {gap_type}")
        
        logger.info(f"Q[{qid}] Pas d'écart détecté, pipeline standard")
        return await self.pipeline.process(question)
    
    def _build_gap_answer(self, qid: str, question: str, result: GapResult) -> FinalAnswer:
        """Convertit GapResult en FinalAnswer."""
        from ..core.types import CandidateAnswer
        
        answer_text = self._render_gap_result(result)
        
        candidate = CandidateAnswer(
            iteration=1,
            text=answer_text,
            structured_data={
                "gap_type": result.gap_type,
                "p1": result.p1,
                "p2": result.p2,
                "gap_count": result.gap_count,
                "gap_float": result.gap_float,
                "position_min": result.position_min,
                "position_max": result.position_max,
                "position_suivant_min": result.position_suivant_min,
                "p_suivant_min": result.p_suivant_min,
                "SA_suivant_min": result.SA_suivant_min,
                "SB_max": result.SB_max,
                "digamma_max": result.digamma_max,
                "digamma_min": result.digamma_min,
                "formula_used": result.formula_used,
                "validation": result.validation,
            },
            score=10.0,
            critique="Calcul spectral certifié (kernel + spectral_core, pas LLM)",
            grounded=True,
            used_engines=["gap_solver", "spectral_core"],
        )
        
        return FinalAnswer(
            question_id=qid,
            answer_text=answer_text,
            structured_data=candidate.structured_data,
            confidence=1.0,
            iterations_used=1,
            best_score=10.0,
            candidates=[candidate],
            explanation=result.explanation,
        )
    
    def _render_gap_result(self, result: GapResult) -> str:
        """Affiche le résultat d'écart."""
        lines = []
        lines.append(f"### Écart spectral {result.gap_type.upper()}")
        lines.append("")
        lines.append(f"**Entre {result.p1} et {result.p2}** : **{result.gap_count} nombres**")
        lines.append("")
        
        lines.append("**Détail du calcul** :")
        lines.append(f"  - Type : {result.gap_type}")
        lines.append(f"  - Position min : {result.position_min}")
        lines.append(f"  - Position max : {result.position_max}")
        lines.append(f"  - Position suivant min : {result.position_suivant_min}")
        lines.append(f"  - Premier suivant min : {result.p_suivant_min}")
        lines.append("")
        
        lines.append("**Valeurs spectrales** :")
        lines.append(f"  - SA(suivant_min) : {result.SA_suivant_min:.6f}")
        lines.append(f"  - SB(max) : {result.SB_max:.6f}")
        lines.append(f"  - digamma(max) : {result.digamma_max:.6f}")
        lines.append(f"  - digamma(min) : {result.digamma_min:.6f}")
        lines.append("")
        
        lines.append("**Formule** :")
        lines.append(f"  {result.formula_used}")
        lines.append("")
        
        lines.append("**Sources** :")
        sources = result.validation.get("source", [])
        if isinstance(sources, str):
            lines.append(f"  • {sources}")
        elif isinstance(sources, list):
            for src in sources:
                lines.append(f"  • {src}")
        
        if result.validation.get("zero_special"):
            lines.append("")
            lines.append("⚠️ **CAS SPÉCIAL** : Zéro a un rôle particulier (lien Riemann)")
        
        lines.append("")
        lines.append(f"**RÉSULTAT** : {result.gap_count} nombres entre {result.p1} et {result.p2}")
        
        return "\n".join(lines)
