#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "${SCRIPT_DIR}/.." && pwd)
LABS_DIR="${REPO_ROOT}/labs"

if [[ ! -d "${LABS_DIR}" ]]; then
  echo "labs directory not found: ${LABS_DIR}" >&2
  exit 1
fi

create_lab() {
  local slug="$1"
  local title="$2"
  local lab_dir="${LABS_DIR}/${slug}"

  if [[ -d "${lab_dir}" ]]; then
    echo "[lab-setup] Existing lab directory detected: ${slug}"
    return 0
  fi

  mkdir -p "${lab_dir}"
  cat > "${lab_dir}/README.md" <<EOF
# ${title}

This lab directory was scaffolded by \`lab-setup/create-labs.sh\`.

## Suggested content

- Add the lab objectives.
- Document the setup and any prerequisites.
- Include step-by-step exercises and validation commands.
EOF

  cat > "${lab_dir}/.gitkeep" <<'EOF'
EOF

  echo "[lab-setup] Created ${slug}"
}

create_lab "lab00-environment-setup" "Lab 00 — Environment Setup"
create_lab "lab01-git-collaboration" "Lab 01 — Git Collaboration"
create_lab "lab02-docker-basics" "Lab 02 — Docker Basics"
create_lab "lab03-compose-microservices" "Lab 03 — Compose Microservices"
create_lab "lab04-cicd-github-actions" "Lab 04 — CI/CD with GitHub Actions"
create_lab "lab05-iac-terraform" "Lab 05 — IaC with Terraform"
create_lab "lab06-kubernetes-kind" "Lab 06 — Kubernetes with kind"
create_lab "lab07-devsecops" "Lab 07 — DevSecOps"
create_lab "lab08-observability" "Lab 08 — Observability"
