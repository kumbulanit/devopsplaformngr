#!/usr/bin/env bash
# Stand up a pipeline web UI on localhost: Gitea + its Actions runner.
#
#   ./setup.sh            start it, create the user, register the runner
#   ./setup.sh --push     also create the repo and push /tmp/day1 to it
#   ./setup.sh --down     remove everything, including the volumes
#
# Safe to re-run: every step checks whether it has already been done.
set -uo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
cd "${SCRIPT_DIR}"

GITEA_URL="http://localhost:3001"
USER="lab"
PASS="labpass123"
REPO="order-service"
WORKDIR="/tmp/day1"

log() { echo "[pipeline-ui] $*"; }

if [[ "${1:-}" == "--down" ]]; then
  log "Removing Gitea, the runner and their volumes"
  RUNNER_TOKEN=unused docker compose down -v
  exit 0
fi

# ---------------------------------------------------------------- 1. Gitea
if docker ps --format '{{.Names}}' | grep -q '^lab-gitea$'; then
  log "Gitea already running"
else
  log "Starting Gitea"
  RUNNER_TOKEN=placeholder docker compose up -d gitea
fi

log "Waiting for Gitea to answer (first start takes ~15s)"
for _ in $(seq 1 60); do
  curl -sf "${GITEA_URL}/api/healthz" >/dev/null 2>&1 && break
  sleep 2
done
if ! curl -sf "${GITEA_URL}/api/healthz" >/dev/null 2>&1; then
  echo "Gitea did not come up. Check: docker logs lab-gitea" >&2
  exit 1
fi

# ------------------------------------------------------------- 2. the user
if docker exec -u git lab-gitea gitea admin user list 2>/dev/null | grep -qw "${USER}"; then
  log "User '${USER}' already exists"
else
  log "Creating user '${USER}' (password: ${PASS})"
  docker exec -u git lab-gitea gitea admin user create \
    --admin --username "${USER}" --password "${PASS}" \
    --email "${USER}@example.com" >/dev/null
fi

# ----------------------------------------------------------- 3. the runner
if docker ps --format '{{.Names}}' | grep -q '^lab-runner$'; then
  log "Runner already registered and running"
else
  log "Generating a runner registration token"
  TOKEN=$(docker exec -u git lab-gitea gitea actions generate-runner-token 2>/dev/null | tr -d '\r\n')
  if [[ -z "${TOKEN}" ]]; then
    echo "Could not generate a runner token. Check: docker logs lab-gitea" >&2
    exit 1
  fi
  log "Starting the runner (reusing the act runner image, so no extra download)"
  RUNNER_TOKEN="${TOKEN}" docker compose up -d runner

  for _ in $(seq 1 30); do
    docker logs lab-runner 2>&1 | grep -qi "registered successfully" && break
    sleep 2
  done
  docker logs lab-runner 2>&1 | grep -qi "registered successfully" \
    && log "Runner registered" \
    || log "WARNING: runner may not have registered - check: docker logs lab-runner"
fi

# ------------------------------------------------- 4. optional: repo + push
if [[ "${1:-}" == "--push" ]]; then
  if [[ ! -d "${WORKDIR}/.git" ]]; then
    echo "No git repository at ${WORKDIR}. Do Lab Day 1 Part B first." >&2
    exit 1
  fi

  code=$(curl -s -u "${USER}:${PASS}" -X POST "${GITEA_URL}/api/v1/user/repos" \
    -H 'content-type: application/json' \
    -d "{\"name\":\"${REPO}\",\"private\":false}" -o /dev/null -w '%{http_code}')
  case "${code}" in
    201) log "Repository '${REPO}' created" ;;
    409) log "Repository '${REPO}' already exists" ;;
    *)   echo "Unexpected response creating the repository: HTTP ${code}" >&2 ;;
  esac

  cd "${WORKDIR}"
  git remote remove gitea 2>/dev/null || true
  git remote add gitea "http://${USER}:${PASS}@localhost:3001/${USER}/${REPO}.git"
  log "Pushing ${WORKDIR} to Gitea - this triggers the pipeline"
  git push -q gitea main --force && log "Pushed"
fi

cat <<EOF

  Pipeline UI ready:

    ${GITEA_URL}/${USER}/${REPO}/actions
    login: ${USER} / ${PASS}

  Push again from ${WORKDIR} to trigger a new run:

    git push gitea main

  Tear it down when you are finished:

    ${SCRIPT_DIR}/setup.sh --down

EOF
