# -*- coding: utf-8 -*-
"""Vérifie la présence du marqueur de test puis le rollback."""
from pathlib import Path

marque = "MARQUEUR_TEST_VARIATEUR_SOIT_RESTAUREE"
repo = Path(r"c:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local")
cibles = [
    "src/spectral/tchebychev_savard_pipeline.py",
    "src/core/spectral_core.py",
    "src/core/pipeline_with_gap_detection.py",
]
print("=== Présence du marqueur (avant rollback) ===")
for rel in cibles:
    p = repo / rel
    t = p.read_text(encoding="utf-8") if p.exists() else ""
    print(f"  {rel}: {'OUI' if marque in t else 'non'}")