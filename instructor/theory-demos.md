# Theory Demos — the "very basic" hands-on for Modules 1–9

Each theory module gets **one small demo or exercise (5–15 min)** so
concepts land without turning the module into a lab. Everything runs on the
participant's Ubuntu VM localhost (or on paper). The three big workshops
(`workshops/`) remain the real hands-on.

| Module | Demo | Time | Type |
|--------|------|------|------|
| 1 | Preflight check together | 5 min | everyone |
| 2 | Westrum self-assessment | 10 min | paper/pairs |
| 3 | Toolchain mapping + DORA estimate | 15 min | pairs |
| 4 | Ansible idempotence, live | 10 min | everyone |
| 5 | Read a real workflow file | 10 min | pairs |
| 6 | What a container is, in 6 commands | 10 min | instructor |
| 7 | Scan + one policy | 10 min | everyone |
| 8 | Mini incident on the dashboard | 15 min | everyone |
| 9 | Platform canvas | 25 min | groups |

---

## Module 1 — Preflight check (5 min, everyone)

```bash
cd ~/devopsplatformengr
./lab-setup/check-environment.sh
```

Everyone confirms an all-PASS table. Frame it: *this is the course's first
automated feedback loop — a machine telling you you're ready, instead of
finding out mid-lab.*

## Module 2 — Westrum self-assessment (10 min, paper)

Privately score your organisation 1 (pathological) – 3 (generative) on:

1. When someone brings bad news, what happens to them?
2. After a failure, is the first question "who?" or "how?"
3. Is information shared proactively or hoarded as leverage?
4. Are risks/near-misses reported before they become incidents?
5. Is cross-team collaboration easy or political?

Pairs: share ONE concrete behaviour that would move one answer one level.
Debrief 3 answers to the room. No company names required.

## Module 3 — Toolchain mapping + DORA estimate (15 min, pairs)

On paper or a shared doc: map your organisation's tools onto the categories
(SCM / CI/CD / artifacts / IaC / config mgmt / runtime / secrets /
observability / incident). Mark gaps and duplicates. Then estimate your four
DORA numbers. Instructor collects a show of hands on lead time
(< 1 day / < 1 week / < 1 month / longer) — discuss the spread.

## Module 4 — Ansible idempotence, live (10 min, everyone)

```bash
cd ~/devopsplatformengr/labs/lab05-iac-terraform/ansible-bonus
sudo apt-get install -y ansible   # pre-baked VMs already have it
ansible-playbook site.yml         # watch: changed=N
ansible-playbook site.yml         # watch: changed=0  <- the lesson
ansible-playbook site.yml --check --diff   # plan, Ansible-style
```

One minute of output teaches idempotence better than any slide.
(Full Terraform loop comes in Workshop 3.)

## Module 5 — Read a real workflow (10 min, pairs)

No execution — pure reading, as preparation for Workshop 1:

```bash
less ~/devopsplatformengr/labs/lab04-cicd-github-actions/.github/workflows/ci.yml
```

Pairs answer: 1) Draw the job graph — what runs in parallel? 2) Which Trivy
step can fail the build and why does it use `ignore-unfixed`? 3) What do
`permissions: contents: read` and `@0.28.0` protect against?

## Module 6 — What a container is, in 6 commands (10 min, instructor demo)

```bash
docker run -d --name demo -p 18080:8000 order-service:lab02
docker exec demo ps aux                # it's just processes...
ps aux | grep uvicorn                  # ...visible from the host!
docker exec demo whoami                # appuser, not root
docker stats --no-stream demo          # cgroups: the meter
docker rm -f demo
```

Narrate: same kernel, namespaced view, cgroup limits — "containers are
processes wearing isolation." (Full build/deploy is Workshop 2.)

## Module 7 — Scan + one policy (10 min, everyone)

```bash
cd ~/devopsplatformengr
trivy image --severity HIGH,CRITICAL order-service:lab02        # triage one finding aloud
conftest test labs/lab06-kubernetes-kind/deployment-order.yaml \
  --policy labs/lab07-devsecops/policy                          # FAILS (no label)
kubectl kustomize labs/lab06-kubernetes-kind | \
  conftest test - --policy labs/lab07-devsecops/policy          # PASSES (rendered)
```

The raw-vs-rendered contrast is the punchline: *test what ships.*
(Full Lab 07 is a self-paced extra.)

## Module 8 — Mini incident (15 min, everyone)

```bash
cd ~/devopsplatformengr/labs/lab08-observability
docker compose -f docker-compose.observability.yml up -d --build
# generate traffic:
for i in {1..30}; do curl -s -X POST http://localhost:8080/orders \
  -H "Content-Type: application/json" -d '{"item":"mocha","quantity":1,"price":5.0}' >/dev/null; done
```

Open `http://localhost:9090` (targets) and `http://localhost:3000`
(admin/admin). **Then the instructor quietly runs:**

```bash
docker stop payment-service-obs
```

The room: notice (payment status `unavailable`), localise (Prometheus target
DOWN), confirm (logs), recover (`docker start payment-service-obs`), and
write a 5-line blameless postmortem together. Tear down after:

```bash
docker compose -f docker-compose.observability.yml down --volumes
```

(Full Lab 08 incl. SLO exercise is a self-paced extra.)

## Module 9 — Platform canvas (25 min + debrief, groups)

Use [`instructor/platform-canvas.md`](platform-canvas.md). Groups of 3–4
design a platform for an organisation someone at the table knows; 2-minute
presentations; debrief boxes 8 (metrics) and 9 (what we will NOT do).
