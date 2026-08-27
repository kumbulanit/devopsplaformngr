# Running the Labs on Windows

## The 30-second version

Open **Ubuntu-24.04** from the Start menu and work there. Every command in
every lab is identical to the Linux instructions — you are running Linux.

```bash
cd "$COURSE_HOME"
./lab-setup/check-environment.sh
```

Not set up yet? See [`../lab-setup/WINDOWS.md`](../lab-setup/WINDOWS.md).

---

## The four things that differ

**1. Which terminal.** Always the Ubuntu one. If your prompt looks like
`PS C:\Users\you>` you are in PowerShell — close it and open Ubuntu.

**2. Where your files live.** In `~/devops-course` inside Ubuntu. Never work
under `/mnt/c/`: it is far slower and breaks the file permissions Docker and
kind rely on.

**3. Browser links.** WSL2 forwards published ports, so every URL a lab gives
you works in your Windows browser unchanged:

| Lab step | Open on Windows |
|---|---|
| Compose stack (Day 2 Part B) | <http://localhost:8080> |
| Pipeline deployment (Day 1 Part C) | <http://localhost:8081> |
| Terraform service (Day 1 Part E) | <http://localhost:8090> |
| kind NodePort (Day 2 Part C) | <http://localhost:30080> |
| Prometheus (Day 2 Part E) | <http://localhost:9090> |
| Grafana (Day 2 Part E) | <http://localhost:3000> |
| Gitea pipeline UI (Day 1 Part H) | <http://localhost:3001> |

**4. Editing files.** You never have to — every change in every lab is a
paste-able command. If you want to look around, install VS Code on Windows
with the **WSL** extension and run `code .` from your Ubuntu terminal.

---

## Per-lab notes

**Lab Day 1** — no differences. `act`, Terraform and Ansible all run inside
Ubuntu. Part H's Gitea UI opens at <http://localhost:3001> in your Windows
browser.

**Lab Day 2** — no differences. kind runs inside Ubuntu; the cluster's
NodePort reaches your Windows browser at <http://localhost:30080>. If the
cluster is slow to create, give WSL more memory (see below) rather than
retrying.

**Memory.** kind plus the observability stack want ~6 GB. That is set for you
in `%UserProfile%\.wslconfig`. To change it, edit that file on Windows and
then, in PowerShell:

```powershell
wsl --shutdown
```

Reopen Ubuntu afterwards.

---

## Quick fixes

| Symptom | Fix |
|---------|-----|
| `Cannot connect to the Docker daemon` | From PowerShell: `wsl --shutdown`, then reopen Ubuntu. If it persists, check `grep systemd /etc/wsl.conf` inside Ubuntu. |
| `permission denied` on docker | `newgrp docker`, or close and reopen the Ubuntu window. |
| `localhost:PORT` does nothing in the browser | Check it is published (`docker ps`), then `wsl --shutdown` and reopen. |
| Everything crawls | You are working under `/mnt/c/`. Move to `~/devops-course`. |
| kind cluster never becomes ready | Raise memory in `.wslconfig`, `wsl --shutdown`, try again. |
| A tool is missing | `cd "$COURSE_HOME" && ./lab-setup/install-ubuntu24.sh` — it installs only what is absent. |

---

## Appendix: no WSL at all

If your machine genuinely cannot run WSL2 and you have Docker Desktop, the
container, Kubernetes and scanning parts of **Lab Day 2** can be done in
PowerShell. **Lab Day 1 Part F (Ansible) cannot** — Windows cannot be an
Ansible control node — and the shell-based steps need translating as you go.

Install the tools:

```powershell
winget install -e --id Kubernetes.kind
winget install -e --id Kubernetes.kubectl
winget install -e --id Hashicorp.Terraform
winget install -e --id AquaSecurity.Trivy
winget install -e --id nektos.act
```

### Command translations

| Linux (the labs) | PowerShell |
|---|---|
| `curl -s URL` | `curl.exe -s URL` (plain `curl` is an alias for `Invoke-WebRequest`) |
| `... \` line continuation | `` ... ` `` (backtick) |
| `echo "exit: $?"` | `Write-Host "exit: $LASTEXITCODE"` |
| `for i in $(seq 1 20); do X; done` | `1..20 \| ForEach-Object { X }` |
| `cat > f <<'EOF' ... EOF` | `@' ... '@ \| Set-Content f` |
| `sed -i 's/a/b/' f` | `(Get-Content f) -replace 'a','b' \| Set-Content f` |
| `grep X f` | `Select-String X f` |
| `... \| jq` | `... \| ConvertFrom-Json \| ConvertTo-Json` |
| `$COURSE_HOME` | `$env:COURSE_HOME` |
| `-v "$PWD":/work` | `-v "${PWD}:/work"` |

### Lab Day 2 Part A–D in PowerShell

```powershell
cd $env:COURSE_HOME

# Part A - build and inspect the image
docker build -t order-service:day2 -f labs/app/Dockerfile labs/app
docker images order-service
docker run -d --name day2-order -p 8000:8000 order-service:day2
Start-Sleep -Seconds 8
curl.exe -s localhost:8000/health
docker exec day2-order id        # uid=1001(appuser)
docker rm -f day2-order

# Part B - two services with Compose
cd labs/app
docker compose up -d --build
Start-Sleep -Seconds 10
curl.exe -s -X POST localhost:8080/orders -H "content-type: application/json" `
  -d '{\"item\":\"latte\",\"quantity\":2,\"price\":4.0}'
docker compose down
cd $env:COURSE_HOME

# Part C - Kubernetes
kind create cluster --name devops-course --config labs/lab06-kubernetes-kind/kind-config.yaml
docker build -t order-service:lab02   -f labs/app/Dockerfile         labs/app
docker build -t payment-service:lab02 -f labs/app/Dockerfile.payment labs/app
kind load docker-image order-service:lab02 payment-service:lab02 --name devops-course
kubectl apply -k labs/lab06-kubernetes-kind/
kubectl wait --for=condition=available --timeout=180s deployment/order-service
curl.exe -s localhost:30080/health

kubectl scale deployment/order-service --replicas=4
kubectl rollout undo deployment/order-service
kubectl get endpoints order-service

# Part D - scanning and policy
trivy image --severity HIGH,CRITICAL order-service:lab02
trivy image --severity CRITICAL --ignore-unfixed --exit-code 1 order-service:lab02
Write-Host "exit code: $LASTEXITCODE"

kubectl kustomize labs/lab06-kubernetes-kind/ | `
  docker run --rm -i -v "${PWD}/labs/lab07-devsecops/policy:/policy" `
  openpolicyagent/conftest:latest test - --policy /policy

# clean up
kind delete cluster --name devops-course
```

**What you lose on this path:** Ansible entirely, the `act` pipeline steps
that assume a Linux shell, and the Gitea UI setup script. Tell your instructor
so they can pair you with someone on WSL for those parts.
