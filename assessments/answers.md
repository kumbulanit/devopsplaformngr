# Quiz Answers

## Day 1

### Section A
A1 **b** (Measurement) · A2 **b** · A3 **c** · A4 **c** · A5 **b**

### Section B

**B1.** Platform engineering provides self-service tooling, templates and
guardrails so developers do not have to learn low-level infrastructure
details (accept: golden paths, paved roads, abstraction of infra).

**B2.** The state file maps Terraform resources to real-world IDs so plans
show accurate diffs. In the lab, deleting `tf-dev-order-service` manually
made the next `terraform plan` show **1 to add** — Terraform detected the
drift between state and reality.

**B3.** Any two: isolated feature work, code review before merge, easier
rollback, main stays stable/deployable, CI runs before merge.

**B4.** A postmortem focused on system and process improvements rather than
individual blame; it matters because it encourages honest reporting and
learning, which prevents repeat incidents.

**B5.** Terraform **provisions** infrastructure (creates/destroys resources:
networks, containers, cloud instances); Ansible **configures** existing
machines (packages, files, services). Accept "provisioning vs configuration
management".

## Day 2

### Section A
A1 **b** · A2 **b** · A3 **b** · A4 **b** · A5 **b**

### Section B

**B1.** Benefit: independent deployment/scaling, team autonomy, fault
isolation. Cost: distributed-system complexity (network failures, service
discovery, observability overhead, eventual consistency).

**B2.** Integrating security checks as early as possible in the lifecycle.
Examples from the labs: Trivy scan in the CI pipeline (Lab 04), the fixable-
CRITICAL gate, secret scanning the repo, Conftest policy on manifests before
deploy, non-root containers / securityContext caught by `trivy config`.

**B3.** Accept any real observed signal: order responses flipped payment
status to `unavailable`; the payment-service target went DOWN on the
Prometheus targets page; error/timeout patterns in the payment logs; a rate
change in the metrics. Key point: detection came from telemetry, not from
being told.

**B4.** The allowable amount of unreliability within the SLO window (1% for
a 99% SLO). When exhausted, risky feature releases pause and the team
prioritises reliability work until the budget recovers.

**B5.** Any two: how to write a CI/CD pipeline, how to configure
Trivy/security gates, Kubernetes manifest details (probes, securityContext,
labels), Terraform module internals, how images get into the cluster, how
monitoring gets wired up.
