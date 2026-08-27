# Lab Day 2 — Run It Like a Service

**Duration:** ~3h · **Runs entirely on your VM** · Builds on Lab Day 1

Yesterday you got a change *to* production safely. Today you package it,
run it on Kubernetes, check it against policy, and put it under an SLO with
an alert that actually fires.

| Part | What you do | Time | Topic |
|------|-------------|------|-------|
| A | Build an image well: bad vs multi-stage | 30 min | containers |
| B | Two services talking, with Compose | 20 min | microservices |
| C | Kubernetes: deploy, probes, scale, roll back | 50 min | orchestration |
| D | Scan the image, gate the manifest with policy | 30 min | DevSecOps |
| E | Metrics, dashboard, SLO alert | 30 min | observability |
| F | Game day: break it — and discover you cannot see it | 20 min | reliability |
| G | Wrap up | 10 min | — |

> **On Windows?** Work inside the **Ubuntu-24.04** terminal (WSL2) — every
> command below is then identical, and the kind NodePort reaches your browser at http://localhost:30080.
> Setup: [`lab-setup/WINDOWS.md`](../../lab-setup/WINDOWS.md) · running the labs:
> [`labs/WINDOWS.md`](../WINDOWS.md)

> Start from the repository root: `cd "$COURSE_HOME"`. If that fails, run
> `find ~ -maxdepth 4 -name lab-setup -type d` and export `COURSE_HOME` to
> the directory containing `lab-setup`.

---

## Part A — Build an Image Well (30 min)

**1. Look at what we ship:**

```bash
cd "$COURSE_HOME"
cat labs/app/Dockerfile
```

Find these four decisions and be ready to say why each matters:

- `python:3.12-slim` rather than the full base image
- dependencies copied and installed **before** the application code
- a non-root `USER` (`appuser`, uid 1001) instead of root
- `CMD` in exec form (`["uvicorn", ...]`), not shell form

**2. Build it and look at the result:**

```bash
docker build -t order-service:day2 -f labs/app/Dockerfile labs/app
docker images order-service
docker history order-service:day2 | head
```

**3. Prove the cache works** — change one line of application code, rebuild,
and watch the dependency layers say `CACHED`:

```bash
echo "# touch" >> labs/app/main.py
docker build -t order-service:day2 -f labs/app/Dockerfile labs/app
git checkout labs/app/main.py
```

**4. Run it and prove it is not root:**

```bash
docker run -d --name day2-order -p 8000:8000 order-service:day2
until curl -sf localhost:8000/health >/dev/null; do sleep 1; done   # ~6s to start
curl -s localhost:8000/health | jq
docker exec day2-order id          # uid=1001(appuser), not 0
docker rm -f day2-order
```

**Checkpoint:**

- [ ] Image built, and the second build reused cached layers
- [ ] The container runs as `appuser` (uid 1001), not root
- [ ] You can name three things that make an image production-ready

---

## Part B — Two Services, One Network (20 min)

```bash
cd "$COURSE_HOME"/labs/app
docker compose up -d --build
docker compose ps
```

The order service is published on **8080**; the payment service has **no
published port** — it is reachable only inside the Compose network, by DNS
name.

```bash
until curl -sf localhost:8080/health >/dev/null; do sleep 1; done
curl -s localhost:8080/health | jq
curl -s -X POST localhost:8080/orders \
  -H 'content-type: application/json' \
  -d '{"item":"latte","quantity":2,"price":4.0}' | jq
```

Look at the `payment` block in the response: `"status": "approved"` means the
order service reached the payment service **by name** over the internal
network. Prove that name resolution is real:

```bash
docker compose exec order-service getent hosts payment-service
docker compose logs --tail=20 payment-service
```

Clean up before Kubernetes:

```bash
docker compose down
```

**Checkpoint:**

- [ ] An order was created, which means service-to-service calls worked
- [ ] You can explain why payment-service has no published port

---

## Part C — Kubernetes (50 min)

**1. Create the cluster** (the config forwards localhost:30080 into it):

```bash
cd "$COURSE_HOME"
kind create cluster --name devops-course \
  --config labs/lab06-kubernetes-kind/kind-config.yaml
kubectl get nodes
```

**2. Build and load the images** — kind has its own image store:

```bash
docker build -t order-service:lab02   -f labs/app/Dockerfile         labs/app
docker build -t payment-service:lab02 -f labs/app/Dockerfile.payment labs/app
kind load docker-image order-service:lab02 payment-service:lab02 --name devops-course
```

**3. Deploy, and watch it converge:**

```bash
kubectl apply -k labs/lab06-kubernetes-kind/
kubectl get pods -w        # Ctrl+C once both are Running
curl -s localhost:30080/health | jq
```

**4. Read the manifest** — `labs/lab06-kubernetes-kind/deployment-order.yaml`
— and find: `readinessProbe`, `livenessProbe`, `resources.requests/limits`,
`securityContext`. Ask yourself which of those you would have remembered.

**5. Self-healing — kill a pod and watch Kubernetes replace it:**

```bash
kubectl delete pod -l app=order-service --wait=false
kubectl get pods -w        # a replacement appears immediately
```

**6. Scale:**

```bash
kubectl scale deployment/order-service --replicas=4
kubectl get pods -l app=order-service
```

**7. Roll forward, then roll back** — the payoff of the whole module:

```bash
docker build -t order-service:v2 --build-arg BUILD_ID=v2 -f labs/app/Dockerfile labs/app
kind load docker-image order-service:v2 --name devops-course
kubectl set image deployment/order-service order=order-service:v2
kubectl rollout status deployment/order-service
curl -s localhost:30080/health | jq .build_id      # v2

kubectl rollout undo deployment/order-service
kubectl rollout status deployment/order-service
curl -s localhost:30080/health | jq .build_id      # back to the previous build
```

**8. The triage commands to keep:**

```bash
kubectl get endpoints order-service   # EMPTY = labels wrong or readiness failing
kubectl describe pod -l app=order-service | tail -20   # Events tell the story
kubectl logs deploy/order-service --tail=20
```

**Checkpoint:**

- [ ] A deleted pod was replaced automatically
- [ ] You rolled forward to v2 and back in one command each
- [ ] You can explain readiness vs liveness

---

## Part D — Security in the Pipeline (30 min)

**1. Scan the image you just deployed:**

```bash
cd "$COURSE_HOME"
trivy image --severity HIGH,CRITICAL order-service:lab02
```

Read the table. Now ask the only question that matters operationally:

```bash
trivy image --severity CRITICAL --ignore-unfixed --exit-code 1 order-service:lab02
echo "exit code: $?"      # 0 = nothing a developer can fix today
```

**2. Scan for secrets and misconfiguration:**

```bash
trivy fs --scanners secret labs/
trivy config labs/lab06-kubernetes-kind/
```

**3. Policy as code** — the institution's rules, as a test:

```bash
cat labs/lab07-devsecops/policy/no_latest_tag.rego
kubectl kustomize labs/lab06-kubernetes-kind/ | \
  conftest test - --policy labs/lab07-devsecops/policy
```

**4. Now violate the policy on purpose:**

```bash
kubectl kustomize labs/lab06-kubernetes-kind/ \
  | sed 's|order-service:lab02|order-service:latest|' \
  | conftest test - --policy labs/lab07-devsecops/policy
```

**FAIL** — because `:latest` is unreproducible. That is the rule enforcing
itself, identically, every time, without anyone remembering it.

**Checkpoint:**

- [ ] You saw the difference between a report scan and a gate scan
- [ ] You made a policy fail, and can explain what it protects against
- [ ] You can say where each of these runs: pipeline, admission, or both

---

## Part E — Observability (30 min)

**1. Free port 8080 first.** This stack publishes the order service on 8080,
the same port Part B used. If the Part B stack is still up, the new one
starts without a published port and you end up curling the *old* services —
with very confusing results in Part F:

```bash
cd "$COURSE_HOME"/labs/app && docker compose down
docker ps --filter publish=8080 --format '{{.Names}}'   # must print nothing
```

**2. Start the stack** (app + Prometheus + Grafana):

```bash
cd "$COURSE_HOME"/labs/lab08-observability
docker compose -f docker-compose.observability.yml up -d --build
until curl -sf localhost:8080/health >/dev/null; do sleep 3; done
docker compose -f docker-compose.observability.yml ps
```

**3. Generate some traffic:**

```bash
for i in $(seq 1 40); do
  curl -s -o /dev/null -X POST localhost:8080/orders \
    -H 'content-type: application/json' \
    -d '{"item":"latte","quantity":1,"price":4.0}'
done
curl -s localhost:8080/metrics | grep -E '^order_requests_total' | head
```

> **Give it two minutes.** Prometheus scrapes every 15s, so `rate()` needs two
> scrapes before it returns anything, and Grafana runs database migrations on
> first start — measured at **~80 seconds** on a 6 GB VM. If a query says "no
> data" or Grafana refuses the connection, wait and retry. That is normal, not
> broken.

**4. Query in Prometheus** — open <http://localhost:9090> and run:

```promql
rate(order_requests_total[1m])
```

```promql
sum(rate(order_requests_total{status=~"5.."}[5m]))
  /
sum(rate(order_requests_total[5m]))
```

The second query is your **error-rate SLI**. If your SLO is 99.9%, the budget
is 0.1% — about 43 minutes of failure per 30 days.

Sanity check from the command line if the UI looks empty:

```bash
curl -s 'localhost:9090/api/v1/targets?state=active' \
  | jq -r '.data.activeTargets[] | "\(.labels.job) \(.health)"'
```

All three targets (order-service, payment-service, prometheus) should be `up`.

**5. Grafana** — open <http://localhost:3000> (admin/admin), find the
pre-provisioned dashboard, and watch it move as you generate more traffic.

**Checkpoint:**

- [ ] Metrics visible in Prometheus
- [ ] Dashboard shows your traffic
- [ ] You can write the availability SLI query from memory

---

## Part F — Game Day (20 min)

Practise failure on a Tuesday morning instead of at 03:00 on a Sunday.

**0. Confirm the baseline first** — an order placed while payment-service is
still starting also reports `unavailable`, which would spoil the comparison:

```bash
curl -s -X POST localhost:8080/orders -H 'content-type: application/json' \
  -d '{"item":"latte","quantity":1,"price":4.0}' | jq -r .payment.status
```

Wait until that prints **`approved`** before continuing.

**1. Break the payment service** — the order service depends on it:

```bash
cd "$COURSE_HOME"/labs/lab08-observability
docker compose -f docker-compose.observability.yml stop payment-service
```

**2. Now order something and watch carefully:**

```bash
curl -s -X POST localhost:8080/orders -H 'content-type: application/json' \
  -d '{"item":"latte","quantity":1,"price":4.0}' | jq
```

**Look at the status code and the body separately.** The request returns
**HTTP 201 Created** — success, as far as any HTTP monitor is concerned. But
inside the body:

```json
"payment": { "status": "unavailable" }
```

Compare that with the `"status": "approved"` you saw when the stack was
healthy. **No payment is being taken, and nothing is reporting an error.**

**3. This is the most important five minutes of the day.** Discuss:

- An availability SLI built on 5xx responses shows **100% healthy** right now.
  Would you have known?
- Which signal *would* have caught it? (a business metric: approved payments
  per minute; a dependency health check; an alert on `status="unavailable"`)
- The service degraded gracefully instead of failing — that is good design.
  What does it cost you in *detectability*?

**4. Look for it in the signals you do have:**

```bash
docker compose -f docker-compose.observability.yml logs --tail=30 order-service
curl -s localhost:8080/health | jq        # the service still calls itself healthy
```

In Prometheus, `rate(order_requests_total[1m])` keeps flowing — the traffic is
fine. The failure is invisible at the infrastructure layer, which is exactly
why SLIs must measure things **users care about**, not things servers report.

**5. Fix it and confirm recovery:**

```bash
docker compose -f docker-compose.observability.yml start payment-service
sleep 8
curl -s -X POST localhost:8080/orders -H 'content-type: application/json' \
  -d '{"item":"latte","quantity":1,"price":4.0}' | jq .payment.status
```

Expected: `"approved"`.

**6. Five-line blameless postmortem** — write it now, while it is fresh:

```
What happened:
User impact (who, how long, and how would we have known?):
How we detected it:
What made this possible (system, not people):
One systemic action, with an owner:
```

**Checkpoint:**

- [ ] You saw a dependency fail *without* any HTTP error appearing
- [ ] You can name one metric that would have caught it
- [ ] You wrote the five-line postmortem

## Part G — What You Built (10 min)

| | Practice | Module |
|---|---|---|
| ✔ | A small, non-root, cache-friendly image | 6 |
| ✔ | Two services discovering each other by name | 6 |
| ✔ | Kubernetes: probes, limits, self-healing, rollback | 6 |
| ✔ | Vulnerability, secret and misconfiguration scanning | 7 |
| ✔ | Policy as code that fails on a real violation | 7 |
| ✔ | Metrics, a dashboard, an SLI and an error budget | 8 |
| ✔ | A rehearsed failure, a detectability gap, and a postmortem | 8 |

**Clean up:**

```bash
cd "$COURSE_HOME"/labs/lab08-observability
docker compose -f docker-compose.observability.yml down
kind delete cluster --name devops-course
docker ps -aq | xargs -r docker rm -f
```

---

## Going Deeper (self-paced)

Every part above is the short version of a full lab, still in the repository
with more detail and stretch goals:

| Part | Full lab |
|------|----------|
| A | `labs/lab02-docker-basics` |
| B | `labs/lab03-compose-microservices` |
| C | `labs/lab06-kubernetes-kind` |
| D | `labs/lab07-devsecops` |
| E, F | `labs/lab08-observability` (+ `slo.md`) |
| all | `labs/lab09-capstone` — the full golden path, end to end |

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `kind create cluster` hangs | Check resources: `free -h` (needs ~6 GB) and `df -h /` (needs ~15 GB) |
| Pods stuck in `ImagePullBackOff` | You forgot `kind load docker-image` — kind has its own image store |
| `curl localhost:30080` refuses | The cluster must be created **with** `kind-config.yaml` (it maps the port) |
| `kubectl get endpoints` is empty | Pod labels do not match the Service selector, or readiness is failing |
| Port 8080 already in use | The Part B stack is still up: `cd labs/app && docker compose down` |
| Part E shows old data, or the game day says `approved` with payment stopped | You are hitting the Part B stack. `docker port order-service-obs` — if it prints nothing, `docker compose -f docker-compose.observability.yml down` then `up -d` again |
| `kubectl rollout status` times out on a small VM | It is usually still converging: re-run it, or add `--timeout=300s` |
| Grafana shows no data | Check Prometheus targets at <http://localhost:9090/targets> |
| Trivy is slow on first run | It is downloading the vulnerability DB; the installer usually pre-caches it |
