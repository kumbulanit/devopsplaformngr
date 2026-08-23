#!/usr/bin/env bash
# Local simulation of the capstone CI/CD pipeline on the Ubuntu VM.
# Builds, scans and deploys the sample application to a kind cluster,
# then smoke-tests it on localhost.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}/../app"
K8S_DIR="${SCRIPT_DIR}/platform/k8s"
TAG="capstone"
CLUSTER_NAME="devops-course"
KIND_CONFIG="${SCRIPT_DIR}/../lab06-kubernetes-kind/kind-config.yaml"

# Prefer the course virtual environment created by Lab 00.
PYTHON="python3"
if [[ -x "${APP_DIR}/.venv/bin/python" ]]; then
  PYTHON="${APP_DIR}/.venv/bin/python"
fi

echo "=== Step 1: Run tests ==="
cd "${APP_DIR}"
"${PYTHON}" -m pytest || { echo "Tests failed"; exit 1; }

echo "=== Step 2: Build images ==="
docker build -t order-service:"${TAG}" --build-arg BUILD_ID="${TAG}" -f Dockerfile .
docker build -t payment-service:"${TAG}" --build-arg BUILD_ID="${TAG}" -f Dockerfile.payment .

echo "=== Step 3: Security scan (Trivy) ==="
if command -v trivy &>/dev/null; then
  trivy image --severity HIGH,CRITICAL order-service:"${TAG}" || true
else
  echo "Trivy not installed; skipping scan."
fi

echo "=== Step 4: Create / verify kind cluster ==="
if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
  kind create cluster --name "${CLUSTER_NAME}" --config "${KIND_CONFIG}"
fi

echo "=== Step 5: Load images into kind ==="
kind load docker-image order-service:"${TAG}" --name "${CLUSTER_NAME}"
kind load docker-image payment-service:"${TAG}" --name "${CLUSTER_NAME}"

echo "=== Step 6: Deploy to Kubernetes ==="
kubectl apply -k "${K8S_DIR}"

echo "=== Step 7: Wait for rollout ==="
kubectl rollout status deployment/order-service --timeout=180s
kubectl rollout status deployment/payment-service --timeout=180s

echo "=== Step 8: Smoke test (NodePort on localhost:30080) ==="
sleep 2
curl -fs http://localhost:30080/health
echo
curl -fs -X POST http://localhost:30080/orders \
  -H "Content-Type: application/json" \
  -d '{"item":"capstone-coffee","quantity":1,"price":6.0}'
echo
echo "=== Capstone deployment complete ==="
echo "Order service: http://localhost:30080/health"
