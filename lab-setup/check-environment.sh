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

check() {
  local name="$1" required="$2"; shift 2
  local detail
  if detail=$("$@" 2>&1 | head -1); then
    ROWS+=("PASS|${name}|${detail}")
    PASS=$((PASS + 1))
  else
    if [[ "${required}" == "required" ]]; then
      ROWS+=("FAIL|${name}|not working — rerun lab-setup/install-ubuntu24.sh")
      FAIL=$((FAIL + 1))
    else
      ROWS+=("WARN|${name}|optional, not found")
    fi
  fi
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
check "COURSE_HOME"       optional bash -c '[ -n "${COURSE_HOME:-}" ] && [ -d "${COURSE_HOME}/lab-setup" ] && echo "${COURSE_HOME}"' 

echo
printf '%-6s %-22s %s\n' "STATUS" "CHECK" "DETAIL"
printf '%-6s %-22s %s\n' "------" "-----" "------"
for row in "${ROWS[@]}"; do
  IFS='|' read -r status name detail <<<"${row}"
  printf '%-6s %-22s %s\n' "${status}" "${name}" "${detail}"
done

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
