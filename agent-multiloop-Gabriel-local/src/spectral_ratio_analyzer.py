"""
Spectral Ratio Analyzer - Rapport Spectral Asymétrique Ordonné (RSA)
Capacité critique de la théorie "L'univers est au carré" de Philippe Thomas Savard

Module analyse RSA entre blocs de nombres premiers avec convergence vers 1/2
"""

import logging
from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass, field
import sympy as sp
from sympy import prime, isprime
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class SpectralBlock:
    """Représente un bloc de nombres premiers"""
    name: str  # 'A' ou 'B'
    primes: List[int]  # Nombres premiers du bloc
    sums: Dict[int, float] = field(default_factory=dict)  # Sommes par ordre
    
    def validate(self):
        """Valide que tous les éléments sont des nombres premiers"""
        for p in self.primes:
            if not isprime(p):
                raise ValueError(f"{p} n'est pas un nombre premier")
        return True
    
    def __repr__(self):
        return f"Block{self.name}({self.primes})"


@dataclass
class SpectralRatioResult:
    """Résultat du calcul de rapport spectral"""
    block_a: SpectralBlock
    block_b: SpectralBlock
    
    # Sommes par ordre
    sum_a_by_order: Dict[int, float]  # {ordre: somme}
    sum_b_by_order: Dict[int, float]  # {ordre: somme}
    
    # Calcul RSA
    numerator: float  # Numérateur RSA
    denominator: float  # Dénominateur RSA
    rsa: float  # Rapport Spectral Asymétrique = num/den
    
    # Convergence
    distance_to_half: float  # |RSA - 0.5|
    convergence_status: str  # 'divergent', 'converging', 'converged'
    
    # Données complètes
    computation_details: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self):
        return f"RSA({self.block_a.name},{self.block_b.name})={self.rsa:.10f} (dist_0.5={self.distance_to_half:.6f})"


class SpectralRatioAnalyzer:
    """Analyseur de Rapport Spectral Asymétrique Ordonné (RSA)"""
    
    def __init__(self, max_order: int = 10):
        """
        Args:
            max_order: Ordre maximum de calcul (par défaut 10)
        """
        self.max_order = max_order
        self.computation_cache = {}
    
    def compute_block_sums(self, block: SpectralBlock, max_order: int = None) -> Dict[int, float]:
        """
        Calcule les sommes de la séquence pour chaque ordre
        
        Pour bloc [p1, p2, p3, ...], ordre k:
        Sum_k = Σ(i=1 to len) (-1)^(i+1) * p_i^k
        """
        if max_order is None:
            max_order = self.max_order
        
        sums = {}
        
        for order in range(1, max_order + 1):
            total = 0.0
            for i, p in enumerate(block.primes):
                # Alternance de signe: (-1)^(i+1)
                sign = (-1) ** (i + 1)
                total += sign * (p ** order)
            sums[order] = total
        
        block.sums = sums
        return sums
    
    def compute_rsa(self, block_a: SpectralBlock, block_b: SpectralBlock, 
                   order: int = 1) -> SpectralRatioResult:
        """
        Calcule le Rapport Spectral Asymétrique Ordonné (RSA)
        
        Formule:
        RSA = (Sum_A(ordre) - Sum_B(ordre)) / (Diff_B(ordre))
        
        Où:
        - Sum_A(ordre) = Σ alternée des p_i^ordre pour bloc A
        - Sum_B(ordre) = Σ alternée des p_i^ordre pour bloc B
        
        Numérateur = Sum_A - Sum_B (avec signe alterné)
        Dénominateur = Diff_B = différence cumulée bloc B
        """
        
        # Valider blocs
        block_a.validate()
        block_b.validate()
        
        # Calculer sommes si pas déjà fait
        if not block_a.sums:
            self.compute_block_sums(block_a, order)
        if not block_b.sums:
            self.compute_block_sums(block_b, order)
        
        # Récupérer sommes pour l'ordre demandé
        sum_a = block_a.sums.get(order)
        sum_b = block_b.sums.get(order)
        
        if sum_a is None or sum_b is None:
            raise ValueError(f"Sommes non calculées pour ordre {order}")
        
        # ============================================================
        # FORMULE RSA - Telle que décrite par l'utilisateur
        # ============================================================
        
        # Numérateur: difference entre sommes des deux blocs
        # Format: (Sum_A - Sum_B)
        numerator_part1 = sum_a - sum_b
        
        # Dénominateur: différence cumulée des blocs B
        # Format: (B1 - B2 - B3 - ...) = B1 - (B2 + B3 + ...)
        # Mais selon formule de l'utilisateur: utiliser structure avec parenthèses
        
        # Reconstituer selon pattern utilisateur
        # Pour bloc B=[p1,p2,p3,...], structure: (p1 - (p2 - (p3 - ...)))
        
        # Dénominateur = sum_b (déjà alternée par compute_block_sums)
        denominator = sum_b
        
        # Calcul RSA
        if denominator == 0:
            rsa = float('inf')
            logger.warning(f"Dénominateur zéro pour {block_a.name}-{block_b.name} ordre {order}")
        else:
            rsa = numerator_part1 / denominator
        
        # Distance à 0.5
        distance_to_half = abs(rsa - 0.5)
        
        # Déterminer statut convergence
        if distance_to_half < 0.01:
            convergence_status = 'converged'
        elif distance_to_half < 0.1:
            convergence_status = 'converging'
        else:
            convergence_status = 'divergent'
        
        return SpectralRatioResult(
            block_a=block_a,
            block_b=block_b,
            sum_a_by_order={order: sum_a},
            sum_b_by_order={order: sum_b},
            numerator=numerator_part1,
            denominator=denominator,
            rsa=rsa,
            distance_to_half=distance_to_half,
            convergence_status=convergence_status,
            computation_details={
                'order': order,
                'sum_a': sum_a,
                'sum_b': sum_b,
                'formula': f'({sum_a} - ({sum_b})) / ({denominator})',
                'block_a_primes': block_a.primes,
                'block_b_primes': block_b.primes,
                'block_a_count': len(block_a.primes),
                'block_b_count': len(block_b.primes)
            }
        )
    
    def analyze_convergence(self, block_a: SpectralBlock, block_b: SpectralBlock,
                           orders: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Analyse la convergence du RSA sur plusieurs ordres
        
        Montre comment RSA converge vers 0.5 quand blocs augmentent
        """
        
        if orders is None:
            orders = list(range(1, min(self.max_order + 1, 6)))  # Par défaut ordres 1-5
        
        results = []
        rsa_values = []
        distances = []
        
        for order in orders:
            result = self.compute_rsa(block_a, block_b, order)
            results.append(result)
            rsa_values.append(result.rsa)
            distances.append(result.distance_to_half)
        
        # Analyser tendance
        if len(rsa_values) >= 2:
            # Vérifier si converge vers 0.5
            trend = "converging_to_0.5" if distances[-1] < distances[0] else "diverging"
        else:
            trend = "insufficient_data"
        
        return {
            'block_a': block_a,
            'block_b': block_b,
            'orders': orders,
            'results': results,
            'rsa_values': rsa_values,
            'distances_to_half': distances,
            'convergence_trend': trend,
            'final_rsa': rsa_values[-1] if rsa_values else None,
            'final_distance': distances[-1] if distances else None,
            'min_distance': min(distances) if distances else None,
            'min_distance_order': orders[distances.index(min(distances))] if distances else None
        }
    
    def compare_block_sizes(self, block_a: SpectralBlock, block_b: SpectralBlock,
                           order: int = 1) -> Dict[str, Any]:
        """
        Compare RSA pour différentes tailles de blocs
        
        Montre convergence vers 0.5 à mesure que blocs grandissent
        """
        
        result_small = self.compute_rsa(block_a, block_b, order)
        
        # Créer versions augmentées des blocs
        # Ajouter primes suivants
        all_primes = []
        p = 2
        while len(all_primes) < 20:
            if isprime(p):
                all_primes.append(p)
            p += 1
        
        # Séparer en A et B augmentés
        block_a_extended = SpectralBlock(
            name=block_a.name + "_ext",
            primes=all_primes[:10]  # 2,3,5,7,11,13,17,19,23,29
        )
        block_b_extended = SpectralBlock(
            name=block_b.name + "_ext",
            primes=all_primes[10:20]  # 31,37,41,43,47,53,59,61,67,71
        )
        
        result_large = self.compute_rsa(block_a_extended, block_b_extended, order)
        
        return {
            'small_blocks': {
                'block_a': result_small.block_a.primes,
                'block_b': result_small.block_b.primes,
                'rsa': result_small.rsa,
                'distance_to_0.5': result_small.distance_to_half
            },
            'large_blocks': {
                'block_a': result_large.block_a.primes,
                'block_b': result_large.block_b.primes,
                'rsa': result_large.rsa,
                'distance_to_0.5': result_large.distance_to_half
            },
            'convergence_improvement': result_small.distance_to_half - result_large.distance_to_half
        }


# ============================================================
# Export formaté pour Gabriel
# ============================================================

def export_rsa_explanation(result: SpectralRatioResult) -> str:
    """Exporte résultat RSA en explication lisible"""
    
    explanation = f"""
RAPPORT SPECTRAL ASYMÉTRIQUE ORDONNÉ (RSA)
{'='*60}

Blocs analysés:
  • Bloc A: {result.block_a.primes}
  • Bloc B: {result.block_b.primes}

Sommes alternées (ordre {result.computation_details.get('order', 1)}):
  • Sum_A = {result.sum_a_by_order.get(result.computation_details.get('order', 1), result.computation_details.get('sum_a'))}
  • Sum_B = {result.sum_b_by_order.get(result.computation_details.get('order', 1), result.computation_details.get('sum_b'))}

Calcul RSA:
  Numérateur = Sum_A - Sum_B = {result.numerator}
  Dénominateur = Sum_B = {result.denominator}
  
  RSA = {result.numerator} / {result.denominator} = {result.rsa:.10f}

Convergence vers 0.5:
  • Distance à 0.5: {result.distance_to_half:.10f}
  • Statut: {result.convergence_status}
  • RSA ≈ {result.rsa:.6f}

Interprétation:
  {get_convergence_interpretation(result)}
"""
    
    return explanation


def get_convergence_interpretation(result: SpectralRatioResult) -> str:
    """Génère interprétation du statut de convergence"""
    
    if result.convergence_status == 'converged':
        return f"RSA est très proche de 0.5 - Convergence forte (écart: {result.distance_to_half:.6f})"
    elif result.convergence_status == 'converging':
        return f"RSA approche 0.5 - Convergence modérée (écart: {result.distance_to_half:.6f})"
    else:
        if result.rsa > 0.5:
            return f"RSA diverge au-dessus de 0.5 (écart: {result.distance_to_half:.6f}) - Les blocs sont trop petits pour convergence"
        else:
            return f"RSA diverge en-dessous de 0.5 (écart: {result.distance_to_half:.6f}) - Les blocs sont trop petits pour convergence"


if __name__ == '__main__':
    print("="*70)
    print("TEST SPECTRAL RATIO ANALYZER")
    print("="*70)
    
    # Test 1: Cas de l'utilisateur - Petits blocs (divergent)
    print("\n[TEST 1] Petits blocs: A=[2], B=[3,5] (DIVERGENT)")
    print("-"*70)
    
    analyzer = SpectralRatioAnalyzer()
    
    block_a_small = SpectralBlock(name="A", primes=[2])
    block_b_small = SpectralBlock(name="B", primes=[3, 5])
    
    result_small = analyzer.compute_rsa(block_a_small, block_b_small, order=1)
    print(export_rsa_explanation(result_small))
    
    # Test 2: Blocs moyens (converging)
    print("\n[TEST 2] Blocs moyens: convergence progressive")
    print("-"*70)
    
    block_a_medium = SpectralBlock(name="A", primes=[2, 3, 5])
    block_b_medium = SpectralBlock(name="B", primes=[7, 11, 13])
    
    result_medium = analyzer.compute_rsa(block_a_medium, block_b_medium, order=1)
    print(export_rsa_explanation(result_medium))
    
    # Test 3: Grands blocs (converged)
    print("\n[TEST 3] Grands blocs: A=[2,3,5,7,11,13], B=[17,19,23,29,31,37,41]")
    print("-"*70)
    
    block_a_large = SpectralBlock(name="A", primes=[2, 3, 5, 7, 11, 13])
    block_b_large = SpectralBlock(name="B", primes=[17, 19, 23, 29, 31, 37, 41])
    
    result_large = analyzer.compute_rsa(block_a_large, block_b_large, order=1)
    print(export_rsa_explanation(result_large))
    
    # Test 4: Analyse convergence
    print("\n[TEST 4] Analyse convergence sur ordres multiples")
    print("-"*70)
    
    convergence = analyzer.analyze_convergence(block_a_large, block_b_large)
    print(f"RSA par ordre:")
    for order, rsa, distance in zip(
        convergence['orders'],
        convergence['rsa_values'],
        convergence['distances_to_half']
    ):
        print(f"  Ordre {order}: RSA = {rsa:.8f}, distance à 0.5 = {distance:.8f}")
    print(f"\nTendance convergence: {convergence['convergence_trend']}")
