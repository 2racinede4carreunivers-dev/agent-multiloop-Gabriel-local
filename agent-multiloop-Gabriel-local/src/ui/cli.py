"""Interface CLI de l'agent multi-loop."""
from __future__ import annotations

import asyncio
import logging

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..core.config import load_config
from ..core.orchestrator import Orchestrator
from ..core.types import FinalAnswer


logger = logging.getLogger(__name__)
console = Console()


BANNER = """
+============================================================+
|     MULTI-LOOP MATH AGENT  -  Philippe Thomas Savard       |
|       Methode Spectrale  *  Isabelle/HOL  *  Multi-Loop    |
+============================================================+
"""


HELP_TEXT = """
  Commandes disponibles
  ----------------------------------------------------------
  aide / help      Affiche ce menu
  quitter / quit   Quitte le programme
  corpus           Liste les fichiers .thy du corpus
  contexte         Affiche le contexte mathematique actuel
  memoire          Affiche les echanges en memoire
  version          Affiche la version

  Domaines supportes :
    - Methode Spectrale (rapports 1/2, 1/3, 1/4)
    - Reconstruction de premiers via SA, SB, digamma
    - Rapport spectral (1x1, n*n, asym ordonnee, asym chaotique)
    - Ecarts entre premiers (+,+), (-,-), (-,+)
    - Plan trifocal (FZg, HyRi, MsP) et lien Riemann
    - Generation/validation Isabelle/HOL
  ----------------------------------------------------------
"""


class CLIInterface:
    """Interface CLI interactive."""

    VERSION = "1.0.0"

    def __init__(self):
        self.config = load_config()
        self.user_name = self.config.get("agent", {}).get("user_name", "Philippe")
        self.orchestrator = Orchestrator(self.config)

    def banner(self) -> None:
        console.print(Text(BANNER, style="bold magenta"))

    def help(self) -> None:
        console.print(Text(HELP_TEXT, style="cyan"))

    async def _handle_special(self, cmd: str) -> bool:
        c = cmd.lower().strip()
        if c in {"aide", "help", "h", "?"}:
            self.help()
            return True
        if c == "version":
            console.print(f"\n  Multi-Loop Math Agent v{self.VERSION}\n", style="green")
            return True
        if c == "corpus":
            console.print("\n  " + self.orchestrator.pipeline.corpus.summary() + "\n", style="cyan")
            return True
        if c == "contexte":
            console.print(f"\n  Contexte : {self.orchestrator.get_context()}\n", style="cyan")
            return True
        if c == "memoire":
            console.print(f"\n  Memoire :\n{self.orchestrator.get_memory()}\n", style="cyan")
            return True
        return False

    def _display_answer(self, answer: FinalAnswer) -> None:
        # Affichage principal
        console.print(
            Panel(
                answer.answer_text,
                title=f"[bold green]Reponse[/bold green]  "
                f"(score {answer.best_score:.1f}/10, iter {answer.iterations_used})",
                border_style="green",
            )
        )
        # Calculs intermediaires
        if answer.structured_data:
            facts = []
            for k, v in answer.structured_data.items():
                if isinstance(v, (int, float, str, bool)):
                    facts.append(f"  {k} = {v}")
            if facts:
                console.print(
                    Panel("\n".join(facts), title="[cyan]Chiffres calcules[/cyan]", border_style="cyan")
                )
        # Script HOL
        if answer.hol_script:
            console.print(
                Panel(answer.hol_script, title="[yellow]Fragment HOL genere[/yellow]", border_style="yellow")
            )

    async def interactive_mode(self) -> None:
        self.banner()
        console.print(f"\n  Agent Multi-Loop pret. Bonjour {self.user_name} !", style="bold")
        console.print("  Tapez 'aide' pour les commandes, 'quitter' pour sortir.\n", style="dim")
        console.print("  " + "-" * 56)

        while True:
            try:
                user_input = console.input(f"\n[bold magenta]{self.user_name} >[/bold magenta] ").strip()
            except (EOFError, KeyboardInterrupt):
                console.print(f"\n\n  Au revoir {self.user_name} !", style="bold green")
                break

            if not user_input:
                continue
            if user_input.lower() in {"quitter", "exit", "quit", "q", ":q"}:
                console.print(f"\n  Au revoir {self.user_name} !", style="bold green")
                break

            if await self._handle_special(user_input):
                continue

            try:
                console.print("\n  [dim]Reflexion en cours (multi-loop self-critique)...[/dim]")
                answer = await self.orchestrator.ask(user_input)
                self._display_answer(answer)
            except Exception as exc:
                logger.error("Erreur traitement : %s", exc, exc_info=True)
                console.print(f"\n  [red][Erreur] {exc}[/red]\n")


def run_cli() -> None:
    """Point d'entree synchrone."""
    cli = CLIInterface()
    asyncio.run(cli.interactive_mode())
