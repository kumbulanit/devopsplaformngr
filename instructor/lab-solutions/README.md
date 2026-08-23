# Lab Solutions & Instructor Notes

This folder contains solution pointers and expected results for each lab. The starter files in `labs/` are already close to a working state; these notes explain the intended final state and common correct answers.

## Lab 00 — Environment Setup

Expected versions at time of writing:

- Docker 24.x+
- kind 0.22+
- kubectl 1.28+
- Terraform 1.6+
- Python 3.10+

If a participant cannot install Terraform locally, they can still read the plan output and inspect the state file in Lab 05.

## Lab 01 — Git Collaboration

Final `main.py` changes:

```python
class HealthResponse(BaseModel):
    status: str
    env: str
    build_id: str
    service_name: str


def health():
    return HealthResponse(
        status="ok",
        env=APP_ENV,
        build_id=BUILD_ID,
        service_name="order-service",
    )
```

New test in `test_app.py`:

```python
def test_health_service_name():
    response = client.get("/health")
    assert response.json()["service_name"] == "order-service"
```

## Lab 02 — Docker Basics

Image `order-service:lab02` exists and a container responds to `http://localhost:8080/health`. Container user is `appuser`.

## Lab 03 — Docker Compose

Both services healthy. POST to `http://localhost:8080/orders` returns an order with a `payment` object.

## Lab 04 — CI/CD

The workflow in `.github/workflows/ci.yml` should have `test`, `build` and `security-scan` jobs. On GitHub, a PR triggers the workflow. With `act`, `act -j test` should pass.

## Lab 05 — IaC

`terraform plan` shows three resources. After apply:

```bash
curl http://localhost:8090/health
# {"status":"ok","env":"dev","build_id":"terraform-dev"}
```

`terraform destroy` removes all `tf-*` containers.

## Lab 06 — Kubernetes

Running pods:

```text
NAME                             READY   STATUS
order-service-...                1/1     Running
payment-service-...              1/1     Running
```

Port-forward returns `env: kubernetes`. Scaling works; rolling update changes `build_id`.

## Lab 07 — DevSecOps

Trivy image scan runs. Trivy config scan runs on Terraform and Kubernetes. Conftest may report a missing `course` label unless the manifests are rendered with Kustomize labels.

## Lab 08 — Observability

Prometheus targets page shows both services up. Grafana renders request rate and p95 duration panels after the load test.

## Lab 09 — Capstone

`./run-capstone.sh` completes and smoke-tests the deployment. `PLATFORM-HANDOVER.md` is created with the five required sections.

## Quick Commands for Live Demo

```bash
# Docker
docker compose -f labs/app/docker-compose.yml up -d --build

# Terraform
cd labs/lab05-iac-terraform && terraform apply -auto-approve

# Kubernetes
cd labs/lab06-kubernetes-kind && kubectl apply -k .

# Observability
cd labs/lab08-observability && docker compose -f docker-compose.observability.yml up -d

# Capstone
cd labs/lab09-capstone && ./run-capstone.sh
```
