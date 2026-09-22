#!/usr/bin/env bash
# ==============================================================================
# Portable Application Runner for Audio Transcriber & AI Summarizer
# ==============================================================================

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"
BIN_DIR="${PROJECT_DIR}/bin"

# Export local bin to PATH and LD_LIBRARY_PATH if present
export PATH="${BIN_DIR}:${PATH}"
export LD_LIBRARY_PATH="${BIN_DIR}:${LD_LIBRARY_PATH:-}"

if [ ! -d "${VENV_DIR}" ]; then
    echo "[!] Virtual environment not found. Please run 'bash install.sh' first."
    exit 1
fi

echo "=========================================================="
echo " Starting Audio Transcriber & AI Summarizer Platform"
echo " Configuration: config.json (or defaults)"
echo "=========================================================="

exec "${VENV_DIR}/bin/python3" main.py
