# 🧮 Gabriel v2.0 - Assistant Mathématique Multiloop avec Moteur Spectral

Amélioration complète de Gabriel pour spécialisation en **géométrie spectrale des nombres premiers** et **hypothèse de Riemann**.

## 🎯 Nouveautés v2.0

### ✨ Modules ajoutés

| Module | Fonction | Fichier |
|--------|----------|---------|
| **Mathematical Engine** | Calculs symboliques & numériques | `src/mathematical_engine.py` |
| **HOL4/Lean4 Interface** | Vérification formelle | `src/hol_lean_interface.py` |
| **PDF RAG Processor** | Extraction & indexation PDF | `src/pdf_rag_processor.py` |
| **Gabriel Integration** | Point d'entrée mathématique | `gabriel_mathematical.py` |
| **FastAPI Routes** | Exposition API | `integration_mathematical.py` |

### 🔧 Capacités nouvelles

- ✅ **Calcul zéros Riemann** avec haute précision (256+ bits)
- ✅ **Analyse écarts spectraux** (gaps, distribution GUE)
- ✅ **Spectre nombres premiers** (densité, géométrie)
- ✅ **Vérification formelle** (HOL4 + Lean4)
- ✅ **Contexte PDF automatique** (RAG from analyse_hypothese_riemann_savard.pdf)
- ✅ **Intégration SymPy + PARI/GP + Wolfram Engine**

## 📦 Installation rapide

### 1. Dépendances Python

```bash
cd agent-multiloop-Gabriel-local
pip install -r requirements.txt
```

### 2. Configuration (optionnel mais recommandé)

Éditer `config_mathematical.env` pour chemins locaux HOL4/Lean4

### 3. Valider installation

```bash
python gabriel_mathematical.py
```

## 🚀 Utilisation basique

### Via Python

```python
from gabriel_mathematical import get_gabriel, MathematicalAssistantContext

gabriel = get_gabriel()

# Requête
ctx = MathematicalAssistantContext(
    query="Calcule les 100 premiers zéros de Riemann",
    use_pdf_context=True,  # Injecte PDF contexte
    require_proof=False
)

result = gabriel.process_spectral_query(ctx)
print(result['explanation'])
```

### Via API FastAPI

```bash
POST /api/mathematical/query
{
    "query": "Analyse les gaps spectraux",
    "require_proof": true,
    "use_pdf_context": true
}
```

## 📁 Structure fichiers

```
agent-multiloop-Gabriel-local/
├── src/
│   ├── mathematical_engine.py       ← Moteur principal
│   ├── hol_lean_interface.py        ← Vérification formelle
│   ├── pdf_rag_processor.py         ← Traitement PDF
│   └── __init__.py
├── theories/
│   ├── riemann_spectral.thy         ← HOL4 Riemann
│   ├── RiemannSpectral.lean         ← Lean4 Riemann
│   └── *.thy (existants)
├── pdf/
│   └── analyse_hypothese_riemann_savard.pdf   ← PDF Riemann (déjà placé ✓)
├── data/
│   └── pdf_index.json               ← Index RAG généré
├── gabriel_mathematical.py          ← Assistant mathématique
├── integration_mathematical.py      ← Routes FastAPI + wrapper
├── config_mathematical.env          ← Configuration
├── requirements.txt                 ← Dépendances
└── SETUP_MATHEMATICAL_v2.md        ← Documentation complète
```

## 🎓 Cas d'usage

### 1️⃣ Théorie "L'univers est au carré"

Gabriel peut désormais:
- Référencer votre corpus théorique (499 pages + 5 chapitres)
- Vérifier formellement propositions via HOL4/Lean4
- Générer code preuves assistées
- Analyser géométrie spectrale chapitre

### 2️⃣ Recherche en géométrie spectrale

```python
# Analyser zéros Riemann
ctx = MathematicalAssistantContext(
    query="Que dit l'analyse_hypothese_riemann_savard.pdf sur les gaps spectraux?",
    use_pdf_context=True,
    require_proof=True
)
```

### 3️⃣ Vérification formelle

```python
# Générer preuve HOL4
ctx = MathematicalAssistantContext(
    query="Prouve le lien Hilbert-Polya",
    require_proof=True
)
```

## 📊 Fichiers PDF & contexte

### ✅ PDF inclus: `analyse_hypothese_riemann_savard.pdf`

Localisation: `pdf/analyse_hypothese_riemann_savard.pdf`

Traitement automatique:
- ✓ Parsing des sections (auto-exclusion sections HOL)
- ✓ Indexation mots-clés & topics
- ✓ Injection contexte pour requêtes pertinentes
- ✓ Recherche sémantique (RAG)

Exemple injection:

```
Requête: "Expliquez la géométrie du spectre"
→ Recherche PDF → Top 3 sections pertinentes
→ Injection contexte → Gabriel répond avec références PDF
```

## 🔍 Détails modules clés

### mathematical_engine.py

```python
MathematicalEngine(precision_bits=256)
├── compute_riemann_zeros(count=100, precision_digits=50)
├── compute_spectral_gap(zero_indices)
├── compute_prime_spectrum(max_prime=1000)
├── simplify_expression(expr_str)
└── pari_gp_command(gp_code)  # Si disponible
```

### hol_lean_interface.py

```python
FormalVerificationPipeline()
├── hol.verify_theorem(name, statement, proof)
├── lean.verify_theorem(name, statement, proof)
└── verify_multi_engine(...)  # Consensus HOL4 + Lean4
```

### pdf_rag_processor.py

```python
processor = PDFRAGProcessor(pdf_path)
├── parse_sections()           # Charge sections
├── search(query, top_k=3)     # Recherche pertinence
└── generate_context_prompt()  # Contexte injection
```

## ⚙️ Configuration avancée

### Précision mathématique

```bash
MATH_PRECISION_BITS=1024     # Pour très haute précision
RIEMANN_ZEROS_COUNT=10000    # Plus de zéros pré-calculés
```

### Vérification formelle

```bash
HOL4_ENABLED=true
LEAN4_ENABLED=true
HOL_VERIFICATION_TIMEOUT=120  # Secondes
```

### PDF RAG

```bash
PDF_EXTRACTION_METHOD=pypdf2  # ou pdfplumber, text_fallback
RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 🧪 Tests validation

```bash
# Test complet
python gabriel_mathematical.py

# Test individual
python src/mathematical_engine.py     # Calculs
python src/hol_lean_interface.py      # Vérification formelle
python src/pdf_rag_processor.py       # PDF/RAG
```

## 📚 Prochaines étapes

1. **Installation HOL4/Lean4** (optionnel mais recommandé)
   - Voir `SETUP_MATHEMATICAL_v2.md`

2. **Configuration `config_mathematical.env`**
   - Adapter chemins à votre système

3. **Tests validation**
   - Exécuter 3 tests pour vérifier

4. **Intégration au `main.py` existant**
   - Voir `integration_mathematical.py`

5. **Usage requêtes mathématiques**
   - Via Python ou API FastAPI

## 🐛 Troubleshooting

| Erreur | Cause | Solution |
|--------|-------|----------|
| "HOL4 non disponible" | HOL4 non installé | Installer ou utiliser Lean4 seul |
| "PDF non trouvé" | Mauvais chemin | Vérifier `pdf/analyse_hypothese_riemann_savard.pdf` |
| "PyPDF2 not found" | Dépendance manquante | `pip install PyPDF2` |
| Performance lente | Trop de zéros | Réduire `RIEMANN_ZEROS_COUNT` |

## 📖 Documentation complète

Voir: **`SETUP_MATHEMATICAL_v2.md`** pour guide installation détaillé

## 🔗 Ressources

- **SymPy docs**: https://docs.sympy.org/
- **HOL4 github**: https://github.com/HOL-Theorem-Prover/HOL
- **Lean4 docs**: https://lean-lang.org/
- **PARI/GP**: https://pari.math.u-bordeaux.fr/
- **Wolfram Engine**: https://www.wolfram.com/engine/

## 🎓 Exemple workflow complet

```python
from gabriel_mathematical import get_gabriel, MathematicalAssistantContext

# 1. Initialiser
gabriel = get_gabriel()

# 2. Requête mathématique avec contexte PDF
ctx = MathematicalAssistantContext(
    query="D'après analyse_hypothese_riemann_savard.pdf, quelle est la géométrie des gaps spectraux?",
    use_pdf_context=True,  # Injection PDF automatique
    require_proof=True     # Génère preuve HOL4/Lean4
)

# 3. Traiter
result = gabriel.process_spectral_query(ctx)

# 4. Résultat complet
print(result['explanation'])              # Explication narrative
print(result['mathematical_result'].result)  # Données brutes
print(result['formal_proof'])             # Certificat preuve
print(result['pdf_context'])              # Sections PDF injectées
```

## ✅ Checklist déploiement

- [ ] `pip install -r requirements.txt`
- [ ] PDF en place: `pdf/analyse_hypothese_riemann_savard.pdf` ✓
- [ ] Tester: `python gabriel_mathematical.py`
- [ ] Adapter `config_mathematical.env` (optionnel)
- [ ] Intégrer à `main.py` (voir `integration_mathematical.py`)
- [ ] Tests API si utilisation FastAPI
- [ ] Documentation théorie personnelle intégrée

---

**Version**: 2.0.0  
**Date**: 2024  
**Auteur**: Gabriel Mathematical Engine Team  
**Status**: ✅ Production Ready
