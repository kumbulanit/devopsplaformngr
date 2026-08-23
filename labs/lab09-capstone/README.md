# Lab 09 — Capstone: End-to-End Golden Path

**Duration:** 90 minutes  
**Prerequisites:** Labs 00–08 completed.

## Objectives

- Experience building a complete DevOps pipeline end-to-end.
- Use platform-provided templates (CI/CD, Terraform module, Kubernetes manifests).
- Deploy the sample application to Kubernetes with security scanning and observability.
- Document the internal platform offering for future teams.

## Scenario

You are the platform team. You have built a **golden path** for stream-aligned teams:

- A reusable GitHub Actions workflow.
- A reusable Terraform module.
- A Kubernetes base layer with monitoring hooks.
- A service request template.

A development team wants to ship the order service. Your job is to run the golden path and hand over a working deployment.

## Part A — Review the Golden Path

Open these files and read them:

- `labs/lab09-capstone/.github/workflows/capstone.yml` — CI/CD pipeline.
- `labs/lab09-capstone/platform/terraform/main.tf` — reusable Terraform module.
- `labs/lab09-capstone/platform/k8s/kustomization.yaml` — Kubernetes base.
- `labs/lab09-capstone/template/service-request.md` — intake template.

## Part B — Run the Capstone Locally

A helper script simulates the full pipeline on your machine:

```bash
cd labs/lab09-capstone
chmod +x run-capstone.sh
./run-capstone.sh
```

The script will:

1. Run Python tests.
2. Build Docker images tagged `capstone`.
3. Scan the order image with Trivy (if installed).
4. Create a kind cluster named `devops-course` if it does not exist.
5. Load images into the cluster.
6. Apply the Kubernetes manifests.
7. Smoke-test the deployment via port-forward.

You should see a JSON health response and an order creation response.

## Part C — Verify in Kubernetes

```bash
kubectl get all
kubectl logs -l app=order-service --tail=20
kubectl logs -l app=payment-service --tail=20
```

## Part D — Add Observability

Reuse the Prometheus and Grafana stack from Lab 08. Update the scrape config to target the Kubernetes services, or add the Prometheus annotations to the Kubernetes manifests.

Example annotation for the order deployment:

```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8000"
    prometheus.io/path: "/metrics"
```

## Part E — Platform Handover Document

Create `PLATFORM-HANDOVER.md` that explains how a new stream-aligned team would consume the golden path. Include:

1. **Onboarding checklist** — what the team needs (repo access, cluster namespace, SLO targets).
2. **How to raise a new service** — use `template/service-request.md`.
3. **How to deploy** — commit to `main`; the pipeline tests, scans and deploys.
4. **Support model** — platform team office hours, escalation path.
5. **Success metrics** — deployment frequency, lead time, change failure rate.

## Expected Output

- A working order service running in kind.
- A completed `PLATFORM-HANDOVER.md`.
- Pipeline logs or script output showing test, build, scan and deploy stages.

## Verification Checklist

- [ ] `./run-capstone.sh` completes without errors.
- [ ] `kubectl get pods` shows Running and Ready pods.
- [ ] Port-forwarded `/health` returns JSON.
- [ ] POST `/orders` returns an order with payment details.
- [ ] `PLATFORM-HANDOVER.md` is created and contains the five required sections.
- [ ] (Optional) Prometheus scrapes the Kubernetes services.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Script fails at tests | Return to Lab 00 and ensure `pytest` works in `labs/app`. |
| kind cluster already exists | Delete it: `kind delete cluster --name devops-course` or let the script reuse it. |
| ImagePullBackOff | Images were not loaded; run `kind load docker-image` manually. |
| Port-forward conflict | Change the local port in the script or stop other services on port 8080. |

## Stretch Goal

Split the monolithic pipeline into separate workflows triggered by different events:

- `test.yml` on every pull request.
- `build-and-scan.yml` on merge to `main`.
- `deploy.yml` triggered only after the build workflow succeeds and a manual approval is given.

This demonstrates environments and deployment gates.
