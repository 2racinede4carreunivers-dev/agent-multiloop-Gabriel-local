#!/usr/bin/env python3
"""
main_cli.py v4.0
Point d'entree CLI pour Gabriel avec API HTTP intègee.

Modes:
  1. Mode interactif: CLI Rich (par defaut si GABRIEL_HTTP_ONLY=0)
  2. Mode API seule: Serveur Flask (si GABRIEL_HTTP_ONLY=1)
  3. Mode hybride: CLI + API simultanes (ThreadPoolExecutor)

Utilise les variables d'environnement:
  - GABRIEL_HTTP_ONLY=1 → Lancer SEULEMENT le serveur HTTP (pas de CLI)
  - GABRIEL_HTTP_ONLY=0 → Lancer SEULEMENT le CLI interactif
  - GABRIEL_HTTP_API=1 → Lancer CLI + API en parallele (defaut)
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Ajouter le repertoire racine au path
_ROOT = Path(__file__).parent.resolve()
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.core.config import load_config
from src.core.logging_setup import _env_verbose, setup_logging
from src.core.pipeline import Pipeline

logger = logging.getLogger(__name__)


def _rich_init_banner() -> "tuple[object, object] | tuple[None, None]":
    """Retourne (console, live_context_manager) si Rich est disponible."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        from rich.align import Align
        from rich.box import ROUNDED
    except ImportError:
        return None, None

    console = Console()
    title = Text("Multi-Loop Mathematical Agent - Gabriel v4.0", style="bold cyan")
    subtitle = Text(
        "Chargement de la Methode Spectrale + HTTP API...",
        style="italic dim",
    )
    body = Align.center(Text.assemble(title, "\n", subtitle))
    panel = Panel(
        body,
        title="[bold]Initialisation[/bold]",
        border_style="cyan",
        box=ROUNDED,
        padding=(1, 2),
    )
    console.print(panel)
    return console, None


def _rich_init_summary(
    console,
    started_at: float,
    log_path: Path,
    verbose: bool,
    http_mode: str,
) -> None:
    """Affiche un mini-résumé propre après l'initialisation (Rich)."""
    if console is None:
        return
    try:
        from rich.panel import Panel
        from rich.text import Text
        from rich.box import ROUNDED
    except ImportError:
        return

    duration = time.monotonic() - started_at
    lines = Text()
    lines.append("  Duree init   : ", style="dim")
    lines.append(f"{duration:.2f}s\n", style="bold green")
    lines.append("  Log file     : ", style="dim")
    lines.append(f"{log_path}\n", style="cyan")
    lines.append("  Mode HTTP    : ", style="dim")
    lines.append(f"{http_mode}\n", style="yellow")
    lines.append("  Verbose      : ", style="dim")
    lines.append(
        "ON (logs INFO au terminal)" if verbose else "OFF (logs INFO -> fichier)",
        style="yellow" if verbose else "green",
    )

    console.print(
        Panel(
            lines,
            title="[bold]Initialisation terminee[/bold]",
            border_style="green",
            box=ROUNDED,
            padding=(0, 2),
        )
    )


def run_http_api(pipeline: Pipeline, config: dict, port: int = 8000) -> None:
    """Lancer le serveur Flask HTTP dans un thread."""
    try:
        from src.api.gabriel_http_api import init_gabriel_api, run_gabriel_api
        
        logger.info("Initializing HTTP API on port %d", port)
        init_gabriel_api(pipeline, config)
        run_gabriel_api(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        logger.error("HTTP API error: %s", e)


def run_cli() -> None:
    """Lancer le CLI interactif."""
    try:
        from src.ui.cli import run_cli as _run_cli
        logger.info("Starting interactive CLI")
        _run_cli()
    except Exception as e:
        logger.error("CLI error: %s", e)


def main() -> None:
    started_at = time.monotonic()

    # 1) Banniere d'init
    console, _ = _rich_init_banner()

    # 2) Config + logging
    config = load_config()
    log_dir = config.get("logging", {}).get("log_dir", "./logs")
    logger_setup = setup_logging(log_dir)

    verbose = _env_verbose()
    logger.info("Starting Gabriel v4.0 (Multi-Loop Mathematical Agent)")

    # 3) Determiner le mode HTTP
    http_only = os.getenv("GABRIEL_HTTP_ONLY", "0") == "1"
    http_enabled = os.getenv("GABRIEL_HTTP_API", "1") == "1"
    http_port = int(os.getenv("GABRIEL_HTTP_PORT", "8000"))

    if http_only:
        http_mode = "HTTP API ONLY (no CLI)"
    elif http_enabled:
        http_mode = "HYBRID (CLI + HTTP API)"
    else:
        http_mode = "CLI ONLY (no HTTP)"

    logger.info("HTTP mode: %s (port %d)", http_mode, http_port)

    # 4) Initialiser le Pipeline Gabriel
    logger.info("Loading Gabriel Pipeline...")
    pipeline = Pipeline(config)

    # 5) Afficher le badge scientifique
    try:
        from src.core.scientific_badge import print_badge_to_console
        if console is not None:
            print_badge_to_console(console)
    except Exception as exc:
        logger.warning("Badge scientifique non disponible: %s", exc)

    # 6) Résumé d'init
    log_path = Path(log_dir).resolve() / "agent_cli.log"
    _rich_init_summary(console, started_at, log_path, verbose, http_mode)

    # 7) Lancer selon le mode
    if http_only:
        # Mode API seule (pas de CLI interactif)
        logger.info("Running in HTTP API ONLY mode...")
        run_http_api(pipeline, config, http_port)
    
    elif http_enabled:
        # Mode hybride: CLI + API en parallele
        logger.info("Running in HYBRID mode (CLI + HTTP API)...")
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Lancer l'API HTTP dans un thread
            http_thread = executor.submit(run_http_api, pipeline, config, http_port)
            
            # Lancer le CLI dans le thread principal
            try:
                run_cli()
            except KeyboardInterrupt:
                logger.info("CLI interrupted by user")
            
            # Attendre la fin de l'API (elle s'arrête quand le CLI s'arrête)
            http_thread.result(timeout=5)
    
    else:
        # Mode CLI seul (pas d'API HTTP)
        logger.info("Running in CLI ONLY mode...")
        run_cli()


if __name__ == "__main__":
    main()
