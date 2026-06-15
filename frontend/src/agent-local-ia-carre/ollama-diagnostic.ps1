# ============================================================
#  DIAGNOSTIC & DÉMARRAGE AUTOMATISÉ - OLLAMA
#  Windows PowerShell Script
# ============================================================
#  Usage: .\ollama-diagnostic.ps1
# ============================================================

$ErrorActionPreference = "Continue"

function Write-Header {
    param([string]$Text)
    Write-Host "`n$('='*60)" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host "$('='*60)`n" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Text)
    Write-Host "✅ $Text" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Text)
    Write-Host "❌ $Text" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Text)
    Write-Host "⚠️  $Text" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Text)
    Write-Host "ℹ️  $Text" -ForegroundColor Cyan
}

# ============================================================
# 1. CHECK DOCKER INSTALLATION
# ============================================================
Write-Header "1️⃣  VÉRIFICATION - Docker Desktop"

try {
    $dockerVersion = docker --version
    Write-Success "Docker détecté"
    Write-Info $dockerVersion
} catch {
    Write-Error-Custom "Docker n'est PAS installé ou n'est pas dans le PATH"
    Write-Warning-Custom "Téléchargez Docker Desktop: https://www.docker.com/products/docker-desktop/"
    pause
    exit 1
}

try {
    $composeVersion = docker compose version
    Write-Success "Docker Compose détecté"
    Write-Info $composeVersion
} catch {
    Write-Error-Custom "Docker Compose n'est pas disponible"
    pause
    exit 1
}

# ============================================================
# 2. CHECK LOCAL PATH
# ============================================================
Write-Header "2️⃣  VÉRIFICATION - Chemins locaux"

$localAiPath = "C:\agent-local-ia-carre\local_ai_agent"
$multiloopPath = "C:\agent-local-ia-carre\agent-multiloop-local"

if (Test-Path $localAiPath) {
    Write-Success "Trouvé: local_ai_agent"
} else {
    Write-Error-Custom "Chemin non trouvé: $localAiPath"
}

if (Test-Path $multiloopPath) {
    Write-Success "Trouvé: agent-multiloop-local"
} else {
    Write-Error-Custom "Chemin non trouvé: $multiloopPath"
}

# ============================================================
# 3. CHECK DOCKER DAEMON
# ============================================================
Write-Header "3️⃣  VÉRIFICATION - Docker Daemon"

try {
    docker ps -q | Out-Null
    Write-Success "Docker Daemon est actif"
    $containerCount = (docker ps -a -q | Measure-Object | Select-Object -ExpandProperty Count)
    Write-Info "Conteneurs actifs/existants: $containerCount"
} catch {
    Write-Error-Custom "Docker Daemon n'est pas actif"
    Write-Warning-Custom "Démarrez Docker Desktop et réessayez"
    pause
    exit 1
}

# ============================================================
# 4. CHECK OLLAMA AVAILABILITY
# ============================================================
Write-Header "4️⃣  VÉRIFICATION - Ollama (Port 11434)"

$ollamaURL = "http://localhost:11434/api/tags"
$ollamaAvailable = $false

try {
    $response = Invoke-WebRequest -Uri $ollamaURL -TimeoutSec 5 -ErrorAction Stop
    $ollamaAvailable = $true
    Write-Success "Ollama est DISPONIBLE sur port 11434"
    
    $models = $response.Content | ConvertFrom-Json
    Write-Info "Modèles disponibles:"
    $models.models | ForEach-Object {
        $sizeMB = [math]::Round($_.size / 1MB, 2)
        Write-Host "    • $($_.name) ($sizeMB MB)" -ForegroundColor Green
    }
} catch {
    Write-Warning-Custom "Ollama n'est PAS en cours d'exécution"
    Write-Info "Le service Ollama doit être démarré via Docker Compose"
    $ollamaAvailable = $false
}

# ============================================================
# 5. CHECK DOCKER IMAGES
# ============================================================
Write-Header "5️⃣  VÉRIFICATION - Images Docker"

try {
    $images = docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
    if ($images) {
        Write-Success "Images Docker disponibles:"
        $images | ForEach-Object { Write-Host "    $_" -ForegroundColor Cyan }
    }
} catch {
    Write-Warning-Custom "Impossible de lister les images"
}

# ============================================================
# 6. CHECK NETWORK
# ============================================================
Write-Header "6️⃣  VÉRIFICATION - Réseau & Connectivité"

try {
    $ping = Test-Connection -ComputerName 8.8.8.8 -Count 1 -Quiet
    if ($ping) {
        Write-Success "Connexion Internet: OK"
    } else {
        Write-Warning-Custom "Connexion Internet: Faible ou absente"
    }
} catch {
    Write-Warning-Custom "Impossible de tester la connexion"
}

# ============================================================
# 7. CHECK DISK SPACE
# ============================================================
Write-Header "7️⃣  VÉRIFICATION - Espace disque"

$drives = Get-Volume | Where-Object { $_.Size -gt 0 }
$drives | ForEach-Object {
    $freePercent = [math]::Round(($_.SizeRemaining / $_.Size) * 100, 2)
    $freeGB = [math]::Round($_.SizeRemaining / 1GB, 2)
    if ($freePercent -lt 10) {
        Write-Error-Custom "Drive $($_.DriveLetter): $freeGB GB libre ($freePercent%)"
    } elseif ($freePercent -lt 20) {
        Write-Warning-Custom "Drive $($_.DriveLetter): $freeGB GB libre ($freePercent%)"
    } else {
        Write-Success "Drive $($_.DriveLetter): $freeGB GB libre ($freePercent%)"
    }
}

# ============================================================
# 8. SUMMARY & RECOMMENDATIONS
# ============================================================
Write-Header "📋 RÉSUMÉ & RECOMMANDATIONS"

if ($ollamaAvailable) {
    Write-Success "✅ Système prêt à exécuter les agents!"
} else {
    Write-Warning-Custom "Ollama doit être démarré avant d'exécuter les agents"
    Write-Info "Deux options:"
    Write-Host "`n  Option A - Via script automatisé (recommandé):" -ForegroundColor Yellow
    Write-Host "    cd $localAiPath" -ForegroundColor Cyan
    Write-Host "    .\docker-start.bat" -ForegroundColor Cyan
    Write-Host "    → Sélectionner option 2 (CLI mode)" -ForegroundColor Cyan
    
    Write-Host "`n  Option B - Commande directe:" -ForegroundColor Yellow
    Write-Host "    cd $localAiPath" -ForegroundColor Cyan
    Write-Host "    docker compose -f docker-compose.cli.yml up -d ollama ollama-init" -ForegroundColor Cyan
    Write-Host "    → Attendre 30-45 secondes pour le téléchargement du modèle" -ForegroundColor Cyan
    
    Write-Host "`n  Option C - Démarrage semi-automatique:" -ForegroundColor Yellow
    Write-Host "    Appuyez sur [D] ci-dessous pour démarrer automatiquement" -ForegroundColor Cyan
}

# ============================================================
# 9. INTERACTIVE MENU
# ============================================================
Write-Header "🎯 MENU INTERACTIF"

Write-Host "Que voulez-vous faire?" -ForegroundColor Cyan
Write-Host "`n  [T] Tester la connexion Ollama à nouveau" -ForegroundColor Yellow
Write-Host "  [D] Démarrer Ollama (mode Docker Compose CLI)" -ForegroundColor Yellow
Write-Host "  [S] Voir l'état des services Ollama" -ForegroundColor Yellow
Write-Host "  [L] Afficher les logs d'Ollama" -ForegroundColor Yellow
Write-Host "  [A] Arrêter tous les services" -ForegroundColor Yellow
Write-Host "  [Q] Quitter" -ForegroundColor Yellow
Write-Host ""

$choice = Read-Host "Votre choix (T/D/S/L/A/Q)"

switch ($choice.ToUpper()) {
    "T" {
        Write-Header "TEST - Ollama"
        try {
            $response = Invoke-WebRequest -Uri $ollamaURL -TimeoutSec 5
            Write-Success "Ollama répond correctement!"
            $response.Content | ConvertFrom-Json | ConvertTo-Json | Write-Host
        } catch {
            Write-Error-Custom "Ollama n'est pas disponible: $_"
        }
    }
    
    "D" {
        Write-Header "DÉMARRAGE - Ollama"
        Write-Info "Démarrage des services Ollama (docker-compose)..."
        Write-Warning-Custom "Cela peut prendre 15-25 minutes la première fois"
        
        cd $localAiPath
        docker compose -f docker-compose.cli.yml up -d ollama ollama-init
        
        Write-Info "Services démarrés. Attente de 30 secondes..."
        1..30 | ForEach-Object {
            Write-Host -NoNewline "."
            Start-Sleep -Seconds 1
        }
        
        Write-Success "Ollama devrait être prêt!"
        Write-Info "Test de connexion..."
        
        try {
            $response = Invoke-WebRequest -Uri $ollamaURL -TimeoutSec 5
            Write-Success "✅ Ollama est opérationnel!"
        } catch {
            Write-Warning-Custom "Ollama charge peut-être le modèle (attente de 5-10 min)"
            Write-Info "Vérifiez avec: docker logs ollama -f"
        }
    }
    
    "S" {
        Write-Header "ÉTAT - Services Ollama"
        docker ps -a --filter "name=ollama" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        Write-Info "Pour plus de détails: docker compose ps"
    }
    
    "L" {
        Write-Header "LOGS - Ollama"
        cd $localAiPath
        docker logs ollama -f --tail=50
    }
    
    "A" {
        Write-Header "ARRÊT - Services"
        cd $localAiPath
        docker compose down
        docker compose -f docker-compose.cli.yml down
        Write-Success "Services arrêtés"
    }
    
    "Q" {
        Write-Host "Au revoir!" -ForegroundColor Cyan
        exit 0
    }
    
    default {
        Write-Error-Custom "Choix invalide"
    }
}

Write-Host "`n`nAppuyez sur une touche pour quitter..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
