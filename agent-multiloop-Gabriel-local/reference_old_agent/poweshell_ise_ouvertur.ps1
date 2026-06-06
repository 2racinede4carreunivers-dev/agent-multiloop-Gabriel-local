# =============================================================================
#  poweshell_ise_ouvertur.ps1  |  Auteur : Philippe  |  Version : 4.0
#  Mode : LLM AGENT COMPLET  (PhilippeLLM + Maths + GitHub + Automatisation)
# =============================================================================

#region ── CONFIGURATION ──────────────────────────────────────────────────────
$AgentMode      = "multiloop"   # valeur initiale, peut etre surchargee au demarrage
$WorkspaceRoot  = "C:\agent-local-ia-carre"
$ProjectRoot    = "C:\agent-local-ia-carre\local_ai_agent"
$DockerfilePath = "C:\agent-local-ia-carre\local_ai_agent\Dockerfile.cli"
$BuildContext   = "C:\agent-local-ia-carre\local_ai_agent"
$ImageName      = "llm-agent"
$ContainerName  = "llm-agent-run"
$IsabellePath   = "/opt/Isabelle2025-2"
$IsabelleHeap   = "HOL"
$AgentScript    = "math-agent-cli.py"
$AgentWorkdir   = "/home/agent/app"
$EnvFile        = "C:\agent-local-ia-carre\.env"
$GitHubReposRoot = "C:\agent-local-ia-carre\GitHub"
$ModeLabel      = "LLM Complet (PhilippeLLM + Maths + GitHub)"

$GitHubRepos = @(
    @{ Name = "Theorie-mathematique-philippe-thomas-savard-2026"; Url = "https://github.com/2racinede4carreunivers-dev/Theorie-mathematique-philippe-thomas-savard-2026.git"; RequiresAuth = $false },
    @{ Name = "formation_evolutive_savard"; Url = "https://github.com/2racinede4carreunivers-dev/formation_evolutive_savard.git"; RequiresAuth = $false },
    @{ Name = "agent-local-ia-carre"; Url = "https://github.com/2racinede4carreunivers-dev/agent-local-ia-carre.git"; RequiresAuth = $true }
)

$Mounts = @()
$C_OK="Green"; $C_WARN="Yellow"; $C_ERR="Red"; $C_INFO="Cyan"

# Repertoires sources Python a monter (pour live-reload sans rebuild)
$SrcMounts = @()

if ($AgentMode -eq "multiloop") {
    $ProjectRoot    = Join-Path $WorkspaceRoot "agent-multiloop-local"
    $DockerfilePath = Join-Path $ProjectRoot "Dockerfile.cli"
    $BuildContext   = $ProjectRoot
    $ImageName      = "llm-agent-multiloop"
    $ContainerName  = "llm-agent-multiloop-run"
    $AgentScript    = "src/main.py"
    $ModeLabel      = "Multi-Loop (Docker + HOL + Ollama/OpenAI + GitHub)"

    $candidateEnv = Join-Path $ProjectRoot ".env"
    if (Test-Path $candidateEnv) {
        $EnvFile = $candidateEnv
    }

    $Mounts = @(
        @{ Host = Join-Path $WorkspaceRoot "local_ai_agent\corpus_actions" ; Container = "/workspace/corpus_actions" },
        @{ Host = Join-Path $WorkspaceRoot "local_ai_agent"                 ; Container = "/home/agent/local_ai_agent" },
        @{ Host = Join-Path $WorkspaceRoot "local_ai_agent\corpus_actions\hol" ; Container = "/workspace/hol"       },
        @{ Host = Join-Path $WorkspaceRoot "local_ai_agent\corpus_actions\pdf" ; Container = "/workspace/pdf"       },
        @{ Host = Join-Path $WorkspaceRoot "local_ai_agent\corpus_actions\tex" ; Container = "/workspace/tex"       },
        @{ Host = Join-Path $ProjectRoot "data"                                  ; Container = "/home/agent/app/data" },
        @{ Host = Join-Path $ProjectRoot "logs"                                  ; Container = "/home/agent/app/logs" },
        @{ Host = $GitHubReposRoot                                                 ; Container = "/home/agent/app/GitHub" }
    )

    $SrcMounts = @(
        @{ Host = Join-Path $ProjectRoot "src"              ; Container = "/home/agent/app/src" },
        @{ Host = Join-Path $ProjectRoot "config"           ; Container = "/home/agent/app/config" },
        @{ Host = Join-Path $ProjectRoot "requirements.txt" ; Container = "/home/agent/app/requirements.txt" }
    )
} else {
    $Mounts = @(
        @{ Host = Join-Path $ProjectRoot "corpus_actions" ; Container = "/workspace/corpus_actions" },
        @{ Host = Join-Path $ProjectRoot "corpus_actions\hol" ; Container = "/workspace/hol"       },
        @{ Host = Join-Path $ProjectRoot "corpus_actions\pdf" ; Container = "/workspace/pdf"       },
        @{ Host = Join-Path $ProjectRoot "corpus_actions\tex" ; Container = "/workspace/tex"       },
        @{ Host = Join-Path $ProjectRoot "data"               ; Container = "/home/agent/app/data" },
        @{ Host = Join-Path $ProjectRoot "logs"               ; Container = "/home/agent/app/logs" },
        @{ Host = $GitHubReposRoot                              ; Container = "/home/agent/app/GitHub" }
    )

    $SrcMounts = @(
        @{ Host = Join-Path $ProjectRoot "src"              ; Container = "/home/agent/app/src"    },
        @{ Host = Join-Path $ProjectRoot "config.yaml"      ; Container = "/home/agent/app/config.yaml" },
        @{ Host = Join-Path $ProjectRoot "math-agent-cli.py"; Container = "/home/agent/app/math-agent-cli.py" }
    )
}
#endregion

#region ── FONCTIONS ─────────────────────────────────────────────────────────
function Write-Step { param([string]$M) Write-Host "`n>  $M" -ForegroundColor $C_INFO }
function Write-OK   { param([string]$M) Write-Host "   OK  $M" -ForegroundColor $C_OK }
function Write-Warn { param([string]$M) Write-Host "   !!  $M" -ForegroundColor $C_WARN }
function Write-Err  { param([string]$M) Write-Host "   XX  $M" -ForegroundColor $C_ERR }

function Ensure-Directory {
    param([string]$Path,[string]$Label)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Warn "Cree : $Path ($Label)"
    } else { Write-OK "Trouve : $Path ($Label)" }
}

function ConvertTo-DockerPath {
    param([string]$WinPath)

    # Remplacer les backslashes par des slashes
    $p = $WinPath -replace '\\','/'

    # Convertir C:\... en /host_mnt/c/...
    if ($p -match '^([A-Za-z]):') {
        $drive = $matches[1].ToLower()
        $p = "/host_mnt/$drive" + $p.Substring(2)
    }

    return $p
}


function Get-EnvValueFromFile {
    param(
        [string]$Path,
        [string]$Name
    )

    if (-not (Test-Path $Path)) { return $null }

    foreach ($line in Get-Content -Path $Path -ErrorAction SilentlyContinue) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith('#')) { continue }
        if ($trimmed -match "^$([regex]::Escape($Name))\s*=\s*(.*)$") {
            $value = $matches[1].Trim()
            if (($value.StartsWith('"') -and $value.EndsWith('"')) -or
                ($value.StartsWith("'") -and $value.EndsWith("'"))) {
                $value = $value.Substring(1, $value.Length - 2)
            }
            return $value
        }
    }

    return $null
}

function Get-AuthenticatedGitUrl {
    param(
        [string]$RepoUrl,
        [string]$Username,
        [string]$Token
    )

    if ([string]::IsNullOrWhiteSpace($RepoUrl) -or
        [string]::IsNullOrWhiteSpace($Username) -or
        [string]::IsNullOrWhiteSpace($Token)) {
        return $RepoUrl
    }

    if (-not $RepoUrl.StartsWith("https://")) {
        return $RepoUrl
    }

    $escapedUser = [uri]::EscapeDataString($Username)
    $escapedToken = [uri]::EscapeDataString($Token)
    return "https://$escapedUser`:$escapedToken@$($RepoUrl.Substring(8))"
}

function Ensure-GitHubRepositories {
    param(
        [string]$Root,
        [array]$Repos,
        [string]$Token,
        [string]$Username
    )

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Err "Git introuvable dans le PATH. Impossible de preparer les depots."
        exit 1
    }

    Ensure-Directory -Path $Root -Label "GitHub repositories"

    foreach ($repo in $Repos) {
        $repoName = $repo.Name
        $repoUrl = $repo.Url
        $requiresAuth = [bool]($repo.RequiresAuth)
        $repoPath = Join-Path $Root $repoName
        $authAvailable = -not [string]::IsNullOrWhiteSpace($Token) -and $Token -notlike '*PASTE_YOUR_GITHUB_FINE_GRAINED_TOKEN_HERE*'
        $authUrl = Get-AuthenticatedGitUrl -RepoUrl $repoUrl -Username $Username -Token $Token

        if ($requiresAuth -and -not $authAvailable) {
            Write-Warn "Depot prive ignore (token absent): $repoName"
            continue
        }

        if (Test-Path (Join-Path $repoPath ".git")) {
            Write-Step "Mise a jour du depot $repoName"
            try {
                & git -C $repoPath pull --ff-only 2>&1 | ForEach-Object { Write-Host $_ }
                if ($LASTEXITCODE -ne 0 -and $authAvailable -and -not [string]::IsNullOrWhiteSpace($authUrl)) {
                    Write-Warn "Pull standard en echec, nouvelle tentative authentifiee pour $repoName"
                    & git -C $repoPath pull --ff-only $authUrl 2>&1 | ForEach-Object { Write-Host $_ }
                }
                if ($LASTEXITCODE -eq 0) {
                    Write-OK "Depot a jour : $repoName"
                } else {
                    Write-Warn "Pull non termine pour $repoName"
                }
            } catch {
                Write-Warn "Echec de pull pour $repoName : $($_.Exception.Message)"
            }
        } else {
            Write-Step "Clone du depot $repoName"
            try {
                if ($authAvailable -and -not [string]::IsNullOrWhiteSpace($authUrl)) {
                    & git clone $authUrl $repoPath 2>&1 | ForEach-Object { Write-Host $_ }
                    if ($LASTEXITCODE -ne 0 -and -not $requiresAuth) {
                        Write-Warn "Clone authentifie en echec, tentative publique pour $repoName"
                        & git clone $repoUrl $repoPath 2>&1 | ForEach-Object { Write-Host $_ }
                    }
                } else {
                    & git clone $repoUrl $repoPath 2>&1 | ForEach-Object { Write-Host $_ }
                }
                if ($LASTEXITCODE -eq 0) {
                    Write-OK "Depot clone : $repoName"
                } else {
                    Write-Err "Clone echoue : $repoName"
                    exit 1
                }
            } catch {
                Write-Err "Clone impossible pour $repoName : $($_.Exception.Message)"
                exit 1
            }
        }
    }
}
#endregion

#region ── BANNER ────────────────────────────────────────────────────────────
Clear-Host
Write-Host @"

  +===========================================================+
  |     AGENT LLM - Philippe  |  Lanceur automatique  v4.0   |
  |   Mode : LLM Complet  (PhilippeLLM + Maths + GitHub)     |
  +===========================================================+

"@ -ForegroundColor Magenta

# Choix interactif du mode (defaut: multiloop)
Write-Host ""
Write-Host "Choisissez le mode de lancement:" -ForegroundColor Cyan
Write-Host "  [1] Multi-loop (defaut)" -ForegroundColor Cyan
Write-Host "  [2] Local" -ForegroundColor Cyan
$modeChoice = Read-Host "Votre choix (1/2, Entree=1)"
switch ($modeChoice.Trim()) {
    "2" { $AgentMode = "local" }
    "local" { $AgentMode = "local" }
    "l" { $AgentMode = "local" }
    default { $AgentMode = "multiloop" }
}

# Recalculer la configuration en fonction du choix effectif
if ($AgentMode -eq "multiloop") {
    $ProjectRoot    = Join-Path $WorkspaceRoot "agent-multiloop-local"
    $DockerfilePath = Join-Path $ProjectRoot "Dockerfile.cli"
    $BuildContext   = $ProjectRoot
    $ImageName      = "llm-agent-multiloop"
    $ContainerName  = "llm-agent-multiloop-run"
    $AgentScript    = "src/main.py"
    $ModeLabel      = "Multi-Loop (Docker + HOL + Ollama/OpenAI + GitHub)"

    # .env partagé : chercher dans local_ai_agent (docker-compose y accède) en priorité
    $candidateEnvLocalAI = Join-Path $WorkspaceRoot "local_ai_agent\.env"
    $candidateEnvRoot  = Join-Path $WorkspaceRoot ".env"
    if (Test-Path $candidateEnvLocalAI) {
        $EnvFile = $candidateEnvLocalAI
    } elseif (Test-Path $candidateEnvRoot) {
        $EnvFile = $candidateEnvRoot
    } else {
        $EnvFile = $candidateEnvLocalAI
    }


    $Mounts = @(
        @{ Host = Join-Path $WorkspaceRoot "local_ai_agent\corpus_actions" ; Container = "/workspace/corpus_actions" },
        @{ Host = Join-Path $WorkspaceRoot "local_ai_agent"                 ; Container = "/home/agent/local_ai_agent" },
        @{ Host = Join-Path $WorkspaceRoot "local_ai_agent\corpus_actions\hol" ; Container = "/workspace/hol"       },
        @{ Host = Join-Path $WorkspaceRoot "local_ai_agent\corpus_actions\pdf" ; Container = "/workspace/pdf"       },
        @{ Host = Join-Path $WorkspaceRoot "local_ai_agent\corpus_actions\tex" ; Container = "/workspace/tex"       },
        @{ Host = Join-Path $ProjectRoot "data"                                  ; Container = "/home/agent/app/data" },
        @{ Host = Join-Path $ProjectRoot "logs"                                  ; Container = "/home/agent/app/logs" },
        @{ Host = $GitHubReposRoot                                                 ; Container = "/home/agent/app/GitHub" }
    )

    $SrcMounts = @(
        @{ Host = Join-Path $ProjectRoot "src"              ; Container = "/home/agent/app/src" },
        @{ Host = Join-Path $ProjectRoot "config"           ; Container = "/home/agent/app/config" },
        @{ Host = Join-Path $ProjectRoot "requirements.txt" ; Container = "/home/agent/app/requirements.txt" }
    )
} else {
    $ProjectRoot    = "C:\agent-local-ia-carre\local_ai_agent"
    $DockerfilePath = "C:\agent-local-ia-carre\local_ai_agent\Dockerfile.cli"
    $BuildContext   = "C:\agent-local-ia-carre\local_ai_agent"
    $ImageName      = "llm-agent"
    $ContainerName  = "llm-agent-run"
    $AgentScript    = "math-agent-cli.py"
    $ModeLabel      = "LLM Complet (PhilippeLLM + Maths + GitHub)"

       # .env partagé : chercher dans local_ai_agent (docker-compose y accède) en priorité
    $candidateEnvLocalAI = Join-Path $WorkspaceRoot "local_ai_agent\.env"
    $candidateEnvRoot  = Join-Path $WorkspaceRoot ".env"
    if (Test-Path $candidateEnvLocalAI) {
        $EnvFile = $candidateEnvLocalAI
    } elseif (Test-Path $candidateEnvRoot) {
        $EnvFile = $candidateEnvRoot
    } else {
        $EnvFile = $candidateEnvLocalAI
    }

    $Mounts = @(
        @{ Host = Join-Path $ProjectRoot "corpus_actions\hol" ; Container = "/workspace/hol"       },
        @{ Host = Join-Path $ProjectRoot "corpus_actions\pdf" ; Container = "/workspace/pdf"       },
        @{ Host = Join-Path $ProjectRoot "corpus_actions\tex" ; Container = "/workspace/tex"       },
        @{ Host = Join-Path $ProjectRoot "data"               ; Container = "/home/agent/app/data" },
        @{ Host = Join-Path $ProjectRoot "logs"               ; Container = "/home/agent/app/logs" },
        @{ Host = $GitHubReposRoot                              ; Container = "/home/agent/app/GitHub" }
    )

    $SrcMounts = @(
        @{ Host = Join-Path $ProjectRoot "src"              ; Container = "/home/agent/app/src"    },
        @{ Host = Join-Path $ProjectRoot "config.yaml"      ; Container = "/home/agent/app/config.yaml" },
        @{ Host = Join-Path $ProjectRoot "math-agent-cli.py"; Container = "/home/agent/app/math-agent-cli.py" }
    )
}

Write-OK "Mode selectionne : $AgentMode"
Write-OK "Profil          : $ModeLabel"
#endregion

#region ── ETAPE 1 ───────────────────────────────────────────────────────────
Write-Step "Verification des dossiers"
foreach ($m in $Mounts) { Ensure-Directory -Path $m.Host -Label $m.Container }

$githubToken = Get-EnvValueFromFile -Path $EnvFile -Name 'GITHUB_TOKEN'
$githubUser = Get-EnvValueFromFile -Path $EnvFile -Name 'GITHUB_USERNAME'
Ensure-GitHubRepositories -Root $GitHubReposRoot -Repos $GitHubRepos -Token $githubToken -Username $githubUser
#endregion

#region ── ETAPE 2 : Docker Desktop ──────────────────────────────────────────
Write-Step "Demarrage de Docker Desktop"
$dockerDesktopExe = "$Env:ProgramFiles\Docker\Docker\Docker Desktop.exe"
$dockerRunning = $false
try { docker info 2>&1 | Out-Null; if ($LASTEXITCODE -eq 0) { $dockerRunning=$true } } catch {}

if ($dockerRunning) {
    Write-OK "Docker deja actif."
} else {
    if (Test-Path $dockerDesktopExe) {
        Start-Process $dockerDesktopExe
        Write-Warn "Attente du daemon..."
        $maxWait=90; $elapsed=0; $interval=5
        while ($elapsed -lt $maxWait) {
            Start-Sleep -Seconds $interval; $elapsed+=$interval
            try { docker info 2>&1 | Out-Null; if ($LASTEXITCODE -eq 0){$dockerRunning=$true;break} } catch {}
            Write-Host "   ... $elapsed/$maxWait s" -ForegroundColor DarkGray
        }
        if (-not $dockerRunning) { Write-Err "Docker non demarre."; exit 1 }
        Write-OK "Docker actif apres ${elapsed}s."
    } else { Write-Err "Docker Desktop introuvable."; exit 1 }
}
#endregion

#region ── ETAPE 3 : Dockerfile ──────────────────────────────────────────────
Write-Step "Verification du Dockerfile"
if (-not (Test-Path $DockerfilePath)) {
    Write-Err "Introuvable : $DockerfilePath"
    Get-ChildItem -Path $ProjectRoot -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "(?i)^dockerfile" } |
        ForEach-Object { Write-Host "     -> $($_.FullName)" -ForegroundColor Yellow }
    exit 1
}
Write-OK "Dockerfile    : $DockerfilePath"
Write-OK "Build context : $BuildContext"
#endregion

#region ── ETAPE 4 : Build ───────────────────────────────────────────────────
Write-Step "Build de l'image  [$ImageName]"
docker build --tag $ImageName --file $DockerfilePath $BuildContext 2>&1 |
    ForEach-Object { Write-Host $_ }
if ($LASTEXITCODE -ne 0) { Write-Err "Echec du build."; exit 1 }
Write-OK "Image '$ImageName' prete."
#endregion

#region ── ETAPE 5 : Nettoyage ───────────────────────────────────────────────
Write-Step "Nettoyage conteneur  [$ContainerName]"
$existing = docker ps -aq --filter "name=^${ContainerName}$"
if ($existing) { docker rm --force $ContainerName | Out-Null; Write-OK "Supprime." }
else { Write-OK "Rien a supprimer." }
#endregion

#region ── ETAPE 6 : Volumes ─────────────────────────────────────────────────
Write-Step "Preparation des volumes"
$mountArgs = @()
foreach ($m in ($Mounts + $SrcMounts)) {
    if (Test-Path $m.Host) {
        $hp = ConvertTo-DockerPath $m.Host
        $mountArgs += "--volume"; $mountArgs += "${hp}:$($m.Container)"
        Write-OK "$($m.Host)  ->  $($m.Container)"
    } else {
        Write-Warn "Absent (skip): $($m.Host)"
    }
}
#endregion

#region ── ETAPE 7 : Script de demarrage (LF Unix) ───────────────────────────
Write-Step "Creation du script de demarrage"

$innerBashCmd = @'
#!/bin/bash
set -e

# ── Environnement Isabelle ─────────────────────────────────────────────────
export PATH=##ISABELLE_PATH##/bin:$PATH
export ISABELLE_HOME=##ISABELLE_PATH##

# ── Corpus ─────────────────────────────────────────────────────────────────
export CORPUS_ACTIONS=/workspace/corpus_actions
export HOL_DIR=/workspace/corpus_actions/hol
export PDF_DIR=/workspace/corpus_actions/pdf
export TEX_DIR=/workspace/corpus_actions/tex

# ── Ollama : pointer vers le host Windows depuis Docker Desktop ─────────────
# (host.docker.internal resout l automatiquement sur Docker Desktop Windows/Mac)
if [ -z "$OLLAMA_HOST" ]; then
  export OLLAMA_HOST=http://host.docker.internal:11434
fi

echo '+============================================================+'
echo '|  AGENT LLM - Philippe  |  Mode LLM Complet  v4.0         |'
echo '+============================================================+'
echo "   Python    : $(python3 --version 2>&1)"
echo "   Workdir   : ##AGENT_WORKDIR##"
echo "   OLLAMA    : $OLLAMA_HOST"
echo "   OpenAI    : ${OPENAI_API_KEY:0:8}... (si definie)"
echo '+------------------------------------------------------------+'
ls /workspace/corpus_actions 2>/dev/null && echo "   /workspace/corpus_actions : OK" || echo "   /workspace/corpus_actions : absent"
ls /workspace/corpus_actions/hol 2>/dev/null && echo "   /workspace/corpus_actions/hol : OK" || echo "   /workspace/corpus_actions/hol : absent"
ls /workspace/corpus_actions/pdf 2>/dev/null && echo "   /workspace/corpus_actions/pdf : OK" || echo "   /workspace/corpus_actions/pdf : absent"
ls /workspace/corpus_actions/tex 2>/dev/null && echo "   /workspace/corpus_actions/tex : OK" || echo "   /workspace/corpus_actions/tex : absent"
echo '+============================================================+'
echo ''
echo '   Demarrage de l agent LLM...'
echo ''

cd ##AGENT_WORKDIR##
##AGENT_RUNNER_BLOCK##

echo ''
echo '[Agent arrete -- Entree pour fermer]'
read
'@

$AgentRunnerBlock = @'
python3 -c "
import sys
sys.path.insert(0, '##AGENT_WORKDIR##/src')
import runpy
runpy.run_path('##AGENT_WORKDIR##/##AGENT_SCRIPT##', run_name='__main__')
"
'@

if ($AgentMode -eq "multiloop") {
                $AgentRunnerBlock = @'
# Bootstrap: installer dependances et preparer index/QA si present
echo '== Bootstrap: verifs et installations =='
if [ -f "/home/agent/app/requirements.txt" ]; then
    echo 'Installing Python requirements from /home/agent/app/requirements.txt'
    python3 -m pip install --upgrade pip setuptools wheel || true
    python3 -m pip install --no-cache-dir -r /home/agent/app/requirements.txt || true
fi
if [ -f "/home/agent/app/requirements-cli.txt" ]; then
    echo 'Installing CLI requirements from /home/agent/app/requirements-cli.txt'
    python3 -m pip install --no-cache-dir -r /home/agent/app/requirements-cli.txt || true
fi
# Build semantic index if helper exists
if [ -f "/home/agent/app/scripts/build_semantic_index.py" ]; then
    echo 'Building semantic index...'
    python3 /home/agent/app/scripts/build_semantic_index.py || true
fi
# Import QA bank if helper exists
if [ -f "/home/agent/app/scripts/import_qa_bank.py" ]; then
    echo 'Importing QA bank...'
    python3 /home/agent/app/scripts/import_qa_bank.py || true
fi

while true; do
        echo -n "Entrez votre objectif multi-loop (vide pour quitter): "
        read GOAL
        if [ -z "$GOAL" ]; then
                break
        fi
        python3 -m src.main --goal "$GOAL"
        echo ""
done
'@
}

$innerBashCmd = $innerBashCmd.Replace('##ISABELLE_PATH##', $IsabellePath)
$innerBashCmd = $innerBashCmd.Replace('##AGENT_WORKDIR##', $AgentWorkdir)
$innerBashCmd = $innerBashCmd.Replace('##AGENT_SCRIPT##',  $AgentScript)
$innerBashCmd = $innerBashCmd.Replace('##AGENT_RUNNER_BLOCK##', $AgentRunnerBlock)

$innerBashCmdLF   = $innerBashCmd -replace "`r`n","`n" -replace "`r","`n"
$tempScriptWin    = Join-Path $env:TEMP "llm-agent-start.sh"
$tempScriptDocker = ConvertTo-DockerPath $tempScriptWin
[System.IO.File]::WriteAllText($tempScriptWin,$innerBashCmdLF,(New-Object System.Text.UTF8Encoding $false))
Write-OK "Script : $tempScriptWin"
#endregion

#region ── ETAPE 8 : docker run ──────────────────────────────────────────────
Write-Step "Preparation docker run (mode LLM)"

# Env vars de base — Ollama accessible depuis le conteneur
$envArgs = @(
    "--env", "OLLAMA_HOST=http://host.docker.internal:11434",
    "--env", "ISABELLE_HOME=$IsabellePath",
    "--env", "ISABELLE_HEAP=$IsabelleHeap",
    "--env", "WORK_DIRECTORY=/home/agent/app"
)

# Charger le fichier .env si present (cles API, GitHub, etc.)
if (Test-Path $EnvFile) {
    # Utiliser le chemin Windows directement (Docker Desktop le résout)
    $envArgs += "--env-file"; $envArgs += $EnvFile
    Write-OK ".env charge     : $EnvFile"
} else {
    Write-Warn ".env absent     : $EnvFile  (variables API non chargees)"
    Write-Host "   -> Copiez .env.example en .env et remplissez vos cles." -ForegroundColor Yellow
}

$dockerRunArgs = @(
    "run","--interactive","--tty",
    "--name",$ContainerName,"--rm",
    "--add-host","host.docker.internal:host-gateway"
) + $mountArgs + $envArgs + @(
    "--volume","${tempScriptDocker}:/tmp/llm-agent-start.sh",
    $ImageName,
    "bash","/tmp/llm-agent-start.sh"
)
$argsQ = $dockerRunArgs | ForEach-Object { "`"$($_ -replace '"','\"')`"" }
$fullDockerCmd = "& docker " + ($argsQ -join ' ')
Write-OK "Commande prete."
#endregion

#region ── ETAPE 9 : Terminal ────────────────────────────────────────────────
Write-Step "Ouverture du terminal"
$newTerminalScript = @"
Write-Host ''
Write-Host '  AGENT LLM  -  Philippe  |  Terminal actif' -ForegroundColor Magenta
Write-Host '  Conteneur : $ContainerName'                -ForegroundColor Cyan
Write-Host '  Mode      : $ModeLabel'                    -ForegroundColor Cyan
Write-Host ''
$fullDockerCmd
"@
$encoded = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($newTerminalScript))
$wt = Get-Command "wt.exe" -ErrorAction SilentlyContinue
if ($wt) {
    Write-OK "Ouverture dans Windows Terminal..."
    Start-Process "wt.exe" -ArgumentList "powershell -NoExit -EncodedCommand $encoded"
} else {
    Write-Warn "wt.exe absent - ouverture dans PowerShell."
    Start-Process "powershell" -ArgumentList "-NoExit -EncodedCommand $encoded"
}
Write-OK "Terminal lance. Bonne session!"
#endregion

#region ── RESUME ────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "==================================================" -ForegroundColor Magenta
Write-Host "  AGENT LLM - Philippe  |  Demarre avec succes"    -ForegroundColor Green
Write-Host "     Mode      : $ModeLabel"                 -ForegroundColor Cyan
Write-Host "     Dockerfile: $DockerfilePath"                  -ForegroundColor Cyan
Write-Host "     Agent     : $AgentWorkdir/$AgentScript"       -ForegroundColor Cyan
Write-Host "     Env file  : $EnvFile"                         -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Magenta
Write-Host ""
#endregion
