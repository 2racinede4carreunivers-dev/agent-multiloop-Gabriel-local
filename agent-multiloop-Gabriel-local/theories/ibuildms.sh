#!/usr/bin/env bash
set -euo pipefail

# Ultra-short, safe launcher for Methode_Spectral from the correct ROOT.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ISABELLE_BIN_DEFAULT="/cygdrive/c/Users/HP 3/Isabelle2025-2/bin/isabelle"
ISABELLE_BIN="${ISABELLE_BIN:-$ISABELLE_BIN_DEFAULT}"

if [[ ! -f "$SCRIPT_DIR/ROOT" ]]; then
  echo "[ibuildms] ERROR: ROOT not found in $SCRIPT_DIR"
  exit 1
fi

if [[ ! -f "$SCRIPT_DIR/methode_spectral.thy" ]]; then
  echo "[ibuildms] ERROR: methode_spectral.thy not found in $SCRIPT_DIR"
  exit 1
fi

if [[ ! -x "$ISABELLE_BIN" ]]; then
  echo "[ibuildms] ERROR: Isabelle binary not executable: $ISABELLE_BIN"
  echo "[ibuildms] Tip: export ISABELLE_BIN='/cygdrive/c/.../isabelle'"
  exit 1
fi

cd "$SCRIPT_DIR"
echo "[ibuildms] Using ROOT: $SCRIPT_DIR/ROOT"
echo "[ibuildms] Running: $ISABELLE_BIN build -D $SCRIPT_DIR $*"
exec "$ISABELLE_BIN" build -D "$SCRIPT_DIR" "$@"
