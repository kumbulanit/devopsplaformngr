# Workshop 1 — Setting Up a Basic DevOps Pipeline

**Slot:** Day 1, 15:30–17:15 (105 min) · **Theory it applies:** Module 5
**Guide:** this page orchestrates [Lab 04](../labs/lab04-cicd-github-actions/README.md)

You will build the left half of the pipeline diagram: a workflow that
**tests, builds, and security-scans** the order service — with a gate that can
genuinely fail the build. It runs **on your own VM** with `act`; pushing it to
GitHub is an optional last step, because the workflow file is the same
artefact either way.

## Success criteria (this is "done")

- [ ] Full workflow runs on your VM — `act push` executes all three jobs.
- [ ] `test` job green — `5 passed`.
- [ ] `build` job produces `order-service:<sha>`.
- [ ] You can explain, in one sentence each, the Trivy **report** step vs the
      **gate** step — and why the gate uses `--ignore-unfixed`.

## Core path (fits the slot)

| Step | Do | Time |
|------|----|------|
| 1 | Warm-up: run the tests yourself first — `cd labs/app && source .venv/bin/activate && pytest` | 5 min |
| 2 | Lab 04 **Part A**: copy the workflow, then **read it aloud in pairs** — find the job graph (`needs:`), `permissions:`, the pinned action version, and the two Trivy steps | 20 min |
| 3 | Lab 04 **Part B**: run it locally — `act -l`, then `act -j test`, `act -j build`, `act -j security-scan`, then `act push` for the whole graph | 30 min |
| 4 | Lab 04 **Part C**: make the gate fail on purpose, read the findings, restore it. Then break a test (`assert body["quantity"] == 3`), re-run, watch it fail, revert | 25 min |
| 5 | Verification checklist + group discussion: what would you add before trusting this pipeline with production? | 15 min |

Step 4 is not optional filler — **seeing the pipeline catch a bad change is
the whole point of CI.**

## Stretch goals

- Lab 04 **Part D**: push the workflow to GitHub and trigger it from a real
  pull request — the same YAML, someone else's runner. Needs an account.
- Push the image to GHCR (Lab 04 stretch — note the extra `permissions:`).
- Add a `conftest` job that policy-checks the rendered Kubernetes manifests
  (you will meet the policies in Module 7).

## Why local first

`act` executes the workflow in a container on the VM: a 30-second feedback
loop, no account, no network dependency, no shared runner queue — so people
can break the gate deliberately and watch it go red. The instructor shows the
GitHub Actions UI once for everyone; participants who want to run it there
themselves have Lab 04 Part D, which changes only *where* it runs.
