#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
fi

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "${SCRIPT_DIR}/.." && pwd)
export ARCH
export OS_CODENAME

if [[ ${EUID} -eq 0 ]]; then
  SUDO=""
else
  if command -v sudo >/dev/null 2>&1; then
    SUDO="sudo"
  else
    echo "sudo is required. Install it and rerun this script." >&2
    exit 1
  fi
fi

run_cmd() {
  local cmd=()
  if [[ -n "${SUDO}" ]]; then
    cmd+=(sudo)
  fi
  cmd+=("$@")
  printf '+ %s\n' "${cmd[*]}"
  if [[ "${DRY_RUN}" != "1" ]]; then
    "${cmd[@]}"
  fi
}

run_cmd_local() {
  local cmd=("$@")
  printf '+ %s\n' "${cmd[*]}"
  if [[ "${DRY_RUN}" != "1" ]]; then
    "${cmd[@]}"
  fi
}

log() {
  echo "[labsetup] $*"
}

log "Repository root: ${REPO_ROOT}"

if [[ "${DRY_RUN}" == "1" ]]; then
  log "Dry run mode enabled; no changes will be made."
fi

detect_os() {
  if command -v lsb_release >/dev/null 2>&1; then
    OS_ID=$(lsb_release -is)
    OS_VERSION=$(lsb_release -rs)
    OS_CODENAME=$(lsb_release -cs)
  elif [[ -f /etc/os-release ]]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    OS_ID="${ID:-unknown}"
    OS_VERSION="${VERSION_ID:-unknown}"
    OS_CODENAME="${VERSION_CODENAME:-${UBUNTU_CODENAME:-unknown}}"
  else
    OS_ID="unknown"
    OS_VERSION="unknown"
    OS_CODENAME="unknown"
  fi
}

detect_arch() {
  if command -v dpkg >/dev/null 2>&1; then
    dpkg --print-architecture
  else
    local machine
    machine=$(uname -m)
    case "${machine}" in
      x86_64) echo amd64 ;;
      aarch64|arm64) echo arm64 ;;
      armv7l) echo armhf ;;
      *) echo "${machine}" ;;
    esac
  fi
}

tolower() {
  printf '%s\n' "$1" | tr '[:upper:]' '[:lower:]'
}

detect_os
ARCH=$(detect_arch)
OS_ID_LOWER=$(tolower "${OS_ID}")
log "Detected OS: ${OS_ID} ${OS_VERSION} (${OS_CODENAME})"
log "Detected architecture: ${ARCH}"

if [[ "${OS_ID_LOWER}" != "ubuntu" && "${DRY_RUN}" != "1" ]]; then
  echo "This script is intended for Ubuntu. Exiting." >&2
  exit 1
fi

if [[ "${OS_ID_LOWER}" != "ubuntu" ]]; then
  log "Warning: this script is intended for Ubuntu. Continuing anyway."
fi

if [[ "${OS_CODENAME}" != "noble" ]]; then
  log "Warning: this script was tested on Ubuntu 24.04 (Noble). Continuing on ${OS_CODENAME}."
fi

log "Installing base packages"
run_cmd env DEBIAN_FRONTEND=noninteractive apt-get update
run_cmd env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  ca-certificates curl gnupg lsb-release git software-properties-common \
  python3 python3-pip python3-venv

log "Installing Docker Engine and Compose plugin"
if [[ ! -f /etc/apt/sources.list.d/docker.list ]]; then
  run_cmd install -m 0755 -d /etc/apt/keyrings
  run_cmd sh -c 'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg'
  run_cmd chmod a+r /etc/apt/keyrings/docker.gpg
  run_cmd sh -c "printf 'deb [arch=%s signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu %s stable\n' \"${ARCH}\" \"$(lsb_release -cs 2>/dev/null || echo \"${OS_CODENAME}\")\" > /etc/apt/sources.list.d/docker.list"
fi
run_cmd env DEBIAN_FRONTEND=noninteractive apt-get update
run_cmd env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

if command -v systemctl >/dev/null 2>&1; then
  run_cmd systemctl enable --now docker
else
  log "systemctl not found; start Docker manually after the script completes"
fi

CURRENT_USER=$(whoami)
if id -nG "${CURRENT_USER}" | grep -qw docker; then
  log "${CURRENT_USER} already has Docker group access"
else
  run_cmd usermod -aG docker "${CURRENT_USER}"
fi

log "Installing kind"
KIND_VERSION="v0.23.0"
KIND_BIN="/usr/local/bin/kind"
if [[ ! -x "${KIND_BIN}" ]]; then
  run_cmd curl -Lo /tmp/kind "https://kind.sigs.k8s.io/dl/${KIND_VERSION}/kind-linux-${ARCH}"
  run_cmd install -m 0755 /tmp/kind "${KIND_BIN}"
  run_cmd rm -f /tmp/kind
fi

log "Installing kubectl"
KUBECTL_BIN="/usr/local/bin/kubectl"
if [[ ! -x "${KUBECTL_BIN}" ]]; then
  K8S_VERSION=$(curl -L -s https://dl.k8s.io/release/stable.txt)
  run_cmd curl -Lo /tmp/kubectl "https://dl.k8s.io/release/${K8S_VERSION}/bin/linux/${ARCH}/kubectl"
  run_cmd install -m 0755 /tmp/kubectl "${KUBECTL_BIN}"
  run_cmd rm -f /tmp/kubectl
fi

log "Installing Terraform"
if [[ ! -f /etc/apt/sources.list.d/hashicorp.list ]]; then
  run_cmd sh -c 'curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg'
  run_cmd sh -c "printf 'deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com %s main\n' \"$(lsb_release -cs 2>/dev/null || echo \"${OS_CODENAME}\")\" > /etc/apt/sources.list.d/hashicorp.list"
fi
run_cmd env DEBIAN_FRONTEND=noninteractive apt-get update
run_cmd env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends terraform

log "Creating Python virtual environment for the sample app"
if [[ -d "${REPO_ROOT}/labs/app" ]]; then
  run_cmd_local python3 -m venv "${REPO_ROOT}/labs/app/.venv"
  run_cmd_local "${REPO_ROOT}/labs/app/.venv/bin/pip" install --upgrade pip
  run_cmd_local "${REPO_ROOT}/labs/app/.venv/bin/pip" install -r "${REPO_ROOT}/labs/app/requirements.txt" pytest python-pptx matplotlib
fi

echo
log "Installation complete."
log "Please log out and back in (or run 'newgrp docker') for Docker group changes to take effect."
log "Verify with:"
log "  docker --version"
log "  docker compose version"
log "  kind version"
log "  kubectl version --client"
log "  terraform -version"
log "  ${REPO_ROOT}/labs/app/.venv/bin/python --version"
