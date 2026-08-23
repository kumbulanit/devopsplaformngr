# Facilitator Guide — DevOps & Platform Engineering

## Course at a Glance

- **Duration:** 2 days (8:30–17:30 each day)
- **Audience:** Beginner-to-intermediate IT professionals
- **Format:** Theory slides + hands-on labs
- **Key deliverables:** PPTX decks, original diagrams, 10 labs, quizzes

## Day 1 — Running Order

| Module | Slides | Activity | Notes for Facilitator |
|--------|--------|----------|----------------------|
| 1 | 4 slides + title | Lab 00 environment setup | Keep this tight; pair strugglers with early finishers. |
| 2 | 4 slides | Lab 01 Git collaboration + retro | Emphasise blameless language. Use a real incident prompt if helpful. |
| 3 | 3 slides | Tooling demo | Show your own CI/CD dashboard or a live pipeline if possible. |
| 4 | 4 slides | Lab 05 Terraform | Walk through `plan` carefully; this is many learners' first IaC exposure. |
| 5 | 4 slides | Lab 04 GitHub Actions | If GitHub is unavailable, use `act`. End day with a green pipeline. |

## Day 2 — Running Order

| Module | Slides | Activity | Notes for Facilitator |
|--------|--------|----------|----------------------|
| 6 | 6 slides | Labs 02, 03, 06 | Docker → Compose → Kubernetes progression builds confidence. |
| 7 | 4 slides | Lab 07 DevSecOps | Expect vulnerability findings; teach triage, not panic. |
| 8 | 4 slides | Lab 08 observability | Make sure participants see a non-empty Grafana panel. |
| 9 | 3 slides | Platform canvas exercise | Small groups fill out a platform canvas. |
| 10 | 3 slides | Lab 09 capstone | Bring it all together; celebrate completion. |

## Common Pitfalls

1. **Docker Desktop not started.** Check in Lab 00; many issues later stem from this.
2. **Port collisions.** Labs use 8080, 8001, 8090, 8091, 9090, 3000. If a participant has local services, remap ports.
3. **kind out of memory.** Recommend at least 4 GB RAM for Docker Desktop.
4. **Terraform docker provider issues.** Ensure Docker daemon is reachable; on macOS use the default Docker socket.
5. **GitHub Actions rate limits / `act` image download.** Have participants work in pairs or use a local runner fallback.

## Pacing Tips

- Day 1 is concept-heavy; keep lectures under 20 minutes before a break or activity.
- Day 2 is lab-heavy; circulate constantly and use the 'ask three before me' rule.
- Reserve 15 minutes at the end of each day for a quiz and Q&A.

## Suggested Talking Points

- DevOps is a learning culture; platform engineering makes that culture scalable.
- IaC is not just 'scripts in Git' — it is a safety and collaboration mechanism.
- CI/CD pipelines are products; iterate on them with the same rigour as product features.
- Security and observability must be defaults provided by the platform, not optional extras.
- A platform is only successful if developers choose to use it.

## Assessment

- Day 1 quiz: 10 questions (mix of multiple choice and short answer).
- Day 2 quiz: 10 questions.
- Answers are in `assessments/answers.md`.

## Extension Ideas

- Add a cloud module using a free-tier AWS/Azure/GCP account.
- Introduce Helm for Kubernetes packaging.
- Run a chaos-engineering experiment with Chaos Mesh or Litmus.
- Host a mini-hackathon where teams build a new service on the golden path.
