#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."
# Make the host-downloaded course binaries (kind, kubectl, terraform) available.
export PATH="${PWD}/verify/bin:${PATH}"
python3 tools/extract_lab_commands.py
python3 tools/run_lab_commands.py
