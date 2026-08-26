# Lab Day 1 — Get a Change to Production Safely

**Duration:** ~2h15 · **Runs entirely on your VM** · No GitHub account needed

One continuous story: you take the order service, put it through a pipeline
that tests, builds and security-scans it, prove the gate really works, then
create its infrastructure from code — twice, to see idempotence.

| Part | What you do | Time | Topic |
|------|-------------|------|-------|
| A | Run the app and its tests | 10 min | the thing we are shipping |
| B | Pipeline: test → build → scan, locally with `act` | 40 min | CI/CD |
| C | Break the security gate, then fix it | 20 min | DevSecOps |
| D | Terraform: plan → apply → drift → destroy | 40 min | IaC |
| E | Ansible: run it twice, see `changed=0` | 20 min | config management |
| F | Wrap up: what you built | 5 min | — |

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

## Part B — The Pipeline, on Your VM (40 min)

`act` runs GitHub Actions workflows locally, in a container. Same YAML a
hosted runner would execute — 30-second feedback, no account.

**1. Put the workflow where a runner looks for it:**

```bash
cd "$COURSE_HOME"
mkdir -p .github/workflows
cp labs/lab04-cicd-github-actions/.github/workflows/ci.yml .github/workflows/ci.yml
```

**2. Read it before you run it** — open `.github/workflows/ci.yml` and find:

- three jobs: `test`, `build`, `security-scan`
- `needs: test` — the dependency that orders the graph
- `permissions: contents: read` — least-privilege token
- Trivy appearing **twice**: a report step (`exit-code: "0"`) and a gate step
  (`exit-code: "1"` + `ignore-unfixed: true`)

**3. List what act found:**

```bash
act -l
```

**4. Run the jobs one at a time:**

```bash
act -j test
act -j build
act -j security-scan
```

> First run only: act pulls a runner image (~1 GB) unless it was pre-pulled
> during setup. After that, seconds.

**5. Run the whole graph the way a push would:**

```bash
act push
```

Watch `test` finish before `build` and `security-scan` start.

**Checkpoint:**

- [ ] `test` green — 5 passed
- [ ] `build` produced an image — `docker images order-service`
- [ ] `security-scan` printed a CVE table and still passed

---

## Part C — Prove the Gate Works (20 min)

A gate you have never seen fail is a gate you do not understand.

**1. Make it strict.** In `.github/workflows/ci.yml`, in the **Trivy gate**
step (the second one, with `exit-code: "1"`), change:

```yaml
          severity: CRITICAL,HIGH
          ignore-unfixed: false
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

**4. Put it back** (`severity: CRITICAL`, `ignore-unfixed: true`) and confirm
it is green:

```bash
act -j security-scan
```

**5. Now break something real** — in `labs/app/test_app.py` change an
expected value so a test fails, then:

```bash
act -j test          # red: the pipeline caught it
```

Undo the change and re-run to get back to green.

**Checkpoint:**

- [ ] You saw the gate fail and restored it
- [ ] You saw a failing test stop the pipeline
- [ ] You can explain report-vs-gate in one sentence

---

## Part D — Infrastructure as Code (40 min)

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

## Part E — Configuration Management (20 min)

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

## Part F — What You Built (5 min)

In 2 hours you have:

| | Practice | Module |
|---|---|---|
| ✔ | A pipeline that tests, builds and scans every change | 5 |
| ✔ | A security gate that genuinely stops the line — and stays fair | 5 + 7 |
| ✔ | Infrastructure created, re-run safely, and drift-corrected | 4 |
| ✔ | Configuration converged idempotently | 4 |

**Tomorrow** the same application gets containerised properly, deployed to
Kubernetes, scanned against policy, and put under an SLO with alerts.

**Clean up if you are done for the day:**

```bash
cd "$COURSE_HOME" && rm -f .github/workflows/ci.yml
docker ps -aq | xargs -r docker rm -f
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
