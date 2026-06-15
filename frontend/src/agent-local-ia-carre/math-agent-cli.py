#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Point d'entree delegue vers local_ai_agent/math-agent-cli.py."""

import runpy
from pathlib import Path


if __name__ == "__main__":
    script = Path(__file__).resolve().parent / "local_ai_agent" / "math-agent-cli.py"
    runpy.run_path(str(script), run_name="__main__")
