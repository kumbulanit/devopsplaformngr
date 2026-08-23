# Lab 08 — Observability & Reliability

**Duration:** 75 minutes  
**Prerequisites:** Labs 00–03 and updated app with Prometheus metrics.

## Objectives

- Run Prometheus and Grafana locally with Docker Compose.
- Scrape application metrics from the `/metrics` endpoint.
- Build a simple dashboard and define an SLO.

## Part A — Start the Observability Stack

The app was updated to expose Prometheus-format metrics on `/metrics`. It also tracks request counts and durations via middleware.

From `labs/lab08-observability`:

```bash
docker compose -f docker-compose.observability.yml up -d --build
```

Check that all containers are running:

```bash
docker compose -f docker-compose.observability.yml ps
```

## Part B — Verify Metrics Endpoints

```bash
curl http://localhost:8080/metrics | grep order_requests_total
curl http://localhost:8001/metrics | grep payment_requests_total
```

You should see Prometheus exposition output with counters and histograms.

## Part C — Explore Prometheus

Open http://localhost:9090.

Run these queries:

```promql
order_requests_total
rate(order_requests_total[1m])
order_request_duration_seconds_bucket
```

Confirm that both `order-service` and `payment-service` targets are up:

```bash
# In Prometheus UI: Status → Targets
# Both should be green.
```

## Part D — Generate Traffic

Run a small load script to populate metrics:

```bash
for i in {1..30}; do
  curl -s -X POST http://localhost:8080/orders \
    -H "Content-Type: application/json" \
    -d '{"item":"mocha","quantity":1,"price":5.0}' > /dev/null
done
```

Return to Prometheus and re-run the rate query. You should see non-zero values.

## Part E — Grafana Dashboard

Open http://localhost:3000 and log in with `admin/admin`.

1. Navigate to **Explore**.
2. Select the Prometheus datasource.
3. Create a new dashboard with two panels:
   - **Request rate**: `rate(order_requests_total[1m])`
   - **Request duration (p95)**: `histogram_quantile(0.95, rate(order_request_duration_seconds_bucket[1m]))`
4. Save the dashboard as "Order Service Overview".

## Part F — SLO Exercise

Open `slo.md` and discuss:

- Is 99% availability realistic for this lab service?
- What would an error budget policy look like?
- What alert threshold would wake the on-call engineer without causing alert fatigue?

Write your answers in a new file `slo-discussion.md`.

## Part G — Clean Up

```bash
docker compose -f docker-compose.observability.yml down --volumes
```

## Expected Output

- Prometheus targets page shows order and payment services up.
- Grafana renders request rate and duration panels.
- `slo-discussion.md` contains team answers.

## Verification Checklist

- [ ] Compose stack starts without errors.
- [ ] `/metrics` returns Prometheus format.
- [ ] Prometheus shows both targets healthy.
- [ ] Grafana login works.
- [ ] Dashboard panels display data after load test.
- [ ] SLO discussion documented.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Prometheus shows no targets | Check `prometheus.yml` hostnames match service names in the compose network. |
| Grafana cannot reach Prometheus | Ensure both are on the same Docker network. |
| Metrics endpoint returns JSON | You may be running an older app image; rebuild with `--build`. |
| No data in panels | Verify the time range in Grafana and that traffic was generated. |

## Stretch Goal

Add a Loki container and configure the app to log to JSON. Create a Grafana panel that correlates error logs with high latency metrics.
