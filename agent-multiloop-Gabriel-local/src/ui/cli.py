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
from .debug_session import DebugSession, MAX_REQUEST_CHARS, MAX_COMMENT_CHARS


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
  gap <v1> <v2>    Ecart spectral direct entre 2 positions/primes (sans LLM)
  debug "<q>"      Mode debugger manuel pedagogique (decompose, bypass, comment)
  verifier <N>     Validation toolkit + creation d'audit citable (rapport 1/2)
  valider <N>      Boucle complete Wolfram <-> Gabriel <-> Isabelle (.thy auto-compile)
  historique       Liste des 20 derniers audits sauvegardes
  audit <id>       Affiche le contenu complet d'un audit (JSON)
  citer <id> [fmt] Genere une citation (fmt = markdown | latex | text)
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
        # Mode debug manuel : partage le kernel et spectral_core du pipeline
        self._debug_session: DebugSession | None = None

    def _get_debug_session(self) -> DebugSession:
        """Lazy init : reutilise le kernel/core/audit_store du pipeline pour eviter de re-charger les .thy."""
        if self._debug_session is None:
            pipeline = self.orchestrator.pipeline
            self._debug_session = DebugSession(
                console=console,
                certainty_kernel=pipeline.certainty_kernel,
                spectral_core=pipeline.spectral_core,
                audit_store=pipeline.audit_store,
            )
        return self._debug_session

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
        if c.startswith("gap "):
            parts = cmd.strip().split()
            if len(parts) < 3:
                console.print(
                    "\n  [yellow]Usage : gap <v1> <v2>  "
                    "(v1, v2 = positions 1..1000 ou primes connus)\n"
                    "  Exemples : 'gap 26 56'  ou  'gap 101 263'  ou  'gap 26 263'[/yellow]\n"
                )
                return True
            try:
                v1 = int(parts[1])
                v2 = int(parts[2])
            except ValueError:
                console.print(f"\n  [yellow]Valeurs invalides : '{parts[1]}' / '{parts[2]}'[/yellow]\n")
                return True
            try:
                from ..spectral.gap_compute import compute_gap, render_gap_report
                result = compute_gap(v1, v2, ratio="1/2")
                from rich.panel import Panel as _Panel
                style = "green" if result.invariant_ok else "red"
                console.print(_Panel(
                    render_gap_report(result),
                    title=f"[{style}]Ecart spectral {v1} <-> {v2}[/{style}]",
                    border_style=style,
                ))
                # Audit automatique citable
                from src.audit import AuditStore as _AS
                store = self.orchestrator.pipeline.audit_store
                record = _AS.build_record(
                    intervention_type="gap",
                    question=f"gap {v1} {v2}",
                    certified_answer=(
                        f"Ecart spectral {v1}<->{v2} : delta_n={result.delta_n}, "
                        f"delta_p={result.delta_p}, RsP={result.rsP_fraction}, "
                        f"invariant_1_2={'OK' if result.invariant_ok else 'ECHEC'}."
                    ),
                    position=result.point1.position,
                    prime_value=result.point1.prime,
                    citations_thy=[
                        "methode_spectral.thy::RsP_def (rapport spectral)",
                        "geometrie_spectre_premier.thy::D_def (D(n,P) = SB-SA-Z*P)",
                        "plan_cognitif::INVARIANT_1_2",
                    ],
                    toolkit_reports={
                        "spectral_core": {
                            "point1": {"n": result.point1.position, "p": result.point1.prime,
                                       "SA": result.point1.SA, "SB": result.point1.SB,
                                       "D": result.point1.D},
                            "point2": {"n": result.point2.position, "p": result.point2.prime,
                                       "SA": result.point2.SA, "SB": result.point2.SB,
                                       "D": result.point2.D},
                            "delta_n": result.delta_n, "delta_p": result.delta_p,
                            "delta_SA": result.delta_SA, "delta_SB": result.delta_SB,
                            "delta_D": result.delta_D,
                            "RsP": result.rsP_fraction, "RsP_decimal": result.rsP_decimal,
                            "invariant_ok": result.invariant_ok,
                        }
                    },
                    ratio="1/2",
                )
                store.save(record)
                console.print(
                    f"\n[dim]Audit cree : id={record.id} (tapez 'citer {record.id}' pour citer)[/dim]\n"
                )
            except (ValueError, RuntimeError) as exc:
                console.print(f"\n  [red]Erreur gap : {exc}[/red]\n")
            return True
        if c == "contexte":
            console.print(f"\n  Contexte : {self.orchestrator.get_context()}\n", style="cyan")
            return True
        if c == "memoire":
            console.print(f"\n  Memoire :\n{self.orchestrator.get_memory()}\n", style="cyan")
            return True
        if c.startswith("debug "):
            # Mode debugger manuel : extrait la question (avec ou sans guillemets)
            raw = cmd.strip()[len("debug "):].strip()
            if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
                question = raw[1:-1]
            elif raw.startswith("'") and raw.endswith("'") and len(raw) >= 2:
                question = raw[1:-1]
            else:
                question = raw
            if not question:
                console.print(
                    f"\n  [yellow]Usage : debug \"<question>\"  "
                    f"(max {MAX_REQUEST_CHARS} caracteres ; "
                    f"jusqu'a {MAX_COMMENT_CHARS} caracteres de commentaire ajoutables)[/yellow]\n"
                )
                return True
            session = self._get_debug_session()
            result = await session.run(question)
            if result is not None:
                self._display_answer(result)
            return True
        if c == "debug":
            console.print(
                f"\n  [yellow]Usage : debug \"<question>\"  "
                f"(ex : debug \"Reconstruis le 26eme premier en rapport 1/2\")  "
                f"\n  Limites : requete <= {MAX_REQUEST_CHARS} ch, "
                f"commentaire <= {MAX_COMMENT_CHARS} ch[/yellow]\n"
            )
            return True
        if c.startswith("verifier ") or c.startswith("verifier"):
            parts = cmd.strip().split()
            if len(parts) < 2:
                console.print(
                    "\n  [yellow]Usage : verifier <position> [ratio]  "
                    "(ex : verifier 26  -- rapport 1/2 par defaut)[/yellow]\n"
                )
                return True
            try:
                position = int(parts[1])
            except ValueError:
                console.print(f"\n  [yellow]Position invalide : '{parts[1]}'[/yellow]\n")
                return True
            ratio = parts[2] if len(parts) >= 3 else "1/2"
            session = self._get_debug_session()
            await session.verifier_position(position, ratio)
            return True
        if c.startswith("valider"):
            parts = cmd.strip().split()
            if len(parts) < 2:
                console.print(
                    "\n  [yellow]Usage : valider <position> [ratio]  "
                    "(ex : valider 26 -- boucle Wolfram<->Gabriel<->Isabelle)[/yellow]\n"
                )
                return True
            try:
                position = int(parts[1])
            except ValueError:
                console.print(f"\n  [yellow]Position invalide : '{parts[1]}'[/yellow]\n")
                return True
            ratio = parts[2] if len(parts) >= 3 else "1/2"
            console.print(
                f"\n  [dim]Boucle automatique en cours pour position={position} ratio={ratio} "
                f"(Wolfram + Gabriel + Isabelle)...[/dim]\n"
            )
            try:
                loop = self.orchestrator.pipeline.verification_loop
                result = await loop.verify(position, ratio)
                from rich.panel import Panel as _Panel
                style = "green" if result.overall_success else "yellow"
                title = "[green]VALIDATION COMPLETE — TOUT OK[/green]" if result.overall_success \
                        else "[yellow]VALIDATION INCOMPLETE[/yellow]"
                body_lines = [
                    f"Position : {result.position}    Prime : {result.prime}    Ratio : {result.ratio}",
                    "",
                    f"[bold]1. Wolfram[/bold]  : {'OK' if result.wolfram.success else 'ECHEC'}",
                    f"    {result.wolfram.detail}",
                    f"[bold]2. Gabriel[/bold]  : {'OK' if result.gabriel.success else 'ECHEC'}",
                    f"    {result.gabriel.detail}",
                    f"[bold]3. Isabelle[/bold] : {'OK' if result.isabelle.success else 'ECHEC'}",
                    f"    {result.isabelle.detail}",
                    f"    tentatives = {result.attempts}   tactique = {result.final_tactic}",
                ]
                if result.thy_path:
                    body_lines.append(f"\n    .thy genere : {result.thy_path}")
                if result.audit_id:
                    body_lines.append(
                        f"\n    Audit : id={result.audit_id} "
                        f"(citer {result.audit_id} pour bloc citable)"
                    )
                console.print(_Panel("\n".join(body_lines), title=title, border_style=style))
            except (ValueError, RuntimeError) as exc:
                console.print(f"\n  [red]Erreur valider : {exc}[/red]\n")
            return True
        if c == "historique":
            store = self.orchestrator.pipeline.audit_store
            records = store.list_records(limit=20)
            if not records:
                console.print("\n  [yellow]Aucun audit sauvegarde pour le moment.[/yellow]\n")
            else:
                from src.audit import AuditStore as _AS
                console.print(Panel(
                    _AS.summary_table(records),
                    title=f"[cyan]Historique des audits ({len(records)} affiches)[/cyan]",
                    border_style="cyan",
                ))
            return True
        if c.startswith("historique "):
            store = self.orchestrator.pipeline.audit_store
            arg = cmd.strip()[len("historique "):].strip()
            # filtre : soit un entier (position) soit un ratio "1/2"
            kwargs = {"limit": 20}
            if arg in {"1/2", "1/3", "1/4"}:
                kwargs["ratio"] = arg
            else:
                try:
                    kwargs["position"] = int(arg)
                except ValueError:
                    console.print(f"\n  [yellow]Filtre invalide : '{arg}'[/yellow]\n")
                    return True
            records = store.list_records(**kwargs)
            from src.audit import AuditStore as _AS
            if not records:
                console.print(f"\n  [yellow]Aucun audit pour le filtre '{arg}'.[/yellow]\n")
            else:
                console.print(Panel(
                    _AS.summary_table(records),
                    title=f"[cyan]Historique filtre ({arg}) — {len(records)} resultats[/cyan]",
                    border_style="cyan",
                ))
            return True
        if c.startswith("audit "):
            audit_id = cmd.strip().split()[1] if len(cmd.strip().split()) > 1 else ""
            if not audit_id:
                console.print("\n  [yellow]Usage : audit <id>[/yellow]\n")
                return True
            store = self.orchestrator.pipeline.audit_store
            record = store.get(audit_id)
            if not record:
                console.print(f"\n  [yellow]Audit '{audit_id}' introuvable.[/yellow]\n")
                return True
            import json as _json
            payload = record.to_dict()
            payload["signature_sha256"] = record.signature_sha256
            payload["signature_valid"] = store.verify(record)
            console.print(Panel(
                _json.dumps(payload, indent=2, ensure_ascii=False),
                title=f"[cyan]Audit {record.id}[/cyan]",
                border_style="cyan",
            ))
            return True
        if c.startswith("citer "):
            parts = cmd.strip().split()
            if len(parts) < 2:
                console.print(
                    "\n  [yellow]Usage : citer <id> [markdown|latex|text]  "
                    "(markdown par defaut)[/yellow]\n"
                )
                return True
            audit_id = parts[1]
            fmt = parts[2] if len(parts) >= 3 else "markdown"
            if fmt not in {"markdown", "latex", "text"}:
                console.print(f"\n  [yellow]Format invalide : '{fmt}' (markdown|latex|text)[/yellow]\n")
                return True
            store = self.orchestrator.pipeline.audit_store
            citation = store.cite(audit_id, format=fmt)
            console.print(Panel(
                citation,
                title=f"[green]Citation audit {audit_id} ({fmt})[/green]",
                border_style="green",
            ))
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
                # Limite de longueur pour eviter des requetes monstrueuses
                # (compatible avec la limite du mode debug : 1600 + 400 = 2000)
                if len(user_input) > MAX_REQUEST_CHARS + MAX_COMMENT_CHARS:
                    console.print(
                        f"\n  [yellow][Requete trop longue] "
                        f"{len(user_input)} caracteres (max {MAX_REQUEST_CHARS + MAX_COMMENT_CHARS}). "
                        f"Reformulez plus brievement ou utilisez 'debug \"<question>\"' "
                        f"pour ajouter un commentaire structure.[/yellow]\n"
                    )
                    continue
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
