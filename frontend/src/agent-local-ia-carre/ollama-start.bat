@echo off
REM ===========================================
REM QUICK START - Démarrer Ollama (Windows)
REM Exécution simple sans menu
REM ===========================================

echo.
echo =============================================
echo   OLLAMA - DÉMARRAGE RAPIDE
echo =============================================
echo.

REM Vérifier Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Docker n'est pas installe ou n'est pas dans le PATH!
    echo.
    echo Telechargez: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

echo [OK] Docker detecte
docker --version
echo.

REM Vérifier Docker Compose
docker compose version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Docker Compose n'est pas disponible!
    pause
    exit /b 1
)

echo [OK] Docker Compose detecte
echo.

REM Aller dans le bon répertoire
cd /d "C:\agent-local-ia-carre\local_ai_agent"
if errorlevel 1 (
    echo ERREUR: Repertoire local_ai_agent non trouve!
    pause
    exit /b 1
)

echo [OK] Repertoire: %cd%
echo.

REM Tester Ollama
echo Vérification si Ollama tourne deja...
timeout /t 1 /nobreak >nul
powershell -Command "try { Invoke-WebRequest -Uri http://localhost:11434/api/tags -TimeoutSec 2 -ErrorAction Stop | Out-Null; Write-Host '[OK] Ollama est DEJA ACTIF!' -ForegroundColor Green; exit 0 } catch { exit 1 }" 

if %ERRORLEVEL% equ 0 (
    echo.
    echo [OK] Ollama repondu! Services deja demarres.
    echo.
    goto test_agent
)

REM Démarrer Ollama
echo.
echo Demarrage d'Ollama (docker compose)...
echo ATTENTION: Cela peut prendre 15-25 minutes la PREMIERE FOIS
echo (Le modele llama3.2 doit etre telecharge)
echo.
pause

docker compose -f docker-compose.cli.yml up -d ollama ollama-init

if %ERRORLEVEL% neq 0 (
    echo ERREUR lors du demarrage d'Ollama
    pause
    exit /b 1
)

echo.
echo Services demarres. Attente de 30 secondes...
echo.

setlocal enabledelayedexpansion
for /l %%i in (1,1,30) do (
    set /p "=." <nul
    timeout /t 1 /nobreak >nul
)
echo.

:test_agent
echo.
echo Verification finale...
echo.

powershell -Command "try { $r = Invoke-WebRequest -Uri http://localhost:11434/api/tags -TimeoutSec 5; $j = $r.Content | ConvertFrom-Json; Write-Host '✅ OLLAMA OPERATIONNEL!' -ForegroundColor Green; Write-Host 'Modeles:' -ForegroundColor Green; $j.models | ForEach-Object { Write-Host ('  • ' + $_.name) -ForegroundColor Cyan }; exit 0 } catch { Write-Host '❌ Ollama n''est pas encore pret (peut-être en train de charger le modele)' -ForegroundColor Red; Write-Host 'Verifiez avec: docker logs ollama -f' -ForegroundColor Yellow; exit 1 }" 

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================
    echo  ✅ PRET! Vous pouvez lancer les agents
    echo ========================================
    echo.
    echo Pour l'agent MULTI-LOOP:
    echo   cd C:\agent-local-ia-carre\agent-multiloop-local
    echo   python -m src.main --goal "Calculer SA(3)"
    echo.
    echo Pour l'agent LOCAL:
    echo   cd C:\agent-local-ia-carre\local_ai_agent
    echo   python math-agent-cli.py
    echo.
) else (
    echo.
    echo ========================================
    echo  ⚠️  Ollama charge le modele
    echo ========================================
    echo.
    echo Attendre quelques minutes...
    echo.
    echo Voir les logs:
    echo   docker logs ollama -f
    echo.
)

pause
