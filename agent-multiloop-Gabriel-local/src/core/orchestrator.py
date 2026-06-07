"""Orchestrator : facade haut-niveau de l'agent."""
from __future__ import annotations

import logging
from typing import Any

from .pipeline import Pipeline
from .types import FinalAnswer


logger = logging.getLogger(__name__)


class Orchestrator:
    """Wrapper haut-niveau autour du pipeline (interface stable pour l'UI)."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.pipeline = Pipeline(config)
        self.memory: list[dict[str, str]] = []

    async def ask(self, question: str) -> FinalAnswer:
        result = await self.pipeline.process(question)
        self.memory.append({"role": "user", "content": question})
        self.memory.append({"role": "assistant", "content": result.answer_text})
        return result

    def get_context(self) -> str:
        return f"{len(self.memory)} echanges en memoire."

    def get_memory(self, last_n: int = 5) -> str:
        if not self.memory:
            return "(memoire vide)"
        slice_ = self.memory[-last_n * 2 :]
        lines = []
        for m in slice_:
            tag = "Q" if m["role"] == "user" else "A"
            lines.append(f"[{tag}] {m['content'][:200]}")
        return "\n".join(lines)
