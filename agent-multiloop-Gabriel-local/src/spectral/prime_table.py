"""
Table des nombres premiers indexes par position (1-based).
Pour rapport 1/2 : n = position = quantite de termes dans A et B.

P[n] = n-ieme nombre premier.
"""
from __future__ import annotations


# Premiers 1 a 100 (positions 1 a 100). Source : OEIS A000040.
PRIMES: list[int] = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
    31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
    127, 131, 137, 139, 149, 151, 157, 163, 167, 173,
    179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
    233, 239, 241, 251, 257, 263, 269, 271, 277, 281,
    283, 293, 307, 311, 313, 317, 331, 337, 347, 349,
    353, 359, 367, 373, 379, 383, 389, 397, 401, 409,
    419, 421, 431, 433, 439, 443, 449, 457, 461, 463,
    467, 479, 487, 491, 499, 503, 509, 521, 523, 541,
]


def nth_prime(n: int) -> int | None:
    """Retourne le n-ieme nombre premier (1-indexed). 2 = 1er, 3 = 2e, etc."""
    if n < 1 or n > len(PRIMES):
        return None
    return PRIMES[n - 1]


def prime_position(p: int) -> int | None:
    """Retourne la position (1-indexed) du nombre premier p, ou None s'il n'est pas dans la table."""
    try:
        return PRIMES.index(p) + 1
    except ValueError:
        return None


def is_known_prime(p: int) -> bool:
    return p in PRIMES
