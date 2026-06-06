# agent-multiloop-Gabriel-local

Projet d'agent IA multiloop — assistant mathématique et HOL/Isabelle.

## Objectif

Ce workspace sert à :
1. Charger et analyser le code de l'agent multiloop local existant de Gabriel
2. Concevoir un **nouvel agent** qui reprendra certaines sections du précédent
3. Améliorer l'architecture multiloop pour l'assistance mathématique et la preuve formelle (HOL/Isabelle)

## Structure du projet

```
agent-multiloop-Gabriel-local/
├── src/                      # Code du nouvel agent (à construire)
├── reference_old_agent/      # Code de l'agent actuel de Gabriel (à charger ici)
├── docs/                     # Documentation, notes d'analyse, architecture
├── examples/                 # Exemples d'utilisation, prompts, cas de test mathématiques
├── tests/                    # Tests unitaires et d'intégration
└── README.md                 # Ce fichier
```

## Workflow

### Phase 1 — Chargement de l'agent existant
- [ ] Charger le code source dans `reference_old_agent/`
- [ ] Documenter les modules principaux dans `docs/`

### Phase 2 — Analyse
- [ ] Analyser l'architecture multiloop existante
- [ ] Identifier les sections à conserver / refactoriser / supprimer
- [ ] Lister les améliorations possibles

### Phase 3 — Conception du nouvel agent
- [ ] Définir l'architecture cible
- [ ] Réutiliser les sections pertinentes de l'ancien agent
- [ ] Implémenter dans `src/`

### Phase 4 — Tests & validation
- [ ] Tests unitaires
- [ ] Tests d'intégration avec HOL/Isabelle
- [ ] Cas d'usage mathématiques

## Notes
Le code de l'agent actuel est volumineux et sera chargé progressivement,
en plusieurs étapes / requêtes.
