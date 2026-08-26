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



Four jobs, and `act -l` shows them in four stages — each one waits for the
one before it:

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

- [ ] `act -l` shows four jobs across four stages
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

## Part H — See the Pipeline in a Web UI (30 min)

`act` is a command-line tool: no web interface. To *watch* a pipeline — jobs,
steps, live logs, re-run buttons — you need something that hosts runs. This
part gives you that on localhost, running **the same `ci-cd.yml` you already
have**, so every box on the screen maps to a block in your YAML.

**1. Start it — one script:**

```bash
cd "$COURSE_HOME"/labs/lab-day1/pipeline-ui
./setup.sh --push
```

That starts Gitea (a self-hosted git forge) plus its Actions runner, creates
a user, registers the runner, creates the repository, and pushes `/tmp/day1`
to it — which triggers a run. It is safe to re-run; every step checks first.

**2. Open the UI:**

<http://localhost:3001/lab/order-service/actions> — log in as
`lab` / `labpass123`.

**3. Read the screen against the file.** Open `ci-cd.yml` beside the browser:

| In the YAML | On the screen |
|-------------|---------------|
| `name: CI/CD — Order Service` | the run title |
| each `jobs:` key (`test`, `build`, `security-scan`, `deploy`) | one row in the left-hand job list |
| `needs:` | why `deploy` sits idle until the two above it are green |
| each `- name:` under `steps:` | one collapsible line in the log pane |
| `run:` contents | the commands echoed in that step's log |
| a step's exit code | the ✅ / ❌ on that line |

Click `deploy`, expand **Smoke test**, and watch it poll until the container
answers. That is the same output `act` printed in Part C — the pipeline did
not change, only where you are watching it from.

**4. Trigger another run and watch it live:**

```bash
cd /tmp/day1
sed -i 's/"day1-demo"/"day1-demo-v2"/' labs/app/main.py
git commit -qam "feat: bump the environment label"
git push gitea main
```

Refresh the Actions tab — a new run appears and moves through the stages.

**5. Tear it down:**

```bash
cd "$COURSE_HOME"/labs/lab-day1/pipeline-ui
./setup.sh --down
```

### Why this one

Gitea Actions **uses act underneath**, so the workflow file is identical
across all three places you can run it — your terminal, this UI, or GitHub.
Nothing about the pipeline is UI-specific.

If you want a UI for **deployments** rather than builds, Argo CD does the same
job for Kubernetes and can be installed into the kind cluster from Lab Day 2.
If your organisation runs **Jenkins**, its stage view is the equivalent screen
— the deck carries the matching `Jenkinsfile`.

### Expectations and troubleshooting

| Symptom | What to do |
|---------|------------|
| First run is slow | The runner reuses the act image the installer pre-pulled, but the job still pulls the Trivy image once. Later runs are much faster. |
| A job hangs with no log output | The runner lost its connection to Gitea. `docker restart lab-runner`, then re-run the job from the UI. |
| Runner log shows `lookup gitea ... i/o timeout` | Same cause — Docker's embedded DNS. Restart the runner. |
| `Repository already exists` | Expected on re-run; the script continues. |
| Port 3001 in use | Change the published port in `pipeline-ui/docker-compose.yml`. |

> **Status of this part:** the setup, runner registration, push, run trigger
> and live job execution were verified. A complete four-job run through the
> UI has not yet been confirmed end to end on a clean Ubuntu VM — do one
> practice run before teaching it, and keep Part C (`act`) as the path you
> rely on in class.

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
