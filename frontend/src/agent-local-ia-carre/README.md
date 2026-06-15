# Agent local IA Carre — Guide d'installation et d'exécution

Ce dépôt contient un agent local et une architecture "multiloop" pour exécuter plusieurs moteurs collaboratifs.

Ce README explique, pas à pas, comment lancer l'agent local et l'agent multiloop depuis le terminal (PowerShell sous Windows). Les commandes ci-dessous supposent que vous travaillez depuis la racine du dépôt :

```powershell
cd C:\agent-local-ia-carre
```

**Pré-requis**
- Git installé et configuré (clé SSH ou token HTTPS)
- Docker et Docker Compose installés
- Python 3.9+ et un virtualenv configuré (facultatif mais recommandé)

**1) Mettre à jour la fenêtre de l'Agent multiloop (rebuild sans cache)**

Pour forcer une reconstruction propre des images Docker et recréer les conteneurs sans utiliser le cache, exécutez depuis la racine du projet :

```powershell
# Reconstruire les images sans cache
docker-compose build --no-cache

# Recréer et démarrer les conteneurs en arrière-plan
docker-compose up -d --force-recreate
```

Ces commandes garantissent que les dernières sources sont utilisées et qu'aucun cache d'image ne fausse l'exécution.

Si vous voulez suivre les logs en direct dans la console (non détaché) :

```powershell
docker-compose up --build --force-recreate
```

**2) Démarrer les services (Docker Compose)**

Si vous n'avez pas encore lancé `docker-compose up`, faites-le (exemple pour la configuration principale) :

```powershell
docker-compose up -d
```

Vérifiez que le conteneur principal est en marche :

```powershell
docker ps --filter "name=llm-agent-multiloop"
```

Remplacez `llm-agent-multiloop` par le nom exact du conteneur si différent.

**3) Ouvrir un terminal dans le conteneur pour accéder au runtime**

Ouvrez un nouveau terminal local et entrez dans le conteneur principal (exemple) :

```powershell
docker exec -it llm-agent-multiloop-run bash
```

Une fois dans le conteneur, placez-vous dans le répertoire de l'agent local :

```bash
cd /workspace/local_ai_agent
# ou, si vous utilisez le dossier monté depuis Windows :
cd C:/agent-local-ia-carre/local_ai_agent
```

Sur l'hôte Windows (si vous préférez lancer depuis votre terminal local), naviguez vers :

```powershell
cd C:\agent-local-ia-carre\local_ai_agent
```

**4) Lancer l'agent local et le multiloop**

Vous pouvez lancer l'interface CLI principale depuis le répertoire `local_ai_agent` :

Terminal 1 (principal) :
```powershell
# Activez votre virtualenv si vous en avez un
. .venv\Scripts\Activate.ps1

python main_cli.py
```

Terminal 2 (optionnel, moteur multiloop) :
```powershell
python main.py
```

Selon la configuration, `main_cli.py` gère l'interface d'utilisation, et `main.py` exécute la boucle multiloop. Vous pouvez lancer les deux simultanément dans deux terminaux séparés.

**Conseils et dépannage**
- Si un import Python échoue, assurez-vous que la racine du dépôt est dans `PYTHONPATH` ou activez le virtualenv depuis la racine.
- Pour reconstruire uniquement une image spécifique :

```powershell
docker-compose build --no-cache <service_name>
docker-compose up -d --force-recreate <service_name>
```

- Pour afficher les logs d'un service particulier :

```powershell
docker-compose logs -f <service_name>
```

**Sécurité / accès GitHub privé**

Ce dépôt peut être privé. Pour cloner ou pousser vers GitHub, configurez soit :

- une clé SSH (préférée) : ajoutez la clé publique à GitHub et clonez avec `git@github.com:...` ;
- un token d'accès personnel (PAT) pour HTTPS : utilisez `https://<username>:<token>@github.com/...` ou configurez un credential manager.

Exemples de commandes Git :

```powershell
# Cloner un dépôt (HTTPS)
git clone https://github.com/2racinede4carreunivers-dev/agent-philippe-thomas-multiloop.git

# Ou, avec SSH
git clone git@github.com:2racinede4carreunivers-dev/agent-philippe-thomas-multiloop.git
```

Pour pousser vos sources locales vers ce remote (si le dépôt distant est vide ou si vous avez les droits) :

```powershell
git remote add origin https://github.com/2racinede4carreunivers-dev/agent-philippe-thomas-multiloop.git
git branch -M main
git add .
git commit -m "Initial commit: add local multiloop agent sources"
git push -u origin main
```

Si `git push` échoue à cause d'authentification, suivez la procédure indiquée plus haut (SSH ou PAT), puis réessayez.

---

Si vous voulez, je peux maintenant tenter de cloner le dépôt distant et effectuer une première poussée depuis cette machine (si vos credentials sont déjà configurés). Voulez-vous que j'essaie ?
