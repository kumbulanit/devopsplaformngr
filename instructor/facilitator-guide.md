# Facilitator Guide — DevOps & Platform Engineering

## Course at a Glance

- **Duration:** 2 days (08:30–17:30 each day)
- **Audience:** Beginner-to-intermediate IT professionals
- **Format:** Theory slides + hands-on labs, everything on each participant's
  **Ubuntu 24.04 VM**, all services on **localhost**
- **Deliverables:** PPTX decks (shared with participants), original diagrams,
  10 labs, platform canvas, quizzes
- **Deck layout (Day 1 and Day 2):** every core topic runs *summary → Deep
  Dive(s) → diagram → In Context (central-bank worked example)*. Presenting the summary
  and diagram slides keeps the module inside its timebox; the Deep Dive and
  In Context slides are written to be read afterwards as the participant
  reference, and carry the discussion prompts and exercises.

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
   Lab 04 runs entirely on the VM with `act` (installed by the setup script,
   runner image pre-pulled). GitHub accounts are only needed for Lab 04
   Part D, which is optional.

## Course Format (matches the sold outline)

Modules 1–9 = **in-depth theory**, each with one very basic demo
(`instructor/theory-demos.md`, 5–15 min). Module 10 = the **three hands-on
workshops** (`workshops/`) plus the capstone. Module 11 closes. The speaker
notes in the decks carry the depth — read them before delivering; they are
also the participant reference after the course.

## Day 1 — Running Order

**Present `DevOps-PlatformEngineering-Day1-Deliver.pptx` (58 slides).** The
full 141-slide deck is the participant reference — hand it out, do not
present it. Roughly 2 minutes per slide leaves room for discussion.

| Time | Block | Facilitator notes |
|------|-------|-------------------|
| 08:30–08:50 | Welcome + preflight | Confirm every VM passed `check-environment.sh` and `COURSE_HOME` is set. |
| 08:50–09:35 | Module 1 | 13 slides, 7 diagrams. Lead with the wall-of-confusion and cognitive-load pictures. |
| 09:35–10:00 | Module 2 | 9 slides. Westrum table + the 5-question self-score. Keep scoring private. |
| 10:15–10:40 | Module 3 | 7 slides. Toolchain map exercise — collect the empty boxes for Module 9. |
| 10:40–11:10 | Module 4 | 9 slides. Terraform plan output is the slide that matters. |
| 11:10–11:45 | Module 5 | 9 slides. Report-vs-gate diagram, then straight into the lab. |
| 11:45–12:30 | **Lab Day 1, Parts A–B** | App + tests, then the pipeline with `act`. First `act` run pulls the runner image — pre-pull it. |
| 13:15–15:30 | **Lab Day 1, Parts C–E** | Gate fail/fix, Terraform plan→apply→drift, Ansible `changed=0`. |
| 15:45–16:45 | Buffer / deeper dives | Overflow room. If ahead: tool profiles from the reference deck, or the SARB *In Context* slides. |
| 16:45–17:15 | Debrief + quiz | Part F wrap-up table; Day 1 quiz. |
| 17:15–17:30 | Q&A | |

## Day 2 — Running Order

**Present `DevOps-PlatformEngineering-Day2-Deliver.pptx` (66 slides, 42%
diagrams).**

| Time | Block | Facilitator notes |
|------|-------|-------------------|
| 08:30–08:45 | Recap | Yesterday's pipeline + IaC in 3 slides. Confirm Docker is running on every VM. |
| 08:45–09:40 | Module 6 | 18 slides, 9 diagrams — the heaviest block. Container-vs-VM and the K8s object map carry it. |
| 09:40–10:00 | Module 7 (part 1) | Shift-left + scanner taxonomy. Save policy-as-code for after the lab. |
| 10:15–12:30 | **Lab Day 2, Parts A–C** | Image build, Compose, then Kubernetes. Create the kind cluster before the break if bandwidth is tight. |
| 13:15–13:45 | Module 7 (part 2) + Module 8 | Policy as code, then SLOs and burn-rate alerting. |
| 13:45–15:45 | **Lab Day 2, Parts D–F** | Scanning, policy gate, Prometheus/Grafana, game day. Part F is the emotional peak — protect the time. |
| 16:00–16:40 | Module 9 | 9 slides. Platform canvas exercise; the ROI slide lands with senior attendees. |
| 16:40–17:10 | Module 11 + quiz | Commitments round: one action for the first week back. |
| 17:10–17:30 | Feedback + close | |

### If you are running behind

Cut in this order, and say what you are cutting and where to read it:

1. The *In Context* (central-bank) slides — they are in the reference deck.
2. Module 2 down to Westrum + psychological safety only.
3. Module 3 to the toolchain diagram plus the exercise.
4. Lab Day 2 Part B (Compose) — Part C covers service discovery again.

**Never cut:** Lab Day 1 Part C (breaking the gate) or Lab Day 2 Part F
(game day). Those two are where the learning actually lands.

## Common Pitfalls

1. **Docker group not active** — the #1 issue: `newgrp docker` or re-login.
2. **Port collisions** — labs use 8080, 8001, 8090–8092, 9090, 3000, 30080;
   `sudo ss -ltnp` finds the squatter.
3. **VM memory pressure** — kind + observability stack together need ~6 GB;
   have participants `docker compose down` finished labs.
4. **kind cluster created without `kind-config.yaml`** — localhost:30080
   dead; delete and recreate with the config.
5. **Stale images in kind** — after rebuilds, `kind load docker-image` again.
6. **A tool is missing on someone's VM** — just re-run
   `./lab-setup/install-ubuntu24.sh`. It checks every component and installs
   only what is absent (a re-run on a healthy VM downloads nothing), so it is
   the fastest repair during a lab. It exits non-zero and lists anything it
   still could not install.

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
