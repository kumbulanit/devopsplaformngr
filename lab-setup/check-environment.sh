#!/usr/bin/env bash
# Preflight check for the DevOps & Platform Engineering course.
# Run this on your Ubuntu 24.04 VM AFTER lab-setup/install-ubuntu24.sh.
# Prints a PASS/FAIL table; exits non-zero if anything required is missing.
set -uo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "${SCRIPT_DIR}/.." && pwd)

PASS=0
FAIL=0
declare -a ROWS

# Failure advice per check. "rerun the installer" is the right answer for a
# missing binary, but not for Docker: there the daemon is usually stopped, or
# the user's group membership has not taken effect in this shell yet.
# (A case statement, not an associative array: this stays portable to bash 3.)
hint_for() {
  case "$1" in
    "docker daemon")     echo "daemon not reachable — see the diagnosis below" ;;
    "docker group")      echo "sudo usermod -aG docker \$USER, then log out and back in (or: newgrp docker)" ;;
    "docker CLI")        echo "docker is not installed — rerun lab-setup/install-ubuntu24.sh" ;;
    "free disk >= 15GB") echo "free space with: docker system prune -a, or grow the disk" ;;
    "RAM >= 6GB")        echo "give the VM at least 6 GB — kind plus the observability stack need it" ;;
    "internet (GitHub)") echo "no route to github.com — check proxy/DNS settings" ;;
    "app venv + pytest") echo "rerun lab-setup/install-ubuntu24.sh — it rebuilds labs/app/.venv" ;;
    *)                   echo "not working — rerun lab-setup/install-ubuntu24.sh" ;;
  esac
}

check() {
  local name="$1" required="$2"; shift 2
  local detail rc
  # Capture first, trim after: piping straight into `head` can SIGPIPE a
  # chatty command and report a working tool as broken under `pipefail`.
  detail=$("$@" 2>&1); rc=$?
  detail=$(printf '%s\n' "${detail}" | head -1)
  if [[ ${rc} -eq 0 ]]; then
    ROWS+=("PASS|${name}|${detail}")
    PASS=$((PASS + 1))
  else
    if [[ "${required}" == "required" ]]; then
      ROWS+=("FAIL|${name}|$(hint_for "${name}")")
      FAIL=$((FAIL + 1))
    else
      ROWS+=("WARN|${name}|optional, not found")
    fi
  fi
}

# Explains WHY the Docker daemon is unreachable, because the fix differs:
# not installed / not started / no permission / no systemd (WSL, containers).
docker_diagnosis() {
  echo
  echo "--- Docker daemon diagnosis ---"
  if ! command -v docker >/dev/null 2>&1; then
    echo "  docker CLI is not installed. Fix: ./lab-setup/install-ubuntu24.sh"
    return
  fi
  local err
  err=$(docker info 2>&1 >/dev/null)
  if [[ -z "${err}" ]]; then
    echo "  Docker is reachable now (transient failure?). Re-run this script."
    return
  fi
  echo "  docker info says: $(printf '%s\n' "${err}" | head -2 | tr '\n' ' ')"
  case "${err}" in
    *"permission denied"*|*"Got permission denied"*)
      echo "  CAUSE: your user cannot reach the docker socket."
      echo "  FIX:   sudo usermod -aG docker \$USER   then log out and back in"
      echo "         (for this shell only: newgrp docker)"
      ;;
    *"Cannot connect to the Docker daemon"*|*"Is the docker daemon running"*|\
    *"failed to connect to the docker API"*|*"no such file or directory"*|*"connection refused"*)
      echo "  CAUSE: the daemon is not running."
      if command -v systemctl >/dev/null 2>&1 && [[ -d /run/systemd/system ]]; then
        echo "  FIX:   sudo systemctl start docker  &&  sudo systemctl enable docker"
        echo "  STATE: $(systemctl is-enabled docker 2>/dev/null || echo unknown)/$(systemctl is-active docker 2>/dev/null || echo inactive)"
        echo "  LOGS:  sudo journalctl -u docker -n 30 --no-pager"
      else
        echo "  FIX:   no systemd here (WSL/container) — start the daemon as your platform expects,"
        echo "         e.g. 'sudo dockerd &' or start Docker Desktop on the host."
      fi
      ;;
    *)
      echo "  FIX:   sudo systemctl restart docker, then re-run this script."
      ;;
  esac
  echo "  VERIFY: docker info --format '{{.ServerVersion}}'  &&  docker run --rm hello-world"
}

echo "Checking course environment on $(hostname) ..."
echo

check "Ubuntu 24.04"      required bash -c 'grep -q "24.04" /etc/os-release && grep VERSION_ID /etc/os-release'
check "git"               required git --version
check "docker CLI"        required docker --version
check "docker daemon"     required docker info --format 'server {{.ServerVersion}}'
check "docker group"      required bash -c 'id -nG | grep -qw docker && echo "user in docker group"'
check "docker compose"    required docker compose version
check "kind"              required kind version
check "kubectl"           required kubectl version --client --output=yaml
check "terraform"         required terraform -version
check "trivy"             required trivy --version
check "conftest"          required conftest --version
check "python3"           required python3 --version
check "app venv + pytest" required "${REPO_ROOT}/labs/app/.venv/bin/python" -m pytest --version
check "tmux"              required tmux -V
check "jq"                required jq --version
check "curl"              required curl --version
check "internet (GitHub)" required curl -fsI --max-time 10 https://github.com
check "free disk >= 15GB" required bash -c '[ "$(df --output=avail -BG / | tail -1 | tr -dc 0-9)" -ge 15 ] && df -h / | tail -1'
check "RAM >= 6GB"        required bash -c '[ "$(free -g | awk "/^Mem:/{print \$2}")" -ge 6 ] && free -h | head -2 | tail -1'
check "act"               required act --version
check "ansible"           required ansible --version
check "COURSE_HOME"       optional bash -c '[ -n "${COURSE_HOME:-}" ] && [ -d "${COURSE_HOME}/lab-setup" ] && echo "${COURSE_HOME}"' 

echo
printf '%-6s %-22s %s\n' "STATUS" "CHECK" "DETAIL"
printf '%-6s %-22s %s\n' "------" "-----" "------"
for row in "${ROWS[@]}"; do
  IFS='|' read -r status name detail <<<"${row}"
  printf '%-6s %-22s %s\n' "${status}" "${name}" "${detail}"
done

# Docker is the dependency most labs share, so explain it properly.
if printf '%s\n' "${ROWS[@]}" | grep -q '^FAIL|docker daemon|'; then
  docker_diagnosis
fi

echo
if [[ ${FAIL} -gt 0 ]]; then
  echo "RESULT: ${FAIL} required check(s) FAILED. Fix these before Day 1."
  echo "Hint: after install-ubuntu24.sh, log out and back in (or run 'newgrp docker')"
  echo "      so Docker group membership takes effect."
  exit 1
fi
if [[ -z "${COURSE_HOME:-}" || ! -d "${COURSE_HOME}/lab-setup" ]]; then
  echo "NOTE: COURSE_HOME is not set (labs use it to find this repository). Fix it with:"
  echo "      echo \"export COURSE_HOME=${REPO_ROOT}\" >> ~/.bashrc && export COURSE_HOME=${REPO_ROOT}"
  echo
fi
echo "RESULT: all required checks passed (${PASS}). You are ready for the course."
