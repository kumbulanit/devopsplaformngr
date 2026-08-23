# Quiz Answers

## Day 1 Answers

1. **CALMS** stands for Culture, Automation, Lean, Measurement, Sharing. It is a model that reminds organisations that DevOps is a balanced transformation, not just automation.

2. Platform engineering provides self-service tooling, templates and guard rails so developers do not have to learn low-level infrastructure details.

3. Any three of: source control, CI/CD, IaC, containers, observability, secrets management, collaboration/communication.

4. **Declarative** IaC describes the desired end state and lets the tool converge reality to it. **Imperative** IaC lists exact commands to execute in sequence.

5. The state file maps Terraform resources to real-world IDs and tracks dependencies so Terraform can plan accurate diffs and avoid duplication.

6. **Continuous Integration** merges code frequently and validates it with automated tests. **Continuous Delivery** keeps code in a deployable state and can deploy to production on demand (human decision); continuous deployment does so automatically.

7. Benefits include isolated feature work, code review, easier rollbacks, and safer collaboration on a shared main branch.

8. A blameless postmortem focuses on system and process improvements after an incident, not on blaming individuals. It encourages learning and honest reporting.

9. Finding vulnerabilities earlier is faster and cheaper to fix. It also prevents insecure artefacts from ever reaching production.

10. Platform adoption rate, time-to-first-service, developer-experience score, deployment frequency, or reduction in toil/support tickets.

## Day 2 Answers

1. A **microservice** is a small, independently deployable service focused on a bounded context. Benefit: team autonomy and independent scaling. Cost: distributed-system complexity.

2. API server, etcd, scheduler, controller manager.

3. A Kubernetes Service provides stable networking and load balancing to a set of Pods matching a label selector.

4. **Shifting security left** means integrating security checks and practices as early as possible in the software lifecycle, starting at design and coding.

5. Examples: Open Policy Agent / Conftest, Terraform Sentinel, Checkov, Falco, `trivy config`, policy-as-code in CI/CD.

6. Metrics, logs, traces.

7. An **SLO** (Service Level Objective) defines the target reliability for a service. The **error budget** is the allowable unreliability over a window; exhausting it signals a pause on risky changes.

8. Detect → Triage → Mitigate → Resolve → Postmortem → Remediate.

9. Treating the platform as a product ensures it has users, a backlog, good documentation, UX, metrics and funding — which drives adoption and value.

10. The **golden path** provided a standard, supported workflow (CI/CD, IaC, Kubernetes manifests) so the stream-aligned team could deploy quickly and safely without reinventing the toolchain.
