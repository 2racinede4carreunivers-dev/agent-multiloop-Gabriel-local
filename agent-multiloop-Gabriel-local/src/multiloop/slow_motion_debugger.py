"""
SlowMotionDebugger — Mode "ralenti debugger" anti-incoherence.

Activation automatique :
  Le CoherenceDetector trouve une incoherence (score < seuil) dans la
  sortie du multiloop. Le pipeline appelle alors ce module.

Procedure (timeline) :
  T1. Reception de la requete originale et du rapport d'incoherence
  T2. Decomposition de la requete en segments logiques (RequestDecomposer)
  T3. Identification des segments coherents (✓) et incoherents (✗)
  T4. By-pass des segments ✗
  T5. Reconstruction d'une requete canonique simplifiee (Rewriter)
  T6. Resolution via CertaintyKernel + spectral_core (PAS DE LLM)
  T7. Construction d'une reponse courte mais CERTAINE
  T8. Generation de la timeline traçable + suggestions de reformulation

L'utilisateur recoit :
  - La reponse certifiee (courte)
  - La timeline complete (transparence totale)
  - Une suggestion de reformulation s'il veut plus de details
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from ..adapters.corpus.certainty_kernel import CertaintyKernel
from ..audit import AuditStore
from ..core.spectral_core import SpectralMethodCore
from ..core.types import FinalAnswer
from ..spectral.prime_table import nth_prime
from .coherence_detector import CoherenceReport
from .request_decomposer import DecomposedRequest, RequestDecomposer, Segment


logger = logging.getLogger(__name__)


@dataclass
class TimelineEvent:
    step: int
    label: str
    detail: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class DebugTimeline:
    events: list[TimelineEvent] = field(default_factory=list)

    def add(self, step: int, label: str, detail: str) -> None:
        self.events.append(TimelineEvent(step=step, label=label, detail=detail))

    def render(self) -> str:
        """Rendu ASCII de la timeline pour affichage CLI."""
        if not self.events:
            return "(timeline vide)"
        lines = ["TIMELINE DEBUGGER (mode ralenti)"]
        lines.append("─" * 60)
        for ev in self.events:
            lines.append(f"  T{ev.step:<2} [{ev.label:<22}] {ev.detail}")
        lines.append("─" * 60)
        return "\n".join(lines)

    def to_dict(self) -> list[dict]:
        return [
            {"step": ev.step, "label": ev.label, "detail": ev.detail, "ts": ev.timestamp}
            for ev in self.events
        ]


class SlowMotionDebugger:
    """
    Mode debugger ralenti avec by-pass des segments incoherents et
    repli sur le CertaintyKernel.
    """

    def __init__(
        self,
        certainty_kernel: Optional[CertaintyKernel] = None,
        spectral_core: Optional[SpectralMethodCore] = None,
        audit_store: Optional[AuditStore] = None,
    ):
        self.kernel = certainty_kernel or CertaintyKernel()
        self.core = spectral_core or SpectralMethodCore()
        self.decomposer = RequestDecomposer()
        self.audit_store = audit_store  # peut etre None -> pas d'audit auto
        logger.info(
            "SlowMotionDebugger initialise : %d certitudes, %d premiers en table, audit=%s",
            len(self.kernel.certainties), len(self.core.prime_list),
            "ON" if self.audit_store else "OFF",
        )

    def debug(
        self,
        question: str,
        final: FinalAnswer,
        coherence_report: CoherenceReport,
        precomputed_facts: Optional[dict[str, Any]] = None,
        skip_auto_audit: bool = False,
    ) -> FinalAnswer:
        """
        Execute la procedure complete du Slow-Motion Debugger.
        
        Args:
            question: la requete originale.
            final: la FinalAnswer multiloop jugee incoherente.
            coherence_report: le diagnostic du CoherenceDetector.
            precomputed_facts: facts spectraux deja calcules par le pipeline.
        
        Returns:
            FinalAnswer enrichie : answer_text = reponse certifiee,
            structured_data inclut la timeline + segments + reformulations.
        """
        timeline = DebugTimeline()
        timeline.add(1, "REQUETE_RECUE", f'"{question[:80]}"')
        timeline.add(2, "INCOHERENCE_DETECTEE",
                     f"score={coherence_report.score:.2f}, "
                     f"signaux={coherence_report.signals[:3]}")

        # T3. Decomposition
        decomposed = self.decomposer.decompose(question)
        coherent_str = ", ".join(f"{s.kind}={s.value}" for s in decomposed.coherent_segments)
        incoherent_str = ", ".join(f"{s.kind}={s.value}" for s in decomposed.incoherent_segments)
        timeline.add(3, "DECOMPOSITION",
                     f"intent={decomposed.detected_intent} "
                     f"ratio={decomposed.detected_ratio} "
                     f"coherents=[{coherent_str}] incoherents=[{incoherent_str}]")

        # T4. By-pass
        bypassed = [s for s in decomposed.incoherent_segments]
        if bypassed:
            timeline.add(4, "BYPASS_SEGMENTS",
                         f"ignores : {[s.text for s in bypassed]} "
                         f"(raisons : {[s.reason for s in bypassed]})")
        else:
            timeline.add(4, "BYPASS_SEGMENTS", "aucun segment a ignorer")

        # T5. Requete canonique
        canonical = self._rewrite_canonical(decomposed)
        timeline.add(5, "REQUETE_CANONIQUE", canonical)

        # T6. Resolution certifiee (sans LLM)
        certified = self._solve_certified(decomposed)
        timeline.add(6, "RESOLUTION_CERTIFIEE", certified["summary"])

        # T7. Reponse courte + reformulations
        suggestions = self._build_reformulations(decomposed, bypassed)
        if suggestions:
            timeline.add(7, "REFORMULATIONS",
                         " | ".join(f'"{s}"' for s in suggestions[:2]))
        else:
            timeline.add(7, "REFORMULATIONS", "aucune suggestion necessaire")

        # T8. Reponse finale construite
        answer_text = self._render_answer(
            question=question,
            decomposed=decomposed,
            bypassed=bypassed,
            certified=certified,
            suggestions=suggestions,
            timeline=timeline,
        )
        timeline.add(8, "REPONSE_CERTIFIEE", f"{len(answer_text)} caracteres produits")

        # Enrichir la FinalAnswer
        final.answer_text = answer_text
        final.confidence = 1.0  # CERTAIN car derive du kernel
        final.structured_data = dict(final.structured_data or {})
        final.structured_data.update({
            "slow_motion_triggered": True,
            "coherence_score": coherence_report.score,
            "coherence_signals": coherence_report.signals,
            "decomposition": {
                "intent": decomposed.detected_intent,
                "ratio": decomposed.detected_ratio,
                "coherent_segments": [
                    {"kind": s.kind, "value": s.value, "text": s.text}
                    for s in decomposed.coherent_segments
                ],
                "incoherent_segments": [
                    {"kind": s.kind, "value": s.value, "text": s.text, "reason": s.reason}
                    for s in decomposed.incoherent_segments
                ],
            },
            "canonical_request": canonical,
            "certified": certified,
            "reformulations": suggestions,
            "debug_timeline": timeline.to_dict(),
        })

        # NOUVEAU : sauvegarde automatique d'audit pour le rapport 1/2
        if not skip_auto_audit:
            self._maybe_save_audit(
                intervention_type="slow_motion_auto",
                question=question,
                final=final,
                decomposed=decomposed,
                certified=certified,
                timeline=timeline,
            )
        return final

    def _maybe_save_audit(
        self,
        intervention_type: str,
        question: str,
        final: FinalAnswer,
        decomposed: DecomposedRequest,
        certified: dict[str, Any],
        timeline: DebugTimeline,
        user_comment: Optional[str] = None,
        forced_bypass: Optional[list[str]] = None,
        toolkit_reports: Optional[dict[str, Any]] = None,
    ) -> None:
        """Sauvegarde un audit JSON signe SI rapport=1/2 et audit_store dispo."""
        if self.audit_store is None:
            return
        # Periode strict : rapport 1/2 uniquement
        ratio = decomposed.detected_ratio or "1/2"
        if ratio != "1/2":
            logger.debug("Audit saute : rapport %s non supporte (v1 = 1/2 only)", ratio)
            return
        position = None
        for s in decomposed.coherent_segments:
            if s.kind == "position":
                position = s.value
                break
        try:
            record = AuditStore.build_record(
                intervention_type=intervention_type,
                question=question,
                certified_answer=final.answer_text,
                position=position,
                prime_value=certified.get("value"),
                decomposition=final.structured_data.get("decomposition", {}),
                timeline=timeline.to_dict(),
                citations_thy=certified.get("citations", []),
                toolkit_reports=toolkit_reports or {},
                user_comment=user_comment,
                forced_bypass=forced_bypass or [],
                ratio="1/2",
            )
            path = self.audit_store.save(record)
            final.structured_data["audit_id"] = record.id
            final.structured_data["audit_path"] = str(path)
            logger.info("Audit cree : id=%s path=%s", record.id, path.name)
        except Exception as exc:
            logger.error("Echec sauvegarde audit : %s", exc, exc_info=True)

    # ---------- Etapes internes ----------

    def _rewrite_canonical(self, dec: DecomposedRequest) -> str:
        """Reconstruit une requete canonique a partir des segments coherents."""
        # Cas reconstruction : intent + position + ratio
        position = None
        for s in dec.coherent_segments:
            if s.kind == "position":
                position = s.value
                break

        if dec.detected_intent == "reconstruction" and position is not None:
            ratio = dec.detected_ratio or "1/2"
            return f"Reconstruire le {position}-eme nombre premier en rapport {ratio}"

        if dec.detected_intent == "ratio" and dec.detected_ratio:
            return f"Calculer le rapport spectral {dec.detected_ratio}"

        if dec.detected_intent == "gap":
            nums = [s.value for s in dec.coherent_segments if s.kind == "number"]
            if len(nums) >= 2:
                return f"Calculer l'ecart spectral entre {nums[0]} et {nums[1]}"

        # Fallback : on resume ce qu'on a compris
        return f"(intent={dec.detected_intent}, ratio={dec.detected_ratio}, "\
               f"segments={[s.value for s in dec.coherent_segments]})"

    def _solve_certified(self, dec: DecomposedRequest) -> dict[str, Any]:
        """
        Resolution sans LLM, uniquement via spectral_core + kernel.
        Retourne un dict avec 'summary', 'value', 'citations'.
        """
        position = None
        for s in dec.coherent_segments:
            if s.kind == "position":
                position = s.value
                break

        # Cas principal : reconstruction du N-ieme premier en rapport 1/2
        if dec.detected_intent == "reconstruction" and position is not None:
            ratio = dec.detected_ratio or "1/2"
            if ratio == "1/2":
                # Lookup table
                p = nth_prime(position)
                # Calcul spectral via core
                data = self.core.reconstruct_prime_1_2(position)
                citations = []
                for key in [
                    "KERNEL_INVARIANT_RECONSTRUCTION_1_2",
                    "KERNEL_INVARIANT_Z_64",
                    "INVARIANT_1_2",
                ]:
                    cert = self.kernel.get(key)
                    if cert:
                        citations.append(cert.cite())
                if data is not None:
                    summary = (
                        f"Le {position}-eme nombre premier est {p}. "
                        f"En rapport 1/2, n = {position} (INVARIANT). "
                        f"Termes dans A et B : {position}."
                    )
                    return {
                        "summary": summary,
                        "value": p,
                        "n": position,
                        "num_terms": position,
                        "SA": data.SA_sum,
                        "SB": data.SB_sum,
                        "digamma_calc": data.digamma_calc,
                        "citations": citations,
                        "method": "spectral_core.reconstruct_prime_1_2 + KERNEL",
                    }
                return {
                    "summary": f"Position {position} hors table. Reponse impossible avec certitude.",
                    "value": None, "citations": citations,
                    "method": "kernel_only",
                }
            # rapports 1/3, 1/4 : on retourne le prime + invariants
            p = nth_prime(position)
            certs = [self.kernel.get("RULE_n_1_3") if ratio == "1/3" else self.kernel.get("RULE_n_1_4")]
            return {
                "summary": (
                    f"Le {position}-eme nombre premier est {p}. "
                    f"En rapport {ratio}, n est le nombre de termes "
                    f"(distinct de la position). Demandez la valeur de n separement."
                ),
                "value": p,
                "n": None,
                "citations": [c.cite() for c in certs if c],
                "method": "kernel + nth_prime",
            }

        # Cas inconnu : on retourne le resume d'urgence du domaine probable
        domain = "ratio_1_2"
        if dec.detected_ratio == "1/3":
            domain = "ratio_1_3"
        elif dec.detected_ratio == "1/4":
            domain = "ratio_1_4"
        summary_block = self.kernel.emergency_summary(domain)
        return {
            "summary": "Requete non resolvable directement par le kernel. "
                       "Voici le resume certifie du domaine concerne.",
            "value": None,
            "citations": [summary_block],
            "method": "kernel_emergency_summary",
        }

    @staticmethod
    def _build_reformulations(dec: DecomposedRequest, bypassed: list[Segment]) -> list[str]:
        """Propose des reformulations courtes pour aider l'utilisateur."""
        suggestions: list[str] = []
        if not bypassed:
            return suggestions
        position = None
        for s in dec.coherent_segments:
            if s.kind == "position":
                position = s.value
                break
        ratio = dec.detected_ratio or "1/2"
        if position:
            suggestions.append(
                f"Reconstruire le {position}-eme premier en rapport {ratio}"
            )
            if ratio == "1/2":
                suggestions.append(
                    f"Quel est le {position}-eme nombre premier et combien de termes "
                    f"dans A et B pour le reconstituer ?"
                )
        return suggestions

    @staticmethod
    def _render_answer(
        question: str,
        decomposed: DecomposedRequest,
        bypassed: list[Segment],
        certified: dict[str, Any],
        suggestions: list[str],
        timeline: DebugTimeline,
    ) -> str:
        """Assemble la reponse finale pour l'utilisateur."""
        parts: list[str] = []
        parts.append("REPONSE CERTIFIEE (mode debugger ralenti)")
        parts.append("=" * 60)
        parts.append("")
        parts.append(certified["summary"])
        parts.append("")

        if bypassed:
            parts.append("Segments ignores (potentiellement incoherents) :")
            for s in bypassed:
                parts.append(f"  ✗ {s.text} — {s.reason}")
            parts.append("")

        if certified.get("citations"):
            parts.append("Sources de certitude :")
            for cit in certified["citations"]:
                parts.append(f"  • {cit}")
            parts.append("")

        if suggestions:
            parts.append("Suggestions de reformulation plus precises :")
            for s in suggestions:
                parts.append(f"  → {s}")
            parts.append("")

        parts.append(timeline.render())
        return "\n".join(parts)
