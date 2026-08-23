# Day 2 Quiz — DevOps & Platform Engineering

**Instructions:** Section A — circle one answer. Section B — answer in 1–3
sentences. 15 minutes.

## Section A — Multiple Choice

**A1.** In Lab 06, `/health` returned `env: kubernetes` but
`build_id: lab02`. Why the difference?
a) A bug in the app
b) `env` came from the ConfigMap at runtime; `build_id` was baked into the image at build time
c) Kubernetes overrides all environment variables
d) The ConfigMap was not applied

**A2.** Why did Conftest FAIL the raw Lab 06 manifests but PASS the
Kustomize-rendered output?
a) Conftest cannot read raw YAML
b) The `course` label is added at render time, so policy must check what ships
c) The policy had a syntax error
d) Kustomize disables policies

**A3.** The three pillars of observability are:
a) Dashboards, alerts, on-call
b) Metrics, logs, traces
c) CPU, memory, disk
d) SLI, SLO, SLA

**A4.** Why was `/health` excluded from the order service's SLI?
a) It has no metrics
b) Health-check traffic almost always succeeds and would inflate availability
c) Prometheus cannot scrape it
d) It is too slow

**A5.** A Kubernetes readiness probe failing causes the pod to:
a) Restart immediately
b) Be removed from Service endpoints until it passes again
c) Be deleted
d) Scale up

## Section B — Short Answer

**B1.** Name a benefit and a cost of microservices compared to a monolith.

**B2.** What does "shifting security left" mean, and give one example from
today's labs.

**B3.** During the game day, how did you *detect* the incident without being
told what was broken? Name the signal.

**B4.** What is an error budget, and what should happen when it is exhausted?

**B5.** In the capstone, what did the platform's "golden path" save the
development team from having to know? Give two examples.
