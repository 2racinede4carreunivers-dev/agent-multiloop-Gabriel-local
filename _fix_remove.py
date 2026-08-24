# -*- coding: utf-8 -*-
"""Retire le bloc corrompu (3 méthodes insérées dans _verifier_syntaxe)."""
from pathlib import Path

p = Path(r"c:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local\orchestrator_main.py")
t = p.read_text(encoding="utf-8")

s = "\n    #  TRANSMISSION : l'orchestrateur interroge l'archiviste"
i = t.find(s)
assert i != -1, "debut bloc introuvable"
e = t.find('            return ""', i)
assert e != -1, "fin bloc introuvable"
t2 = t[: i + 1] + t[e:]
p.write_text(t2, encoding="utf-8")
print("OK retiré, delta:", i - e)