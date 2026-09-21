# TODO — Pipeline Cognitif Gabriel / Système Convolutif Spectral

## Étape 1 — Analyse du fichier Excel (70% fait)
- [x] Lire le générateur du fichier Excel (generate_excel_convolutif_general.py lu)
- [x] Extraire la structure des niveaux 1 et 2 depuis le générateur
- [x] Formaliser : suites A/B niveau 1, Digamma 4 possibilités, décision ancrage, suites A/B niveau 2
- [ ] Lire le contenu effectif de l'Excel via openpyxl (pour vérifier onglets « Parametres », « Validation HOL Générale », etc.)
- [ ] Compléter le résumé technique structuré des niveaux 1 et 2 avec Excel

## Étape 2 — Analyse du pipeline cognitif de l'agent Gabriel
- [x] Explorer et lister les fichiers du pipeline cognitif (multiloop/, cognitive/, spectral/)
- [x] Identifier la gestion des rapports typiques 1/k = 1/2 vs non typiques 1/k <> 1/2
- [x] Analyser spectral_core.py, rapports_non_typiques.py, __init__.py
- [ ] Produire le schéma textuel du pipeline actuel (entrée requête → détermination rapport 1/k → choix niveau 1/2 → sortie réponse Gabriel)

## Étape 3 — Mise à jour du pipeline cognitif
- [ ] Adapter la chaîne de réponse Gabriel pour appliquer systématiquement les niveaux 1 et 2 du système convolutif Excel
- [ ] Ajouter la mention explicite des ancrages de premiers (ou leur absence) dans chaque réponse
- [ ] Gérer les rapports typiques 1/2 ET les rapports non typiques 1/k <> 1/2 via le système convolutif

## Étape 4 — Intégration dans l'agent Gabriel
- [ ] Modifier le code du pipeline pour appeler la logique niveaux 1 et 2 basée sur le fichier Excel
- [ ] Formater les réponses de Mme Gabriel selon la structure demandée (3 cas : niveau 1 trouve premier, seul niveau 2 trouve, aucun niveau ne trouve)
- [ ] Documenter dans le code (commentaires) :
  - Où le système convolutif est appliqué
  - Comment les rapports typiques et non typiques sont gérés
- [ ] Proposer un exemple de réponse type de Mme Gabriel pour :
  - Un cas où le niveau 1 trouve un premier
  - Un cas où seul le niveau 2 trouve un premier
  - Un cas où aucun niveau ne trouve de premier

