# =============================================================================
#  start-agent.ps1  |  Auteur : Gabriel  |  Version : 1.0
#  Multi-Loop Math Agent (Methode Spectrale Savard + Isabelle/HOL + Ollama/OpenAI)
#
#  Inspire de poweshell_ise_ouvertur.ps1 v4.0
#
#  Workflow :
#    1. Verifie Docker Desktop (le demarre si necessaire)
#    2. Build de l'image (--no-cache si -Rebuild)
#    3. Lance les services via docker-compose (ollama + isabelle + agent)
#    4. Ouvre un terminal PowerShell qui lance automatiquement le CLI multiloop
#
#  Usage :
#    .\start-agent.ps1                # build + up + ouverture du CLI
#    .\start-agent.ps1 -Rebuild       # rebuild --no-cache complet
#    .\start-agent.ps1 -Logs          # affiche les logs au lieu d'ouvrir le CLI
#    .\start-agent.ps1 -Stop          # arret de tous les services
#    .\start-agent.ps1 -Status        # affiche l'etat des conteneurs
# =============================================================================

param(
    [switch]$Rebuild,
    [switch]$Logs,
    [switch]$Stop,
    [switch]$Status,
    [switch]$NoOpen
)

# ============================================================================
# CONFIGURATION (adaptez ces chemins a votre installation locale)
# ============================================================================
$ProjectRoot   = $PSScriptRoot                       # dossier ou se trouve ce .ps1
$ProjectName   = "agent-multiloop-gabriel-local"
$ContainerName = "llm-agent-multiloop-run"
$ServiceMain   = "llm-agent-multiloop"
$EnvFile       = Join-Path $ProjectRoot ".env"
$EnvExample    = Join-Path $ProjectRoot ".env.example"
$EnvExampleAlt = Join-Path $ProjectRoot "env.example.txt"  # fallback si .env.example filtre par git
$TheoriesDir   = Join-Path $ProjectRoot "theories"
$DataDir       = Join-Path $ProjectRoot "data"
$LogsDir       = Join-Path $ProjectRoot "logs"
$ComposeFile   = Join-Path $ProjectRoot "docker-compose.yml"

# ============================================================================
# COULEURS
# ============================================================================
$C_OK = "Green"; $C_WARN = "Yellow"; $C_ERR = "Red"; $C_INFO = "Cyan"

function Write-Step { param([string]$M) Write-Host "`n>  $M" -ForegroundColor $C_INFO }
function Write-OK   { param([string]$M) Write-Host "   OK  $M" -ForegroundColor $C_OK }
function Write-Warn { param([string]$M) Write-Host "   !!  $M" -ForegroundColor $C_WARN }
function Write-Err  { param([string]$M) Write-Host "   XX  $M" -ForegroundColor $C_ERR }

function Ensure-Directory {
    param([string]$Path, [string]$Label)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Warn "Cree : $Path ($Label)"
    } else {
        Write-OK "Trouve : $Path ($Label)"
    }
}

# ============================================================================
# BANNER
# ============================================================================
Clear-Host
Write-Host @"

  +============================================================+
  |   MULTI-LOOP MATH AGENT  -  Gabriel Local Launcher  v1.0  |
  |   Methode Spectrale  *  Ollama / OpenAI  *  Isabelle/HOL  |
  +============================================================+

"@ -ForegroundColor Magenta

Write-OK "Project root : $ProjectRoot"

# ============================================================================
# ACTIONS RAPIDES (Stop / Status / Logs)
# ============================================================================
if ($Stop) {
    Write-Step "Arret des services docker-compose"
    docker compose -f $ComposeFile -p $ProjectName down
    Write-OK "Services arretes."
    exit 0
}

if ($Status) {
    Write-Step "Etat des conteneurs"
    docker compose -f $ComposeFile -p $ProjectName ps
    exit 0
}

if ($Logs) {
    Write-Step "Streaming des logs (Ctrl+C pour quitter)"
    docker compose -f $ComposeFile -p $ProjectName logs -f
    exit 0
}

# ============================================================================
# ETAPE 1 : Verifications structure de projet
# ============================================================================
Write-Step "Verification des dossiers"
Ensure-Directory -Path $TheoriesDir -Label "theories (.thy)"
Ensure-Directory -Path $DataDir     -Label "data"
Ensure-Directory -Path $LogsDir     -Label "logs"

if (-not (Test-Path $ComposeFile)) {
    Write-Err "docker-compose.yml introuvable : $ComposeFile"
    exit 1
}
Write-OK "docker-compose.yml present"

# ============================================================================
# ETAPE 2 : Verification du fichier .env
# ============================================================================
Write-Step "Verification du fichier .env"
if (-not (Test-Path $EnvFile)) {
    Write-Warn ".env absent."
    $source = $null
    if (Test-Path $EnvExample) {
        $source = $EnvExample
    } elseif (Test-Path $EnvExampleAlt) {
        $source = $EnvExampleAlt
        Write-Warn "Utilisation de env.example.txt (fallback)."
    }
    if ($source) {
        Copy-Item $source $EnvFile
        Write-OK ".env cree a partir de $source."
        Write-Warn "IMPORTANT : Editez $EnvFile et ajoutez vos cles (OPENAI_API_KEY, etc.) puis relancez."
        exit 1
    } else {
        Write-Err "Ni .env.example ni env.example.txt introuvables. Creez un .env manuellement."
        exit 1
    }
}

$openaiKey = Get-Content $EnvFile -ErrorAction SilentlyContinue | Where-Object { $_ -match "^OPENAI_API_KEY=(.+)" }
if (-not $openaiKey -or $openaiKey -match "VOTRE-CLE-OPENAI") {
    Write-Warn "OPENAI_API_KEY non configuree (fallback OpenAI desactive)."
    Write-Warn "L'agent utilisera Ollama uniquement."
} else {
    Write-OK ".env charge avec OPENAI_API_KEY configuree."
}

# ============================================================================
# ETAPE 3 : Demarrage de Docker Desktop
# ============================================================================
Write-Step "Verification de Docker Desktop"
$dockerRunning = $false
try { docker info 2>&1 | Out-Null; if ($LASTEXITCODE -eq 0) { $dockerRunning = $true } } catch {}

if ($dockerRunning) {
    Write-OK "Docker deja actif."
} else {
    $dockerDesktopExe = "$Env:ProgramFiles\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerDesktopExe) {
        Write-Warn "Docker non actif - demarrage de Docker Desktop..."
        Start-Process $dockerDesktopExe
        $maxWait = 120; $elapsed = 0; $interval = 5
        while ($elapsed -lt $maxWait) {
            Start-Sleep -Seconds $interval; $elapsed += $interval
            try { docker info 2>&1 | Out-Null; if ($LASTEXITCODE -eq 0) { $dockerRunning = $true; break } } catch {}
            Write-Host "   ... attente daemon  $elapsed / $maxWait s" -ForegroundColor DarkGray
        }
        if (-not $dockerRunning) { Write-Err "Docker n'a pas demarre."; exit 1 }
        Write-OK "Docker actif apres ${elapsed}s."
    } else {
        Write-Err "Docker Desktop introuvable a $dockerDesktopExe."
        exit 1
    }
}

# ============================================================================
# ETAPE 4 : Build des images
# ============================================================================
if ($Rebuild) {
    Write-Step "REBUILD complet (--no-cache)"
    docker compose -f $ComposeFile -p $ProjectName build --no-cache
} else {
    Write-Step "Build (incrementiel)"
    docker compose -f $ComposeFile -p $ProjectName build
}
if ($LASTEXITCODE -ne 0) { Write-Err "Build echoue."; exit 1 }
Write-OK "Image(s) Docker prete(s)."

# ============================================================================
# ETAPE 5 : Up des services (Ollama, Isabelle, agent)
# ============================================================================
Write-Step "Demarrage des services (Ollama, Isabelle, ollama-init)"
docker compose -f $ComposeFile -p $ProjectName up -d ollama isabelle
if ($LASTEXITCODE -ne 0) { Write-Err "Echec up Ollama/Isabelle."; exit 1 }

Write-Step "Initialisation d'Ollama (telechargement du modele)"
docker compose -f $ComposeFile -p $ProjectName up -d ollama-init
Write-OK "Services up. Attendez ~30s pour que Ollama soit pret la premiere fois."

# ============================================================================
# ETAPE 6 : Ouverture du terminal interactif avec l'agent
# ============================================================================
if ($NoOpen) {
    Write-OK "Services lances. Pour lancer l'agent : "
    Write-Host "   docker compose -f $ComposeFile -p $ProjectName run --rm $ServiceMain python main_cli.py" -ForegroundColor Yellow
    exit 0
}

Write-Step "Ouverture du terminal multiloop"

# Construire la commande qui sera executee dans le nouveau terminal
$dockerRunCmd = @"
Write-Host ''
Write-Host '  +===========================================================+' -ForegroundColor Magenta
Write-Host '  |   AGENT MULTI-LOOP  -  Gabriel  |  Terminal actif        |' -ForegroundColor Magenta
Write-Host '  |   Container : $ContainerName' -ForegroundColor Magenta
Write-Host '  |   Mode      : Multi-Loop (Ollama/OpenAI + HOL + critique) |' -ForegroundColor Magenta
Write-Host '  +===========================================================+' -ForegroundColor Magenta
Write-Host ''
docker compose -f '$ComposeFile' -p '$ProjectName' run --rm --service-ports $ServiceMain python main_cli.py
Write-Host ''
Write-Host '[Agent termine - Entree pour fermer]' -ForegroundColor Yellow
Read-Host
"@

$encoded = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($dockerRunCmd))

$wt = Get-Command "wt.exe" -ErrorAction SilentlyContinue
if ($wt) {
    Write-OK "Ouverture dans Windows Terminal..."
    Start-Process "wt.exe" -ArgumentList "powershell -NoExit -EncodedCommand $encoded"
} else {
    Write-Warn "wt.exe absent - ouverture dans PowerShell standard."
    Start-Process "powershell" -ArgumentList "-NoExit -EncodedCommand $encoded"
}

Write-OK "Terminal multiloop lance. Bonne session Gabriel !"

# ============================================================================
# RESUME
# ============================================================================
Write-Host ""
Write-Host "==================================================" -ForegroundColor Magenta
Write-Host "  MULTI-LOOP AGENT  -  Demarrage complet"          -ForegroundColor Green
Write-Host "     Project   : $ProjectName"                       -ForegroundColor Cyan
Write-Host "     Theories  : $TheoriesDir"                       -ForegroundColor Cyan
Write-Host "     Logs      : $LogsDir"                           -ForegroundColor Cyan
Write-Host "     Env file  : $EnvFile"                           -ForegroundColor Cyan
Write-Host ""
Write-Host "  Commandes utiles :"                                -ForegroundColor Cyan
Write-Host "     .\start-agent.ps1 -Logs      # streaming logs"  -ForegroundColor DarkCyan
Write-Host "     .\start-agent.ps1 -Status    # etat services"   -ForegroundColor DarkCyan
Write-Host "     .\start-agent.ps1 -Stop      # arret"           -ForegroundColor DarkCyan
Write-Host "     .\start-agent.ps1 -Rebuild   # rebuild complet" -ForegroundColor DarkCyan
Write-Host "==================================================" -ForegroundColor Magenta
Write-Host ""
