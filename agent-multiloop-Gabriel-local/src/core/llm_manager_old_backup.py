"""
LLM Manager : Ollama primaire avec fallback OpenAI.
Si Ollama ne repond pas (timeout / erreur / indisponible), bascule sur OpenAI.
"""
from __future__ import annotations

import logging
from typing import Any

from ..adapters.llm.ollama_client import OllamaClient
from ..adapters.llm.openai_client import OpenAIClient


logger = logging.getLogger(__name__)


class LLMManager:
    """Wrapper avec strategie : Ollama -> OpenAI fallback."""

    def __init__(self, config: dict[str, Any]):
        llm_cfg = config.get("llm", {})
        ollama_cfg = llm_cfg.get("ollama", {})
        openai_cfg = llm_cfg.get("openai", {})

        self.primary = llm_cfg.get("primary", "ollama")
        self.fallback = llm_cfg.get("fallback", "openai")

        self.ollama = OllamaClient(
            base_url=ollama_cfg.get("base_url"),
            model=ollama_cfg.get("model", "llama3.2"),
            timeout=float(ollama_cfg.get("timeout_seconds", 60)),
        )

        self.openai = OpenAIClient(
            api_key=None,  # lit depuis env
            model=openai_cfg.get("model", "gpt-5.4"),
            temperature=float(openai_cfg.get("temperature", 0.2)),
            max_tokens=int(openai_cfg.get("max_tokens", 4096)),
            timeout=float(openai_cfg.get("timeout_seconds", 90)),
        )

        self._ollama_available: bool | None = None  # cache

    async def _check_ollama(self) -> bool:
        if self._ollama_available is None:
            self._ollama_available = await self.ollama.is_available()
        return self._ollama_available

    async def generate(self, prompt: str, system: str | None = None, temperature: float = 0.2) -> str:
        """
        Tente Ollama d'abord. Si echec/timeout/empty, bascule sur OpenAI.
        Si les deux echouent, retourne une erreur claire.
        """
        # Tentative Ollama
        if self.primary == "ollama" and await self._check_ollama():
            logger.info("Tentative LLM : Ollama (%s)", self.ollama.model)
            result = await self.ollama.generate(prompt, system=system, temperature=temperature)
            if result:
                return result
            logger.warning("Ollama n'a pas retourne de reponse, fallback OpenAI.")
        elif self.primary == "ollama":
            logger.warning("Ollama indisponible. Fallback direct OpenAI.")

        # Fallback OpenAI
        if self.openai.is_available():
            logger.info("Tentative LLM : OpenAI (%s)", self.openai.model)
            result = await self.openai.generate(prompt, system=system, temperature=temperature)
            if result:
                return result
            logger.error("OpenAI a echoue aussi.")
        else:
            logger.error("OPENAI_API_KEY absent : impossible d'utiliser le fallback.")

        return "[LLM indisponible] Ollama et OpenAI sont tous deux inaccessibles."

    async def chat(self, messages: list[dict], temperature: float = 0.2) -> str:
        """Chat multi-tours avec memoire de conversation."""
        if self.primary == "ollama" and await self._check_ollama():
            result = await self.ollama.chat(messages, temperature=temperature)
            if result:
                return result
            logger.warning("Ollama chat sans reponse, fallback OpenAI.")
        elif self.primary == "ollama":
            logger.warning("Ollama indisponible.")

        if self.openai.is_available():
            result = await self.openai.chat(messages, temperature=temperature)
            if result:
                return result

        return "[LLM indisponible]"
