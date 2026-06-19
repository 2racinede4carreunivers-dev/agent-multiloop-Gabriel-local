"""
Multiloop Validation Engine - Boucle de validation matérielle complète
Intègre Gabriel + HOL Proof Corrector + Isabelle pour atteindre 0.8+ confiance
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time

from src.isabelle_validator import IsabelleValidator, ValidationResult, ValidationStatus
from src.hol_proof_corrector import HOLProofCorrector, CorrectionAttempt

logger = logging.getLogger(__name__)

class MultiloopStage(Enum):
    """Étapes de la boucle multiloop"""
    GENERATION = "generation"           # Générer preuve (Gabriel)
    VALIDATION = "validation"           # Valider via Isabelle
    CORRECTION = "correction"           # Corriger si erreurs
    VERIFICATION = "verification"       # Vérifier confiance
    COMPLETED = "completed"             # Complétée

@dataclass
class MultiloopIteration:
    """Représente une itération de la boucle multiloop"""
    iteration_number: int
    stage: MultiloopStage
    timestamp: float
    
    # Input
    input_theorem: str
    input_proof: str
    
    # Processing
    validation_result: Optional[ValidationResult] = None
    correction_attempts: List[CorrectionAttempt] = field(default_factory=list)
    
    # Output
    output_proof: str = ""
    confidence_score: float = 0.0
    
    # Meta
    errors: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

@dataclass
class MultiloopResult:
    """Résultat final de la boucle multiloop"""
    theorem_name: str
    
    # Trajectoire
    iterations: List[MultiloopIteration] = field(default_factory=list)
    
    # Résultat final
    final_proof: str = ""
    final_confidence: float = 0.0
    is_valid: bool = False
    
    # Stats
    total_iterations: int = 0
    total_time: float = 0.0
    corrections_applied: int = 0
    
    def __repr__(self):
        status = "✓ VALIDE" if self.is_valid else "✗ INVALIDE"
        return f"{status} {self.theorem_name} (confiance: {self.final_confidence:.2f})"


class MultiloopValidationEngine:
    """Boucle multiloop: Gabriel → Validation → Correction → Verification"""
    
    def __init__(self, max_iterations: int = 3, target_confidence: float = 0.8):
        """
        Args:
            max_iterations: Max itérations (défaut 3)
            target_confidence: Confiance minimale cible (0-1)
        """
        self.max_iterations = max_iterations
        self.target_confidence = target_confidence
        self.validator = IsabelleValidator()
        self.corrector = HOLProofCorrector(max_iterations=3)
        self.validation_history = {}
    
    def process_theorem(self, theorem_name: str, initial_proof: str) -> MultiloopResult:
        """
        Traite un théorème à travers la boucle multiloop complète
        
        Flow:
        1. GENERATION: Gabriel fournit preuve initiale
        2. VALIDATION: Isabelle valide
        3. Si erreurs → CORRECTION: Corriger automatiquement
        4. VERIFICATION: Vérifier confiance ≥ 0.8
        5. Répéter jusqu'à succès ou max_iterations
        
        Returns:
            MultiloopResult avec trajectoire complète
        """
        
        logger.info(f"[MULTILOOP] Début traitement: {theorem_name}")
        
        result = MultiloopResult(theorem_name=theorem_name)
        start_time = time.time()
        
        current_proof = initial_proof
        
        for iteration_num in range(1, self.max_iterations + 1):
            logger.info(f"[MULTILOOP] Itération {iteration_num}/{self.max_iterations}")
            
            # Créer itération
            iteration = MultiloopIteration(
                iteration_number=iteration_num,
                stage=MultiloopStage.GENERATION,
                timestamp=time.time(),
                input_theorem=theorem_name,
                input_proof=current_proof
            )
            
            # ============================================================
            # ÉTAPE 1: VALIDATION (Isabelle)
            # ============================================================
            
            iteration.stage = MultiloopStage.VALIDATION
            logger.info(f"  [1/4] VALIDATION via Isabelle...")
            
            validation_result = self.validator.validate_proof(current_proof, theorem_name)
            iteration.validation_result = validation_result
            
            if validation_result.is_valid:
                # ✓ Preuve valide!
                iteration.stage = MultiloopStage.COMPLETED
                iteration.output_proof = current_proof
                iteration.confidence_score = 1.0
                iteration.notes.append("✓ Preuve valide - Isabelle OK")
                
                result.iterations.append(iteration)
                result.final_proof = current_proof
                result.final_confidence = 1.0
                result.is_valid = True
                result.total_iterations = iteration_num
                
                logger.info(f"✓ SUCCÈS à itération {iteration_num}")
                break
            
            else:
                # ✗ Erreurs - passer à correction
                iteration.notes.append(
                    f"✗ {len(validation_result.errors)} erreur(s) détectée(s)"
                )
                
                # ============================================================
                # ÉTAPE 2: CORRECTION
                # ============================================================
                
                iteration.stage = MultiloopStage.CORRECTION
                logger.info(f"  [2/4] CORRECTION automatique...")
                
                corrected_proof, correction_attempts = self.corrector.correct_proof(
                    current_proof,
                    theorem_name
                )
                
                iteration.correction_attempts = correction_attempts
                result.corrections_applied += len(correction_attempts)
                
                # Vérifier si correction a réussi
                last_attempt = correction_attempts[-1]
                if last_attempt.success:
                    iteration.notes.append(
                        f"✓ Correction réussie (tentative {last_attempt.attempt_number})"
                    )
                    current_proof = corrected_proof
                else:
                    iteration.notes.append(
                        f"~ Correction appliquée mais validation incomplète"
                    )
                    current_proof = corrected_proof
                
                # ============================================================
                # ÉTAPE 3: VÉRIFICATION
                # ============================================================
                
                iteration.stage = MultiloopStage.VERIFICATION
                logger.info(f"  [3/4] VÉRIFICATION confiance...")
                
                # Re-valider après correction
                revalidation = self.validator.validate_proof(current_proof, theorem_name)
                
                iteration.output_proof = current_proof
                iteration.confidence_score = revalidation.confidence_score
                
                if revalidation.is_valid:
                    iteration.notes.append("✓ Post-correction valide")
                else:
                    if revalidation.confidence_score >= self.target_confidence:
                        iteration.notes.append(
                            f"~ Confiance acceptable: {revalidation.confidence_score:.2f}"
                        )
                    else:
                        iteration.notes.append(
                            f"✗ Confiance insuffisante: {revalidation.confidence_score:.2f}"
                        )
                
                iteration.stage = MultiloopStage.COMPLETED
                result.iterations.append(iteration)
                
                # Vérifier sortie
                if revalidation.confidence_score >= self.target_confidence:
                    result.final_proof = current_proof
                    result.final_confidence = revalidation.confidence_score
                    result.is_valid = revalidation.is_valid
                    result.total_iterations = iteration_num
                    
                    logger.info(
                        f"✓ SUCCÈS (confiance: {revalidation.confidence_score:.2f})"
                    )
                    break
        
        # Finaliser
        result.total_time = time.time() - start_time
        
        if not result.final_proof:
            # Utiliser dernière tentative
            result.final_proof = current_proof
            result.final_confidence = result.iterations[-1].confidence_score if result.iterations else 0.0
        
        logger.info(f"[MULTILOOP] Terminé: {result}")
        return result
    
    def export_multiloop_report(self, result: MultiloopResult) -> str:
        """Exporte rapport multiloop détaillé"""
        
        report = f"""
{'='*70}
RAPPORT MULTILOOP VALIDATION
{'='*70}

Théorème: {result.theorem_name}
Status: {'✓ VALIDE' if result.is_valid else '✗ INVALIDE'}
Confiance finale: {result.final_confidence * 100:.1f}%
Temps total: {result.total_time:.2f}s
Itérations: {result.total_iterations}/{self.max_iterations}
Corrections appliquées: {result.corrections_applied}

TRAJECTOIRE:
"""
        
        for iteration in result.iterations:
            stage_str = iteration.stage.value.upper()
            
            report += f"""
[Itération {iteration.iteration_number}] {stage_str}
  Timestamp: {iteration.timestamp:.2f}
  Confiance: {iteration.confidence_score * 100:.1f}%
"""
            
            if iteration.validation_result:
                vr = iteration.validation_result
                report += f"  Validation: {vr.status.value}"
                if vr.errors:
                    report += f" ({len(vr.errors)} erreurs)\n"
                else:
                    report += "\n"
            
            if iteration.correction_attempts:
                report += f"  Corrections: {len(iteration.correction_attempts)} tentatives\n"
            
            for note in iteration.notes:
                report += f"    • {note}\n"
        
        report += f"""
{'='*70}
PREUVE FINALE:
{'='*70}
{result.final_proof[:500]}...

Status: {('✓ VALIDÉE' if result.is_valid else '✗ NON VALIDÉE')} (Confiance: {result.final_confidence:.2f})
"""
        
        return report


if __name__ == '__main__':
    # Test
    engine = MultiloopValidationEngine(max_iterations=3, target_confidence=0.8)
    
    print("="*70)
    print("MULTILOOP VALIDATION ENGINE TEST")
    print("="*70)
    
    # Test 1: Preuve avec erreurs (nécessite correction)
    test_proof = """
Theorem riemann_basic: "∀ n : ℕ, n > 0 → ∃ p, prime p ∧ p > n"
Proof
  intro n h
  (* Preuve schématique *)
  sorry
"""  # Incomplète intentionnellement
    
    print("\n[TEST] Processing preuve incomplète...")
    result = engine.process_theorem("riemann_basic", test_proof)
    
    print(engine.export_multiloop_report(result))
    
    if result.is_valid:
        print(f"\n✓ Théorème validé avec confiance {result.final_confidence:.2f}")
    else:
        print(f"\n~ Théorème traité - Confiance finale: {result.final_confidence:.2f}")
