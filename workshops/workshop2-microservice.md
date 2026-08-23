# Workshop 2 — Building and Deploying a Microservice

**Slot:** Day 2, 10:00–12:15 (135 min) · **Theory it applies:** Module 6
**Guide:** orchestrates [Lab 02](../labs/lab02-docker-basics/README.md) →
[Lab 03](../labs/lab03-compose-microservices/README.md) →
[Lab 06](../labs/lab06-kubernetes-kind/README.md)

One continuous journey with one application: **container → composed stack →
Kubernetes**, all served on localhost of your VM.

## Success criteria (this is "done")

- [ ] Image built; container runs as `appuser`, answers on `localhost:8080`.
- [ ] Compose stack healthy; POST `/orders` returns payment `"approved"`.
- [ ] Kubernetes serves `/health` on **`localhost:30080`** (NodePort, no port-forward).
- [ ] You performed a **rolling update** (build_id → `lab06`) **and a rollback** (→ `lab02`).

## Core path (fits the slot)

| Step | Do | Time |
|------|----|------|
| 1 | **Lab 02** Parts A–B: build the image, run it, `/health` on :8080, `whoami` → `appuser`; skim Part C (layers) as a group | 25 min |
| 2 | **Lab 03** Parts A–C: compose up, end-to-end order with `approved` payment, prove the payment service is internal-only | 30 min |
| 3 | **Lab 03** Part D: scale payment to 2 replicas — observe split in-memory state (the statelessness lesson), then `docker compose down` | 10 min |
| 4 | **Lab 06** Parts A–C: kind cluster **with `kind-config.yaml`**, load images, `kubectl apply -k .`, curl `localhost:30080` | 35 min |
| 5 | **Lab 06** Parts D–F: scale to 3, rolling update to `lab06`, watch `/health` change, roll back | 25 min |
| 6 | Verification checklists; **keep the cluster running** for the capstone | 10 min |

## Compressions if time is tight

- Step 1: skip `docker exec` exploration; instructor shows layers once.
- Step 3: demo from the front instead of per-participant.
- Step 5: rollback as instructor demo.

## Stretch goals

- Lab 02: `dive` image analysis · Lab 03: live-reload override file ·
  Lab 06: NGINX ingress with `order.localtest.me`.
