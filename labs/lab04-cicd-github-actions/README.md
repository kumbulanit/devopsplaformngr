# Lab 04 — CI/CD with GitHub Actions

**Duration:** 75 minutes  
**Prerequisites:** Labs 00–03; a GitHub account (or `act` for local runs).

## Objectives

- Write a GitHub Actions workflow that tests, builds and scans a container image.
- Understand job dependencies, matrix builds and security scanning.
- Trigger the workflow from a pull request.

## Part A — Add the Workflow to Your Repository

1. Copy the workflow file into the course repository root (or into a real repo you own):

```bash
cp labs/lab04-cicd-github-actions/.github/workflows/ci.yml .github/workflows/ci.yml
```

2. Inspect the file. It has three jobs:
   - **test**: installs Python dependencies and runs `pytest`.
   - **build**: builds the Docker image with a SHA-based tag.
   - **security-scan**: runs Trivy to find CRITICAL and HIGH vulnerabilities.

3. Commit and push to GitHub:

```bash
git add .github/workflows/ci.yml
git commit -m "Add CI workflow for order service"
git push origin main
```

## Part B — Trigger the Workflow

1. Create a small change on a branch, for example add a comment in `main.py`.

```bash
git checkout -b ci-demo
echo "# CI demo branch" >> labs/app/main.py
git add labs/app/main.py
git commit -m "Demo change to trigger CI"
git push origin ci-demo
```

2. Open a pull request on GitHub.
3. Watch the Actions tab. The workflow should run automatically.
4. Wait for all three jobs to finish.

## Part C — Local Fallback with act

If you cannot use GitHub right now, run the workflow locally:

```bash
# macOS / Linux
brew install act

# In the repository root
act -j test
act -j build
act -j security-scan
```

`act` uses a container to emulate the GitHub Actions runner. The first run downloads a large image.

## Expected Output

- `test` job passes with `pytest` reporting green.
- `build` job creates an image named `order-service:<sha>`.
- `security-scan` job prints a Trivy report. Some base-image CVEs are normal; note them but do not panic.

## Verification Checklist

- [ ] Workflow file is committed in `.github/workflows/ci.yml`.
- [ ] Pull request triggers the workflow.
- [ ] `test`, `build` and `security-scan` jobs complete.
- [ ] Docker image is listed locally after `act` or on the runner.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Workflow does not trigger | Ensure the YAML is valid and the branch name matches the `on:` filters. |
| `pytest` cannot find tests | Confirm `working-directory: labs/app` is set and `pytest` is installed. |
| Trivy scan times out | Set `timeout: 10m0s` or allowlist low-severity findings. |
| `act` fails to pull image | Use a smaller image: `act -P ubuntu-latest=node:16-buster-slim`. |

## Stretch Goal

Add a job that pushes the image to GitHub Container Registry. This requires `GITHUB_TOKEN` (auto-provided) and a login step:

```yaml
- name: Log in to GHCR
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

Then tag and push the image.
