# Lab 01 — Culture and Collaboration with Git

**Duration:** 45 minutes
**Prerequisites:** Lab 00 completed; basic Git familiarity.

## Objectives

- Practise a feature-branch workflow with pull requests.
- Experience code review as a collaboration tool.
- Conduct a short blameless retrospective.

## Scenario

You are part of a stream-aligned team that owns the order service. A new
requirement arrives: the health endpoint must also return the service name.
You will implement it on a branch, simulate a pull-request review, and run a
retrospective.

## Setup — Work in a Copy

We practise on a **copy** of the app in `/tmp`, so the course repository
itself is never touched (never run `git init` or `rm -rf .git` inside a
repository you care about):

```bash
mkdir -p /tmp/lab01 && cp -r labs/app /tmp/lab01/app
cd /tmp/lab01/app
rm -rf .venv .pytest_cache __pycache__
git init -b main
git add .
git commit -m "Initial order and payment services"
```

> `git init -b main` names the default branch `main` explicitly, so the lab
> works identically on every machine regardless of Git configuration.

The tests still run from the course venv:

```bash
source "$COURSE_HOME"/labs/app/.venv/bin/activate
pytest
# Expected: 5 passed
```

## Part A — Feature Branch Workflow

1. Create and switch to a feature branch:

```bash
git checkout -b feature/health-service-name
```

2. Make the change. Two edits to `main.py` — add the field to the response
   model, and populate it in the handler. Copy and paste:

```bash
# add the field to the HealthResponse model
python3 - <<'PY'
from pathlib import Path
p = Path("main.py"); s = p.read_text()
s = s.replace(
    'class HealthResponse(BaseModel):\n    status: str\n    env: str\n    build_id: str',
    'class HealthResponse(BaseModel):\n    status: str\n    env: str\n    build_id: str\n    service_name: str')
s = s.replace(
    '    return HealthResponse(\n        status="ok",',
    '    return HealthResponse(\n        status="ok",\n        service_name="order-service",')
p.write_text(s)
print("main.py patched")
PY

# see exactly what you changed
git diff main.py
```

   You should see two added lines: `service_name: str` in the model and
   `service_name="order-service"` in the return.

3. Run the tests to make sure nothing broke:

```bash
pytest
```

4. Commit with a clear message:

```bash
git add main.py
git commit -m "feat: add service_name to health endpoint"
```

## Part B — Pull Request Simulation

Because this is a local-only exercise, we simulate the PR review with a bare
"remote" and a reviewer clone.

1. Create a bare remote and push your branch:

```bash
git clone --bare /tmp/lab01/app /tmp/lab01/review-repo.git
cd /tmp/lab01/app
git remote add local /tmp/lab01/review-repo.git
git push local feature/health-service-name
```

2. Clone a reviewer copy:

```bash
cd /tmp/lab01
git clone review-repo.git reviewer-copy
cd reviewer-copy
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

5. Back in `/tmp/lab01/app`, address the reviewer's suggestion by adding the
   test. Copy and paste:

```bash
cd /tmp/lab01/app
cat >> test_app.py <<'PY'


def test_health_reports_service_name():
    body = client.get("/health").json()
    assert body["service_name"] == "order-service"
PY

pytest                       # expected: 6 passed
git add test_app.py
git commit -m "test: cover the new service_name field"
git push local feature/health-service-name
```

6. Merge the branch:

```bash
cd /tmp/lab01/app
git checkout main
git merge --no-ff feature/health-service-name -m "Merge feature/health-service-name"
git push local main
```

## Part C — Blameless Retrospective

In your group (or individually), spend 10 minutes on these questions and
record the answers in `RETRO.md`:

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
| Merge conflict | Open the file, resolve the markers, then `git add` and `git commit`. |
| `pytest` not found | Activate the venv: `source "$COURSE_HOME"/labs/app/.venv/bin/activate`. |
| Reviewer clone cannot see the branch | Push the branch to the bare repo first (Part B step 1). |
| `main` vs `master` mismatch | Re-run setup with `git init -b main`. |

## Stretch Goal

Configure a Git hook that rejects commit messages containing `TODO` or
`FIXME` without a ticket ID:

```bash
cat > .git/hooks/commit-msg <<'EOF'
#!/bin/bash
if grep -qE 'TODO|FIXME' "$1" && ! grep -qE '#[0-9]+' "$1"; then
  echo "Commit message with TODO/FIXME must include a ticket ID (e.g. #123)"
  exit 1
fi
EOF
chmod +x .git/hooks/commit-msg
```

## Clean Up

```bash
rm -rf /tmp/lab01
```
