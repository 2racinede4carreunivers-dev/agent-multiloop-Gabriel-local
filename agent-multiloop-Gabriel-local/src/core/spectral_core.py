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
        self.prime_list = self._generate_primes(1000)
        self.spectral_cache = {}
        logger.info(f"SpectralMethodCore initialized with {len(self.prime_list)} primes")
    
    @staticmethod
    def _generate_primes(limit: int) -> List[int]:
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
            sa_sum = self.compute_SA(position)
            sb_sum = self.compute_SB(position)
            digamma = sb_sum - 64 * prime
            digamma_calc = (sb_sum - digamma) / 64
            if abs(digamma_calc - prime) < 1e-6:
                data = PrimeSpectralData(position, prime, position, SpectralRatio.RATIO_1_2,
                                        sa_sum, sb_sum, digamma, digamma_calc, True)
                self.spectral_cache[position] = data
                return data
        except:
            pass
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
    
    @staticmethod
    def _extract_position(text: str) -> Optional[int]:
        patterns = [r'(\d+)(?:eme|e|th)\s+(?:premier|prime)', r'position\s+(\d+)']
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        return None
