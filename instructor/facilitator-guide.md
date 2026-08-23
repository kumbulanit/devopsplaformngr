# Facilitator Guide — DevOps & Platform Engineering

## Course at a Glance

- **Duration:** 2 days (08:30–17:30 each day)
- **Audience:** Beginner-to-intermediate IT professionals
- **Format:** Theory slides + hands-on labs, everything on each participant's
  **Ubuntu 24.04 VM**, all services on **localhost**
- **Deliverables:** PPTX decks (shared with participants), original diagrams,
  10 labs, platform canvas, quizzes

## Before the Course (critical)

1. **Pre-bake the VMs.** Clone the repo onto each VM and run
   `lab-setup/install-ubuntu24.sh`, then **log out/in once** so Docker group
   membership is active, then run `lab-setup/check-environment.sh` and keep
   the output. This removes ~45 minutes of install risk from Day 1 and
   pre-downloads the Trivy DB.
2. **Send the preflight a week ahead** if participants bring their own VMs:
   they run the installer + `check-environment.sh` and send you the PASS
   table as their ticket in.
3. VM sizing: **4 vCPU / 8 GB RAM / 30 GB disk** per participant. One VM per
   person — labs hardcode localhost ports (8080, 8001, 8090–8092, 9090,
   3000, 30080) and a kind cluster name, so a shared machine collides.
4. Day 1 needs outbound internet (image pulls, Terraform providers, GitHub).
   Lab 04 additionally needs participant GitHub accounts **or** `act`.

## Day 1 — Running Order

| Time | Module | Activity | Facilitator notes |
|------|--------|----------|-------------------|
| 08:30–09:00 | Welcome, logistics | — | Confirm every VM passed preflight. |
| 09:00–10:30 | 1: Intro to DevOps & Platform Eng | Lab 00 (30 min verify-only) | Lab 00 is verification, not installation — VMs are pre-baked. Teach tmux here. |
| 10:30–10:45 | *Break* | | |
| 10:45–12:15 | 2: Culture & Collaboration | Lab 01 (45 min) | Emphasise blameless language; the retro format returns in Lab 08's game day. |
| 12:15–13:00 | *Lunch* | | |
| 13:00–14:00 | 3: Tools & Technologies | **Toolchain mapping exercise** (15 min) | Pairs map their own company's tools onto the infinity-loop diagram, then tour this course's chain. |
| 14:00–15:30 | 4: Infrastructure as Code | Lab 05 (60 min) + Ansible bonus | First IaC exposure for many — walk `plan` output slowly. Bonus shows the config-management half of IaC. |
| 15:30–15:45 | *Break* | | |
| 15:45–17:15 | 5: CI/CD | Lab 04 (60 min) | The report-vs-gate Trivy discussion is the key takeaway. End the day with a green pipeline. |
| 17:15–17:30 | Day 1 quiz + Q&A | | |

## Day 2 — Running Order

| Time | Module | Activity | Facilitator notes |
|------|--------|----------|-------------------|
| 08:30–10:00 | 6: Microservices & Containers | Labs 02+03 as one guided block (75 min) | Docker → Compose progression; Lab 02 Parts C–D compress well if late. |
| 10:00–10:15 | *Break* | | |
| 10:15–11:45 | 6 cont.: Kubernetes | Lab 06 (75 min) | localhost:30080 NodePort demo lands well; keep the cluster alive for Lab 07/09. |
| 11:45–12:15 | 7: Security & Compliance theory | — | |
| 12:15–13:00 | *Lunch* | **Start capstone image pre-builds on your demo VM** | |
| 13:00–14:00 | 7 cont. | Lab 07 (60 min) | Raw-vs-rendered conftest demo is the aha moment. Teach triage, not panic. |
| 14:00–15:15 | 8: Observability & Reliability | Lab 08 (60 min + 15 min game day) | You are the saboteur in Part G: stop/pause the payment container per group. Insist on the 5-line postmortem. |
| 15:15–15:30 | *Break* | | |
| 15:30–16:15 | 9: Platform as a Product | **Platform canvas** (`instructor/platform-canvas.md`, 25 min + debrief) | Print or share the canvas; box 9 ("what we will NOT do") drives the best discussion. |
| 16:15–17:00 | 10: Capstone | Lab 09 guided (45 min) | Pre-create the kind cluster at lunch; the script then runs in ~5 min, leaving time for the handover doc. |
| 17:00–17:30 | 11: Summary & next steps, Day 2 quiz | — | Closing slides: recap the golden path they built, certification roadmap, first-week-back actions. |

## Common Pitfalls

1. **Docker group not active** — the #1 issue: `newgrp docker` or re-login.
2. **Port collisions** — labs use 8080, 8001, 8090–8092, 9090, 3000, 30080;
   `sudo ss -ltnp` finds the squatter.
3. **VM memory pressure** — kind + observability stack together need ~6 GB;
   have participants `docker compose down` finished labs.
4. **kind cluster created without `kind-config.yaml`** — localhost:30080
   dead; delete and recreate with the config.
5. **Stale images in kind** — after rebuilds, `kind load docker-image` again.

## Pacing Tips

- Keep every lecture under 20 minutes before a break or activity.
- Circulate constantly during labs; use "ask three before me".
- **Exit tickets:** at each break, one sticky per person — "one thing that
  clicked, one thing still fuzzy". Adjust the next block accordingly.
- Every lab ends with a Verification Checklist — completion = checklist done,
  not time elapsed.

## Suggested Talking Points

- DevOps is a learning culture; platform engineering makes it scalable.
- IaC is a safety and collaboration mechanism, not "scripts in Git" — the
  lock file and the plan diff are the collaboration features.
- A pipeline that cannot fail is a dashboard, not a gate.
- Security and observability must be platform **defaults**, not team chores.
- A platform is only successful if developers *choose* it.
- Everything ran on one Ubuntu VM's localhost — the workflow, not the
  infrastructure, is what transfers to cloud.

## Assessment

- Day 1 & Day 2 quizzes: multiple choice + short answer
  (`assessments/`, answers in `assessments/answers.md`).
- Practical component: the capstone Verification Checklist + the
  `PLATFORM-HANDOVER.md` document.

## Extension Ideas

- Cloud module: same Terraform lab against a free-tier account — swap the
  provider block, keep the workflow.
- Helm for Kubernetes packaging.
- Chaos engineering: scheduled game days with Chaos Mesh or Litmus.
- Mini-hackathon: teams ship a brand-new service down the golden path.
