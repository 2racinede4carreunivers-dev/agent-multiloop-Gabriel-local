"""
LLM Manager v2 - Chaîne de fallback: Ollama → Claude → OpenAI
Nouvelle priorité: Claude est PRIORITAIRE après Ollama
"""
from __future__ import annotations

import logging
from typing import Any

from ..adapters.llm.ollama_client import OllamaClient
from ..adapters.llm.openai_client import OpenAIClient
from ..adapters.llm.utf8_sanitizer import UTF8Sanitizer

logger = logging.getLogger(__name__)

# Nouvelles imports Claude
try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False


class ClaudeClient:
    """Client Anthropic Claude - nouveau dans v2"""
    
    def __init__(self, api_key: str | None = None,
                 model: str | None = None,
                 temperature: float = 0.7, max_tokens: int = 4096, timeout: float = 60):
        import os

        self.api_key = api_key or os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        # Detection des placeholders d'un .env non rempli -> on neutralise
        if self.api_key:
            placeholders = ("COLLEZ", "VOTRE", "PLACEHOLDER", "sk-ant-[")
            if any(self.api_key.upper().startswith(p.upper()) for p in placeholders):
                logger.warning(
                    "CLAUDE_API_KEY contient un placeholder (%s...) - "
                    "Claude desactive jusqu'a saisie d'une cle reelle sk-ant-...",
                    self.api_key[:20],
                )
                self.api_key = None
        # Modele : argument explicite > variable d'env > defaut Sonnet 4.5
        self.model = (
            model
            or os.getenv("CLAUDE_MODEL")
            or "claude-sonnet-4-5-20250929"
        )
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        
        self.client = None
        if self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info(f"✅ Claude client initialized: {model}")
            except Exception as e:
                logger.error(f"❌ Claude initialization failed: {e}")
    
    def is_available(self) -> bool:
        """Vérifie si Claude est disponible"""
        return self.client is not None and self.api_key is not None
    
    async def generate(self, prompt: str, system: str | None = None, 
                      temperature: float | None = None) -> str:
        """Génère réponse via Claude API"""
        
        if not self.is_available():
            return ""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system or "Tu es Gabriel, un expert en mathématiques et géométrie spectrale.",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature or self.temperature,
                timeout=self.timeout
            )
            
            return response.content[0].text
        
        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            return ""
        except Exception as e:
            logger.error(f"Claude generation error: {e}")
            return ""
    
    async def chat(self, messages: list[dict], temperature: float | None = None) -> str:
        """Chat multi-tours avec Claude"""
        
        if not self.is_available():
            return ""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=messages,
                temperature=temperature or self.temperature,
                timeout=self.timeout
            )
            
            return response.content[0].text
        
        except Exception as e:
            logger.error(f"Claude chat error: {e}")
            return ""


class LLMManager:
    """
    LLM Manager v2 - Chaîne de fallback RÉVISÉE
    
    NOUVELLE PRIORITÉ:
    1. Ollama (10s timeout) - local, rapide
    2. Claude (60s timeout) - expert logique, tâches complexes
    3. OpenAI (90s timeout) - fallback ultime
    """

    def __init__(self, config: dict[str, Any]):
        llm_cfg = config.get("llm", {})
        ollama_cfg = llm_cfg.get("ollama", {})
        claude_cfg = llm_cfg.get("claude", {})
        openai_cfg = llm_cfg.get("openai", {})

        # Configuration primaire/fallbacks
        self.primary = llm_cfg.get("primary", "ollama")
        self.fallback_1 = llm_cfg.get("fallback_1", "claude")  # NOUVEAU: Claude est fallback 1
        self.fallback_2 = llm_cfg.get("fallback_2", "openai")  # OpenAI est fallback 2

        # Initialiser clients
        self.ollama = OllamaClient(
            base_url=ollama_cfg.get("base_url"),
            model=ollama_cfg.get("model", "llama3.2"),
            timeout=float(ollama_cfg.get("timeout_seconds", 10)),  # 10s Ollama
        )

        self.claude = ClaudeClient(
            api_key=None,  # lit depuis env CLAUDE_API_KEY ou ANTHROPIC_API_KEY
            model=claude_cfg.get("model") or None,  # None -> lit CLAUDE_MODEL ou defaut Sonnet 4.5
            temperature=float(claude_cfg.get("temperature", 0.7)),
            max_tokens=int(claude_cfg.get("max_tokens", 4096)),
            timeout=float(claude_cfg.get("timeout_seconds", 60)),  # 60s Claude
        )

        self.openai = OpenAIClient(
            api_key=None,  # lit depuis env OPENAI_API_KEY
            model=openai_cfg.get("model", "gpt-4o"),
            temperature=float(openai_cfg.get("temperature", 0.2)),
            max_tokens=int(openai_cfg.get("max_tokens", 4096)),
            timeout=float(openai_cfg.get("timeout_seconds", 90)),  # 90s OpenAI
        )

        self._ollama_available: bool | None = None  # cache

        logger.info("✅ LLM Manager v2 Initialized")
        logger.info("   Chaîne fallback: Ollama (10s) → Claude (60s) → OpenAI (90s)")

    async def _check_ollama(self) -> bool:
        if self._ollama_available is None:
            self._ollama_available = await self.ollama.is_available()
        return self._ollama_available

    async def generate(self, prompt: str, system: str | None = None, temperature: float = 0.2) -> str:
        """
        NOUVELLE LOGIQUE:
        1. Tenter Ollama (10s timeout)
        2. Si échec → Tenter Claude (60s timeout) ← PRIORITÉ SUR OpenAI
        3. Si échec → Tenter OpenAI (90s timeout)
        4. Si tout échoue → Erreur
        """
        # Sanitization UTF-8 contre les surrogates (\udcc3 etc.) qui font crasher
        # le client HTTP des LLM lors de l'encodage. Sans coût pour les
        # textes deja propres.
        prompt = UTF8Sanitizer.sanitize(prompt) if prompt else prompt
        if system:
            system = UTF8Sanitizer.sanitize(system)
        
        # ========== ÉTAPE 1: OLLAMA ==========
        if self.primary == "ollama" and await self._check_ollama():
            logger.info("🔵 Tentative 1/3: Ollama (llama3.2) - timeout 10s")
            result = await self.ollama.generate(prompt, system=system, temperature=temperature)
            if result and len(result.strip()) > 0:
                logger.info("✅ Ollama a répondu")
                return result
            logger.warning("⚠️ Ollama timeout ou réponse vide (10s expiré)")
        elif self.primary == "ollama":
            logger.warning("⚠️ Ollama indisponible (daemon non détecté)")

        # ========== ÉTAPE 2: CLAUDE (NOUVEAU) ==========
        if self.claude.is_available():
            logger.info("🔴 Tentative 2/3: Claude-3.5-Sonnet - timeout 60s")
            result = await self.claude.generate(prompt, system=system, temperature=temperature)
            if result and len(result.strip()) > 0:
                logger.info("✅ Claude a répondu")
                return result
            logger.warning("⚠️ Claude timeout ou erreur")
        else:
            logger.warning("⚠️ Claude indisponible (CLAUDE_API_KEY manquante)")

        # ========== ÉTAPE 3: OPENAI ==========
        if self.openai.is_available():
            logger.info("🟢 Tentative 3/3: OpenAI (gpt-4o) - timeout 90s")
            result = await self.openai.generate(prompt, system=system, temperature=temperature)
            if result and len(result.strip()) > 0:
                logger.info("✅ OpenAI a répondu")
                return result
            logger.error("❌ OpenAI timeout ou erreur")
        else:
            logger.error("❌ OpenAI indisponible (OPENAI_API_KEY manquante)")

        # ========== ERREUR CRITIQUE ==========
        logger.critical("❌ TOUS LES LLM ONT ÉCHOUÉ")
        return "[ERREUR LLM] Ollama, Claude ET OpenAI sont inaccessibles."

    async def chat(self, messages: list[dict], temperature: float = 0.2) -> str:
        """
        Chat multi-tours avec même logique de fallback:
        Ollama → Claude → OpenAI
        """
        # Sanitization UTF-8 de chaque tour de chat
        sanitized: list[dict] = []
        for msg in messages:
            new_msg = dict(msg)
            if isinstance(new_msg.get("content"), str):
                new_msg["content"] = UTF8Sanitizer.sanitize(new_msg["content"])
            sanitized.append(new_msg)
        messages = sanitized
        
        # OLLAMA
        if self.primary == "ollama" and await self._check_ollama():
            logger.info("🔵 Chat Ollama")
            result = await self.ollama.chat(messages, temperature=temperature)
            if result:
                return result
            logger.warning("⚠️ Ollama chat vide, fallback Claude")

        # CLAUDE (NOUVEAU)
        if self.claude.is_available():
            logger.info("🔴 Chat Claude")
            result = await self.claude.chat(messages, temperature=temperature)
            if result:
                return result
            logger.warning("⚠️ Claude chat vide, fallback OpenAI")

        # OPENAI
        if self.openai.is_available():
            logger.info("🟢 Chat OpenAI")
            result = await self.openai.chat(messages, temperature=temperature)
            if result:
                return result
            logger.error("❌ OpenAI chat vide")

        return "[ERREUR LLM] Chat indisponible"


# ============================================================
# DEBUG: Affiche configuration fallback
# ============================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*70)
    print("LLM MANAGER v2 - CONFIGURATION FALLBACK")
    print("="*70)
    
    print("""
    NOUVELLE CHAÎNE DE FALLBACK:
    
    1️⃣ OLLAMA (llama3.2)
       └─ Timeout: 10s
       └─ Local, rapide
       └─ Si timeout → passer à Claude
    
    2️⃣ CLAUDE (claude-3-5-sonnet) ⭐ NOUVEAU - PRIORITAIRE
       └─ Timeout: 60s
       └─ Expert logique & mathématiques
       └─ Si timeout/erreur → passer à OpenAI
    
    3️⃣ OPENAI (gpt-4o)
       └─ Timeout: 90s
       └─ Fallback ultime
       └─ Si timeout/erreur → ERREUR CRITIQUE
    
    CHANGEMENT MAJEUR:
    ❌ AVANT: Ollama → OpenAI (Claude jamais utilisé)
    ✅ APRÈS: Ollama → Claude → OpenAI (Claude prioritaire!)
    
    RÉSULTAT:
    • Questions mathématiques: Claude prend le relais (expert)
    • Réponses plus rigoureuses & HOL4 certifiées
    • OpenAI reste fallback ultime (moins expert)
    """)
    
    print("="*70)
