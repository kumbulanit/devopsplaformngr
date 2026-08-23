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

## Course Format (matches the sold outline)

Modules 1–9 = **in-depth theory**, each with one very basic demo
(`instructor/theory-demos.md`, 5–15 min). Module 10 = the **three hands-on
workshops** (`workshops/`) plus the capstone. Module 11 closes. The speaker
notes in the decks carry the depth — read them before delivering; they are
also the participant reference after the course.

## Day 1 — Running Order

| Time | Block | Facilitator notes |
|------|-------|-------------------|
| 08:30–09:00 | Welcome | Confirm every VM passed preflight before Module 1. |
| 09:00–10:15 | Module 1 theory | History → Three Ways → CALMS → platform engineering. Demo: preflight together. |
| 10:30–11:30 | Module 2 theory | Westrum + psychological safety + Conway. Exercise: self-assessment — keep it anonymous. |
| 11:30–12:15 | Module 3 theory | Categories not brands. Exercise: toolchain mapping; collect lead-time show of hands. |
| 13:00–14:15 | Module 4 theory | The deepest theory block. Demo: Ansible idempotence live — rehearse it. |
| 14:15–15:15 | Module 5 theory | Report-vs-gate is the key slide. Demo: read the workflow in pairs. |
| 15:30–17:15 | **Workshop 1** | Pipeline hands-on. Step 4 (break a test on purpose) is the payoff — do not cut it. |
| 17:15–17:30 | Quiz + Q&A | |

## Day 2 — Running Order

| Time | Block | Facilitator notes |
|------|-------|-------------------|
| 08:30–09:45 | Module 6 theory | Trade-offs honestly; 12-factor mapped to our app. Demo: container in 6 commands. |
| 10:00–12:15 | **Workshop 2** | The big one: Docker → Compose → kind. Keep the cluster alive for the capstone. |
| 13:00–13:50 | Module 7 theory | Scanner taxonomy + supply chain + triage. Demo: scan + raw-vs-rendered policy. |
| 13:50–14:30 | Module 8 theory | SLO/error budgets + burn rates. Demo: mini incident — you are the saboteur. |
| 14:30–15:30 | **Workshop 3** | Full Terraform loop + drift. Step 5 (cloud read-through) answers "why localhost?" |
| 15:45–16:30 | Module 9 theory | Product thinking. Exercise: platform canvas — debrief boxes 8 and 9. |
| 16:30–17:10 | Module 10 capstone | Pre-create cluster + pre-build images at lunch; script then runs in ~5 min. |
| 17:10–17:30 | Module 11 + quiz | Commitments round: one action for the first week back. |

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
