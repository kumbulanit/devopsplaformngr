#!/usr/bin/env bash
# Local simulation of the capstone CI/CD pipeline.
# This script builds, scans and deploys the sample application to a kind cluster.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}/../app"
K8S_DIR="${SCRIPT_DIR}/platform/k8s"
TAG="capstone"
CLUSTER_NAME="devops-course"

echo "=== Step 1: Run tests ==="
cd "${APP_DIR}"
python3 -m pytest || { echo "Tests failed"; exit 1; }

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
  kind create cluster --name "${CLUSTER_NAME}"
fi

echo "=== Step 5: Load images into kind ==="
kind load docker-image order-service:"${TAG}" --name "${CLUSTER_NAME}"
kind load docker-image payment-service:"${TAG}" --name "${CLUSTER_NAME}"

echo "=== Step 6: Deploy to Kubernetes ==="
kubectl apply -k "${K8S_DIR}"

echo "=== Step 7: Wait for rollout ==="
kubectl rollout status deployment/order-service
kubectl rollout status deployment/payment-service

echo "=== Step 8: Smoke test ==="
kubectl port-forward svc/order-service 8080:8000 &
PF_PID=$!
sleep 3

cleanup() {
  echo "Stopping port-forward..."
  kill "${PF_PID}" 2>/dev/null || true
}
trap cleanup EXIT

curl -s http://localhost:8080/health
echo
curl -s -X POST http://localhost:8080/orders \
  -H "Content-Type: application/json" \
  -d '{"item":"capstone-coffee","quantity":1,"price":6.0}'
echo
echo "=== Capstone deployment complete ==="
