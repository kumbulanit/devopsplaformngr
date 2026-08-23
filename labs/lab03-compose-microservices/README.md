# Lab 03 — Docker Compose Microservices

**Duration:** 60 minutes  
**Prerequisites:** Lab 02 complete.

## Objectives

- Orchestrate two services with Docker Compose.
- Understand service discovery, health checks and environment variables.
- Observe inter-service communication.

## Part A — Start the Stack

From `labs/app`:

```bash
docker compose up -d --build
```

Check status:

```bash
docker compose ps
```

Both services should be `healthy`.

## Part B — Test End-to-End Flow

Create an order through the public port:

```bash
curl -X POST http://localhost:8080/orders \
  -H "Content-Type: application/json" \
  -d '{"item":"latte","quantity":1,"price":4.0}'
```

Expected response includes an `id`, `payment` status and a `payment` object from the payment service.

List orders:

```bash
curl http://localhost:8080/orders
```

## Part C — Service Discovery

The order service reaches the payment service by DNS name `payment-service`. This works because Docker Compose creates a bridge network and registers each service in an internal DNS.

Inspect the network:

```bash
docker network ls
docker network inspect app_app-network  # name may vary; look for app-network
```

## Part D — Scaling and Load

Scale the payment service to two replicas:

```bash
docker compose up -d --scale payment-service=2
```

Create several orders and observe that requests are distributed across payment containers. Note: the sample app keeps in-memory state, so listing payments from each replica may differ.

## Part E — Environment Variables

Run with a custom build ID:

```bash
BUILD_ID=compose-demo docker compose up -d --build
```

Verify:

```bash
curl http://localhost:8080/health
# Expected build_id: "compose-demo"
```

## Part F — Clean Up

```bash
docker compose down --volumes
```

## Expected Output

- Both services healthy in `docker compose ps`.
- POST to `/orders` returns an order with payment details.
- Scaling changes the replica count in `docker compose ps`.

## Verification Checklist

- [ ] `docker compose up -d --build` succeeds.
- [ ] `/health` returns `ok` for both services.
- [ ] POST `/orders` creates an order and calls the payment service.
- [ ] Network inspection shows both containers attached to `app-network`.
- [ ] `docker compose down` removes everything.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `payment-service` unreachable | Ensure `depends_on` condition is `service_healthy` and the network name matches. |
| Payment status shows error | The payment service may still be starting; wait a few seconds and retry. |
| Health check fails | Check logs: `docker compose logs payment-service`. |

## Stretch Goal

Add a `docker-compose.override.yml` that mounts source code for live reload during development and uses `uvicorn --reload`, without changing the production `docker-compose.yml`.
