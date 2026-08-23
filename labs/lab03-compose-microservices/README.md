# Lab 03 — Docker Compose Microservices

**Duration:** 45 minutes
**Prerequisites:** Lab 02 complete.

## Objectives

- Orchestrate two services with Docker Compose.
- Understand service discovery, health checks and environment variables.
- Observe inter-service communication on localhost.

## Part A — Start the Stack

From `labs/app`:

```bash
cd labs/app
docker compose up -d --build
```

Check status:

```bash
docker compose ps
```

Both services should show `healthy` (the images define a `HEALTHCHECK`, and
the order service waits for the payment service via
`depends_on: condition: service_healthy`).

## Part B — Test the End-to-End Flow

Create an order through the published port:

```bash
curl -X POST http://localhost:8080/orders \
  -H "Content-Type: application/json" \
  -d '{"item":"latte","quantity":1,"price":4.0}'
```

Expected: the response now includes a `payment` object with
`"status": "approved"` — unlike Lab 00, the payment service is running and
reachable.

List orders:

```bash
curl http://localhost:8080/orders
```

## Part C — Service Discovery

The order service reaches the payment service by the DNS name
`payment-service` — Compose creates a bridge network and registers every
service in an internal DNS.

```bash
docker network ls
docker network inspect app_app-network
```

Note that the **payment service has no published port**: it is reachable
only inside the Compose network. Prove it:

```bash
curl --max-time 2 http://localhost:8001/health || echo "not reachable from the host - by design"
docker compose exec order-service python -c \
  "import httpx; print(httpx.get('http://payment-service:8000/health').json())"
```

## Part D — Scaling

Scale the payment service to two replicas (possible precisely because it has
no fixed host port):

```bash
docker compose up -d --scale payment-service=2
docker compose ps
```

Create several orders and check the payment lists on each replica — the
sample app keeps in-memory state, so each replica has seen different
payments. This is the classic argument for **stateless services**:

```bash
for i in 1 2 3 4; do
  curl -s -X POST http://localhost:8080/orders \
    -H "Content-Type: application/json" \
    -d '{"item":"flat-white","quantity":1,"price":4.0}' > /dev/null
done
docker compose exec --index 1 payment-service python -c \
  "import httpx; print(httpx.get('http://localhost:8000/payments').json()['count'])"
docker compose exec --index 2 payment-service python -c \
  "import httpx; print(httpx.get('http://localhost:8000/payments').json()['count'])"
```

## Part E — Environment Variables

Run with a custom build ID:

```bash
BUILD_ID=compose-demo docker compose up -d --build
curl http://localhost:8080/health
# Expected build_id: "compose-demo"
```

## Part F — Clean Up

```bash
docker compose down --volumes
```

## Expected Output

- Both services healthy in `docker compose ps`.
- POST to `/orders` returns a payment with status `approved`.
- Scaling changes the replica count; replicas hold different in-memory state.

## Verification Checklist

- [ ] `docker compose up -d --build` succeeds and both services are healthy.
- [ ] POST `/orders` returns `"status": "approved"` in the payment object.
- [ ] Payment service is NOT reachable from the host, but IS reachable from the order container.
- [ ] Scaling to two payment replicas works.
- [ ] `docker compose down` removes everything.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `payment-service` unhealthy | `docker compose logs payment-service` — usually still starting; wait for the healthcheck interval. |
| Payment status `unavailable` | The payment container is down or unhealthy; check `docker compose ps`. |
| Network name differs | `docker network ls \| grep app` — the prefix is the Compose project (directory) name. |

## Stretch Goal

Add a `docker-compose.override.yml` that mounts the source code and runs
`uvicorn --reload` for live-reload development — without changing the
production `docker-compose.yml`. Hint: overrides merge automatically when
you run `docker compose up`.
