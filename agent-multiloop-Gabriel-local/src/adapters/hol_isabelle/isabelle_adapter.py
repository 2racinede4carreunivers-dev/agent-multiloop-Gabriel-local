"""
Adapter Isabelle/HOL : generation de scripts .thy et validation via le conteneur.

Architecture :
  - Genere des fragments .thy a partir des resultats spectraux calcules.
  - Si le conteneur Isabelle est joignable, peut lancer `isabelle build`.
  - Si non, retourne le script genere pour copier-coller manuel.
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)


class IsabelleAdapter:
    """Generateur et validateur de scripts HOL."""

    def __init__(self, config: dict[str, Any]):
        isa_cfg = config.get("isabelle", {})
        self.enabled = bool(isa_cfg.get("enabled", True))
        self.home = isa_cfg.get("home", os.environ.get("ISABELLE_HOME", "/opt/Isabelle2025-2"))
        self.heap = isa_cfg.get("heap", "HOL")
        self.theory_dir = Path(isa_cfg.get("theory_dir", "/theories"))

    def is_isabelle_available(self) -> bool:
        """Verifie si l'executable isabelle est dans le PATH."""
        return shutil.which("isabelle") is not None or (Path(self.home) / "bin" / "isabelle").exists()

    def generate_verification_script(
        self,
        theory_name: str,
        n: int,
        p: int,
        model: str,
        SA_val: int | float,
        SB_val: int | float,
        digamma_val: int | float,
    ) -> str:
        """Genere un .thy minimal pour verifier l'equation prime_equation."""
        return f"""theory {theory_name}
  imports methode_spectral
begin

(* Script genere automatiquement pour verifier le premier {p} avec n={n} *)

section "Verification {p} via modele {model}"

lemma verif_premier_{p}_n_{n}:
  "prime_equation {n} {p} = real {p}"
  unfolding prime_equation_def digamma_calc_def
  by simp

lemma SA_n_{n}_valeur:
  "SA {n} = {SA_val}"
  unfolding SA_def by simp

lemma SB_n_{n}_valeur:
  "SB {n} = {SB_val}"
  unfolding SB_def by simp

lemma digamma_calc_n_{n}_p_{p}:
  "digamma_calc {n} {p} = {digamma_val}"
  unfolding digamma_calc_def SB_def by simp

end
"""

    def write_script(self, theory_name: str, content: str) -> Path:
        """Ecrit le .thy genere dans theory_dir."""
        self.theory_dir.mkdir(parents=True, exist_ok=True)
        path = self.theory_dir / f"{theory_name}.thy"
        path.write_text(content, encoding="utf-8")
        return path

    def validate_theory(self, theory_name: str, timeout: int = 300) -> dict[str, Any]:
        """
        Tente de valider la theorie via `isabelle process -e ...`.
        Si Isabelle non dispo, retourne un statut informatif.
        """
        if not self.is_isabelle_available():
            return {
                "status": "skipped",
                "reason": "Isabelle non disponible dans le PATH (utilisez le conteneur isabelle).",
                "theory": theory_name,
            }
        path = self.theory_dir / f"{theory_name}.thy"
        if not path.exists():
            return {"status": "error", "reason": f"Fichier {path} introuvable."}

        try:
            cmd = [
                "isabelle", "process",
                "-d", str(self.theory_dir),
                "-T", theory_name,
                "-l", self.heap,
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, check=False
            )
            return {
                "status": "ok" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "stdout": result.stdout[-2000:],
                "stderr": result.stderr[-2000:],
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "reason": f"Validation > {timeout}s"}
        except Exception as exc:
            return {"status": "error", "reason": str(exc)}
