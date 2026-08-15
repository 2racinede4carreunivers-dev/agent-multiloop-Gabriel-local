"""
Gabriel Vision Integration - Intégrateur principal
===================================================

Intègre les modules de vision et d'accès aux images dans Gabriel Multi-Loop.
Permet au agent de:
  1. Accéder aux images depuis n'importe où (chemin, URL, réseau)
  2. Analyser les images (points, lignes, formes)
  3. Valider les figures géométriques
  4. Générer du code paramétrique (Python, LaTeX, HOL)
  5. Générer des rapports d'analyse

Utilisation:
    image_analyzer = GabrielVisionIntegration()
    
    # Analyser une image
    result = image_analyzer.analyze_image(
        "C:/path/to/image.png"
        or "https://example.com/image.png"
    )
    
    if result.success:
        print(result.report)
        print(result.python_code)
        print(result.hol_code)

Auteur: Gabriel Multi-Loop Agent
Date: 2026
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import traceback

from image_access_manager import (
    ImageAccessManager,
    ImageSource,
    access_image,
    get_image_access_manager,
)
from vision_module import (
    ImageVisionAnalyzer,
    Point,
    Line,
    Shape,
)

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Résultat complet d'une analyse d'image"""
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    image_path: Optional[str] = None
    source: Optional[ImageSource] = None
    
    # Analyses
    points_detected: int = 0
    lines_detected: int = 0
    shapes_detected: int = 0
    
    # Validation
    is_valid: bool = False
    consistency_score: float = 0.0
    validation_errors: list[str] = field(default_factory=list)
    validation_warnings: list[str] = field(default_factory=list)
    
    # Générations
    report: str = ""
    python_code: str = ""
    latex_code: str = ""
    hol_code: str = ""
    
    # Métadonnées
    analysis_duration_ms: float = 0.0
    error_message: Optional[str] = None
    traceback_info: Optional[str] = None
    
    coordinates: Dict[str, Any] = field(default_factory=dict)


class GabrielVisionIntegration:
    """
    Intégrateur de vision pour Gabriel Multi-Loop Agent
    Point d'entrée principal pour l'analyse d'images
    """
    
    def __init__(self, 
                 cache_dir: Optional[Path | str] = None,
                 auto_generate_code: bool = True):
        """
        Initialise l'intégrateur de vision
        
        Args:
            cache_dir: Répertoire de cache personnalisé
            auto_generate_code: Générer automatiquement le code après analyse
        """
        self.access_manager = get_image_access_manager(cache_dir=cache_dir)
        self.auto_generate_code = auto_generate_code
        self.last_analysis: Optional[AnalysisResult] = None
        
        logger.info("GabrielVisionIntegration initialisé")
    
    def analyze_image(self, image_path: str, 
                     generate_code: bool = True,
                     detect_points: bool = True,
                     detect_lines: bool = True,
                     detect_shapes: bool = True) -> AnalysisResult:
        """
        Analyse complète d'une image
        
        Args:
            image_path: Chemin, URL, ou adresse réseau de l'image
            generate_code: Générer le code paramétrique
            detect_points: Détecter les points
            detect_lines: Détecter les lignes
            detect_shapes: Détecter les formes
        
        Returns:
            AnalysisResult avec tous les résultats
        """
        import time
        start_time = time.time()
        
        result = AnalysisResult(
            success=False,
            image_path=image_path,
        )
        
        try:
            logger.info(f"Début analyse: {image_path}")
            
            # ÉTAPE 1: Accéder à l'image
            logger.debug("Étape 1: Accès à l'image")
            source = self.access_image(image_path)
            
            if source is None:
                result.error_message = f"Impossible d'accéder à l'image: {image_path}"
                logger.error(result.error_message)
                return result
            
            result.source = source
            
            # ÉTAPE 2: Charger et analyser l'image
            logger.debug("Étape 2: Analyse vision")
            analyzer = ImageVisionAnalyzer(source.resolved_path)
            
            # Détections
            if detect_points:
                analyzer.detect_points()
                result.points_detected = len(analyzer.points)
                logger.debug(f"Points détectés: {result.points_detected}")
            
            if detect_lines:
                analyzer.detect_lines()
                result.lines_detected = len(analyzer.lines)
                logger.debug(f"Lignes détectées: {result.lines_detected}")
            
            if detect_shapes:
                analyzer.detect_shapes()
                result.shapes_detected = len(analyzer.shapes)
                logger.debug(f"Formes détectées: {result.shapes_detected}")
            
            # ÉTAPE 3: Validation
            logger.debug("Étape 3: Validation")
            validation = analyzer.validate_figure()
            result.is_valid = validation['valid']
            result.consistency_score = validation['consistency_score']
            result.validation_errors = validation['errors']
            result.validation_warnings = validation['warnings']
            
            # ÉTAPE 4: Génération du rapport
            logger.debug("Étape 4: Rapport")
            result.report = analyzer.analyze_and_report()
            
            # ÉTAPE 5: Extraction des coordonnées
            logger.debug("Étape 5: Extraction coordonnées")
            result.coordinates = analyzer.extract_coordinates()
            
            # ÉTAPE 6: Génération du code (si demandé)
            if generate_code and analyzer.shapes:
                logger.debug("Étape 6: Génération code")
                try:
                    result.python_code = analyzer.generate_python_code(0)
                    result.latex_code = analyzer.generate_latex_code(0)
                    result.hol_code = analyzer.generate_hol_code(0)
                except Exception as e:
                    logger.warning(f"Erreur génération code: {e}")
            
            result.success = True
            logger.info("Analyse complétée avec succès")
        
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse: {e}")
            result.error_message = str(e)
            result.traceback_info = traceback.format_exc()
        
        finally:
            result.analysis_duration_ms = (time.time() - start_time) * 1000
            self.last_analysis = result
        
        return result
    
    def access_image(self, image_path: str) -> Optional[ImageSource]:
        """
        Accès universel à une image
        
        Args:
            image_path: Chemin/URL/adresse réseau
        
        Returns:
            ImageSource accessible ou None
        """
        return self.access_manager.access_image(image_path)
    
    def add_search_root(self, root: Path | str) -> None:
        """Ajoute une racine de recherche pour les chemins relatifs"""
        self.access_manager.add_search_root(root)
        logger.info(f"Racine de recherche ajoutée: {root}")
    
    def validate_points_with_figure(self, 
                                   image_path: str,
                                   points: list[tuple[float, float]]) -> Dict[str, Any]:
        """
        Valide que les points donnés correspondent à la figure
        
        Args:
            image_path: Chemin de l'image
            points: Liste de tuples (x, y)
        
        Returns:
            Résultat de validation
        """
        source = self.access_image(image_path)
        if source is None:
            return {'valid': False, 'error': 'Image non accessible'}
        
        try:
            analyzer = ImageVisionAnalyzer(source.resolved_path)
            analyzer.detect_shapes()
            
            result = {
                'valid': True,
                'provided_points': len(points),
                'detected_shapes': len(analyzer.shapes),
                'checks': [],
            }
            
            # Créer des Point objects
            provided_points = [
                Point(x, y, type=None) 
                for x, y in points
            ]
            
            # Vérifier chaque forme
            for shape in analyzer.shapes:
                check = {
                    'shape_type': shape.type,
                    'shape_points': len(shape.points),
                    'coherent': True,
                    'issues': [],
                }
                
                # Vérifier que les points fournis sont proches des points détectés
                for provided_pt in provided_points:
                    min_dist = min(
                        provided_pt.distance_to(detected_pt)
                        for detected_pt in shape.points
                    )
                    
                    if min_dist > 10:  # Tolérance de 10 pixels
                        check['coherent'] = False
                        check['issues'].append(
                            f"Point ({provided_pt.x}, {provided_pt.y}) "
                            f"éloigné de {min_dist:.1f}px de la forme"
                        )
                
                result['checks'].append(check)
                if not check['coherent']:
                    result['valid'] = False
            
            return result
        
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def generate_parametric_code(self, image_path: str,
                                language: str = 'python') -> str:
        """
        Génère du code paramétrique pour une image
        
        Args:
            image_path: Chemin de l'image
            language: 'python', 'latex', 'hol'
        
        Returns:
            Code généré
        """
        result = self.analyze_image(image_path)
        
        if not result.success:
            return f"# Erreur: {result.error_message}"
        
        if language == 'python':
            return result.python_code
        elif language == 'latex':
            return result.latex_code
        elif language == 'hol':
            return result.hol_code
        else:
            return f"# Langage non supporté: {language}"
    
    def get_analysis_summary(self) -> str:
        """Résumé de la dernière analyse"""
        if self.last_analysis is None:
            return "Aucune analyse réalisée"
        
        r = self.last_analysis
        
        summary = f"""
╭────────────────────────────────────────────────────────────────╮
│           RÉSUMÉ DERNIÈRE ANALYSE - GABRIEL VISION            │
╰────────────────────────────────────────────────────────────────╯

✓ Succès: {'Oui' if r.success else 'Non'}
📁 Image: {r.image_path}
⏱️  Durée: {r.analysis_duration_ms:.1f}ms

📊 DÉTECTIONS
   Points: {r.points_detected}
   Lignes: {r.lines_detected}
   Formes: {r.shapes_detected}

✅ VALIDATION
   Valide: {'Oui' if r.is_valid else 'Non'}
   Score cohérence: {r.consistency_score:.1%}
   Erreurs: {len(r.validation_errors)}
   Avertissements: {len(r.validation_warnings)}

📍 COORDONNÉES DÉTECTÉES
   Points: {len(r.coordinates.get('points', []))}
   Lignes: {len(r.coordinates.get('lines', []))}
   Formes: {len(r.coordinates.get('shapes', []))}

💾 CODE GÉNÉRÉ
   Python: {'✓' if r.python_code else '✗'}
   LaTeX: {'✓' if r.latex_code else '✗'}
   HOL: {'✓' if r.hol_code else '✗'}
"""
        
        if r.error_message:
            summary += f"\n⚠️  ERREUR: {r.error_message}"
        
        return summary
    
    def list_accessible_images(self) -> list[str]:
        """Liste les images actuellement en cache"""
        cached = self.access_manager.list_cached_images()
        return [str(path) for path, _, _ in cached]
    
    def cache_stats(self) -> Dict[str, Any]:
        """Statistiques du cache"""
        return self.access_manager.get_cache_stats()
    
    def clear_cache(self, older_than_hours: int = 24) -> int:
        """Nettoie le cache"""
        return self.access_manager.clear_cache(older_than_hours)


# Singleton global
_vision_integration: Optional[GabrielVisionIntegration] = None


def get_vision_integration(cache_dir: Optional[Path | str] = None) -> GabrielVisionIntegration:
    """Obtient ou crée l'intégrateur de vision"""
    global _vision_integration
    
    if _vision_integration is None:
        _vision_integration = GabrielVisionIntegration(cache_dir=cache_dir)
    
    return _vision_integration


# Fonction de commodité
def analyze_image(image_path: str) -> AnalysisResult:
    """Analyse rapide d'une image"""
    integration = get_vision_integration()
    return integration.analyze_image(image_path)


if __name__ == '__main__':
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     Gabriel Vision Integration - Démonstration            ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Initialiser
    vision = GabrielVisionIntegration()
    
    print("Intégrateur de vision Gabriel initialisé!")
    print("Utilisez analyze_image(chemin) pour analyser une image.\n")
    
    # Exemple d'utilisation (à décommenter si image disponible)
    # result = vision.analyze_image("path/to/image.png")
    # if result.success:
    #     print(result.report)
    #     print(result.python_code)
    # else:
    #     print(f"Erreur: {result.error_message}")
