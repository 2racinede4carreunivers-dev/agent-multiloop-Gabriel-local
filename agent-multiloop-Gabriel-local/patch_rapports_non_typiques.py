#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PATCH — RAPPORTS NON-TYPIQUES 1/k<>1/2  (variateur mécanique de correction)

Ce patch encode la généralisation des rapports non-typiques 1/k<>1/2 dans la
programmation de Gabriel (méthode Savard — « L'Univers est au Carré »).

Il contient les opérations suivantes (à appliquer via la transmission) :

  1. `creer_fichier`  src/spectral/rapports_non_typiques.py
      → module exclusif : suites A/B 1/k<>1/2, Digamma 7e/8e position ±,
        reconstruction P=(Somme B − Digamma_calculé)/t^6,
        détermination du nombre de termes n (croissant/décroissant depuis n=10).

  2. `remplacer_texte` src/core/spectral_core.py
      → Injection d'une méthode publique `reconstruire_rapport_non_typique`
        sur SpectralMethodCore (accès direct au module depuis le moteur central).

  3. `remplacer_texte` (audit) src/core/spectral_core.py
      → L'AntiHallucinationValidator n'impose plus l'invariant n=position pour
        les rapports non-typiques (seulement pour 1/2) : utilise la nouvelle
        règle "n = nombre de termes".

  ,4. `executer_python` (test) — vérifie les 3 exemples de l'extrait.

Usage (UN CLIC) :
   cd C:\\agent-multiloop-Gabriel-local-final\\agent-multiloop-Gabriel-local
   python transmission_un_clic.py --patch patch_rapports_non_typiques.py --dry-run
   python transmission_un_clic.py --patch patch_rapports_non_typiques.py

(ou directement :  python orchestrator_main.py --apply patch_rapports_non_typiques.json)
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent

# ──────────────────────────────────────────────────────────────────────────
#  1) MODULE EXCLUSIF — lu depuis le disque pour garantir l'exactitude
# ──────────────────────────────────────────────────────────────────────────
MODULE_SOURCE = (REPO / "src" / "spectral" / "rapports_non_typiques.py")
MODULE_CODE = MODULE_SOURCE.read_text(encoding="utf-8") if MODULE_SOURCE.exists() else None
if MODULE_CODE is None:
    raise SystemExit(
        "Introuvable : src/spectral/rapports_non_typiques.py — placez le module "
        "(fourni) dans le dépôt avant d'exécuter ce patch."
    )

# ──────────────────────────────────────────────────────────────────────────
#  2. INTÉGRATION DANS SpectralMethodCore (spectral_core.py)
#     Ancre : le "# === MARQUEUR_TEXTATIQUE_4C4F4AE38E1 ===" en tête du fichier.
# ──────────────────────────────────────────────────────────────────────────
ANCRE_IMPORT = 'import re\n'
NOUVEAU_IMPORT = (
    'import re\n'
    '# [VARIATEUR] Rapports non-typiques 1/k<>1/2 (module exclusif)\n'
    'try:\n'
    '    from src.spectral.rapports_non_typiques import (\n'
    '        reconstruire_premier as rnt_reconstruire_premier,\n'
    '        reconstruire_premier_pour_n as rnt_reconstruire_pour_n,\n'
    '        determiner_n as rnt_determiner_n,\n'
    '        suite_A as rnt_suite_A, suite_B as rnt_suite_B,\n'
    '        verifier_exemples as rnt_verifier_exemples,\n'
    '    )\n'
    'except Exception:  # import relatif selon le point d\'entree\n'
    '    from ..spectral.rapports_non_typiques import (\n'
    '        reconstruire_premier as rnt_reconstruire_premier,\n'
    '        reconstruire_premier_pour_n as rnt_reconstruire_pour_n,\n'
    '        determiner_n as rnt_determiner_n,\n'
    '        suite_A as rnt_suite_A, suite_B as rnt_suite_B,\n'
    '        verifier_exemples as rnt_verifier_exemples,\n'
    '    )\n'
)

# ──────────────────────────────────────────────────────────────────────────
#  3. MÉTHODE PUBLIQUE à ajouter dans SpectralMethodCore
# ──────────────────────────────────────────────────────────────────────────
METHODE_RAPPORT_NON_TYPIQUE = '''

    # ──────────────────────────────────────────────────────────────────
    # [VARIATEUR] Rapport non-typique 1/k<>1/2
    # ──────────────────────────────────────────────────────────────────
    def reconstruire_rapport_non_typique(self, rapport: str, n: int = 10,
                                         position: Optional[int] = None,
                                         signe: Optional[int] = None) -> Dict:
        """Reconstruit le premier pour un rapport 1/k<>1/2 via le module exclusif.

        Retourne un dict {rapport, n/premier, A, B, digamma, position...}.
        """
        try:
            if n == 10:
                return rnt_reconstruire_premier(rapport, n=10,
                                                verifier=True)
            return rnt_reconstruire_pour_n(rapport, n=n)
        except Exception as exc:
            logger.debug("reconstruire_rapport_non_typique(%s) error %s", rapport, exc)
            return {"rapport": rapport, "premier": None, "error": str(exc)}

    def expliquer_rapport_non_typique(self, rapport: str, n: int = 10) -> str:
        res = self.reconstruire_rapport_non_typique(rapport, n=n)
        if not res.get("premier"):
            return f"[{rapport}] reconstruction impossible pour n={n}"
        retour = (
            f"Rapport non-typique {res.get('rapport')} | Somme A={res.get('A')}, "
            f"Somme B={res.get('B')}, Digamma={res.get('digamma_calcule')}, "
            f"premier reconstruit={res.get('premier')} (n={res.get('n')})"
        )
        return retour
'''

# ──────────────────────────────────────────────────────────────────────────
#  4. AUDIT — règle généralisée au lieu de "1/2 uniquement"
# ──────────────────────────────────────────────────────────────────────────
# La méthode actuelle AntiHallucinationValidator reproduit un code similaire
# à la règle 2 (INVARIANT 1/2). Le patch (mode contrat) ci-dessous effectue
# le remplacement minimal pour le rapport mentionné.
# (Voir opérations _AUDIT_OPERATIONS plus bas.)