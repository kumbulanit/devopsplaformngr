#!/usr/bin/env bash
# End-to-end verification of the course package on Ubuntu.
# This script runs inside the verify/Dockerfile container with the host Docker socket mounted.
set -euo pipefail

cd /workspace

echo "===== Tool versions ====="
python3 --version
pip3 --version
docker --version
terraform -version
kind version
kubectl version --client

echo "===== Install Python dependencies in a venv ====="
python3 -m venv .venv-ubuntu
source .venv-ubuntu/bin/activate
pip install --upgrade pip --quiet
pip install -r labs/app/requirements.txt pytest python-pptx matplotlib --quiet

echo "===== Run unit tests ====="
python3 -m pytest labs/app/test_app.py

echo "===== Regenerate diagrams ====="
python3 diagrams/build_diagrams.py

echo "===== Regenerate slide decks ====="
python3 slides/build_slides.py

echo "===== Build Docker images ====="
cd labs/app
docker build -t order-service:ubuntu-verify --build-arg BUILD_ID=ubuntu-verify -f Dockerfile .
docker build -t payment-service:ubuntu-verify --build-arg BUILD_ID=ubuntu-verify -f Dockerfile.payment .
# The Terraform lab expects the lab02 tags used in its terraform.tfvars.example.
docker tag order-service:ubuntu-verify order-service:lab02
docker tag payment-service:ubuntu-verify payment-service:lab02

echo "===== Run Docker Compose smoke test ====="
docker compose down --volumes || true
BUILD_ID=ubuntu-compose docker compose up -d --build
echo "Waiting for services to become healthy..."
for i in {1..30}; do
  if curl -fs http://localhost:8080/health > /dev/null 2>&1; then
    echo "Order service is healthy"
    break
  fi
  sleep 2
done

curl -s http://localhost:8080/health
echo
ORDER_RESULT=$(curl -s -X POST http://localhost:8080/orders \
  -H "Content-Type: application/json" \
  -d '{"item":"ubuntu-coffee","quantity":1,"price":5.0}')
echo "Order created: ${ORDER_RESULT}"
if [[ "${ORDER_RESULT}" != *"id"* ]]; then
  echo "ERROR: order creation failed"
  exit 1
fi
docker compose down --volumes
cd /workspace

echo "===== Terraform init / plan ====="
cd labs/lab05-iac-terraform
# Clean up any leftovers from a previous interrupted verification run.
terraform destroy -auto-approve 2>/dev/null || true
 docker network rm tf-dev-app-network 2>/dev/null || true
 docker rm -f tf-dev-order-service tf-dev-payment-service 2>/dev/null || true
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan -out=tfplan
terraform apply tfplan

echo "===== Terraform smoke test ====="
echo "Waiting for Terraform-managed services to become healthy..."
for i in {1..30}; do
  if curl -fs http://localhost:8090/health > /dev/null 2>&1; then
    echo "Order service is healthy"
    break
  fi
  sleep 2
done
curl -s http://localhost:8090/health
echo
terraform destroy -auto-approve
cd /workspace

echo "===== kind + Kubernetes smoke test ====="
kind delete cluster --name ubuntu-course 2>/dev/null || true
kind create cluster --name ubuntu-course
kind load docker-image order-service:lab02 --name ubuntu-course
kind load docker-image payment-service:lab02 --name ubuntu-course

cd labs/lab06-kubernetes-kind
kubectl apply -k .
echo "Waiting for deployments..."
kubectl rollout status deployment/order-service
kubectl rollout status deployment/payment-service

echo "===== Kubernetes smoke test ====="
kubectl port-forward svc/order-service 18080:8000 &
PF_PID=$!
sleep 3
kill_trap() {
  kill "${PF_PID}" 2>/dev/null || true
}
trap kill_trap EXIT

curl -s http://localhost:18080/health
kind delete cluster --name ubuntu-course

echo "===== All Ubuntu verification checks passed ====="
