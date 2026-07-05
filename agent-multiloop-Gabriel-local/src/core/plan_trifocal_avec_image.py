#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amélioration du module Plan Trifocal - Intégration de l'image
"""

from pathlib import Path
from PIL import Image
from rich.console import Console
from rich.image import Image as RichImage

class PlanTrifocalAvecImage:
    """Plan Trifocal avec image intégrée"""
    
    # Chemin de l'image (DÉJÀ EXISTANTE)
    IMAGE_PATH = Path(r"C:\theorie-mathematique-philippe-thomas-savard-2026\src\tex\quadrature_parabole_zero_critique.png")
    
    def __init__(self):
        self.console = Console()
        self.image_disponible = self.IMAGE_PATH.exists()
    
    def afficher_image(self) -> None:
        """Affiche l'image du schéma"""
        if self.image_disponible:
            try:
                # Ouvrir et afficher l'image
                img = RichImage(str(self.IMAGE_PATH))
                self.console.print("\n[bold cyan]Schéma: Quadrature Parabole Zéro Critique[/bold cyan]\n")
                self.console.print(img)
                self.console.print("\n")
            except Exception as e:
                self.console.print(f"[yellow]Image non chargeable: {e}[/yellow]\n")
        else:
            self.console.print(f"[yellow]Image non trouvée à: {self.IMAGE_PATH}[/yellow]\n")
    
    def description_image(self) -> str:
        """Description de ce que l'image montre"""
        return """
[bold cyan]Schéma: Quadrature Parabole Zéro Critique[/bold cyan]

Ce schéma illustre:

1. [bold]Rectangle des zéros critiques[/bold]
   - Zone considérée (tronquée): T_tr
   - Zone restante: T_rest

2. [bold]Parabole formée par écarts mixtes[/bold]
   - Courbe créée par surdensité combinatoire
   - Suit la quadrature d'Archimède

3. [bold]Équilibre géométrique[/bold]
   - Aire parabole = (4/3) × aire triangle
   - Si Aire_parabole = T_rest → HR vraie

4. [bold]Géométrie épipolaire[/bold]
   - Lien entre 3 piliers (Zêta, Spectral, Équivalence)
   - Observe position des zéros critiques
"""


# Intégration dans les commandes
def handle_plan_trifocal_with_image(cmd: str) -> None:
    """Gestionnaire amélioré avec image"""
    
    plan = PlanTrifocalAvecImage()
    tokens = cmd.strip().split()
    
    if len(tokens) < 3:
        sub_cmd = "complete"
    else:
        sub_cmd = tokens[2].lower()
    
    if sub_cmd == "image":
        plan.afficher_image()
    elif sub_cmd == "schema":
        plan.console.print(plan.description_image())
        plan.afficher_image()
    elif sub_cmd == "complete":
        # Afficher tous les piliers + image
        plan.afficher_image()
        # ... puis afficher les 3 piliers
    else:
        plan.console.print("[yellow]Commande inconnue. Utilise: image, schema, ou complete[/yellow]")


if __name__ == "__main__":
    plan = PlanTrifocalAvecImage()
    plan.console.print("\n[bold]STATUS ACCÈS IMAGE:[/bold]")
    if plan.image_disponible:
        plan.console.print(f"✅ Image trouvée: {plan.IMAGE_PATH}")
        plan.afficher_image()
    else:
        plan.console.print(f"❌ Image NON trouvée: {plan.IMAGE_PATH}")
