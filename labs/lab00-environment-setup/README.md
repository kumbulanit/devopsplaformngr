# Lab 00 — Environment Setup & Verification

**Duration:** 30 minutes
**Environment:** your personal **Ubuntu 24.04 VM**. Every lab in this course
runs on this VM and every URL is `http://localhost:...` on it.
**Prerequisites:** sudo rights on the VM and internet access.

## Objectives

- Install (or verify) the complete course toolchain **with one script**.
- Prove the environment works with the automated preflight check.
- Run the sample application natively and call it on localhost.
- Learn the two terminal habits used all course: `tmux` and `curl`.

## Part A — Install the Toolchain (one script)

Everything the course needs is installed by a single script. If your
instructor pre-provisioned the VM this has already been run — skip to Part B.

```bash
cd ~/devopsplatformengr        # wherever you cloned the course repository
./lab-setup/install-ubuntu24.sh
```

The script installs: Git, Docker Engine + Compose plugin, kind, kubectl,
Terraform, Trivy, Conftest, tmux, jq, Python 3 with the sample-app virtual
environment in `labs/app/.venv`.

> **Important:** the script adds you to the `docker` group. Group membership
> only applies to **new** sessions — log out and back in, or run:
>
> ```bash
> newgrp docker
> ```

Preview what the script would do without changing anything:

```bash
./lab-setup/install-ubuntu24.sh --dry-run
```

## Part B — Preflight Check

One command tells you whether you are ready for the whole course:

```bash
./lab-setup/check-environment.sh
```

Expected: a table where every required row shows **PASS**, ending with
`RESULT: all required checks passed`. If anything shows FAIL, fix it now —
every later lab depends on this.

## Part C — Two Terminals with tmux

Many labs need one terminal running a server and another running `curl`.
On this VM we use `tmux`:

```bash
tmux new -s lab
```

| Keys | Action |
|------|--------|
| `Ctrl+b` then `%` | Split the window into two panes |
| `Ctrl+b` then `←`/`→` | Move between panes |
| `Ctrl+b` then `d` | Detach (session keeps running) |
| `tmux attach -t lab` | Re-attach |

Keep this session open — you will use both panes in Part D.

## Part D — Run the Sample App Natively

In the **left pane**:

```bash
cd labs/app
source .venv/bin/activate
uvicorn main:app --port 8000
```

In the **right pane**:

```bash
curl http://localhost:8000/health
# Expected: {"status":"ok","env":"development","build_id":"local"}

curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"item":"coffee","quantity":2,"price":3.5}'
# Expected: an order with a payment status of "unavailable"
# (the payment service is not running yet — that is Lab 03's job)
```

Run the unit tests, then stop the server with `Ctrl+C` in the left pane:

```bash
cd labs/app && source .venv/bin/activate
pytest
# Expected: 5 passed
```

## Part E — Kubernetes Preview

```bash
kind create cluster --name devops-course --config labs/lab06-kubernetes-kind/kind-config.yaml
kubectl get nodes
# Expected: one Ready control-plane node
kind delete cluster --name devops-course
```

## Completion Checklist

- [ ] `check-environment.sh` reports all required checks PASS.
- [ ] Sample app responds on `http://localhost:8000/health`.
- [ ] `pytest` reports 5 passed.
- [ ] A kind cluster was created and deleted.
- [ ] You can split, switch and detach tmux panes.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `permission denied` on `docker ...` | You are not in the `docker` group yet: `newgrp docker`, or log out/in. |
| `docker: Cannot connect to daemon` | `sudo systemctl start docker` |
| `kind create cluster` hangs | Check VM resources: `free -h` (needs ~6 GB RAM) and `df -h /` (needs ~15 GB free). |
| Port 8000 already in use | `sudo ss -ltnp 'sport = :8000'` to find the process, or use `--port 8080`. |
| `pytest: command not found` | Activate the venv first: `source labs/app/.venv/bin/activate`. |

## Stretch Goal

Install `act` to run GitHub Actions workflows locally in Lab 04:

```bash
curl -fsSL https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash -s -- -b /usr/local/bin
act --version
```
