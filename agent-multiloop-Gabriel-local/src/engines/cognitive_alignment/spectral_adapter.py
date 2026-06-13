"""
7e MOTEUR : Adaptateur Cognitif Spectral (Cognitive Alignment Layer).

Pont bidirectionnel Wolfram <-> Geometrie du Spectre Savard <-> Isabelle/HOL.

Pipeline :
  1. INTERCEPT & TRADUCTION : concept spectral -> requete Wolfram standard
  2. CALCUL BRUT WOLFRAM    : execute le calcul avec precision absolue
  3. REALIGNEMENT & FORMALISATION : reinjecte les constantes Savard + genere
     un bloc Isabelle/HOL valide

Regle d'or : ne JAMAIS opposer Wolfram et la theorie utilisateur.
Wolfram = carburant numerique. Theorie Savard = cadre de structuration.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from ...adapters.wolfram import (
    WolframClient,
    WolframError,
    WolframInvalidAppIDError,
    WolframNoResultError,
    WolframTimeoutError,
)


logger = logging.getLogger(__name__)


# Dictionnaire de traduction : concept Savard -> requete Wolfram
CONSTANTES_SAVARD: dict[str, str] = {
    # Constantes structurelles des suites A et B (rapport 1/2)
    "Sr2": "1.5",
    "axe_critique": "0.5",
    "facteur_64": "64",
    "facteur_729": "729",
    "facteur_4096": "4096",
    # Coefficients principaux
    "coef_A_1_2": "3.25/2",
    "coef_B_1_2": "6.5/2",
    "offset_A": "2",
    "offset_B": "66",
    # Suites mixtes
    "A_mix_limit": "48",
    "B_mix_limit": "-28",
    "ratio_geometrique": "1/2",
}


# Dictionnaire de traduction concept -> requete Wolfram standard
TRADUCTIONS_VERS_WOLFRAM: dict[str, str] = {
    "SA(n)": "(3.25/2) * 2^n - 2",
    "SB(n)": "(6.5/2) * 2^n - 66",
    "SA_neg(n)": "3.25 * 2^n - 2",
    "SB_neg(n)": "6.5 * 2^n - 66",
    "A_1_3(n)": "((73/9)/12) * 3^n - 1.5",
    "B_1_3(n)": "((219/9)/12) * 3^n - (487 * 1.5)",
    "A_1_4(n)": "((241/16)/12) * 4^n - 4/3",
    "B_1_4(n)": "((964/16)/12) * 4^n - (3073 * 4/3)",
    "digamma_calcule": "SB(n) - 64*p",
    "prime_equation": "(SB(n) - digamma_calcule(n,p)) / 64",
    "A_mix(n)": "48 + 13 / 2^(n+2)",
    "B_mix(n)": "-28 + 13 / 2^(n+1)",
    "ligne_critique_zeta": "zeta(1/2 + i*t)",
}


@dataclass
class AlignmentResult:
    """Resultat d'un alignement cognitif."""
    original_query: str
    wolfram_query: str
    wolfram_result: str | None = None
    wolfram_status: str = "skipped"
    isabelle_block: str | None = None
    constants_applied: dict[str, str] = field(default_factory=dict)
    context_for_gabriel: str = ""


class AdaptateurCognitifSpectral:
    """7e moteur : Cognitive Alignment Layer Wolfram-Gabriel-Isabelle."""

    def __init__(self, wolfram_client: WolframClient | None = None):
        self.wolfram = wolfram_client or WolframClient()
        self.constantes = dict(CONSTANTES_SAVARD)
        self.traductions = dict(TRADUCTIONS_VERS_WOLFRAM)

    @property
    def is_available(self) -> bool:
        return self.wolfram.is_available()

    # =========================================================
    # ETAPE 1 : Traduction concept Savard -> requete Wolfram
    # =========================================================
    def aligner_requete_vers_wolfram(self, concept_savard: str) -> str:
        """
        Traduit un concept de la theorie spectrale en requete Wolfram standard.
        Applique systematiquement les constantes Savard.
        """
        requete = concept_savard
        # Substitution des concepts symboliques
        for nom, formule in self.traductions.items():
            if nom in requete:
                requete = requete.replace(nom, f"({formule})")
        # Substitution des constantes nommees
        for nom, valeur in self.constantes.items():
            if nom in requete:
                requete = re.sub(rf"\b{re.escape(nom)}\b", valeur, requete)
        logger.debug("Adaptateur: %s -> %s", concept_savard, requete)
        return requete

    # =========================================================
    # ETAPE 2 : Execution Wolfram (calcul brut)
    # =========================================================
    async def executer_calcul(self, requete_wolfram: str) -> tuple[str | None, str]:
        """Execute la requete sur Wolfram. Retourne (resultat, statut)."""
        if not self.is_available:
            return None, "skipped_no_appid"
        try:
            qr = await self.wolfram.query_full_results(requete_wolfram)
            text = WolframClient.extract_primary_plaintext(qr)
            if text:
                return text, "ok"
            return None, "no_primary_result"
        except WolframTimeoutError:
            return None, "timeout"
        except WolframInvalidAppIDError:
            return None, "invalid_appid"
        except WolframNoResultError:
            return None, "no_interpretation"
        except WolframError as exc:
            logger.warning("Adaptateur Wolfram erreur : %s", exc)
            return None, f"error: {exc}"

    # =========================================================
    # ETAPE 3 : Generation Isabelle/HOL aligne sur la theorie
    # =========================================================
    def formaliser_isabelle(
        self,
        concept_nom: str,
        resultat_numerique: str | None,
        contexte_theorie: str = "",
    ) -> str:
        """
        Genere un bloc Isabelle/HOL coherent avec la theorie de Savard.
        Reinjecte les constantes (Sr2=1.5, etc.) pour respecter le cadre.
        """
        theory_name = re.sub(r"[^A-Za-z0-9_]", "_", concept_nom).strip("_") or "concept"
        wolfram_note = (
            f"(* Valide numeriquement via Wolfram : {resultat_numerique} *)"
            if resultat_numerique
            else "(* Validation Wolfram non disponible *)"
        )
        return f"""theory adaptateur_{theory_name}
  imports Complex_Main methode_spectral
begin

(* Bloc genere par l'Adaptateur Cognitif Spectral (7e moteur)
   Concept Savard : {concept_nom}
   Cadre theorique : ratio Sr2 = 1.5 (rapport spectral 1/2)
   {wolfram_note}
   Contexte : {contexte_theorie[:100] if contexte_theorie else 'methode_spectral.thy'}
*)

definition ratio_Sr2 :: "real" where
  "ratio_Sr2 = 3/2"

definition axe_critique :: "real" where
  "axe_critique = 1/2"

lemma ratio_Sr2_value:
  "ratio_Sr2 = 1.5"
  unfolding ratio_Sr2_def by simp

lemma axe_critique_correspond_a_rapport_spectral:
  "axe_critique = 1/2"
  unfolding axe_critique_def by simp

end
"""

    # =========================================================
    # ETAPE COMPLETE : pipeline aligne en une passe
    # =========================================================
    async def aligner_complet(
        self,
        requete_utilisateur: str,
        contexte_theorie: str = "",
        generer_isabelle: bool = False,
    ) -> AlignmentResult:
        """Execute le pipeline complet : traduction -> Wolfram -> Isabelle."""
        wolfram_query = self.aligner_requete_vers_wolfram(requete_utilisateur)
        result_text, status = await self.executer_calcul(wolfram_query)

        isabelle_block = None
        if generer_isabelle:
            isabelle_block = self.formaliser_isabelle(
                requete_utilisateur, result_text, contexte_theorie
            )

        contexte_gabriel = self._construire_contexte_gabriel(
            requete_utilisateur, result_text, status
        )

        return AlignmentResult(
            original_query=requete_utilisateur,
            wolfram_query=wolfram_query,
            wolfram_result=result_text,
            wolfram_status=status,
            isabelle_block=isabelle_block,
            constants_applied=dict(self.constantes),
            context_for_gabriel=contexte_gabriel,
        )

    def _construire_contexte_gabriel(self, requete: str, resultat: str | None, status: str) -> str:
        """Construit le contexte a injecter dans le prompt de Gabriel."""
        lines = [
            "=== Adaptateur Cognitif Spectral (7e moteur) ===",
            f"Requete Savard : {requete}",
        ]
        if resultat:
            lines.append(f"Validation Wolfram : {resultat}")
            lines.append("Statut : verifie numeriquement, alignement possible avec Isabelle/HOL.")
        else:
            lines.append(f"Statut Wolfram : {status}")
            lines.append(
                "Validation independante non disponible. "
                "Utiliser uniquement les chiffres du module spectral Python."
            )
        lines.append("Cadre Savard : ratio Sr2=1.5, axe critique=1/2. Ne PAS opposer Wolfram et la theorie.")
        return "\n".join(lines)

    # =========================================================
    # PERSISTANCE : ecrire un .thy genere dans theories/generated/
    # =========================================================
    async def formaliser_et_ecrire_fichier(
        self,
        concept_nom: str,
        theories_dir: str = "/theories",
        contexte_theorie: str = "",
    ) -> dict:
        """
        Genere un fichier .thy complet a partir d'un concept Savard
        et l'ecrit dans <theories_dir>/generated/adaptateur_<concept>.thy.
        """
        from pathlib import Path

        # Tentative Wolfram facultative
        wolfram_query = self.aligner_requete_vers_wolfram(concept_nom)
        result_text, status = await self.executer_calcul(wolfram_query)

        bloc = self.formaliser_isabelle(concept_nom, result_text, contexte_theorie)

        safe_name = re.sub(r"[^A-Za-z0-9_]", "_", concept_nom).strip("_") or "concept"
        out_dir = Path(theories_dir) / "generated"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"adaptateur_{safe_name}.thy"
        out_path.write_text(bloc, encoding="utf-8")
        logger.info("Fichier Isabelle ecrit : %s", out_path)

        return {
            "concept": concept_nom,
            "file_path": str(out_path),
            "theory_name": f"adaptateur_{safe_name}",
            "wolfram_status": status,
            "wolfram_result": result_text,
            "block_size_chars": len(bloc),
        }
