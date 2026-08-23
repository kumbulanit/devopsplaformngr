# Workshop 3 — Implementing Infrastructure as Code

**Slot:** Day 2, 14:30–15:30 (60 min) · **Theory it applies:** Module 4
**Guide:** orchestrates [Lab 05](../labs/lab05-iac-terraform/README.md)
(+ [Ansible bonus](../labs/lab05-iac-terraform/ansible-bonus/README.md))

You will run the **complete IaC loop** — init, plan, apply, verify, drift,
destroy — declaring real infrastructure (network + two containers) on your
VM's local Docker daemon. The workflow is identical for cloud; only the
provider changes.

## Success criteria (this is "done")

- [ ] `terraform plan` shows exactly **3 resources to add**.
- [ ] After apply: `curl localhost:8090/health` → `env: "dev"`, `build_id: "terraform-dev"`.
- [ ] **Drift detected**: after manually deleting a managed container, `plan` shows `1 to add`.
- [ ] `terraform destroy` leaves **zero** `tf-*` containers.

## Core path (fits the slot)

| Step | Do | Time |
|------|----|------|
| 1 | **Lab 05** Parts A–B: build images (skip if done in W2), `cp tfvars.example`, `terraform init`; **read `.terraform.lock.hcl`** — why is it committed? | 10 min |
| 2 | Parts C–E: `plan -out=tfplan` (read the diff aloud), `apply`, verify on `localhost:8090` — note the order→payment wiring Terraform created | 20 min |
| 3 | Part F + drift: `terraform state list`, then `docker rm -f tf-dev-order-service && terraform plan` → watch Terraform notice | 10 min |
| 4 | Part H: `destroy`, confirm nothing is left | 5 min |
| 5 | **Cloud read-through**: open `providers.tf` and `main.tf` — identify the ONLY things that change for AWS (provider block + resource types). The loop, state, plan and review workflow are identical | 10 min |
| 6 | Verification checklist | 5 min |

## Bonus (if time / fast finishers) — the other half of IaC

The [Ansible bonus](../labs/lab05-iac-terraform/ansible-bonus/README.md):
run the playbook against the VM's localhost **twice** and watch
`changed=N` become `changed=0` — idempotence made visible. 15 min.

## Stretch goals

- Lab 05 Part G: change `order_port` in tfvars → plan → apply → the container is *replaced*, and plan told you first.
- Refactor into a module (the capstone's `platform/terraform/` shows the finished pattern).
