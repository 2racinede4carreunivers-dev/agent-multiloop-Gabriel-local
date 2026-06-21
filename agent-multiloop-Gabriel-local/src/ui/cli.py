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
from .keybindings import install_keybindings, save_history as _save_kb_history


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
  modele <action> [args]   Interroge les 3 modeles spectraux (1/2, 1/3, 1/4).
                           Actions : list | questions | all | rsp1x1 <n1> <n2> |
                                     rsp <A>|<B> [sym|chaos|ord] | reconstruct <N> | gap <p1> <p2>
                           Ex: 'modele all', 'modele reconstruct 26', 'modele gap -19 -5'
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
  aide  (h, ?)     Aide rapide (cet ecran)
  commandes (cmd)  Liste complete + raccourcis clavier (recommande)
  ask              Interpeller Gabriel : principales commandes pour interagir
  ask type         Voir les fonctions et caracteristiques de Gabriel
  ask rules        Guide pour interagir efficacement avec Gabriel
  ci               Lance la suite pytest locale (236 tests) et affiche le rapport
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
        if c in {"commandes", "commands", "cmd"}:
            self._show_full_commands()
            return True
        if c == "ask" or c.startswith("ask "):
            self._handle_ask(cmd)
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
        if c.startswith("modele") or c.startswith("modèle"):
            return await self._handle_modele(cmd)
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

    def _show_full_commands(self) -> None:
        """Affiche la liste complete des commandes Gabriel + raccourcis clavier.

        Active par : commandes | commands | cmd
        """
        from rich.table import Table
        from .keybindings import is_available as _kb_available

        # ----- Categories de commandes -----
        sections: list[tuple[str, list[tuple[str, str]]]] = [
            ("[bold cyan]GENERAL[/bold cyan]", [
                ("aide  (h, ?)", "Aide rapide (HELP_TEXT)"),
                ("commandes  (cmd)", "Liste complete (ce panel)"),
                ("version", "Version de Gabriel"),
                ("contexte", "Contexte mathematique actuel"),
                ("memoire", "Historique des echanges de la session"),
                ("quitter", "Ferme Gabriel proprement"),
            ]),
            ("[bold cyan]CORPUS & PRIMES[/bold cyan]", [
                ("corpus", "Resume des fichiers .thy charges"),
                ("corpus detail", "Vue detaillee (sections, defs, lemmes)"),
                ("primes", "Statut table des nombres premiers (1..1000)"),
                ("prime <N>", "N-ieme nombre premier   ex: prime 26 -> 101"),
            ]),
            ("[bold cyan]CALCULS DETERMINISTES (sans LLM)[/bold cyan]", [
                ("gap <v1> <v2>", "Ecart spectral direct   ex: gap 26 56"),
                ("rsp <A> <B>", "Rapport spectral direct   ex: rsp 2 3"),
                ("rsp-test <cfg> <N>",
                 "N tests aleatoires. cfg: 1x1|sym2|sym3|sym5|chaos|ord"),
                ("modele list",
                 "Liste les 3 modeles spectraux (1/2, 1/3, 1/4)"),
                ("modele questions",
                 "Liste les 8 questions canoniques de la Methode"),
                ("modele all",
                 "Repond aux 8 questions sur les 3 modeles (audit auto)"),
                ("modele rsp1x1 <n1> <n2>",
                 "Q1.a sur 1/2, 1/3, 1/4   ex: modele rsp1x1 3 5"),
                ("modele rsp <A>|<B> [cas]",
                 "Q1.b/c/d   cas: sym|chaos|ord"),
                ("modele reconstruct <N>",
                 "Q2 sur les 3 modeles   ex: modele reconstruct 26"),
                ("modele gap <p1> <p2>",
                 "Q3 sur les 3 modeles (auto detecte le cas)"),
            ]),
            ("[bold cyan]VISUALISATIONS (ASCII + Table + PNG)[/bold cyan]", [
                ("rsp-courbe <cfg> [kmax]", "Courbe RsP en ASCII"),
                ("courbe <type> <n1>..<n2>",
                 "Types: SA|SB|SA_SB|digamma|invariant|ratio|gap|prime"),
                ("  --table",     "  + tableau Rich avec valeurs exactes"),
                ("  --png",       "  + PNG haute res (150 dpi, data/graphs/)"),
                ("  --scale=X",   "  Echelle: auto(defaut)|linear|log10|log2"),
            ]),
            ("[bold cyan]VALIDATION MATHEMATIQUE[/bold cyan]", [
                ("verifier <N>",
                 "Validation toolkit (sympy/mpmath/z3) + audit signe"),
                ("valider <N>",
                 "Boucle Wolfram <-> Gabriel <-> Isabelle (+.thy auto)"),
            ]),
            ("[bold cyan]AUDIT & CITATIONS SCIENTIFIQUES[/bold cyan]", [
                ("historique", "Liste les 20 derniers audits"),
                ("audit <id>", "Affiche le JSON complet d'un audit"),
                ("citer <id> [fmt]",
                 "Citation prete a inserer. fmt: markdown|latex|text"),
            ]),
            ("[bold cyan]DEBUGGER PEDAGOGIQUE[/bold cyan]", [
                ('debug "<q>"',
                 "Mode debug interactif (decompose/bypass/comment)"),
            ]),
            ("[bold cyan]TESTS & CI[/bold cyan]", [
                ("ci  (tests, pytest)",
                 "Lance les 236 tests pytest locaux"),
            ]),
            ("[bold cyan]LANGAGE NATUREL & AUTO-TRIGGER[/bold cyan]", [
                ("<question libre>",
                 "Pipeline multi-loop avec garde-fous"),
                ("(viz auto)",
                 "Detecte 'trace/illustre/evolue SA/SB/digamma/...'"),
            ]),
        ]

        for title, rows in sections:
            table = Table(
                title=title,
                title_justify="left",
                show_header=False,
                show_lines=False,
                expand=True,
                padding=(0, 2),
                border_style="dim cyan",
            )
            table.add_column("Commande", style="bold yellow", no_wrap=True, width=30)
            table.add_column("Description", style="white")
            for cmd_text, desc in rows:
                table.add_row(cmd_text, desc)
            console.print(table)
            console.print()

        # ----- Raccourcis clavier -----
        kb_active = _kb_available()
        kb_body_lines = [
            "[bold green]Raccourcis clavier interactifs[/bold green]   "
            + ("[green](actifs)[/green]" if kb_active else "[red](indisponibles)[/red]"),
            "",
            "  [bold]Fleche Haut / Bas[/bold]      Naviguer dans l'historique des commandes",
            "  [bold]Ctrl + R[/bold]               Recherche inversee dans l'historique",
            "  [bold]Tab[/bold]                    Auto-completion des commandes Gabriel",
            "  [bold]Ctrl + A[/bold]               Aller en debut de ligne",
            "  [bold]Ctrl + E[/bold]               Aller en fin de ligne",
            "  [bold]Ctrl + W[/bold]               Effacer le mot precedent",
            "  [bold]Ctrl + U[/bold]               Effacer toute la ligne (vers la gauche)",
            "  [bold]Ctrl + K[/bold]               Effacer toute la ligne (vers la droite)",
            "  [bold]Ctrl + L[/bold]               Effacer l'ecran",
            "  [bold]Ctrl + Y[/bold]               Coller le dernier texte coupe (yank)",
            "  [bold]Ctrl + C[/bold]               Interrompre la commande en cours",
            "  [bold]Ctrl + D[/bold]               Quitter Gabriel (EOF)",
            "",
            "  [dim]L'historique est sauvegarde dans data/.gabriel_history "
            "et persiste entre les sessions.[/dim]",
        ]
        if not kb_active:
            kb_body_lines.append("")
            kb_body_lines.append(
                "  [yellow]Note: le module 'readline' n'est pas disponible. "
                "Sur Windows hors Docker, installez : pip install pyreadline3[/yellow]"
            )
        console.print(Panel(
            "\n".join(kb_body_lines),
            title="[bold cyan]RACCOURCIS CLAVIER[/bold cyan]",
            border_style="green",
            padding=(1, 2),
        ))
        console.print()

        # ----- Fichiers de reference -----
        console.print(Panel(
            "  Documentation complete    : [cyan]commande-gabriel/COMMANDES.md[/cyan]\n"
            "  Aide-memoire (cheatsheet) : [cyan]commande-gabriel/AIDE-MEMOIRE.txt[/cyan]\n"
            "  Audits crees              : [cyan]data/audits/*.json[/cyan]\n"
            "  Graphiques PNG            : [cyan]data/graphs/*.png[/cyan]\n"
            "  Historique commandes      : [cyan]data/.gabriel_history[/cyan]",
            title="[bold cyan]FICHIERS DE REFERENCE[/bold cyan]",
            border_style="dim cyan",
            padding=(1, 2),
        ))
        console.print()

    def _handle_ask(self, cmd: str) -> None:
        """Commande 'ask' : 3 modes d'aide contextuelle sur Gabriel.

        Modes :
          ask          -> Principales commandes pour interpeller Gabriel
          ask type     -> Fonctions et caracteristiques + comment les utiliser
          ask rules    -> Guide pour interagir efficacement avec Gabriel
        """
        from .ask_gabriel import get_response

        tokens = cmd.strip().split(maxsplit=1)
        sub = tokens[1].strip().lower() if len(tokens) > 1 else None

        try:
            response = get_response(sub)
        except ValueError as exc:
            console.print(Panel(
                f"  [red]{exc}[/red]\n\n"
                "  Sous-commandes disponibles :\n"
                "    [cyan]ask[/cyan]         Principales commandes pour interagir avec Gabriel\n"
                "    [cyan]ask type[/cyan]    Fonctions et caracteristiques\n"
                "    [cyan]ask rules[/cyan]   Guide d'interaction avec Gabriel",
                title="[red]Erreur Ask Gabriel[/red]",
                border_style="red",
            ))
            return

        # En-tete unifie
        header = (
            f"[bold green]{response.title}[/bold green]\n"
            f"[dim]Aide contextuelle deterministe (zero appel LLM)[/dim]"
        )
        console.print(Panel(header, border_style="green", padding=(0, 2)))
        console.print()

        # Rendu des sections
        for section in response.sections:
            body = "\n".join(section["lines"])
            console.print(Panel(
                body,
                title=section["title"],
                border_style="cyan",
                padding=(1, 2),
            ))
            console.print()

        # Pied de page : navigation
        if response.mode == "main":
            footer = (
                "  Suite logique : [cyan]ask type[/cyan] (fonctions) ou "
                "[cyan]ask rules[/cyan] (regles d'interaction)"
            )
        elif response.mode == "type":
            footer = (
                "  Suite logique : [cyan]ask rules[/cyan] (regles d'interaction) "
                "ou [cyan]commandes[/cyan] (liste complete)"
            )
        else:
            footer = (
                "  Vous etes pret ! Essayez : [cyan]modele all[/cyan] ou "
                "[cyan]courbe ratio 1..50 --png[/cyan]"
            )
        console.print(Panel(footer, border_style="dim green"))
        console.print()

    async def _handle_modele(self, cmd: str) -> bool:
        """Commande `modele <action> [args...]` pour interroger les 3 modeles spectraux.

        Actions :
          modele list                         Liste les 3 modeles et leurs facteurs
          modele questions                    Liste les 8 questions canoniques
          modele all                          Repond aux 8 questions sur les 3 modeles
          modele rsp1x1 <n1> <n2>             Q1.a sur les 3 modeles
          modele rsp <A_pos>|<B_pos> [cas]    Q1.b/c/d sur les 3 modeles
                                              ex: modele rsp 2,3,4|5,6,7 sym
          modele reconstruct <N>              Q2 sur les 3 modeles (N-ieme premier)
          modele gap <p1> <p2>                Q3 sur les 3 modeles
        """
        from src.engines.geometrie_spectrale_engine import GeometrieSpectraleEngine
        from rich.table import Table

        tokens = cmd.strip().split()
        if len(tokens) < 2:
            console.print(Panel(
                "  [bold]Commande modele[/bold] - interroge les 3 modeles spectraux (1/2, 1/3, 1/4)\n\n"
                "  Actions :\n"
                "    [yellow]modele list[/yellow]                         Liste les modeles\n"
                "    [yellow]modele questions[/yellow]                    Liste les 8 questions canoniques\n"
                "    [yellow]modele all[/yellow]                          Repond aux 8 questions sur les 3 modeles\n"
                "    [yellow]modele rsp1x1 <n1> <n2>[/yellow]             Q1.a sur les 3 modeles\n"
                "    [yellow]modele rsp <A_pos>|<B_pos> [cas][/yellow]    Q1.b/c/d (cas: sym|chaos|ord)\n"
                "    [yellow]modele reconstruct <N>[/yellow]              Q2 (N-ieme premier)\n"
                "    [yellow]modele gap <p1> <p2>[/yellow]                Q3 (auto detecte +,+ / -,- / -,+)\n\n"
                "  Exemples :\n"
                "    [cyan]modele rsp1x1 3 5[/cyan]\n"
                "    [cyan]modele rsp 2,3,4|5,6,7 sym[/cyan]\n"
                "    [cyan]modele reconstruct 26[/cyan]      # 26eme premier = 101\n"
                "    [cyan]modele gap -19 -5[/cyan]\n"
                "    [cyan]modele all[/cyan]                  # Les 8 questions, 3 modeles",
                title="[cyan]Aide commande modele[/cyan]",
                border_style="cyan",
            ))
            return True

        engine = GeometrieSpectraleEngine(self.orchestrator.pipeline.spectral_core)
        action = tokens[1].lower()

        try:
            if action == "list":
                tbl = Table(title="Modeles spectraux disponibles", border_style="cyan")
                tbl.add_column("Modele", style="bold yellow")
                tbl.add_column("n_factor", justify="right")
                tbl.add_column("reconstruction_factor", justify="right")
                tbl.add_column("Ratio cible", justify="center")
                for name in engine.list_supported_models():
                    m = engine.models[name]
                    tbl.add_row(name, str(m.n_factor), str(m.reconstruction_factor), str(m.ratio))
                console.print(tbl)
                return True

            if action == "questions":
                tbl = Table(title="8 questions canoniques", border_style="cyan")
                tbl.add_column("Q", style="bold yellow")
                tbl.add_column("Description")
                for q, desc in engine.list_questions().items():
                    tbl.add_row(q, desc)
                console.print(tbl)
                return True

            if action == "all":
                console.print("  [dim]Execution des 8 questions sur les 3 modeles...[/dim]\n")
                reports = engine.answer_all_questions()
                for r in reports:
                    console.print(Panel(r.to_text(), border_style="green"))
                return True

            if action == "rsp1x1":
                if len(tokens) < 4:
                    console.print("  [yellow]Usage : modele rsp1x1 <n1> <n2>[/yellow]")
                    return True
                n1, n2 = int(tokens[2]), int(tokens[3])
                report = engine.compute_rsp_1x1_all_models(n1, n2)
                console.print(Panel(report.to_text(), border_style="green"))
                self._save_modele_audit(report, cmd)
                return True

            if action == "rsp":
                if len(tokens) < 3 or "|" not in tokens[2]:
                    console.print("  [yellow]Usage : modele rsp <A_pos>|<B_pos> [cas][/yellow]")
                    return True
                a_str, b_str = tokens[2].split("|", 1)
                A_pos = [int(x) for x in a_str.split(",") if x]
                B_pos = [int(x) for x in b_str.split(",") if x]
                case_map = {"sym": "nxn_symetrique", "chaos": "asym_chaotique", "ord": "asym_ordonnee"}
                case = case_map.get(tokens[3].lower() if len(tokens) > 3 else "sym", "nxn_symetrique")
                report = engine.compute_rsp_nxn_all_models(A_pos, B_pos, case=case)
                console.print(Panel(report.to_text(), border_style="green"))
                self._save_modele_audit(report, cmd)
                return True

            if action == "reconstruct":
                if len(tokens) < 3:
                    console.print("  [yellow]Usage : modele reconstruct <N>[/yellow]")
                    return True
                n = int(tokens[2])
                report = engine.reconstruct_all_models(n)
                console.print(Panel(report.to_text(), border_style="green"))
                self._save_modele_audit(report, cmd)
                return True

            if action == "gap":
                if len(tokens) < 4:
                    console.print("  [yellow]Usage : modele gap <p1> <p2>[/yellow]")
                    return True
                p1, p2 = int(tokens[2]), int(tokens[3])
                report = engine.compute_gap_all_models(p1, p2)
                console.print(Panel(report.to_text(), border_style="green"))
                self._save_modele_audit(report, cmd)
                return True

            console.print(f"  [red]Action inconnue : '{action}'. Tapez 'modele' pour l'aide.[/red]")
        except (ValueError, ZeroDivisionError) as exc:
            console.print(f"  [red]Erreur : {exc}[/red]")
        return True

    def _save_modele_audit(self, report, cmd_text: str) -> None:
        """Sauvegarde un audit JSON citable pour les commandes modele."""
        try:
            from src.audit import AuditStore as _AS
            store = self.orchestrator.pipeline.audit_store
            results_summary = {}
            for name, res in report.results_by_model.items():
                # Convertir Fraction en str pour serialisation
                results_summary[name] = {
                    k: (str(v) if not isinstance(v, (int, float, bool, str, list, dict, type(None))) else v)
                    for k, v in res.__dict__.items()
                }
            record = _AS.build_record(
                intervention_type="modele_spectral",
                question=cmd_text,
                certified_answer=f"{report.question} : {report.description}",
                citations_thy=[
                    "methode_spectral.thy::SA_def, SB_def, RsP_def",
                    "methode_spectral.thy::A_1_3, B_1_3, A_1_4, B_1_4",
                    "methode_spectral.thy::digamma_calc, prime_equation",
                ],
                toolkit_reports={
                    "geometrie_spectrale_engine": {
                        "question": report.question,
                        "description": report.description,
                        "results_by_model": results_summary,
                        "notes": report.notes,
                    }
                },
                ratio="1/2,1/3,1/4",
            )
            store.save(record)
            console.print(f"  [dim]Audit cree : id={record.id} (citer {record.id})[/dim]\n")
        except Exception as exc:
            logger.warning(f"Audit modele non sauvegarde : {exc}")

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
        # Installation des raccourcis clavier (readline) + historique persistant
        kb = install_keybindings(history_file="data/.gabriel_history")
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
        # Statut clavier
        if kb._installed:
            console.print(
                "  [dim]Raccourcis clavier actifs (Tab=completion, Ctrl+R=recherche, "
                "Up/Down=historique). Tapez 'commandes' pour tout voir.[/dim]"
            )
        console.print(f"\n  Agent Multi-Loop pret. Bonjour {self.user_name} !", style="bold")
        console.print("  Tapez 'aide' pour l'aide rapide, 'commandes' pour la liste complete, 'quitter' pour sortir.", style="dim")
        console.print(
            "  [bold green]>>> Pour decouvrir Gabriel :[/bold green]  "
            "[cyan]ask[/cyan] = commandes principales  |  "
            "[cyan]ask type[/cyan] = fonctions  |  "
            "[cyan]ask rules[/cyan] = guide d'interaction"
        )
        console.print()
        console.print("  " + "-" * 56)

        while True:
            try:
                user_input = console.input(f"\n[bold magenta]{self.user_name} >[/bold magenta] ").strip()
            except (EOFError, KeyboardInterrupt):
                console.print(f"\n\n  Au revoir {self.user_name} !", style="bold green")
                _save_kb_history()
                break

            if not user_input:
                continue
            if user_input.lower() in {"quitter", "exit", "quit", "q", ":q"}:
                console.print(f"\n  Au revoir {self.user_name} !", style="bold green")
                _save_kb_history()
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
