#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
math-agent-cli.py  –  Interface CLI pour l'agent mathematique de Philippe
Version : 3.3  –  Mai 2026
"""

import sys
import os
import asyncio
import argparse
import logging
import shutil
import subprocess
from pathlib import Path

# ===========================================================================
#  CORRECTION DES CHEMINS D'IMPORT
#  Ajoute src/ au sys.path => "from core.agent import MathAgent" fonctionne
#  Les imports relatifs de agent.py (.llm_manager, etc.) sont preserves
#  car le module est charge avec son contexte de package (core.agent).
# ===========================================================================
_APP_DIR = Path(__file__).parent.resolve()
_SRC_DIR = _APP_DIR / "src"

if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

# Remplace l'ancien : from agent import MathAgent
from core.agent import MathAgent  # type: ignore

# ===========================================================================
#  CONSTANTES
# ===========================================================================
LOG_DIR  = _APP_DIR / "logs"
DATA_DIR = _APP_DIR / "data"

HOL_DIR = Path(os.environ.get("HOL_DIR", "/workspace/hol"))
PDF_DIR = Path(os.environ.get("PDF_DIR", "/workspace/pdf"))
TEX_DIR = Path(os.environ.get("TEX_DIR", "/workspace/tex"))

LOG_FILE   = LOG_DIR / "agent_cli.log"
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
VERSION    = "3.3"

GITHUB_REPOS = (
    {
        "name": "Theorie-mathematique-philippe-thomas-savard-2026",
        "url": "https://github.com/2racinede4carreunivers-dev/Theorie-mathematique-philippe-thomas-savard-2026.git",
        "requires_auth": False,
    },
    {
        "name": "formation_evolutive_savard",
        "url": "https://github.com/2racinede4carreunivers-dev/formation_evolutive_savard.git",
        "requires_auth": False,
    },
    {
        "name": "agent-local-ia-carre",
        "url": "https://github.com/2racinede4carreunivers-dev/agent-local-ia-carre.git",
        "requires_auth": True,
    },
)

# ===========================================================================
#  LOGGING
# ===========================================================================
def setup_logging(verbose: bool = False) -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    level = logging.DEBUG if verbose else logging.INFO
    formatter = logging.Formatter(LOG_FORMAT)

    # FIX 1: FileHandler avec errors='replace' pour UTF-8
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8", errors="replace")
    file_handler.setFormatter(formatter)

    # FIX 2: Utiliser stderr au lieu de stdout avec UTF-8
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    
    # FIX 3: Reconfigurer stderr pour UTF-8 avec fallback 'replace'
    if hasattr(sys.stderr, 'reconfigure'):
        try:
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(file_handler)
    root.addHandler(console_handler)

    # Evite le bruit des logs HTTP de transport qui masquent la vraie reponse.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    return logging.getLogger("math-agent-cli")


def _read_env_file_value(path: Path, key: str) -> str | None:
    if not path.exists():
        return None

    prefix = f"{key}="
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#") or not line.startswith(prefix):
                    continue
                return line[len(prefix):].strip().strip('"').strip("'")
    except OSError:
        return None

    return None


def _default_github_root() -> Path:
    if _APP_DIR.name == "local_ai_agent":
        return _APP_DIR.parent / "GitHub"
    return _APP_DIR / "GitHub"


def _resolve_github_root() -> Path:
    env_root = os.environ.get("GITHUB_REPOS_ROOT")
    if env_root:
        return Path(env_root)

    candidates = [
        _APP_DIR / "GitHub",
        _APP_DIR.parent / "GitHub",
        _default_github_root(),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    return _default_github_root()


def _git_auth_url(repo_url: str, username: str | None, token: str | None) -> str:
    if not username or not token:
        return repo_url

    if not repo_url.startswith("https://"):
        return repo_url

    https_prefix = "https://"
    return f"{https_prefix}{username}:{token}@{repo_url[len(https_prefix):]}"


def bootstrap_github_repositories(logger: logging.Logger) -> None:
    git = shutil.which("git")
    if not git:
        logger.warning("Git introuvable dans le PATH, bootstrap GitHub ignore.")
        return

    github_root = _resolve_github_root()
    github_root.mkdir(parents=True, exist_ok=True)

    token = os.environ.get("GITHUB_TOKEN") or _read_env_file_value(_APP_DIR / ".env", "GITHUB_TOKEN")
    username = os.environ.get("GITHUB_USERNAME") or _read_env_file_value(_APP_DIR / ".env", "GITHUB_USERNAME")
    if not token:
        token = _read_env_file_value(_APP_DIR.parent / ".env", "GITHUB_TOKEN")
    if not username:
        username = _read_env_file_value(_APP_DIR.parent / ".env", "GITHUB_USERNAME")

    auth_available = bool(token and token != "PASTE_YOUR_GITHUB_FINE_GRAINED_TOKEN_HERE")

    def _is_auth_failure(text: str) -> bool:
        lowered = text.lower()
        return any(
            marker in lowered
            for marker in (
                "invalid credentials",
                "authentication failed",
                "write access to repository not granted",
                "permission denied",
                "403",
            )
        )

    for repo in GITHUB_REPOS:
        repo_name = repo["name"]
        repo_url = repo["url"]
        repo_path = github_root / repo_name
        requires_auth = bool(repo["requires_auth"])

        if requires_auth and not auth_available:
            logger.warning("Depot prive ignore (token absent): %s", repo_name)
            continue

        if (repo_path / ".git").exists():
            logger.info("Mise a jour du depot %s", repo_name)
            update_url = _git_auth_url(repo_url, username if requires_auth and auth_available else None, token if requires_auth and auth_available else None)
            result = subprocess.run(
                [git, "-C", str(repo_path), "pull", "--ff-only"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.stdout:
                logger.info("%s", result.stdout.strip())
            if result.returncode != 0:
                message = result.stderr.strip() if result.stderr else "code retour non nul"
                if requires_auth and _is_auth_failure(message):
                    logger.warning("Depot prive saute (droits GitHub insuffisants): %s", repo_name)
                else:
                    logger.warning("Echec de pull pour %s: %s", repo_name, message)
            else:
                logger.info("Depot a jour : %s", repo_name)
        else:
            logger.info("Clone du depot %s", repo_name)
            clone_url = _git_auth_url(repo_url, username if requires_auth and auth_available else None, token if requires_auth and auth_available else None)
            result = subprocess.run(
                [git, "clone", clone_url, str(repo_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.stdout:
                logger.info("%s", result.stdout.strip())
            if result.returncode != 0:
                message = result.stderr.strip() if result.stderr else "code retour non nul"
                if requires_auth and _is_auth_failure(message):
                    logger.warning("Depot prive saute (droits GitHub insuffisants): %s", repo_name)
                else:
                    logger.warning("Echec de clone pour %s: %s", repo_name, message)
            else:
                logger.info("Depot clone : %s", repo_name)


# ===========================================================================
#  BANNIERE
# ===========================================================================
def print_banner(logger: logging.Logger) -> None:
    print(f"""
  +============================================================+
  |   AGENT LLM - Philippe  |  LLM Complet + Maths  v{VERSION}  |
  |   PhilippeLLM  *  Isabelle/HOL  *  GitHub  *  CLI         |
  +============================================================+
""")
    logger.info("Agent LLM CLI demarre – version %s", VERSION)
    logger.info("App dir    : %s", _APP_DIR)
    logger.info("Corpus HOL : %s", HOL_DIR)
    logger.info("Corpus PDF : %s", PDF_DIR)
    logger.info("Corpus TeX : %s", TEX_DIR)
    logger.info("Data dir   : %s", DATA_DIR)


# ===========================================================================
#  AIDE
# ===========================================================================
HELP_TEXT = """
  Commandes disponibles
  ----------------------------------------------------------
  aide / help      Affiche ce menu
  quitter / quit   Quitte le programme
  version          Affiche la version
  corpus           Liste les fichiers du corpus charges
  contexte         Affiche le contexte mathematique actuel
  memoire          Affiche les elements en memoire

  Domaines supportes :
    - Isabelle/HOL, preuves formelles
    - Fonction zeta de Riemann, hypothese de Riemann
    - Geometrie des nombres premiers
    - Methode de Philippot
    - Espace de Philippot
    - Mecanique harmonique du chaos discret
    - Postulat de l univers carre
    - Analyse spectrale
  ----------------------------------------------------------
"""


def _print_help() -> None:
    print(HELP_TEXT)


# ===========================================================================
#  COMMANDES SPECIALES
# ===========================================================================
async def _handle_special(cmd: str, agent: MathAgent,
                           logger: logging.Logger) -> bool:
    c = cmd.lower().strip()

    if c in ("aide", "help", "h", "?"):
        _print_help()
        return True

    if c == "version":
        print(f"\n  Math-Agent CLI v{VERSION}\n")
        return True

    if c == "corpus":
        print("\n  Fichiers du corpus :")
        for d, label in [(HOL_DIR, "HOL"), (PDF_DIR, "PDF"), (TEX_DIR, "LaTeX")]:
            if d.exists():
                files = sorted(d.iterdir())
                print(f"    [{label}]  {d}  –  {len(files)} fichier(s)")
                for f in files[:5]:
                    print(f"      • {f.name}")
                if len(files) > 5:
                    print(f"      ... et {len(files) - 5} autre(s)")
            else:
                print(f"    [{label}]  {d}  –  absent ou vide")
        print()
        return True

    if c == "contexte":
        try:
            ctx = await agent.get_context()
            print(f"\n  Contexte :\n{ctx}\n")
        except Exception as e:
            logger.warning("Contexte non disponible : %s", e)
            print("  [Contexte non disponible]\n")
        return True

    if c == "memoire":
        try:
            mem = await agent.get_memory()
            print(f"\n  Memoire :\n{mem}\n")
        except Exception as e:
            logger.warning("Memoire non disponible : %s", e)
            print("  [Memoire non disponible]\n")
        return True

    return False


# ===========================================================================
#  BOUCLE CLI PRINCIPALE
# ===========================================================================
async def run_cli(args: argparse.Namespace, logger: logging.Logger) -> None:
    logger.info("Initialisation du MathAgent (mode LLM)...")
    try:
        import yaml  # type: ignore
        config_path = _APP_DIR / "config.yaml"
        config: dict = {}
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as fh:
                config = yaml.safe_load(fh) or {}
        # Injecter les chemins corpus depuis l'environnement
        config.setdefault("data", {})
        config["data"]["hol_dir"]  = str(HOL_DIR)
        config["data"]["pdf_dir"]  = str(PDF_DIR)
        config["data"]["tex_dir"]  = str(TEX_DIR)
        config["data"]["data_dir"] = str(DATA_DIR)
        config["root_dir"] = str(_SRC_DIR)
        agent = MathAgent(config)
        logger.info("MathAgent (LLM) initialise avec succes.")
    except Exception as e:
        logger.error("Erreur fatale dans main_cli.py: %s", e, exc_info=True)
        sys.exit(1)

    print("\n  Agent LLM pret. (PhilippeLLM + maths + GitHub)")
    print("  Tapez 'aide' pour les commandes, 'quitter' pour sortir.\n")
    print("  " + "-" * 56)

    while True:
        try:
            user_input = input("\nPhilippe > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Au revoir Philippe !")
            logger.info("Session terminee (EOF/CTRL+C).")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quitter", "exit", "quit", "q", ":q"):
            print("\n  Au revoir Philippe !")
            logger.info("Session terminee par commande.")
            break

        handled = await _handle_special(user_input, agent, logger)
        if handled:
            continue

        logger.debug("Question : %s", user_input)
        try:
            response = await agent.process_message(user_input)
            print(f"\n  Agent > {response}\n")
            logger.debug("Reponse : %s", response)
        except Exception as e:
            logger.error("Erreur traitement : %s", e, exc_info=True)
            print(f"\n  [Erreur] {e}\n")


# ===========================================================================
#  POINT D'ENTREE
# ===========================================================================
def main() -> None:
    parser = argparse.ArgumentParser(
        prog="math-agent-cli",
        description="Math-Agent CLI – Agent mathematique de Philippe",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Mode verbeux (logs DEBUG)")
    parser.add_argument("--version", action="version",
                        version=f"math-agent-cli {VERSION}")
    args = parser.parse_args()

    logger = setup_logging(verbose=args.verbose)
    bootstrap_github_repositories(logger)
    print_banner(logger)

    try:
        asyncio.run(run_cli(args, logger))
    except Exception as e:
        logger.error("Erreur fatale dans math-agent-cli.py: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
