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

# ---------------------------------------------------------------------------
# Idempotence and repair
#
# This script is safe to run repeatedly. Every component is checked first and
# only the missing ones are installed, so a re-run on a fully provisioned VM
# performs no downloads at all — it does not even run `apt-get update`. That
# makes it the repair tool too: if one tool is missing, or a lab removed
# something, just run it again.
#
# One failure does not stop the rest: anything that cannot be installed is
# collected and reported at the end, and the script exits non-zero so the
# preflight check (and any automation) notices.
# ---------------------------------------------------------------------------
INSTALLED=()
PRESENT=()
FAILED=()

have() { command -v "$1" >/dev/null 2>&1; }

mark_installed() { INSTALLED+=("$1"); log "$1: installed"; }
mark_present()   { PRESENT+=("$1");   log "$1: already present - skipping"; }
mark_failed()    { FAILED+=("$1");    log "$1: FAILED - see the output above"; }

APT_UPDATED=0
apt_update_once() {
  if [[ "${APT_UPDATED}" == "1" ]]; then
    return 0
  fi
  if run_cmd env DEBIAN_FRONTEND=noninteractive apt-get update; then
    APT_UPDATED=1
    return 0
  fi
  return 1
}

pkg_installed() {
  dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q "ok installed"
}

# apt_install_missing <label> <pkg>...  — installs only the packages that are
# not already installed, and only touches the network if there are any.
apt_install_missing() {
  local label="$1"; shift
  local missing=() pkg
  for pkg in "$@"; do
    pkg_installed "${pkg}" || missing+=("${pkg}")
  done
  if [[ ${#missing[@]} -eq 0 ]]; then
    mark_present "${label}"
    return 0
  fi
  log "${label}: missing ${missing[*]}"
  if ! apt_update_once; then
    mark_failed "${label} (apt-get update failed - check network)"
    return 0
  fi
  if run_cmd env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${missing[@]}"; then
    mark_installed "${label}"
  else
    mark_failed "${label}"
  fi
}

log "Checking base packages"
apt_install_missing "Base packages" \
  ca-certificates curl gnupg lsb-release git software-properties-common \
  python3 python3-pip python3-venv tmux jq unzip apt-transport-https

log "Checking Ansible (configuration management, Lab Day 1 Part E)"
apt_install_missing "Ansible" ansible

log "Checking Docker Engine and Compose plugin"
if [[ ! -f /etc/apt/sources.list.d/docker.list ]]; then
  log "Adding the Docker apt repository"
  run_cmd install -m 0755 -d /etc/apt/keyrings
  run_cmd sh -c 'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg'
  run_cmd chmod a+r /etc/apt/keyrings/docker.gpg
  run_cmd sh -c "printf 'deb [arch=%s signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu %s stable\n' \"${ARCH}\" \"$(lsb_release -cs 2>/dev/null || echo \"${OS_CODENAME}\")\" > /etc/apt/sources.list.d/docker.list"
  APT_UPDATED=0   # a new repository means the package lists are stale again
fi
apt_install_missing "Docker Engine + Compose plugin" \
  docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Starting the daemon is best-effort: systemd is absent in containers and WSL,
# and a failure here must not stop the remaining tools from installing.
if have systemctl && [[ -d /run/systemd/system ]]; then
  if systemctl is-active --quiet docker 2>/dev/null; then
    log "Docker service: already running"
  elif run_cmd systemctl enable --now docker; then
    log "Docker service: enabled and started"
  else
    log "Docker service: could not be started automatically - start it manually with 'sudo systemctl start docker'"
  fi
else
  log "Docker service: systemd not running here (container/WSL) - start the daemon the way your platform expects"
fi

CURRENT_USER=$(whoami)
if id -nG "${CURRENT_USER}" 2>/dev/null | grep -qw docker; then
  log "Docker group: ${CURRENT_USER} already a member"
elif run_cmd usermod -aG docker "${CURRENT_USER}"; then
  log "Docker group: added ${CURRENT_USER} - log out and back in (or run 'newgrp docker') to activate"
else
  log "Docker group: could not add ${CURRENT_USER}; add it manually with 'sudo usermod -aG docker ${CURRENT_USER}'"
fi

log "Checking kind"
KIND_VERSION="v0.23.0"
install_kind() {
  run_cmd curl -fLo /tmp/kind "https://kind.sigs.k8s.io/dl/${KIND_VERSION}/kind-linux-${ARCH}" || return 1
  run_cmd install -m 0755 /tmp/kind /usr/local/bin/kind || return 1
  run_cmd rm -f /tmp/kind || true
}
if have kind; then
  mark_present "kind"
elif install_kind; then
  mark_installed "kind ${KIND_VERSION}"
else
  mark_failed "kind"
fi

log "Checking kubectl"
# Pinned for course reproducibility; bump deliberately each quarter.
K8S_VERSION="v1.30.3"
install_kubectl() {
  run_cmd curl -fLo /tmp/kubectl "https://dl.k8s.io/release/${K8S_VERSION}/bin/linux/${ARCH}/kubectl" || return 1
  run_cmd install -m 0755 /tmp/kubectl /usr/local/bin/kubectl || return 1
  run_cmd rm -f /tmp/kubectl || true
}
if have kubectl; then
  mark_present "kubectl"
elif install_kubectl; then
  mark_installed "kubectl ${K8S_VERSION}"
else
  mark_failed "kubectl"
fi

log "Checking Terraform"
if have terraform; then
  mark_present "Terraform"
else
  if [[ ! -f /etc/apt/sources.list.d/hashicorp.list ]]; then
    log "Adding the HashiCorp apt repository"
    run_cmd sh -c 'curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg'
    run_cmd sh -c "printf 'deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com %s main\n' \"$(lsb_release -cs 2>/dev/null || echo \"${OS_CODENAME}\")\" > /etc/apt/sources.list.d/hashicorp.list"
    APT_UPDATED=0
  fi
  apt_install_missing "Terraform" terraform
fi

log "Checking Trivy (vulnerability & misconfiguration scanner, Lab 07)"
if have trivy; then
  mark_present "Trivy"
else
  if [[ ! -f /etc/apt/sources.list.d/trivy.list ]]; then
    log "Adding the Trivy apt repository"
    run_cmd sh -c 'curl -fsSL https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor -o /usr/share/keyrings/trivy.gpg'
    run_cmd sh -c "printf 'deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb %s main\n' \"$(lsb_release -cs 2>/dev/null || echo \"${OS_CODENAME}\")\" > /etc/apt/sources.list.d/trivy.list"
    APT_UPDATED=0
  fi
  apt_install_missing "Trivy" trivy
fi

# Pre-download the vulnerability DB so Lab 07 does not wait on classroom Wi-Fi.
# Refresh it deliberately later with: trivy image --download-db-only
if have trivy; then
  if [[ -f "${HOME}/.cache/trivy/db/trivy.db" ]]; then
    mark_present "Trivy vulnerability DB"
  elif run_cmd_local trivy image --download-db-only; then
    mark_installed "Trivy vulnerability DB"
  else
    log "Trivy DB pre-download failed; Lab 07 will download it on first scan"
  fi
fi

log "Checking Conftest (policy-as-code, Lab 07)"
CONFTEST_VERSION="0.56.0"
# Conftest release names use x86_64 / arm64
CONFTEST_ARCH=$(uname -m); [[ "${CONFTEST_ARCH}" == "aarch64" ]] && CONFTEST_ARCH="arm64"
install_conftest() {
  run_cmd_local curl -fsSL -o /tmp/conftest.tar.gz \
    "https://github.com/open-policy-agent/conftest/releases/download/v${CONFTEST_VERSION}/conftest_${CONFTEST_VERSION}_Linux_${CONFTEST_ARCH}.tar.gz" || return 1
  run_cmd_local tar -xzf /tmp/conftest.tar.gz -C /tmp conftest || return 1
  run_cmd install -m 0755 /tmp/conftest /usr/local/bin/conftest || return 1
  run_cmd_local rm -f /tmp/conftest /tmp/conftest.tar.gz || true
}
if have conftest; then
  mark_present "Conftest"
elif install_conftest; then
  mark_installed "Conftest ${CONFTEST_VERSION}"
else
  mark_failed "Conftest"
fi

log "Checking act (runs GitHub Actions workflows locally, Lab 04)"
ACT_VERSION="0.2.68"
# act release assets use x86_64 / arm64
ACT_ARCH=$(uname -m); [[ "${ACT_ARCH}" == "aarch64" ]] && ACT_ARCH="arm64"
install_act_pinned() {
  run_cmd_local curl -fsSL -o /tmp/act.tar.gz \
    "https://github.com/nektos/act/releases/download/v${ACT_VERSION}/act_Linux_${ACT_ARCH}.tar.gz" || return 1
  run_cmd_local tar -xzf /tmp/act.tar.gz -C /tmp act || return 1
  run_cmd install -m 0755 /tmp/act /usr/local/bin/act || return 1
  run_cmd_local rm -f /tmp/act /tmp/act.tar.gz || true
}
if have act; then
  mark_present "act"
elif install_act_pinned; then
  mark_installed "act ${ACT_VERSION}"
elif run_cmd sh -c 'curl -fsSL https://raw.githubusercontent.com/nektos/act/master/install.sh | bash -s -- -b /usr/local/bin'; then
  log "Pinned act download failed; used the upstream installer instead"
  mark_installed "act (upstream installer)"
else
  mark_failed "act (Lab 04 Parts B-C need it)"
fi

# Pre-pull the images the pipeline uses, so a lab never waits on classroom
# Wi-Fi: the act/Gitea runner image (~1 GB) and the Trivy scanner image.
ACT_RUNNER_IMAGE="catthehacker/ubuntu:act-latest"
if have act && have docker; then
  if ! docker info >/dev/null 2>&1; then
    log "act runner image: Docker not reachable yet (new session needed for group membership) - the first 'act' run will pull ${ACT_RUNNER_IMAGE}"
  elif docker image inspect "${ACT_RUNNER_IMAGE}" >/dev/null 2>&1; then
    mark_present "act runner image"
  elif run_cmd_local docker pull "${ACT_RUNNER_IMAGE}"; then
    mark_installed "act runner image"
  else
    log "act runner image pre-pull failed; the first 'act' run will download it"
  fi
fi

# The CI/CD workflow runs Trivy as a container, so pre-pull that too.
if have docker && docker info >/dev/null 2>&1; then
  if docker image inspect aquasec/trivy:latest >/dev/null 2>&1; then
    mark_present "Trivy scanner image"
  elif run_cmd_local docker pull aquasec/trivy:latest; then
    mark_installed "Trivy scanner image"
  else
    log "Trivy image pre-pull failed; the pipeline will pull it on first run"
  fi
fi

log "Checking the Python virtual environment for the sample app"
APP_DIR="${REPO_ROOT}/labs/app"
VENV_PIP="${APP_DIR}/.venv/bin/pip"
VENV_PY="${APP_DIR}/.venv/bin/python"
install_app_deps() {
  run_cmd_local "${VENV_PIP}" install --upgrade pip || return 1
  run_cmd_local "${VENV_PIP}" install -r "${APP_DIR}/requirements.txt" || return 1
}
if [[ ! -d "${APP_DIR}" ]]; then
  log "No ${APP_DIR} directory found; skipping the virtualenv"
elif [[ ! -x "${VENV_PY}" ]]; then
  log "Creating ${APP_DIR}/.venv"
  if run_cmd_local python3 -m venv "${APP_DIR}/.venv" && install_app_deps; then
    mark_installed "App virtualenv"
  else
    mark_failed "App virtualenv"
  fi
elif "${VENV_PY}" -c 'import fastapi, pytest, httpx, uvicorn, prometheus_client' >/dev/null 2>&1; then
  mark_present "App virtualenv"
else
  log "App virtualenv exists but its dependencies are incomplete - reinstalling them"
  if install_app_deps; then
    mark_installed "App virtualenv dependencies"
  else
    mark_failed "App virtualenv dependencies"
  fi
fi

# --------------------------------------------------------------------- summary
echo
if [[ ${#INSTALLED[@]} -eq 0 ]]; then
  log "Nothing to install — every component was already present."
else
  log "Installed or repaired this run:"
  for item in "${INSTALLED[@]}"; do log "  + ${item}"; done
fi
if [[ ${#PRESENT[@]} -gt 0 ]]; then
  log "Already present: ${#PRESENT[@]} component(s)"
fi

if [[ ${#FAILED[@]} -gt 0 ]]; then
  echo
  log "STILL MISSING — re-run this script to retry just these:"
  for item in "${FAILED[@]}"; do log "  ! ${item}"; done
  echo
  log "Common causes: no network, a proxy blocking downloads, or full disk (df -h /)."
  exit 1
fi

echo
log "Setup complete. Safe to re-run at any time: it only fixes what is missing."
log "If you were just added to the docker group, log out and back in (or run 'newgrp docker')."
log "Verify with:"
log "  docker --version"
log "  docker compose version"
log "  kind version"
log "  kubectl version --client"
log "  terraform -version"
log "  trivy --version"
log "  conftest --version"
log "  act --version"
log "  ${REPO_ROOT}/labs/app/.venv/bin/python --version"
log ""
log "Now run the preflight check:"
log "  ${REPO_ROOT}/lab-setup/check-environment.sh"
