# Lab 09 — Capstone: End-to-End Golden Path

**Duration:** 45 minutes guided (full version: 90 minutes self-paced)
**Prerequisites:** Labs 00–08.

## Scenario

You are the **platform team**. You have built a *golden path* for
stream-aligned teams:

- A reusable GitHub Actions workflow (`.github/workflows/capstone.yml`).
- A reusable Terraform module (`platform/terraform/`).
- A Kubernetes overlay built on the Lab 06 base (`platform/k8s/`).
- A service-request intake template (`template/service-request.md`).

A development team wants to ship the order service. Run the golden path
end-to-end on your VM and hand over a working deployment.

## Part A — Review the Golden Path (10 min)

Open and skim these four files. For each, answer: *what does the consuming
team NOT have to know because this exists?*

- `.github/workflows/capstone.yml` — test → build → scan (report + gate) →
  deploy to a kind cluster on the runner.
- `platform/terraform/main.tf` — the module a team calls with just an
  environment name and image tags.
- `platform/k8s/kustomization.yaml` — an **overlay** that reuses the Lab 06
  manifests as a base and stamps platform labels + capstone image tags.
- `template/service-request.md` — the intake contract.

## Part B — Run the Golden Path (15 min)

One script simulates the whole pipeline locally:

```bash
cd labs/lab09-capstone
./run-capstone.sh
```

It runs the tests, builds both images, Trivy-scans, creates (or reuses) the
kind cluster with the course config, loads images, applies the overlay,
waits for rollout, and smoke-tests **http://localhost:30080**.

Expected final output: a JSON health response with `build_id: "capstone"`
and an order creation with payment `approved`.

## Part C — Verify in Kubernetes (5 min)

```bash
kubectl get all
kubectl get deploy order-service -o jsonpath='{.metadata.labels}' ; echo
# note both the lab06 base labels AND the platform overlay labels
kubectl logs -l app=order-service --tail=10
```

## Part D — Platform Handover Document (15 min)

Create `PLATFORM-HANDOVER.md` explaining how a new stream-aligned team
consumes the golden path. Required sections:

1. **Onboarding checklist** — repo access, cluster namespace, SLO targets.
2. **How to request a service** — point at `template/service-request.md`.
3. **How to deploy** — commit to `main`; pipeline tests, scans, gates, deploys.
4. **Support model** — office hours, escalation path.
5. **Success metrics** — the four DORA metrics + platform adoption.

## Expected Output

- Order service running in kind, reachable at `http://localhost:30080`.
- `PLATFORM-HANDOVER.md` with the five sections.
- You can narrate every pipeline stage from memory — that narration IS the
  course summary.

## Verification Checklist

- [ ] `./run-capstone.sh` completes without errors.
- [ ] Pods Running and Ready; overlay labels present.
- [ ] `http://localhost:30080/health` returns `build_id: "capstone"`.
- [ ] POST `/orders` returns payment `approved`.
- [ ] `PLATFORM-HANDOVER.md` complete.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Script fails at tests | `labs/app/.venv` missing — re-run Lab 00 Part A. |
| `localhost:30080` refused | Cluster exists but was created without the course config: `kind delete cluster --name devops-course` and re-run the script. |
| `ImagePullBackOff` | Re-run the script; it reloads images into kind. |
| Rollout timeout | `kubectl describe pod ...` — usually VM memory pressure; close other stacks (`docker compose down` in labs 03/08). |

## Stretch Goals

1. **Observability hook:** re-deploy the Lab 08 Prometheus stack and add
   scrape annotations to the deployments, or a scrape config for
   `host.docker.internal:30080`.
2. **Split the pipeline** into `test.yml` (every PR), `build-and-scan.yml`
   (merge to `main`), and `deploy.yml` (manual approval via environments) —
   deployment gates in practice.
3. **Terraform path:** deploy the same app with the platform module instead
   of Kubernetes: `cd platform/terraform && terraform init && terraform apply
   -var environment=capstone -var order_image=order-service:capstone -var
   payment_image=payment-service:capstone`.
