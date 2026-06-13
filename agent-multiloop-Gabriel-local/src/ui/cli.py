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
  corpus           Resume des fichiers .thy charges
  corpus detail    Vue detaillee : sections, defs, lemmes par fichier
  primes           Statut de la table des nombres premiers
  prime <N>        Donne le N-ieme nombre premier (ex: 'prime 26' -> 101)
  aligner <expr>   7e moteur : traduit l'expression Savard vers Wolfram + Isabelle
  formaliser <concept>  Genere un fichier .thy complet dans theories/generated/
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
        if c in {"corpus detail", "corpus details", "corpus -d"}:
            console.print(self.orchestrator.pipeline.corpus.detailed_view(), style="cyan")
            return True
        if c == "primes":
            from ..spectral import max_position, nth_prime
            mp = max_position()
            console.print(
                f"\n  Table des premiers : {mp} entrees disponibles.\n"
                f"  Premier (n=1) = {nth_prime(1)}, dernier (n={mp}) = {nth_prime(mp)}.\n"
                f"  Exemples : n=26 -> {nth_prime(26)}, n=100 -> {nth_prime(100)}, "
                f"n=500 -> {nth_prime(500)}, n=501 -> {nth_prime(501)}.\n",
                style="cyan",
            )
            return True
        if c.startswith("prime "):
            try:
                from ..spectral import nth_prime, max_position
                n = int(c.split()[1])
                p = nth_prime(n)
                if p is not None:
                    console.print(f"\n  Le {n}-ieme nombre premier est : [bold green]{p}[/bold green]\n")
                else:
                    console.print(f"\n  [yellow]N={n} hors limites (table : 1..{max_position()})[/yellow]\n")
            except (ValueError, IndexError):
                console.print("\n  Usage : prime <N>  (ex : prime 26)\n", style="yellow")
            return True
        if c.startswith("aligner "):
            expression = cmd[len("aligner "):].strip()
            adapter = self.orchestrator.pipeline.spectral_adapter
            try:
                result = await adapter.aligner_complet(expression, generer_isabelle=True)
                console.print(f"\n  [cyan]Requete originale :[/cyan] {result.original_query}")
                console.print(f"  [cyan]Traduite Wolfram  :[/cyan] {result.wolfram_query}")
                console.print(f"  [cyan]Statut Wolfram    :[/cyan] {result.wolfram_status}")
                if result.wolfram_result:
                    console.print(f"  [green]Resultat Wolfram :[/green] {result.wolfram_result}")
                if result.isabelle_block:
                    from rich.panel import Panel
                    console.print(Panel(result.isabelle_block, title="[yellow]Bloc Isabelle/HOL genere[/yellow]", border_style="yellow"))
            except Exception as exc:
                console.print(f"\n  [red]Erreur adaptateur : {exc}[/red]\n")
            return True
        if c.startswith("formaliser "):
            concept = cmd[len("formaliser "):].strip()
            adapter = self.orchestrator.pipeline.spectral_adapter
            theories_dir = self.config.get("data", {}).get("hol_dir", "/theories")
            try:
                info = await adapter.formaliser_et_ecrire_fichier(
                    concept_nom=concept,
                    theories_dir=theories_dir,
                )
                console.print(f"\n  [green]Fichier .thy genere :[/green] {info['file_path']}")
                console.print(f"  [cyan]Concept :[/cyan] {info['concept']}")
                console.print(f"  [cyan]Theory :[/cyan] {info['theory_name']}")
                console.print(f"  [cyan]Wolfram status :[/cyan] {info['wolfram_status']}")
                if info['wolfram_result']:
                    console.print(f"  [cyan]Wolfram resultat :[/cyan] {info['wolfram_result']}")
                console.print(f"  [dim]Taille : {info['block_size_chars']} caracteres[/dim]")
                # Recharge le corpus pour que l'agent voie le nouveau fichier
                self.orchestrator.pipeline.corpus.load_all()
                console.print("  [dim]Corpus recharge - le nouveau fichier est accessible.[/dim]\n")
            except Exception as exc:
                console.print(f"\n  [red]Erreur formaliser : {exc}[/red]\n")
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
