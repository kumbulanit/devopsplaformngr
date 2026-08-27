# Lab 08 — Observability & Reliability

**Duration:** 60 minutes + 15 minute game day
**Prerequisites:** Labs 00–03.

All UIs run on **localhost of your Ubuntu VM**: Prometheus on
`http://localhost:9090`, Grafana on `http://localhost:3000` — open them in
the VM's browser.

## Objectives

- Run Prometheus and Grafana locally with Docker Compose.
- Scrape application metrics from `/metrics` and query them with PromQL.
- Build a dashboard, define an SLO, and respond to a live incident.

## Part A — Start the Observability Stack

The sample app exposes Prometheus metrics on `/metrics` — request counts and
durations recorded by a middleware (open `labs/app/main.py` and find the
`Counter`, the `Histogram` and the `@app.middleware("http")` function; you
will extend this in the stretch goal).

```bash
cd labs/lab08-observability
docker compose -f docker-compose.observability.yml up -d --build
docker compose -f docker-compose.observability.yml ps
```

## Part B — Verify the Metrics Endpoints

```bash
curl -s http://localhost:8080/metrics | grep order_requests_total
curl -s http://localhost:8001/metrics | grep payment_requests_total
```

You should see Prometheus exposition format: counters with
`method`/`endpoint`/`status` labels, plus histogram buckets.

## Part C — Explore Prometheus

Open **http://localhost:9090** in the VM browser and run:

```promql
order_requests_total
rate(order_requests_total[1m])
order_request_duration_seconds_bucket
```

Then check **Status → Targets**: `order-service`, `payment-service` and
`prometheus` should all be **UP**.

## Part D — Generate Traffic

```bash
for i in {1..50}; do
  curl -s -X POST http://localhost:8080/orders \
    -H "Content-Type: application/json" \
    -d '{"item":"mocha","quantity":1,"price":5.0}' > /dev/null
done
```

Re-run the `rate(...)` query — non-zero now.

## Part E — Grafana Dashboard

Open **http://localhost:3000** (login `admin` / `admin`; the Prometheus
datasource is pre-provisioned).

Create a dashboard with two panels:

- **Request rate:** `sum(rate(order_requests_total[1m]))`
- **p95 latency:** `histogram_quantile(0.95, sum(rate(order_request_duration_seconds_bucket[1m])) by (le))`

Save it as **"Order Service Overview"**.

## Part F — SLO Exercise

Open `slo.md`. It defines a 99% SLO, the SLI query (note `/health` is
excluded — discuss why), the error budget, and **burn-rate alerts** instead
of naive threshold alerts. Answer the three discussion questions in a new
`slo-discussion.md`.

## Part G — Mini Game Day 🔥

Your instructor (or your neighbour) will now **break the system** — for
example:

```bash
# saboteur runs ONE of these, without telling you which:
docker stop payment-service-obs
# or
docker pause payment-service-obs
```

Your job, using only observability tools (no peeking at the saboteur's
terminal):

1. Generate a few orders (Part D loop) and *notice* the symptom — payment
   status becomes `unavailable`.
2. Localise it: which Prometheus target is down? What does
   `rate(order_requests_total{endpoint="/orders"}[1m])` show vs the payment
   service's metrics?
3. Confirm with logs: `docker compose -f docker-compose.observability.yml logs payment-service`
4. Restore service (`docker start` / `docker unpause`) and verify recovery
   in Grafana.
5. Write a **5-line blameless postmortem**. The template is below — paste it,
   then fill in the five answers (that part is the exercise):

```bash
cat > postmortem.md <<'MD'
# Postmortem — payment-service outage (game day)

**What happened:**

**User impact** (who, how long, and how would we have known?):

**How we detected it:**

**What made this possible** (system, not people):

**One systemic action, with an owner and a date:**
MD

cat postmortem.md
```

This is the incident lifecycle from the slides — detect → diagnose →
mitigate → learn — at lab scale.

## Part H — Clean Up

```bash
docker compose -f docker-compose.observability.yml down --volumes
```

## Expected Output

- Prometheus shows all targets UP; Grafana panels render live data.
- `slo-discussion.md` and `postmortem.md` written.

## Verification Checklist

- [ ] Both `/metrics` endpoints return Prometheus format.
- [ ] All Prometheus targets UP.
- [ ] Dashboard shows request rate and p95 after the load loop.
- [ ] Game-day incident detected, diagnosed, and recovered using the tools.
- [ ] Postmortem written — blameless.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| No targets in Prometheus | Hostnames in `prometheus.yml` must match the Compose service names. |
| Grafana cannot reach Prometheus | Both must be on `obs-network`; `docker network inspect lab08-observability_obs-network`. |
| No data in panels | Check the Grafana time range (last 15 min) and re-run the traffic loop. |
| Ports 3000/9090 in use | Stop the conflicting service or remap in the compose file. |

## Stretch Goal — Instrument Your Own Metric

Add a business metric to `labs/app/main.py` — copy and paste:

```bash
cd "$COURSE_HOME"
python3 - <<'PY'
from pathlib import Path
p = Path("labs/app/main.py"); s = p.read_text()

# 1. declare the counter next to the existing ones
s = s.replace(
    'REQUEST_DURATION = Histogram(',
    'ORDER_VALUE = Counter(\n'
    '    "order_value_total",\n'
    '    "Cumulative value of all orders placed",\n'
    ')\n\n'
    'REQUEST_DURATION = Histogram(', 1)

# 2. increment it where the order total is computed
s = s.replace('    ORDERS.append(record)',
              '    ORDER_VALUE.inc(total)\n    ORDERS.append(record)', 1)
p.write_text(s)
print("metric added")
PY

grep -n "ORDER_VALUE" labs/app/main.py
```

Rebuild, generate traffic, then graph it:

```bash
cd labs/lab08-observability
docker compose -f docker-compose.observability.yml up -d --build
until curl -sf localhost:8080/health >/dev/null; do sleep 3; done
for i in $(seq 1 20); do
  curl -s -o /dev/null -X POST localhost:8080/orders \
    -H 'content-type: application/json' \
    -d '{"item":"latte","quantity":1,"price":4.0}'
done
curl -s localhost:8080/metrics | grep order_value_total
```

Then graph `rate(order_value_total[5m])` in Prometheus — revenue per second.
Observability is for **business** questions, not just CPU.
