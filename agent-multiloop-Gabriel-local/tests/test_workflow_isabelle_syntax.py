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


class TestMinimalIsabelleInstallation:
    """v3.25.b : verifie l'installation MINIMALE + CACHE (option Philippe c).
    Objectifs : reduire taille disque ~450 MB + accelerer builds suivants
    via cache heap GitHub Actions."""

    @pytest.fixture(scope="class")
    def build_content(self):
        build = REPO_ROOT / ".github" / "workflows" / "build.yml"
        if not build.exists():
            pytest.skip(f"{build} n'existe pas")
        return build.read_text(encoding="utf-8")

    def test_cache_action_present(self, build_content):
        """Un actions/cache@v4 doit etre configure sur ~/.isabelle/heaps."""
        assert "actions/cache@v4" in build_content, (
            "Le workflow doit utiliser actions/cache@v4 pour la heap Isabelle"
        )
        assert "~/.isabelle/Isabelle2024/heaps" in build_content, (
            "Le chemin de cache doit inclure ~/.isabelle/Isabelle2024/heaps"
        )

    def test_cache_key_uses_hashfiles_on_thy(self, build_content):
        """La cle de cache doit dependre du contenu de methode_spectral.thy
        pour invalider automatiquement le cache si la theorie change."""
        assert "hashFiles" in build_content
        assert "methode_spectral.thy" in build_content
        assert "ROOT" in build_content

    def test_cache_hit_skips_install(self, build_content):
        """Si le cache est present, l'installation Isabelle est skippee."""
        # 'if: steps.cache-isabelle-heap.outputs.cache-hit != true'
        assert "cache-isabelle-heap.outputs.cache-hit != 'true'" in build_content, (
            "L'etape d'install Isabelle doit etre conditionnee au cache miss"
        )
        # Une etape de restore PATH doit exister pour cache-hit=true
        assert "cache-isabelle-heap.outputs.cache-hit == 'true'" in build_content, (
            "Une etape doit restaurer le PATH quand le cache hit"
        )

    @pytest.mark.parametrize("removed_component", [
        "isabelle/doc/",                # Documentation PDF ~200 MB (SEUL safe)
    ])
    def test_minimal_removes_unused_components(self, build_content, removed_component):
        """L'installation minimale ULTRA-prudente supprime UNIQUEMENT doc/
        (les PDFs finaux). Tous les autres composants sont references dans
        les settings/build.props/env vars d'Isabelle et cassent le build
        si supprimes."""
        assert removed_component in build_content, (
            f"L'installation minimale doit supprimer `{removed_component}`"
        )

    def test_no_removal_of_referenced_components(self, build_content):
        """CRITIQUE : ne PAS supprimer les composants references dans
        etc/build.props ou etc/settings d'Isabelle.
        Bugs reportes :
        - 2026-07-10 (a) : contrib/z3-* + src/Tools/jEdit/ -> 'Missing component'
        - 2026-07-10 (b) : contrib/isabelle_fonts-* -> 'Undefined ISABELLE_FONTS'
        """
        forbidden_removals = [
            r"rm\s+-rf\s+.*contrib/z3-",
            r"rm\s+-rf\s+.*contrib/cvc",
            r"rm\s+-rf\s+.*contrib/jedit_build",
            r"rm\s+-rf\s+.*contrib/jortho",
            r"rm\s+-rf\s+.*contrib/isabelle_fonts-",  # AJOUTE (bug 2026-07-10b)
            r"rm\s+-rf\s+.*src/Tools/jEdit",
        ]
        import re
        for pat in forbidden_removals:
            assert not re.search(pat, build_content), (
                f"Suppression interdite detectee : pattern `{pat}` "
                f"est reference dans Isabelle (build.props/settings/env)."
            )


class TestDetailedErrorReporting:
    """v3.26 : le workflow doit afficher les erreurs Isabelle detaillees
    (numeros de ligne, type d'erreur) via isabelle build_log."""

    @pytest.fixture(scope="class")
    def build_content(self):
        build = REPO_ROOT / ".github" / "workflows" / "build.yml"
        if not build.exists():
            pytest.skip(f"{build} n'existe pas")
        return build.read_text(encoding="utf-8")

    def test_build_log_error_command(self, build_content):
        """Sur echec, isabelle build_log -H Error doit etre invoque."""
        assert "isabelle build_log -H Error Methode_Spectral" in build_content, (
            "Le workflow doit invoquer 'isabelle build_log -H Error' "
            "pour afficher les erreurs Isabelle detaillees en cas d'echec"
        )

    def test_failure_step_conditional(self, build_content):
        """L'etape 'Affichage detaille des erreurs' doit etre conditionnee
        au fait que le build a echoue (if: failure())."""
        assert "if: failure()" in build_content or "if: ${{ failure()" in build_content

    def test_build_output_log_captured(self, build_content):
        """La sortie doit etre capturee dans build_output.log via tee."""
        assert "tee build_output.log" in build_content

    def test_env_vars_verification_step(self, build_content):
        """Une etape de verification des variables env Isabelle doit exister
        pour diagnostiquer les problemes d'ISABELLE_FONTS, ML_HOME, etc."""
        assert "isabelle getenv" in build_content or "getenv ISABELLE_HOME" in build_content

    def test_polyml_and_jdk_preserved(self, build_content):
        """CRITIQUE : polyml (moteur ML) et jdk (JVM) NE doivent PAS
        etre supprimes — Isabelle en depend imperativement."""
        # On verifie qu'aucune ligne `rm -rf ...polyml*` n'existe
        import re
        assert not re.search(r"rm\s+-rf\s+.*polyml-", build_content), (
            "polyml est requis par Isabelle. Ne JAMAIS le supprimer."
        )
        assert not re.search(r"rm\s+-rf\s+.*jdk-", build_content), (
            "jdk est requis par Isabelle (JVM). Ne JAMAIS le supprimer."
        )
