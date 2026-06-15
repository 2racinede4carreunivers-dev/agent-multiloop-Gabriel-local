"""Utilitaire CI : exécute la suite pytest locale et formate un résumé Rich.

Sert deux usages :
  1. Commande CLI `ci` : affiche le résultat détaillé des 161 tests.
  2. Bannière d'ouverture : affiche un résumé compact (XXX/YYY OK).

Aucune dépendance réseau : tout est exécuté localement, en sous-processus.
"""
from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CISummary:
    """Résumé de l'exécution pytest locale."""
    passed: int
    failed: int
    errors: int
    skipped: int
    total: int
    duration_s: float
    ok: bool
    raw_tail: str  # Dernières lignes brutes pour debug

    @property
    def badge(self) -> str:
        """Badge texte court pour la bannière (ex: '161/161 OK')."""
        if self.ok and self.failed == 0 and self.errors == 0:
            return f"{self.passed}/{self.total} OK"
        return f"{self.passed}/{self.total} ({self.failed} fail, {self.errors} err)"

    @property
    def style(self) -> str:
        """Couleur Rich associée au résultat."""
        if self.ok and self.failed == 0 and self.errors == 0:
            return "bold green"
        return "bold red"


_REPO_ROOT = Path(__file__).resolve().parents[2]
_TESTS_DIR = _REPO_ROOT / "tests"

# Regex pour parser la ligne de résumé pytest :
# "161 passed, 1 warning in 1.99s" ou "159 passed, 2 failed in 2.3s" etc.
_SUMMARY_RE = re.compile(
    r"(?:(?P<passed>\d+)\s+passed)?"
    r"(?:.*?(?P<failed>\d+)\s+failed)?"
    r"(?:.*?(?P<errors>\d+)\s+error)?"
    r"(?:.*?(?P<skipped>\d+)\s+skipped)?"
    r".*?in\s+(?P<dur>[\d.]+)s",
    re.IGNORECASE,
)


def run_pytest_local(timeout_s: int = 120) -> CISummary:
    """Exécute `python -m pytest tests/ -q --tb=no` localement et parse le résultat.

    Renvoie un `CISummary`. Ne lève jamais : encapsule les erreurs dans le résumé.
    """
    if not _TESTS_DIR.is_dir():
        return CISummary(0, 0, 1, 0, 0, 0.0, False, f"Tests directory introuvable: {_TESTS_DIR}")

    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(_TESTS_DIR), "-q", "--tb=no", "--no-header"],
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return CISummary(0, 0, 1, 0, 0, float(timeout_s), False,
                         f"Timeout (>{timeout_s}s) en exécutant pytest")
    except FileNotFoundError as exc:
        return CISummary(0, 0, 1, 0, 0, 0.0, False, f"Pytest introuvable: {exc}")

    output = (proc.stdout or "") + "\n" + (proc.stderr or "")
    tail = "\n".join(output.strip().splitlines()[-8:])

    passed = failed = errors = skipped = 0
    duration = 0.0

    # Cherche la dernière ligne contenant "passed" / "failed" / "in Xs"
    summary_line = ""
    for line in reversed(output.splitlines()):
        if " in " in line and ("passed" in line or "failed" in line or "error" in line):
            summary_line = line
            break

    if summary_line:
        m = _SUMMARY_RE.search(summary_line)
        if m:
            passed = int(m.group("passed") or 0)
            failed = int(m.group("failed") or 0)
            errors = int(m.group("errors") or 0)
            skipped = int(m.group("skipped") or 0)
            try:
                duration = float(m.group("dur"))
            except (TypeError, ValueError):
                duration = 0.0

    total = passed + failed + errors + skipped
    ok = (proc.returncode == 0) and (failed == 0) and (errors == 0) and (passed > 0)

    return CISummary(
        passed=passed,
        failed=failed,
        errors=errors,
        skipped=skipped,
        total=total,
        duration_s=duration,
        ok=ok,
        raw_tail=tail,
    )
