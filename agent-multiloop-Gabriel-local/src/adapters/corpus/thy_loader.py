"""
Chargeur de fichiers .thy (Isabelle/HOL) - extrait sections, definitions, axiomes.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any


SECTION_RE = re.compile(r'^section\s+"([^"]+)"', re.MULTILINE)
DEFINITION_RE = re.compile(r'^definition\s+(\w+)\s*::', re.MULTILINE)
LEMMA_RE = re.compile(r'^lemma\s+(\w+)\s*:', re.MULTILINE)
THEOREM_RE = re.compile(r'^theorem\s+(\w+)\s*:', re.MULTILINE)
AXIOM_RE = re.compile(r'axiomatization where\s*\n\s*(\w+)\s*:', re.MULTILINE)


class TheoryLoader:
    """Charge et indexe les fichiers .thy du corpus."""

    def __init__(self, theory_dir: str | Path = "/theories"):
        self.theory_dir = Path(theory_dir)
        self.theories: dict[str, dict[str, Any]] = {}

    def load_all(self) -> dict[str, dict[str, Any]]:
        """Charge tous les .thy du dossier."""
        if not self.theory_dir.exists():
            return {}
        for thy in self.theory_dir.glob("*.thy"):
            self.theories[thy.stem] = self.parse_file(thy)
        return self.theories

    def parse_file(self, path: Path) -> dict[str, Any]:
        """Extrait les sections, definitions, lemmes, theoremes et axiomes."""
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return {"name": path.stem, "sections": [], "definitions": [], "lemmas": [], "theorems": [], "axioms": [], "raw_size": 0}

        return {
            "name": path.stem,
            "path": str(path),
            "raw_size": len(content),
            "sections": SECTION_RE.findall(content),
            "definitions": DEFINITION_RE.findall(content),
            "lemmas": LEMMA_RE.findall(content),
            "theorems": THEOREM_RE.findall(content),
            "axioms": AXIOM_RE.findall(content),
        }

    def summary(self) -> str:
        """Resume textuel du corpus charge."""
        if not self.theories:
            return "Corpus HOL : aucun fichier .thy charge."
        lines = [f"Corpus HOL ({len(self.theories)} fichier(s)) :"]
        for name, info in self.theories.items():
            lines.append(
                f"  - {name}.thy : {len(info['sections'])} sections, "
                f"{len(info['definitions'])} defs, {len(info['lemmas'])} lemmes, "
                f"{len(info['theorems'])} theoremes, {len(info['axioms'])} axiomes"
            )
        return "\n".join(lines)
