"""
Pipeline CORRIGÉ avec intégration de la 7ème loop auto-trigger.

Changements:
  1. Ajout de SlowMotionTrigger dans __init__
  2. Avant d'exécuter refinement: appeler trigger.should_trigger_7_loop()
  3. Si True: lancer le debugger immediatement
  4. Sinon: exécution normale du multiloop
  5. Après slow-motion: proposer sauvegarde de la timeline en DB
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
from ..multiloop import (
    Critic,
    RefinementLoop,
    SilentAuditLoop,
    CoherenceDetector,
    SlowMotionDebugger,
    AutomaticVerificationLoop,
)
from ..multiloop.slowmotion_trigger import SlowMotionTrigger
from ..adapters.corpus.certainty_kernel import CertaintyKernel
from ..audit import AuditStore
from ..spectral import (
    PRIMES,
    compute_gap,
    compute_spectral_ratio,
    is_known_prime,
    nth_prime,
    prime_position,
    verify_prime_equation,
)
from .spectral_core import (
    SpectralMethodCore,
    AntiHallucinationValidator,
    SpectralRatio,
)


logger = logging.getLogger(__name__)


class Pipeline:
    """Pipeline complet du Multi-Loop Agent avec 7ème loop auto-trigger."""

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
        self.verifier = NumericalVerifier()
        self.corpus = TheoryLoader(config.get("data", {}).get("hol_dir", "/theories"))
        self.corpus.load_all()
        
        # Spectral + audit
        self.spectral_core = SpectralMethodCore()
        self.anti_hallucination = AntiHallucinationValidator()
        self.silent_audit = SilentAuditLoop(self.llm, config)
        
        # Slow-motion core
        slowmo_cfg = config.get("slow_motion", {}) if config else {}
        self.slowmo_enabled = bool(slowmo_cfg.get("enabled", True))
        coherence_threshold = float(slowmo_cfg.get("coherence_threshold", 0.55))
        theories_dir = config.get("data", {}).get("hol_dir", "/theories")
        self.certainty_kernel = CertaintyKernel(theories_dir=theories_dir)
        self.coherence_detector = CoherenceDetector(threshold=coherence_threshold)
        
        # Audit store
        audit_dir = config.get("data", {}).get("audit_dir", "/home/agent/app/data/audits")
        self.audit_store = AuditStore(base_dir=audit_dir)
        
        # Slow-Motion Debugger
        self.slow_motion = SlowMotionDebugger(
            certainty_kernel=self.certainty_kernel,
            spectral_core=self.spectral_core,
            audit_store=self.audit_store,
        )
        
        # NOUVEAU: Trigger de la 7ème loop
        self.slowmotion_trigger = SlowMotionTrigger(
            slow_motion_debugger=self.slow_motion,
            coherence_detector=self.coherence_detector,
        )
        
        # Verification loop
        self.verification_loop = AutomaticVerificationLoop(
            config=config,
            spectral_core=self.spectral_core,
            audit_store=self.audit_store,
        )
        
        logger.info("✓ Pipeline initialized with SpectralMethodCore (INVARIANT: n=position=num_termes)")
        logger.info("✓ Silent Audit Loop enabled: %s (max_retries=%d)",
                    self.silent_audit.enabled, self.silent_audit.max_retries)
        logger.info("✓ Slow-Motion Debugger enabled: %s (coherence_threshold=%.2f, %d certitudes)",
                    self.slowmo_enabled, coherence_threshold,
                    len(self.certainty_kernel.certainties))
        logger.info("✓ SlowMotionTrigger active : 7ème loop auto-déclenchable")

    async def process(self, question: str, previous_answer: FinalAnswer | None = None) -> FinalAnswer:
        """
        Traite une question end-to-end via le pipeline.
        
        Si la question déclenche la 7ème loop, exécute le SlowMotionDebugger
        avant le multiloop standard.
        """
        qid = uuid.uuid4().hex[:8]
        
        # NOUVEAU: Vérifier si c'est une demande de 7ème loop
        if self.slowmotion_trigger.should_trigger_7_loop(question, previous_answer):
            if previous_answer is not None:
                # On a une reponse precedente jugee incoherente
                # Creer un contexte pour la question precedente
                ctx = QuestionContext(
                    question_id=qid,
                    raw_question=question,
                )
                logger.info("Q[%s] 7ème loop auto-déclenchée", qid)
                
                # Declencher le debugger
                final = await self.slowmotion_trigger.trigger(
                    question=question,
                    previous_answer=previous_answer,
                    ctx=ctx,
                    precomputed_facts=previous_answer.structured_data,
                )
                
                return final
        
        # SINON: workflow standard
        ctx = self.abstraction.abstract(qid, question)
        logger.info("Q[%s] domain=%s model=%s intent=%s", qid, ctx.detected_domain, ctx.detected_model, ctx.metadata.get("intent"))

        goal = self.goal_analyzer.analyze(ctx)
        strategy = self.strategy_selector.select(ctx, goal)
        plan = self.proof_planner.plan(ctx, goal, strategy)

        concept_names = [c.name for c in ctx.concepts]
        expanded = self.navigator.expand_concepts(concept_names)

        precomputed_facts: dict[str, Any] = {}
        if goal["needs_computation"]:
            precomputed_facts = self._compute_spectral(ctx, plan, qid)
            logger.info("Q[%s] calculs spectraux directs : %s", qid, list(precomputed_facts.keys())[:5])

            if self.verifier.is_available and goal["intent"] == "reconstruction":
                p_val = precomputed_facts.get("p")
                if isinstance(p_val, int):
                    wolfram_check = await self.verifier.verify_prime(p_val)
                    precomputed_facts["wolfram_verification"] = wolfram_check
                    logger.info("Q[%s] Wolfram check: %s", qid, wolfram_check.get("outcome"))

        general = self.generalizer.generalize(
            precomputed_facts,
            {
                "intent": goal["intent"],
                "model": plan["model"],
                "question": question,
            },
        )

        base_prompt = self._build_base_prompt(ctx, plan, general, expanded)
        final = await self.refinement.run(ctx, precomputed_facts, base_prompt)
        
        # Detection d'incoherence post-multiloop
        if self.slowmo_enabled:
            coherence = self.coherence_detector.evaluate(
                question=question,
                candidates=final.candidates or [],
                best_answer_text=final.answer_text,
                precomputed_facts=precomputed_facts,
            )
            logger.info("Q[%s] coherence=%.2f signals=%s",
                        qid, coherence.score, coherence.signals[:3])
            if coherence.incoherent:
                logger.warning("Q[%s] INCOHERENCE => Slow-Motion Debugger active", qid)
                final = self.slow_motion.debug(
                    question=question,
                    final=final,
                    coherence_report=coherence,
                    precomputed_facts=precomputed_facts,
                )
                return final
        
        # Audit silencieux post-pipeline
        final = await self.silent_audit.audit_and_correct(
            question=question,
            final=final,
            precomputed_facts=precomputed_facts,
        )

        # Generation HOL si demandée
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
        """Calcule directement via le module spectral selon l'intent."""
        intent = ctx.metadata.get("intent")
        model = plan.get("model", "1/2")
        numbers = ctx.metadata.get("numbers_mentioned", [])
        question_low = ctx.raw_question.lower()

        try:
            if intent == "reconstruction":
                n: int | None = None
                p: int | None = None

                position_kw = any(kw in question_low for kw in [
                    "ieme premier", "ième premier", "eme premier", "ème premier",
                    "n-ieme", "n-ième", "neme nombre", "n ieme", "n ième",
                    "position", "rang",
                ])

                if position_kw and len(numbers) >= 1:
                    candidate_n = numbers[0]
                    p_lookup = nth_prime(candidate_n)
                    if p_lookup is not None:
                        n = candidate_n
                        p = p_lookup if model == "1/2" else p_lookup
                elif len(numbers) >= 2:
                    n, p = numbers[0], numbers[1]
                elif len(numbers) == 1:
                    num = numbers[0]
                    if is_known_prime(num):
                        p = num
                        n = prime_position(num) if model == "1/2" else None
                        if n is None:
                            n = 10
                    else:
                        p_lookup = nth_prime(num)
                        if p_lookup:
                            n = num
                            p = p_lookup

                if n is None or p is None:
                    return {
                        "error": "Question ambigue. Precisez : 'le N-ieme premier' OU 'le premier P avec n=X'.",
                        "hint": "Exemple : 'reconstruis le 26eme premier' ou 'p=29 et n=10 modele 1/2'.",
                    }

                if len(numbers) >= 1:
                    position = numbers[0]
                    logger.info(f"Q[{qid}] Reconstruction via spectral_core: position={position}")
                    
                    data = self.spectral_core.reconstruct_prime_1_2(position)
                    
                    if data is None:
                        return {"error": f"Cannot reconstruct prime at position {position}"}
                    
                    return {
                        "position": data.position,
                        "n": data.position,
                        "num_terms": data.num_terms,
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
                    return {"error": "Aucun nombre mentionne pour reconstruction."}

            if intent == "ratio":
                if len(numbers) >= 2:
                    half = len(numbers) // 2
                    A = numbers[:half]
                    B = numbers[half:]
                    return compute_spectral_ratio(A, B, model)
                return {"error": "Pas assez d'indices pour calculer le ratio."}

            if intent == "gap":
                if len(numbers) >= 2:
                    p_high, p_low = max(numbers[:2]), min(numbers[:2])
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
