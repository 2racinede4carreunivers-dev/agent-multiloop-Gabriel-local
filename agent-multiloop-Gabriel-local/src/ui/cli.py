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
from .ci_status import run_pytest_local
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
  rsp <A> <B>      Rapport spectral direct (auto-detect 1x1, nxn, chaos, ord)
  rsp-test <cfg> <N>  N tests aleatoires de config (1x1|sym2|sym3|sym5|chaos|ord)
  rsp-courbe <cfg> [kmax]  Courbe ASCII RsP en fonction de k (config: 1x1|sym|chaos|ord)
  courbe <type> <n1>..<n2> [--table] [--png] [--scale=X]
                   Trace une courbe ASCII (toujours) + tableau Rich (--table)
                   + export PNG citable (--png).
                   Types : SA | SB | SA_SB | digamma | invariant | ratio | gap | prime
                   Echelle : auto (defaut) | linear | log10 | log2
                   Exemples : 'courbe SA_SB 1..50 --png',
                              'courbe ratio 1..200 --table --png',
                              'courbe digamma 1..30 --table'
  debug "<q>"      Mode debugger manuel pedagogique (decompose, bypass, comment)
  verifier <N>     Validation toolkit + creation d'audit citable (rapport 1/2)
  valider <N>      Boucle complete Wolfram <-> Gabriel <-> Isabelle (.thy auto-compile)
  historique       Liste des 20 derniers audits sauvegardes
  audit <id>       Affiche le contenu complet d'un audit (JSON)
  citer <id> [fmt] Genere une citation (fmt = markdown | latex | text)
  contexte         Affiche le contexte mathematique actuel
  memoire          Affiche les echanges en memoire
  ci               Lance la suite pytest locale (230 tests) et affiche le rapport
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
        if c in {"ci", "tests", "pytest"}:
            console.print("\n  [dim]Execution de la suite pytest locale (tests/)... patientez quelques secondes.[/dim]\n")
            summary = run_pytest_local()
            body = (
                f"  Tests passes  : [bold]{summary.passed}[/bold]\n"
                f"  Echecs        : [bold]{summary.failed}[/bold]\n"
                f"  Erreurs       : [bold]{summary.errors}[/bold]\n"
                f"  Ignores       : [bold]{summary.skipped}[/bold]\n"
                f"  Total         : [bold]{summary.total}[/bold]\n"
                f"  Duree         : [bold]{summary.duration_s:.2f}s[/bold]\n"
                f"  Statut        : [{summary.style}]{summary.badge}[/{summary.style}]\n"
                f"\n  [dim]Sortie pytest (queue) :[/dim]\n  [dim]{summary.raw_tail}[/dim]"
            )
            title = "[green]CI - Tests Gabriel[/green]" if summary.ok else "[red]CI - Tests Gabriel[/red]"
            console.print(Panel(body, title=title, border_style="green" if summary.ok else "red"))
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
        if c.startswith("rsp-courbe"):
            parts = cmd.strip().split()
            if len(parts) < 2:
                console.print(
                    "\n  [yellow]Usage : rsp-courbe <config> [kmax]\n"
                    "  config = 1x1 | sym | chaos | ord\n"
                    "  kmax = nombre de points (defaut 50, max 500)[/yellow]\n"
                )
                return True
            config = parts[1]
            try:
                kmax = int(parts[2]) if len(parts) >= 3 else 50
                kmax = max(2, min(500, kmax))
            except ValueError:
                kmax = 50
            from src.spectral.rsp_curve import compute_rsp_curve, render_ascii_curve, summarize_curve
            core = self.orchestrator.pipeline.spectral_core
            try:
                points = compute_rsp_curve(core, config, k_max=kmax)
            except ValueError as exc:
                console.print(f"\n  [red]Erreur : {exc}[/red]\n")
                return True
            from rich.panel import Panel as _Panel
            graph = render_ascii_curve(points, width=64, height=18, target=0.5)
            summary = summarize_curve(points)
            console.print(_Panel(
                graph + "\n\n" + summary,
                title=f"[cyan]Courbe rsp-{config} (k=1..{kmax}) — convergence vers 1/2[/cyan]",
                border_style="cyan",
            ))
            return True
        if c.startswith("courbe"):
            return await self._handle_courbe(cmd)
        if c.startswith("rsp-test"):
            parts = cmd.strip().split()
            if len(parts) < 3:
                console.print(
                    "\n  [yellow]Usage : rsp-test <config> <N>\n"
                    "  config = 1x1 | sym2 | sym3 | sym5 | chaos | ord\n"
                    "  N = nombre de tests aleatoires (ex : rsp-test sym3 100)[/yellow]\n"
                )
                return True
            config = parts[1]
            try:
                n_tests = int(parts[2])
            except ValueError:
                console.print(f"\n  [yellow]N invalide : '{parts[2]}'[/yellow]\n")
                return True
            from src.spectral.rsp_command import random_combo
            from src.core.spectral_core import SpectralMethodCore
            core = self.orchestrator.pipeline.spectral_core
            results_near = 0
            results_exact = 0
            results_far = 0
            errors = 0
            samples = []
            for i in range(n_tests):
                try:
                    A, B = random_combo(core, config)
                    r = core.analyze_spectral_ratio(A, B)
                    if "error" in r:
                        errors += 1
                        continue
                    if r.get("matches_half"):
                        results_exact += 1
                    elif r.get("near_half"):
                        results_near += 1
                    else:
                        results_far += 1
                    if i < 5:
                        samples.append((A, B, r["RsP_fraction"], r["RsP_decimal"]))
                except Exception as exc:
                    errors += 1
            from rich.panel import Panel as _Panel
            body = [
                f"Configuration testee : [bold]{config}[/bold]   N = {n_tests}",
                "",
                f"  Egal a 1/2 exact   : {results_exact} ({100*results_exact/max(n_tests,1):.1f}%)",
                f"  Proche de 1/2 (5%) : {results_near} ({100*results_near/max(n_tests,1):.1f}%)",
                f"  Eloigne de 1/2     : {results_far} ({100*results_far/max(n_tests,1):.1f}%)",
                f"  Erreurs            : {errors}",
                "",
                "Echantillons (5 premiers) :",
            ]
            for A, B, frac, dec in samples:
                body.append(f"  {A} vs {B} -> {frac} ({dec:.6f})")
            console.print(_Panel("\n".join(body),
                                 title=f"[cyan]rsp-test {config} ({n_tests} echantillons)[/cyan]",
                                 border_style="cyan"))
            return True
        if c.startswith("rsp "):
            from src.spectral.rsp_command import parse_rsp_args
            raw_args = cmd.strip()[len("rsp "):]
            parsed = parse_rsp_args(raw_args)
            if parsed is None:
                console.print(
                    "\n  [yellow]Usage : rsp <A> <B>\n"
                    "  Exemples :\n"
                    "    rsp 7,23,2 29,17,13       (config 3x3 symetrique)\n"
                    "    rsp (7,23,2) (29,17,13)   (idem avec parentheses)\n"
                    "    rsp 2 3                    (config 1x1)\n"
                    "    rsp 2,3 5,7,11             (asymetrique ordonnee)\n"
                    "    rsp 3,23 41,29,31          (asymetrique chaotique)[/yellow]\n"
                )
                return True
            A, B = parsed
            try:
                core = self.orchestrator.pipeline.spectral_core
                r = core.analyze_spectral_ratio(A, B)
                if "error" in r:
                    console.print(f"\n  [red]rsp : {r['error']}[/red]\n")
                    return True
                from rich.panel import Panel as _Panel
                style = "green" if r.get("matches_half") or r.get("near_half") else "yellow"
                mark = ("= 1/2 EXACT" if r.get("matches_half")
                        else "~= 1/2 (proche)" if r.get("near_half")
                        else "ECARTE de 1/2")
                lines = [
                    f"Configuration : [bold]{r['configuration']}[/bold]",
                    f"  Methode      : {r['method']}",
                    "",
                    f"  Bloc A (primes)  : {r['A_input']}",
                    f"  Bloc A (positions): {r['A_positions']}",
                    f"  Bloc B (primes)  : {r['B_input']}",
                    f"  Bloc B (positions): {r['B_positions']}",
                ]
                if "sum_SA" in r:  # config nxn
                    lines.append(f"  sum(SA(A)) = {r['sum_SA']}")
                    lines.append(f"  sum(SB(B)) = {r['sum_SB']}")
                if "numerator" in r:  # config asym
                    lines.append(f"  num (sum_SA(A) - sum_SA(B)) = {r['numerator']}")
                    lines.append(f"  den (sum_SB(A) - sum_SB(B)) = {r['denominator']}")
                lines += [
                    "",
                    f"  RsP = [bold]{r['RsP_fraction']}[/bold] ({r['RsP_decimal']:.10f})  {mark}",
                    "",
                    "Citations :",
                ]
                for c_text in r.get("citations", []):
                    lines.append(f"  • {c_text}")
                console.print(_Panel("\n".join(lines),
                                     title=f"[{style}]Rapport spectral {r['configuration']}[/{style}]",
                                     border_style=style))
                # Audit auto
                from src.audit import AuditStore as _AS
                store = self.orchestrator.pipeline.audit_store
                record = _AS.build_record(
                    intervention_type="rsp",
                    question=f"rsp {A} {B}",
                    certified_answer=(
                        f"Configuration {r['configuration']}, "
                        f"RsP = {r['RsP_fraction']} ({r['RsP_decimal']:.6f}), "
                        f"egal_1_2={r.get('matches_half')}, proche_1_2={r.get('near_half')}"
                    ),
                    position=None,
                    prime_value=None,
                    citations_thy=r.get("citations", []),
                    toolkit_reports={"spectral_core_analysis": r},
                    ratio="1/2",
                )
                store.save(record)
                console.print(f"\n[dim]Audit : id={record.id} (citer {record.id} pour bloc citable)[/dim]\n")
            except (ValueError, RuntimeError) as exc:
                console.print(f"\n  [red]Erreur rsp : {exc}[/red]\n")
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

    async def _handle_courbe(self, cmd: str) -> bool:
        """Commande `courbe <type> <n_min>..<n_max> [--table] [--png] [--scale=...]`.

        Types : SA, SB, SA_SB, digamma, invariant, ratio, gap, prime.
        Flags :
          --table    : ajoute un tableau Rich apres l'ASCII.
          --png      : exporte un PNG haute resolution + cree un audit JSON citable.
          --scale=X  : force l'echelle (linear|log10|log2|auto, defaut: auto).
        """
        from pathlib import Path as _Path
        from src.visualization import (
            compute_curve, render_ascii, render_table, render_png,
            list_supported_kinds, MATPLOTLIB_AVAILABLE,
        )

        tokens = cmd.strip().split()
        if len(tokens) < 3:
            console.print(
                "\n  [yellow]Usage : courbe <type> <n_min>..<n_max> [--table] [--png] [--scale=X]\n"
                f"  Types disponibles : {' | '.join(list_supported_kinds())}\n"
                "  Exemples :\n"
                "    courbe SA 1..50\n"
                "    courbe SA_SB 1..30 --table\n"
                "    courbe digamma 1..100 --png\n"
                "    courbe ratio 1..200 --table --png\n"
                "    courbe invariant 1..50 --scale=linear[/yellow]\n"
            )
            return True

        kind = tokens[1]
        range_spec = tokens[2]
        # Parsing range "n_min..n_max"
        if ".." not in range_spec:
            console.print(f"\n  [yellow]Range invalide : '{range_spec}'. "
                          f"Format attendu : n_min..n_max (ex: 1..50)[/yellow]\n")
            return True
        try:
            n_min_s, n_max_s = range_spec.split("..", 1)
            n_min, n_max = int(n_min_s), int(n_max_s)
        except ValueError:
            console.print(f"\n  [yellow]Range invalide : '{range_spec}'[/yellow]\n")
            return True

        # Flags
        want_table = "--table" in tokens
        want_png = "--png" in tokens
        scale = "auto"
        for tok in tokens[3:]:
            if tok.startswith("--scale="):
                scale = tok.split("=", 1)[1]

        # Calcul
        core = self.orchestrator.pipeline.spectral_core
        try:
            curve = compute_curve(core, kind, n_min, n_max, scale=scale)
        except ValueError as exc:
            console.print(f"\n  [red]Erreur : {exc}[/red]\n")
            return True

        # 1) ASCII (toujours)
        ascii_view = render_ascii(curve, width=70, height=18)
        console.print(Panel(
            ascii_view,
            title=f"[cyan]Courbe {curve.kind.value} (n={n_min}..{n_max})[/cyan]",
            border_style="cyan",
        ))

        # 2) Table Rich (optionnel)
        if want_table:
            console.print(render_table(curve, max_rows=30))

        # 3) PNG (optionnel) + audit JSON citable
        png_path = None
        if want_png:
            if not MATPLOTLIB_AVAILABLE:
                console.print(
                    "\n  [red]matplotlib non installe. Installation : "
                    "'pip install matplotlib'[/red]\n"
                )
            else:
                output_dir = _Path("data/graphs")
                try:
                    png_path = render_png(curve, output_dir=output_dir, dpi=150)
                    console.print(
                        f"\n  [green]PNG cree :[/green] [bold]{png_path}[/bold]  "
                        f"(taille : {png_path.stat().st_size // 1024} Ko, dpi=150)\n"
                    )
                except (ImportError, ValueError) as exc:
                    console.print(f"\n  [red]Erreur PNG : {exc}[/red]\n")

        # Audit citable
        from src.audit import AuditStore as _AS
        store = self.orchestrator.pipeline.audit_store
        record = _AS.build_record(
            intervention_type="courbe",
            question=cmd.strip(),
            certified_answer=(
                f"Courbe {curve.kind.value} sur n={n_min}..{n_max} "
                f"(echelle {curve.scale}). {len(curve.points)} points. "
                f"Formule : {curve.formula}."
            ),
            position=n_min,
            prime_value=core.get_prime_at_position(n_min),
            citations_thy=[
                "methode_spectral.thy::SA_def (suite alternee A)",
                "methode_spectral.thy::SB_def (suite alternee B)",
                "geometrie_spectre_premier.thy::D_def (invariant spectral)",
            ],
            toolkit_reports={
                "visualization": {
                    "kind": curve.kind.value,
                    "n_min": n_min, "n_max": n_max,
                    "scale": curve.scale,
                    "formula": curve.formula,
                    "summary": curve.summary(),
                    "png_path": str(png_path) if png_path else None,
                }
            },
            ratio="1/2",
        )
        store.save(record)
        console.print(
            f"\n[dim]Audit cree : id={record.id} (tapez 'citer {record.id}' pour citer)[/dim]\n"
        )
        return True

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
        # Affichage du statut CI dans l'en-tete d'ouverture (tests pytest locaux)
        console.print("  [dim]Verification de la suite de tests (pytest local)...[/dim]")
        try:
            ci_summary = run_pytest_local(timeout_s=60)
            status_line = (
                f"  [bold]Statut CI Gabriel :[/bold] "
                f"[{ci_summary.style}]{ci_summary.badge}[/{ci_summary.style}] "
                f"[dim](pytest local, {ci_summary.duration_s:.2f}s - tapez 'ci' pour le rapport detaille)[/dim]"
            )
        except Exception as exc:
            logger.warning("Impossible d'executer pytest a l'ouverture : %s", exc)
            status_line = "  [yellow]Statut CI Gabriel : indisponible (pytest a echoue au demarrage)[/yellow]"
        console.print(status_line)
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
