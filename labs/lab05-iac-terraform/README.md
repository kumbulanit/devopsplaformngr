# Lab 05 — Infrastructure as Code with Terraform

**Duration:** 60 minutes
**Prerequisites:** Lab 00; Docker running. (Lab 02 helps but is not required —
Part A builds the images.)

Everything here runs against the **local Docker daemon** on your Ubuntu VM —
no cloud account, no cost, and `terraform destroy` cleans up completely. The
workflow (`init → plan → apply → destroy`) is exactly what you would use
against AWS/Azure/GCP; only the provider block changes.

## Objectives

- Define infrastructure declaratively with Terraform.
- Practise `init`, `plan`, `apply`, state inspection and `destroy`.
- Understand variables, outputs, resource dependencies and the lock file.

## Part A — Build the Images

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

`init` downloads the Docker provider into `.terraform/` and records the
exact provider version in **`.terraform.lock.hcl`**. The lock file is
**committed to Git** — that is how every teammate (and CI) gets the same
provider version. `.terraform/` and state files are ignored; the lock file
is not. Look at it:

```bash
cat .terraform.lock.hcl
```

## Part C — Plan

```bash
terraform plan -out=tfplan
```

Review the plan. Terraform will create:

- One Docker network.
- One payment-service container.
- One order-service container that depends on the payment service.

Notice the `+` markers, and that `PAYMENT_SERVICE_URL` references the
payment container **by resource attribute** — that reference is what creates
the dependency ordering.

## Part D — Apply

```bash
terraform apply tfplan
```

## Part E — Verify on localhost

```bash
terraform output order_service_url
curl $(terraform output -raw order_service_url)/health
# Expected: {"status":"ok","env":"dev","build_id":"terraform-dev"}

curl -X POST $(terraform output -raw order_service_url)/orders \
  -H "Content-Type: application/json" \
  -d '{"item":"cappuccino","quantity":1,"price":4.5}'
# Expected: payment status "approved" — Terraform wired the two services together
```

## Part F — Inspect State

```bash
terraform state list
terraform state show docker_container.order_service
```

The state file maps Terraform resource names to real Docker container IDs.
Discuss: what happens if someone deletes a container manually? (Try it:
`docker rm -f tf-dev-order-service && terraform plan`.)

## Part G — Change and Re-apply

Edit `terraform.tfvars`, change `order_port` to `8092`, then:

```bash
terraform plan
terraform apply
curl http://localhost:8092/health
```

Terraform **replaces** the container to bind the new host port — the plan
told you so before you agreed to it.

## Part H — Clean Up

```bash
terraform destroy
docker ps -a --filter "name=tf-"
# Expected: empty
```

## Expected Output

- `terraform plan` shows three resources to create.
- `/health` on localhost returns env `dev`, build_id `terraform-dev`.
- `terraform destroy` leaves no `tf-*` containers.

## Verification Checklist

- [ ] `terraform init` downloads the Docker provider and writes the lock file.
- [ ] `terraform plan` shows the expected diff.
- [ ] Containers respond on localhost:8090 (order) after apply.
- [ ] State list shows three resources.
- [ ] `terraform destroy` leaves no `tf-*` containers.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `provider registry not found` | Run `terraform init` again (network hiccup). |
| Port already allocated | Change `order_port`/`payment_port` in `terraform.tfvars`. |
| Image not found | Re-run Part A. |
| State lock error | Only if no apply is running: delete `.terraform.tfstate.lock.info`. |

## Bonus — Configuration Management with Ansible (15 min)

Terraform *provisions*; Ansible *configures*. The `ansible-bonus/` folder
contains a playbook that configures this very VM over the local connection
and demonstrates idempotence — see `ansible-bonus/README.md`.

## Stretch Goal

Refactor the container resource into a reusable module
(`modules/container/{main,variables,outputs}.tf`) and call it twice from
`main.tf`. The capstone's `platform/terraform/` shows the finished pattern.
