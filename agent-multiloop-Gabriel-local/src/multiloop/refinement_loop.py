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
from .critic import Critic


logger = logging.getLogger(__name__)


GROUNDED_SYSTEM_PROMPT = """Tu es Math-Agent, expert de la METHODE SPECTRALE de Philippe Thomas Savard.
Tu maitrises :
- Les suites SA(n) = (3.25/2)*2^n - 2 et SB(n) = (6.5/2)*2^n - 66
- Les suites A_1_3, B_1_3, A_1_4, B_1_4 (rapports 1/3 et 1/4)
- Le digamma_calc(n,p) = SB(n) - factor*p (factor = 64, 729 ou 4096)
- L'equation prime_equation(n,p) = (SB(n) - digamma_calc(n,p)) / factor = p
- Les 4 configurations du rapport spectral : 1x1, n*n, asymetrique ordonnee, asymetrique chaotique
- La formule de gap : gap_equation = (A_next - B_high + D_high - D_low) / factor

IMPERATIFS :
1. NE JAMAIS inventer de chiffres. Si des CHIFFRES CALCULES sont fournis dans le contexte, UTILISE-LES textuellement.
2. Explique en francais, clairement, en t'appuyant sur les formules du corpus.
3. Cite les concepts du corpus par leur nom officiel.
"""


REFINEMENT_INSTRUCTION = """Voici la critique de ta reponse precedente :
---
{critique}
---
Score precedent : {score}/10.

Ameliore ta reponse en corrigeant les points souleves. RESTE FIDELE AUX CHIFFRES CALCULES."""


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
    ) -> FinalAnswer:
        """Execute la boucle multi-loop et retourne la meilleure reponse."""
        all_candidates: list[CandidateAnswer] = []
        best: CandidateAnswer | None = None
        last_critique: str = ""

        for iteration in range(1, self.max_iterations + 1):
            logger.info("=== Multi-loop iteration %d/%d ===", iteration, self.max_iterations)
            round_candidates = []
            for cand_idx in range(self.num_candidates):
                prompt = self._build_prompt(ctx, precomputed_facts, base_prompt, last_critique, iteration)
                # Temperature un peu plus haute pour diversifier les candidats
                temp = 0.2 + 0.1 * cand_idx
                text = await self.llm.generate(prompt, system=GROUNDED_SYSTEM_PROMPT, temperature=temp)
                cand = CandidateAnswer(
                    iteration=iteration,
                    text=text or "[Vide]",
                    structured_data=precomputed_facts or {},
                    used_engines=["llm", "multiloop"],
                )
                cand = await self.critic.critique(cand, ctx, precomputed_facts)
                round_candidates.append(cand)
                all_candidates.append(cand)

            # Selection du meilleur du tour
            round_best = max(round_candidates, key=lambda c: c.score)
            if best is None or round_best.score > best.score:
                best = round_best
            last_critique = round_best.critique

            # Arret si score suffisant
            if best.score >= self.min_score:
                logger.info("Score suffisant (%.1f >= %.1f). Arret.", best.score, self.min_score)
                break

        assert best is not None
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
