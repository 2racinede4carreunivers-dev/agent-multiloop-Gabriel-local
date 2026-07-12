# Manuel Isabelle: alias court + mode sans echec

## Objectif
Eviter les erreurs de ROOT en compilant toujours depuis le bon dossier theories.

Dossier de build valide:
- /cygdrive/c/agent-multiloop-Gabriel-local-final/agent-multiloop-Gabriel-local/theories

## Option A (recommandee): alias ibuildms dans terminal Isabelle

1. Ouvrir ton terminal Isabelle/Cygwin.
2. Ajouter cet alias dans ~/.bashrc:

```bash
echo "alias ibuildms='bash /cygdrive/c/agent-multiloop-Gabriel-local-final/agent-multiloop-Gabriel-local/theories/ibuildms.sh'" >> ~/.bashrc
source ~/.bashrc
```

3. Lancer la compilation:

```bash
ibuildms
```

## Option B: lanceur Windows direct

Depuis PowerShell ou CMD, execute:

```bat
C:\agent-multiloop-Gabriel-local-final\ibuildms.bat
```

## Mode sans echec (checklist)

1. Verifier le dossier courant (terminal Isabelle):

```bash
pwd
```

2. Verifier qu on cible le bon ROOT:

```bash
ls /cygdrive/c/agent-multiloop-Gabriel-local-final/agent-multiloop-Gabriel-local/theories/ROOT
```

3. Build force sur le bon dossier, peu importe le dossier courant:

```bash
isabelle build -D /cygdrive/c/agent-multiloop-Gabriel-local-final/agent-multiloop-Gabriel-local/theories
```

4. Si erreur inattendue, nettoyer la session puis relancer:

```bash
isabelle build -c -D /cygdrive/c/agent-multiloop-Gabriel-local-final/agent-multiloop-Gabriel-local/theories
isabelle build -D /cygdrive/c/agent-multiloop-Gabriel-local-final/agent-multiloop-Gabriel-local/theories
```

5. Diagnostic rapide des erreurs ROOT (si besoin):

```bash
sed -n '1,80p' /cygdrive/c/agent-multiloop-Gabriel-local-final/agent-multiloop-Gabriel-local/theories/ROOT
```

## Signes que tu es dans le mauvais dossier

- La sortie mentionne /cygdrive/c/Users/HP 3/Isabelle2025-2/ROOT
- Erreurs sur Securite_Spectrale.thy ou Attestation_Logs.thy
- Erreur sur document/root.tex

Dans ce cas, ne pas utiliser `isabelle build -D .` depuis ~/Isabelle2025-2.
Utiliser `ibuildms` ou la commande avec chemin absolu ci-dessus.
