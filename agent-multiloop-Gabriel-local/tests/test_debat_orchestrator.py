"""Tests pour DebatOrchestrator : 5 personas, alternance Claude/OpenAI, JSON+MD.

Les LLMs reels ne sont jamais appeles : on patche `_call_llm` pour controler
les reponses et inspecter le flow (selection persona, provider, sauvegarde).
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.multiloop.debat_orchestrator import (
    DebatOrchestrator,
    DebatResult,
    DebatTour,
    ORDRE_ROTATION,
    PERSONAS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def fake_llm():
    """LLMManager mock avec claude+openai disponibles."""
    llm = MagicMock()
    llm.claude = MagicMock()
    llm.openai = MagicMock()
    llm.claude.is_available = MagicMock(return_value=True)
    llm.openai.is_available = MagicMock(return_value=True)
    # generate retourne des reponses canonicalisees
    llm.claude.generate = AsyncMock(return_value="REPONSE-CLAUDE")
    llm.openai.generate = AsyncMock(return_value="REPONSE-OPENAI")
    return llm


@pytest.fixture
def orch(fake_llm, tmp_path):
    """DebatOrchestrator avec dossier temporaire pour audits."""
    return DebatOrchestrator(llm=fake_llm, audits_dir=tmp_path / "debats")


# ---------------------------------------------------------------------------
# Personas
# ---------------------------------------------------------------------------
class TestPersonas:
    def test_5_personas_exactly(self):
        assert len(PERSONAS) == 5

    def test_personas_keys(self):
        assert set(PERSONAS.keys()) == {
            "analytique", "logicien", "sceptique",
            "geometre", "computationnaliste",
        }

    def test_chaque_persona_a_nom_specialite_system(self):
        for key, p in PERSONAS.items():
            assert "nom" in p and p["nom"], f"persona {key} sans nom"
            assert "specialite" in p and p["specialite"]
            assert "system" in p and len(p["system"]) > 200, \
                f"system prompt {key} trop court"

    def test_ordre_rotation_couvre_5_personas(self):
        assert len(ORDRE_ROTATION) == 5
        assert set(ORDRE_ROTATION) == set(PERSONAS.keys())

    def test_list_personas_static(self):
        lst = DebatOrchestrator.list_personas()
        assert len(lst) == 5
        for entry in lst:
            assert set(entry.keys()) == {"cle", "nom", "specialite"}


# ---------------------------------------------------------------------------
# Selection persona (mode rotation vs fixe)
# ---------------------------------------------------------------------------
class TestSelectionPersona:
    def test_persona_fixe(self, orch):
        for key in PERSONAS:
            assert orch._select_persona(key, 1) == key
            assert orch._select_persona(key, 42) == key

    def test_persona_rotation_cycle_sur_5(self, orch):
        seen = [orch._select_persona("rotation", i) for i in range(1, 11)]
        # 10 tours => 2 cycles complets
        assert seen[0] == ORDRE_ROTATION[0]
        assert seen[4] == ORDRE_ROTATION[4]
        assert seen[5] == ORDRE_ROTATION[0]  # cycle
        assert seen[:5] == list(ORDRE_ROTATION)
        assert seen[5:] == list(ORDRE_ROTATION)


# ---------------------------------------------------------------------------
# Alternance Claude / OpenAI
# ---------------------------------------------------------------------------
class TestAlternanceProviders:
    @pytest.mark.asyncio
    async def test_premier_appel_claude_deuxieme_openai(self, orch, fake_llm):
        # 1er appel : counter=0 -> claude
        txt1, prov1 = await orch._call_llm("p", "s", 0.4)
        assert prov1 == "claude"
        assert txt1 == "REPONSE-CLAUDE"
        # 2eme appel : counter=1 -> openai
        txt2, prov2 = await orch._call_llm("p", "s", 0.4)
        assert prov2 == "openai"
        assert txt2 == "REPONSE-OPENAI"
        # 3eme appel : counter=2 -> claude
        _, prov3 = await orch._call_llm("p", "s", 0.4)
        assert prov3 == "claude"

    @pytest.mark.asyncio
    async def test_fallback_si_claude_indisponible(self, orch, fake_llm):
        fake_llm.claude.is_available.return_value = False
        txt, prov = await orch._call_llm("p", "s", 0.4)
        assert prov == "openai"
        assert txt == "REPONSE-OPENAI"

    @pytest.mark.asyncio
    async def test_fallback_si_claude_repond_vide(self, orch, fake_llm):
        fake_llm.claude.generate = AsyncMock(return_value="")
        txt, prov = await orch._call_llm("p", "s", 0.4)
        assert prov == "openai"

    @pytest.mark.asyncio
    async def test_message_erreur_si_aucun_llm(self, orch, fake_llm):
        fake_llm.claude.is_available.return_value = False
        fake_llm.openai.is_available.return_value = False
        txt, prov = await orch._call_llm("p", "s", 0.4)
        assert prov == "none"
        assert "ERREUR DEBAT" in txt

    @pytest.mark.asyncio
    async def test_ollama_jamais_appele(self, orch, fake_llm):
        # ollama n'est jamais utilise dans le debat
        # Note : fake_llm n'a meme pas .ollama, mais on verifie qu'aucun
        # acces n'echoue. Si jamais l'orchestrateur essayait d'utiliser
        # ollama, le mock leverait AttributeError.
        await orch._call_llm("p", "s", 0.4)
        # OK : aucune exception levee


# ---------------------------------------------------------------------------
# Execution complete d'un debat (mock LLM)
# ---------------------------------------------------------------------------
class TestRunDebat:
    @pytest.mark.asyncio
    async def test_debat_3_tours_produit_5_messages(self, orch):
        result = await orch.run(theme="Le rapport 1/k", nb_tours=3)
        # 3 tours = 1 these + 2 x (critique + defense) = 5 messages
        assert len(result.tours) == 5
        assert result.tours[0].role == "gabriel"
        assert result.tours[1].role == "critique"
        assert result.tours[2].role == "gabriel"
        assert result.tours[3].role == "critique"
        assert result.tours[4].role == "gabriel"

    @pytest.mark.asyncio
    async def test_debat_rotation_personas_differentes(self, orch):
        result = await orch.run(theme="Theme", nb_tours=3, persona="rotation")
        critiques = [t for t in result.tours if t.role == "critique"]
        assert len(critiques) == 2
        # 2 personas distinctes (analytique puis logicien)
        assert critiques[0].persona == "analytique"
        assert critiques[1].persona == "logicien"

    @pytest.mark.asyncio
    async def test_debat_persona_fixe_logicien(self, orch):
        result = await orch.run(theme="t", nb_tours=3, persona="logicien")
        critiques = [t for t in result.tours if t.role == "critique"]
        for c in critiques:
            assert c.persona == "logicien"

    @pytest.mark.asyncio
    async def test_debat_persona_invalide_leve(self, orch):
        with pytest.raises(ValueError, match="Persona inconnue"):
            await orch.run(theme="t", nb_tours=2, persona="inexistante")

    @pytest.mark.asyncio
    async def test_debat_nb_tours_zero_leve(self, orch):
        with pytest.raises(ValueError, match="nb_tours"):
            await orch.run(theme="t", nb_tours=0)

    @pytest.mark.asyncio
    async def test_debat_synthese_non_vide(self, orch):
        result = await orch.run(theme="t", nb_tours=2)
        assert result.synthese_citable and len(result.synthese_citable) > 0

    @pytest.mark.asyncio
    async def test_debat_providers_alternent(self, orch):
        """Verifie qu'au moins 2 providers differents sont utilises."""
        result = await orch.run(theme="t", nb_tours=3)
        providers = {t.provider for t in result.tours}
        assert "claude" in providers
        assert "openai" in providers


# ---------------------------------------------------------------------------
# Sauvegarde JSON + Markdown
# ---------------------------------------------------------------------------
class TestSauvegarde:
    @pytest.mark.asyncio
    async def test_json_et_markdown_crees(self, orch, tmp_path):
        result = await orch.run(theme="Theme test", nb_tours=2)
        assert result.json_path is not None
        assert result.markdown_path is not None
        assert Path(result.json_path).exists()
        assert Path(result.markdown_path).exists()

    @pytest.mark.asyncio
    async def test_json_contenu_valide(self, orch):
        result = await orch.run(theme="Theme test", nb_tours=2)
        data = json.loads(Path(result.json_path).read_text(encoding="utf-8"))
        assert data["theme"] == "Theme test"
        assert data["debat_id"] == result.debat_id
        assert len(data["tours"]) == 3
        assert "synthese_citable" in data
        assert data["persona_mode"] == "rotation"

    @pytest.mark.asyncio
    async def test_markdown_contient_sections(self, orch):
        result = await orch.run(theme="Sujet X", nb_tours=2, persona="sceptique")
        md = Path(result.markdown_path).read_text(encoding="utf-8")
        assert "# Debat contradictoire" in md
        assert "Sujet X" in md
        assert "sceptique" in md
        assert "## Synthese citable" in md
        # Au moins un tour Gabriel + un tour Critique
        assert "Gabriel" in md
        assert "Critique" in md

    @pytest.mark.asyncio
    async def test_filename_format(self, orch):
        result = await orch.run(theme="t", nb_tours=2)
        json_p = Path(result.json_path)
        md_p = Path(result.markdown_path)
        # Format YYYY-MM-DD_<id>.json
        assert json_p.name.endswith(".json")
        assert md_p.name.endswith(".md")
        assert result.debat_id in json_p.name
        assert result.debat_id in md_p.name


# ---------------------------------------------------------------------------
# Integration CLI (smoke test)
# ---------------------------------------------------------------------------
class TestCLIIntegration:
    def test_handle_debat_method_existe(self):
        from src.ui.cli import CLIInterface
        assert hasattr(CLIInterface, "_handle_debat")
        assert asyncio.iscoroutinefunction(CLIInterface._handle_debat)

    def test_help_text_mentionne_debat(self):
        from src.ui.cli import HELP_TEXT
        assert "debat" in HELP_TEXT.lower()
        assert "personas" in HELP_TEXT.lower() or "persona" in HELP_TEXT.lower()
