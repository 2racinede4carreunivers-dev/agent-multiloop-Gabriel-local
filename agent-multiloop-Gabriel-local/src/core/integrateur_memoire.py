"""Integrateur Memoire Gabriel - pont vers le RAG officiel `memory/`.

Ce module satisfait l'import `from integrateur_memoire import IntegrateurMemoireGabriel`
dans `src/core/llm_manager.py` (ligne 34). Il delegue toute la logique au module RAG
officiel `memory/adaptateur_cognitif_rag.py` qui contient :
  - le Dictionnaire Spectral (12 regimes dont XI/XII)
  - l'AdaptateurCognitifSpectral (detection regex + construction prompt)
  - Section XI (suites 8+ termes) et Section XII (1/k_i parametrique)

API exposee : IntegrateurMemoireGabriel().augmenter_prompt(prompt, domaine) -> str
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Permet d'importer `memory.*` quand on charge l'agent depuis /home/agent/app/
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


class IntegrateurMemoireGabriel:
    """Pont vers AdaptateurCognitifSpectral (RAG officiel).

    Initialise au demarrage du LLM Manager, augmente chaque prompt LLM avec
    le contexte spectral pertinent (regimes detectes, lemmes, regles, avertissements).
    """

    def __init__(self) -> None:
        try:
            from memory.adaptateur_cognitif_rag import AdaptateurCognitifSpectral
            from memory.dictionnaire_spectral import regime_count, total_lemmes
        except ImportError as exc:
            raise ImportError(
                f"Module RAG 'memory/' introuvable. Verifiez que le dossier "
                f"agent-multiloop-Gabriel-local/memory/ est present. Erreur: {exc}"
            ) from exc

        self._adaptateur = AdaptateurCognitifSpectral()
        self._regime_count = regime_count()
        self._total_lemmes = total_lemmes()

        # Optionnel : charger les sections XI et XII si presentes
        self._sections_extra = []
        for sec_name in ("methode_spectral_section_XI", "methode_spectral_section_XII"):
            try:
                module = __import__(f"memory.{sec_name}", fromlist=["*"])
                self._sections_extra.append(sec_name)
                if hasattr(module, "get_section_XI_entries"):
                    self._n_entries_XI = len(module.get_section_XI_entries())
                if hasattr(module, "get_section_XII_entries"):
                    self._n_entries_XII = len(module.get_section_XII_entries())
            except ImportError:
                logger.debug("Section optionnelle %s non chargee", sec_name)

        logger.info(
            "Integrateur Memoire Gabriel : %d regimes, %d lemmes, sections XI/XII = %s",
            self._regime_count, self._total_lemmes,
            ", ".join(self._sections_extra) or "absentes",
        )

    def augmenter_prompt(self, prompt: str, domaine: str = "general") -> str:
        """Augmente un prompt LLM avec le contexte spectral detecte.

        Args:
            prompt: le prompt utilisateur original.
            domaine: domaine de la requete (informatif, non utilise actuellement).

        Returns:
            Le prompt augmente avec le contexte des regimes detectes,
            ou le prompt original si aucun regime n'est detecte.
        """
        try:
            analyse = self._adaptateur.analyser(prompt)
            return analyse.prompt_augmente
        except Exception as exc:
            logger.warning("Erreur RAG, prompt original retourne: %s", exc)
            return prompt

    def detecter_regimes(self, prompt: str) -> list[str]:
        """Retourne la liste des regimes detectes (utile pour logging/debug)."""
        try:
            regimes, _ = self._adaptateur.detecter_regimes(prompt)
            return regimes
        except Exception:
            return []

    def info(self) -> dict:
        """Statistiques de la memoire (pour CLI 'memoire' command)."""
        return {
            "regimes": self._regime_count,
            "lemmes_certifies": self._total_lemmes,
            "sections_extra": self._sections_extra,
            "module": "memory.adaptateur_cognitif_rag",
        }
