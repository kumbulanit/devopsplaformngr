# DevOps & Platform Engineering — 2-Day Training Course

A complete, ready-to-deliver training package for a beginner-to-intermediate
audience. **Every lab runs on a single Ubuntu 24.04 VM, entirely on
localhost** — no cloud account, no cost, full cleanup.

## Package Contents

```text
├── slides/                          # Theory PPTX decks (shared with participants)
├── diagrams/                        # Original PNG diagrams
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
├── workshops/                       # THE 3 hands-on workshops (Module 10)
├── lab-setup/                       # install-ubuntu24.sh + check-environment.sh
├── instructor/                      # Facilitator guide, solutions, canvas, theory demos
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

## Course Format

Matching the published outline: **Modules 1–9 are in-depth theory** (each
with one very basic demo from `instructor/theory-demos.md`), and
**Module 10's three workshops are the hands-on core** (`workshops/`):

1. **Setting up a basic DevOps pipeline** — Workshop 1 (Day 1 pm)
2. **Building and deploying a microservice** — Workshop 2 (Day 2 am)
3. **Implementing IaC for infrastructure** — Workshop 3 (Day 2 pm)

The capstone (Lab 09) ties all three together as one golden path. Labs 01,
07 and 08 remain as self-paced extras after the course.

## Agenda

### Day 1 — Foundations, Culture, Tools, IaC & CI/CD

| Time | Block | Hands-on element |
|-------------|--------------------------------------------|--------------------------------------|
| 08:30–09:00 | Welcome, logistics | Preflight confirmation |
| 09:00–10:15 | **Module 1**: Intro to DevOps & Platform Eng (theory) | Demo: preflight check (5 min) |
| 10:15–10:30 | *Break* | |
| 10:30–11:30 | **Module 2**: Culture & Collaboration (theory) | Westrum self-assessment (10 min) |
| 11:30–12:15 | **Module 3**: Tools & Technologies (theory) | Toolchain mapping + DORA (15 min) |
| 12:15–13:00 | *Lunch* | |
| 13:00–14:15 | **Module 4**: Infrastructure as Code (theory) | Demo: Ansible idempotence (10 min) |
| 14:15–15:15 | **Module 5**: CI/CD (theory) | Read a real workflow (10 min) |
| 15:15–15:30 | *Break* | |
| 15:30–17:15 | **WORKSHOP 1: Setting up a basic DevOps pipeline** | full hands-on (105 min) |
| 17:15–17:30 | Day 1 quiz + Q&A | |

### Day 2 — Containers, Security, Observability, Platform Thinking & Workshops

| Time | Block | Hands-on element |
|-------------|--------------------------------------------|--------------------------------------|
| 08:30–09:45 | **Module 6**: Microservices & Containerization (theory) | Demo: a container in 6 commands |
| 09:45–10:00 | *Break* | |
| 10:00–12:15 | **WORKSHOP 2: Building and deploying a microservice** | full hands-on (135 min) |
| 12:15–13:00 | *Lunch* | |
| 13:00–13:50 | **Module 7**: Security & Compliance (theory) | Demo: scan + one policy (10 min) |
| 13:50–14:30 | **Module 8**: Observability & Reliability (theory) | Demo: mini incident (15 min) |
| 14:30–15:30 | **WORKSHOP 3: Implementing IaC** | full hands-on (60 min) |
| 15:30–15:45 | *Break* | |
| 15:45–16:30 | **Module 9**: Platform as a Product (theory) | Platform canvas (25 min) |
| 16:30–17:10 | **Module 10**: Capstone — the golden path | run-capstone + handover doc |
| 17:10–17:30 | **Module 11**: Summary & next steps + Day 2 quiz | |

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

1. **Participants:** run the Quick Start, follow the theory demos in class,
   and use `workshops/` for the three hands-on workshops. Every workshop has
   success criteria — done means criteria checked. Labs 01/07/08 are yours
   to run self-paced after the course.
2. **Instructor:** read `instructor/facilitator-guide.md` (including the
   *Before the Course* section) and the speaker notes in the PPTX decks.
3. **Slides** are designed to be presented and then **shared with
   participants** — speaker notes carry the delivery guidance, the slides
   carry the content.
4. **Slide structure (both decks).** Every core topic in Modules 1–11 runs as
   a sequence: a **summary** slide (the talking points), one or two **Deep
   Dive** slides (every bullet expanded with mechanism, evidence, examples and
   anti-patterns), a **diagram**, and an **In Context** slide applying the
   topic to a central-bank environment. When running to time, present the
   summary + diagram and leave the Deep Dive / In Context slides as the
   participant reference; when the room wants depth, teach straight through.
   The *In Context* slides are illustrative teaching scenarios built from
   publicly known central-bank functions — they are not descriptions of any
   institution's internal systems, and the deck says so on the first one.

## Slides & Diagrams

The decks in `slides/` and the PNGs in `diagrams/` are the deliverables and are
committed as finished artefacts. The scripts that generate them are authoring
tools kept outside version control (see `.gitignore`) — this repository holds
the course material, not the machinery used to produce it.

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
