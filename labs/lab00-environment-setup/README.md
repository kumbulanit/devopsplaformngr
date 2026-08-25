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

The script is **safe to run again at any time**: it checks each component and
installs only what is missing, so a re-run on a healthy VM downloads nothing.
If a tool goes missing later in the course, re-running it is the fix.

First, find the repository and remember where it is. Every later lab starts
from this directory, and the path differs depending on how the VM was
prepared:

```bash
# if the instructor pre-provisioned the VM, locate the repo:
find ~ -maxdepth 3 -name lab-setup -type d 2>/dev/null
```

That prints something like `/home/student/devops-course/lab-setup` — the
course repository is the directory **containing** `lab-setup`. Store it once
so every lab can use `cd "$COURSE_HOME"`:

```bash
cd /home/student/devops-course          # <- the directory the find printed, minus /lab-setup
echo "export COURSE_HOME=$(pwd)" >> ~/.bashrc
export COURSE_HOME=$(pwd)
echo "$COURSE_HOME"                     # sanity check: prints the repo path
```

Then install the toolchain:

```bash
./lab-setup/install-ubuntu24.sh
```

The script installs: Git, Docker Engine + Compose plugin, kind, kubectl,
Terraform, Trivy, Conftest, `act` (runs GitHub Actions workflows locally in
Lab 04), tmux, jq, Python 3 with the sample-app virtual environment in
`labs/app/.venv`. It also pre-pulls the large images the labs need — the
Trivy vulnerability database and the `act` runner image — so no lab waits on
classroom Wi-Fi.

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

- [ ] `echo "$COURSE_HOME"` prints the course repository path.
- [ ] `check-environment.sh` reports all required checks PASS.
- [ ] Sample app responds on `http://localhost:8000/health`.
- [ ] `pytest` reports 5 passed.
- [ ] A kind cluster was created and deleted.
- [ ] You can split, switch and detach tmux panes.
- [ ] `act --version` works (Lab 04 runs pipelines locally with it).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `permission denied` on `docker ...` | You are not in the `docker` group yet: `newgrp docker`, or log out/in. |
| `docker: Cannot connect to daemon` | The daemon is stopped: `sudo systemctl start docker` (see *Is Docker running?* below). |
| `kind create cluster` hangs | Check VM resources: `free -h` (needs ~6 GB RAM) and `df -h /` (needs ~15 GB free). |
| Port 8000 already in use | `sudo ss -ltnp 'sport = :8000'` to find the process, or use `--port 8080`. |
| `pytest: command not found` | Activate the venv first: `source labs/app/.venv/bin/activate`. |

## Is Docker Running?

Almost every lab needs the Docker daemon, and it fails in two different ways
that need two different fixes. Check in this order:

```bash
docker version        # shows Client AND Server — if Server is missing, the daemon is not reachable
docker info           # one command that either works or tells you exactly why
systemctl is-active docker    # running / inactive / failed
```

Then act on what you saw:

```bash
# daemon stopped -> start it, and make it start at boot
sudo systemctl start docker
sudo systemctl enable docker
sudo journalctl -u docker -n 30 --no-pager    # if it refuses to start

# "permission denied" -> the daemon is fine, your session is not in the group
newgrp docker            # this shell only
# or log out and back in, after: sudo usermod -aG docker $USER
```

Prove it end to end:

```bash
docker run --rm hello-world
```

`./lab-setup/check-environment.sh` runs these checks for you and prints a
**Docker daemon diagnosis** block naming the cause and the fix.

## Stretch Goal

Confirm the Lab 04 toolchain is ready to run a pipeline on this VM — no
GitHub account required:

```bash
act --version
act -l -W labs/lab04-cicd-github-actions/.github/workflows/ci.yml
```

The second command lists the jobs `act` found in the Lab 04 workflow. If the
runner image was pre-pulled during install, Lab 04 will start in seconds:

```bash
docker image ls catthehacker/ubuntu
```
