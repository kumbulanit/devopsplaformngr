# Workshop 1 — Setting Up a Basic DevOps Pipeline

**Slot:** Day 1, 15:30–17:15 (105 min) · **Theory it applies:** Module 5
**Guide:** this page orchestrates [Lab 04](../labs/lab04-cicd-github-actions/README.md)

You will build the left half of the pipeline diagram: a workflow that
**tests, builds, and security-scans** the order service, triggered by a
pull request — with a gate that can genuinely fail the build.

## Success criteria (this is "done")

- [ ] Pipeline triggers from a pull request (GitHub) or runs via `act` (local).
- [ ] `test` job green — `5 passed`.
- [ ] `build` job produces `order-service:<sha>`.
- [ ] You can explain, in one sentence each, the Trivy **report** step vs the
      **gate** step — and why the gate uses `--ignore-unfixed`.

## Core path (fits the slot)

| Step | Do | Time |
|------|----|------|
| 1 | Warm-up: run the tests yourself first — `cd labs/app && source .venv/bin/activate && pytest` | 5 min |
| 2 | Lab 04 **Part A**: copy the workflow, then **read it aloud in pairs** — find the job graph (`needs:`), `permissions:`, the pinned action version, and the two Trivy steps | 25 min |
| 3 | Lab 04 **Part B** (GitHub) *or* **Part C** (`act`): trigger it from a branch + PR | 35 min |
| 4 | Watch it run; when green, deliberately break a test (`assert body["quantity"] == 3`), push, watch it fail, revert | 25 min |
| 5 | Verification checklist + group discussion: what would you add before trusting this pipeline with production? | 15 min |

Step 4 is not optional filler — **seeing the pipeline catch a bad change is
the whole point of CI.**

## Stretch goals

- Push the image to GHCR (Lab 04 stretch — note the extra `permissions:`).
- Add a `conftest` job that policy-checks the rendered Kubernetes manifests
  (you will meet the policies in Module 7).

## If GitHub is unavailable

`act -j test` and `act -j build` run the same workflow in a local container
— the instructor demo will show the GitHub UI once for everyone.
