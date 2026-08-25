# Lab 04 — CI/CD Pipelines (locally with act, then on GitHub)

**Duration:** 60 minutes
**Prerequisites:** Lab 00 completed. Everything in Parts A–C runs **on your VM
with `act`** — no GitHub account and no repository access required. Part D is
an optional follow-up for anyone who wants to see the same workflow run on
GitHub's own runners.

## Objectives

- Read a real CI workflow and explain its job graph.
- **Run that pipeline locally** with `act`, on your own VM.
- Understand what a **security gate** really is — by making it fail, then fixing it.
- Know exactly what changes (and what does not) when the same file runs on GitHub.

## Why local first

The workflow file is the same artefact in both places. Running it locally
first means you get a 30-second feedback loop, no account, no network
dependency and no shared runner queue — so you can break things deliberately
and see what happens. That IS the lesson; GitHub is just a different machine
executing the same YAML.

---

## Part A — Read the Workflow (10 min)

1. Put the workflow where a runner expects to find it:

```bash
cd ~/devopsplatformengr
mkdir -p .github/workflows
cp labs/lab04-cicd-github-actions/.github/workflows/ci.yml .github/workflows/ci.yml
```

2. Open `.github/workflows/ci.yml` and find the three jobs:

   - **test** — installs Python dependencies and runs `pytest`.
   - **build** — builds the Docker image with a commit-SHA tag (`needs: test`).
   - **security-scan** — runs Trivy **twice**: a report step that never fails
     (`exit-code: "0"`) and a gate step that fails the build on any *fixable*
     CRITICAL vulnerability (`exit-code: "1"` + `ignore-unfixed: true`).

3. Answer these before you run anything:

   - Which jobs can run in parallel, and which must wait? (look for `needs:`)
   - Why is a scan that cannot fail the build **not** a gate?
   - What does `permissions: contents: read` protect you from?
   - Why is the Trivy action pinned to `@0.28.0` rather than `@master`?

> The last two are supply-chain practices from Module 7: a least-privilege
> token limits what a compromised step can do, and a pinned action means you
> run the code you reviewed, not whatever was pushed last night.

---

## Part B — Run the Pipeline on Your VM with act (20 min)

`act` reads `.github/workflows/` and executes the jobs inside a container that
emulates a GitHub runner. Same YAML, your machine.

1. Confirm `act` is available (the installer puts it there; see Lab 00):

```bash
act --version
```

2. List what `act` found in the workflow:

```bash
cd ~/devopsplatformengr
act -l
```

You should see the three jobs and their dependencies.

3. Run the jobs one at a time so you can watch each stage:

```bash
act -j test
```

> **First run only:** `act` downloads a runner image (~1 GB if it was not
> pre-pulled during setup). Later runs start in seconds.

```bash
act -j build
act -j security-scan
```

4. Now run the whole workflow the way a push would trigger it:

```bash
act push
```

Watch the job order: `test` completes before `build` and `security-scan`
start, because both declare `needs: test`.

### What to look for

| Job | Expected result |
|-----|-----------------|
| `test` | green, `5 passed` |
| `build` | produces `order-service:<sha>` — check with `docker images order-service` |
| `security-scan` | the report step prints a CVE table; the gate step passes while no CVE is both CRITICAL **and** fixable |

---

## Part C — Make the Gate Do Its Job (15 min)

A gate you have never seen fail is a gate you do not understand. Force it.

1. Temporarily make the gate strict — edit `.github/workflows/ci.yml` and in
   the **Trivy gate** step change:

```yaml
          severity: CRITICAL,HIGH
          ignore-unfixed: false
```

2. Re-run just the scan:

```bash
act -j security-scan
```

The job should now go **red**. Read the table: these are the findings that
were always there, previously filtered out because they are either lower
severity or have no released fix.

3. Discuss (this is the point of the lab):

   - How many of these could a developer actually fix **today**?
   - What happens to a team's respect for a red build if the gate fails on
     things nobody can fix?
   - Where would you set the threshold for the order service, and why?

4. Put the gate back to `severity: CRITICAL` and `ignore-unfixed: true`, and
   confirm it is green again:

```bash
act -j security-scan
```

> The two-step pattern — a broad **report** for visibility plus a narrow
> **gate** for enforcement — is what makes security in CI survive contact
> with a delivery deadline.

---

## Part D — Optional: the Same Workflow on GitHub

Everything above proved the pipeline works. This part changes only *where it
runs*. You need a GitHub account and a repository you can push to.

1. Commit the workflow and push it:

```bash
git add .github/workflows/ci.yml
git commit -m "Add CI workflow for order service"
git push origin main
```

2. Trigger it from a pull request — the way it will actually be used:

```bash
git checkout -b ci-demo
echo "# CI demo" >> labs/app/main.py
git add labs/app/main.py
git commit -m "Demo change to trigger CI"
git push origin ci-demo
```

3. Open a pull request on GitHub, then watch the **Actions** tab. You are
   looking at the same three jobs you just ran locally.

### What differs between act and GitHub

| | `act` (your VM) | GitHub Actions |
|---|---|---|
| Trigger | you type a command | push / pull request / schedule |
| Runner | a container on your VM | GitHub-hosted (or self-hosted) runner |
| Secrets | `--secret KEY=value` or `.secrets` file | repository / environment secrets |
| Approvals & environments | not enforced | environment protection rules, required reviewers |
| Caching, artifacts, matrix | partially supported | fully supported |
| Cost | free, offline | runner minutes |

The takeaway: the workflow file is portable, the *platform services around it*
are what you get from a hosted forge — and those services (environments,
approvals, secrets, artifact retention) are exactly what a platform team
provides on the golden path.

---

## Expected Output

- `act -l` lists three jobs with `test` as a dependency of the other two.
- `act push` runs the full graph green.
- You have seen the gate step fail on purpose and explained why the default
  threshold is *fixable CRITICAL* rather than everything.

## Verification Checklist

- [ ] Workflow copied to `.github/workflows/ci.yml`.
- [ ] `act -j test`, `act -j build` and `act -j security-scan` all run on your VM.
- [ ] You made the gate fail and restored it.
- [ ] You can explain the difference between the Trivy report step and gate step.
- [ ] (Optional) The same workflow ran on GitHub from a pull request.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `act: command not found` | `curl -fsSL https://raw.githubusercontent.com/nektos/act/master/install.sh \| sudo bash -s -- -b /usr/local/bin` |
| `act` cannot pull the runner image | `act -P ubuntu-latest=catthehacker/ubuntu:act-latest` |
| `act` cannot reach Docker | You must be in the `docker` group: `newgrp docker`, or log out and back in. |
| First run is very slow | It is downloading the runner image once; subsequent runs are fast. |
| `pytest` cannot find tests | Confirm `working-directory: labs/app` in the workflow. |
| Trivy gate fails unexpectedly | Read the table: is the CVE fixable? Updating the base image (`python:3.12-slim`) is the real fix — that IS the lesson. |
| Workflow does not trigger on GitHub (Part D) | The file must be at the repo root under `.github/workflows/`; check the `on:` branch filters. |

## Stretch Goals

**1. Run act with a secret** (local, no GitHub needed):

```bash
act -j test --secret MY_TOKEN=not-a-real-secret
```

Add a step that echoes `${{ secrets.MY_TOKEN }}` and watch GitHub-style secret
masking appear in the log. Never put a real credential on the command line.

**2. Push the image to GHCR** (needs Part D):

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

## Clean Up

```bash
# remove the local copy of the workflow if you do not want to commit it
rm -f ~/devopsplatformengr/.github/workflows/ci.yml

# act's runner images are large; reclaim the space when you are done
docker image ls | grep act
```
