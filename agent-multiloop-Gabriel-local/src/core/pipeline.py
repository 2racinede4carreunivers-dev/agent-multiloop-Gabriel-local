"""
Pipeline cognitif principal : orchestre les 5 moteurs + multiloop + spectral.

Flow :
  Question
    -> Abstraction (extrait concepts)
    -> Meta-raisonnement (selectionne strategie)
    -> Navigation conceptuelle (etend contexte)
    -> Generalisation (templates)
    -> Calcul DIRECT via module spectral (si applicable)
    -> Multi-loop self-critique (explication)
    -> Generation HOL (si applicable)
    -> Reponse finale
"""
from __future__ import annotations

import logging
import uuid
from typing import Any

from ..adapters.corpus.thy_loader import TheoryLoader
from ..adapters.hol_isabelle.isabelle_adapter import IsabelleAdapter
from ..core.llm_manager import LLMManager
from ..core.types import FinalAnswer, QuestionContext, SpectralModel
from ..engines.abstraction import AbstractionLayer
from ..engines.concept_navigation import Navigator
from ..engines.generalization import Generalizer
from ..engines.meta_reasoning import GoalAnalyzer, ProofPlanner, StrategySelector
from ..engines.numerical_verification import NumericalVerifier
from ..engines.theorem_discovery import DiscoveryLoop
from ..multiloop import Critic, RefinementLoop
from ..spectral import (
    compute_gap,
    compute_spectral_ratio,
    verify_prime_equation,
)
from .spectral_core import (
    SpectralMethodCore,
    AntiHallucinationValidator,
    SpectralRatio,
)


logger = logging.getLogger(__name__)


class Pipeline:
    """Pipeline complet du Multi-Loop Agent avec compréhension spectrale stricte."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.llm = LLMManager(config)
        self.abstraction = AbstractionLayer()
        self.goal_analyzer = GoalAnalyzer()
        self.strategy_selector = StrategySelector()
        self.proof_planner = ProofPlanner()
        self.navigator = Navigator()
        self.generalizer = Generalizer()
        self.discovery = DiscoveryLoop()
        self.critic = Critic(self.llm)
        self.refinement = RefinementLoop(self.llm, self.critic, config)
        self.isabelle = IsabelleAdapter(config)
        self.verifier = NumericalVerifier()  # 6e moteur : Wolfram (optionnel)
        self.corpus = TheoryLoader(config.get("data", {}).get("hol_dir", "/theories"))
        self.corpus.load_all()
        
        # NOUVEAU: Moteur spectral core (compréhension stricte)
        self.spectral_core = SpectralMethodCore()
        self.anti_hallucination = AntiHallucinationValidator()
        logger.info("✓ Pipeline initialized with SpectralMethodCore (INVARIANT: n=position=num_termes)")

    async def process(self, question: str) -> FinalAnswer:
        """Traite une question end-to-end via le pipeline."""
        qid = uuid.uuid4().hex[:8]

        # 1. Abstraction
        ctx = self.abstraction.abstract(qid, question)
        logger.info("Q[%s] domain=%s model=%s intent=%s", qid, ctx.detected_domain, ctx.detected_model, ctx.metadata.get("intent"))

        # 2. Meta-raisonnement
        goal = self.goal_analyzer.analyze(ctx)
        strategy = self.strategy_selector.select(ctx, goal)
        plan = self.proof_planner.plan(ctx, goal, strategy)

        # 3. Navigation conceptuelle
        concept_names = [c.name for c in ctx.concepts]
        expanded = self.navigator.expand_concepts(concept_names)

        # 4. Calcul direct (le coeur de la verite mathematique)
        precomputed_facts: dict[str, Any] = {}
        if goal["needs_computation"]:
            precomputed_facts = self._compute_spectral(ctx, plan, qid)
            logger.info("Q[%s] calculs spectraux directs : %s", qid, list(precomputed_facts.keys())[:5])

            # 4.bis Verification independante via Wolfram (si configure)
            if self.verifier.is_available and goal["intent"] == "reconstruction":
                p_val = precomputed_facts.get("p")
                if isinstance(p_val, int):
                    wolfram_check = await self.verifier.verify_prime(p_val)
                    precomputed_facts["wolfram_verification"] = wolfram_check
                    logger.info("Q[%s] Wolfram check: %s", qid, wolfram_check.get("outcome"))

        # 5. Generalisation
        general = self.generalizer.generalize(
            precomputed_facts,
            {
                "intent": goal["intent"],
                "model": plan["model"],
                "question": question,
            },
        )

        # 6. Construction du prompt grounded + Multi-loop self-critique
        base_prompt = self._build_base_prompt(ctx, plan, general, expanded)
        final = await self.refinement.run(ctx, precomputed_facts, base_prompt)
        
        # NOUVEAU: Validation anti-hallucination sur la réponse LLM
        is_valid, feedback = self.anti_hallucination.validate_answer(question, final.answer_text)
        if not is_valid:
            logger.warning(f"Q[{qid}] HALLUCINATION DETECTED: {feedback}")
            final.answer_text = f"""⚠️ CORRECTION MANDATORY:
{feedback}

INVARIANT SPECTRAL (non-négociable):
  Position du nombre premier = n = Nombre de termes dans A et B

Votre question parlait de position {self.anti_hallucination._extract_position(question)}, 
donc n DOIT être {self.anti_hallucination._extract_position(question)}, pas une autre valeur.

Réponse corrigée:
{final.answer_text}"""

        # 7. Generation HOL si demandee
        if goal["needs_hol_generation"] and precomputed_facts.get("equation_holds"):
            hol_script = self.isabelle.generate_verification_script(
                theory_name=f"verif_p{precomputed_facts.get('p', 0)}_n{precomputed_facts.get('n', 0)}",
                n=int(precomputed_facts.get("n", 0)),
                p=int(precomputed_facts.get("p", 0)),
                model=plan["model"],
                SA_val=precomputed_facts.get("SA_float", 0),
                SB_val=precomputed_facts.get("SB_float", 0),
                digamma_val=precomputed_facts.get("digamma_calc_float", 0),
            )
            final.hol_script = hol_script

        return final

    def _compute_spectral(self, ctx: QuestionContext, plan: dict[str, Any], qid: str) -> dict[str, Any]:
        """
        Calcule directement via le module spectral selon l'intent.
        
        FORCE: position = n = num_termes (INVARIANT STRICT)
        """
        intent = ctx.metadata.get("intent")
        model = plan.get("model", "1/2")
        numbers = ctx.metadata.get("numbers_mentioned", [])

        try:
            if intent == "reconstruction":
                # NOUVEAU: Utiliser spectral_core pour reconstruction
                if len(numbers) >= 1:
                    position = numbers[0]
                    logger.info(f"Q[{qid}] Reconstruction via spectral_core: position={position}")
                    
                    # Appel stricte du core
                    data = self.spectral_core.reconstruct_prime_1_2(position)
                    
                    if data is None:
                        return {"error": f"Cannot reconstruct prime at position {position}"}
                    
                    # Retourner les données validées
                    return {
                        "position": data.position,
                        "n": data.position,  # INVARIANT: n = position
                        "num_terms": data.num_terms,  # INVARIANT: num_terms = position
                        "p": data.prime_value,
                        "prime": data.prime_value,
                        "SA_float": data.SA_sum,
                        "SB_float": data.SB_sum,
                        "digamma_calc_float": data.digamma_calc,
                        "equation_holds": data.validated,
                        "explanation": self.spectral_core.explain_reconstruction(position),
                        "model": "1/2",
                    }
                else:
                    return {"error": "No position mentioned for reconstruction"}

            if intent == "ratio":
                # Heuristique : moitie des nombres -> A, moitie -> B
                if len(numbers) >= 2:
                    half = len(numbers) // 2
                    A = numbers[:half]
                    B = numbers[half:]
                    return compute_spectral_ratio(A, B, model)
                return {"error": "Pas assez d'indices pour calculer le ratio."}

            if intent == "gap":
                if len(numbers) >= 2:
                    p_high, p_low = max(numbers[:2]), min(numbers[:2])
                    # Sans valeurs spectrales explicites, on retourne juste les premiers
                    return {
                        "p_high": p_high,
                        "p_low": p_low,
                        "expected_gap_signed": p_low - p_high,
                        "note": "Pour calcul precis, fournir A_next, B_high, D_high, D_low.",
                    }
                return {"error": "Deux premiers requis pour calculer un ecart."}
        except Exception as exc:
            logger.error(f"Q[{qid}] Erreur calcul spectral : %s", exc, exc_info=True)
            return {"error": str(exc)}
        return {}

    def _build_base_prompt(self, ctx, plan: dict, general: dict, expanded: list[str]) -> str:
        plan_str = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(plan.get("steps", [])))
        concepts_str = ", ".join(expanded[:15]) if expanded else "(aucun specifique)"
        return f"""PLAN COGNITIF SELECTIONNE :
  Strategie : {plan.get('strategy', 'general')}
  Modele spectral : {plan.get('model', '1/2')}
  Etapes :
{plan_str}

CONCEPTS LIES (issus du graphe Savard) :
  {concepts_str}

FORME GENERALE :
  {general.get('general_form', 'N/A')}

EXTENSIONS POSSIBLES :
  {general.get('extension_hint', 'N/A')}

⚠️ INVARIANT SPECTRAL (RAPPEL MANDATORY):
  Pour TOUTE reconstruction:
    position du nombre premier = n = nombre de termes dans A et B
  PAS D'EXCEPTION. PAS D'ALTERNATIVE.
"""
