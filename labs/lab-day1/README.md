# Lab Day 1 — Get a Change to Production Safely

**Duration:** ~2h15 · **Runs entirely on your VM** · No GitHub account needed

One continuous story: you take the order service, put it through a pipeline
that tests, builds and security-scans it, prove the gate really works, then
create its infrastructure from code — twice, to see idempotence.

| Part | What you do | Time | Topic |
|------|-------------|------|-------|
| A | Run the app and its tests | 10 min | the thing we are shipping |
| B | **Push a change** to a git remote | 10 min | source control |
| C | The pipeline runs: **test → build → scan → deploy** | 35 min | CI/CD |
| D | Break the security gate, then fix it | 20 min | DevSecOps |
| E | Terraform: plan → apply → drift → destroy | 40 min | IaC |
| F | Ansible: run it twice, see `changed=0` | 20 min | config management |
| G | Wrap up: what you built | 5 min | — |

Optional: **Part H** puts a real web UI in front of the same pipeline.

> **Everything starts from the repository root.** If `cd "$COURSE_HOME"` fails,
> set it first: `find ~ -maxdepth 4 -name lab-setup -type d`, then
> `export COURSE_HOME=<the directory containing lab-setup>`.

---

## Part A — The Application (10 min)

```bash
cd "$COURSE_HOME"
source labs/app/.venv/bin/activate
cd labs/app && pytest
```

Expected: **5 passed**.

Run it and look at what it exposes:

```bash
uvicorn main:app --port 8000 &
sleep 2
curl -s localhost:8000/health | jq
curl -s -X POST localhost:8000/orders \
  -H 'content-type: application/json' \
  -d '{"item":"latte","quantity":2,"price":4.0}' | jq
kill %1
```

The order comes back with a `payment` block — the order service called the
payment service to get it. Right now there is no payment service running, so
look at what `payment.status` says.

**Notice:** `/health` is what Kubernetes will probe tomorrow, and `/metrics`
is what Prometheus will scrape. Observability is built in, not bolted on.

---

## Part B — Push a Change (10 min)

A pipeline starts with a push, so let us make one. Everything stays on your
VM: a bare repository plays the role of the remote.

**1. Make a working copy with a remote** (never run `git init` inside the
course repo):

```bash
mkdir -p /tmp/day1 && cp -r "$COURSE_HOME"/labs /tmp/day1/
mkdir -p /tmp/day1/.github/workflows
cp "$COURSE_HOME"/labs/lab-day1/ci-cd.yml /tmp/day1/.github/workflows/
cd /tmp/day1
rm -rf labs/app/.venv labs/app/__pycache__ labs/lab05-iac-terraform/.terraform*

git init -qb main .
git config user.email "you@example.com"
git config user.name "Your Name"
git add -A && git commit -qm "Order service + CI/CD pipeline"

git init --bare -q /tmp/day1-remote.git
git remote add origin /tmp/day1-remote.git
git push -q origin main && echo "pushed to the remote"
```

**2. Now make the change you are going to ship** — add the service name to
the health endpoint. In `/tmp/day1/labs/app/main.py`, find the `health()`
function and change what it returns so `env` reads `"day1-demo"`:

```bash
cd /tmp/day1
sed -i 's/env=APP_ENV/env="day1-demo"/' labs/app/main.py
git diff --stat
```

**3. Commit and push it — the way every change should arrive:**

```bash
git checkout -b feature/health-env
git add labs/app/main.py
git commit -m "feat: report day1-demo as the environment"
git push -q origin feature/health-env && echo "branch pushed"

git checkout main
git merge --no-ff -q feature/health-env -m "Merge feature/health-env"
git push -q origin main && echo "merged to main - this is what triggers CI/CD"
```

**Checkpoint:**

- [ ] `git log --oneline --graph --all` shows the branch and the merge
- [ ] The remote has your commit: `git --git-dir=/tmp/day1-remote.git log --oneline -3`

---

## Part C — The Pipeline: Test → Build → Scan → Deploy (35 min)

`act` runs the workflow exactly as a hosted runner would — same YAML, your
machine, 30-second feedback, no account.

**1. See the shape of the pipeline before you run it:**

```bash
cd /tmp/day1
act -l          # jobs and the stage each one runs in
act --graph     # the dependency graph, drawn in the terminal
```

> **Does act have a web UI?** No — `act` is a command-line tool. It gives you
> `--graph` (above), live step-by-step output with ✅/❌ per step, and
> `--json` for machine-readable logs. If you want a **real pipeline web UI on
> your VM**, do Part H at the end: Gitea runs *this exact workflow file* and
> shows the runs, jobs, live logs and re-run buttons in a browser.



Four jobs, in three stages:

```
  test  →  build  →  security-scan  →  deploy
```

`deploy` declares `needs: [build, security-scan]`, so **nothing ships unless
the tests passed AND the scan passed**.

**2. Read `.github/workflows/ci-cd.yml`** and find:

- `on: push` — the trigger. Nobody starts this by hand.
- `needs:` on each job — the dependency graph you just drew.
- Trivy twice: a **report** (`--exit-code 0`) and a **gate** (`--exit-code 1`
  with `--ignore-unfixed`).
- The **smoke test** after deploy — a deploy that "succeeded" but serves
  errors is a failed deploy.

**3. Run the whole thing, the way your push would have:**

```bash
act push
```

> First run only: `act` pulls its runner image (~1 GB) unless the setup
> script pre-pulled it. After that, runs start in seconds.

Watch the order in the output: `test` completes, then `build`, then
`security-scan`, and only then `deploy`.

**4. Your change is now running — prove it:**

```bash
docker ps --filter name=day1-order --format '{{.Names}}	{{.Ports}}	{{.Status}}'
curl -s localhost:8081/health | jq
```

The `env` field should read **`day1-demo`** — the change you committed two
steps ago is now serving traffic, and every stage in between was automated.

**Checkpoint:**

- [ ] `act -l` shows four jobs across three stages
- [ ] `act push` ran test → build → scan → deploy in that order
- [ ] `curl localhost:8081/health` returns your change

---

## Part D — Prove the Gate Works (20 min)

A gate you have never seen fail is a gate you do not understand.

**1. Make it strict.** In `/tmp/day1/.github/workflows/ci-cd.yml`, find the
**Gate** step in the `security-scan` job and change its severity line so it
also fails on HIGH, and stop ignoring unfixable findings:

```bash
cd /tmp/day1
sed -i 's/--severity CRITICAL --ignore-unfixed/--severity CRITICAL,HIGH/' \
  .github/workflows/ci-cd.yml
```

**2. Re-run just the scan:**

```bash
act -j security-scan
```

It should now go **red**. Those findings were always there — the normal
settings filter them out because they are lower severity or have no fix.

**3. Discuss with your neighbour:**

- How many of these could a developer actually fix **today**?
- What happens to a team's respect for a red build if the gate blocks on
  things nobody can fix?
- Where would you set the threshold for this service, and why?

**4. Put it back and confirm it is green again:**

```bash
sed -i 's/--severity CRITICAL,HIGH/--severity CRITICAL --ignore-unfixed/' \
  .github/workflows/ci-cd.yml
act -j security-scan
```

**5. Now break something real** — in `/tmp/day1/labs/app/test_app.py` change
an expected value so a test fails, then:

```bash
act -j test          # red: the pipeline caught it
```

Undo the change and re-run to get back to green.

**Checkpoint:**

- [ ] You saw the gate fail and restored it
- [ ] You saw a failing test stop the pipeline — and `deploy` never ran
- [ ] You can explain report-vs-gate in one sentence

---

## Part E — Infrastructure as Code (40 min)

Same application, now with its infrastructure declared instead of clicked.

Terraform will start containers from images tagged `:lab02`, so build them
once (this is also your first look at the Dockerfiles you meet tomorrow):

```bash
cd "$COURSE_HOME"
docker build -t order-service:lab02   -f labs/app/Dockerfile         labs/app
docker build -t payment-service:lab02 -f labs/app/Dockerfile.payment labs/app
docker images | grep lab02
```

```bash
cd "$COURSE_HOME"/labs/lab05-iac-terraform
terraform init
```

**1. Read `main.tf`** — find the `docker_network`, the two `docker_container`
resources, and the line where one container references another. Nobody wrote
the creation order; Terraform derives it from that reference.

**2. Plan — the change record:**

```bash
terraform plan
```

Read the summary line: `Plan: N to add, 0 to change, 0 to destroy`. In
production this line is what a reviewer approves — and a destroy count you
did not expect is a stop signal.

**3. Apply, and check it really ran:**

```bash
terraform apply -auto-approve
docker ps --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'
curl -s localhost:8090/health | jq
```

The containers are named `tf-dev-order-service` and `tf-dev-payment-service`
(`tf-<environment>-<service>`), published on **8090** and **8091**.

**4. Idempotence — ask again what would change:**

```bash
terraform plan
```

Expected: **No changes. Your infrastructure matches the configuration.**
(Re-running `terraform apply` says `0 added, 0 changed, 0 destroyed` — the
same fact, said differently.)

**5. Drift — break it by hand, the way a 03:00 fix would:**

```bash
docker rm -f tf-dev-order-service
terraform plan          # Terraform now reports exactly what diverged
terraform apply -auto-approve
curl -s localhost:8090/health | jq   # back, without anyone remembering how
```

**6. Clean up:**

```bash
terraform destroy -auto-approve
```

**Checkpoint:**

- [ ] Second apply reported **No changes**
- [ ] You caused drift and Terraform detected and corrected it
- [ ] You can explain what the state file is for

---

## Part F — Configuration Management (20 min)

Terraform made infrastructure *exist*. Ansible makes an existing machine
*correct* — and proves the same idempotence idea in a different tool.

```bash
cd "$COURSE_HOME"/labs/lab05-iac-terraform/ansible-bonus
ansible-playbook site.yml
```

> The playbook targets this VM directly (`hosts: localhost`,
> `connection: local`) — no inventory file, no SSH.

Look at the **PLAY RECAP**: `changed=N`.

Now run exactly the same command again:

```bash
ansible-playbook site.yml
```

**PLAY RECAP: `changed=0`.** Nothing to do — reality already matches the
declaration. A shell script cannot tell you this.

Preview mode, which is what belongs in a change record:

```bash
ansible-playbook site.yml --check --diff
```

**Checkpoint:**

- [ ] Second run reported `changed=0`
- [ ] You can say when you would use Ansible instead of Terraform
      (*existence* vs *correctness*)

---

## Part G — What You Built (5 min)

In 2 hours you have:

| | Practice | Module |
|---|---|---|
| ✔ | A push that triggers test → build → scan → **deploy** | 5 |
| ✔ | A security gate that genuinely stops the line — and stays fair | 5 + 7 |
| ✔ | Infrastructure created, re-run safely, and drift-corrected | 4 |
| ✔ | Configuration converged idempotently | 4 |

**Tomorrow** the same application gets containerised properly, deployed to
Kubernetes, scanned against policy, and put under an SLO with alerts.

**Clean up if you are done for the day:**

```bash
docker rm -f day1-order 2>/dev/null
rm -rf /tmp/day1 /tmp/day1-remote.git
docker ps -aq | xargs -r docker rm -f      # everything, if you are finished
```

---

## Part H — Optional: Watch the Pipeline in a Web UI (30 min)

`act` has no web interface. **Gitea** does — and Gitea Actions runs the same
workflow file using act underneath, so nothing about your pipeline changes.
You get a browser view of runs, jobs, live logs and re-run buttons, entirely
on your VM.

**1. Start Gitea:**

```bash
mkdir -p /tmp/gitea && cd /tmp/gitea
cat > docker-compose.yml <<'EOF'
services:
  gitea:
    image: gitea/gitea:1.22
    container_name: lab-gitea
    environment:
      GITEA__server__ROOT_URL: http://localhost:3001/
      GITEA__actions__ENABLED: "true"
      GITEA__security__INSTALL_LOCK: "true"
    ports: ["3001:3000"]
    volumes: ["gitea-data:/data"]
volumes:
  gitea-data:
EOF
docker compose up -d
until curl -sf localhost:3001/api/healthz >/dev/null; do sleep 2; done
echo "Gitea is up on http://localhost:3001"
```

**2. Create a user and register a runner:**

```bash
docker exec -u git lab-gitea gitea admin user create \
  --admin --username lab --password labpass123 --email lab@example.com

TOKEN=$(docker exec -u git lab-gitea gitea actions generate-runner-token | tr -d '\r\n')

docker run -d --name lab-runner --network gitea_default \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e GITEA_INSTANCE_URL=http://gitea:3000 \
  -e GITEA_RUNNER_REGISTRATION_TOKEN="$TOKEN" \
  -e GITEA_RUNNER_NAME=lab-runner \
  gitea/act_runner:latest

docker logs lab-runner 2>&1 | grep -i "registered successfully"
```

**3. Create the repository and push to it:**

```bash
curl -s -u lab:labpass123 -X POST localhost:3001/api/v1/user/repos \
  -H 'content-type: application/json' \
  -d '{"name":"order-service","private":false}' -o /dev/null -w '%{http_code}\n'

cd /tmp/day1
git remote add gitea http://lab:labpass123@localhost:3001/lab/order-service.git
git push gitea main
```

**4. Watch it run in the browser:**

Open <http://localhost:3001/lab/order-service/actions> and log in as
`lab` / `labpass123`. You will see the run, its four jobs, and live logs —
click into `deploy` to watch the smoke test.

> **Be patient on the first run.** The runner downloads its own image (~1 GB)
> before the first job starts, so run 1 can take several minutes with nothing
> visible happening. Later runs start immediately.

**What this demonstrates:** the workflow file is portable. Same YAML, three
different places to run it — your terminal (`act`), a self-hosted forge with
a UI (Gitea), or GitHub. The pipeline is yours; the runner is a detail.

**Clean up:**

```bash
docker rm -f lab-runner
cd /tmp/gitea && docker compose down -v
```

---

## Going Deeper (self-paced)

Each part above is a condensed version of a full lab. Everything is still in
the repository, with more detail, more explanation and stretch goals:

| Part | Full lab |
|------|----------|
| A | `labs/lab00-environment-setup`, `labs/lab01-git-collaboration` |
| B, C | `labs/lab04-cicd-github-actions`, `labs/lab07-devsecops` |
| D, E | `labs/lab05-iac-terraform` (+ `ansible-bonus/`) |
| all | `labs/lab09-capstone` — the full golden path, end to end |

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `cd: $COURSE_HOME: No such file or directory` | `find ~ -maxdepth 4 -name lab-setup -type d`, then export `COURSE_HOME` to the directory containing it |
| `act: command not found` | Re-run `./lab-setup/install-ubuntu24.sh` — it installs only what is missing |
| `act` cannot reach Docker | `newgrp docker`, or log out and back in |
| `permission denied` on docker | Same — your session is not in the `docker` group yet |
| Port 8090/8091 already in use | `docker ps` then `docker rm -f <name>`, or `sudo ss -ltnp 'sport = :8090'` |
| `ansible-playbook: command not found` | Re-run `./lab-setup/install-ubuntu24.sh` (it now installs Ansible), or `sudo apt-get install -y ansible` |
| `terraform plan` errors on the provider | `terraform init` again; check the Docker daemon is running (`docker info`) |
