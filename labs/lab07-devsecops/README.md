# Lab 07 — DevSecOps Scanning & Policy as Code

**Duration:** 75 minutes  
**Prerequisites:** Labs 00–06; Docker running.

## Objectives

- Scan a container image for known vulnerabilities.
- Scan source code and Kubernetes manifests for misconfigurations.
- Write a simple policy-as-code check.

## Part A — Install Trivy

```bash
# macOS
brew install aquasecurity/trivy/trivy

# Windows
winget install Aquasecurity.Trivy

# Linux
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
```

Verify:

```bash
trivy version
```

## Part B — Image Vulnerability Scan

Scan the order service image built in Lab 02:

```bash
trivy image --severity HIGH,CRITICAL order-service:lab02
```

Trivy compares layers against vulnerability databases. Expect some findings in the base image; the goal is to be aware of them and decide whether to accept, patch or replace the base image.

## Part C — Repository Secret Scan

Trivy can also scan for leaked secrets:

```bash
trivy fs --scanners secret .
```

Run this from the repository root. If no secrets are present, Trivy will report a clean scan.

## Part D — Infrastructure Misconfiguration Scan

Scan the Terraform and Kubernetes files:

```bash
trivy config labs/lab05-iac-terraform
trivy config labs/lab06-kubernetes-kind
```

Look for issues such as:

- Containers running as root.
- Missing resource limits.
- Exposed secrets in manifests.

Compare the findings to the files. Notice that the Dockerfiles already create a non-root user and the Kubernetes manifests set resource requests/limits.

## Part E — Policy as Code with OPA / Conftest

Install `conftest`:

```bash
brew install conftest   # macOS
# or download from https://github.com/open-policy-agent/conftest/releases
```

Create a policy that requires every Kubernetes Deployment to have a `course` label:

```bash
mkdir -p labs/lab07-devsecops/policy
cat > labs/lab07-devsecops/policy/labels.rego <<'EOF'
package main

deny[msg] {
  input.kind == "Deployment"
  not input.metadata.labels.course
  msg := "Deployment must have a 'course' label"
}
EOF
```

Run the policy against the Kubernetes manifests:

```bash
conftest test labs/lab06-kubernetes-kind/*.yaml --policy labs/lab07-devsecops/policy
```

Because the manifests include a `course` label in `kustomization.yaml` but the raw files do not, you may see a denial. That is expected: it demonstrates why centralised labels matter and how policy catches drift.

## Part F — Add a Security Gate to CI

Open `.github/workflows/ci.yml` from Lab 04 and ensure the `security-scan` job exists. If it does not, copy the snippet from that lab.

Commit the policy file:

```bash
git add labs/lab07-devsecops/policy
git commit -m "Add Kubernetes label policy"
```

## Expected Output

- Trivy image scan lists vulnerabilities by severity.
- Trivy secret scan runs without finding hard-coded credentials.
- Trivy config scan reports misconfigurations or returns a clean scan.
- Conftest either passes or reports a policy violation.

## Verification Checklist

- [ ] Trivy is installed and runs.
- [ ] Image scan completes.
- [ ] Secret scan completes.
- [ ] Config scan completes on Terraform and Kubernetes files.
- [ ] Conftest evaluates the label policy.
- [ ] Policy files are committed.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Trivy DB download is slow | Use `--skip-db-update` after the first run or set `TRIVY_DB_REPOSITORY`. |
| `conftest` not found | Install from GitHub releases or use the Docker image: `openpolicyagent/conftest`. |
| Policy never triggers | Verify the `input.kind` value and that the file is valid YAML. |

## Stretch Goal

Write a second policy that forbids container images with tag `latest`:

```rego
deny[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  endswith(container.image, ":latest")
  msg := sprintf("Container %s must not use latest tag", [container.name])
}
```

Test it against a manifest that uses `:latest`.
