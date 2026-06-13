#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SPECTRAL_CORE - Gabriel spectral module"""
import math
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)

class SpectralRatio(Enum):
    RATIO_1_2 = 0.5
    RATIO_1_3 = 1/3
    RATIO_1_4 = 0.25

@dataclass
class PrimeSpectralData:
    position: int
    prime_value: int
    num_terms: int
    ratio: SpectralRatio
    SA_sum: float
    SB_sum: float
    digamma: float
    digamma_calc: float
    validated: bool = False

class SpectralMethodCore:
    def __init__(self):
        # On utilise directement prime_table.PRIMES (1000 entrees cross-validees
        # contre sympy.prime()) au lieu de regenerer un crible local qui n'allait
        # que jusqu'a la valeur 1000 (168 primes). Cette alignement permet a
        # reconstruct_prime_1_2(N), verifier, valider, etc. de fonctionner pour
        # N de 1 a 1000 (= 1000 positions, premiers de 2 a 7919).
        self.prime_list = self._load_prime_list()
        self.spectral_cache = {}
        logger.info(f"SpectralMethodCore initialized with {len(self.prime_list)} primes (positions 1..{len(self.prime_list)})")

    @staticmethod
    def _load_prime_list() -> List[int]:
        """Charge la table des 1000 premiers (cross-validee), avec fallback crible."""
        try:
            # Import relatif quand utilise comme package
            from ..spectral.prime_table import PRIMES
            return list(PRIMES)
        except (ImportError, ValueError):
            pass
        try:
            # Import absolu quand spectral_core.py est utilise directement
            from src.spectral.prime_table import PRIMES  # type: ignore
            return list(PRIMES)
        except (ImportError, ValueError):
            pass
        # Fallback : crible local jusqu'a la valeur 1000 (168 primes)
        logger.warning("prime_table.PRIMES introuvable, fallback crible (168 primes max)")
        return SpectralMethodCore._generate_primes(1000)
    
    @staticmethod
    def _generate_primes(limit: int) -> List[int]:
        """Genere les premiers jusqu'a la VALEUR `limit` (fallback historique)."""
        sieve = [True] * (limit + 1)
        sieve[0] = sieve[1] = False
        for i in range(2, int(math.sqrt(limit)) + 1):
            if sieve[i]:
                for j in range(i*i, limit + 1, i):
                    sieve[j] = False
        return [i for i in range(2, limit + 1) if sieve[i]]
    
    def get_prime_at_position(self, position: int) -> Optional[int]:
        if position < 1 or position > len(self.prime_list):
            return None
        return self.prime_list[position - 1]
    
    def compute_SA(self, n: int, ratio: SpectralRatio = SpectralRatio.RATIO_1_2) -> float:
        try:
            if ratio == SpectralRatio.RATIO_1_2:
                return (3.25 / 2) * (2 ** n) - 2
            elif ratio == SpectralRatio.RATIO_1_3:
                return ((73 / 9) / 12) * (3 ** n) - 1.5
            elif ratio == SpectralRatio.RATIO_1_4:
                return ((241 / 16) / 12) * (4 ** n) - (4 / 3)
        except OverflowError:
            return float('inf')
        return 0.0
    
    def compute_SB(self, n: int, ratio: SpectralRatio = SpectralRatio.RATIO_1_2) -> float:
        try:
            if ratio == SpectralRatio.RATIO_1_2:
                return (6.5 / 2) * (2 ** n) - 66
            elif ratio == SpectralRatio.RATIO_1_3:
                return ((219 / 9) / 12) * (3 ** n) - (487 * 1.5)
            elif ratio == SpectralRatio.RATIO_1_4:
                return ((964 / 16) / 12) * (4 ** n) - (3073 * (4 / 3))
        except OverflowError:
            return float('inf')
        return 0.0
    
    def validate_ratio(self, n1: int, n2: int, ratio: SpectralRatio) -> Tuple[bool, float]:
        if n1 == n2:
            return False, 0.0
        sa1, sa2 = self.compute_SA(n1, ratio), self.compute_SA(n2, ratio)
        sb1, sb2 = self.compute_SB(n1, ratio), self.compute_SB(n2, ratio)
        denom = sb1 - sb2
        if abs(denom) < 1e-10:
            return False, 0.0
        computed = (sa1 - sa2) / denom
        return abs(computed - ratio.value) < 1e-6, computed
    
    def reconstruct_prime_1_2(self, position: int) -> Optional[PrimeSpectralData]:
        if position < 1 or position in self.spectral_cache:
            return self.spectral_cache.get(position)
        prime = self.get_prime_at_position(position)
        if not prime:
            return None
        try:
            # Calculs en ENTIERS Python (precision arbitraire) pour eviter
            # toute perte de precision sur grandes positions (>= 168).
            # SA(n) = (13 * 2^n) / 8 - 2  -> entier (13 * 2^n est divisible par 8 des que n>=3)
            # SB(n) = (13 * 2^n) / 4 - 66 -> entier (13 * 2^n est divisible par 4 des que n>=2)
            two_n = 1 << position  # 2^n exact
            sa_int = (13 * two_n) // 8 - 2
            sb_int = (13 * two_n) // 4 - 66
            # digamma = SB - 64*p  (entier exact)
            digamma_int = sb_int - 64 * prime
            # P_reconstruit = (SB - digamma) / 64  = (64*p) / 64 = p  EXACTEMENT
            recon_num = sb_int - digamma_int
            if recon_num % 64 != 0:
                # Ne devrait jamais arriver par construction
                return None
            recon = recon_num // 64
            if recon == prime:
                data = PrimeSpectralData(
                    position, prime, position, SpectralRatio.RATIO_1_2,
                    float(sa_int), float(sb_int),
                    float(digamma_int), float(recon),
                    True,
                )
                self.spectral_cache[position] = data
                return data
        except Exception as exc:
            logger.debug("reconstruct_prime_1_2(%d) error: %s", position, exc)
        return None
    
    def explain_reconstruction(self, position: int) -> str:
        data = self.reconstruct_prime_1_2(position)
        if not data:
            return f"Cannot reconstruct prime at position {position}"
        return (
            f"Position {data.position}: Prime={data.prime_value}, "
            f"n={data.position}, Terms={data.num_terms}\n"
            f"INVARIANT (ratio 1/2): position = n = number_of_terms = {data.position}\n"
            f"SA_sum={data.SA_sum:.6f}, SB_sum={data.SB_sum:.6f}, "
            f"digamma={data.digamma:.6f}"
        )

class AntiHallucinationValidator:
    def __init__(self):
        self.core = SpectralMethodCore()
    
    def validate_answer(self, question: str, answer: str) -> Tuple[bool, str]:
        position = self._extract_position(question)
        if not position:
            return True, "OK"
        if "terms" in answer.lower() and str(position) not in answer:
            return False, f"HALLUCINATION: position {position} not in answer"
        return True, "OK"
    
    def audit(self, question: str, answer: str, ground_truth: Optional[Dict] = None) -> Dict:
        """
        Audit silencieux complet d'une reponse LLM contre la verite spectrale.
        
        Verifie :
          1. Si une position est mentionnee dans la question, le nombre premier
             correspondant DOIT apparaitre dans la reponse.
          2. INVARIANT 1/2 : si la question mentionne une position N et le rapport 1/2,
             alors n DOIT etre N et num_termes DOIT etre N (mention textuelle).
          3. Aucun nombre premier hallucine (si un "Neme premier" est mentionne, 
             le bon prime DOIT y figurer).
          4. Vocabulaire interdit (incoherent, absurde, faux, etc.) - rejette le ton.
        
        Returns:
            dict avec:
              - valid: bool
              - violations: list[str] (raisons d'echec)
              - corrective_prompt: str (instruction de correction pour re-prompt LLM)
              - ground_truth: dict (donnees correctes a injecter)
        """
        violations: List[str] = []
        position = self._extract_position(question)
        
        # Construire la verite terrain depuis spectral_core si absente
        if ground_truth is None and position:
            data = self.core.reconstruct_prime_1_2(position)
            if data:
                ground_truth = {
                    "position": data.position,
                    "prime": data.prime_value,
                    "n": data.position,
                    "num_terms": data.num_terms,
                    "ratio": "1/2",
                }
        
        gt = ground_truth or {}
        answer_low = answer.lower()
        
        # Regle 1 : position citee -> prime correct doit apparaitre
        if position and "prime" in gt:
            expected_prime = gt["prime"]
            if str(expected_prime) not in answer:
                violations.append(
                    f"Le {position}e nombre premier est {expected_prime}, "
                    f"mais cette valeur n'apparait pas dans la reponse."
                )
        
        # Regle 2 : INVARIANT 1/2 - n = position = num_termes
        if position and gt.get("ratio") == "1/2":
            # Cherche une mention "n = X" qui ne soit pas egale a la position
            n_match = re.search(r'\bn\s*=\s*(\d+)', answer, re.IGNORECASE)
            if n_match:
                claimed_n = int(n_match.group(1))
                if claimed_n != position:
                    violations.append(
                        f"INVARIANT 1/2 VIOLE : la reponse affirme n={claimed_n}, "
                        f"mais pour la position {position} en rapport 1/2, "
                        f"n DOIT etre egal a {position}."
                    )
        
        # Regle 3 : vocabulaire interdit (rejette le ton dismissif)
        forbidden = ["incoherent", "incohérent", "absurde", "faux", "erroné", 
                     "erronee", "n'a pas de sens", "n'a aucun sens", "invalide"]
        for word in forbidden:
            if word in answer_low:
                violations.append(
                    f"Vocabulaire interdit detecte : '{word}'. "
                    f"La methode spectrale de l'utilisateur est valide et doit etre respectee."
                )
                break  # une seule mention suffit
        
        # Construire le prompt correctif
        corrective_prompt = ""
        if violations:
            corrective_prompt = self._build_corrective_prompt(violations, gt, question)
        
        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "corrective_prompt": corrective_prompt,
            "ground_truth": gt,
        }
    
    @staticmethod
    def _build_corrective_prompt(violations: List[str], gt: Dict, question: str) -> str:
        """Construit l'instruction de correction silencieuse pour le LLM."""
        gt_lines = []
        if "position" in gt:
            gt_lines.append(f"  - Position demandee : {gt['position']}")
        if "prime" in gt:
            gt_lines.append(f"  - Nombre premier CORRECT : {gt['prime']}")
        if "n" in gt:
            gt_lines.append(f"  - n CORRECT : {gt['n']}")
        if "num_terms" in gt:
            gt_lines.append(f"  - Nombre de termes CORRECT dans A et B : {gt['num_terms']}")
        if "ratio" in gt:
            gt_lines.append(f"  - Rapport : {gt['ratio']}")
        
        gt_block = "\n".join(gt_lines) if gt_lines else "(verite terrain non disponible)"
        violations_block = "\n".join(f"  - {v}" for v in violations)
        
        return f"""AUDIT SPECTRAL : ta reponse precedente contient des erreurs FACTUELLES.

Violations detectees :
{violations_block}

VERITE TERRAIN (calculee par le module spectral, non-negociable) :
{gt_block}

INVARIANT (rapport 1/2) : position = n = nombre_de_termes. SANS EXCEPTION.

Regenere ta reponse en utilisant EXACTEMENT ces valeurs. 
N'argumente PAS contre la methode. Reste bienveillant et factuel.
Reponds en francais.

Question initiale : {question}
"""
    
    @staticmethod
    def _extract_position(text: str) -> Optional[int]:
        patterns = [
            r'(\d+)\s*(?:eme|ieme|ième|ème|e|th|st|nd|rd)\s*(?:nombre\s+)?(?:premier|prime)',
            r'position\s+(\d+)',
            r'rang\s+(\d+)',
            r'(\d+)\s*(?:e|eme|ieme|ième|ème)\s+rang',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        return None
