#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch TEMPORAIRE de validation — marqueur inoffensif (sera restauré)."""
PATCH = {
    "meta": {"nom": "test_appliquer_restaurer", "description": "Validation écriture/rollback"},
    "mots_cles": ["spectral"],
    "role": "core",
    "profondeur": 1,
    "operation": {
        "op": "ajouter_a_la_fin",
        "contenu": "\n# === MARQUEUR_TEST_VARIATEUR_SOIT_RESTAUREE ===",
    },
}