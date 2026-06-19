"""
Gabriel LLM Integration - Intègre LLM Router dans Gabriel
Utilise Claude en priorité, OpenAI en fallback
"""

import logging
from typing import Dict, Any, Optional, Tuple

from src.llm_router import LLMRouter, TaskType
from src.prompt_injector import PromptInjector

logger = logging.getLogger(__name__)

class GabrielLLMIntegration:
    """Intègre routeur LLM dans Gabriel"""
    
    def __init__(self):
        """Initialise intégration"""
        self.router = LLMRouter()
        self.injector = PromptInjector()
        self.response_cache = {}
    
    def query_intelligent(self, question: str, 
                         task_type: Optional[TaskType] = None,
                         use_theory_context: bool = True,
                         validate_response: bool = True) -> Dict[str, Any]:
        """
        Requête intelligente:
        1. Classifier tâche
        2. Injecter contexte théorique si pertinent
        3. Router vers meilleur modèle (Claude → OpenAI)
        4. Valider réponse conformité
        
        Returns:
            {
                'response': str,
                'model': str,
                'task_type': str,
                'routing_decision': dict,
                'validation': dict,
                'tokens_used': int,
            }
        """
        
        logger.info(f"[Gabriel] Requête: {question[:50]}...")
        
        # Classifier si nécessaire
        if task_type is None:
            task_type = self.router.classify_task(question)
            logger.info(f"  → Tâche classifiée: {task_type.value}")
        
        # Injecter contexte théorique si applicable
        if use_theory_context:
            injected = self.injector.inject_for_ollama(question, str(task_type.value))
            prompt = injected
        else:
            prompt = question
        
        # Décider modèle
        decision = self.router.decide_model(task_type)
        logger.info(f"  → Modèle sélectionné: {decision.selected_model.upper()}")
        logger.info(f"  → Raison: {decision.reason}")
        
        # System prompt adapté
        system_prompt = self._build_system_prompt(task_type)
        
        try:
            # Requête via routeur
            response_text, metadata = self.router.query(
                prompt=prompt,
                task_type=task_type,
                system_prompt=system_prompt
            )
            
            # Validation si demandée
            validation_result = {}
            if validate_response and task_type != TaskType.GENERAL:
                validation_result = self.injector.validate_llm_response(
                    response_text,
                    str(task_type.value)
                )
                
                # Corriger si non-conforme
                if not validation_result.get('is_compliant', True):
                    logger.warning(f"  ⚠ Réponse non-conforme (score: {validation_result['score']:.2f})")
                    response_text = self.injector.rewrite_response(
                        response_text,
                        str(task_type.value)
                    )
                    logger.info(f"  → Réponse corrigée pour conformité")
            
            # Construire réponse complète
            result = {
                'response': response_text,
                'model': metadata['model'],
                'task_type': task_type.value,
                'routing_decision': {
                    'selected': decision.selected_model,
                    'reason': decision.reason,
                    'fallback': decision.fallback_model
                },
                'validation': validation_result,
                'tokens': metadata.get('tokens_used', 0),
                'tokens_detail': {
                    'input': metadata.get('input_tokens', 0),
                    'output': metadata.get('output_tokens', 0)
                }
            }
            
            logger.info(f"  ✓ Réponse obtenue ({result['tokens']} tokens)")
            
            return result
        
        except Exception as e:
            logger.error(f"  ✗ Erreur requête: {e}")
            return {
                'response': None,
                'error': str(e),
                'model': decision.selected_model,
                'task_type': task_type.value
            }
    
    def _build_system_prompt(self, task_type: TaskType) -> str:
        """Construit system prompt adapté à la tâche"""
        
        base_prompt = """Tu es Gabriel, un assistant mathématique multiloop de haut niveau.

Ton expertise couvre:
- Théorie personnelle "L'univers est au carré" (Philippe Thomas Savard)
- Géométrie spectrale asymétrique des nombres premiers
- Analyse RSA (Rapport Spectral Asymétrique Ordonné)
- Preuves formelles en HOL4/Lean4
- Validation de structures mathématiques rigoureuses"""
        
        # Adaptations spécifiques par tâche
        if task_type == TaskType.MATHEMATICAL_REASONING:
            return base_prompt + """

PRIORITÉ: Raisonnement mathématique rigoureux
- Structurer clairement les étapes
- Justifier chaque affirmation
- Utiliser notation formelle quand pertinent"""
        
        elif task_type == TaskType.CODE_VALIDATION:
            return base_prompt + """

PRIORITÉ: Validation de code formel
- Vérifier syntaxe HOL4/Lean4
- Détecter erreurs logiques
- Suggérer améliorations formelles"""
        
        elif task_type == TaskType.HOL_PROOF_GENERATION:
            return base_prompt + """

PRIORITÉ: Génération de preuves HOL4/Lean4
- Code HOL4/Lean4 syntaxiquement valide
- Preuves complètes et rigoureuses
- Commentaires explicatifs clairs"""
        
        elif task_type == TaskType.RIEMANN_ANALYSIS:
            return base_prompt + """

PRIORITÉ: Analyse géométrie spectrale
- Utiliser théorique Savard (Sr2=1.5, RSA, ordres multiples)
- Jamais théorie classique
- Convergence vers 0.5 comme fait géométrique"""
        
        elif task_type in [TaskType.CONTENT_GENERATION, TaskType.TEXT_FLUENCY]:
            return """Tu es Gabriel, assistant multiloop.

Ton rôle ici: générer contenu clair, fluide et engageant.
- Éloquence textuelle
- Communication accessible
- Structure narrative logique"""
        
        else:
            return base_prompt
    
    def get_routing_report(self) -> Dict[str, Any]:
        """Retourne rapport routing LLM"""
        
        stats = self.router.get_routing_stats()
        
        report = {
            'summary': {
                'total_requests': stats['total_requests'],
                'claude_percentage': f"{stats['claude_percentage']:.1f}%",
                'openai_percentage': f"{100 - stats['claude_percentage']:.1f}%"
            },
            'usage': {
                'claude_requests': stats['claude_requests'],
                'openai_requests': stats['openai_requests'],
                'claude_tokens': stats['claude_tokens'],
                'openai_tokens': stats['openai_tokens']
            },
            'rate_limits': stats['rate_limit_status']
        }
        
        return report
    
    def print_routing_stats(self):
        """Affiche statistiques routage"""
        
        report = self.get_routing_report()
        
        print("\n" + "="*70)
        print("LLM ROUTING STATISTICS")
        print("="*70)
        print(f"\nTotal requests: {report['summary']['total_requests']}")
        print(f"Claude (primary): {report['summary']['claude_percentage']}")
        print(f"OpenAI (fallback): {report['summary']['openai_percentage']}")
        print(f"\nTokens used:")
        print(f"  Claude: {report['usage']['claude_tokens']}")
        print(f"  OpenAI: {report['usage']['openai_tokens']}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Test intégration
    print("="*70)
    print("GABRIEL LLM INTEGRATION TEST")
    print("="*70)
    
    gabriel = GabrielLLMIntegration()
    
    # Test 1: Requête mathématique (Claude)
    print("\n[TEST 1] Requête mathématique")
    result = gabriel.query_intelligent(
        "Explique le rapport spectral asymétrique (RSA) et comment il converge vers 0.5"
    )
    
    if result.get('response'):
        print(f"✓ Modèle: {result['model'].upper()}")
        print(f"  Tokens: {result['tokens']}")
        print(f"  Réponse: {result['response'][:200]}...")
    
    # Stats finales
    gabriel.print_routing_stats()
