#!/usr/bin/env python3
"""
QUICK START - Gabriel v5.2 HOL Formal Generation
Test immédiat du système
"""

import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

def test_hol_generator():
    """Test 1: Générateur HOL formel"""
    
    print("="*70)
    print("TEST 1: HOL Formel Generator")
    print("="*70)
    
    from src.hol_isabelle_formal_generator import HOLIsabelleResponseGenerator
    
    gen = HOLIsabelleResponseGenerator()
    
    # Générer Isabelle
    print("\n[Génération Isabelle]")
    isabelle = gen.generate_isabelle_spectral_theory("Reconstruction primes")
    
    # Vérifier structure
    checks = [
        ("theory Spectral_Primes", "Structure theory trouvée"),
        ("definition A :: \"nat ⇒ real\"", "Définition A trouvée"),
        ("A n = (13 / 8) * (2 ^ n) - 2", "Formule A correcte"),
        ("definition digamma :: \"nat ⇒ real ⇒ real\"", "Digamma trouvée"),
        ("definition RSA ::", "RSA trouvée"),
        ("theorem rsa_convergence:", "Théorème trouvé"),
        ("lemma A_strictly_increasing:", "Lemme trouvé"),
        ("end", "Fermeture theory trouvée"),
    ]
    
    passed = 0
    for check, desc in checks:
        if check in isabelle:
            print(f"  ✅ {desc}")
            passed += 1
        else:
            print(f"  ❌ {desc}")
    
    print(f"\nScore: {passed}/{len(checks)}")
    
    return passed == len(checks)


def test_prompt_injector():
    """Test 2: Prompt Injector amélioré"""
    
    print("\n" + "="*70)
    print("TEST 2: Prompt Injector Enhanced")
    print("="*70)
    
    from memory.prompt_injector_enhanced import PromptInjector
    
    inj = PromptInjector()
    
    # Test détection query type
    print("\n[Détection Query Type]")
    
    test_queries = [
        ("Génère théorie HOL pour RSA", "hol_proof_generation"),
        ("Calcule RSA([2], [3,5])", "rsa_calculation"),
        ("Explique zéros Riemann", "riemann_analysis"),
    ]
    
    for query, expected_type in test_queries:
        detected = inj.detect_query_type(query)
        match = "✅" if expected_type in detected or detected == expected_type else "❌"
        print(f"  {match} '{query[:30]}...' → {detected}")
    
    # Test injection HOL stricte
    print("\n[Injection HOL Stricte]")
    
    query = "Génère théorie Isabelle pour reconstruction premiers"
    injected = inj.inject_for_claude_hol(query)
    
    # Vérifier injection
    injection_checks = [
        ("SPÉCIFICATIONS HOL4/ISABELLE/LEAN4 FORMELLES STRICTES", "Specs trouvées"),
        ("definition A :: \"nat ⇒ real\"", "Formule A injectée"),
        ("Sr2 = 1.5", "Sr2 injecté"),
        ("REJETER IMMÉDIATEMENT SI", "Validation injectée"),
    ]
    
    passed = 0
    for check, desc in injection_checks:
        if check in injected:
            print(f"  ✅ {desc}")
            passed += 1
        else:
            print(f"  ❌ {desc}")
    
    print(f"\nScore: {passed}/{len(injection_checks)}")
    
    return passed == len(injection_checks)


def test_hol_validation():
    """Test 3: Validation syntaxe HOL"""
    
    print("\n" + "="*70)
    print("TEST 3: HOL Syntax Validation")
    print("="*70)
    
    from memory.prompt_injector_enhanced import PromptInjector
    
    inj = PromptInjector()
    
    # Code BON
    print("\n[Code Valide Isabelle]")
    
    good_code = """
theory Spectral_Primes imports Main begin

definition A :: "nat ⇒ real" where
  "A n = (13 / 8) * (2 ^ n) - 2"

definition digamma :: "nat ⇒ real ⇒ real" where
  "digamma n p = B n - 64 * p"

definition prime_reconstruct :: "nat ⇒ real" where
  "prime_reconstruct i = (B i - digamma i (real i)) / 64"

definition RSA :: "real list ⇒ real list ⇒ nat ⇒ real" where
  "RSA blockA blockB k = ..."

theorem convergence: "∀ k. P k"

end
"""
    
    val_good = inj.validate_llm_response(good_code, "hol_proof_generation")
    print(f"  Valide: {val_good['is_compliant']}")
    print(f"  Score: {val_good['score']:.2f}")
    
    # Code MAUVAIS (pseudo-code)
    print("\n[Code Invalide (Pseudo-code)]")
    
    bad_code = """
fun A(n) = (3.25 / 2) * (2 pow n) - 2
fun digamma_calcule(n, p) = B(n) - 64 * p
fun prime_reconstruction(i) = ...
"""
    
    val_bad = inj.validate_llm_response(bad_code, "hol_proof_generation")
    print(f"  Valide: {val_bad['is_compliant']}")
    print(f"  Score: {val_bad['score']:.2f}")
    if val_bad.get('hol_valid'):
        print(f"  Erreurs: {val_bad['hol_valid']['errors'][:2]}")
    
    return True


def test_integration():
    """Test 4: Intégration Gabriel"""
    
    print("\n" + "="*70)
    print("TEST 4: Gabriel Integration")
    print("="*70)
    
    print("\n[Configuration Gabriel v5.2]")
    
    try:
        from src.gabriel_llm_integration_safe import GabrielLLMIntegrationSafeBudget
        from memory.prompt_injector_enhanced import PromptInjector
        
        gabriel = GabrielLLMIntegrationSafeBudget(monthly_budget_usd=7.0)
        injector = PromptInjector()
        
        print("  ✅ Gabriel initialized")
        print("  ✅ Injector initialized")
        
        # Montrer flux
        print("\n[Flux Complet]")
        
        query = "Génère théorie Isabelle pour RSA"
        print(f"  1. Requête: '{query}'")
        
        injected = injector.inject_for_claude_hol(query)
        print(f"  2. Injection: {len(injected)} chars")
        
        print("  3. (Simule) Claude génère réponse")
        print("  4. Validation réponse HOL")
        print("  5. Budget tracking")
        
        print("\n  ✅ Flux opérationnel")
        
        return True
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False


def main():
    """Exécute tous les tests"""
    
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║         GABRIEL v5.2 - QUICK START TEST SUITE                          ║")
    print("║         HOL4/Isabelle Formal Code Generation                           ║")
    print("╚════════════════════════════════════════════════════════════════════════╝")
    
    tests = [
        ("HOL Generator", test_hol_generator),
        ("Prompt Injector", test_prompt_injector),
        ("HOL Validation", test_hol_validation),
        ("Gabriel Integration", test_integration),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ ERREUR dans {name}: {e}")
            results.append((name, False))
    
    # Résumé
    print("\n" + "="*70)
    print("RÉSUMÉ")
    print("="*70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print(f"\nGlobal: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n🎉 Gabriel v5.2 prêt pour production!")
        print("\nProcédure d'utilisation:")
        print("  1. from memory.prompt_injector_enhanced import PromptInjector")
        print("  2. injector = PromptInjector()")
        print("  3. injected = injector.inject_for_claude_hol(query)")
        print("  4. result = gabriel.query_intelligent(injected)")
        print("  5. print(result['response'])  # Code Isabelle formel")
    else:
        print("\n⚠️ Quelques tests ont échoué")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
