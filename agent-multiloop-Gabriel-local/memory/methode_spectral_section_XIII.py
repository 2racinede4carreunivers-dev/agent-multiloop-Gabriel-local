"""Section XIII - Le Pont Savard : psi de Tchebychev, zeta et Re(rho) = 1/2.

Ce module assure l'APPRENTISSAGE de la Section XIII de methode_spectral.thy
par Gabriel : les regles du Pont Savard deviennent des entrees ontologiques
injectables dans les prompts LLM via le Dictionnaire Spectral RAG.

Contenu appris :
  - L'equation psi_savard (variante spectrale de Tchebychev, base log10).
  - Les 4 validations numeriques canoniques de Philippe (30, 98, 228, -100).
  - Le Premier Pont (unicite fonctionnelle Tchebychev <-> zeta).
  - Le Deuxieme Pont (exclusivite sur P par l'absurde, 3 piliers).
  - Le Theoreme de l'Ensemble (locale ensemble_savard, satisfaisabilite
    prouvee via RsP 1 2 = 1/2) et la conclusion RsP = Re = 1/2.
  - Le statut epistemologique HONNETE (pont constructif, PAS une preuve de RH).

Source     : methode_spectral.thy (Section XIII, v3.32).
Auteur     : Philippe Thomas Savard.
Validation : psi_savard(30,10)=28.888143698, psi_savard(98,25)=96.894150249,
             psi_savard(228,49)=226.894132001, psi_savard(-100,-26)=-100.798158152.
"""
from __future__ import annotations

import math
from typing import Any


SECTION_XIII_TITLE = "XIII. Le Pont Savard : psi de Tchebychev, fonction zeta et Re(rho) = 1/2"


# Nomenclature originale de l'auteur <-> symboles formels du locale Isabelle
NOMENCLATURE_ENSEMBLE: dict[str, dict[str, str]] = {
    "1/y1": {"symbole": "zeta_tchebychev", "sens": "composante Tchebychev de zeta"},
    "1/y2": {"symbole": "zeta_critique", "sens": "droite critique Re(rho) = 1/2"},
    "1/y3": {"symbole": "zeta_positions", "sens": "positions des premiers dans zeta"},
    "1/t": {"symbole": "tau_savard", "sens": "equation psi_savard"},
    "1/ms1": {"symbole": "ms_reconstruction", "sens": "reconstruction du i-ieme premier"},
    "1/ms2": {"symbole": "ms_exclusion", "sens": "exclusion des composes (3 piliers)"},
    "1/ms3": {"symbole": "ms_rapport", "sens": "rapport spectral RsP = 1/2"},
}


# Validations numeriques canoniques (verifiees a 1e-9 pres, base log10)
VALIDATIONS_CANONIQUES: list[dict[str, Any]] = [
    {"n": 10, "x": 30.0, "psi_savard": 28.888143698680, "premier_vise": 29},
    {"n": 25, "x": 98.0, "psi_savard": 96.894150248989, "premier_vise": 97},
    {"n": 49, "x": 228.0, "psi_savard": 226.894132001183, "premier_vise": 227},
    {"n": -26, "x": -100.0, "psi_savard": -100.798158152322, "premier_vise": -101},
]


SECTION_XIII_REGLES: list[dict[str, Any]] = [
    {
        "code": "XIII.1",
        "nom": "equation_psi_savard",
        "regle": (
            "psi_savard(x, n) = x - (2^n / SB(n)) - log10(2*pi) "
            "- (1/2)*log10(1 - 1/x^2), ou SB(n) = 3.25*2^n - 66. "
            "Variante spectrale de la formule de Riemann-von Mangoldt : la somme "
            "infinie sur les zeros non-triviaux sum_{rho}(x^rho/rho) est substituee "
            "par le terme UNIQUE rapport_zeta_savard(n) = 2^n/SB(n). "
            "Base logarithmique : log10 (choix de l'auteur)."
        ),
        "domaine_validite": "x reel avec |x| > 1, n = rang du n-ieme premier",
    },
    {
        "code": "XIII.2",
        "nom": "validations_numeriques_canoniques",
        "regle": (
            "4 validations exactes de Philippe Savard : "
            "psi_savard(30, 10) = 28.888143698 (premier 29) ; "
            "psi_savard(98, 25) = 96.894150249 (premier 97) ; "
            "psi_savard(228, 49) = 226.894132001 (premier 227) ; "
            "psi_savard(-100, -26) = -100.798158152 (premier -101, regime negatif, "
            "SB tend vers -66 quand n -> -inf). "
            "Comportement : psi_savard(x, n) ~ x - 1, erreur epsilon(x) ~ 0.11 "
            "qui diminue quand |x| augmente. Par defaut x = prime(n) + 1."
        ),
        "domaine_validite": "n in [-1000..-1] U [1..1000], lemmes rapport_zeta_savard_at_{10,25,49}",
    },
    {
        "code": "XIII.3",
        "nom": "premier_pont_unicite_fonctionnelle",
        "regle": (
            "L'equation de Tchebychev n'a d'utilite et de sens QUE pour la fonction "
            "zeta de Riemann (formule explicite de Riemann-von Mangoldt). La "
            "substitution numeriquement exacte de psi_savard dans ce role prouve "
            "que la Methode Spectrale et la fonction zeta traitent du MEME sujet. "
            "Formalisation : predicat concerne_fonction_zeta utilise en HYPOTHESE "
            "des theoremes finaux (aucun axiome global introduit)."
        ),
        "domaine_validite": "pont conceptuel, hypothese explicite des theoremes",
    },
    {
        "code": "XIII.4",
        "nom": "deuxieme_pont_exclusivite_P",
        "regle": (
            "La Methode Spectrale exclut strictement tout compose C (preuve par "
            "l'absurde) : elle n'admet de solution que pour les premiers P. "
            "3 piliers prouves : composite_not_prime_i (ecarts), "
            "composite_no_reconstruction_position (reconstruction), "
            "composite_pair_no_rsp_positions (rapport RsP). "
            "Forme condensee : lemme methode_spectrale_exclusivite_P "
            "(not prime C ==> forall i. C != prime_i i)."
        ),
        "domaine_validite": "tout compose C, corpus canonique {4, 9, 15, 51, 91, 121}",
    },
    {
        "code": "XIII.5",
        "nom": "theoreme_de_l_ensemble",
        "regle": (
            "Nomenclature Savard : 1/x = zeta = 1/y1 + 1/y2 + 1/y3 "
            "(y1=Tchebychev, y2=Re=1/2, y3=positions P) ; 1/t = psi_savard avec "
            "1/y1 = 1/t ; 1/ms = Methode Spectrale = 1/ms1 + 1/ms2 + 1/ms3 "
            "(ms1=position i-ieme premier, ms2=composes exclus, ms3=RsP=1/2). "
            "Conclusion : 1/ms3 = 1/y2, donc Re(rho) = 1/2 VRAI sur P. "
            "Formalisation COHERENTE : locale ensemble_savard (hypotheses "
            "hypothese_critique, pont_fonctionnel, rapport_un_demi) avec "
            "satisfaisabilite DEMONTREE (theoreme ensemble_savard_satisfaisable, "
            "temoin concret RsP 1 2 = 1/2 via RsP_un_demi_general). "
            "AUCUNE axiomatisation contradictoire."
        ),
        "domaine_validite": "locale Isabelle, theoremes alignement_central / alignement_inverse / conclusion_ensemble",
    },
    {
        "code": "XIII.6",
        "nom": "conclusion_rsp_egale_re_un_demi",
        "regle": (
            "Re_droite_critique(n1, n2) = RsP(n1, n2) = 1/2 pour n1, n2 >= 1 et "
            "n1 != n2 (theoremes pont_spectral_direct_final et synthese_pont_savard). "
            "Chaine du pont : Tchebychev <-> psi_savard <-> Suites A/B <-> Premiers "
            "reconstruits. Donc sur l'ensemble des premiers P : RsP = Re = 1/2 (VRAI)."
        ),
        "domaine_validite": "n1, n2 >= 1, n1 != n2",
    },
    {
        "code": "XIII.7",
        "nom": "statut_epistemologique_honnete",
        "regle": (
            "La Section XIII N'EST PAS une preuve deductive de l'hypothese de "
            "Riemann. C'est un pont CONSTRUCTIF, numeriquement exact et "
            "structurellement coherent, entre la Methode Spectrale et la droite "
            "critique. Toujours presenter ce resultat comme un pont/une conjecture "
            "constructive, jamais comme 'RH est prouvee'."
        ),
        "domaine_validite": "obligatoire dans toute reponse sur le Pont Savard",
    },
]


def get_section_XIII_entries() -> list[dict[str, Any]]:
    """Retourne les regles de la Section XIII sous forme d'entrees RAG
    consommables par adaptateur_cognitif_rag.py."""
    return [
        {
            "id": f"section_XIII_{r['code']}",
            "titre": f"Section XIII / {r['code']} - {r['nom']}",
            "contenu": r["regle"],
            "metadata": {
                "section": "XIII",
                "code": r["code"],
                "domaine_validite": r["domaine_validite"],
                "source_thy": "methode_spectral.thy (Section XIII, v3.32)",
            },
        }
        for r in SECTION_XIII_REGLES
    ]


def render_section_XIII_summary() -> str:
    """Resume textuel pour injection dans un prompt LLM."""
    lines = [f"=== {SECTION_XIII_TITLE} ==="]
    for r in SECTION_XIII_REGLES:
        lines.append(f"\n[{r['code']}] {r['nom']} ({r['domaine_validite']}):")
        lines.append(f"  {r['regle']}")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Helpers de calcul (utilisables par le pipeline cognitif)
# --------------------------------------------------------------------------
def sb_reel(n: int) -> float:
    """SB(n) = 3.25 * 2^n - 66 (formule reelle, valide aussi pour n < 0)."""
    return 3.25 * (2.0 ** n) - 66.0


def rapport_zeta_savard(n: int) -> float:
    """Terme spectral 2^n / SB(n) qui remplace la somme sur les zeros."""
    return (2.0 ** n) / sb_reel(n)


def psi_savard(x: float, n: int) -> float:
    """Equation psi_savard (base log10). Exige |x| > 1 et n != 0."""
    if n == 0:
        raise ValueError("n = 0 n'a pas de sens spectral (rang du n-ieme premier)")
    if x * x <= 1:
        raise ValueError(f"|x| doit etre > 1 (recu x={x})")
    return (
        x
        - rapport_zeta_savard(n)
        - math.log10(2.0 * math.pi)
        - 0.5 * math.log10(1.0 - 1.0 / (x * x))
    )


def verifier_validations_canoniques(tol: float = 1e-9) -> list[dict[str, Any]]:
    """Rejoue les 4 validations canoniques de Philippe et retourne le verdict."""
    resultats = []
    for v in VALIDATIONS_CANONIQUES:
        calcule = psi_savard(v["x"], v["n"])
        resultats.append({
            **v,
            "calcule": calcule,
            "ok": math.isclose(calcule, v["psi_savard"], abs_tol=tol),
        })
    return resultats


if __name__ == "__main__":
    print(render_section_XIII_summary())
    print(f"\n{len(get_section_XIII_entries())} entrees RAG generees.")
    print("\n--- Validations canoniques Philippe ---")
    for r in verifier_validations_canoniques():
        statut = "OK " if r["ok"] else "FAIL"
        print(f"  [{statut}] psi_savard({r['x']:.0f}, {r['n']}) = {r['calcule']:.9f} "
              f"(attendu {r['psi_savard']:.9f}, premier vise {r['premier_vise']})")
