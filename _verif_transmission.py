# -*- coding: utf-8 -*-
"""Vérification : combien de fichiers la transmission résout-t-elle ?"""
import sys
from pathlib import Path
sys.path.insert(0, r"c:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local")

from archiviste import ArchivisteCorrection

repo = Path(r"c:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local")
a = ArchivisteCorrection(repo / "data" / "gabriel_repo_map.db", repo)

for mots, role, prof in [(["spectral"], "core", 1), (["spectral", "reconstruction"], "core", 1), (["ratio"], None, 1)]:
    res = a.reseau_de_correction(mots, role=role, profondeur=prof)
    print(f"mots={mots} role={role} prof={prof} -> {len(res)} adresses")
    for r in res[:5]:
        print("   ", r["rel_path"], r.get("type"))
    print()

# Détail du réseau pour le contrat de test
res = a.reseau_de_correction(["spectral", "reconstruction"], role="core", profondeur=1)
print("=== Cibles du contrat de test ===")
for r in res:
    print("  ", r["rel_path"], f"({r.get('type')})")