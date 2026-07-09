"""
Tests v3.25 : verifie que les workflows GitHub Actions Isabelle utilisent
la syntaxe CORRECTE.

Bug reporte par Philippe : la commande `isabelle process -T ./theories/xxx.thy`
etait INVALIDE (l'option -T attend un nom de theorie sans extension, ou on
utilise `isabelle build -D .` avec un fichier ROOT). Ceci causait l'erreur
`Malformed theory import`.

Ce test scanne TOUS les workflows .yml et refuse les patterns buggues.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path("/app")
LOCAL_ROOT = REPO_ROOT / "agent-multiloop-Gabriel-local"


def _workflow_files():
    """Retourne tous les fichiers .yml dans .github/workflows/ des 2 racines."""
    files = []
    for base in (REPO_ROOT, LOCAL_ROOT):
        wf_dir = base / ".github" / "workflows"
        if wf_dir.exists():
            files.extend(sorted(wf_dir.glob("*.yml")))
    return files


class TestNoInvalidIsabelleCommand:
    """Regression : le pattern `isabelle process -T ./PATH.thy` est INVALIDE
    et cause 'Malformed theory import'. Il ne doit apparaitre dans AUCUN
    workflow YAML."""

    @pytest.mark.parametrize("wf", _workflow_files(), ids=str)
    def test_no_process_dash_T_with_dotthy_path(self, wf):
        content = wf.read_text(encoding="utf-8")
        # Pattern buggue : "process -T " suivi d'un chemin se terminant par ".thy"
        import re
        bad = re.findall(r"isabelle\s+process\s+-T\s+\S+\.thy", content)
        assert not bad, (
            f"Workflow {wf} contient la commande INVALIDE : {bad}. "
            f"Utiliser `isabelle build -D .` avec un fichier ROOT a la place."
        )

    @pytest.mark.parametrize("wf", _workflow_files(), ids=str)
    def test_no_relative_path_prefix_theory_arg(self, wf):
        """Pattern `-T ./xxx` ou `-T ./theories/xxx.thy` est aussi mauvais."""
        content = wf.read_text(encoding="utf-8")
        import re
        # Chercher `-T ./` suivi d'un chemin (n'importe quelle option Isabelle)
        bad = re.findall(r"isabelle\s+\S+\s+-T\s+\./\S+", content)
        assert not bad, (
            f"Workflow {wf} passe un chemin relatif `./...` a `-T`. "
            f"L'option `-T` attend un nom de theorie (sans extension)."
        )


class TestRootFileExists:
    """Le fichier ROOT Isabelle doit exister pour permettre `isabelle build -D .`."""

    def test_theories_ROOT_exists(self):
        root = LOCAL_ROOT / "theories" / "ROOT"
        assert root.exists(), (
            "Le fichier `theories/ROOT` doit exister pour declarer la session "
            "Isabelle 'Methode_Spectral'."
        )

    def test_ROOT_declares_methode_spectral_session(self):
        root = LOCAL_ROOT / "theories" / "ROOT"
        content = root.read_text(encoding="utf-8")
        assert "session \"Methode_Spectral\"" in content
        assert "methode_spectral" in content
        assert "HOL-Computational_Algebra" in content


class TestBuildWorkflowUsesIsabelleBuild:
    """Le workflow doit utiliser `isabelle build -D .` (pas `process -T`)."""

    def test_root_build_yml_uses_isabelle_build(self):
        build = REPO_ROOT / ".github" / "workflows" / "build.yml"
        if not build.exists():
            pytest.skip(f"{build} n'existe pas")
        content = build.read_text(encoding="utf-8")
        assert "isabelle build" in content, (
            "Le workflow doit utiliser `isabelle build -D .` "
            "(commande standard pour compiler une session Isabelle)."
        )

    def test_paths_point_to_correct_theories(self):
        """Verifie que les chemins pointent bien vers
        agent-multiloop-Gabriel-local/theories/methode_spectral.thy
        (et non l'ancien src/hol/ inexistant)."""
        build = REPO_ROOT / ".github" / "workflows" / "build.yml"
        if not build.exists():
            pytest.skip(f"{build} n'existe pas")
        content = build.read_text(encoding="utf-8")
        # L'ancien chemin src/hol/ ne doit plus apparaitre
        assert "src/hol/methode_spectral.thy" not in content, (
            "Le workflow reference encore l'ancien chemin `src/hol/...` "
            "qui n'existe pas. Corriger vers "
            "`agent-multiloop-Gabriel-local/theories/methode_spectral.thy`."
        )
