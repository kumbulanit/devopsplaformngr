# Lab 00 — Environment Setup

**Duration:** 45 minutes  
**Prerequisites:** A laptop with internet access and administrator rights.

## Objectives

- Verify or install the toolchain used in the course.
- Confirm Docker, Git, Python and Kubernetes tools are working.
- Build and run the sample app locally to validate your environment.

## Required Software

| Tool                | Minimum Version | Purpose                              |
|---------------------|-----------------|--------------------------------------|
| Git                 | 2.40            | Source control                       |
| Docker Desktop / Engine | 24.x        | Container runtime                    |
| Docker Compose      | 2.20            | Multi-container local orchestration  |
| kind                | 0.22            | Local Kubernetes cluster             |
| kubectl             | 1.28            | Kubernetes CLI                       |
| Terraform           | 1.6             | Infrastructure as Code               |
| Python              | 3.10            | Sample app runtime                   |
| VS Code (recommended) | latest        | Editor and terminal                  |

## Installation Instructions

### macOS (Homebrew)

```bash
brew install git docker --cask docker
brew install docker-compose kind kubectl terraform python
```

> **Note:** Docker Desktop must be launched from Applications after installation.

### Windows (winget)

```powershell
winget install Git.Git
winget install Docker.DockerDesktop
winget install Kubernetes.kind
winget install Kubernetes.kubectl
winget install Hashicorp.Terraform
winget install Python.Python.3.12
```

### Linux (Ubuntu 24.04 LTS recommended)

These instructions are tested on the latest Ubuntu LTS release (Noble 24.04) and should also work on recent Debian-based distributions.

For a one-shot Ubuntu 24.04 setup, run the lab-local helper script:

```bash
cd labs/lab00-environment-setup
chmod +x setup-ubuntu24.sh
./setup-ubuntu24.sh
```

This wrapper calls the repository installer in `lab-setup/install-ubuntu24.sh` and installs the base tooling, Docker Engine with the Compose plugin, kind, kubectl, Terraform, and the sample app dependencies in `labs/app/.venv`.

If you prefer the manual steps, use the following commands:

```bash
# Update package index and install base tooling
sudo apt-get update
sudo apt-get install -y git curl ca-certificates gnupg lsb-release

# Docker Engine and Docker Compose v2 plugin
sudo apt-get install -y docker.io docker-compose-v2
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
# Log out and back in for the docker group to take effect.

# kind
ARCH=$(dpkg --print-architecture)
curl -Lo ./kind "https://kind.sigs.k8s.io/dl/v0.23.0/kind-linux-${ARCH}"
chmod +x ./kind && sudo mv ./kind /usr/local/bin/kind

# kubectl
curl -LO "https://dl.k8s/release/$(curl -L -s https://dl.k8s/release/stable.txt)/bin/linux/${ARCH}/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl

# terraform
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update && sudo apt-get install -y terraform
```

## Verification Steps

Run each command and confirm the output looks similar.

```bash
# Git
git --version
# Expected: git version 2.40.x or higher

# Docker
docker --version
docker run --rm hello-world

# Docker Compose
docker compose version

# kind
kind version

# kubectl
kubectl version --client

# Terraform
terraform -version

# Python and pip
python3 --version
python3 -m pip --version
```

## Run the Sample App Natively

```bash
cd labs/app
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

In another terminal:

```bash
curl http://localhost:8000/health
# Expected: {"status":"ok","env":"development","build_id":"local"}

curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"item":"coffee","quantity":2,"price":3.5}'
```

Stop the server with `Ctrl+C`.

## Create a kind Cluster (Preview)

```bash
kind create cluster --name devops-course
kubectl get nodes
# Expected: one Ready control-plane node
kind delete cluster --name devops-course
```

## Troubleshooting

| Symptom | Likely Fix |
|---------|------------|
| `docker: Cannot connect to daemon` | Start Docker Desktop / service: `sudo systemctl start docker` |
| `kind create cluster` hangs | Ensure Docker has at least 4 GB RAM allocated. |
| `terraform` not found | Reinstall or add to PATH; use `tfenv` for version management. |
| Port 8000 already in use | Kill the process or run on a different port (`--port 8080`). |

## Completion Checklist

- [ ] All tools installed and versions verified.
- [ ] `docker run hello-world` succeeded.
- [ ] Sample app responds to `/health` and `/orders`.
- [ ] A kind cluster was created and deleted successfully.

## Stretch Goal

Install `act` so you can run GitHub Actions workflows locally:

```bash
brew install act        # macOS
choco install act-cli   # Windows
```
