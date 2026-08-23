# DevOps & Platform Engineering — 2-Day Training Course

A complete, ready-to-deliver training package for a beginner-to-intermediate
audience. **Every lab runs on a single Ubuntu 24.04 VM, entirely on
localhost** — no cloud account, no cost, full cleanup.

## Package Contents

```text
├── slides/                          # Theory PPTX decks (shared with participants)
├── diagrams/                        # Original PNG diagrams + generator
├── labs/
│   ├── app/                         # Shared sample microservices (order + payment)
│   ├── lab00-environment-setup/     # Verify the pre-baked toolchain
│   ├── lab01-git-collaboration/
│   ├── lab02-docker-basics/
│   ├── lab03-compose-microservices/
│   ├── lab04-cicd-github-actions/
│   ├── lab05-iac-terraform/         # + ansible-bonus/ (config management)
│   ├── lab06-kubernetes-kind/
│   ├── lab07-devsecops/
│   ├── lab08-observability/         # + mini game day
│   └── lab09-capstone/              # Golden-path end-to-end
├── lab-setup/                       # install-ubuntu24.sh + check-environment.sh
├── instructor/                      # Facilitator guide, solutions, platform canvas
├── assessments/                     # Day 1 & 2 quizzes + answers
├── tools/                           # Extract & run every lab command (QA harness)
└── verify/                          # End-to-end verification container
```

## Quick Start (participants)

```bash
git clone <this-repo> ~/devopsplatformengr
cd ~/devopsplatformengr
./lab-setup/install-ubuntu24.sh     # installs the full toolchain
# log out and back in (docker group), then:
./lab-setup/check-environment.sh    # must end with: all required checks passed
```

Then follow `labs/lab00-environment-setup/README.md` and each lab in order.

## Agenda

### Day 1 — Foundations, Culture, IaC & CI/CD

| Time | Module | Activity / Lab |
|-------------|------------------------------------------|------------------------------------|
| 08:30–09:00 | Welcome, course goals, logistics | Preflight confirmation |
| 09:00–10:30 | 1: Intro to DevOps & Platform Engineering | Lab 00: Environment verification |
| 10:30–10:45 | *Break* | |
| 10:45–12:15 | 2: Culture & Collaboration | Lab 01: Git collaboration + retro |
| 12:15–13:00 | *Lunch* | |
| 13:00–14:00 | 3: Tools & Technologies | Toolchain mapping exercise |
| 14:00–15:30 | 4: Infrastructure as Code | Lab 05: Terraform (+ Ansible bonus) |
| 15:30–15:45 | *Break* | |
| 15:45–17:15 | 5: CI/CD | Lab 04: GitHub Actions pipeline |
| 17:15–17:30 | Day 1 quiz + Q&A | |

### Day 2 — Containers, Security, Observability & Platform Thinking

| Time | Module | Activity / Lab |
|-------------|------------------------------------------------|----------------------------------------|
| 08:30–10:00 | 6: Microservices & Containerization | Labs 02+03: Docker & Compose |
| 10:00–10:15 | *Break* | |
| 10:15–11:45 | 6 cont.: Kubernetes | Lab 06: Kubernetes on kind |
| 11:45–12:15 | 7: Security & Compliance theory | |
| 12:15–13:00 | *Lunch* | |
| 13:00–14:00 | 7 cont. (DevSecOps) | Lab 07: Scanning & policy as code |
| 14:00–15:15 | 8: Observability & Reliability | Lab 08: Prometheus/Grafana + game day |
| 15:15–15:30 | *Break* | |
| 15:30–16:15 | 9: Platform as a Product | Platform canvas exercise |
| 16:15–17:00 | 10: Capstone | Lab 09: Golden-path deploy |
| 17:00–17:30 | 11: Summary & next steps + Day 2 quiz | |

## Audience Assumptions

- Comfortable with the Linux command line (cd, ls, cat, grep, chmod).
- Basic Git experience (clone, commit, push, pull).
- No prior Docker, Kubernetes, Terraform or CI/CD experience required.

## Environment

One **Ubuntu 24.04 LTS VM per participant** (4 vCPU / 8 GB RAM / 30 GB disk
recommended). The full toolchain — Git, Docker Engine + Compose, kind,
kubectl, Terraform, Trivy, Conftest, tmux, jq, Python — is installed by
`lab-setup/install-ubuntu24.sh` and verified by
`lab-setup/check-environment.sh`. Lab 04 optionally uses a GitHub account
(local fallback with `act` is documented).

## How to Use This Package

1. **Participants:** run the Quick Start, then follow each lab's `README.md`
   in agenda order. Every lab ends with a Verification Checklist — done means
   checklist done.
2. **Instructor:** read `instructor/facilitator-guide.md` (including the
   *Before the Course* section) and the speaker notes in the PPTX decks.
3. **Slides** are designed to be presented and then **shared with
   participants** — speaker notes carry the delivery guidance, the slides
   carry the content.

## Regenerating Slides & Diagrams (authors only)

Authoring dependencies are separate from the student toolchain:

```bash
python3 -m venv .venv-author
source .venv-author/bin/activate
pip install -r slides/requirements-authoring.txt
python3 diagrams/build_diagrams.py     # regenerates diagrams/*.png
python3 slides/build_slides.py         # regenerates both PPTX decks (idempotent)
```

## Quality Checks

```bash
# Extract every command from the lab READMEs and execute them, writing a
# pass/fail report (run this on a disposable Ubuntu VM, not your laptop):
./tools/run_lab_commands.sh

# Full end-to-end verification in a container (uses the host Docker daemon):
cd verify && ./prepare-binaries.sh && cd ..
docker build -t devops-course-verify -f verify/Dockerfile .
docker run --rm --network=host -v /var/run/docker.sock:/var/run/docker.sock devops-course-verify
```

## License / Reuse

Training materials are original. Diagrams are generated programmatically by
this repository.
