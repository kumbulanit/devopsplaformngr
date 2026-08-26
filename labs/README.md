# Labs

## In the classroom — two labs

These are the labs the course actually runs. Each is one continuous story on
your own VM, split into parts with a checkpoint at the end of every part.

| Lab | Duration | Covers |
|-----|----------|--------|
| [Lab Day 1](lab-day1/README.md) — *Get a change to production safely* | ~2h15 | pipeline with `act`, security gate, Terraform, Ansible |
| [Lab Day 2](lab-day2/README.md) — *Run it like a service* | ~3h | Docker, Compose, Kubernetes, Trivy + policy, Prometheus/Grafana, game day |

Between them they touch every tool in the course: Git, GitHub Actions (via
`act`), Trivy, Conftest/OPA, Terraform, Ansible, Docker, Compose, kind,
kubectl, Prometheus and Grafana.

**Start here:** [Lab 00](lab00-environment-setup/README.md) — one script
installs the toolchain and one script verifies it. Do this before Day 1.

## After the course — self-paced

The numbered labs below are the long-form versions. Each part of the two
classroom labs is a condensed slice of one of these, so they are the natural
next step when you want the detail, the stretch goals and the explanation.

| Lab | Duration | Topic |
|-----|----------|-------|
| [00](lab00-environment-setup/README.md) | 30 min | Environment setup and preflight |
| [01](lab01-git-collaboration/README.md) | 45 min | Git collaboration, PR review, retrospective |
| [02](lab02-docker-basics/README.md) | 45 min | Docker images and containers |
| [03](lab03-compose-microservices/README.md) | 45 min | Compose, service discovery, scaling |
| [04](lab04-cicd-github-actions/README.md) | 60 min | CI/CD with `act`, then GitHub |
| [05](lab05-iac-terraform/README.md) | 60 min | Terraform (+ `ansible-bonus/`) |
| [06](lab06-kubernetes-kind/README.md) | 75 min | Kubernetes on kind |
| [07](lab07-devsecops/README.md) | 60 min | Scanning, policy as code, triage |
| [08](lab08-observability/README.md) | 60 min | Metrics, dashboards, SLOs, game day |
| [09](lab09-capstone/README.md) | 45–90 min | The full golden path, end to end |

The three `workshops/` guides orchestrate the numbered labs into longer
blocks — useful if you are re-running the material with more time than a
two-day course allows.

## Ground rules for every lab

- Start from the repository root: `cd "$COURSE_HOME"`.
- If `COURSE_HOME` is unset: `find ~ -maxdepth 4 -name lab-setup -type d`,
  then export it to the directory containing `lab-setup`.
- Everything runs on **localhost**. No cloud account, no shared infrastructure.
- Something missing? Re-run `./lab-setup/install-ubuntu24.sh` — it installs
  only what is absent and is safe to run repeatedly.
- "Done" means the checkpoint boxes are ticked, not that the time is up.
