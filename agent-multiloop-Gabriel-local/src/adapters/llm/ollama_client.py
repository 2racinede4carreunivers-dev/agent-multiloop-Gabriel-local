"""Client async pour Ollama (LLM local primaire)."""
from __future__ import annotations

import logging
import os

import httpx


logger = logging.getLogger(__name__)


class OllamaClient:
    """Client async simple pour l'API Ollama."""

    def __init__(self, base_url: str | None = None, model: str = "llama3.2", timeout: float = 10.0):
        self.base_url = (base_url or os.environ.get("OLLAMA_HOST", "http://ollama:11434")).rstrip("/")
        self.model = model
        self.timeout = timeout

    async def is_available(self) -> bool:
        """Verifie si Ollama est joignable et que le modele est present."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code != 200:
                    return False
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                # Tolere les variantes :latest
                return any(self.model in name for name in models)
        except Exception as exc:
            logger.warning("Ollama indisponible : %s", exc)
            return False

    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.2,
    ) -> str | None:
        """Genere une reponse via /api/generate. Retourne None si echec."""
        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if system:
            payload["system"] = system
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/api/generate", json=payload)
                if resp.status_code != 200:
                    logger.warning("Ollama HTTP %s : %s", resp.status_code, resp.text[:200])
                    return None
                data = resp.json()
                return data.get("response", "").strip() or None
        except httpx.TimeoutException:
            logger.warning("Ollama : timeout apres %ss", self.timeout)
            return None
        except Exception as exc:
            logger.warning("Ollama : erreur %s", exc)
            return None

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.2,
    ) -> str | None:
        """Chat multi-tours via /api/chat. messages = [{role, content}, ...]."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                if resp.status_code != 200:
                    return None
                data = resp.json()
                return (data.get("message", {}).get("content") or "").strip() or None
        except Exception as exc:
            logger.warning("Ollama chat : erreur %s", exc)
            return None
