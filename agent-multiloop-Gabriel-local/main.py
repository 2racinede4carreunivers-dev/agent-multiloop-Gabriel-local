#!/usr/bin/env python3
"""Point d'entree principal du Multi-Loop Mathematical Agent."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

# Ajouter le repertoire racine au path
_ROOT = Path(__file__).parent.resolve()
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.core.config import load_config
from src.core.logging_setup import setup_logging


def main() -> None:
    config = load_config()
    log_dir = config.get("logging", {}).get("log_dir", "./logs")
    logger = setup_logging(log_dir)
    logger.info("Starting Multi-Loop Mathematical Agent (Gabriel local)")

    from src.ui.cli import run_cli
    run_cli()


if __name__ == "__main__":
    main()
