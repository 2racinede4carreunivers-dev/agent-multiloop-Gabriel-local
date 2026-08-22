from dataclasses import dataclass
from typing import Literal

ModeDigamma = Literal["add", "sub"]

@dataclass
class NonTypicalConfig:
    k: int
    n: int = 10
    digamma_position: int = 8
    digamma_mode: ModeDigamma = "sub"


def _suite_A_n10_k3() -> int:
    # Exemple explicite pour 1/3, n = 10
    # 3^1+3^2+3^4+3^5+3^6+3^7+3^8+(3^9-3^7)+(3^10-3^8)
    termes = [
        3**1, 3**2, 3**4, 3**5, 3**6, 3**7, 3**8,
        3**9 - 3**7,
        3**10 - 3**8,
    ]
    return sum(termes)


def _suite_B_n10_k3() -> int:
    # 3^1+3^2+3^4+3^5+3^7+3^8+3^9+(3^10-3^8)+(3^11-3^9)
    termes = [
        3**1, 3**2, 3**4, 3**5, 3**7, 3**8, 3**9,
        3**10 - 3**8,
        3**11 - 3**9,
    ]
    return sum(termes)


def _suite_A_n10_k5() -> int:
    # 5^1+5^2+5^4+5^5+5^6+5^7+5^8+(5^9-5^7)+(5^10-5^8)
    termes = [
        5**1, 5**2, 5**4, 5**5, 5**6, 5**7, 5**8,
        5**9 - 5**7,
        5**10 - 5**8,
    ]
    return sum(termes)


def _suite_B_n10_k5() -> int:
    # 5^1+5^2+5^4+5^5+5^7+5^8+5^9+(5^10-5^8)+(5^11-5^9)
    termes = [
        5**1, 5**2, 5**4, 5**5, 5**7, 5**8, 5**9,
        5**10 - 5**8,
        5**11 - 5**9,
    ]
    return sum(termes)


def _suite_A_n10_k6() -> int:
    # 6^1+6^2+6^3+6^4+6^5+6^6+6^7+6^8+(6^9-6^7)+(6^10+6^8)
    termes = [
        6**1, 6**2, 6**3, 6**4, 6**5, 6**6, 6**7, 6**8,
        6**9 - 6**7,
        6**10 + 6**8,
    ]
    return sum(termes)


def _suite_B_n10_k6() -> int:
    # 6^1+6^2+6^3+6^4+6^5+6^7+6^8+6^9+(6^10-6^8)+(6^11+6^9)
    termes = [
        6**1, 6**2, 6**3, 6**4, 6**5, 6**7, 6**8, 6**9,
        6**10 - 6**8,
        6**11 + 6**9,
    ]
    return sum(termes)


def _digamma_n10_k3(sumA: int) -> int:
    # Digamma = 3^8, soustrait
    return sumA - 3**8


def _digamma_n10_k5(sumA: int) -> int:
    # Digamma = +5^7, ajouté
    return sumA + 5**7


def _digamma_n10_k6(sumA: int) -> int:
    # Digamma = -6^7, soustrait
    return sumA - 6**7


def reconstruire_premier_n10(cfg: NonTypicalConfig) -> int:
    """
    Reconstruit le premier pour n = 10 selon le rapport non-typique 1/k.
    Utilise les exemples explicites pour k = 3, 5, 6.
    """
    k = cfg.k
    if k == 3:
        sumA = _suite_A_n10_k3()
        sumB = _suite_B_n10_k3()
        digamma_calc = _digamma_n10_k3(sumA)
        return (sumB - digamma_calc) // (3**6)
    elif k == 5:
        sumA = _suite_A_n10_k5()
        sumB = _suite_B_n10_k5()
        digamma_calc = _digamma_n10_k5(sumA)
        return (sumB - digamma_calc) // (5**6)
    elif k == 6:
        sumA = _suite_A_n10_k6()
        sumB = _suite_B_n10_k6()
        digamma_calc = _digamma_n10_k6(sumA)
        return (sumB - digamma_calc) // (6**6)
    else:
        # Générique : même schéma, mais sans exemple explicite
        # A et B sont des sommes de puissances de k, digamma à position cfg.digamma_position
        termes_A = [k**p for p in range(1, cfg.n + 1)]
        termes_B = [k**p for p in range(1, cfg.n + 2)]
        sumA = sum(termes_A)
        sumB = sum(termes_B)
        digamma = k**cfg.digamma_position
        if cfg.digamma_mode == "sub":
            digamma_calc = sumA - digamma
        else:
            digamma_calc = sumA + digamma
        return (sumB - digamma_calc) // (k**6)


def premiers_non_typiques(
    cfg: NonTypicalConfig,
    direction: str = "croissant",
    count: int = 10,
) -> list[int]:
    """
    À partir du premier reconstruit pour n = 10, génère les premiers
    suivants (croissants) ou précédents (décroissants).
    Ici, on laisse la structure spectrale telle quelle : ce sont des entiers
    reconstruits, pas filtrés par primalité mathématique.
    """
    base = reconstruire_premier_n10(cfg)

    if direction == "croissant":
        return [base + i for i in range(count)]
    else:
        # décroissant : on descend en dessous de n=10, puis vers -∞
        return [base - i for i in range(count)]
