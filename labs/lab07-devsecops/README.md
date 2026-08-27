# Lab 07 — DevSecOps: Scanning & Policy as Code

**Duration:** 60 minutes
**Prerequisites:** Labs 00–06. Trivy and Conftest are already installed by
`lab-setup/install-ubuntu24.sh` (verify: `trivy --version`, `conftest --version`).

## Objectives

- Scan a container image for known vulnerabilities and learn to triage.
- Scan Terraform and Kubernetes files for misconfigurations.
- Enforce rules with policy as code (OPA/Conftest) — and see policy catch drift.

## Part A — Image Vulnerability Scan

Scan the order-service image from Lab 02:

```bash
trivy image --severity HIGH,CRITICAL order-service:lab02
```

Trivy compares each image layer against CVE databases. Expect findings in
the base image. **Triage, don't panic** — for each finding ask:

1. Is it *fixable* (a patched version exists)? → update the base image.
2. Is it reachable in our usage? → assess, maybe accept with an expiry date.
3. Neither? → `--ignore-unfixed` filters CVEs that have no fix yet:

```bash
trivy image --severity CRITICAL --ignore-unfixed order-service:lab02
```

That second command is the **gate condition** used in the Lab 04 pipeline —
a build should fail only on findings you can actually action.

## Part B — Repository Secret Scan

```bash
cd "$COURSE_HOME"
trivy fs --scanners secret .
```

Expected: clean. Now prove it works — plant a fake secret and re-scan:

```bash
echo 'aws_secret_access_key = "AKIAIOSFODNN7EXAMPLE1234"' > /tmp/leak-test/config.txt 2>/dev/null || \
  { mkdir -p /tmp/leak-test && echo 'aws_secret_access_key = "AKIAIOSFODNN7EXAMPLE1234"' > /tmp/leak-test/config.txt; }
trivy fs --scanners secret /tmp/leak-test
rm -rf /tmp/leak-test
```

## Part C — Infrastructure Misconfiguration Scan

```bash
trivy config labs/lab05-iac-terraform
trivy config labs/lab06-kubernetes-kind
```

Read the Kubernetes findings against the actual YAML. The manifests already
set a `securityContext` (non-root, dropped capabilities, read-only root
filesystem) and resource limits — many checks pass because Lab 06 was built
that way. For anything still flagged, decide: fix, or document why not.

## Part D — Policy as Code with OPA / Conftest

Policies live in `policy/`. Read the first one:

```bash
cat labs/lab07-devsecops/policy/labels.rego
```

```rego
package main

import rego.v1

deny contains msg if {
	input.kind == "Deployment"
	not input.metadata.labels.course
	msg := sprintf("Deployment %q must have a 'course' label", [input.metadata.name])
}
```

(That is modern Rego — OPA 1.0+ requires `import rego.v1` and the
`deny contains msg if` form; the older `deny[msg]` syntax no longer parses.)

**1. Test the raw manifests:**

```bash
conftest test labs/lab06-kubernetes-kind/deployment-*.yaml \
  --policy labs/lab07-devsecops/policy
# Expected: FAILURES — the raw files have no 'course' label
```

**2. Test what actually gets applied** — Kustomize adds the labels at render
time:

```bash
kubectl kustomize labs/lab06-kubernetes-kind | \
  conftest test - --policy labs/lab07-devsecops/policy
# Expected: PASS
```

This gap between raw files and rendered output is exactly why policies must
run against **what ships**, not what sits in the editor — and how policy
catches drift when someone bypasses the kustomization.

## Part E — Read a Policy, Then Watch It Bite

You are here to learn how policy-as-code works, not to learn Rego syntax, so
the policies are written for you. Read them, run them, break them.

`policy/no_latest_tag.rego` forbids `:latest` (and untagged) images. Verify
it against the manifests, then break it on purpose:

```bash
kubectl kustomize labs/lab06-kubernetes-kind | \
  conftest test - --policy labs/lab07-devsecops/policy

sed 's/order-service:lab02/order-service:latest/' \
  labs/lab06-kubernetes-kind/deployment-order.yaml | \
  conftest test - --policy labs/lab07-devsecops/policy
# Expected: failure from no_latest_tag.rego
```

## Part F — Where This Lives in CI

Open `labs/lab04-cicd-github-actions/.github/workflows/ci.yml` and find the
two Trivy steps: the **report** (exit-code 0, never blocks) and the **gate**
(exit-code 1 on fixable CRITICALs). A `conftest test` step against the
rendered manifests would slot in the same way. Discussion: which policies
belong in a *blocking* gate on day one, and which start as report-only?

## Expected Output

- Image scan lists vulnerabilities by severity; you can explain the triage.
- Secret scan is clean on the repo, and catches the planted secret.
- Conftest fails raw manifests, passes rendered ones, and rejects `:latest`.

## Verification Checklist

- [ ] `trivy image` completes and you triaged one finding aloud.
- [ ] Planted secret detected, then cleaned up.
- [ ] `trivy config` findings reviewed against the real YAML.
- [ ] Conftest raw-vs-rendered difference demonstrated.
- [ ] `no_latest_tag.rego` rejects a `:latest` image.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Trivy DB download slow | The installer pre-downloaded it; otherwise `--skip-db-update` after first run. |
| `conftest: command not found` | Re-run `lab-setup/install-ubuntu24.sh` (installs a pinned release). |
| Policy never triggers | Check `input.kind` capitalisation and that the YAML parses (`kubectl kustomize`). |
| `rego_parse_error` | You are using pre-1.0 syntax — see the `import rego.v1` note above. |

## Part G — A Third Policy: Resource Limits

A container with no memory limit can starve every other workload on the node,
so this is usually the first rule a platform team enforces. The policy is
already in `policy/require_memory_limits.rego` — read it, then prove it works:

```bash
cat labs/lab07-devsecops/policy/require_memory_limits.rego
```

It denies a Deployment whose containers omit `resources.limits.memory` or
`resources.requests.memory`. First confirm the real manifests pass:

```bash
kubectl kustomize labs/lab06-kubernetes-kind/ | \
  conftest test - --policy labs/lab07-devsecops/policy
# Expected: all tests pass
```

Now strip the memory limits out and watch it fail:

```bash
kubectl kustomize labs/lab06-kubernetes-kind/ \
  | sed '/^            memory: 256Mi$/d' \
  | conftest test - --policy labs/lab07-devsecops/policy
```

Expected:

```
FAIL - - main - Container "order" must set resources.limits.memory
FAIL - - main - Container "payment" must set resources.limits.memory
```

**Discussion:** this rule would block a real team's deploy. Would you ship it
as blocking on day one, or run it in report-only mode until the backlog of
existing services is fixed? What changes that answer?

## Stretch Goal

Add a rule of your own to `require_memory_limits.rego` — for example, denying
any container that does not set `readOnlyRootFilesystem: true`. The pattern to
copy is already in the file; change the field it looks for and the message.
