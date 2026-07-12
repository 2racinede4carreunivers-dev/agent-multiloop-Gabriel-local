# Guide: Trace en direct des etapes Gabriel

## But
Afficher dans le terminal un suivi vivant des etapes de traitement pendant une question:
- analyse
- strategie
- calcul spectral
- tours multiloop
- scores candidats

Ce mode montre un resume operationnel en temps reel.

## Ce qui est affiche
- Etape en cours (abstraction, calcul, multiloop, finalisation)
- Tour multiloop i/N
- Score de chaque candidat
- Meilleur score du tour
- Arret anticipe si le seuil est atteint

## Mode cinematique (nouveau)
Le mode cinematique ajoute une couche visuelle supplementaire:
- Barre de progression pipeline
- Barre de progression multiloop
- Timer global + timer de l'etape courante
- Jauge de confiance coloree (rouge/jaune/vert)

Le mode cinematique est actif par defaut si la trace live est active.

## Activation (par defaut)
Le mode est actif par defaut.

Dans le panneau d'accueil, la ligne affiche:
- Trace live : ON

## Desactivation
Pour masquer la trace et revenir a l'affichage minimal:

### Cygwin / Bash
```bash
export GABRIEL_LIVE_TRACE=0
python main.py
```

### PowerShell
```powershell
$env:GABRIEL_LIVE_TRACE = "0"
python main.py
```

## Desactivation du mode cinematique uniquement

### Cygwin / Bash
```bash
export GABRIEL_CINEMATIC=0
python main.py
```

### PowerShell
```powershell
$env:GABRIEL_CINEMATIC = "0"
python main.py
```

## Reactivation
### Cygwin / Bash
```bash
export GABRIEL_LIVE_TRACE=1
export GABRIEL_CINEMATIC=1
python main.py
```

### PowerShell
```powershell
$env:GABRIEL_LIVE_TRACE = "1"
$env:GABRIEL_CINEMATIC = "1"
python main.py
```

## Conseils d'usage
1. Garder ON pour les demonstrations et le debug.
2. Mettre OFF pour une sortie plus epuree.
3. Si tu veux plus de details techniques en plus de la trace, active aussi:
   - GABRIEL_VERBOSE=1

## Depannage rapide
Si la trace ne s'affiche pas:
1. Verifier que tu lances bien l'interface CLI (main.py).
2. Verifier la variable d'environnement:
   - Bash: echo $GABRIEL_LIVE_TRACE
   - PowerShell: echo $env:GABRIEL_LIVE_TRACE
3. Verifier aussi le mode cinematique:
   - Bash: echo $GABRIEL_CINEMATIC
   - PowerShell: echo $env:GABRIEL_CINEMATIC
4. Mettre explicitement GABRIEL_LIVE_TRACE=1 puis relancer.
