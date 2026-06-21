#!/usr/bin/env python3
"""
Test de validation - Vérifie que Claude API key est correctement localisée
"""

import os
import sys
from pathlib import Path

def test_env_file():
    """Teste si .env contient les clés Claude"""
    
    print("\n" + "="*70)
    print("TEST 1: Vérifier .env")
    print("="*70)
    
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env introuvable")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    has_claude = "CLAUDE_API_KEY" in content
    has_anthropic = "ANTHROPIC_API_KEY" in content
    
    print(f"✓ .env trouvé: {env_path.absolute()}")
    print(f"{'✅' if has_claude else '❌'} CLAUDE_API_KEY présente: {has_claude}")
    print(f"{'✅' if has_anthropic else '❌'} ANTHROPIC_API_KEY présente: {has_anthropic}")
    
    return has_claude or has_anthropic


def test_env_loaded():
    """Teste si Python peut charger les clés"""
    
    print("\n" + "="*70)
    print("TEST 2: Charger variables d'environnement")
    print("="*70)
    
    from dotenv import load_dotenv
    
    load_dotenv()
    
    claude_key = os.getenv("CLAUDE_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    print(f"{'✅' if claude_key else '❌'} CLAUDE_API_KEY chargée: {bool(claude_key)}")
    if claude_key:
        print(f"   Commence par: {claude_key[:10]}...")
        print(f"   Longueur: {len(claude_key)} chars")
    
    print(f"{'✅' if anthropic_key else '❌'} ANTHROPIC_API_KEY chargée: {bool(anthropic_key)}")
    if anthropic_key:
        print(f"   Commence par: {anthropic_key[:10]}...")
    
    return bool(claude_key or anthropic_key)


def test_claude_client():
    """Teste si ClaudeClient peut s'initialiser"""
    
    print("\n" + "="*70)
    print("TEST 3: Initialiser ClaudeClient")
    print("="*70)
    
    try:
        from src.core.llm_manager_v2 import ClaudeClient
        
        claude = ClaudeClient()
        
        available = claude.is_available()
        model = claude.model
        
        print(f"{'✅' if available else '⚠️'} Claude disponible: {available}")
        print(f"✓ Modèle: {model}")
        
        if not available:
            print("   Raison: CLAUDE_API_KEY manquante ou invalide")
        
        return available
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_llm_manager():
    """Teste si LLMManager s'initialise correctement"""
    
    print("\n" + "="*70)
    print("TEST 4: Initialiser LLMManager")
    print("="*70)
    
    try:
        from src.core.llm_manager_v2 import LLMManager
        
        config = {
            'llm': {
                'primary': 'ollama',
                'fallback_1': 'claude',
                'fallback_2': 'openai',
                'ollama': {'base_url': 'http://localhost:11434', 'model': 'llama3.2'},
                'claude': {'model': 'claude-3-5-sonnet-20241022'},
                'openai': {'model': 'gpt-4o'}
            }
        }
        
        manager = LLMManager(config)
        
        print(f"✓ LLMManager initialisé")
        print(f"✓ Primaire: {manager.primary}")
        print(f"✓ Fallback 1: {manager.fallback_1}")
        print(f"✓ Fallback 2: {manager.fallback_2}")
        
        claude_avail = manager.claude.is_available()
        print(f"{'✅' if claude_avail else '⚠️'} Claude client disponible: {claude_avail}")
        
        return True
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_key_format():
    """Valide le format de la clé Claude"""
    
    print("\n" + "="*70)
    print("TEST 5: Valider format clé Claude")
    print("="*70)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    key = os.getenv("CLAUDE_API_KEY")
    
    if not key:
        print("⚠️ Clé non trouvée")
        return False
    
    # Validations
    checks = [
        (key.startswith("sk-ant-"), "Commence par 'sk-ant-'"),
        (len(key) > 40, f"Longueur valide ({len(key)} chars)"),
        (all(c.isalnum() or c == '-' for c in key), "Caractères valides (alphanumériques + tirets)"),
    ]
    
    all_valid = True
    for valid, desc in checks:
        print(f"{'✅' if valid else '❌'} {desc}")
        if not valid:
            all_valid = False
    
    return all_valid


def main():
    """Lance tous les tests"""
    
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " VALIDATION CLAUDE API KEY LOCALISATION ".center(68) + "║")
    print("╚" + "="*68 + "╝")
    
    results = {
        "TEST 1: .env": test_env_file(),
        "TEST 2: Variables chargées": test_env_loaded(),
        "TEST 3: ClaudeClient": test_claude_client(),
        "TEST 4: LLMManager": test_llm_manager(),
        "TEST 5: Format clé": test_key_format(),
    }
    
    # Résumé
    print("\n" + "="*70)
    print("RÉSUMÉ FINAL")
    print("="*70)
    
    for test_name, passed in results.items():
        print(f"{'✅' if passed else '❌'} {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ TOUS LES TESTS PASSÉS")
        print("Claude API key est correctement localisée!")
        print("Gabriel utilisera Claude après Ollama timeout.")
    else:
        print("⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("\nActions recommandées:")
        print("1. Vérifier .env contient CLAUDE_API_KEY=sk-ant-xxxxx")
        print("2. Redémarrer Python après modification .env")
        print("3. Vérifier clé est valide (de https://console.anthropic.com/)")
        print("4. Vérifier pas d'espaces autour du '='")
    print("="*70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
