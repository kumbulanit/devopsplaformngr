# Lab 01 — Culture and Collaboration with Git

**Duration:** 60 minutes  
**Prerequisites:** Lab 00 completed; basic Git familiarity.

## Objectives

- Practise a feature-branch workflow with pull requests.
- Experience code review as a collaboration tool.
- Conduct a short blameless retrospective.

## Scenario

You are part of a stream-aligned team that owns the order service. A new requirement arrives: the health endpoint must also return the service name. You will implement it using a branch, open a pull request, review a teammate's PR, and run a retrospective.

## Setup

```bash
cd labs/app
# Initialise a fresh local repository for the exercise
rm -rf .git
git init
git add .
git commit -m "Initial order and payment services"
```

## Part A — Feature Branch Workflow

1. Create and switch to a feature branch:

```bash
git checkout -b feature/health-service-name
```

2. Edit `main.py`. In the `HealthResponse` model, add `service_name: str`. In the `health()` function, return `"order-service"` as the service name.

3. Run the tests to make sure nothing broke:

```bash
source .venv/bin/activate
pytest
```

4. Commit the change with a clear message:

```bash
git add main.py
git commit -m "feat: add service_name to health endpoint"
```

## Part B — Pull Request Simulation

Because this is a local-only exercise, we will simulate a PR review with a second clone.

1. Create a bare remote and push your branch:

```bash
cd /tmp
git clone --bare /path/to/labs/app review-repo.git
cd /path/to/labs/app
git remote add local /tmp/review-repo.git
git push local feature/health-service-name
```

2. Clone a 'reviewer' copy:

```bash
cd /tmp
git clone review-repo.git reviewer-copy
cd reviewer-copy
git fetch --all
git checkout feature/health-service-name
```

3. As the reviewer, inspect the diff:

```bash
git diff main..feature/health-service-name
```

4. Leave review comments by creating a `REVIEW.md` file:

```markdown
# PR Review: feature/health-service-name

- ✅ Change is focused and easy to understand.
- ✅ Tests still pass.
- 💡 Consider adding a test for the new field.
```

5. Address the review suggestion: add a test in `test_app.py` that asserts `service_name` equals `"order-service"`. Commit and push.

6. Merge the branch:

```bash
git checkout main
git merge --no-ff feature/health-service-name -m "Merge feature/health-service-name"
git push local main
```

## Part C — Blameless Retrospective

In your group (or individually), spend 10 minutes answering these questions and record them in `RETRO.md`.

```markdown
# Blameless Retro — Lab 01

## What went well?
- Example: Feature branch kept main stable.

## What slowed us down?
- Example: Merge conflict in test_app.py.

## What will we try next time?
- Example: Run the test suite in CI before merging.

## What do we need from the platform team?
- Example: A templated PR checklist and CI pipeline.
```

## Expected Output

- A merge commit on `main` containing the health-endpoint change.
- `REVIEW.md` showing constructive feedback.
- `RETRO.md` with blameless reflection.

## Verification

```bash
git log --oneline --graph --all
pytest
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Merge conflict | Open the file, resolve markers, then `git add` and `git commit`. |
| `pytest` not found | Activate the virtual environment from Lab 00. |
| Reviewer clone cannot push | Ensure you pushed the branch to the bare repo first. |

## Stretch Goal

Configure a Git hook that prevents commits with `TODO` or `FIXME` unless a ticket ID is present:

```bash
cat > .git/hooks/commit-msg <<'EOF'
#!/bin/bash
if grep -E 'TODO|FIXME' "$1" && ! grep -E '#[0-9]+' "$1"; then
  echo "Commit message with TODO/FIXME must include a ticket ID"
  exit 1
fi
EOF
chmod +x .git/hooks/commit-msg
```
