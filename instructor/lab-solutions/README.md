# Lab Solutions & Instructor Notes

Solution pointers and expected results for each lab. The starter files in
`labs/` are working; these notes give intended final states and answers.

## Lab 00 — Environment Setup

`lab-setup/check-environment.sh` must end with
`RESULT: all required checks passed`. Everything else in the course assumes
this. `pytest` in `labs/app` reports **5 passed**.

## Lab 01 — Git Collaboration

All work happens in `/tmp/lab01/app` — never in the course repo itself.

Final `main.py` changes:

```python
class HealthResponse(BaseModel):
    status: str
    env: str
    build_id: str
    service_name: str
```

and in `health()` add `service_name="order-service",`.

New test in `test_app.py`:

```python
def test_health_service_name():
    response = client.get("/health")
    assert response.json()["service_name"] == "order-service"
```

## Lab 02 — Docker Basics

`curl localhost:8080/health` → `env: "production"`, `build_id: "lab02"`.
`whoami` in the container → `appuser`. Teaching point: env/build_id changed
from Lab 00 because they are baked into the image.

## Lab 03 — Docker Compose

POST `/orders` → payment `"status": "approved"` (payment service now
reachable). Payment service is intentionally NOT published to the host;
Part C proves this with a failing host curl + a succeeding in-network call.
Part D scaling shows per-replica in-memory state → statelessness argument.

## Lab 04 — CI/CD

The key answer: the first Trivy step (**report**, exit-code 0) can never
fail the build — it is visibility only. The second (**gate**, exit-code 1,
`ignore-unfixed`) fails on *actionable* CRITICALs. Also point out
`permissions: contents: read` and the pinned action version (`@0.28.0`, not
`@master`).

## Lab 05 — IaC

`terraform plan` shows **3 to add**. After apply:
`curl localhost:8090/health` → `env: "dev"`, `build_id: "terraform-dev"`,
and POST `/orders` → payment `approved` (Terraform wired the network).
`.terraform.lock.hcl` is committed; state files are not — ask why.
Part F experiment: `docker rm -f tf-dev-order-service && terraform plan`
shows **1 to add** — Terraform detects drift from state.
Ansible bonus: second run of the playbook reports `changed=0` (idempotence).

## Lab 06 — Kubernetes

- Part C: `curl localhost:30080/health` → `env: "kubernetes"` (ConfigMap),
  `build_id: "lab02"` (baked into image — nothing overrides it).
- Part E: after `kubectl set image ... order-service:lab06`,
  `build_id` becomes `"lab06"`. Rollback restores `"lab02"`.
- If localhost:30080 fails, the cluster was created without
  `kind-config.yaml` (no NodePort mapping) — recreate.

## Lab 07 — DevSecOps

- Raw manifests **fail** the label policy; `kubectl kustomize | conftest`
  **passes** — labels are added at render time. That contrast is the lesson.
- `:latest` sed-experiment fails `no_latest_tag.rego`.
- Rego must be v1 syntax (`import rego.v1`, `deny contains msg if`); the old
  `deny[msg]` form is a parse error on current OPA/Conftest.

## Lab 08 — Observability

- All three Prometheus targets UP; panels show data after the traffic loop.
- Game day (Part G): stop or pause `payment-service-obs` yourself. Detection
  signal: order payment status flips to `unavailable`; payment target goes
  DOWN in Prometheus. Require the 5-line blameless postmortem.
- SLO discussion: `/health` excluded from the SLI (health-check traffic
  inflates availability); burn-rate alerts replace naive thresholds.

## Lab 09 — Capstone

`./run-capstone.sh` ends with health JSON showing `build_id: "capstone"`
from `http://localhost:30080` and an order with payment `approved`.
`kubectl get deploy order-service -o jsonpath='{.metadata.labels}'` shows
base labels (course/environment=lab06 overridden to capstone) plus
`platform: course-golden-path` — evidence of base + overlay composition.
`PLATFORM-HANDOVER.md` has the five sections.

## Quick Commands for Live Demo

```bash
# Compose
cd labs/app && docker compose up -d --build

# Terraform
cd labs/lab05-iac-terraform && cp terraform.tfvars.example terraform.tfvars \
  && terraform init && terraform apply -auto-approve

# Kubernetes
kind create cluster --name devops-course --config labs/lab06-kubernetes-kind/kind-config.yaml
cd labs/lab06-kubernetes-kind && kubectl apply -k .

# Observability
cd labs/lab08-observability && docker compose -f docker-compose.observability.yml up -d --build

# Capstone
cd labs/lab09-capstone && ./run-capstone.sh
```
