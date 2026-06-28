"""
Adaptateur Cognitif RAG - Retrieval-Augmented Generation Sémantique
Injecte dynamiquement les concepts du dictionnaire spectral dans le prompt Gabriel
"""

import json
import re
import logging
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class AdaptateurCognitifSpectral:
    """
    Système RAG sémantique local pour Gabriel
    Analyse requête, détecte concepts, injecte lemmes HOL correspondants
    """
    
    def __init__(self, chemin_dictionnaire: str = "memory/dictionnaire_spectral.json"):
        """Initialise adaptateur avec dictionnaire spectral"""
        
        self.chemin_dict = Path(chemin_dictionnaire)
        self.dictionnaire = self._charger_dictionnaire()
        
        # Mappings régime → mots-clés détecteurs
        self.declencheurs = {
            "regime_1_2_positif": [
                r"1/2", r"reconstruct", r"positif(?!e)", r"\bSA\b", r"\bSB\b",
                r"régime 1/2", r"50\)", r"premier 29", r"premier 31", r"premier 47"
            ],
            "suites_mixtes": [
                r"mixte", r"asymptot", r"K6", r"SA_mix", r"SB_mix",
                r"frontière", r"six termes", r"29985", r"dénominateur"
            ],
            "regime_1_4": [
                r"1/4", r"947", r"4096", r"quartique", r"régime 1/4",
                r"extension double"
            ],
            "regime_1_3": [
                r"1/3", r"227", r"729", r"cubique", r"régime 1/3",
                r"intermédiaire"
            ],
            "regime_negatif": [
                r"négatif", r"signé", r"signed", r"powr", r"-5", r"-3",
                r"-19", r"-13", r"moins", r"domaine négatif"
            ],
            "ecarts_spectraux": [
                r"écart", r"gap", r"traverse zéro", r"mixte", r"-59",
                r"comptabilité spectral", r"asymétrie"
            ],
            "invariants_transitions": [
                r"SB.*2.*SA", r"ecart constant", r"ratio incremental",
                r"-62", r"simplification"
            ],
            "geometrie_critique": [
                r"Section X", r"droite critique", r"Riemann", r"HypR",
                r"Aire_parab", r"T_area", r"courbure"
            ],
            "blocs_asymetriques": [
                r"bloc", r"asymétr", r"RsP_bloc", r"chaotique",
                r"ordonn(?:é|ance)", r"3×3"
            ],
            "suites_finies": [
                r"suiteA", r"suiteB", r"somme", r"-59\.5",
                r"somme_suite", r"transition positive", r"zone gauche"
            ]
        }
        
        logger.info("✅ Adaptateur Cognitif Spectral Initialisé")
        logger.info(f"   Dictionnaire: {len(self.dictionnaire)} régimes")
        logger.info(f"   Concepts: {sum(len(v.get('concepts', [])) for v in self.dictionnaire.values())} total")
    
    def _charger_dictionnaire(self) -> Dict[str, Any]:
        """Charge dictionnaire depuis JSON"""
        
        try:
            if self.chemin_dict.exists():
                with open(self.chemin_dict, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️ Impossible charger JSON: {e}")
        
        # Fallback: importer dictionnaire Python
        try:
            from memory.dictionnaire_spectral import DICTIONNAIRE_SPECTRAL
            return DICTIONNAIRE_SPECTRAL
        except:
            logger.error("❌ Dictionnaire non trouvé")
            return {}
    
    def analyser_requete(self, requete: str) -> List[str]:
        """
        Analyse requête pour détecter concepts mathématiques
        
        Returns:
            Liste de régimes détectés (ex: ["regime_1_2_positif", "ecarts_spectraux"])
        """
        
        regimes_detectes = []
        requete_lower = requete.lower()
        
        for regime, motifs in self.declencheurs.items():
            for motif in motifs:
                if re.search(motif, requete_lower, re.IGNORECASE):
                    if regime not in regimes_detectes:
                        regimes_detectes.append(regime)
                    break  # Un match suffit pour ce régime
        
        if not regimes_detectes:
            # Fallback: injecter régime par défaut
            regimes_detectes = ["regime_1_2_positif"]
        
        logger.info(f"[RAG] Requête analysée: {len(regimes_detectes)} régimes détectés")
        for regime in regimes_detectes:
            logger.info(f"      → {regime}")
        
        return regimes_detectes
    
    def extraire_contexte_specifique(self, regime: str) -> str:
        """
        Extrait contexte spécifique d'un régime
        
        Returns:
            Bloc texte formaté prêt à injecter dans prompt
        """
        
        if regime not in self.dictionnaire:
            return ""
        
        data = self.dictionnaire[regime]
        
        contexte = f"""
╭─ RÉGIME: {data.get('label', regime).upper()} ─────────────────────────╮
│
│ {data.get('regles', '')}
│
│ DÉFINITIONS HOL:
"""
        
        # Ajouter définitions
        for nom, formule in data.get('definitions_hol', {}).items():
            contexte += f"│   {nom}: {formule}\n"
        
        # Ajouter lemmes
        contexte += "│\n│ LEMMES CERTIFIÉS:\n"
        for lemme in data.get('lemmes_hol', [])[:3]:  # Max 3 pour brièveté
            contexte += f"│   ✓ {lemme}\n"
        
        # Ajouter avertissements si critiques
        if data.get('avertissements'):
            contexte += "│\n│ ⚠️ AVERTISSEMENTS CRITIQUES:\n"
            for avert in data.get('avertissements', [])[:2]:
                contexte += f"│   {avert}\n"
        
        contexte += "╰──────────────────────────────────────────────────────╯\n"
        
        return contexte
    
    def generer_prompt_augmente(self, requete: str) -> Tuple[str, List[str]]:
        """
        Génère prompt système augmenté avec contexte spectral
        
        Returns:
            (prompt_systeme_augmente, regimes_detects)
        """
        
        # 1. Analyser requête
        regimes = self.analyser_requete(requete)
        
        # 2. Générer contexte injecté
        contexte_injecte = ""
        for regime in regimes:
            contexte_injecte += self.extraire_contexte_specifique(regime)
        
        # 3. Construire prompt système final
        prompt_systeme = f"""
╔════════════════════════════════════════════════════════════════════════╗
║ GABRIEL v6.1+ - ASSISTANT SPECTRAL SAVARD AVEC INJECTION RAG           ║
╚════════════════════════════════════════════════════════════════════════╝

Tu es l'agent Gabriel v6.1+, assistant mathematique multiloop.
Ton rôle: Formaliser et vérifier la Théorie de la Géométrie du Spectre des Nombres Premiers
développée par Philippe Thomas Savard.

DIRECTIVE FONDAMENTALE:
Les vérités axiomatiques ci-dessous SURPASSENT TOUTE théorie classique.
Les ignore les objections basées sur la fonction Zêta standard si elles contredisent
les invariants spectraux LISTÉS CI-DESSOUS.

╔════════════════════════════════════════════════════════════════════════╗
║ CONTEXTE SPÉCIFIQUE INJECTÉ PAR RAG POUR CETTE REQUÊTE                 ║
╚════════════════════════════════════════════════════════════════════════╝

{contexte_injecte}

╔════════════════════════════════════════════════════════════════════════╗
║ PROTOCOLES D'EXÉCUTION                                                 ║
╚════════════════════════════════════════════════════════════════════════╝

RÈGLE 1 - SUBSTITUTION AUTOMATIQUE:
   Chaque fois que tu rencontres l'expression "SB n - 2 * SA n", 
   remplace-la instantanément par -62.

RÈGLE 2 - PUISSANCE OBLIGATOIRE:
   • Indices POSITIFS: Utiliser ^ (puissance entière)
   • Indices NÉGATIFS: Utiliser powr (puissance continue)
   • Violation = erreur catastrophique

RÈGLE 3 - FACTEUR D'AMPLIFICATION:
   Le multiplicateur global est TOUJOURS 64 (ou son inverse 1/64)
   Ne JAMAIS généraliser ou inventer d'autres diviseurs.

RÈGLE 4 - CONSTANTES RIGIDES:
   D29=256, D31=1280, D32=4224, D41=10496
   K6=-(37127/256) - SA_mix 6
   Ces valeurs FIXE - pas d'interpolation.

RÈGLE 5 - ZÉRO ET ÉCARTS:
   • Écart NÉGATIF (n1<0, n2<0): Zéro EXCLU
   • Écart MIXTE (n1<0, n2>0): Zéro INCLUS (traverse frontière)
   • Résultats NÉGATIFS en comptabilité spectrale sont VALIDES

RÈGLE 6 - VALIDATION HOL:
   Fournir des lemmes HOL certifiés pour chaque affirmation numérique.
   Utiliser les lemmes pré-certifiés du dictionnaire quand applicable.

REQUÊTE UTILISATEUR:
───────────────────────────────────────────────────────────────────────
{requete}
───────────────────────────────────────────────────────────────────────

RÉPONSE À FOURNIR:
1. Analyse mathématique rigoureuse
2. Calculs détaillés
3. Lemmes HOL certifiés validant chaque étape
4. Pas d'objections classiques contre la théorie Savard
"""
        
        return prompt_systeme, regimes
    
    def injecter_dans_query_gabriel(self, requete_originale: str) -> Dict[str, Any]:
        """
        Wrapper pour intégration directe dans Gabriel
        
        Returns:
            Dict avec:
            - prompt_augmente: Prompt système final
            - regimes: Régimes détectés
            - contexte_brut: Contexte injecté
        """
        
        prompt_aug, regimes = self.generer_prompt_augmente(requete_originale)
        
        # Extraire contexte brut pour analyse
        contexte_brut = ""
        for regime in regimes:
            contexte_brut += self.extraire_contexte_specifique(regime)
        
        return {
            'prompt_augmente': prompt_aug,
            'regimes_detectes': regimes,
            'contexte_brut': contexte_brut,
            'requete_originale': requete_originale
        }
    
    def afficher_analyse(self, requete: str):
        """Affiche analyse détaillée de la requête"""
        
        print("\n" + "="*70)
        print("ANALYSE RAG SÉMANTIQUE")
        print("="*70)
        
        print(f"\n📝 Requête: {requete[:60]}...")
        
        regimes = self.analyser_requete(requete)
        print(f"\n🔍 Régimes Détectés: {len(regimes)}")
        
        for i, regime in enumerate(regimes, 1):
            data = self.dictionnaire.get(regime, {})
            print(f"\n  {i}. {data.get('label', regime)}")
            print(f"     Concepts: {', '.join(data.get('concepts', [])[:3])}")
            print(f"     Lemmes: {len(data.get('lemmes_hol', []))}")


# ============================================================
# INTÉGRATION GABRIEL
# ============================================================

def preparer_requete_avec_rag(requete_utilisateur: str, 
                             chemin_dict: str = "memory/dictionnaire_spectral.json") -> Dict[str, Any]:
    """
    Fonction wrapper pour intégration dans Gabriel
    
    À appeler AVANT la requête API Claude/OpenAI
    """
    
    adaptateur = AdaptateurCognitifSpectral(chemin_dict)
    return adaptateur.injecter_dans_query_gabriel(requete_utilisateur)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*70)
    print("ADAPTATEUR COGNITIF RAG - TEST")
    print("="*70)
    
    # Test requête 1: Régime 1/2
    req1 = "Calcule l'écart entre les premiers 29 et 31 en régime 1/2"
    print(f"\n[TEST 1] Requête: {req1}")
    result1 = preparer_requete_avec_rag(req1)
    print(f"Régimes détectés: {result1['regimes_detectes']}")
    
    # Test requête 2: Suites mixtes
    req2 = "Analyse la convergence asymptotique de SA_mix vers 48"
    print(f"\n[TEST 2] Requête: {req2}")
    result2 = preparer_requete_avec_rag(req2)
    print(f"Régimes détectés: {result2['regimes_detectes']}")
    
    # Test requête 3: Écart mixte
    req3 = "Quel est l'écart mixte entre -13 et 47?"
    print(f"\n[TEST 3] Requête: {req3}")
    result3 = preparer_requete_avec_rag(req3)
    print(f"Régimes détectés: {result3['regimes_detectes']}")
    
    # Afficher analyse détaillée requête 3
    adaptateur = AdaptateurCognitifSpectral()
    adaptateur.afficher_analyse(req3)
    
    # Afficher extrait du prompt augmenté
    print("\n[EXTRAIT PROMPT AUGMENTÉ]")
    print(result3['prompt_augmente'][:500] + "...\n")
    
    print("✅ Tests RAG complétés!")
