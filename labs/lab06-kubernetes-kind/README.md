# Lab 06 — Kubernetes on kind

**Duration:** 90 minutes  
**Prerequisites:** Labs 00–03; kind and kubectl installed; images built.

## Objectives

- Create a local Kubernetes cluster with kind.
- Deploy the order and payment services using YAML manifests.
- Scale a deployment and perform a rolling update.

## Part A — Create a kind Cluster

```bash
kind create cluster --name devops-course
kubectl get nodes
# Expected: one Ready control-plane node
```

Load your locally built images into the cluster so Kubernetes can use them without a registry:

```bash
kind load docker-image order-service:lab02 --name devops-course
kind load docker-image payment-service:lab02 --name devops-course
```

## Part B — Apply Manifests

```bash
cd labs/lab06-kubernetes-kind
kubectl apply -k .
```

Wait for pods to be ready:

```bash
kubectl get pods --watch
# Press Ctrl+C once both pods show Running and 1/1 Ready
```

## Part C — Verify Services

Port-forward to the order service:

```bash
kubectl port-forward svc/order-service 8080:8000
```

In another terminal:

```bash
curl http://localhost:8080/health
# Expected: {"status":"ok","env":"kubernetes","build_id":"k8s-order"}

curl -X POST http://localhost:8080/orders \
  -H "Content-Type: application/json" \
  -d '{"item":"espresso","quantity":2,"price":2.5}'
```

## Part D — Scale the Order Service

```bash
kubectl scale deployment order-service --replicas=3
kubectl get pods -l app=order-service
```

You should see three order pods.

## Part E — Rolling Update

1. Rebuild the image with a new tag to simulate a code change:

```bash
cd labs/app
docker build -t order-service:lab06 --build-arg BUILD_ID=lab06 -f Dockerfile .
kind load docker-image order-service:lab06 --name devops-course
```

2. Update the deployment image:

```bash
kubectl set image deployment/order-service order=order-service:lab06
kubectl rollout status deployment/order-service
```

3. Verify the new build ID:

```bash
kubectl port-forward svc/order-service 8080:8000
curl http://localhost:8080/health
# build_id should now be "lab06"
```

## Part F — Rollback (Optional)

```bash
kubectl rollout history deployment/order-service
kubectl rollout undo deployment/order-service
kubectl rollout status deployment/order-service
```

## Part G — Clean Up

```bash
kind delete cluster --name devops-course
```

## Expected Output

- kind cluster `devops-course` is running.
- Two deployments and two services exist in the `default` namespace.
- Order service returns `env: kubernetes`.
- Scaling changes the replica count.
- Rolling update changes the `build_id`.

## Verification Checklist

- [ ] kind cluster created and nodes Ready.
- [ ] Images loaded into kind.
- [ ] `kubectl apply -k .` succeeds.
- [ ] Pods are Running and Ready.
- [ ] `/health` and `/orders` respond via port-forward.
- [ ] Scaling to three replicas works.
- [ ] Rolling update changes the image tag.
- [ ] Cluster deleted at the end.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ImagePullBackOff` | The image was not loaded into kind or the tag is wrong. |
| `CrashLoopBackOff` | Check logs: `kubectl logs <pod-name>`. Usually a missing env var. |
| Port-forward fails | Ensure the service selector matches pod labels. |
| Pod stuck Pending | kind may be out of resources; recreate with more CPU/RAM. |

## Stretch Goal

Expose the service via an Ingress controller. Install the NGINX ingress on kind:

```bash
kubectl apply -f https://kind.sigs.k8s.io/examples/ingress/deploy-ingress-nginx.yaml
```

Then create an `ingress.yaml` that routes `order.local` to the order service.
