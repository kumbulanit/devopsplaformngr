# DevOps & Platform Engineering — 2-Day Training Course

A complete, ready-to-deliver training package for a beginner-to-intermediate audience.

## Package Contents

```text
├── slides/                           # Theory PPTX decks
│   ├── DevOps-PlatformEngineering-Day1.pptx
│   └── DevOps-PlatformEngineering-Day2.pptx
├── diagrams/                         # Original PNG diagrams
│   ├── build_diagrams.py
│   └── *.png
├── labs/                             # Hands-on labs
│   ├── lab00-environment-setup/
│   ├── lab01-git-collaboration/
│   ├── lab02-docker-basics/
│   ├── lab03-compose-microservices/
│   ├── lab04-cicd-github-actions/
│   ├── lab05-iac-terraform/
│   ├── lab06-kubernetes-kind/
│   ├── lab07-devsecops/
│   ├── lab08-observability/
│   └── lab09-capstone/
├── app/                              # Shared sample microservice
├── instructor/                       # Facilitator guide and solutions
└── assessments/                      # Day 1 & Day 2 quizzes + answers
```

## Agenda

### Day 1 — Foundations, Culture, IaC & CI/CD

| Time        | Topic                                    | Activity / Lab                     |
|-------------|------------------------------------------|------------------------------------|
| 08:30–09:00 | Welcome, course goals, logistics         |                                    |
| 09:00–10:30 | Module 1: Intro to DevOps & Platform Eng | Lab 00: Environment setup          |
| 10:30–10:45 | *Break*                                  |                                    |
| 10:45–12:15 | Module 2: Culture & Collaboration        | Lab 01: Git collaboration exercise |
| 12:15–13:00 | *Lunch*                                  |                                    |
| 13:00–14:00 | Module 3: Tools & Technologies           | Tooling demo / architecture tour   |
| 14:00–15:30 | Module 4: Infrastructure as Code         | Lab 05: Terraform IaC              |
| 15:30–15:45 | *Break*                                  |                                    |
| 15:45–17:30 | Module 5: CI/CD                          | Lab 04: GitHub Actions pipeline    |

### Day 2 — Containers, Security, Observability & Platform Thinking

| Time        | Topic                                          | Activity / Lab                          |
|-------------|------------------------------------------------|-----------------------------------------|
| 08:30–10:00 | Module 6: Microservices & Containerization     | Labs 02 & 03: Docker & Compose          |
| 10:00–10:15 | *Break*                                        |                                         |
| 10:15–12:15 | Module 6 continued                             | Lab 06: Kubernetes on kind              |
| 12:15–13:00 | *Lunch*                                        |                                         |
| 13:00–14:30 | Module 7: Security & Compliance (DevSecOps)    | Lab 07: Scanning & policy as code       |
| 14:30–15:45 | Module 8: Observability & Reliability          | Lab 08: Prometheus/Grafana + SLOs       |
| 15:45–16:00 | *Break*                                        |                                         |
| 16:00–16:45 | Module 9: Platform as a Product                | Platform canvas / product thinking      |
| 16:45–17:30 | Module 10: Capstone workshop                   | Lab 09: End-to-end golden-path deploy   |

## Audience Assumptions

- Comfortable with the Linux command line (cd, ls, cat, grep, chmod).
- Basic Git experience (clone, commit, push, pull).
- No prior Docker, Kubernetes, Terraform or CI/CD experience required.

## Required Software

Install these **before the course** (detailed instructions in `labs/lab00-environment-setup/`):

- Git 2.40+
- Docker Desktop / Docker Engine + Docker Compose
- `kind` or `minikube`
- `kubectl`
- `terraform` 1.6+
- Python 3.10–3.13 and a code editor (VS Code recommended)
- (Optional) GitHub account for Actions; local fallback with `act` is documented.

All hands-on labs and the provided sample application containers are verified on **Ubuntu 24.04 LTS**.

## How to Use This Package

1. **Participants**: read `README.md`, complete Lab 00, then follow each lab's `README.md` in order.
2. **Instructor**: review `instructor/facilitator-guide.md` and speaker notes in the PPTX files.
3. **Regenerate assets**:
   - `cd diagrams && python3 build_diagrams.py`
   - `cd slides && python3 build_slides.py`

## Regenerating Materials

Use the virtual environment installed in this folder:

```bash
cd "/Users/kumbulani.tshuma/Documents/devops trainning/devopsplatformengr"
source .venv/bin/activate
python3 diagrams/build_diagrams.py
python3 slides/build_slides.py
```

## Verifying the Package on Ubuntu 24.04 LTS

A verification container validates that the labs and sample application run end-to-end on the latest Ubuntu LTS.

```bash
# Download tooling binaries (run once, or whenever you want newer versions)
cd verify
./prepare-binaries.sh
cd ..

# Build and run the verification container
# --network=host is required so the container can reach services published on the host
docker build -t devops-course-verify -f verify/Dockerfile .
docker run --rm --network=host -v /var/run/docker.sock:/var/run/docker.sock devops-course-verify
```

## License / Reuse

Training materials are original. Diagrams are generated programmatically by this repository.
