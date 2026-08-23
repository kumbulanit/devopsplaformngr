# Lab 05 — Infrastructure as Code with Terraform

**Duration:** 75 minutes  
**Prerequisites:** Labs 00–02; Terraform installed.

## Objectives

- Define Docker infrastructure declaratively with Terraform.
- Practise `init`, `plan`, `apply`, and state inspection.
- Understand variables, outputs and resource dependencies.

## Part A — Build Images

If you have not already built the images in Lab 02, do so now:

```bash
cd labs/app
docker build -t order-service:lab02 --build-arg BUILD_ID=lab02 -f Dockerfile .
docker build -t payment-service:lab02 --build-arg BUILD_ID=lab02 -f Dockerfile.payment .
```

## Part B — Initialise Terraform

```bash
cd labs/lab05-iac-terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
```

You should see the Docker provider downloaded and a `.terraform` directory created.

## Part C — Plan

```bash
terraform plan -out=tfplan
```

Review the plan. Terraform will create:

- One Docker network.
- One payment service container.
- One order service container that depends on the payment service.

Notice the `+` signs showing resources to be created. Notice `PAYMENT_SERVICE_URL` references the payment container by name.

## Part D — Apply

```bash
terraform apply tfplan
```

When apply completes, Terraform prints outputs including the order service URL.

## Part E — Verify

```bash
terraform output order_service_url
curl $(terraform output -raw order_service_url)/health
# Expected: {"status":"ok","env":"dev","build_id":"terraform-dev"}

# Create an order
curl -X POST $(terraform output -raw order_service_url)/orders \
  -H "Content-Type: application/json" \
  -d '{"item":"cappuccino","quantity":1,"price":4.5}'
```

## Part F — Inspect State

```bash
terraform state list
terraform state show docker_container.order_service
```

The state file maps Terraform resource names to real Docker container IDs.

## Part G — Change and Re-apply

Edit `terraform.tfvars` and change `order_port` to `8092`. Run:

```bash
terraform plan
terraform apply
```

Terraform will replace the order service container to bind the new host port.

## Part H — Clean Up

```bash
terraform destroy
```

Confirm with `yes`. Verify no containers remain:

```bash
docker ps -a --filter "name=tf-"
```

## Expected Output

- `terraform plan` shows three resources to create.
- `terraform apply` succeeds and prints URLs.
- `/health` returns the environment and build ID set by Terraform.
- `terraform destroy` removes all resources.

## Verification Checklist

- [ ] `terraform init` downloads the Docker provider.
- [ ] `terraform plan` shows the expected diff.
- [ ] Containers start and respond to health checks.
- [ ] State file contains container IDs.
- [ ] `terraform destroy` leaves no `tf-*` containers.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `provider registry not found` | Run `terraform init` again. |
| Port already allocated | Change `order_port` or `payment_port` in `terraform.tfvars`. |
| Image not found | Build the images in Lab 02 or update image tags in `terraform.tfvars`. |
| State lock error | Delete stale `.terraform.tfstate.lock.info` only if no apply is running. |

## Stretch Goal

Refactor the container resource into a reusable module:

1. Create `modules/container/main.tf`, `variables.tf`, `outputs.tf`.
2. Move the container logic there.
3. Call the module twice from `main.tf` for order and payment services.

This demonstrates module reuse, a core IaC best practice.
