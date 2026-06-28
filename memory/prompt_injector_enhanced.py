"""
Prompt Injector Enhanced - Injecte axiomes théorie + spécifications HOL formelles
Intercepte appels Ollama/Claude/OpenAI avec exigences rigoureuses HOL4/Isabelle
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import sys
from pathlib import Path

# Importer manager axiomes
sys.path.insert(0, str(Path(__file__).parent.parent))
from memory.theory_axioms_manager import TheoryAxiomsManager

logger = logging.getLogger(__name__)

@dataclass
class PromptContext:
    """Contexte pour injection axiomes"""
    original_query: str
    query_type: str  # 'rsa_calculation', 'riemann_analysis', etc.
    include_axioms: bool = True
    include_directives: bool = True
    include_parameters: bool = True
    include_hol_specs: bool = False  # Spécifications HOL formelles
    target_llm: str = "ollama"  # ollama, openai, claude, wolfram

class PromptInjector:
    """Injecte axiomes théorie avant envoi requête LLM"""
    
    def __init__(self, memory_path: str = "memory"):
        self.manager = TheoryAxiomsManager(memory_path)
        self.injection_count = 0
        self.cache = {}
    
    def inject_axioms(self, query: str, query_type: str = "riemann_analysis") -> str:
        """
        Injecte axiomes avant requête
        
        Args:
            query: Requête originale utilisateur
            query_type: Type de requête
        
        Returns:
            Requête augmentée avec axiomes
        """
        
        # Vérifier cache
        cache_key = f"{query}_{query_type}"
        if cache_key in self.cache:
            logger.debug(f"Injection en cache: {query_type}")
            return self.cache[cache_key]
        
        # Créer contexte
        ctx = PromptContext(
            original_query=query,
            query_type=query_type
        )
        
        # Générer pre-prompt
        pre_prompt = self.manager.get_pre_prompt(query_type)
        
        # Augmenter requête
        augmented_query = f"""{pre_prompt}

REQUÊTE UTILISATEUR:
{'-'*60}
{query}

RÉPONDEZ EN RESPECTANT LES AXIOMES CI-DESSUS.
"""
        
        # Cacher
        self.cache[cache_key] = augmented_query
        self.injection_count += 1
        
        logger.info(f"✓ Axiomes injectés ({self.injection_count})")
        
        return augmented_query
    
    def detect_query_type(self, query: str) -> str:
        """
        Détecte automatiquement type requête
        
        Returns:
            'rsa_calculation', 'riemann_analysis', 'prime_spectrum', etc.
        """
        
        query_lower = query.lower()
        
        # Détection patterns
        if any(word in query_lower for word in ['rapport spectral', 'rsa', 'asymétrique']):
            return 'rsa_calculation'
        
        elif any(word in query_lower for word in ['riemann', 'zéro', 'zero', 'hypothèse']):
            return 'riemann_analysis'
        
        elif any(word in query_lower for word in ['premier', 'prime', 'spectre', 'spectrum']):
            return 'prime_spectrum'
        
        elif any(word in query_lower for word in ['sr2', '1.5', 'ratio corrigé']):
            return 'sr2_calculation'
        
        elif any(word in query_lower for word in ['hol', 'isabelle', 'lean', 'proof', 'preuve']):
            return 'hol_proof_generation'
        
        else:
            return 'default'
    
    def inject_for_ollama(self, query: str, query_type: Optional[str] = None) -> str:
        """Injecte axiomes pour Ollama"""
        
        if query_type is None:
            query_type = self.detect_query_type(query)
        
        augmented = self.inject_axioms(query, query_type)
        
        logger.info(f"[Ollama] Injection pour: {query_type}")
        return augmented
    
    def inject_for_claude_hol(self, query: str, query_type: Optional[str] = None) -> str:
        """
        Injecte axiomes + SPÉCIFICATIONS HOL formelles STRICTES pour Claude
        Force génération code HOL4/Isabelle rigoureux
        """
        
        if query_type is None:
            query_type = self.detect_query_type(query)
        
        # Si HOL/preuve, ajouter spécifications formelles
        hol_specs = ""
        if 'hol' in query_type.lower() or 'proof' in query_type.lower():
            hol_specs = self._get_hol_formal_requirements()
        
        pre_prompt = self.manager.get_pre_prompt(query_type)
        
        injected = f"""{pre_prompt}

{hol_specs}

REQUÊTE UTILISATEUR:
{'-'*70}
{query}

INSTRUCTIONS FINALES:
- Générer code HOL4/Isabelle/Lean4 SYNTAXIQUEMENT VALIDE
- Respecter formules Savard: A(n), B(n), digamma, Sr2=1.5
- Implémenter RSA et convergence vers 0.5
- Formalisez les théorèmes avec preuves (ou sorry)
- Aucun pseudo-code - UNIQUEMENT HOL formel
"""
        
        logger.info(f"[Claude HOL] Injection stricte pour: {query_type}")
        return injected
    
    def inject_for_wolfram(self, query: str, query_type: Optional[str] = None) -> str:
        """Injecte axiomes pour WolframAlpha"""
        
        if query_type is None:
            query_type = self.detect_query_type(query)
        
        # Format adapté Wolfram
        pre_prompt = self.manager.get_pre_prompt(query_type)
        
        # Wolfram préfère format compact
        compact_prompt = f"""
CONTEXTE: Théorie Savard "L'univers est au carré"
- Sr2 = 1.5 (constante)
- RSA (Rapport Spectral Asymétrique) utilisé
- Ordres multiples analysés
- Géométrie spectrale asymétrique

REQUÊTE: {query}

APPLIQUER AXIOMES SAVARD UNIQUEMENT, PAS THÉORIE CLASSIQUE.
"""
        
        logger.info(f"[Wolfram] Injection pour: {query_type}")
        return compact_prompt
    
    def inject_for_openai(self, query: str, query_type: Optional[str] = None) -> Dict[str, Any]:
        """Injecte axiomes pour OpenAI (format messages)"""
        
        if query_type is None:
            query_type = self.detect_query_type(query)
        
        pre_prompt = self.manager.get_pre_prompt(query_type)
        
        # Format OpenAI
        messages = [
            {
                "role": "system",
                "content": pre_prompt
            },
            {
                "role": "user",
                "content": query
            }
        ]
        
        logger.info(f"[OpenAI] Injection pour: {query_type}")
        return messages
    
    def _get_hol_formal_requirements(self) -> str:
        """Retourne spécifications formelles HOL4/Isabelle/Lean4 strictes"""
        
        return """
╔════════════════════════════════════════════════════════════════════════╗
║ SPÉCIFICATIONS HOL4/ISABELLE/LEAN4 FORMELLES STRICTES                  ║
║ (AUCUN PSEUDO-CODE - CODE FORMEL UNIQUEMENT)                           ║
╚════════════════════════════════════════════════════════════════════════╝

1️⃣ STRUCTURE OBLIGATOIRE:
   ✓ theory Spectral_Primes imports Main begin ... end
   ✓ Sections clairement délimitées (section "...", subsection "...")
   ✓ Définitions rigoureuses (definition, def)
   ✓ Théorèmes avec énoncés (theorem name: "∀ x. P x")
   ✓ Lemmes d'appui (lemma)
   ✓ Preuves: 'by ...' ou 'proof ... qed' ou 'sorry'

2️⃣ FORMULES SAVARD EXACTES (OBLIGATOIRES - SYNTAXE HOL):
   definition A :: "nat ⇒ real" where
     "A n = (13 / 8) * (2 ^ n) - 2"
   
   definition B :: "nat ⇒ real" where
     "B n = (13 / 4) * (2 ^ n) - 66"
   
   definition digamma :: "nat ⇒ real ⇒ real" where
     "digamma n p = B n - 64 * p"
   
   definition Sr2 :: "real" where
     "Sr2 = 3 / 2"
   
   definition prime_reconstruct :: "nat ⇒ real" where
     "prime_reconstruct i = (B i - digamma i (real i)) / 64"

3️⃣ IMPLÉMENTATION RSA FORMELLE:
   definition alternating_sum :: "nat list ⇒ nat ⇒ real" where
     "alternating_sum primes k = 
        (∑ i ∈ {0..<length primes}. 
           (if even i then 1 else -1) * (real (primes ! i)) ^ k)"
   
   definition RSA :: "nat list ⇒ nat list ⇒ nat ⇒ real" where
     "RSA blockA blockB k =
        (alternating_sum blockA k - alternating_sum blockB k) / 
        (alternating_sum blockB k)"
   
   definition converges_to_half :: "nat list ⇒ nat list ⇒ bool" where
     "converges_to_half blockA blockB =
        ∀ ε > 0. ∃ K. ∀ k ≥ K. abs (RSA blockA blockB k - 0.5) < ε"

4️⃣ ÉTATS CONVERGENCE:
   datatype convergence_status = 
     DIVERGENT | CONVERGING | CONVERGED
   
   definition classify_convergence :: "real ⇒ convergence_status" where
     "classify_convergence rsa_value =
        (if abs (rsa_value - 0.5) > 0.3 then DIVERGENT
         else if abs (rsa_value - 0.5) > 0.05 then CONVERGING
         else CONVERGED)"

5️⃣ ANALYSE RIEMANN/EIGENVALUES:
   definition riemann_zero :: "complex ⇒ bool" where
     "riemann_zero s = (Re s = 1/2 ∧ s ≠ 1/2)"
   
   definition spectral_operator :: "real ⇒ complex" where
     "spectral_operator λ = Complex (1/2) (ln (2 * π * λ))"

6️⃣ THÉORÈMES CENTRAUX:
   theorem rsa_convergence:
     "∀ blockA blockB. increasing_blocks blockA blockB ⟶ 
                       converges_to_half blockA blockB"
   
   theorem prime_reconstruction_valid:
     "∀ i > 0. is_prime_result (prime_reconstruct i)"
   
   theorem spectral_geometry_critical_line:
     "∀ ν. riemann_zero (Complex (1/2) ν) ⟶ 
           (∃ λ > 0. spectral_operator λ = Complex (1/2) ν)"

7️⃣ LEMMES D'APPUI:
   lemma A_exponential_growth:
     "∀ n > 0. A n < A (n + 1)"
   
   lemma B_exponential_growth:
     "∀ n > 0. B n < B (n + 1)"

8️⃣ SYNTAXE CORRECTE PAR LANGAGE:
   HOL4:       :: et ⇒ et ∀ ∃ ∧ ∨ ¬
   Isabelle:   ⇒ ∀ ∃ ∧ ∨ ¬ λ
   Lean4:      → ∀ ∃ ∧ ∨ ¬ fun

REJETER IMMÉDIATEMENT SI:
   ✗ Pseudo-code (non-syntaxe HOL)
   ✗ Formules A/B incorrectes
   ✗ RSA non implémenté
   ✗ Sr2 ≠ 1.5
   ✗ Théorie classique nombre premiers
   ✗ Pas de structure theory/definition/theorem
   ✗ Mélange syntaxe (HOL vs Isabelle vs Lean4)

✓ ACCEPTER SI:
   ✓ theory...begin...end structure
   ✓ A(n) = (13/8) * 2^n - 2
   ✓ B(n) = (13/4) * 2^n - 66
   ✓ digamma(n,p) = B(n) - 64*p
   ✓ Sr2 = 1.5
   ✓ RSA implémenté avec alternating_sum
   ✓ Convergence 0.5 formalisée
   ✓ Théorèmes rigoureux avec énoncés
   ✓ Syntaxe HOL4/Isabelle/Lean4 valide
"""
    
    def validate_llm_response(self, response: str, query_type: str = "default") -> Dict[str, Any]:
        """
        Valide si réponse LLM respecte axiomes
        
        Returns:
            Résultat validation + suggestions
        """
        
        result = self.manager.validate_response(response, query_type)
        
        # Validation supplémentaire pour HOL
        if 'hol' in query_type.lower() or 'proof' in query_type.lower():
            hol_validation = self._validate_hol_syntax(response)
            result['hol_valid'] = hol_validation['valid']
            if not hol_validation['valid']:
                result['is_compliant'] = False
                result['violations'].extend(hol_validation['errors'])
        
        if not result['is_compliant']:
            logger.warning(f"Réponse non-conforme (score: {result['score']:.2f})")
            logger.warning(f"Violations: {result['violations'][:3]}")
        
        return result
    
    def _validate_hol_syntax(self, code: str) -> Dict[str, Any]:
        """Valide syntaxe HOL/Isabelle/Lean4 basique"""
        
        errors = []
        
        # Vérifier structure
        if 'theory' not in code and 'def' not in code:
            errors.append("Pas de structure theory ou def trouvée")
        
        if 'definition' not in code and 'def' not in code:
            errors.append("Pas de definitions trouvées")
        
        # Vérifier formules
        required = ['A', 'B', 'digamma', 'Sr2', 'prime_reconstruct']
        for formula in required:
            if formula not in code:
                errors.append(f"Formule '{formula}' manquante")
        
        # Vérifier RSA
        if 'RSA' not in code and 'alternating_sum' not in code:
            errors.append("RSA ou alternating_sum manquant")
        
        # Vérifier théorèmes
        if 'theorem' not in code and 'lemma' not in code:
            errors.append("Pas de théorèmes trouvés")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def rewrite_response(self, response: str, query_type: str = "default") -> str:
        """
        Ré-écrit réponse non-conforme pour respecter axiomes
        """
        
        validation = self.validate_llm_response(response, query_type)
        
        if validation['is_compliant']:
            return response  # Déjà conforme
        
        # Appliquer corrections
        corrected = response
        
        # Ajouter axiomes manquants
        for suggestion in validation['suggestions']:
            if "Sr2" in suggestion:
                corrected = f"(Avec Sr2 = 1.5 correction spectrale appliquée:) {corrected}"
            
            if "RSA" in suggestion:
                corrected = f"RSA = (Sum_A - Sum_B) / Sum_B → {corrected}"
        
        # Remplacer théorie classique
        replacements = {
            'prime number theorem': 'théorème Savard (spectral)',
            'distribution de Cramér': 'distribution spectrale asymétrique',
            'nombre d\'or': 'Sr2 = 1.5',
            'normal distribution': 'géométrie spectrale'
        }
        
        for old, new in replacements.items():
            corrected = corrected.replace(old, new)
        
        return corrected
    
    def export_injection_stats(self) -> Dict[str, Any]:
        """Exporte statistiques injections"""
        
        return {
            'total_injections': self.injection_count,
            'cache_size': len(self.cache),
            'axioms_loaded': len(self.manager.axioms),
            'directives_loaded': len(self.manager.directives),
            'parameters': self.manager.parameters
        }


def create_injector(memory_path: str = "memory") -> PromptInjector:
    """Factory pour créer injector"""
    return PromptInjector(memory_path)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Test
    injector = PromptInjector()
    
    print("="*70)
    print("ENHANCED PROMPT INJECTOR TEST")
    print("="*70)
    
    # Test HOL Claude
    print("\n[TEST] Injection Claude HOL Formelle")
    
    query = "Génère une théorie HOL4 rigoureuse pour la reconstruction des nombres premiers via RSA"
    injected = injector.inject_for_claude_hol(query)
    
    print(f"Query originale: {len(query)} chars")
    print(f"Query injectée: {len(injected)} chars")
    print(f"\nDébut injection:\n{injected[:400]}...\n")
