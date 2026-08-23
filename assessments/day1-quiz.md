# Day 1 Quiz — DevOps & Platform Engineering

**Instructions:** Section A — circle one answer. Section B — answer in 1–3
sentences. 15 minutes.

## Section A — Multiple Choice

**A1.** In the CALMS model, the "M" stands for:
a) Microservices  b) Measurement  c) Management  d) Monitoring

**A2.** Which statement about declarative IaC is TRUE?
a) It lists exact commands to run in order
b) It describes the desired end state and the tool converges to it
c) It only works in the cloud
d) It cannot detect manual changes

**A3.** In today's Terraform lab, what was the purpose of `.terraform.lock.hcl`?
a) Prevents two people applying at once
b) Stores the container IDs
c) Pins provider versions so every machine gets the same ones
d) Encrypts the state file

**A4.** A CI security scan step with `exit-code: 0` will:
a) Fail the build on any CRITICAL finding
b) Fail only on fixable findings
c) Never fail the build — it is report-only
d) Skip the scan

**A5.** Continuous Delivery means:
a) Every commit deploys to production automatically
b) Code is always in a deployable state; deployment is a human decision
c) Deployments happen only on Fridays
d) Testing happens after deployment

## Section B — Short Answer

**B1.** Give one way platform engineering reduces cognitive load for
development teams.

**B2.** Why is a Terraform state file important, and what happened in the lab
when a managed container was deleted manually?

**B3.** List two benefits of feature branches with pull requests.

**B4.** What is a blameless postmortem, and why does it matter?

**B5.** Terraform and Ansible are both IaC. In one sentence each, what is
the difference in what they manage?
