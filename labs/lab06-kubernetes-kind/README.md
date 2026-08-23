# Lab 06 — Kubernetes on kind

**Duration:** 75 minutes
**Prerequisites:** Labs 00–03; images `order-service:lab02` and
`payment-service:lab02` built (Lab 02 / Lab 05 Part A).

## Objectives

- Create a local Kubernetes cluster with kind.
- Deploy both services with manifests and Kustomize.
- Reach a Service on localhost via NodePort, scale it, and roll out an update.

## Part A — Create the Cluster

The course kind config forwards **localhost:30080 → NodePort 30080**, so you
can reach the order service without `kubectl port-forward`:

```bash
cd labs/lab06-kubernetes-kind
kind create cluster --name devops-course --config kind-config.yaml
kubectl get nodes
# Expected: one Ready control-plane node
```

Load the locally built images into the cluster (kind has no registry):

```bash
kind load docker-image order-service:lab02 --name devops-course
kind load docker-image payment-service:lab02 --name devops-course
```

## Part B — Apply the Manifests

```bash
kubectl apply -k .
kubectl get pods --watch
# Ctrl+C once all pods are Running and 1/1 Ready
```

While you wait, open the YAML and find:

- the **readiness and liveness probes** hitting `/health`;
- the **resource requests/limits**;
- the **securityContext** (`runAsNonRoot`, dropped capabilities, read-only
  root filesystem) — Lab 07 scans will verify these;
- in `kustomization.yaml`, the `labels:` block that stamps every object with
  `course` and `environment` labels at render time.

## Part C — Reach the Service on localhost

```bash
curl http://localhost:30080/health
# Expected: {"status":"ok","env":"kubernetes","build_id":"lab02"}
```

Two things to note:

- `env` is `kubernetes` — injected by the ConfigMap via `envFrom`.
- `build_id` is `lab02` — baked into the **image** at build time. Nothing in
  the manifests overrides it, which makes Part E visible.

Create an order (the order pod calls the payment pod through the
`payment-service` ClusterIP Service — same DNS idea as Compose, cluster-wide):

```bash
curl -X POST http://localhost:30080/orders \
  -H "Content-Type: application/json" \
  -d '{"item":"espresso","quantity":2,"price":2.5}'
# Expected: payment status "approved"
```

> `kubectl port-forward svc/order-service 8080:8000` remains the universal
> fallback when no NodePort mapping exists — try it in a second tmux pane.

## Part D — Scale

```bash
kubectl scale deployment order-service --replicas=3
kubectl get pods -l app=order-service
```

## Part E — Rolling Update

1. Build and load a new image version:

```bash
cd ../app
docker build -t order-service:lab06 --build-arg BUILD_ID=lab06 -f Dockerfile .
kind load docker-image order-service:lab06 --name devops-course
cd ../lab06-kubernetes-kind
```

2. Update the deployment and watch the rollout:

```bash
kubectl set image deployment/order-service order=order-service:lab06
kubectl rollout status deployment/order-service
```

3. Verify the new build is serving:

```bash
curl http://localhost:30080/health
# build_id is now "lab06"
```

## Part F — Rollback

```bash
kubectl rollout history deployment/order-service
kubectl rollout undo deployment/order-service
kubectl rollout status deployment/order-service
curl http://localhost:30080/health
# build_id is back to "lab02"
```

## Part G — Clean Up

Keep the cluster if you are continuing to Lab 07/09 today; otherwise:

```bash
kind delete cluster --name devops-course
```

## Expected Output

- `http://localhost:30080/health` answers directly (NodePort mapping).
- `env: kubernetes` from the ConfigMap; `build_id` follows the image tag.
- Scaling and rolling update/rollback behave as described.

## Verification Checklist

- [ ] Cluster created with `kind-config.yaml`, node Ready.
- [ ] Images loaded into kind.
- [ ] Pods Running and Ready.
- [ ] `curl localhost:30080/health` works without port-forward.
- [ ] POST `/orders` returns payment status `approved`.
- [ ] Rolling update changes `build_id` to `lab06`; rollback restores `lab02`.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ImagePullBackOff` | Image not loaded into kind, or tag mismatch: re-run `kind load docker-image ...`. |
| `CrashLoopBackOff` | `kubectl logs <pod>` and `kubectl describe pod <pod>`. |
| `localhost:30080` refused | Cluster was created **without** `--config kind-config.yaml`; recreate it. |
| Pod stuck Pending | `kubectl describe pod` → usually insufficient CPU/RAM; check `free -h`. |

## Stretch Goal

Install the NGINX Ingress controller on kind and route `order.localtest.me`
to the order service (`*.localtest.me` resolves to 127.0.0.1 — no
`/etc/hosts` editing needed):

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```
