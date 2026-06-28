"""
Dictionnaire Spectral Savard - Base de connaissances JSON structurée
Contient tous les concepts, lemmes HOL et règles cognitives
"""

import json
from pathlib import Path

DICTIONNAIRE_SPECTRAL = {
    "regime_1_2_positif": {
        "label": "Régime 1/2 Positif",
        "concepts": ["SA", "SB", "prime_equation", "reconstruction_P"],
        "regles": """
RÈGLES COGNITIVES CRITIQUES:
1. SB n - 2 * SA n = -62 (invariant affine absolu)
2. Utiliser la puissance naturelle (^) pour les indices positifs
3. Le facteur d'amplification global reste fixé à 64
4. Rapport spectral 1/2 est l'invariant géométrique absolu
5. digamma_calc n p = SB n - 64 * p (absorption du premier)
""",
        "definitions_hol": {
            "SA": "SA n = (3.25 / 2) * (2 ^ n) - 2",
            "SB": "SB n = (6.5 / 2) * (2 ^ n) - 66",
            "digamma_calc": "digamma_calc n p = SB n - 64 * p",
            "prime_equation": "prime_equation n p = (SB n - digamma_calc n p) / 64"
        },
        "lemmes_hol": [
            "ecart_spectral_constant: SB n - 2 * SA n = -62",
            "ratio_incremental_un_demi: SA (Suc n) - SA n = (SB (Suc n) - SB n) / 2",
            "prime_equation_identity: prime_equation n p = real p",
            "reconstruction_premier_pos: (SB n - digamma_calc n p) / 64 = real p"
        ],
        "exemples": [
            "Premier 29: n=10, SA(10)=1650, SB(10)=3234",
            "Premier 31: n=11, SA(11)=3298, SB(11)=6498",
            "Premier 47: n=15, SA(15)=26214, SB(15)=52362"
        ]
    },
    
    "suites_mixtes": {
        "label": "Suites Mixtes (Régime Fractionnaire)",
        "concepts": ["SA_mix", "SB_mix", "digamma_mix", "K6", "asymptote"],
        "regles": """
RÈGLES COGNITIVES CRITIQUES:
1. Décroissance asymptotique (puissances de 2 au DÉNOMINATEUR)
2. NE PAS appliquer la croissance standard exponentielle
3. Isomorphisme de puissance continue (powr) obligatoire
4. SA_mix converge vers asymptote 48
5. SB_mix converge vers asymptote -28
6. Le facteur d'amplification reste 64 (sous forme 1/64)
7. K6 est la constante d'étalonnage stricte pour 6 termes négatifs
""",
        "definitions_hol": {
            "SA_mix_limit": "SA_mix n - 48 = 13 / (2 ^ (n + 2))",
            "SB_mix_limit": "SB_mix n + 28 = 13 / (2 ^ (n + 1))",
            "SA_mix_step": "SA_mix (Suc n) = SA_mix n - 13 / (2 ^ (n + 3))",
            "SB_mix_step": "SB_mix (Suc n) = SB_mix n - 13 / (2 ^ (n + 2))",
            "digamma_mix": "digamma_mix K n = SA_mix n + K n",
            "premier_mix": "premier_mix K n = 64 * (SB_mix n - digamma_mix K n)"
        },
        "constantes": {
            "K6": "-(37127 / 256) - SA_mix 6",
            "premier_mix_6": "29985 / 4"
        },
        "lemmes_hol": [
            "SA_mix_limit_shape: SA_mix n - 48 = 13 / (2 ^ (n + 2))",
            "SB_mix_limit_shape: SB_mix n + 28 = 13 / (2 ^ (n + 1))",
            "SA_mix_step: SA_mix (Suc n) = SA_mix n - 13 / (2 ^ (n + 3))",
            "SB_mix_step: SB_mix (Suc n) = SB_mix n - 13 / (2 ^ (n + 2))",
            "premier_mix_rewrite: premier_mix K n = 64 * (SB_mix n - digamma_mix K n)"
        ],
        "avertissements": [
            "INTERDICTION: Ne pas recalculer la forme fermée à chaque rang",
            "OBLIGATION: Utiliser les pas d'évolution (SA_mix_step, SB_mix_step)",
            "DANGER: Confusion avec le régime 1/2 - les puissances sont au DÉNOMINATEUR"
        ]
    },
    
    "regime_1_4": {
        "label": "Régime 1/4 (Extension Quartique)",
        "concepts": ["A_1_4", "B_1_4", "RsP_1_4", "prime_equation_1_4"],
        "regles": """
RÈGLES COGNITIVES CRITIQUES:
1. Rapport spectral strictement verrouillé à 1/4
2. Dénominateur d'extraction: 4096 (/ 4096)
3. Permet validation des premiers plus grands (ex: 947)
4. Formules spécifiques A_1_4 et B_1_4 non génériques
5. Invariant constant: (A_1_4(n1) - A_1_4(n2)) / (B_1_4(n1) - B_1_4(n2)) = 1/4
""",
        "definitions_hol": {
            "A_1_4": "A_1_4 n = (241/16 / 12) * (4 ^ n) - 4/3",
            "B_1_4": "B_1_4 n = (964/16 / 12) * (4 ^ n) - (3073 * 4/3)",
            "prime_equation_1_4": "prime_1_4 n p = (B_1_4 n - digamma_1_4 n p) / 4096"
        },
        "lemmes_hol": [
            "RsP_un_quart_constant: (A_1_4 n1 - A_1_4 n2) / (B_1_4 n1 - B_1_4 n2) = 1/4",
            "prime_equation_1_4_identity: prime_1_4 n p = real p"
        ],
        "exemples": [
            "Premier 947: Validation complète via régime 1/4"
        ],
        "avertissements": [
            "Dénominateur 4096 est FIXE - pas de généralisation"
        ]
    },
    
    "regime_1_3": {
        "label": "Régime 1/3 (Extension Cubique)",
        "concepts": ["A_1_3", "B_1_3", "RsP_1_3", "prime_equation_1_3"],
        "regles": """
RÈGLES COGNITIVES CRITIQUES:
1. Rapport spectral strictement verrouillé à 1/3
2. Dénominateur d'extraction: 729 (/ 729)
3. Structure intermédiaire validée (ex: premier 227)
4. Invariant constant: (A_1_3(n1) - A_1_3(n2)) / (B_1_3(n1) - B_1_3(n2)) = 1/3
""",
        "definitions_hol": {
            "A_1_3": "A_1_3 n = (73/9 / 12) * (3 ^ n) - 1.5",
            "B_1_3": "B_1_3 n = (219/9 / 12) * (3 ^ n) - (487 * 1.5)",
            "prime_equation_1_3": "prime_1_3 n p = (B_1_3 n - digamma_1_3 n p) / 729"
        },
        "lemmes_hol": [
            "RsP_un_tiers_constant: (A_1_3 n1 - A_1_3 n2) / (B_1_3 n1 - B_1_3 n2) = 1/3",
            "prime_equation_1_3_identity: prime_1_3 n p = real p"
        ],
        "exemples": [
            "Premier 227: Validation complète via régime 1/3"
        ],
        "avertissements": [
            "Dénominateur 729 est FIXE - pas de généralisation"
        ]
    },
    
    "regime_negatif": {
        "label": "Régime Négatif et Signé",
        "concepts": ["SA_signed", "SB_signed", "powr", "digamma_neg", "gap_neg_val"],
        "regles": """
RÈGLES COGNITIVES CRITIQUES:
1. OBLIGATION: Utiliser powr (puissance continue) pour indices négatifs
2. INTERDICTION: Utiliser ^ (puissance entière) sur indices < 0
3. Rapport spectral négatif reste 1/2
4. Exemple: n=-3 → utiliser 2 powr (-3) = 1/8
5. Formule écart négatif: (A_next - (B_high - D_high) - D_low) / 64
6. Zéro EXCLU des écarts de même signe (négatif seul)
""",
        "definitions_hol": {
            "SA_signed": "SA_signed n = 3.25 / 2 * (2 powr n) - 2",
            "SB_signed": "SB_signed n = 6.5 / 2 * (2 powr n) - 66",
            "digamma_neg": "digamma_neg n p = SB_signed n - 64 * p",
            "gap_neg_val": "(A_next - (B_high - D_high) - D_low) / 64"
        },
        "lemmes_hol": [
            "spectral_ratio_neg_un_demi: Rapport spectral négatif = 1/2",
            "gap_negative_exact: gap_neg_val entre -19 et -5 = -13"
        ],
        "exemples": [
            "n=-3: SA_signed(-3) = 3.25/2 * (2 powr -3) - 2 = 1.625 * 0.125 - 2 = -1.796875",
            "Écart entre -19 et -5: Résultat exact = -13"
        ],
        "avertissements": [
            "DANGER CRITIQUE: Confusion ^ vs powr causera erreurs catastrophiques",
            "Les puissances de 2 au DÉNOMINATEUR (powr négatif)",
            "Zéro ne compte PAS dans écarts négatifs purs"
        ]
    },
    
    "ecarts_spectraux": {
        "label": "Écarts Spectraux (Gaps)",
        "concepts": ["gap_neg_val", "gap_mix_val", "asymmetrie", "traversee_zero"],
        "regles": """
RÈGLES COGNITIVES CRITIQUES:
1. Écart NÉGATIF (n1<0, n2<0): Formule (A_next - (B_high - D_high) - D_low) / 64
2. Écart MIXTE (n1<0, n2>0): Même formule MAIS zéro EST COMPTÉ
3. Asymétrie ordonnée: Zéro traverse = traversée de la frontière
4. L'écart mixte est asymétrique: gap_mix(n1, n2) ≠ gap_mix(n2, n1)
5. Résultats peuvent être NÉGATIFS (comptabilité spectrale)
""",
        "definitions_hol": {
            "gap_neg_val": "(A_next - (B_high - D_high) - D_low) / 64",
            "gap_mix_val": "(SA(n_next) - (SB(n_max) - dgm(n_max)) - dgm(n_min)) / 64"
        },
        "lemmes_hol": [
            "gap_negative_between_minus_19_and_minus_5: -13",
            "gap_mixed_between_minus_13_and_47: -59",
            "gap_asymmetry: gap_mixed p1 p2 ≠ gap_mixed p2 p1"
        ],
        "exemples": [
            "Écart négatif -19 à -5: -13 (deux premiers négatifs)",
            "Écart mixte -13 à 47: -59 (traverse zéro)",
            "Écart mixte -31 à 17: -47 (traverse zéro)"
        ],
        "avertissements": [
            "Résultats NÉGATIFS sont VALIDES en comptabilité spectrale",
            "Zéro: Exclu si écart négatif seul, Inclus si écart mixte",
            "Ne pas confondre comptabilité spectrale avec décompte classique"
        ]
    },
    
    "invariants_transitions": {
        "label": "Invariants de Transition Linéaire",
        "concepts": ["ecart_spectral_constant", "ratio_incremental"],
        "regles": """
RÈGLES COGNITIVES CRITIQUES:
1. SB n - 2 * SA n = -62 (INVARIANT ABSOLU)
2. Chaque fois que vous croisez cette expression, REMPLACER par -62
3. SA (Suc n) - SA n = (SB (Suc n) - SB n) / 2
4. La vitesse de croissance de SA est EXACTEMENT moitié de SB
5. Ces invariants sont des RÈGLES DE SIMPLIFICATION AUTOMATIQUE
""",
        "definitions_hol": {
            "ecart_constant": "SB n - 2 * SA n = -62",
            "ratio_incremental": "SA (Suc n) - SA n = (SB (Suc n) - SB n) / 2"
        },
        "lemmes_hol": [
            "ecart_spectral_constant: SB n - 2 * SA n = -62",
            "ratio_incremental_un_demi: SA (Suc n) - SA n = (SB (Suc n) - SB n) / 2",
            "digamma_affine_en_SA: digamma_calc n p = 2 * SA n - (62 + 64 * real p)"
        ],
        "regles_simplification": [
            "Pattern: SB n - 2 * SA n → Remplacer par -62",
            "Pattern: SA (Suc n) - SA n → Remplacer par (SB (Suc n) - SB n) / 2"
        ]
    },
    
    "geometrie_critique": {
        "label": "Géométrie de la Droite Critique (Section X)",
        "concepts": ["T_area", "T_tr_area", "T_restant_area", "Aire_parab", "HypR_demi_solFinal"],
        "regles": """
RÈGLES COGNITIVES CRITIQUES:
1. Conservation géométrique: T_area = T_tr_area + T_restant_area
2. Aire parabolique (courbure): Aire_parab = surplus combinatoire mixte
3. Condition Riemann: Aire_parab = T_restant_area ⟹ HypR_demi_solFinal = True
4. NE JAMAIS valider HR par méthodes analytiques traditionnelles
5. OBLIGATION: Passer par comparaison des trois constats géométriques
""",
        "definitions_hol": {
            "T_area": "Aire du rectangle des zéros critiques",
            "T_tr_area": "Aire tronquée spectrale (intervalle fini)",
            "T_restant_area": "Aire restante d'écart",
            "Aire_parab": "Aire parabolique de sur-combinatoire",
            "postulate_aire_rectangle": "T_area = T_tr_area + T_restant_area",
            "postulate_solution": "Aire_parab = T_restant_area ⟹ HypR_demi_solFinal"
        },
        "lemmes_hol": [
            "aire_conservation: T_area = T_tr_area + T_restant_area",
            "riemann_condition: Aire_parab = T_restant_area → HypR_demi_solFinal"
        ],
        "avertissements": [
            "RÈGLE TRIFOCALE: Interdiction d'évaluer HypR par méthodes traditionnelles",
            "OBLIGATION: Transiter par trois constats géométriques",
            "Ne pas mélanger avec fonction Zêta classique"
        ]
    },
    
    "blocs_asymetriques": {
        "label": "Blocs Asymétriques et Ordonnances",
        "concepts": ["asymetrique_ordonnee", "asymetrique_chaotique", "RsP_bloc"],
        "regles": """
RÈGLES COGNITIVES CRITIQUES:
1. Asymétrie Ordonnée: B a exactement length(A) + 1 éléments
2. Asymétrie Chaotique: Longueurs différentes, pas de transition consécutive
3. RsP_bloc (rapport spectral de bloc) dépend de la structure
4. Régime ordonné: RsP_bloc → 1 (à mesure que blocs s'étendent)
5. Régime chaotique: RsP_bloc → 1/k (k = ratio de tailles)
""",
        "definitions_hol": {
            "asymetrique_ordonnee": "length B = length A + 1, dernier(A) < premier(B)",
            "asymetrique_chaotique": "length A ≠ length B, pas de transition consécutive",
            "RsP_bloc": "sum(SA) / sum(SB) pour listes d'indices"
        },
        "lemmes_hol": [
            "asymetrique_ordonnee_nat: Définition formelle HOL",
            "asymetrique_chaotique_nat: Définition formelle HOL",
            "rsp_bloc_comportement: RsP_bloc → 1/k (régime chaotique)"
        ],
        "exemples": [
            "Bloc 3×3 ordonné: A3=[2,9,10], B3=[3,11,15]",
            "Bloc chaotique: Longueurs différentes sans pattern"
        ]
    },
    
    "suites_finies": {
        "label": "Suites Finies et Ancrages Numériques",
        "concepts": ["suiteA_1", "suiteB_11", "somme_suiteA_11", "transition_positive"],
        "regles": """
RÈGLES COGNITIVES CRITIQUES:
1. Ne PAS générer suites génériques - utiliser segments EXACTS
2. suiteA et suiteB définies explicitement pour chaque premier
3. sum(suiteA_n) = SA(n), sum(suiteB_n) = SB(n) (correspondances garanties)
4. Transition positive: À n=8, infrastructure de SB abandonne -59.5
5. Zone gauche (n≤7): Inclut -59.5 comme ancre d'origine
""",
        "definitions_hol": {
            "suiteA_1": "[2]",
            "suiteA_2": "[2, 3]",
            "suiteA_3": "[2, 3, 6]",
            "suiteB_1": "[-59.5]",
            "suiteB_11": "[-59.5, 6.5, 13, 26, 52]"
        },
        "sommes": {
            "somme_suiteA_11": "sum_list suiteA_11 = SA 5 = 50",
            "somme_suiteB_11": "sum_list suiteB_11 = SB 5 = 38",
            "somme_suiteB_8": "sum_list suiteB_8 = SB 8"
        },
        "lemmes_hol": [
            "somme_suiteA_11: sum_list [2,4,8,12,24] = SA 5",
            "somme_suiteB_11: sum_list [-59.5,6.5,13,26,52] = SB 5"
        ],
        "avertissements": [
            "Pas de suites 'par défaut' - utiliser définitions explicites",
            "Transition -59.5 critère n=8 (point d'inflexion)",
            "Zone négative: -59.5 FIXE dans toutes les suiteB ≤ 7"
        ]
    }
}


def save_dictionnaire_json(path: str = "memory/dictionnaire_spectral.json"):
    """Sauvegarde dictionnaire en JSON"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(DICTIONNAIRE_SPECTRAL, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Dictionnaire sauvegardé: {path}")
    return path


def load_dictionnaire_json(path: str = "memory/dictionnaire_spectral.json"):
    """Charge dictionnaire depuis JSON"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


if __name__ == '__main__':
    # Test
    save_dictionnaire_json()
    
    # Afficher résumé
    print("\n" + "="*70)
    print("DICTIONNAIRE SPECTRAL SAVARD - RÉSUMÉ")
    print("="*70)
    
    for regime, data in DICTIONNAIRE_SPECTRAL.items():
        print(f"\n🔹 {data['label']}")
        print(f"   Concepts: {', '.join(data['concepts'][:3])}...")
        print(f"   Lemmes: {len(data.get('lemmes_hol', []))} théorèmes")
