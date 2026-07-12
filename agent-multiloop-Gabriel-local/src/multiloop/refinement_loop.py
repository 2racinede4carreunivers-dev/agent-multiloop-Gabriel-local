"""
Boucle de raffinement multi-loop :
  1. Genere N candidats
  2. Critique chacun
  3. Si meilleur score < seuil, genere une nouvelle iteration avec critique en entree
  4. Repete jusqu'a max_iterations ou score >= seuil
  5. Retourne la meilleure reponse
"""
from __future__ import annotations

import logging
from typing import Any

from ..core.llm_manager import LLMManager
from ..core.types import CandidateAnswer, FinalAnswer, QuestionContext
from ..spectral.spectral_knowledge import build_grounded_system_prompt
from .critic import Critic


logger = logging.getLogger(__name__)


GROUNDED_SYSTEM_PROMPT = build_grounded_system_prompt()


REFINEMENT_INSTRUCTION = """Voici la critique constructive de ta reponse precedente :
---
{critique}
---
Score precedent : {score}/10.

Ameliore ta reponse en tenant compte de ces remarques.
RAPPEL CRITIQUE : utilise UNIQUEMENT les chiffres calcules fournis, n'invente RIEN.
Reste bienveillant et ne dis JAMAIS que la methode est incoherente."""


class RefinementLoop:
    """Boucle multi-loop avec self-critique."""

    def __init__(self, llm: LLMManager, critic: Critic, config: dict[str, Any]):
        self.llm = llm
        self.critic = critic
        ml_cfg = config.get("multiloop", {})
        self.max_iterations = int(ml_cfg.get("max_iterations", 3))
        self.min_score = float(ml_cfg.get("min_acceptance_score", 8.0))
        self.num_candidates = int(ml_cfg.get("num_candidates_per_round", 2))

    async def run(
        self,
        ctx: QuestionContext,
        precomputed_facts: dict[str, Any] | None = None,
        base_prompt: str | None = None,
        progress_cb: Any | None = None,
    ) -> FinalAnswer:
        """Execute la boucle multi-loop et retourne la meilleure reponse."""
        all_candidates: list[CandidateAnswer] = []
        best: CandidateAnswer | None = None
        last_critique: str = ""

        def _emit(event: str, **payload: Any) -> None:
            if not progress_cb:
                return
            try:
                progress_cb(event, payload)
            except Exception:
                # Le rendu terminal ne doit jamais interrompre le calcul.
                pass

        for iteration in range(1, self.max_iterations + 1):
            logger.info("=== Multi-loop iteration %d/%d ===", iteration, self.max_iterations)
            _emit(
                "multiloop_iteration_start",
                iteration=iteration,
                max_iterations=self.max_iterations,
                num_candidates=self.num_candidates,
            )
            round_candidates = []
            for cand_idx in range(self.num_candidates):
                prompt = self._build_prompt(ctx, precomputed_facts, base_prompt, last_critique, iteration)
                # Temperature un peu plus haute pour diversifier les candidats
                temp = 0.2 + 0.1 * cand_idx
                text = await self.llm.generate(
                    prompt,
                    system=GROUNDED_SYSTEM_PROMPT,
                    temperature=temp,
                    include_conversation=True,
                )
                cand = CandidateAnswer(
                    iteration=iteration,
                    text=text or "[Vide]",
                    structured_data=precomputed_facts or {},
                    used_engines=["llm", "multiloop"],
                )
                cand = await self.critic.critique(cand, ctx, precomputed_facts)
                round_candidates.append(cand)
                all_candidates.append(cand)
                _emit(
                    "multiloop_candidate_scored",
                    iteration=iteration,
                    candidate=cand_idx + 1,
                    score=round(cand.score, 2),
                    grounded=bool(cand.grounded),
                )

            # Selection du meilleur du tour
            round_best = max(round_candidates, key=lambda c: c.score)
            if best is None or round_best.score > best.score:
                best = round_best
            last_critique = round_best.critique
            _emit(
                "multiloop_round_best",
                iteration=iteration,
                score=round(round_best.score, 2),
                threshold=self.min_score,
            )

            # Arret si score suffisant
            if best.score >= self.min_score:
                logger.info("Score suffisant (%.1f >= %.1f). Arret.", best.score, self.min_score)
                _emit(
                    "multiloop_stop",
                    iteration=iteration,
                    score=round(best.score, 2),
                    threshold=self.min_score,
                    reason="threshold_reached",
                )
                break

        assert best is not None
        _emit(
            "multiloop_done",
            best_score=round(best.score, 2),
            iterations_used=best.iteration,
            total_candidates=len(all_candidates),
        )
        return FinalAnswer(
            question_id=ctx.question_id,
            answer_text=best.text,
            structured_data=best.structured_data,
            confidence=best.score / 10.0,
            iterations_used=best.iteration,
            best_score=best.score,
            candidates=all_candidates,
            explanation=best.critique,
        )

    def _build_prompt(
        self,
        ctx: QuestionContext,
        facts: dict[str, Any] | None,
        base_prompt: str | None,
        last_critique: str,
        iteration: int,
    ) -> str:
        parts: list[str] = []
        if base_prompt:
            parts.append(base_prompt)
        parts.append(f"QUESTION DE L'UTILISATEUR :\n{ctx.raw_question}\n")
        if facts:
            facts_lines = ["CHIFFRES CALCULES (a utiliser textuellement) :"]
            for k, v in facts.items():
                if isinstance(v, (int, float, str)):
                    facts_lines.append(f"  - {k} = {v}")
            parts.append("\n".join(facts_lines))
        if iteration > 1 and last_critique:
            parts.append(REFINEMENT_INSTRUCTION.format(critique=last_critique, score="precedent"))
        parts.append("\nReponds en francais, de maniere structuree et complete.")
        return "\n\n".join(parts)
