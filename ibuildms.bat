@echo off
setlocal

set "CYGWIN_BASH=C:\Users\HP 3\Isabelle2025-2\contrib\cygwin\bin\bash.exe"
set "THEORIES_CYG=/cygdrive/c/agent-multiloop-Gabriel-local-final/agent-multiloop-Gabriel-local/theories"
set "ISABELLE_CYG=/cygdrive/c/Users/'HP 3'/Isabelle2025-2/bin/isabelle"

if not exist "%CYGWIN_BASH%" (
  echo [ibuildms] ERROR: Cygwin bash not found: %CYGWIN_BASH%
  exit /b 1
)

"%CYGWIN_BASH%" -lc "cd %THEORIES_CYG% && %ISABELLE_CYG% build -D ."
set "RC=%ERRORLEVEL%"

echo [ibuildms] EXIT_CODE=%RC%
exit /b %RC%
