"""Setup logging UTF-8 robuste (Windows + Docker)."""
from __future__ import annotations

import logging
import sys
from pathlib import Path


def setup_logging(log_dir: str | Path = "./logs", verbose: bool = False, log_file: str = "agent_cli.log") -> logging.Logger:
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)

    level = logging.DEBUG if verbose else logging.INFO
    fmt = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
    formatter = logging.Formatter(fmt)

    file_handler = logging.FileHandler(log_dir_path / log_file, encoding="utf-8", errors="replace")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)

    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
        except Exception:
            pass

    root = logging.getLogger()
    root.setLevel(level)
    # Eviter les doublons si re-appele
    root.handlers = [file_handler, console_handler]

    # Bruit reseau bas
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

    return logging.getLogger("multiloop-agent")
