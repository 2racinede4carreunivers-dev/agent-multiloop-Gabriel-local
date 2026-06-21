"""
Gabriel v6.2 - Intégration du système RAG sémantique
Injecte automatiquement le contexte spectral dans chaque requête
"""

import logging
from typing import Dict, Any, Optional

from src.gabriel_llm_integration_v2 import GabrielLLMIntegrationV2
from memory.adaptateur_cognitif_rag import preparer_requete_avec_rag, AdaptateurCognitifSpectral

logger = logging.getLogger(__name__)

class GabrielWithSemanticRAG:
    """
    Gabriel v6.2 avec système RAG sémantique
    Injecte automatiquement contexte spectral avant requête API
    """
    
    def __init__(self, monthly_budget_usd: float = 7.0):
        """Initialise Gabriel v6.2 avec RAG"""
        
        self.gabriel = GabrielLLMIntegrationV2(monthly_budget_usd)
        self.adaptateur_rag = AdaptateurCognitifSpectral()
        self.historique_rag = []
        
        logger.info("✅ Gabriel v6.2 Initialized")
        logger.info("   RAG Sémantique: ENABLED")
        logger.info("   Injection Dynamique: ENABLED")
    
    def query_with_rag(self, 
                      question: str,
                      use_rag: bool = True,
                      verbose_rag: bool = False) -> Dict[str, Any]:
        """
        Requête Gabriel avec injection RAG automatique
        
        Args:
            question: Requête utilisateur
            use_rag: Activer injection RAG (défaut: True)
            verbose_rag: Afficher analyse RAG (défaut: False)
        
        Returns:
            Réponse Gabriel augmentée avec métadonnées RAG
        """
        
        logger.info(f"[Gabriel RAG] Requête: {question[:50]}...")
        
        # 1. Préparation RAG
        if use_rag:
            rag_data = preparer_requete_avec_rag(question)
            prompt_augmente = rag_data['prompt_augmente']
            regimes_detectes = rag_data['regimes_detectes']
            
            if verbose_rag:
                self.adaptateur_rag.afficher_analyse(question)
            
            logger.info(f"  → RAG: {len(regimes_detectes)} régimes injectés")
        else:
            prompt_augmente = question
            regimes_detectes = []
            logger.info("  → RAG: DÉSACTIVÉ")
        
        # 2. Requête Gabriel avec prompt augmenté
        result = self.gabriel.query_intelligent(
            prompt_augmente,
            use_theory_context=True,
            validate_response=True
        )
        
        # 3. Ajouter métadonnées RAG à résultat
        result['rag_metadata'] = {
            'rag_active': use_rag,
            'regimes_injectes': regimes_detectes,
            'nombre_regimes': len(regimes_detectes),
            'contexte_brut': rag_data.get('contexte_brut', '') if use_rag else ''
        }
        
        # 4. Historique RAG
        self.historique_rag.append({
            'requete': question,
            'regimes': regimes_detectes,
            'model': result['model'],
            'tokens': result['tokens']
        })
        
        logger.info(f"  ✓ Réponse: {result['tokens']} tokens via {result['model'].upper()}")
        
        return result
    
    def get_rag_stats(self) -> Dict[str, Any]:
        """Retourne statistiques utilisation RAG"""
        
        if not self.historique_rag:
            return {'total_queries': 0}
        
        regime_counts = {}
        for entry in self.historique_rag:
            for regime in entry['regimes']:
                regime_counts[regime] = regime_counts.get(regime, 0) + 1
        
        return {
            'total_queries': len(self.historique_rag),
            'regime_distribution': regime_counts,
            'average_regimes_per_query': sum(len(e['regimes']) for e in self.historique_rag) / len(self.historique_rag)
        }
    
    def print_rag_report(self):
        """Affiche rapport utilisation RAG"""
        
        stats = self.get_rag_stats()
        
        print("\n" + "="*70)
        print("GABRIEL v6.2 - RAPPORT RAG SÉMANTIQUE")
        print("="*70)
        
        print(f"\n📊 STATISTIQUES:")
        print(f"   Total requêtes: {stats['total_queries']}")
        print(f"   Régimes/requête (moy): {stats.get('average_regimes_per_query', 0):.1f}")
        
        print(f"\n📈 DISTRIBUTION RÉGIMES:")
        for regime, count in sorted(stats['regime_distribution'].items(), 
                                   key=lambda x: x[1], reverse=True):
            pct = (count / stats['total_queries']) * 100
            print(f"   {regime}: {count} ({pct:.0f}%)")
        
        print("\n" + "="*70)


# ============================================================
# INTÉGRATION DANS BOUCLE CLAUDE
# ============================================================

def integrate_rag_in_claude_query(requete: str, 
                                 gabriel_instance: Optional[GabrielWithSemanticRAG] = None,
                                 use_rag: bool = True) -> Dict[str, Any]:
    """
    Wrapper pour intégration directe dans requête Claude
    
    À utiliser dans gabriel_llm_integration_v2.query_intelligent()
    """
    
    if gabriel_instance is None:
        gabriel_instance = GabrielWithSemanticRAG()
    
    return gabriel_instance.query_with_rag(requete, use_rag=use_rag)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*70)
    print("GABRIEL v6.2 - RAG SÉMANTIQUE TEST")
    print("="*70)
    
    # Initialiser Gabriel avec RAG
    gabriel = GabrielWithSemanticRAG(monthly_budget_usd=7.0)
    
    print("\n[TEST 1] Requête simple 1/2")
    print("─" * 70)
    result1 = gabriel.query_with_rag(
        "Calcule l'écart entre les premiers 29 et 31 en régime 1/2",
        verbose_rag=True
    )
    print(f"✓ Régimes: {result1['rag_metadata']['regimes_injectes']}")
    print(f"✓ Tokens: {result1['tokens']}")
    
    print("\n[TEST 2] Requête complexe: écart mixte + HOL4")
    print("─" * 70)
    result2 = gabriel.query_with_rag(
        "Quel est l'écart mixte entre -13 et 47? Génère le script HOL4 de validation",
        verbose_rag=True
    )
    print(f"✓ Régimes: {result2['rag_metadata']['regimes_injectes']}")
    print(f"✓ Model: {result2['model'].upper()}")
    
    print("\n[TEST 3] Requête sans RAG (baseline)")
    print("─" * 70)
    result3 = gabriel.query_with_rag(
        "Explique le régime 1/3",
        use_rag=False
    )
    print(f"✓ RAG: {result3['rag_metadata']['rag_active']}")
    
    # Afficher rapport
    print("\n[RAPPORT FINAL]")
    print("─" * 70)
    gabriel.print_rag_report()
    
    print("\n✅ Tests Gabriel v6.2 complets!")
