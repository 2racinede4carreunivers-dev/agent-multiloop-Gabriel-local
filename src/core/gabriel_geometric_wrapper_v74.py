#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WRAPPER GABRIEL - INTÉGRATION MÉTAPHORES GÉOMÉTRIQUES + FALLBACK GÉOMÉTRIQUE
=============================================================================

Ajoute automatiquement un bloc "Structure Géométrique Spatiale"
à chaque réponse de Gabriel.

v7.4 — Ajout du pipeline des suites géométriques A et B (Philippe Savard 2026)
       et du mécanisme de fallback géométrique automatique :
         Si l'approche algébrique (suites A/B entières + 4 Digamma) ne
         reconstruit aucun premier → seconde tentative via l'approche
         géométrique (termes hypoténuse sqrt(a²+b²)).
"""

import re
from typing import Dict, Any, List, Optional, Union
from src.core.metaphore_geometrique import MetaphoreGeometriqueGenerator, Point3D
from src.core.suites_geometriques_AB import (
    PipelineSuitesGeometriques,
    ResultatSuiteGeo,
)
from src.core.fallback_geometrique import (
    GestionnaireFallbackGeometrique,
    ResultatReconstruction,
    TypeApproche,
)

class GabrielGeometricResponseWrapper:
    """
    Wrapper pour ajouter métaphores géométriques aux réponses de Gabriel.

    Intègre également le pipeline des suites géométriques A et B
    et le gestionnaire de fallback géométrique (v7.4).
    """

    def __init__(self, k_typique: Union[int, float] = 2, verbose: bool = False):
        self.geo_gen = MetaphoreGeometriqueGenerator()
        self.response_history = []

        # ── NOUVEAU v7.4 : Pipeline suites géométriques A et B ──────────
        self.k_typique = k_typique
        self.pipeline_geo = PipelineSuitesGeometriques(k_typique=k_typique)

        # ── NOUVEAU v7.4 : Gestionnaire de fallback géométrique ──────────
        self.fallback_gestionnaire = GestionnaireFallbackGeometrique(
            k=k_typique, verbose=verbose
        )
        self.verbose = verbose
    
    def enrichir_reponse(self, 
                        reponse_originale: str,
                        contexte: Optional[Dict[str, Any]] = None) -> str:
        """
        Ajoute bloc géométrique à une réponse
        
        Args:
            reponse_originale: Réponse de Gabriel (texte/code/HOL)
            contexte: Info sur le type de requête (convergence, spectral, etc.)
        
        Returns:
            Réponse enrichie avec bloc géométrique
        """
        
        output = reponse_originale
        
        # Détecter le type de réponse automatiquement
        contexte_detecte = self._detecter_contexte(reponse_originale)
        
        # Générer bloc géométrique approprié
        bloc_geo = self._generer_bloc_geometrique(contexte_detecte or contexte)
        
        # Ajouter le bloc
        if bloc_geo:
            output += "\n" + bloc_geo
        
        return output
    
    def _detecter_contexte(self, texte: str) -> Optional[Dict[str, Any]]:
        """Détecte automatiquement le type de réponse"""
        
        texte_lower = texte.lower()
        
        # Détection: Convergence
        if any(kw in texte_lower for kw in ["convergence", "converge", "converger", "tend vers", "asymptote"]):
            # Extraire les valeurs numériques
            values = re.findall(r'0\.\d+', texte)
            if values:
                try:
                    values_float = [float(v) for v in values[:10]]  # Prendre les 10 premiers
                    return {
                        'type': 'convergence',
                        'values': values_float,
                        'target': 0.5
                    }
                except:
                    pass
        
        # Détection: Rapport spectral
        if any(kw in texte_lower for kw in ["rapport spectral", "1/2", "1/3", "1/4", "spectre"]):
            return {'type': 'spectral', 'ratios': {'1/2': 0.5, '1/3': 0.333, '1/4': 0.25}}
        
        # Détection: Comparaison asymétrique
        if any(kw in texte_lower for kw in ["comparaison asymétrique", "bloc A", "bloc B", "asymétrique ordonnée"]):
            return {
                'type': 'asym_ordonnee',
                'bloc_a': [2, 3, 5, 7],
                'bloc_b': [11, 13, 17, 19, 23],
                'ratio': 0.5026
            }
        
        return None
    
    def _generer_bloc_geometrique(self, contexte: Optional[Dict]) -> Optional[str]:
        """Génère bloc géométrique selon contexte"""
        
        if not contexte:
            return None
        
        contexte_type = contexte.get('type')
        
        if contexte_type == 'convergence':
            values = contexte.get('values', [0.8, 0.65, 0.55, 0.52, 0.501])
            target = contexte.get('target', 0.5)
            return self.geo_gen.generer_pour_convergence(
                values, 
                target=target,
                title="Convergence Analysée"
            )
        
        elif contexte_type == 'spectral':
            ratios = contexte.get('ratios', {'1/2': 0.5})
            return self.geo_gen.generer_pour_rapport_spectral(
                ratios,
                title="Spectre Analyisé"
            )
        
        elif contexte_type == 'asym_ordonnee':
            bloc_a = contexte.get('bloc_a', [2, 3, 5, 7])
            bloc_b = contexte.get('bloc_b', [11, 13, 17, 19, 23])
            ratio = contexte.get('ratio', 0.5026)
            return self.geo_gen.generer_pour_bloc_asymetrique(
                bloc_a, 
                bloc_b, 
                ratio
            )
        
        return None
    
    # ================================================================
    # NOUVEAU v7.4 — SUITES GÉOMÉTRIQUES A ET B
    # ================================================================

    def calculer_suites_AB(
        self,
        k: Union[int, float, None] = None
    ) -> ResultatSuiteGeo:
        """
        Calcule les sommes des suites géométriques A et B pour t = 1/k.

        Si k est None, utilise le rapport typique k_typique (défaut 2).
        Supporte les rapports typiques (k=2) et non typiques (k≠2).

        Retourne un ResultatSuiteGeo avec :
          .somme_A   : somme de la suite A
          .somme_B   : somme de la suite B
          .termes_A  : liste des 10 termes hypoténuse de A
          .termes_B  : liste des 10 termes hypoténuse de B
        """
        k_eff = k if k is not None else self.k_typique
        return self.pipeline_geo.calcul_pour_rapport(k_eff)

    def convolution_suites_AB(
        self,
        n_max: int = 10,
        k: Union[int, float, None] = None
    ) -> Dict[str, List[float]]:
        """
        Calcule la convolution discrète A⊗B sur n_max termes.
        Retourne dict avec 'sommes_A', 'sommes_B', 'convolution', 'ratios_AB'.
        """
        k_eff = k if k is not None else self.k_typique
        return self.pipeline_geo.convolution_AB(n_max=n_max, k=k_eff)

    # ================================================================
    # NOUVEAU v7.4 — FALLBACK GÉOMÉTRIQUE
    # ================================================================

    def reconstruire_avec_fallback(
        self,
        n: int,
        fn_algebrique,
        k: Union[int, float, None] = None,
    ) -> ResultatReconstruction:
        """
        Tente la reconstruction des premiers pour la valeur n.

        LOGIQUE :
          1. Appelle fn_algebrique(n) — approche existante (suites entières + Digamma).
          2. Si aucun premier trouvé → FALLBACK GÉOMÉTRIQUE automatique.
             Relance via les suites A et B modèle géométrique (termes hypoténuse).

        Paramètres
        ----------
        n : int
            Valeur de n à reconstruire.
        fn_algebrique : Callable[[int], List[int]]
            Fonction de reconstruction algébrique existante.
            Doit retourner List[int] (vide si échec Digamma).
        k : int, float ou None
            Rapport t = 1/k. Si None, utilise k_typique.

        Retourne
        --------
        ResultatReconstruction avec .premiers_finals et .approche_finale.
        """
        k_eff = k if k is not None else self.k_typique
        return self.fallback_gestionnaire.reconstruire(
            n=n,
            fn_algebrique=fn_algebrique,
            k_override=k_eff,
        )

    def reconstruire_batch_avec_fallback(
        self,
        n_values: List[int],
        fn_algebrique,
        k: Union[int, float, None] = None,
    ) -> Dict[int, ResultatReconstruction]:
        """
        Applique le double mécanisme (algébrique + fallback géo)
        pour une liste complète de valeurs de n.
        Couvre l'ensemble des valeurs de n demandées.
        """
        k_eff = k if k is not None else self.k_typique
        return self.fallback_gestionnaire.reconstruire_batch(
            n_values=n_values,
            fn_algebrique=fn_algebrique,
            k_override=k_eff,
        )

    def rapport_fallback_session(self) -> str:
        """Retourne le rapport de session du gestionnaire de fallback."""
        return self.fallback_gestionnaire.rapport_session()

    # ================================================================
    # STRUCTURE EXPORTABLE (MÉTHODE EXISTANTE — INCHANGÉE)
    # ================================================================

    def creer_structure_exportable(self,
                                  reponse: str,
                                  contexte: Dict) -> Dict[str, Any]:
        """
        Crée structure exportable vers CAO/modélisation
        
        Retourne format exploitable par FreeCAD, Blender, OpenSCAD
        """
        
        export = {
            'texte': reponse,
            'geometrie': [],
            'points_3d': [],
            'matrices': [],
            'instructions_cad': []
        }
        
        # Extraire points 3D
        points_3d = re.findall(
            r'\([-\d.]+,\s*[-\d.]+,\s*[-\d.]+\)',
            reponse
        )
        
        for pt_str in points_3d:
            coords = re.findall(r'[-\d.]+', pt_str)
            if len(coords) == 3:
                pt = Point3D(float(coords[0]), float(coords[1]), float(coords[2]))
                export['points_3d'].append(pt.to_tuple())
        
        # Générer instructions CAO
        if contexte.get('type') == 'convergence':
            export['instructions_cad'].append("""
# FreeCAD Script
import FreeCAD as App
import Part

# Créer points de convergence
points = """ + str(export['points_3d']) + """

# Créer polyline
pl = Part.makePolygon(points)
App.ActiveDocument.addObject("Part::Feature", "ConvergencePath").Shape = pl
""")
        
        return export

# ========================================================================
# INTÉGRATION DANS GABRIEL
# ========================================================================

def enrichir_reponse_gabriel(reponse: str, contexte: Optional[Dict] = None) -> str:
    """
    Fonction à appeler dans le pipeline multiloop de Gabriel
    
    Exemple d'utilisation dans integrateur_memoire.py:
    
        response = await llm_router.route_request(question)
        
        # Enrichir avec métaphores géométriques
        response_enrichie = enrichir_reponse_gabriel(response, contexte)
        
        return response_enrichie
    """
    
    wrapper = GabrielGeometricResponseWrapper()
    return wrapper.enrichir_reponse(reponse, contexte)

# ========================================================================
# TEST
# ========================================================================

if __name__ == "__main__":
    wrapper = GabrielGeometricResponseWrapper()
    
    # Test 1: Enrichir une réponse sur convergence
    print("\n[TEST] Enrichissement d'une réponse sur convergence:\n")
    reponse_test = """
    Le ratio converge vers 1/2:
    - k=1: 0.625
    - k=2: 0.552
    - k=3: 0.501
    - k=4: 0.5001
    """
    
    reponse_enrichie = wrapper.enrichir_reponse(reponse_test)
    print(reponse_enrichie)
    
    # Test 2: Créer export CAO
    print("\n[TEST] Export CAO:\n")
    export = wrapper.creer_structure_exportable(
        reponse_enrichie,
        {'type': 'convergence'}
    )
    
    print("Points 3D extraits:")
    for pt in export['points_3d']:
        print(f"  {pt}")
    
    print("\nInstructions CAO:")
    for instr in export['instructions_cad']:
        print(instr[:200] + "...")
