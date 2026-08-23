# Lab 04 — CI/CD with GitHub Actions

**Duration:** 60 minutes
**Prerequisites:** Lab 00 (images are built by the pipeline itself); a GitHub
account, or `act` for fully local runs on the VM.

## Objectives

- Read and run a GitHub Actions workflow that tests, builds and scans a container image.
- Understand job dependencies and what a **security gate** really is.
- Trigger the workflow from a pull request.

## Part A — Add the Workflow to Your Repository

1. Copy the workflow file into the repository's workflow directory:

```bash
mkdir -p .github/workflows
cp labs/lab04-cicd-github-actions/.github/workflows/ci.yml .github/workflows/ci.yml
```

2. Open the file and find the three jobs:
   - **test** — installs Python dependencies and runs `pytest`.
   - **build** — builds the Docker image with a commit-SHA tag (`needs: test`).
   - **security-scan** — runs Trivy **twice**: a report step that never fails
     (`exit-code: 0`) and a gate step that fails the build on any *fixable*
     CRITICAL vulnerability (`exit-code: 1` + `ignore-unfixed`). Discuss: why
     is a scan that cannot fail the build not a gate?

   Also note the `permissions: contents: read` block (least-privilege token)
   and that the Trivy action is **pinned to a version tag**, not `@master` —
   both supply-chain practices from Module 7.

3. Commit and push to your own GitHub repository:

```bash
git add .github/workflows/ci.yml
git commit -m "Add CI workflow for order service"
git push origin main
```

## Part B — Trigger the Workflow from a PR

1. Create a small change on a branch:

```bash
git checkout -b ci-demo
echo "# CI demo" >> labs/app/main.py
git add labs/app/main.py
git commit -m "Demo change to trigger CI"
git push origin ci-demo
```

2. Open a pull request on GitHub, watch the **Actions** tab, and wait for the
   jobs to finish.

## Part C — Local Fallback with act

No GitHub access? Run the same workflow **on the VM**:

```bash
# install once (also the Lab 00 stretch goal)
curl -fsSL https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash -s -- -b /usr/local/bin

# from the repository root
act -j test
act -j build
```

`act` emulates the GitHub runner in a container; the first run downloads a
large runner image. The `security-scan` job also works but downloads the
Trivy DB inside the runner — expect it to be slower.

## Expected Output

- `test` job green with `5 passed`.
- `build` job produces `order-service:<sha>`.
- `security-scan`: the report step lists base-image CVEs (normal — triage,
  don't panic); the gate step passes as long as none of them are fixable
  CRITICALs.

## Verification Checklist

- [ ] Workflow file committed at `.github/workflows/ci.yml`.
- [ ] A pull request triggers the workflow.
- [ ] You can explain the difference between the Trivy report step and gate step.
- [ ] All jobs complete (on GitHub or via `act`).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Workflow does not trigger | YAML must be at repo root under `.github/workflows/`; check the `on:` branch filters. |
| `pytest` cannot find tests | Confirm `working-directory: labs/app` in the workflow. |
| Trivy gate fails | Read the table: is the CVE fixable? Update the base image (`python:3.12-slim`) and re-run — that IS the lesson. |
| `act` fails to pull runner image | `act -P ubuntu-latest=catthehacker/ubuntu:act-latest` |

## Stretch Goal

Add a job that pushes the image to GitHub Container Registry using the
auto-provided `GITHUB_TOKEN`:

```yaml
    permissions:
      contents: read
      packages: write
    steps:
      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
```

Then tag the image as `ghcr.io/<your-user>/order-service:<sha>` and push it.
Note the job-level `permissions` — the default token cannot write packages.
