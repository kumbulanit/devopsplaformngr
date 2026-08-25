"""Generate original PNG diagrams for the training course.

Run with: python3 diagrams/build_diagrams.py
All output is written to diagrams/.

Design rules used throughout:
- every element is labelled; arrows say WHAT flows, not just that it flows
- one consistent palette; colour always encodes the same category
- footnote line ties the diagram back to the course labs
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle

OUT_DIR = Path(__file__).parent

# ------------------------------------------------------------------ palette
BLUE = "#2E6DA4"      # process / pipeline
LIGHTBLUE = "#D6EAF8"
GREEN = "#2E8B57"     # runtime / success
LIGHTGREEN = "#D5F5E3"
ORANGE = "#E67E22"    # artifacts / change
RED = "#C0392B"       # security / incidents
PURPLE = "#7D3C98"    # policy / governance
GREY = "#5D6D7E"
INK = "#212F3D"


def save(name: str, fig: plt.Figure) -> None:
    path = OUT_DIR / f"{name}.png"
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {path}")


@dataclass
class Node:
    x: float
    y: float
    w: float
    h: float
    text: str
    color: str = BLUE
    text_color: str = "white"
    fontsize: int = 10
    radius: float = 0.05
    edge: str = "black"


def draw_box(ax, node: Node) -> None:
    box = FancyBboxPatch(
        (node.x - node.w / 2, node.y - node.h / 2),
        node.w, node.h,
        boxstyle=f"round,pad=0.02,rounding_size={node.radius}",
        facecolor=node.color, edgecolor=node.edge, linewidth=1.2,
    )
    ax.add_patch(box)
    ax.text(node.x, node.y, node.text, ha="center", va="center",
            color=node.text_color, fontsize=node.fontsize, weight="bold")


def panel(ax, x, y, w, h, face, edge, lw=2.0, rounding=0.1):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0.02,rounding_size={rounding}",
                       facecolor=face, edgecolor=edge, linewidth=lw)
    ax.add_patch(p)
    return p


def arrow(ax, start: Tuple[float, float], end: Tuple[float, float],
          color: str = INK, lw: float = 1.8, style: str = "-|>",
          rad: float = 0.0, label: str = "", label_dy: float = 0.16,
          fontsize: int = 8, label_color: str = None):
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                                connectionstyle=f"arc3,rad={rad}",
                                shrinkA=2, shrinkB=2))
    if label:
        mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        ax.text(mx, my + label_dy, label, ha="center", va="bottom",
                fontsize=fontsize, color=label_color or color, style="italic")


def footnote(ax, text, x=0.5):
    ax.text(x, -0.02, text, transform=ax.transAxes, ha="center", va="top",
            fontsize=9, style="italic", color=GREY)


# =================================================================== 01
def devops_loop():
    """DevOps infinity loop: a real lemniscate with 8 labelled phases."""
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.set_xlim(-1.62, 1.62)
    ax.set_ylim(-0.95, 0.95)
    ax.axis("off")
    ax.set_title("The DevOps Infinity Loop — one continuous flow, not a handover",
                 fontsize=15, weight="bold", pad=16, color=INK)

    # Lemniscate of Gerono: x = cos t, y = sin t * cos t
    ts = [i / 400 * 2 * math.pi for i in range(401)]
    xs = [1.15 * math.cos(t) for t in ts]
    ys = [0.75 * math.sin(t) * math.cos(t) for t in ts]
    # Left lobe (Dev) drawn blue, right lobe (Ops) green
    left = [(x, y) for x, y in zip(xs, ys) if x <= 0.02]
    right = [(x, y) for x, y in zip(xs, ys) if x >= -0.02]
    ax.plot([p[0] for p in left], [p[1] for p in left], color=BLUE, lw=7,
            solid_capstyle="round", zorder=1)
    ax.plot([p[0] for p in right], [p[1] for p in right], color=GREEN, lw=7,
            solid_capstyle="round", zorder=1)

    ax.text(-0.62, 0.82, "DEV", fontsize=13, weight="bold", color=BLUE, ha="center")
    ax.text(0.62, 0.82, "OPS", fontsize=13, weight="bold", color=GREEN, ha="center")

    phases = [
        ("1. Plan",    -0.58,  0.52, BLUE,  "backlog, user stories"),
        ("2. Code",    -1.28,  0.28, BLUE,  "Git branches, review"),
        ("3. Build",   -1.28, -0.28, BLUE,  "CI, container image"),
        ("4. Test",    -0.58, -0.52, BLUE,  "automated tests, scans"),
        ("5. Release",  0.58, -0.52, GREEN, "versioned artifact"),
        ("6. Deploy",   1.28, -0.28, GREEN, "IaC, rolling update"),
        ("7. Operate",  1.28,  0.28, GREEN, "runbooks, incidents"),
        ("8. Monitor",  0.58,  0.52, GREEN, "metrics, logs, traces"),
    ]
    for name, x, y, color, sub in phases:
        draw_box(ax, Node(x, y, 0.42, 0.17, name, color, fontsize=10))
        ax.text(x, y - 0.155, sub, ha="center", va="top", fontsize=7.5, color=GREY,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.0))

    ax.text(0, 0.30, "Feedback", ha="center", fontsize=10, weight="bold", color=INK,
            bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
    ax.text(0, -0.30, "Monitoring informs the next plan —\nthe loop never stops",
            ha="center", va="top", fontsize=8.5, color=GREY, style="italic",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
    footnote(ax, "This course walks the loop once: plan & code (Lab 01) → build/test (Labs 02–04) → deploy (Labs 05–06) → operate & monitor (Labs 07–08).")
    save("01-devops-infinity-loop", fig)


# =================================================================== 02
def cicd_pipeline():
    """CI/CD pipeline with CI/CD zones, gates, and labelled feedback loops."""
    fig, ax = plt.subplots(figsize=(13, 5.2))
    ax.set_xlim(0, 13)
    ax.set_ylim(-0.5, 4.4)
    ax.axis("off")
    ax.set_title("CI/CD Pipeline — every stage can stop a bad change",
                 fontsize=15, weight="bold", pad=14, color=INK)

    # Zones
    panel(ax, 0.3, 1.3, 6.2, 2.6, "#EBF5FB", BLUE, lw=1.6)
    ax.text(3.4, 3.66, "CONTINUOUS INTEGRATION  (every push / PR)",
            fontsize=9.5, weight="bold", color=BLUE, ha="center")
    panel(ax, 6.9, 1.3, 5.8, 2.6, "#E9F7EF", GREEN, lw=1.6)
    ax.text(9.8, 3.66, "CONTINUOUS DELIVERY  (merge to main)",
            fontsize=9.5, weight="bold", color=GREEN, ha="center")

    steps = [
        (1.3,  "Commit\n+ PR",       BLUE,   "developer pushes\na feature branch"),
        (2.9,  "Build",              BLUE,   "docker build\nSHA-tagged image"),
        (4.5,  "Test",               BLUE,   "pytest, lint\nunit + API tests"),
        (6.0,  "Security\nGate",     RED,    "Trivy: fail on\nfixable CRITICAL"),
        (7.9,  "Deploy\nStaging",    GREEN,  "kubectl apply -k\nrolling update"),
        (9.6,  "Smoke\nTest",        ORANGE, "curl /health\ncreate test order"),
        (11.5, "Deploy\nProduction", GREEN,  "manual approval\n(environment gate)"),
    ]
    for x, text, color, sub in steps:
        draw_box(ax, Node(x, 2.55, 1.32, 0.95, text, color, fontsize=9.5))
        ax.text(x, 1.92, sub, ha="center", va="top", fontsize=7.5, color=GREY)
    for i in range(len(steps) - 1):
        arrow(ax, (steps[i][0] + 0.7, 2.55), (steps[i + 1][0] - 0.7, 2.55), lw=2)

    # Feedback loops (routed below the zone panels to avoid overlap)
    arrow(ax, (6.0, 1.22), (1.3, 1.22), color=RED, rad=0.30, lw=1.5)
    ax.text(3.65, 0.42, "gate fails → fix forward in minutes, not weeks",
            ha="center", fontsize=8.5, color=RED, style="italic")
    arrow(ax, (11.5, 1.22), (7.9, 1.22), color=GREY, rad=0.30, lw=1.4)
    ax.text(9.7, 0.42, "rollback = redeploy previous version",
            ha="center", fontsize=8.5, color=GREY, style="italic")

    ax.text(6.5, -0.05,
            "Artifact promotion: the SAME image (immutable, SHA-tagged) moves through every stage — never rebuilt between environments.",
            ha="center", fontsize=9, style="italic", color=INK)
    footnote(ax, "Lab 04 builds this pipeline in GitHub Actions; Lab 09's golden path adds the deploy stages.")
    save("02-cicd-pipeline", fig)


# =================================================================== 03
def iac_flow():
    """IaC loop including drift detection and the lock file."""
    fig, ax = plt.subplots(figsize=(12, 5.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5.6)
    ax.axis("off")
    ax.set_title("Infrastructure as Code — declare the destination, let the tool drive",
                 fontsize=15, weight="bold", pad=14, color=INK)

    draw_box(ax, Node(1.6, 4.3, 2.3, 1.0, "Code in Git\n(.tf files)", BLUE))
    ax.text(1.6, 3.62, "desired state,\nreviewed like any code", ha="center",
            va="top", fontsize=8, color=GREY)
    draw_box(ax, Node(4.8, 4.3, 2.3, 1.0, "terraform plan\n(preview diff)", ORANGE))
    ax.text(4.8, 3.62, "shows +create ~update\n-destroy before acting", ha="center",
            va="top", fontsize=8, color=GREY)
    draw_box(ax, Node(8.0, 4.3, 2.3, 1.0, "terraform apply\n(converge)", GREEN))
    ax.text(8.0, 3.62, "creates network +\ncontainers in order", ha="center",
            va="top", fontsize=8, color=GREY)
    draw_box(ax, Node(10.9, 4.3, 1.9, 1.0, "Real\nInfrastructure", GREY))
    ax.text(10.9, 3.62, "Docker on localhost\n(cloud: same workflow)", ha="center",
            va="top", fontsize=8, color=GREY)

    arrow(ax, (2.8, 4.3), (3.6, 4.3), label="review + merge", label_dy=0.12)
    arrow(ax, (6.0, 4.3), (6.8, 4.3), label="human approves", label_dy=0.12)
    arrow(ax, (9.2, 4.3), (9.9, 4.3), label="API calls", label_dy=0.12)

    # State file
    draw_box(ax, Node(6.4, 1.9, 3.4, 0.85, "STATE FILE  (terraform.tfstate)", PURPLE, fontsize=9.5))
    ax.text(6.4, 1.32, "maps resource names → real IDs · tracks dependencies · NEVER edited by hand",
            ha="center", va="top", fontsize=8, color=GREY)
    arrow(ax, (8.0, 3.75), (7.2, 2.4), color=PURPLE, lw=1.4, label="records IDs", label_dy=0.0)
    arrow(ax, (5.6, 2.4), (4.8, 3.75), color=PURPLE, lw=1.4, label="compares", label_dy=0.0)

    # Drift
    arrow(ax, (10.6, 3.7), (8.1, 1.95), color=RED, rad=-0.25, lw=1.5,
          label="DRIFT: manual change detected on next plan", label_dy=-0.3, fontsize=8.5)

    # Lock file
    draw_box(ax, Node(1.9, 1.9, 2.6, 0.85, ".terraform.lock.hcl", INK, fontsize=9.5))
    ax.text(1.9, 1.32, "pins provider versions —\ncommitted to Git for reproducibility",
            ha="center", va="top", fontsize=8, color=GREY)

    footnote(ax, "Lab 05: this exact loop against local Docker — plan, apply, drift experiment, destroy. Only the provider block changes for cloud.")
    save("03-iac-flow", fig)


# =================================================================== 04
def k8s_architecture():
    """Kubernetes architecture with labelled component roles and request path."""
    fig, ax = plt.subplots(figsize=(13, 7.2))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.2)
    ax.axis("off")
    ax.set_title("Kubernetes Architecture — control plane decides, workers run",
                 fontsize=15, weight="bold", pad=14, color=INK)

    # Control plane
    panel(ax, 0.5, 4.5, 12.0, 2.2, LIGHTBLUE, BLUE)
    ax.text(1.0, 6.42, "CONTROL PLANE (the cluster's brain)", fontsize=11,
            weight="bold", color=BLUE)

    cps = [
        (2.3, "API Server", "single front door:\nkubectl & components\nall talk to it"),
        (5.2, "etcd", "key-value store:\nthe cluster's entire\ndesired + actual state"),
        (8.1, "Scheduler", "picks the best node\nfor each new Pod\n(resources, affinity)"),
        (11.0, "Controller\nManager", "reconciliation loops:\nactual state →\ndesired state"),
    ]
    for x, name, desc in cps:
        draw_box(ax, Node(x, 5.95, 2.1, 0.62, name, BLUE, fontsize=10))
        ax.text(x, 5.52, desc, ha="center", va="top", fontsize=7.6, color=INK)

    # Workers
    worker_data = [
        (2.6, "Worker Node 1", [("order-service pod", GREEN), ("order-service pod", GREEN)]),
        (6.5, "Worker Node 2", [("order-service pod", GREEN), ("payment-service pod", ORANGE)]),
        (10.4, "Worker Node 3", [("payment-service pod", ORANGE), ("(space for more)", GREY)]),
    ]
    for wx, wname, pods in worker_data:
        panel(ax, wx - 1.75, 0.7, 3.5, 3.1, LIGHTGREEN, GREEN, rounding=0.08)
        ax.text(wx, 3.52, wname, fontsize=10, weight="bold", color=GREEN, ha="center")
        py = 2.9
        for pname, pcolor in pods:
            draw_box(ax, Node(wx, py, 2.9, 0.5, pname, pcolor, fontsize=8.5))
            py -= 0.68
        draw_box(ax, Node(wx, 1.25, 3.05, 0.5,
                          "kubelet (runs pods) · kube-proxy (routes)",
                          "#A9DFBF", text_color=INK, fontsize=7.8))

    for wx, _, _ in worker_data:
        arrow(ax, (6.5, 4.42), (wx, 3.9), color=GREY, lw=1.3, rad=0.05)
    ax.text(6.5, 4.18, "desired state flows down; node/pod status flows back up",
            ha="center", fontsize=8.5, color=GREY, style="italic")

    # kubectl entry
    draw_box(ax, Node(0.9, 6.9, 1.5, 0.5, "kubectl", INK, fontsize=9.5))
    arrow(ax, (1.55, 6.82), (2.3, 6.30), color=INK, lw=1.4)

    footnote(ax, "Lab 06: kind runs this whole picture in Docker containers on your VM — one 'node', same components, same kubectl.")
    save("04-kubernetes-architecture", fig)


# =================================================================== 05
def monolith_vs_microservices():
    """Deploy-unit comparison with pros/cons."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.8))
    fig.suptitle("Monolith vs Microservices — the unit of deployment changes everything",
                 fontsize=15, weight="bold", color=INK)

    ax = axes[0]
    ax.set_xlim(0, 6); ax.set_ylim(0, 6); ax.axis("off")
    ax.set_title("Monolith — one deployable", fontsize=12, weight="bold", color=RED)
    panel(ax, 0.9, 1.4, 4.2, 3.9, "#FDEDEC", RED)
    for y, label in [(4.6, "Web UI"), (3.8, "Orders logic"), (3.0, "Payments logic"),
                     (2.2, "Inventory logic")]:
        draw_box(ax, Node(3.0, y, 3.2, 0.6, label, RED, fontsize=9.5))
    draw_box(ax, Node(3.0, 0.85, 2.6, 0.55, "one shared database", GREY, fontsize=8.5))
    ax.text(3.0, 5.58, "deployed & scaled as ONE unit", ha="center",
            fontsize=9, style="italic", color=RED)
    ax.text(3.0, -0.1, "+ simple to start, easy local dev, one thing to run\n"
                       "− one bug can take all of it down; whole app redeployed\n"
                       "  for any change; teams queue on one release",
            ha="center", va="top", fontsize=8.5, color=INK)

    ax = axes[1]
    ax.set_xlim(0, 6); ax.set_ylim(0, 6); ax.axis("off")
    ax.set_title("Microservices — independent deployables", fontsize=12,
                 weight="bold", color=BLUE)
    svcs = [(1.5, 4.5, "Web", BLUE), (4.5, 4.5, "Orders", GREEN),
            (1.5, 2.6, "Payments", ORANGE), (4.5, 2.6, "Inventory", PURPLE)]
    for x, y, label, color in svcs:
        panel(ax, x - 1.05, y - 0.75, 2.1, 1.5, "white", color, lw=1.6, rounding=0.06)
        draw_box(ax, Node(x, y + 0.15, 1.7, 0.5, label, color, fontsize=9.5))
        draw_box(ax, Node(x, y - 0.42, 1.7, 0.4, "own DB", GREY, fontsize=7.5))
    arrow(ax, (2.55, 4.5), (3.45, 4.5), color=GREY, lw=1.3, label="API", label_dy=0.05)
    arrow(ax, (4.5, 3.72), (4.5, 3.4), color=GREY, lw=1.3)
    arrow(ax, (3.45, 2.6), (2.6, 2.6), color=GREY, lw=1.3, label="API", label_dy=0.05)
    arrow(ax, (2.2, 3.72), (3.9, 3.32), color=GREY, lw=1.3, rad=0.15)
    ax.text(3.0, 5.58, "each service: own repo, pipeline, deploy, scale",
            ha="center", fontsize=9, style="italic", color=BLUE)
    ax.text(3.0, -0.1, "+ independent deploys & scaling, team autonomy, fault isolation\n"
                       "− network calls can fail; needs service discovery, tracing,\n"
                       "  and platform support — complexity moves between services",
            ha="center", va="top", fontsize=8.5, color=INK)

    fig.text(0.5, -0.04, "This course's app: order-service + payment-service — a two-service microsystem you deploy in Labs 03, 05 and 06.",
             ha="center", fontsize=9, style="italic", color=GREY)
    save("05-monolith-vs-microservices", fig)


# =================================================================== 06
def observability_pillars():
    """Three pillars with examples and the questions each answers."""
    fig, ax = plt.subplots(figsize=(11.5, 6.4))
    ax.set_xlim(0, 11.5)
    ax.set_ylim(-0.4, 6.4)
    ax.axis("off")
    ax.set_title("The Three Pillars of Observability — from 'is it up?' to 'why is it slow?'",
                 fontsize=15, weight="bold", pad=14, color=INK)

    pillars = [
        (2.1, "METRICS", RED,
         "numbers over time,\ncheap to store & aggregate",
         "order_requests_total\np95 latency histogram\nCPU / memory usage",
         'answers: "HOW MUCH?\nHOW FAST? Is the SLO met?"',
         "Prometheus (Lab 08)"),
        (5.75, "LOGS", ORANGE,
         "discrete timestamped events,\nrich detail per occurrence",
         'ERROR payment timeout\norder_id=4f2c amount=7.0\nstack traces',
         'answers: "WHAT exactly\nhappened at 14:32?"',
         "docker/kubectl logs (Labs 02–08)"),
        (9.4, "TRACES", BLUE,
         "one request's journey\nacross service boundaries",
         "order-service 120 ms\n  └─ payment-service 95 ms\n      └─ (db would go here)",
         'answers: "WHERE in the chain\nis the time/error?"',
         "OpenTelemetry (mentioned)"),
    ]
    for x, title, color, what, examples, answers, tool in pillars:
        panel(ax, x - 1.6, 0.9, 3.2, 4.6, "white", color, lw=2)
        draw_box(ax, Node(x, 5.05, 3.0, 0.62, title, color, fontsize=12))
        ax.text(x, 4.45, what, ha="center", va="top", fontsize=8.5, color=INK)
        panel(ax, x - 1.45, 2.75, 2.9, 1.05, "#F8F9F9", GREY, lw=0.8, rounding=0.04)
        ax.text(x, 3.68, examples, ha="center", va="top", fontsize=7.6,
                color=INK, family="monospace")
        ax.text(x, 2.45, answers, ha="center", va="top", fontsize=8.5,
                color=color, weight="bold")
        ax.text(x, 1.35, tool, ha="center", va="top", fontsize=8, color=GREY,
                style="italic")

    ax.text(5.75, 0.42, "Monitoring asks known questions. Observability lets you ask NEW questions about unknown failures — all three pillars together.",
            ha="center", fontsize=9.5, style="italic", color=INK)
    footnote(ax, "Lab 08: metrics with Prometheus + Grafana; logs during the game day; traces discussed as the next step.")
    save("06-observability-pillars", fig)


# =================================================================== 07
def devsecops_shift_left():
    """Shift-left with the cost-of-fix curve and this course's tools."""
    fig, ax = plt.subplots(figsize=(13, 5.6))
    ax.set_xlim(0, 13)
    ax.set_ylim(-0.3, 5.6)
    ax.axis("off")
    ax.set_title("DevSecOps: Shift Security Left — find it where it's cheap to fix",
                 fontsize=15, weight="bold", pad=14, color=INK)

    stages = [
        (1.4,  "Design",  "threat modelling,\nsecure defaults"),
        (3.6,  "Code",    "secret scanning,\ncode review"),
        (5.8,  "Build",   "dependency & image\nscanning (Trivy)"),
        (8.0,  "Deploy",  "policy as code\n(OPA/Conftest)"),
        (10.2, "Runtime", "non-root, read-only fs,\nleast privilege"),
        (12.0, "Operate", "vuln mgmt,\npatching cadence"),
    ]
    for x, name, sub in stages:
        draw_box(ax, Node(x, 2.6, 1.55, 0.75, name, BLUE, fontsize=10))
        ax.text(x, 2.05, sub, ha="center", va="top", fontsize=7.8, color=GREY)
    for i in range(len(stages) - 1):
        arrow(ax, (stages[i][0] + 0.82, 2.6), (stages[i + 1][0] - 0.82, 2.6), lw=1.8)

    # Cost curve
    cxs = [1.4 + 10.6 * i / 100 for i in range(101)]
    cys = [3.45 + 1.5 * (i / 100) ** 2.2 for i in range(101)]
    ax.plot(cxs, cys, color=RED, lw=2.5)
    ax.text(2.2, 3.75, "cost & blast radius of a\nsecurity fix", fontsize=8.5,
            color=RED, ha="center")
    ax.text(11.3, 5.25, "found in production:\nincident + rebuild + disclosure",
            fontsize=8.5, color=RED, ha="center")
    ax.text(2.5, 3.28, "found at commit:\none-line change", fontsize=8.5,
            color=GREEN, ha="center")

    # Gate vs report
    panel(ax, 3.3, 0.15, 6.8, 1.1, "#FDF2E9", ORANGE, lw=1.4)
    ax.text(6.7, 0.98, "Report vs Gate (Lab 04)", fontsize=9, weight="bold",
            color=ORANGE, ha="center")
    ax.text(6.7, 0.68, "report: scan results visible, build stays green  ·  gate: build FAILS on fixable criticals — only a gate changes behaviour",
            fontsize=8, ha="center", color=INK)

    footnote(ax, "Lab 07: Trivy image/secret/config scans + Conftest policies; Lab 04 wires them into CI as report + gate.")
    save("07-devsecops-shift-left", fig)


# =================================================================== 08
def platform_as_product():
    """IDP with golden path, interface, and the do-it-yourself contrast."""
    fig, ax = plt.subplots(figsize=(12.5, 6.6))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(-0.3, 6.6)
    ax.axis("off")
    ax.set_title("Platform as a Product — a paved road developers choose to use",
                 fontsize=15, weight="bold", pad=14, color=INK)

    # Teams
    for y, name in [(5.0, "Stream-aligned team A"), (3.6, "Stream-aligned team B"),
                    (2.2, "Stream-aligned team C")]:
        draw_box(ax, Node(1.5, y, 2.5, 0.7, name, GREEN, fontsize=9))
    ax.text(1.5, 5.6, "USERS (developers)", fontsize=9.5, weight="bold",
            color=GREEN, ha="center")

    # Interface
    draw_box(ax, Node(4.1, 3.6, 1.5, 2.9, "SELF-\nSERVICE\nINTERFACE", INK, fontsize=9))
    ax.text(4.1, 1.85, "templates · CLI · portal\nno tickets, no waiting",
            ha="center", va="top", fontsize=7.8, color=GREY)
    for y in (5.0, 3.6, 2.2):
        arrow(ax, (2.78, y), (3.32, y), lw=1.5, color=GREY)

    # Platform internals
    panel(ax, 5.1, 1.4, 4.9, 4.4, LIGHTBLUE, BLUE)
    ax.text(7.55, 5.55, "INTERNAL DEVELOPER PLATFORM", fontsize=10.5,
            weight="bold", color=BLUE, ha="center")
    caps = [
        (6.3, 4.7, "CI/CD\npipelines"), (8.8, 4.7, "Golden-path\ntemplates"),
        (6.3, 3.6, "Kubernetes\nruntime"),  (8.8, 3.6, "IaC modules\n& envs"),
        (6.3, 2.5, "Security\ngates"),      (8.8, 2.5, "Observability\nstack"),
    ]
    for x, y, text in caps:
        draw_box(ax, Node(x, y, 2.1, 0.8, text, BLUE, fontsize=8.5))
    ax.text(7.55, 1.62, "run BY the platform team, AS a product: backlog, docs, SLOs, roadmap",
            ha="center", fontsize=8, style="italic", color=INK)

    arrow(ax, (4.88, 3.6), (5.2, 3.6), lw=1.5, color=GREY)

    # Outcome
    draw_box(ax, Node(11.3, 3.6, 1.8, 1.1, "Ship value\nfaster,\nsafer", ORANGE, fontsize=10))
    arrow(ax, (10.05, 3.6), (10.35, 3.6), lw=2, color=GREY)

    # Cognitive load note
    panel(ax, 0.4, 0.15, 9.4, 0.95, "#F4ECF7", PURPLE, lw=1.3)
    ax.text(5.1, 0.85, "Why it works: cognitive load moves OFF product teams", fontsize=9,
            weight="bold", color=PURPLE, ha="center")
    ax.text(5.1, 0.55, "teams no longer need to master K8s YAML, pipeline syntax, scanner config — the platform encodes it once, for everyone",
            fontsize=8, ha="center", color=INK)

    footnote(ax, "Lab 09 capstone: you play the platform team and hand a golden path to a stream-aligned team.")
    save("08-platform-as-product", fig)


# =================================================================== 09
def team_topologies():
    """Four team types + three interaction modes."""
    fig, ax = plt.subplots(figsize=(12.5, 6.0))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(-0.3, 6.0)
    ax.axis("off")
    ax.set_title("Team Topologies — four team types, three interaction modes",
                 fontsize=15, weight="bold", pad=14, color=INK)

    draw_box(ax, Node(3.2, 4.6, 4.6, 0.95, "Stream-aligned team", GREEN, fontsize=11))
    ax.text(3.2, 3.95, "owns a product/user journey end-to-end · the team type\neverything else exists to serve · e.g. 'orders team'",
            ha="center", va="top", fontsize=8, color=INK)

    draw_box(ax, Node(9.3, 4.6, 4.6, 0.95, "Platform team", BLUE, fontsize=11))
    ax.text(9.3, 3.95, "provides the internal platform as a product ·\nreduces cognitive load of stream-aligned teams",
            ha="center", va="top", fontsize=8, color=INK)

    draw_box(ax, Node(3.2, 2.2, 4.6, 0.95, "Enabling team", ORANGE, fontsize=11))
    ax.text(3.2, 1.55, "coaches teams through a capability gap (e.g. 'learn\nKubernetes') · temporary by design, then steps away",
            ha="center", va="top", fontsize=8, color=INK)

    draw_box(ax, Node(9.3, 2.2, 4.6, 0.95, "Complicated-subsystem team", PURPLE, fontsize=10))
    ax.text(9.3, 1.55, "owns a component needing rare expertise\n(ML model, codec, trading engine)",
            ha="center", va="top", fontsize=8, color=INK)

    arrow(ax, (6.2, 4.85), (7.0, 4.85), color=BLUE, lw=2,
          label="X-as-a-Service: consume via self-service", label_dy=0.14, fontsize=8)
    arrow(ax, (3.2, 3.0), (3.2, 3.9), color=ORANGE, lw=2,
          label="", rad=0.0)
    ax.text(2.0, 3.42, "facilitating\n(time-boxed coaching)", fontsize=8,
            color=ORANGE, ha="center", style="italic")
    arrow(ax, (7.15, 2.45), (6.85, 2.45), color=PURPLE, lw=2)
    ax.text(6.42, 2.72, "X-as-a-Service", fontsize=7.5, color=PURPLE, ha="center",
            style="italic")

    panel(ax, 1.2, 0.05, 10.1, 0.8, "#FBFCFC", GREY, lw=1.0)
    ax.text(6.25, 0.63, "Interaction modes:", fontsize=8.5, weight="bold", color=INK, ha="center")
    ax.text(6.25, 0.33, "collaboration (discover together, high bandwidth, temporary) · X-as-a-Service (consume with minimal contact) · facilitating (coach, then leave)",
            fontsize=8, ha="center", color=GREY)

    footnote(ax, "Source model: Team Topologies (Skelton & Pais). This course: you are stream-aligned in Labs 1–8, platform team in Lab 9.")
    save("09-team-topologies", fig)


# =================================================================== 10
def incident_lifecycle():
    """Incident lifecycle circle with MTTD/MTTR annotations."""
    fig, ax = plt.subplots(figsize=(11, 7.4))
    ax.set_xlim(-1.85, 1.85)
    ax.set_ylim(-1.52, 1.52)
    ax.axis("off")
    ax.set_title("Incident Lifecycle — respond, recover, and above all: learn",
                 fontsize=15, weight="bold", pad=14, color=INK)

    steps = [
        ("1. Detect", "alert fires or user\nreports — MTTD starts", BLUE),
        ("2. Triage", "severity? impact?\nwho responds?", BLUE),
        ("3. Mitigate", "stop the bleeding:\nrollback, failover", ORANGE),
        ("4. Resolve", "root cause fixed,\nservice fully restored", GREEN),
        ("5. Postmortem", "BLAMELESS review:\ntimeline, contributing\nfactors, lessons", RED),
        ("6. Remediate", "action items shipped:\nalerts, tests, runbooks", PURPLE),
    ]
    n = len(steps)
    R = 0.92
    for i, (label, desc, color) in enumerate(steps):
        a = math.pi / 2 - i * 2 * math.pi / n
        x, y = R * math.cos(a), R * math.sin(a)
        c = Circle((x, y), 0.255, color=color, ec="black", lw=1.2, zorder=3)
        ax.add_patch(c)
        ax.text(x, y, label, ha="center", va="center", fontsize=8.6,
                weight="bold", color="white", zorder=4)
        # description placed radially outside the circle
        dist = R + 0.50
        dx, dy = dist * math.cos(a), dist * math.sin(a)
        ax.text(dx, dy, desc, ha="center", va="center", fontsize=7.8, color=INK)
        a2 = math.pi / 2 - ((i + 1) % n) * 2 * math.pi / n
        x2, y2 = R * math.cos(a2), R * math.sin(a2)
        arrow(ax, (x, y), (x2, y2), color=GREY, lw=1.4, rad=-0.28)

    ax.text(0, 0.18, "MTTD: detect fast (monitoring)\nMTTR: recover fast (automation)",
            ha="center", fontsize=9, color=INK, weight="bold")
    ax.text(0, -0.12, "blameless culture makes both\npossible — people report early\nwhen they are safe",
            ha="center", va="top", fontsize=8.2, color=GREY, style="italic")

    footnote(ax, "Lab 08 game day runs one full cycle: detect via metrics, diagnose via logs, recover, and write a 5-line postmortem.")
    save("10-incident-lifecycle", fig)


# =================================================================== 11 (new)
def lab_topology():
    """Everything that runs on the course VM's localhost, with ports."""
    fig, ax = plt.subplots(figsize=(13, 7.4))
    ax.set_xlim(0, 13)
    ax.set_ylim(-0.3, 7.4)
    ax.axis("off")
    ax.set_title("Your Course Lab — everything on ONE Ubuntu 24.04 VM, all on localhost",
                 fontsize=15, weight="bold", pad=14, color=INK)

    # VM boundary
    panel(ax, 0.3, 0.4, 12.4, 6.3, "#FBFCFC", INK, lw=2.2, rounding=0.12)
    ax.text(0.75, 6.42, "UBUNTU 24.04 VM", fontsize=11, weight="bold", color=INK)

    # Terminal / you
    draw_box(ax, Node(1.75, 5.4, 2.1, 0.75, "You: tmux +\ncurl + browser", GREY, fontsize=9))

    # Native python
    panel(ax, 0.7, 3.3, 2.4, 1.35, "#FEF9E7", ORANGE, lw=1.4)
    ax.text(1.9, 4.4, "Native (Lab 00)", fontsize=8.5, weight="bold", color=ORANGE, ha="center")
    draw_box(ax, Node(1.9, 3.85, 2.0, 0.55, "uvicorn :8000", ORANGE, fontsize=8.5))

    # Docker engine box
    panel(ax, 3.5, 0.7, 9.0, 5.35, "#EBF5FB", BLUE, lw=1.8)
    ax.text(8.0, 5.82, "DOCKER ENGINE", fontsize=10.5, weight="bold", color=BLUE, ha="center")

    # Compose stack
    panel(ax, 3.75, 3.6, 4.1, 1.95, "white", GREEN, lw=1.4, rounding=0.06)
    ax.text(5.8, 5.28, "Compose stack (Labs 03, 08)", fontsize=8.5, weight="bold",
            color=GREEN, ha="center")
    draw_box(ax, Node(4.8, 4.65, 1.85, 0.5, "order-service\n:8080→8000", GREEN, fontsize=7.5))
    draw_box(ax, Node(6.8, 4.65, 1.85, 0.5, "payment-service\n(internal only)", GREEN, fontsize=7.5))
    draw_box(ax, Node(4.8, 3.95, 1.85, 0.5, "Prometheus\n:9090", RED, fontsize=7.5))
    draw_box(ax, Node(6.8, 3.95, 1.85, 0.5, "Grafana\n:3000", ORANGE, fontsize=7.5))

    # Terraform containers
    panel(ax, 3.75, 1.0, 4.1, 2.3, "white", PURPLE, lw=1.4, rounding=0.06)
    ax.text(5.8, 3.0, "Terraform-managed (Lab 05)", fontsize=8.5, weight="bold",
            color=PURPLE, ha="center")
    draw_box(ax, Node(4.8, 2.35, 1.85, 0.5, "tf-dev-order\n:8090→8000", PURPLE, fontsize=7.5))
    draw_box(ax, Node(6.8, 2.35, 1.85, 0.5, "tf-dev-payment\n:8091→8000", PURPLE, fontsize=7.5))
    ax.text(5.8, 1.55, "created & destroyed by\nterraform apply / destroy",
            fontsize=7.5, color=GREY, ha="center")

    # kind cluster
    panel(ax, 8.25, 1.0, 4.0, 4.55, "white", GREEN, lw=1.4, rounding=0.06)
    ax.text(10.25, 5.25, "kind cluster (Labs 06, 09)", fontsize=8.5, weight="bold",
            color=GREEN, ha="center")
    panel(ax, 8.45, 1.25, 3.6, 3.7, LIGHTGREEN, GREEN, lw=1.0, rounding=0.05)
    ax.text(10.25, 4.68, "control-plane node\n(a Docker container)", fontsize=7.5,
            color=GREEN, ha="center")
    draw_box(ax, Node(10.25, 3.95, 3.1, 0.5, "order-service ×2 pods", GREEN, fontsize=7.8))
    draw_box(ax, Node(10.25, 3.25, 3.1, 0.5, "payment-service pod", GREEN, fontsize=7.8))
    draw_box(ax, Node(10.25, 2.55, 3.1, 0.5, "NodePort 30080", INK, fontsize=7.8))
    ax.text(10.25, 1.95, "kind-config.yaml maps\nlocalhost:30080 → NodePort",
            fontsize=7.5, color=GREY, ha="center")

    # localhost access note (arrows to every box would criss-cross panels)
    arrow(ax, (1.9, 5.02), (1.9, 4.55), color=GREY, lw=1.3)
    ax.text(1.75, 2.6, "every box showing a :port\nis reachable from your\nterminal & browser at\nhttp://localhost:<port>",
            ha="center", fontsize=8.5, color=INK,
            bbox=dict(facecolor="#FBFCFC", edgecolor=GREY, boxstyle="round,pad=0.4"))

    ax.text(6.5, 0.02, "http://localhost:<port> — no cloud account, no shared infra, full cleanup with down/destroy/delete. The workflow is what transfers to production.",
            ha="center", fontsize=9, style="italic", color=INK)
    save("11-course-lab-topology", fig)


# =================================================================== 12 (new)
def dora_metrics():
    """The four DORA metrics: throughput vs stability."""
    fig, ax = plt.subplots(figsize=(12, 6.0))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.4, 6.0)
    ax.axis("off")
    ax.set_title("The Four DORA Metrics — measure the system, not the people",
                 fontsize=15, weight="bold", pad=14, color=INK)

    panel(ax, 0.4, 2.1, 5.5, 3.2, "#EBF5FB", BLUE, lw=1.6)
    ax.text(3.15, 5.0, "THROUGHPUT — how fast value flows", fontsize=9.5,
            weight="bold", color=BLUE, ha="center")
    draw_box(ax, Node(3.15, 4.15, 4.6, 0.62, "Deployment Frequency", BLUE, fontsize=10))
    ax.text(3.15, 3.72, "how often you deploy to production\nelite: on demand, many times a day",
            ha="center", va="top", fontsize=8, color=INK)
    draw_box(ax, Node(3.15, 2.95, 4.6, 0.62, "Lead Time for Changes", BLUE, fontsize=10))
    ax.text(3.15, 2.52, "commit → running in production\nelite: less than a day",
            ha="center", va="top", fontsize=8, color=INK)

    panel(ax, 6.3, 2.1, 5.5, 3.2, "#FDEDEC", RED, lw=1.6)
    ax.text(9.05, 5.0, "STABILITY — how safely it flows", fontsize=9.5,
            weight="bold", color=RED, ha="center")
    draw_box(ax, Node(9.05, 4.15, 4.6, 0.62, "Change Failure Rate", RED, fontsize=10))
    ax.text(9.05, 3.72, "% of deploys causing degradation\nelite: ~5% or lower",
            ha="center", va="top", fontsize=8, color=INK)
    draw_box(ax, Node(9.05, 2.95, 4.6, 0.62, "Failed Deployment Recovery Time", RED, fontsize=9))
    ax.text(9.05, 2.52, "how fast a bad deploy is recovered\nelite: under an hour (rollback!)",
            ha="center", va="top", fontsize=8, color=INK)

    panel(ax, 1.6, 0.35, 8.8, 1.15, "#E9F7EF", GREEN, lw=1.4)
    ax.text(6.0, 1.24, "The research finding that changed the industry (DORA / Accelerate):",
            fontsize=9, weight="bold", color=GREEN, ha="center")
    ax.text(6.0, 0.9, "speed and stability are NOT a trade-off — elite teams are better at BOTH,\nbecause small, automated, well-tested changes are both faster AND safer.",
            fontsize=8.5, ha="center", color=INK)

    footnote(ax, "Use all four together: gaming one (deploy hourly, break everything) is visible in the others. Capstone handover asks teams to track these.")
    save("12-dora-metrics", fig)


# =================================================================== 13
def wall_of_confusion():
    """Pre-DevOps incentive conflict: Dev vs Ops separated by the wall."""
    fig, ax = plt.subplots(figsize=(12, 6.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.4, 6.4)
    ax.axis("off")
    ax.set_title("The Wall of Confusion — two rational teams, one broken system",
                 fontsize=15, weight="bold", pad=14, color=INK)

    # Dev side
    panel(ax, 0.3, 1.6, 4.6, 4.2, "#EBF5FB", BLUE, lw=1.6)
    ax.text(2.6, 5.45, "DEVELOPMENT", fontsize=11, weight="bold", color=BLUE, ha="center")
    ax.text(2.6, 5.05, "measured on CHANGE delivered", fontsize=9, style="italic",
            color=INK, ha="center")
    for i, t in enumerate(["features shipped per quarter",
                           "projects closed on time",
                           "scope signed off",
                           "rewarded for saying YES"]):
        draw_box(ax, Node(2.6, 4.35 - i * 0.72, 3.9, 0.5, t, BLUE, fontsize=9))

    # Ops side
    panel(ax, 7.1, 1.6, 4.6, 4.2, "#E9F7EF", GREEN, lw=1.6)
    ax.text(9.4, 5.45, "OPERATIONS", fontsize=11, weight="bold", color=GREEN, ha="center")
    ax.text(9.4, 5.05, "measured on STABILITY", fontsize=9, style="italic",
            color=INK, ha="center")
    for i, t in enumerate(["uptime % and SLA reports",
                           "incident and audit counts",
                           "change = biggest risk",
                           "rewarded for saying NO"]):
        draw_box(ax, Node(9.4, 4.35 - i * 0.72, 3.9, 0.5, t, GREEN, fontsize=9))

    # The wall
    for row in range(6):
        for col in range(2):
            x = 5.35 + col * 0.62 + (0.31 if row % 2 else 0)
            panel(ax, x, 1.35 + row * 0.75, 0.6, 0.68, "#B03A2E", "#7B241C", lw=1.0, rounding=0.02)
    ax.text(6.0, 6.0, "THE WALL", fontsize=10, weight="bold", color=RED, ha="center")

    arrow(ax, (4.2, 4.9), (7.6, 4.9), color=ORANGE, lw=2.4, rad=-0.25)
    ax.text(6.0, 5.62, "quarterly big-bang release\n'thrown over the wall'", fontsize=8.5,
            ha="center", color=ORANGE, weight="bold",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.2))
    arrow(ax, (7.6, 2.0), (4.4, 2.0), color=RED, lw=2.0, rad=-0.25)
    ax.text(6.0, 1.28, "blame, tickets, war rooms", fontsize=8.5, ha="center",
            color=RED, weight="bold", bbox=dict(facecolor="white", edgecolor="none", pad=1.2))

    panel(ax, 1.6, -0.15, 8.8, 0.95, "#FEF9E7", ORANGE, lw=1.4)
    ax.text(6.0, 0.55, "The fix is not nicer people — it is shared goals, shared pipeline, shared pager:",
            fontsize=9, weight="bold", color=INK, ha="center")
    ax.text(6.0, 0.2, "measure BOTH teams on lead time AND change-failure rate, and the wall has no reason to exist.",
            fontsize=8.5, ha="center", color=GREY)
    footnote(ax, "2009: Flickr's '10+ Deploys per Day' showed Dev + Ops cooperating beats Dev vs Ops — the talk that started DevOps.")
    save("13-wall-of-confusion", fig)


# =================================================================== 14
def three_ways():
    """The Three Ways: flow, feedback, continual learning."""
    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("The Three Ways — the theoretical backbone of every DevOps practice",
                 fontsize=15, weight="bold", pad=14, color=INK)

    # First way: flow
    panel(ax, 0.3, 4.35, 11.4, 1.85, "#EBF5FB", BLUE, lw=1.6)
    ax.text(0.6, 5.82, "1. FLOW  (left → right)", fontsize=10.5, weight="bold", color=BLUE)
    stages = ["Idea", "Code", "Build", "Test", "Deploy", "Operate"]
    for i, st in enumerate(stages):
        x = 1.6 + i * 1.7
        draw_box(ax, Node(x, 5.15, 1.15, 0.52, st, BLUE, fontsize=9))
        if i < len(stages) - 1:
            arrow(ax, (x + 0.62, 5.15), (x + 1.06, 5.15), color=BLUE, lw=2.0)
    ax.text(11.15, 5.15, "value", fontsize=8.5, color=BLUE, ha="center", style="italic")
    ax.text(6.0, 4.62, "small batches • limit WIP • remove handoffs • make work visible",
            fontsize=8.5, ha="center", color=GREY, style="italic")

    # Second way: feedback
    panel(ax, 0.3, 2.25, 11.4, 1.85, "#FDEDEC", RED, lw=1.6)
    ax.text(0.6, 3.72, "2. FEEDBACK  (right → left)", fontsize=10.5, weight="bold", color=RED)
    arrow(ax, (10.35, 3.42), (2.0, 3.42), color=RED, lw=2.2)
    fb = [("tests fail\nin seconds", 2.55), ("scans block\nbad builds", 4.65),
          ("canary\nmetrics", 6.75), ("pager &\ntelemetry", 8.85)]
    for t, x in fb:
        draw_box(ax, Node(x, 2.98, 1.8, 0.6, t, RED, fontsize=8))
    ax.text(6.0, 2.5, "shorten the distance — in time and in people — between cause and signal",
            fontsize=8.5, ha="center", color=GREY, style="italic")

    # Third way: learning
    panel(ax, 0.3, 0.2, 11.4, 1.8, "#E9F7EF", GREEN, lw=1.6)
    ax.text(0.6, 1.62, "3. CONTINUAL LEARNING", fontsize=10.5, weight="bold", color=GREEN)
    lc = [("experiment\nsafely", 2.55), ("practise failure\n(game days)", 4.65),
          ("blameless\npostmortems", 6.75), ("improvement is\nfirst-class work", 8.85)]
    for t, x in lc:
        draw_box(ax, Node(x, 0.85, 1.8, 0.62, t, GREEN, fontsize=8))
    ax.text(10.5, 0.85, "↻", fontsize=22, color=GREEN, ha="center", va="center", weight="bold")
    footnote(ax, "Classify any practice by which Way it serves: code review = feedback, canary = flow + feedback, game day = learning. If none — why do it?")
    save("14-three-ways", fig)


# =================================================================== 15
def calms_model():
    """CALMS: five pillars holding up DevOps outcomes."""
    fig, ax = plt.subplots(figsize=(12, 6.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.6, 6.4)
    ax.axis("off")
    ax.set_title("CALMS — five dimensions; organisations over-buy the A and starve the rest",
                 fontsize=15, weight="bold", pad=14, color=INK)

    draw_box(ax, Node(6.0, 5.6, 9.6, 0.7, "DevOps outcomes: shorter lead time WITHOUT losing stability",
                      INK, fontsize=11))
    pillars = [
        ("C", "Culture", BLUE, "shared ownership,\npsych safety,\nblameless learning", "pipeline exists, but\nevery deploy still waits\nfor a board meeting"),
        ("A", "Automation", GREEN, "pipelines, IaC,\ntests - machines do\nrepeatable work", "'we automated deploys'\nbut thin tests mean\nnobody trusts them"),
        ("L", "Lean", ORANGE, "small batches,\nlimit WIP,\nwaiting = waste", "one release train,\n200 changes - which\none derailed it?"),
        ("M", "Measurement", PURPLE, "DORA metrics, SLOs:\ndata beats\nanecdotes", "policy set by\n'deploys feel risky'\nwith no data"),
        ("S", "Sharing", RED, "InnerSource, docs,\npostmortems\npublished widely", "3 teams build the\nsame deploy script\n3 times"),
    ]
    for i, (letter, name, color, good, fail) in enumerate(pillars):
        x = 1.5 + i * 2.25
        panel(ax, x - 0.95, 1.7, 1.9, 3.3, "white", color, lw=2.0)
        ax.text(x, 4.62, letter, fontsize=20, weight="bold", color=color, ha="center")
        ax.text(x, 4.15, name, fontsize=10.5, weight="bold", color=INK, ha="center")
        ax.text(x, 3.75, good, fontsize=7.6, ha="center", va="top", color=INK)
        panel(ax, x - 0.85, 1.82, 1.7, 1.0, "#FDF2F0", RED, lw=0.9, rounding=0.04)
        ax.text(x, 2.72, "failure mode", fontsize=7, weight="bold", color=RED, ha="center")
        ax.text(x, 2.52, fail, fontsize=6.8, ha="center", va="top", color=GREY)

    panel(ax, 1.6, -0.35, 8.8, 0.9, "#FEF9E7", ORANGE, lw=1.4)
    ax.text(6.0, 0.3, "Health check: score each letter 1–5 with your team, attack the LOWEST letter first —",
            fontsize=9, weight="bold", ha="center", color=INK)
    ax.text(6.0, -0.05, "more automation cannot compensate for missing culture, measurement or sharing.",
            fontsize=8.5, ha="center", color=GREY)
    footnote(ax, "Jez Humble, building on Damon Edwards & John Willis. This course: C=Module 2, A=Modules 4–5, L=Module 1, M=Modules 3+8, S=throughout.")
    save("15-calms-model", fig)


# =================================================================== 16
def cognitive_load():
    """Why platform engineering emerged: cognitive load before/after."""
    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("Cognitive Load — the bottleneck platform engineering exists to remove",
                 fontsize=15, weight="bold", pad=14, color=INK)

    tools = ["Kubernetes", "Terraform", "pipelines", "monitoring", "alerting",
             "scanning", "secrets", "registries", "networking", "policy"]

    # Before
    panel(ax, 0.3, 0.1, 5.5, 5.9, "#FDEDEC", RED, lw=1.6)
    ax.text(3.05, 5.62, "WITHOUT A PLATFORM", fontsize=10.5, weight="bold", color=RED, ha="center")
    ax.text(3.05, 5.25, "every product team carries everything", fontsize=8.5,
            style="italic", color=GREY, ha="center")
    for i, t in enumerate(tools):
        x = 1.75 + (i % 2) * 2.6
        y = 4.65 - (i // 2) * 0.55
        draw_box(ax, Node(x, y, 2.3, 0.44, t, GREY, fontsize=8))
    draw_box(ax, Node(3.05, 1.35, 4.4, 0.62, "the actual business domain", RED, fontsize=9.5))
    ax.text(3.05, 0.72, "extraneous load crushes intrinsic work:\nthe product gets what is LEFT of the team",
            fontsize=8, ha="center", va="top", color=RED)

    arrow(ax, (6.05, 3.0), (6.75, 3.0), color=INK, lw=2.6)

    # After
    panel(ax, 6.9, 0.1, 4.9, 5.9, "#E9F7EF", GREEN, lw=1.6)
    ax.text(9.35, 5.62, "WITH A PLATFORM", fontsize=10.5, weight="bold", color=GREEN, ha="center")
    ax.text(9.35, 5.25, "extraneous load absorbed ONCE, served to all", fontsize=8.5,
            style="italic", color=GREY, ha="center")
    panel(ax, 7.2, 2.7, 4.3, 2.25, "#EBF5FB", BLUE, lw=1.4)
    ax.text(9.35, 4.68, "PLATFORM TEAM  (IDP)", fontsize=9, weight="bold", color=BLUE, ha="center")
    for i, t in enumerate(["golden paths & templates", "pipelines · secrets · registry",
                           "observability & policy defaults"]):
        draw_box(ax, Node(9.35, 4.2 - i * 0.55, 3.8, 0.44, t, BLUE, fontsize=8))
    draw_box(ax, Node(9.35, 1.85, 4.1, 0.62, "product teams: the business domain", GREEN, fontsize=9))
    arrow(ax, (9.35, 2.35), (9.35, 2.68), color=GREEN, lw=2.0)
    ax.text(9.35, 1.25, "self-service consumption — no tickets,\nno queue, ownership stays with the team",
            fontsize=8, ha="center", va="top", color=GREEN)
    footnote(ax, "Cognitive load theory (Sweller, applied by Team Topologies): intrinsic load is the job; extraneous load is the toll. The platform collapses the toll.")
    save("16-cognitive-load", fig)


# =================================================================== 17
def westrum_spectrum():
    """Westrum's three cultures as a comparison table."""
    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("Westrum Typology — culture is how the organisation handles BAD NEWS",
                 fontsize=15, weight="bold", pad=14, color=INK)

    cols = [
        ("PATHOLOGICAL", RED, "#FDEDEC", "power-oriented",
         ["info is hoarded\nas leverage", "messengers\nare shot", "failure →\nscapegoating", "novelty\nis crushed"]),
        ("BUREAUCRATIC", ORANGE, "#FEF9E7", "rule-oriented",
         ["info flows in\nofficial channels", "messengers\nare tolerated", "failure → new\nprocess, blame-shift", "novelty creates\nproblems"]),
        ("GENERATIVE", GREEN, "#E9F7EF", "performance-oriented",
         ["info is actively\nsought & shared", "messengers\nare trained", "failure →\ninquiry & learning", "novelty is\nimplemented"]),
    ]
    rows = ["information", "messengers", "failure", "novelty"]
    for i, r in enumerate(rows):
        ax.text(0.85, 4.3 - i * 0.95, r.upper(), fontsize=8, weight="bold",
                color=GREY, ha="center", rotation=0)
    for c, (name, color, face, sub, cells) in enumerate(cols):
        x = 3.05 + c * 3.35
        panel(ax, x - 1.5, 0.55, 3.0, 5.15, face, color, lw=1.8)
        ax.text(x, 5.38, name, fontsize=10.5, weight="bold", color=color, ha="center")
        ax.text(x, 5.02, sub, fontsize=8.5, style="italic", color=GREY, ha="center")
        for i, cell in enumerate(cells):
            draw_box(ax, Node(x, 4.3 - i * 0.95, 2.6, 0.68, cell, color, fontsize=8))
    arrow(ax, (3.05, 0.25), (9.75, 0.25), color=INK, lw=2.4)
    ax.text(6.4, -0.08, "DORA finding: moving toward GENERATIVE statistically predicts delivery AND organisational performance",
            fontsize=8.5, ha="center", color=INK, weight="bold")
    footnote(ax, "Ron Westrum studied safety-critical industries (aviation, healthcare). Test your org: what happened to the last person who brought bad news?")
    save("17-westrum-spectrum", fig)


# =================================================================== 18
def conways_law():
    """Conway's Law: org chart above, architecture below, reverse maneuver."""
    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("Conway's Law — the architecture you ship is the org chart you have",
                 fontsize=15, weight="bold", pad=14, color=INK)

    # Left: siloed org -> layered architecture
    panel(ax, 0.3, 0.35, 5.6, 5.6, "#FDEDEC", RED, lw=1.6)
    ax.text(3.1, 5.6, "SILOED ORG  →  SEAMS & QUEUES", fontsize=9.5, weight="bold", color=RED, ha="center")
    for i, t in enumerate(["Frontend\nteam", "Backend\nteam", "DBA\nteam", "QA\ndept"]):
        draw_box(ax, Node(1.35 + i * 1.18, 4.85, 1.05, 0.62, t, GREY, fontsize=7.5))
    arrow(ax, (3.1, 4.45), (3.1, 3.95), color=RED, lw=2.0)
    ax.text(3.55, 4.2, "produces", fontsize=7.5, color=RED, style="italic")
    layers = [("UI layer", 3.5), ("API layer\n(versioned, negotiated)", 2.8),
              ("shared database\n(ticket queue to change)", 2.05), ("testing phase at the end", 1.3)]
    for t, y in layers:
        draw_box(ax, Node(3.1, y, 4.6, 0.58, t, RED, fontsize=8))
    ax.text(3.1, 0.75, "every boundary = a handoff, a queue,\nand an incident nobody owns end-to-end",
            fontsize=8, ha="center", va="top", color=GREY, style="italic")

    arrow(ax, (6.1, 3.1), (6.8, 3.1), color=INK, lw=2.6)
    ax.text(6.45, 3.55, "REVERSE\nCONWAY", fontsize=8, weight="bold", color=INK, ha="center")

    # Right: stream-aligned teams -> independent services
    panel(ax, 6.95, 0.35, 4.85, 5.6, "#E9F7EF", GREEN, lw=1.6)
    ax.text(9.37, 5.6, "TEAMS SHAPED FOR THE\nARCHITECTURE YOU WANT", fontsize=9, weight="bold",
            color=GREEN, ha="center", va="center")
    doms = ["Orders team", "Payments team", "Accounts team"]
    for i, t in enumerate(doms):
        draw_box(ax, Node(9.37, 4.6 - i * 0.72, 3.9, 0.55, t + "  →  " + t.split()[0].lower() + " service",
                          GREEN, fontsize=8))
    ax.text(9.37, 2.35, "each team: own repo, own pipeline,\nown deploy, own pager, own data",
            fontsize=8, ha="center", color=INK)
    panel(ax, 7.35, 0.6, 4.05, 1.15, "#EBF5FB", BLUE, lw=1.2)
    ax.text(9.37, 1.55, "TEST", fontsize=8, weight="bold", color=BLUE, ha="center")
    ax.text(9.37, 1.12, "can one team ship to production today\nwithout another team's calendar?",
            fontsize=8, ha="center", color=INK)
    footnote(ax, "Mel Conway, 1968: four teams building a compiler produced a four-pass compiler. Team Topologies turned the law into a design tool.")
    save("18-conways-law", fig)


# =================================================================== 19
def batch_size_risk():
    """Risk grows super-linearly with batch size."""
    fig, ax = plt.subplots(figsize=(12, 6.0))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.6, 6.2)
    ax.axis("off")
    ax.set_title("Batch Size Is the Enemy — risk grows faster than size",
                 fontsize=15, weight="bold", pad=14, color=INK)

    # axes for the curve
    ox, oy, w, h = 1.0, 0.9, 6.2, 4.6
    arrow(ax, (ox, oy), (ox + w, oy), color=INK, lw=1.6)
    arrow(ax, (ox, oy), (ox, oy + h), color=INK, lw=1.6)
    ax.text(ox + w / 2, oy - 0.45, "batch size (lines changed per release)", fontsize=9, ha="center", color=INK)
    ax.text(ox - 0.35, oy + h / 2, "risk of failure ×\ncost of diagnosis", fontsize=9,
            ha="center", va="center", rotation=90, color=INK)
    xs = [i / 100 for i in range(101)]
    pts = [(ox + x * (w - 0.4), oy + (x ** 2.3) * (h - 0.5)) for x in xs]
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=RED, lw=3.5, solid_capstyle="round")

    x1, y1 = ox + 0.12 * (w - 0.4), oy + (0.12 ** 2.3) * (h - 0.5)
    ax.plot([x1], [y1], "o", color=GREEN, markersize=11, zorder=5)
    ax.text(x1 + 0.2, y1 + 0.95, "50-line PR: reviewable,\ntestable, one-command revert",
            fontsize=8, color=GREEN, weight="bold")
    x2, y2 = ox + 0.93 * (w - 0.4), oy + (0.93 ** 2.3) * (h - 0.5)
    ax.plot([x2], [y2], "o", color=RED, markersize=11, zorder=5)
    ax.text(x2 - 0.2, y2 + 0.15, "5000-line merge:\nskimmed & hoped about", fontsize=8,
            color=RED, weight="bold", ha="right")

    panel(ax, 7.9, 2.6, 3.9, 2.9, "#E9F7EF", GREEN, lw=1.5)
    ax.text(9.85, 5.15, "SAME total change,\ndifferent risk", fontsize=9.5, weight="bold",
            color=GREEN, ha="center", va="center")
    ax.text(9.85, 4.3, "20 × 10-line deploys:\neach reviewed, tested,\nreversible in minutes",
            fontsize=8.5, ha="center", color=INK)
    ax.text(9.85, 3.25, "1 × 200-line release:\ninteractions untested,\nwhich change broke it?",
            fontsize=8.5, ha="center", color=RED)
    panel(ax, 7.9, 0.6, 3.9, 1.6, "#FEF9E7", ORANGE, lw=1.4)
    ax.text(9.85, 1.85, "Also true for infrastructure,\nconfig and DB migrations —", fontsize=8.5,
            ha="center", color=INK, weight="bold")
    ax.text(9.85, 1.05, "expand/contract in small steps\nbeats break-and-fix in one",
            fontsize=8.5, ha="center", color=GREY)
    footnote(ax, "Danger lives in the INTERACTIONS between changes, so risk compounds super-linearly. Small batches are a SAFETY practice, not a speed hack.")
    save("19-batch-size-risk", fig)


# =================================================================== 20
def report_vs_gate():
    """The two-step scan pattern: report for visibility, gate for behaviour."""
    fig, ax = plt.subplots(figsize=(12, 6.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, 6.4)
    ax.axis("off")
    ax.set_title("A Scan Is Not a Gate — the two-step pattern that keeps red meaningful",
                 fontsize=15, weight="bold", pad=14, color=INK)

    draw_box(ax, Node(1.3, 5.3, 1.8, 0.6, "build image\n(SHA-tagged)", BLUE, fontsize=8.5))
    arrow(ax, (2.25, 5.3), (3.0, 5.3), color=INK, lw=2.0)
    draw_box(ax, Node(3.95, 5.3, 1.8, 0.6, "scan\n(Trivy)", PURPLE, fontsize=9))

    # Report branch
    arrow(ax, (4.9, 5.45), (6.1, 4.75), color=GREEN, lw=2.0, rad=-0.2)
    panel(ax, 6.0, 3.7, 5.6, 1.9, "#E9F7EF", GREEN, lw=1.6)
    ax.text(8.8, 5.28, "STEP 1 — REPORT  (exit 0, build stays green)", fontsize=9.5,
            weight="bold", color=GREEN, ha="center")
    ax.text(8.8, 4.85, "severity HIGH + CRITICAL, everything printed", fontsize=8.5, ha="center", color=INK)
    ax.text(8.8, 4.5, "full visibility for triage · SARIF/JSON to the dashboard", fontsize=8.5, ha="center", color=INK)
    ax.text(8.8, 4.12, "awareness only — nobody's build breaks on unfixables", fontsize=8, ha="center",
            color=GREY, style="italic")

    # Gate branch
    arrow(ax, (4.9, 5.12), (6.1, 2.6), color=RED, lw=2.0, rad=0.25)
    panel(ax, 6.0, 1.2, 5.6, 1.9, "#FDEDEC", RED, lw=1.6)
    ax.text(8.8, 2.8, "STEP 2 — GATE  (exit 1, the line STOPS)", fontsize=9.5,
            weight="bold", color=RED, ha="center")
    ax.text(8.8, 2.37, "severity CRITICAL only  +  --ignore-unfixed", fontsize=8.5, ha="center", color=INK)
    ax.text(8.8, 2.0, "fails ONLY on findings a developer can fix TODAY", fontsize=8.5, ha="center", color=INK)
    ax.text(8.8, 1.62, "a gate on unfixable CVEs teaches people to ignore red", fontsize=8, ha="center",
            color=GREY, style="italic")

    panel(ax, 0.4, 0.55, 4.6, 3.3, "#FEF9E7", ORANGE, lw=1.5)
    ax.text(2.7, 3.55, "WIDEN THE GATE DELIBERATELY", fontsize=9, weight="bold", color=ORANGE, ha="center")
    steps = ["1. gate: fixable CRITICALs only", "2. clear the backlog (bots help)",
             "3. add fixable HIGHs", "4. keep an audited exception\n    path with expiry dates"]
    for i, s in enumerate(steps):
        ax.text(0.7, 3.1 - i * 0.62, s, fontsize=8.5, color=INK, va="top")
    footnote(ax, "Workshop 1 wires exactly this into GitHub Actions: a report job and a gate job on the same Trivy scan of the same image.")
    save("20-report-vs-gate", fig)


# =================================================================== 21
def gitops_push_pull():
    """Push vs pull deployment models."""
    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("Push vs Pull (GitOps) — who holds the keys, and who fixes drift",
                 fontsize=15, weight="bold", pad=14, color=INK)

    # Push model
    panel(ax, 0.3, 0.4, 5.6, 5.5, "#FEF9E7", ORANGE, lw=1.6)
    ax.text(3.1, 5.55, "PUSH — pipeline applies", fontsize=10.5, weight="bold", color=ORANGE, ha="center")
    draw_box(ax, Node(1.7, 4.6, 1.7, 0.6, "Git repo\n(desired state)", BLUE, fontsize=8))
    draw_box(ax, Node(4.4, 4.6, 1.7, 0.6, "CI pipeline", ORANGE, fontsize=9))
    draw_box(ax, Node(4.4, 2.6, 1.9, 0.65, "cluster /\nenvironment", GREEN, fontsize=8.5))
    arrow(ax, (2.6, 4.6), (3.45, 4.6), color=INK, lw=1.8, label="triggers")
    arrow(ax, (4.4, 4.25), (4.4, 3.0), color=ORANGE, lw=2.2)
    ax.text(3.35, 3.6, "kubectl apply\n(the runner holds\ncluster credentials)", fontsize=7.5,
            color=ORANGE, ha="right")
    ax.text(3.1, 1.75, "simple, familiar — but the runner holds prod keys,\nand manual drift stays until the next push",
            fontsize=8, ha="center", va="top", color=GREY, style="italic")

    # Pull model
    panel(ax, 6.15, 0.4, 5.6, 5.5, "#E9F7EF", GREEN, lw=1.6)
    ax.text(8.95, 5.55, "PULL — cluster syncs (GitOps)", fontsize=10.5, weight="bold", color=GREEN, ha="center")
    draw_box(ax, Node(7.5, 4.6, 1.7, 0.6, "Git repo\n(desired state)", BLUE, fontsize=8))
    panel(ax, 8.15, 1.7, 3.2, 2.3, "white", GREEN, lw=1.4)
    ax.text(9.75, 3.75, "cluster", fontsize=8.5, weight="bold", color=GREEN, ha="center")
    draw_box(ax, Node(9.6, 3.15, 2.3, 0.55, "agent (Argo CD / Flux)", GREEN, fontsize=7.5))
    draw_box(ax, Node(9.6, 2.25, 2.3, 0.55, "workloads", GREEN, fontsize=8.5))
    arrow(ax, (8.4, 4.3), (9.1, 3.5), color=GREEN, lw=2.2, rad=-0.2)
    ax.text(8.05, 3.78, "pulls & diffs", fontsize=7.5, color=GREEN, style="italic", ha="left")
    arrow(ax, (9.6, 2.87), (9.6, 2.55), color=GREEN, lw=1.8)
    ax.text(9.6, 1.87, "converge · heal drift · forever", fontsize=7.5, color=GREEN,
            ha="center", va="center", style="italic")
    ax.text(8.95, 1.35, "no cluster creds in CI · manual edits reverted ·\n'what runs = what's in Git at commit X' — audit for free",
            fontsize=8, ha="center", va="top", color=INK, weight="bold")
    footnote(ax, "Deploy = merge; rollback = revert. Cost: another component to run, and out-of-band changes genuinely stop working — that is the point.")
    save("21-gitops-push-pull", fig)


# =================================================================== 22
def terraform_mental_model():
    """Terraform's five concepts in one picture."""
    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("Terraform's Mental Model — code declares, state remembers, plan is the diff",
                 fontsize=15, weight="bold", pad=14, color=INK)

    # Module wrapper
    panel(ax, 0.35, 3.3, 4.6, 2.75, "#EBF5FB", BLUE, lw=1.6)
    ax.text(2.65, 5.72, "MODULE (reusable, versioned)", fontsize=9, weight="bold", color=BLUE, ha="center")
    draw_box(ax, Node(1.6, 5.05, 1.5, 0.55, "variables\n(inputs)", GREY, fontsize=8))
    draw_box(ax, Node(3.65, 5.05, 1.5, 0.55, "outputs\n(facts out)", GREY, fontsize=8))
    draw_box(ax, Node(2.65, 4.2, 3.6, 0.6, "resources (.tf code)\ndesired end state", BLUE, fontsize=8.5))
    ax.text(2.65, 3.78, "provider plugin speaks the platform's API\n(docker · aws · azurerm · kubernetes)",
            fontsize=7.5, ha="center", va="top", color=GREY)

    draw_box(ax, Node(2.65, 2.3, 2.4, 0.65, "terraform plan", ORANGE, fontsize=10))
    arrow(ax, (2.65, 3.28), (2.65, 2.65), color=INK, lw=2.0)
    draw_box(ax, Node(6.35, 2.3, 2.2, 0.65, "terraform apply", GREEN, fontsize=10))
    arrow(ax, (3.9, 2.3), (5.2, 2.3), color=INK, lw=2.0, label="approved diff")

    # State + reality
    draw_box(ax, Node(6.35, 4.6, 2.3, 0.75, "STATE file\ncode name ↔ real ID", PURPLE, fontsize=8.5))
    draw_box(ax, Node(9.9, 4.6, 2.6, 0.75, "REALITY\nnetworks, containers, DNS", GREEN, fontsize=8.5))
    arrow(ax, (5.0, 2.55), (5.9, 4.2), color=PURPLE, lw=1.8, rad=0.2)
    arrow(ax, (7.6, 4.6), (8.5, 4.6), color=GREY, lw=1.6, label="refresh")
    arrow(ax, (7.5, 2.3), (9.4, 4.15), color=GREEN, lw=2.2, rad=-0.15, label="create / update / destroy")

    panel(ax, 8.15, 0.55, 3.6, 2.3, "#FEF9E7", ORANGE, lw=1.5)
    ax.text(9.95, 2.55, "PLAN OUTPUT = the review", fontsize=8.5, weight="bold", color=ORANGE, ha="center")
    ax.text(9.95, 2.15, "+ create   ~ update   - destroy", fontsize=9, ha="center", color=INK, family="monospace")
    ax.text(9.95, 1.72, "posted into the PR — the reviewer\napproves an exact diff of reality;\nread the destroy count TWICE",
            fontsize=7.8, ha="center", va="top", color=GREY)
    panel(ax, 0.55, 0.55, 6.9, 1.1, "#E9F7EF", GREEN, lw=1.4)
    ax.text(4.0, 1.36, "One sentence: code declares desire · state records reality ·",
            fontsize=8.2, ha="center", color=INK, weight="bold")
    ax.text(4.0, 1.02, "plan is the difference · apply closes it · modules make it reusable.",
            fontsize=8.2, ha="center", color=INK, weight="bold")
    footnote(ax, "Workshop 3 uses the kreuzwerker/docker provider on localhost — swap one provider block for hashicorp/aws and the whole workflow is unchanged.")
    save("22-terraform-mental-model", fig)


# =================================================================== 23
def value_stream_wait():
    """Value-stream map: work time vs wait time for a regulated change."""
    fig, ax = plt.subplots(figsize=(12.5, 6.4))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(-0.6, 6.6)
    ax.axis("off")
    ax.set_title("Value-Stream Map — waiting is the biggest waste (illustrative regulated-institution change)",
                 fontsize=14, weight="bold", pad=14, color=INK)

    steps = [
        ("code the\nchange", "4 h", "2 d", 1.35),
        ("peer\nreview", "40 m", "3 d", 3.25),
        ("QA in shared\nenvironment", "6 h", "5 d", 5.15),
        ("security\nreview", "2 h", "7 d", 7.05),
        ("CAB\napproval", "30 m", "6 d", 8.95),
        ("release\nwindow", "2 h", "4 d", 10.85),
    ]
    for name, work, wait, x in steps:
        draw_box(ax, Node(x, 4.5, 1.6, 0.85, name, BLUE, fontsize=8.5))
        panel(ax, x - 0.8, 3.25, 1.6, 0.75, "#E9F7EF", GREEN, lw=1.1, rounding=0.04)
        ax.text(x, 3.62, "work " + work, fontsize=8.5, ha="center", va="center",
                color=GREEN, weight="bold")
        panel(ax, x - 0.8, 2.25, 1.6, 0.85, "#FDEDEC", RED, lw=1.1, rounding=0.04)
        ax.text(x, 2.68, "WAIT " + wait, fontsize=9, ha="center", va="center",
                color=RED, weight="bold")
        if x < 10:
            arrow(ax, (x + 0.85, 4.5), (x + 1.05, 4.5), color=INK, lw=1.6)

    panel(ax, 0.5, 0.7, 5.6, 1.25, "#E9F7EF", GREEN, lw=1.5)
    ax.text(3.3, 1.62, "VALUE-ADDING TIME  ≈ 15 hours", fontsize=10.5, weight="bold",
            color=GREEN, ha="center")
    ax.text(3.3, 1.15, "the part everyone tries to optimise\n('developers must work faster')",
            fontsize=8.5, ha="center", va="center", color=GREY, style="italic")
    panel(ax, 6.4, 0.7, 5.6, 1.25, "#FDEDEC", RED, lw=1.5)
    ax.text(9.2, 1.62, "WAITING TIME  ≈ 27 days", fontsize=10.5, weight="bold",
            color=RED, ha="center")
    ax.text(9.2, 1.15, "queues, handoffs, calendars, approvals —\nwhere the lead time actually lives",
            fontsize=8.5, ha="center", va="center", color=GREY, style="italic")
    ax.text(6.25, 0.2, "Flow efficiency ≈ 2%.  Attack the RED, not the green.",
            fontsize=10, ha="center", weight="bold", color=INK)
    footnote(ax, "Exercise: map one real change in your area, mark every hour WORK or WAIT, then automate or delete the largest wait first.")
    save("23-value-stream-wait", fig)


# =================================================================== 24
def deploy_vs_release():
    """Deploy vs release, illustrated with an embargoed publication."""
    fig, ax = plt.subplots(figsize=(12.5, 6.2))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(-0.6, 6.4)
    ax.axis("off")
    ax.set_title("Deploy ≠ Release — the embargo pattern (e.g. a market-sensitive publication)",
                 fontsize=14, weight="bold", pad=14, color=INK)

    # timeline
    arrow(ax, (0.9, 3.5), (11.8, 3.5), color=INK, lw=2.0)
    marks = [(1.9, "Mon 09:00", "merge to trunk", BLUE),
             (4.3, "Mon 11:00", "DEPLOY to production\n(feature flag OFF)", GREEN),
             (7.0, "Tue–Wed", "verify in production:\nhealth, dashboards,\ncontent rendered dark", PURPLE),
             (9.9, "Thu 15:00", "RELEASE\n(flip the flag)", ORANGE)]
    for x, when, what, color in marks:
        ax.plot([x], [3.5], "o", color=color, markersize=13, zorder=5)
        ax.text(x, 3.95, when, fontsize=9, weight="bold", color=color, ha="center")
        draw_box(ax, Node(x, 2.55, 2.35, 0.95, what, color, fontsize=8))

    panel(ax, 0.7, 4.55, 5.3, 1.5, "#E9F7EF", GREEN, lw=1.5)
    ax.text(3.35, 5.72, "DEPLOY  =  the bits are running", fontsize=10, weight="bold",
            color=GREEN, ha="center")
    ax.text(3.35, 5.05, "an engineering event · reversible · boring ·\nhappens as often as you like",
            fontsize=8.5, ha="center", va="center", color=INK)
    panel(ax, 6.5, 4.55, 5.3, 1.5, "#FEF9E7", ORANGE, lw=1.5)
    ax.text(9.15, 5.72, "RELEASE  =  users can see it", fontsize=10, weight="bold",
            color=ORANGE, ha="center")
    ax.text(9.15, 5.05, "a business event · scheduled to the minute ·\nflag flip, no deployment risk",
            fontsize=8.5, ha="center", va="center", color=INK)

    panel(ax, 0.7, 0.35, 11.1, 1.5, "#EBF5FB", BLUE, lw=1.5)
    ax.text(6.25, 1.5, "Why this matters where timing is regulated or market-sensitive:", fontsize=9.5,
            weight="bold", color=BLUE, ha="center")
    for i, t in enumerate([
        "the risky part (deploying code) happens days early, in daylight, with people watching",
        "the timed part (exposing it) is one flag flip — instantly reversible, no build, no restart",
        "kill switch: if something is wrong at 15:01, flip back in seconds instead of rolling back a release",
    ]):
        ax.text(6.25, 1.15 - i * 0.3, "• " + t, fontsize=8.5, ha="center", color=INK)
    footnote(ax, "Same pattern for any fixed-time announcement, campaign or regulatory publication. Flags need owners and removal dates — they are debt.")
    save("24-deploy-vs-release", fig)


# =================================================================== 25
def container_vs_vm():
    """What a container actually is, next to a VM."""
    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("A Container Is Not a VM — same hardware, very different isolation",
                 fontsize=15, weight="bold", pad=14, color=INK)

    # VM stack
    panel(ax, 0.3, 0.55, 5.4, 5.3, "#FDEDEC", RED, lw=1.6)
    ax.text(3.0, 5.55, "VIRTUAL MACHINES", fontsize=10.5, weight="bold", color=RED, ha="center")
    vm_layers = [("app A | app B | app C", GREY, 0.5),
                 ("GUEST OS  |  GUEST OS  |  GUEST OS", RED, 0.72),
                 ("hypervisor", GREY, 0.5),
                 ("host operating system", GREY, 0.5),
                 ("physical hardware", INK, 0.5)]
    y = 4.85
    for text, color, h in vm_layers:
        draw_box(ax, Node(3.0, y, 4.9, h, text, color, fontsize=8.5))
        y -= h + 0.22
    ax.text(3.0, 1.45, "each VM boots a full kernel:\nGBs of image, tens of seconds to start,\nstrong isolation boundary",
            fontsize=8, ha="center", va="top", color=RED)

    # Container stack
    panel(ax, 6.3, 0.55, 5.4, 5.3, "#E9F7EF", GREEN, lw=1.6)
    ax.text(9.0, 5.55, "CONTAINERS", fontsize=10.5, weight="bold", color=GREEN, ha="center")
    c_layers = [("app A | app B | app C  (just processes)", GREY, 0.5),
                ("container runtime (containerd / Docker)", GREEN, 0.5),
                ("ONE shared host kernel\nnamespaces = what you SEE · cgroups = what you USE", GREEN, 0.9),
                ("host operating system", GREY, 0.5),
                ("physical hardware", INK, 0.5)]
    y = 4.85
    for text, color, h in c_layers:
        draw_box(ax, Node(9.0, y, 4.9, h, text, color, fontsize=8.2)
                 if "\n" not in text else Node(9.0, y, 4.9, h, text, color, fontsize=8.0))
        y -= h + 0.22
    ax.text(9.0, 1.28, "MBs of image, milliseconds to start,\nisolation is kernel-enforced, not hardware —\nso the kernel is the shared trust boundary",
            fontsize=8, ha="center", va="top", color=GREEN)
    footnote(ax, "Consequence for security (Module 7): container escape = host compromise, so non-root, dropped capabilities and seccomp are not optional extras.")
    save("25-container-vs-vm", fig)


# =================================================================== 26
def image_layers():
    """Image layers and the multi-stage build."""
    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("Images: Layers, Cache and the Multi-Stage Build",
                 fontsize=15, weight="bold", pad=14, color=INK)

    # Layers
    panel(ax, 0.3, 2.15, 4.5, 3.75, "#EBF5FB", BLUE, lw=1.6)
    ax.text(2.55, 5.6, "AN IMAGE = STACKED LAYERS", fontsize=9.5, weight="bold", color=BLUE, ha="center")
    layers = [("your application code", ORANGE, "changes every commit"),
              ("installed dependencies", BLUE, "changes when manifest changes"),
              ("runtime (python/jre/node)", GREY, "changes rarely"),
              ("base image (OS packages)", INK, "shared by every service")]
    for i, (t, c, note) in enumerate(layers):
        y = 4.95 - i * 0.72
        draw_box(ax, Node(2.35, y, 3.5, 0.5, t, c, fontsize=8))
        ax.text(4.35, y, note, fontsize=6.8, color=GREY, ha="right", va="center", style="italic")
    ax.text(2.55, 2.45, "content-addressed & shared: 50 services on one base\nstore that base ONCE — the digest is the identity",
            fontsize=7.8, ha="center", va="top", color=INK)

    # cache ordering
    panel(ax, 5.1, 2.15, 3.1, 3.75, "#FEF9E7", ORANGE, lw=1.5)
    ax.text(6.65, 5.6, "ORDER FOR CACHE", fontsize=9.5, weight="bold", color=ORANGE, ha="center")
    ax.text(6.65, 5.15, "COPY requirements.txt\nRUN pip install\nCOPY . .", fontsize=8.5,
            ha="center", va="top", color=INK, family="monospace")
    ax.text(6.65, 3.85, "manifest first, source last:\na code change rebuilds\nONE layer, not all of them",
            fontsize=8, ha="center", va="top", color=ORANGE)
    ax.text(6.65, 2.85, "reversed = every build\nreinstalls everything", fontsize=7.8,
            ha="center", va="top", color=RED, style="italic")

    # multistage
    panel(ax, 8.5, 2.15, 3.2, 3.75, "#E9F7EF", GREEN, lw=1.5)
    ax.text(10.1, 5.6, "MULTI-STAGE BUILD", fontsize=9.5, weight="bold", color=GREEN, ha="center")
    draw_box(ax, Node(10.1, 4.9, 2.7, 0.75, "stage 1: BUILDER\ncompilers, dev headers,\ntest tools", GREY, fontsize=7.5))
    arrow(ax, (10.1, 4.45), (10.1, 4.05), color=GREEN, lw=2.0)
    ax.text(10.35, 4.25, "copy only\nthe artefact", fontsize=6.8, color=GREEN, va="center")
    draw_box(ax, Node(10.1, 3.6, 2.7, 0.75, "stage 2: RUNTIME\nslim base + binary\nnon-root user", GREEN, fontsize=7.5))
    ax.text(10.1, 3.0, "build tools never reach\nproduction = smaller image,\nsmaller CVE surface",
            fontsize=7.8, ha="center", va="top", color=GREEN)

    panel(ax, 0.4, 0.4, 11.3, 1.4, "#EBF5FB", BLUE, lw=1.5)
    ax.text(6.05, 1.5, "THE GOOD-IMAGE CHECKLIST", fontsize=9.5, weight="bold", color=BLUE, ha="center")
    items = ["multi-stage build", "non-root USER", "slim/distroless base", "pinned base version",
             "HEALTHCHECK", "graceful shutdown", ".dockerignore", "no secrets in layers"]
    for i, t in enumerate(items):
        ax.text(0.95 + (i % 4) * 2.75, 1.05 - (i // 4) * 0.42, "✓  " + t, fontsize=8.5, color=INK, va="center")
    footnote(ax, "A secret added in one layer and deleted in the next is STILL in the image history. Never bake credentials — inject them at runtime.")
    save("26-image-layers", fig)


# =================================================================== 27
def k8s_object_map():
    """The Kubernetes objects a team actually touches, and how they relate."""
    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("The Objects You Will Actually Touch — and how they relate",
                 fontsize=15, weight="bold", pad=14, color=INK)

    draw_box(ax, Node(2.6, 5.6, 3.4, 0.62, "Deployment", BLUE, fontsize=10.5))
    ax.text(2.6, 6.15, "desired replicas + pod template + rollout strategy", fontsize=7.5,
            ha="center", color=GREY, style="italic")
    arrow(ax, (2.6, 5.25), (2.6, 4.72), color=INK, lw=1.8)
    ax.text(2.75, 5.0, "creates & owns", fontsize=7.2, color=GREY, va="center", ha="left")
    draw_box(ax, Node(2.6, 4.4, 3.0, 0.55, "ReplicaSet  (one per revision)", BLUE, fontsize=9))
    ax.text(4.3, 4.4, "→ rollback = the\n   previous ReplicaSet", fontsize=7.2, color=GREY, va="center")
    arrow(ax, (2.6, 4.1), (2.6, 3.68), color=INK, lw=1.8)
    ax.text(2.75, 3.89, "keeps N running", fontsize=7.2, color=GREY, va="center", ha="left")

    for i in range(3):
        draw_box(ax, Node(1.5 + i * 1.15, 3.35, 1.0, 0.55, "Pod", GREEN, fontsize=9))
    ax.text(2.6, 2.88, "Pods are MORTAL: replaced, never repaired. No pod has a stable identity or IP.",
            fontsize=7.8, ha="center", color=RED, style="italic")

    draw_box(ax, Node(7.9, 3.35, 2.6, 0.62, "Service", PURPLE, fontsize=10))
    ax.text(7.9, 2.9, "stable name + virtual IP,\nselects pods by LABEL", fontsize=7.8,
            ha="center", va="top", color=GREY, style="italic")
    arrow(ax, (6.6, 3.35), (4.05, 3.35), color=PURPLE, lw=2.0)
    ax.text(5.3, 3.55, "load-balances to", fontsize=7.5, color=PURPLE, ha="center", style="italic")
    draw_box(ax, Node(7.9, 5.0, 2.6, 0.62, "Ingress / Gateway", PURPLE, fontsize=9.5))
    arrow(ax, (7.9, 4.65), (7.9, 3.7), color=PURPLE, lw=1.8)
    ax.text(8.05, 4.18, "routes host / path", fontsize=7.2, color=PURPLE, va="center", ha="left")
    ax.text(10.6, 5.0, "outside\ntraffic", fontsize=8, color=PURPLE, ha="center", va="center")
    arrow(ax, (11.0, 4.6), (9.25, 5.0), color=PURPLE, lw=1.6)

    panel(ax, 0.4, 0.5, 5.3, 1.95, "#FEF9E7", ORANGE, lw=1.5)
    ax.text(3.05, 2.12, "INJECTED AT RUNTIME  (12-factor)", fontsize=9, weight="bold", color=ORANGE, ha="center")
    draw_box(ax, Node(1.75, 1.55, 2.2, 0.5, "ConfigMap", ORANGE, fontsize=8.5))
    draw_box(ax, Node(4.35, 1.55, 2.2, 0.5, "Secret", ORANGE, fontsize=8.5))
    ax.text(3.05, 1.12, "one image, many environments —\nnever rebuild to change a setting", fontsize=7.8,
            ha="center", va="top", color=INK)

    panel(ax, 6.1, 0.5, 5.6, 1.95, "#E9F7EF", GREEN, lw=1.5)
    ax.text(8.9, 2.12, "HOW THE PLATFORM KNOWS YOU ARE WELL", fontsize=9, weight="bold", color=GREEN, ha="center")
    ax.text(8.9, 1.72, "liveness probe → restart me    readiness probe → send me traffic",
            fontsize=8, ha="center", va="top", color=INK)
    ax.text(8.9, 1.34, "requests = what I need to be scheduled\nlimits = the ceiling I may not exceed",
            fontsize=8, ha="center", va="top", color=INK)
    footnote(ax, "Workshop 2 creates every object on this page against a local kind cluster, then rolls out a bad image and rolls it back with one command.")
    save("27-k8s-object-map", fig)


# =================================================================== 28
def scanner_taxonomy():
    """Which scanner runs where in the pipeline."""
    fig, ax = plt.subplots(figsize=(12.5, 6.2))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(-0.5, 6.4)
    ax.axis("off")
    ax.set_title("The Scanner Taxonomy — what checks what, and when it runs",
                 fontsize=15, weight="bold", pad=14, color=INK)

    stages = [("commit", 1.5), ("pull request", 3.7), ("build", 6.0), ("deploy", 8.3), ("running", 10.6)]
    for name, x in stages:
        draw_box(ax, Node(x, 5.5, 1.9, 0.55, name, INK, fontsize=9.5))
        if x < 10:
            arrow(ax, (x + 1.0, 5.5), (x + 1.3, 5.5), color=INK, lw=1.6)

    scanners = [
        ("SECRET scanning", "credentials in code and history", RED, 1.5, 4.55, 2.0),
        ("SAST", "your source code, flaw patterns", BLUE, 3.7, 4.55, 2.0),
        ("SCA / dependencies", "libraries vs CVE databases", PURPLE, 3.7, 3.45, 2.0),
        ("IaC / config scanning", "Terraform & K8s misconfig", GREEN, 3.7, 2.35, 2.0),
        ("IMAGE scanning", "OS + language packages (Trivy)", ORANGE, 6.0, 4.55, 2.0),
        ("SBOM generation", "inventory of what is inside", ORANGE, 6.0, 3.45, 2.0),
        ("POLICY (admission)", "rules enforced at the door", PURPLE, 8.3, 4.55, 2.0),
        ("DAST", "probes the running app", RED, 10.6, 4.55, 2.0),
        ("runtime / drift", "what changed since deploy", GREY, 10.6, 3.45, 2.0),
    ]
    for name, what, color, x, y, w in scanners:
        draw_box(ax, Node(x, y, w, 0.5, name, color, fontsize=8))
        ax.text(x, y - 0.38, what, fontsize=6.9, ha="center", color=GREY)

    panel(ax, 0.4, 0.35, 11.7, 1.5, "#EBF5FB", BLUE, lw=1.5)
    ax.text(6.25, 1.55, "Two rules that decide whether any of this changes behaviour:", fontsize=9.5,
            weight="bold", color=BLUE, ha="center")
    ax.text(6.25, 1.15, "1.  Earlier is cheaper — a finding at PR time costs a comment; the same finding in production costs an incident.",
            fontsize=8.5, ha="center", color=INK)
    ax.text(6.25, 0.78, "2.  Report broadly, GATE narrowly — fail the build only on findings a developer can fix today.",
            fontsize=8.5, ha="center", color=INK)
    footnote(ax, "Most real-world risk lives in SCA (your dependencies) and secrets — start there, not with the most exotic scanner on the market.")
    save("28-scanner-taxonomy", fig)


# =================================================================== 29
def supply_chain():
    """The software supply chain attack surface and its countermeasures."""
    fig, ax = plt.subplots(figsize=(12.5, 6.4))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("Your Pipeline Is a Target — the supply chain, link by link",
                 fontsize=15, weight="bold", pad=14, color=INK)

    links = [
        ("upstream\ndependencies", 1.4, "a malicious or\nhijacked package"),
        ("base\nimages", 3.4, "an image tag that\nmoved under you"),
        ("CI actions\n& plugins", 5.4, "third-party code with\nyour credentials"),
        ("build\ninfrastructure", 7.4, "the SolarWinds case:\nthe BUILD was breached"),
        ("registry", 9.4, "a tag repointed to\na different artefact"),
        ("deploy\ntarget", 11.4, "unsigned artefact\naccepted as valid"),
    ]
    for name, x, risk in links:
        draw_box(ax, Node(x, 5.15, 1.75, 0.8, name, BLUE, fontsize=8.5))
        panel(ax, x - 0.88, 3.55, 1.76, 1.05, "#FDEDEC", RED, lw=1.0, rounding=0.04)
        ax.text(x, 4.45, "risk", fontsize=7, weight="bold", color=RED, ha="center")
        ax.text(x, 4.25, risk, fontsize=6.9, ha="center", va="top", color=GREY)
        if x < 11:
            arrow(ax, (x + 0.92, 5.15), (x + 1.1, 5.15), color=INK, lw=1.5)

    panel(ax, 0.4, 1.35, 11.7, 1.95, "#E9F7EF", GREEN, lw=1.6)
    ax.text(6.25, 3.05, "COUNTERMEASURES — in the order they pay off", fontsize=10,
            weight="bold", color=GREEN, ha="center")
    cm = [
        ("1. PIN", "versions AND digests —\nno moving tags anywhere"),
        ("2. LEAST PRIVILEGE", "scoped, short-lived tokens;\ndeclare permissions per job"),
        ("3. SBOM", "machine-readable inventory\nof everything you ship"),
        ("4. SIGN & VERIFY", "cosign on push, verify at\nadmission — provenance"),
        ("5. SLSA LEVELS", "a maturity ladder for build\nintegrity: know your target"),
    ]
    for i, (t, d) in enumerate(cm):
        x = 1.55 + i * 2.35
        draw_box(ax, Node(x, 2.5, 2.15, 0.45, t, GREEN, fontsize=8))
        ax.text(x, 2.18, d, fontsize=6.9, ha="center", va="top", color=INK)

    panel(ax, 2.6, 0.25, 7.3, 0.85, "#FEF9E7", ORANGE, lw=1.4)
    ax.text(6.25, 0.68, "The uncomfortable question: what would happen if your CI runner were compromised tonight?",
            fontsize=9, ha="center", weight="bold", color=INK)
    footnote(ax, "Your pipeline holds production credentials and runs third-party code on every commit — apply the third-party risk thinking you already apply to suppliers.")
    save("29-supply-chain", fig)


# =================================================================== 30
def policy_as_code():
    """Policy as code: author once, enforce in CI and at admission."""
    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("Compliance as Code — one rule, enforced in two places",
                 fontsize=15, weight="bold", pad=14, color=INK)

    panel(ax, 0.35, 3.95, 3.4, 2.0, "#F4ECF7", PURPLE, lw=1.6)
    ax.text(2.05, 5.62, "1. THE RULE, WRITTEN ONCE", fontsize=9, weight="bold", color=PURPLE, ha="center")
    ax.text(2.05, 5.2, "'every workload must set\nresource limits and\nrun as non-root'", fontsize=8.5,
            ha="center", va="top", color=INK)
    draw_box(ax, Node(2.05, 4.35, 2.9, 0.5, "policy.rego  (in Git)", PURPLE, fontsize=8.5))

    arrow(ax, (3.8, 4.95), (4.5, 4.95), color=PURPLE, lw=2.2)

    panel(ax, 4.6, 3.95, 3.4, 2.0, "#EBF5FB", BLUE, lw=1.6)
    ax.text(6.3, 5.62, "2. GATE IN THE PIPELINE", fontsize=9, weight="bold", color=BLUE, ha="center")
    ax.text(6.3, 5.2, "conftest test on the RENDERED\nmanifests, on every pull request", fontsize=8.5,
            ha="center", va="top", color=INK)
    draw_box(ax, Node(6.3, 4.35, 2.9, 0.5, "fails the build → fixed before merge", BLUE, fontsize=8))

    arrow(ax, (8.05, 4.95), (8.75, 4.95), color=BLUE, lw=2.2)

    panel(ax, 8.85, 3.95, 2.9, 2.0, "#E9F7EF", GREEN, lw=1.6)
    ax.text(10.3, 5.62, "3. BACKSTOP AT THE DOOR", fontsize=9, weight="bold", color=GREEN, ha="center")
    ax.text(10.3, 5.2, "admission controller in the\ncluster rejects anything\nthat arrived another way", fontsize=8.5,
            ha="center", va="top", color=INK)
    draw_box(ax, Node(10.3, 4.3, 2.5, 0.45, "no bypass route", GREEN, fontsize=8))

    panel(ax, 0.35, 1.9, 5.6, 1.75, "#FEF9E7", ORANGE, lw=1.5)
    ax.text(3.15, 3.4, "TEST WHAT SHIPS, NOT WHAT YOU WROTE", fontsize=9, weight="bold",
            color=ORANGE, ha="center")
    ax.text(3.15, 2.98, "Helm/Kustomize add labels, defaults and\npatches at RENDER time — so evaluate the\nrendered output, or you are testing a draft",
            fontsize=8.2, ha="center", va="top", color=INK)

    panel(ax, 6.2, 1.9, 5.55, 1.75, "#E9F7EF", GREEN, lw=1.5)
    ax.text(8.97, 3.4, "THE AUDIT EVIDENCE WRITES ITSELF", fontsize=9, weight="bold",
            color=GREEN, ha="center")
    ax.text(8.97, 2.98, "the policy file + its Git history + the pipeline\nrun that evaluated it = what the rule was,\nwhen it changed, and that it was enforced",
            fontsize=8.2, ha="center", va="top", color=INK)

    ax.text(6.0, 1.25, "Wiki rules are wishes.  Encoded policies are guarantees — evaluated on every single change.",
            fontsize=10, ha="center", weight="bold", color=INK)
    footnote(ax, "Workshop/Lab: a Rego policy that requires limits and non-root, run by conftest in CI — deliberately identical in shape to a production control.")
    save("30-policy-as-code", fig)


# =================================================================== 31
def slo_error_budget():
    """SLI/SLO/SLA and the error budget as a spendable resource."""
    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("SLI → SLO → Error Budget — reliability as a decision, not a wish",
                 fontsize=15, weight="bold", pad=14, color=INK)

    ladder = [("SLI", "the MEASUREMENT\nsuccessful requests ÷ total\np95 latency of /orders", BLUE, 1.9),
              ("SLO", "your internal TARGET\n99% success over 30 days\n(chosen, not inherited)", GREEN, 4.6),
              ("SLA", "the external CONTRACT\npenalties attached —\nalways looser than the SLO", PURPLE, 7.3)]
    for name, desc, color, x in ladder:
        draw_box(ax, Node(x, 5.35, 2.3, 0.6, name, color, fontsize=12))
        ax.text(x, 4.9, desc, fontsize=8, ha="center", va="top", color=INK)
        if x < 7:
            arrow(ax, (x + 1.2, 5.35), (x + 1.45, 5.35), color=INK, lw=1.8)

    panel(ax, 9.05, 4.15, 2.7, 1.75, "#FDEDEC", RED, lw=1.5)
    ax.text(10.4, 5.6, "100% IS THE WRONG\nTARGET", fontsize=9, weight="bold", color=RED,
            ha="center", va="center")
    ax.text(10.4, 4.95, "each extra nine multiplies\ncost — and users cannot\ntell past a point", fontsize=7.8,
            ha="center", va="top", color=INK)

    # budget bar
    ax.text(0.6, 3.55, "ERROR BUDGET  =  100% − SLO", fontsize=11, weight="bold", color=INK)
    ax.text(0.6, 3.15, "99% over 30 days  →  about 7.2 hours of permitted failure", fontsize=9.5, color=GREY)
    panel(ax, 0.6, 2.05, 10.9, 0.85, "#E9F7EF", GREEN, lw=1.4, rounding=0.03)
    panel(ax, 0.6, 2.05, 7.2, 0.85, "#ABEBC6", GREEN, lw=1.0, rounding=0.03)
    panel(ax, 7.8, 2.05, 3.7, 0.85, "#F5B7B1", RED, lw=1.0, rounding=0.03)
    ax.text(4.2, 2.47, "budget remaining → SHIP FEATURES", fontsize=9.5, weight="bold",
            color=GREEN, ha="center", va="center")
    ax.text(9.65, 2.47, "budget spent → RELIABILITY WINS", fontsize=9.5, weight="bold",
            color=RED, ha="center", va="center")

    panel(ax, 0.6, 0.4, 10.9, 1.35, "#EBF5FB", BLUE, lw=1.5)
    ax.text(6.05, 1.5, "Why this ends the oldest argument in IT:", fontsize=9.5, weight="bold",
            color=BLUE, ha="center")
    ax.text(6.05, 1.12, "'ship faster' vs 'be more stable' becomes one number that both sides agreed on IN ADVANCE.",
            fontsize=8.8, ha="center", color=INK)
    ax.text(6.05, 0.75, "Nobody negotiates during the incident — the policy was set when everyone was calm.",
            fontsize=8.8, ha="center", color=INK)
    footnote(ax, "Set SLOs from what users actually need, review them quarterly, and let the budget — not seniority — decide what the team works on next.")
    save("31-slo-error-budget", fig)


# =================================================================== 32
def alerting_burn_rate():
    """Symptom vs cause alerting, and burn-rate windows."""
    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("Alerting That Respects Humans — page on symptoms, ticket on causes",
                 fontsize=15, weight="bold", pad=14, color=INK)

    panel(ax, 0.35, 3.85, 5.5, 2.1, "#FDEDEC", RED, lw=1.6)
    ax.text(3.1, 5.62, "PAGE  (wake someone up)", fontsize=10, weight="bold", color=RED, ha="center")
    for i, t in enumerate(["users are failing to complete payments",
                           "error-budget burn is fast enough to exhaust it",
                           "a customer-visible journey is broken"]):
        ax.text(3.1, 5.2 - i * 0.38, "• " + t, fontsize=8.5, ha="center", color=INK)
    ax.text(3.1, 4.1, "SYMPTOMS — the user is hurting NOW", fontsize=8.5, style="italic",
            color=RED, ha="center")

    panel(ax, 6.15, 3.85, 5.5, 2.1, "#FEF9E7", ORANGE, lw=1.6)
    ax.text(8.9, 5.62, "TICKET  (deal with it tomorrow)", fontsize=10, weight="bold", color=ORANGE, ha="center")
    for i, t in enumerate(["disk will be full in six days",
                           "one replica restarted, service unaffected",
                           "certificate expires in three weeks"]):
        ax.text(8.9, 5.2 - i * 0.38, "• " + t, fontsize=8.5, ha="center", color=INK)
    ax.text(8.9, 4.1, "CAUSES — nobody is hurting yet", fontsize=8.5, style="italic",
            color=ORANGE, ha="center")

    panel(ax, 0.35, 1.55, 11.3, 2.0, "#EBF5FB", BLUE, lw=1.6)
    ax.text(6.0, 3.25, "BURN-RATE ALERTING — two windows, two urgencies", fontsize=10,
            weight="bold", color=BLUE, ha="center")
    draw_box(ax, Node(3.2, 2.5, 4.6, 0.55, "FAST: 14× burn over 1 hour  →  PAGE", RED, fontsize=9))
    ax.text(3.2, 2.08, "catastrophic — the month's budget gone in hours", fontsize=7.8,
            ha="center", color=GREY)
    draw_box(ax, Node(8.6, 2.5, 4.6, 0.55, "SLOW: 6× burn over 6 hours  →  TICKET", ORANGE, fontsize=9))
    ax.text(8.6, 2.08, "a real leak, but there is time to think", fontsize=7.8, ha="center", color=GREY)
    ax.text(6.0, 1.72, "Raw thresholds ('CPU > 80%') page you for things that do not matter and miss things that do.",
            fontsize=8.2, ha="center", color=INK, style="italic")

    panel(ax, 1.4, 0.25, 9.2, 1.0, "#E9F7EF", GREEN, lw=1.4)
    ax.text(6.0, 0.92, "Every page must be ACTIONABLE, URGENT and NOVEL — otherwise delete or downgrade it.",
            fontsize=9, weight="bold", color=GREEN, ha="center")
    ax.text(6.0, 0.55, "Every alert links a runbook. Every false page gets tuned. Alert fatigue is a SAFETY failure.",
            fontsize=8.5, ha="center", color=INK)
    footnote(ax, "Track pages per on-call shift as a team health metric — an engineer who has learned to ignore the pager is how a large outage gets missed.")
    save("32-alerting-burn-rate", fig)


# =================================================================== 33
def reliability_patterns():
    """Designing for partial failure."""
    fig, ax = plt.subplots(figsize=(12.5, 6.4))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("Designing for Failure — what happens when a dependency is sick?",
                 fontsize=15, weight="bold", pad=14, color=INK)

    draw_box(ax, Node(2.0, 5.15, 2.4, 0.7, "order service", BLUE, fontsize=10))
    draw_box(ax, Node(9.9, 5.15, 2.4, 0.7, "payment service\n(slow / down)", RED, fontsize=9.5))
    arrow(ax, (3.25, 5.15), (8.65, 5.15), color=INK, lw=2.0)
    ax.text(5.95, 5.45, "what protects the caller when the callee misbehaves?", fontsize=8.5,
            ha="center", color=GREY, style="italic")

    patterns = [
        ("TIMEOUT", GREEN, "never wait forever — an\nunbounded wait turns one\nsick service into all of them",
         "no timeout = threads pile\nup = cascading failure", 1.75),
        ("RETRY + BACKOFF\n+ JITTER", GREEN, "retry transient faults, with\ngrowing gaps and randomness\nso callers do not synchronise",
         "naive retries become a\nself-inflicted DDoS", 4.65),
        ("CIRCUIT BREAKER", ORANGE, "after N failures, stop calling\nfor a while, then probe —\nfail fast instead of hanging",
         "gives the sick service room\nto recover", 7.55),
        ("BULKHEAD +\nGRACEFUL DEGRADATION", PURPLE, "isolate resource pools; serve\nreduced function rather than\nnone at all",
         "'payment unavailable, order\nsaved' beats a 500 page", 10.45),
    ]
    for name, color, how, why, x in patterns:
        panel(ax, x - 1.35, 1.55, 2.7, 2.95, "white", color, lw=1.7)
        draw_box(ax, Node(x, 4.15, 2.45, 0.6, name, color, fontsize=8.5))
        ax.text(x, 3.72, how, fontsize=7.6, ha="center", va="top", color=INK)
        panel(ax, x - 1.2, 1.72, 2.4, 0.95, "#F4F6F7", GREY, lw=0.9, rounding=0.04)
        ax.text(x, 2.5, why, fontsize=7.2, ha="center", va="top", color=GREY, style="italic")

    panel(ax, 1.0, 0.35, 10.5, 1.0, "#E9F7EF", GREEN, lw=1.5)
    ax.text(6.25, 1.05, "And the pattern that beats all of them: RECOVER FAST.", fontsize=10,
            weight="bold", color=GREEN, ha="center")
    ax.text(6.25, 0.65, "Redundancy plus a rollback measured in seconds usually returns more availability than any amount of failure prevention.",
            fontsize=8.5, ha="center", color=INK)
    footnote(ax, "Lab 07/08 make this concrete: the order service degrades gracefully when payments is stopped, and the game day proves it under time pressure.")
    save("33-reliability-patterns", fig)


# =================================================================== 34
def platform_product():
    """Platform as a product: users, adoption, metrics."""
    fig, ax = plt.subplots(figsize=(12.5, 6.4))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("Platform as a Product — adoption is the vote, not the mandate",
                 fontsize=15, weight="bold", pad=14, color=INK)

    # funnel
    stages = [("teams AWARE of the platform", 5.9, 5.25, BLUE),
              ("teams that TRIED the golden path", 5.0, 4.45, BLUE),
              ("teams RUNNING on it in production", 4.1, 3.65, GREEN),
              ("teams who would RECOMMEND it", 3.2, 2.85, GREEN)]
    for text, w, y, color in stages:
        draw_box(ax, Node(3.4, y, w, 0.6, text, color, fontsize=8.5))
        if y > 3.0:
            arrow(ax, (3.4, y - 0.33), (3.4, y - 0.48), color=INK, lw=1.5)
    ax.text(3.4, 2.3, "every drop-off is a product problem:\ndiscoverability, docs, friction, or trust",
            fontsize=8, ha="center", va="top", color=RED, style="italic")

    panel(ax, 6.7, 3.2, 5.4, 2.75, "#EBF5FB", BLUE, lw=1.6)
    ax.text(9.4, 5.72, "THE FOUR NUMBERS TO PUBLISH", fontsize=9.5, weight="bold", color=BLUE, ha="center")
    metrics = [("ADOPTION", "% of services on the golden path — and the trend"),
               ("SPEED", "time-to-first-deploy for a NEW team"),
               ("LOAD", "support tickets per team per month (must FALL)"),
               ("EXPERIENCE", "would teams recommend it? (survey / NPS)")]
    for i, (k, v) in enumerate(metrics):
        y = 5.3 - i * 0.55
        ax.text(7.0, y, k, fontsize=8.5, weight="bold", color=BLUE, va="center")
        ax.text(8.5, y, v, fontsize=7.8, color=INK, va="center")

    panel(ax, 6.7, 1.5, 5.4, 1.5, "#E9F7EF", GREEN, lw=1.5)
    ax.text(9.4, 2.78, "THE ROI SENTENCE", fontsize=9, weight="bold", color=GREEN, ha="center")
    ax.text(9.4, 2.4, "(toil hours saved per team × number of teams)\n+ risk reduction from one assessed path\n− the platform team's cost",
            fontsize=8.2, ha="center", va="top", color=INK)

    panel(ax, 0.6, 0.3, 11.4, 1.0, "#FEF9E7", ORANGE, lw=1.5)
    ax.text(6.3, 1.0, "START FROM THE THINNEST VIABLE PLATFORM — grow by demand, not by roadmap fantasy.",
            fontsize=9.5, weight="bold", color=ORANGE, ha="center")
    ax.text(6.3, 0.62, "A wiki page that documents the one good way is a platform. Build the automation where the pain actually is.",
            fontsize=8.5, ha="center", color=INK)
    footnote(ax, "If teams must file a ticket and wait, you have built a silo with better branding. Self-service is the test that separates platform from bottleneck.")
    save("34-platform-product", fig)


# =================================================================== 35
def twelve_factor():
    """Build, release, run separation and config in the environment."""
    fig, ax = plt.subplots(figsize=(12.5, 6.2))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(-0.5, 6.4)
    ax.axis("off")
    ax.set_title("The Portability Contract — build once, configure per environment, run anywhere",
                 fontsize=14.5, weight="bold", pad=14, color=INK)

    draw_box(ax, Node(2.0, 5.05, 2.9, 0.85, "BUILD\ncode → immutable image\n(happens ONCE)", BLUE, fontsize=8.5))
    arrow(ax, (3.5, 5.05), (4.2, 5.05), color=INK, lw=2.0)
    draw_box(ax, Node(5.7, 5.05, 2.9, 0.85, "RELEASE\nimage + this environment's\nconfig", ORANGE, fontsize=8.5))
    arrow(ax, (7.2, 5.05), (7.9, 5.05), color=INK, lw=2.0)
    draw_box(ax, Node(9.4, 5.05, 2.9, 0.85, "RUN\nprocesses started from\nthat release", GREEN, fontsize=8.5))
    ax.text(11.4, 5.05, "strictly\nseparate", fontsize=8, color=GREY, ha="center", va="center", style="italic")

    # environments
    envs = [("dev", 2.4), ("test", 5.0), ("staging", 7.6), ("production", 10.2)]
    ax.text(4.4, 4.42, "the SAME image digest, four different configurations", fontsize=9,
            ha="center", color=INK, weight="bold")
    ax.plot([2.4, 10.2], [4.15, 4.15], color=GREEN, lw=1.6, zorder=1)
    arrow(ax, (9.4, 4.6), (9.4, 4.2), color=GREEN, lw=1.6)
    for name, x in envs:
        draw_box(ax, Node(x, 3.6, 2.1, 0.5, name, GREY, fontsize=9))
        arrow(ax, (x, 4.13), (x, 3.9), color=GREEN, lw=1.4)

    panel(ax, 0.5, 1.5, 5.7, 1.75, "#E9F7EF", GREEN, lw=1.5)
    ax.text(3.35, 3.0, "CONFIG LIVES IN THE ENVIRONMENT", fontsize=9, weight="bold", color=GREEN, ha="center")
    for i, t in enumerate(["endpoints, credentials, feature flags, tuning",
                           "injected at runtime (ConfigMap / Secret / env)",
                           "so a setting change needs no rebuild, no redeploy of the artefact"]):
        ax.text(3.35, 2.62 - i * 0.33, "• " + t, fontsize=7.8, ha="center", color=INK)

    panel(ax, 6.4, 1.5, 5.6, 1.75, "#EBF5FB", BLUE, lw=1.5)
    ax.text(9.2, 3.0, "WHAT MAKES ORCHESTRATION POSSIBLE", fontsize=9, weight="bold", color=BLUE, ha="center")
    for i, t in enumerate(["stateless processes — replicas are interchangeable",
                           "logs to stdout — the platform aggregates, the app does not",
                           "fast start, graceful shutdown — disposable by design"]):
        ax.text(9.2, 2.62 - i * 0.33, "• " + t, fontsize=7.8, ha="center", color=INK)

    ax.text(6.25, 0.85, "Break any of these and the platform cannot schedule, scale, move or heal your service.",
            fontsize=9.5, ha="center", weight="bold", color=INK)
    footnote(ax, "Twelve-factor (Adam Wiggins, Heroku) predates Kubernetes — but it describes exactly the contract Kubernetes assumes your application already honours.")
    save("35-twelve-factor", fig)


# =================================================================== 36
def service_boundaries():
    """Bounded contexts vs the distributed monolith."""
    fig, ax = plt.subplots(figsize=(12.5, 6.4))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("Service Boundaries — the acid test is independent deployability",
                 fontsize=15, weight="bold", pad=14, color=INK)

    # distributed monolith
    panel(ax, 0.35, 1.35, 5.7, 4.6, "#FDEDEC", RED, lw=1.6)
    ax.text(3.2, 5.62, "DISTRIBUTED MONOLITH", fontsize=10.5, weight="bold", color=RED, ha="center")
    ax.text(3.2, 5.25, "split by technical layer, shipped together", fontsize=8.2,
            style="italic", color=GREY, ha="center")
    for i, t in enumerate(["orders-api", "orders-worker", "orders-ui"]):
        draw_box(ax, Node(1.55 + i * 1.65, 4.5, 1.5, 0.5, t, GREY, fontsize=8))
    draw_box(ax, Node(3.2, 3.55, 4.6, 0.6, "ONE SHARED DATABASE", RED, fontsize=9.5))
    for i in range(3):
        arrow(ax, (1.55 + i * 1.65, 4.22), (3.2 - (1 - i) * 0.9, 3.88), color=RED, lw=1.2)
    for i, t in enumerate(["one release train — all three ship together",
                           "a schema change breaks three teams at once",
                           "network calls added, independence not gained",
                           "all the cost of distribution, none of the benefit"]):
        ax.text(3.2, 3.0 - i * 0.36, "✗  " + t, fontsize=8, ha="center", color=RED)

    # bounded contexts
    panel(ax, 6.45, 1.35, 5.7, 4.6, "#E9F7EF", GREEN, lw=1.6)
    ax.text(9.3, 5.62, "BOUNDED CONTEXTS", fontsize=10.5, weight="bold", color=GREEN, ha="center")
    ax.text(9.3, 5.25, "split by business domain, shipped alone", fontsize=8.2,
            style="italic", color=GREY, ha="center")
    for i, (svc, db) in enumerate([("Orders", "orders db"), ("Payments", "payments db"), ("Accounts", "accounts db")]):
        x = 7.65 + i * 1.65
        draw_box(ax, Node(x, 4.5, 1.5, 0.5, svc, GREEN, fontsize=8.5))
        draw_box(ax, Node(x, 3.8, 1.5, 0.42, db, GREY, fontsize=7))
        arrow(ax, (x, 4.24), (x, 4.03), color=GREEN, lw=1.2)
    ax.text(9.3, 3.35, "integration by API and events only", fontsize=8, ha="center",
            color=GREEN, style="italic")
    for i, t in enumerate(["each team deploys on its own schedule",
                           "schema is private — change it without asking",
                           "failure is contained by design",
                           "team boundary = service boundary (Conway)"]):
        ax.text(9.3, 2.95 - i * 0.36, "✓  " + t, fontsize=8, ha="center", color=GREEN)

    panel(ax, 2.0, 0.3, 8.5, 0.95, "#EBF5FB", BLUE, lw=1.5)
    ax.text(6.25, 0.95, "THE ACID TEST", fontsize=9, weight="bold", color=BLUE, ha="center")
    ax.text(6.25, 0.6, "If two services must always be released together, they are ONE service in two deployments.",
            fontsize=9, ha="center", color=INK)
    footnote(ax, "Start with a well-structured monolith. Split only where you have a real reason — independent scaling, independent release cadence, or a separate team.")
    save("36-service-boundaries", fig)


# =================================================================== 37
def reconciliation_loop():
    """The control loop that underpins Kubernetes (and Terraform)."""
    fig, ax = plt.subplots(figsize=(12, 6.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, 6.4)
    ax.axis("off")
    ax.set_title("The Reconciliation Loop — declare desired state, controllers close the gap",
                 fontsize=15, weight="bold", pad=14, color=INK)

    cx, cy, r = 3.5, 3.75, 1.85
    steps = [("OBSERVE\nactual state", 0), ("COMPARE\nto desired", 1), ("ACT\nclose the gap", 2), ("REPEAT\nforever", 3)]
    for text, i in steps:
        ang = math.pi / 2 - i * math.pi / 2
        x, y = cx + r * math.cos(ang), cy + r * math.sin(ang)
        draw_box(ax, Node(x, y, 2.05, 0.8, text, BLUE if i < 2 else GREEN, fontsize=8.5))
    # arrow ring drawn well inside the boxes so nothing is overdrawn
    ri = 0.85
    for i in range(4):
        a1 = math.pi / 2 - i * math.pi / 2 - 0.35
        a2 = math.pi / 2 - (i + 1) * math.pi / 2 + 0.35
        arrow(ax, (cx + ri * math.cos(a1), cy + ri * math.sin(a1)),
              (cx + ri * math.cos(a2), cy + ri * math.sin(a2)), color=INK, lw=1.7, rad=-0.4)
    ax.text(cx, cy, "controller", fontsize=9, weight="bold", color=GREY, ha="center", va="center")

    draw_box(ax, Node(9.1, 5.35, 4.2, 0.75, "DESIRED STATE\n5 replicas, this image, these limits", GREEN, fontsize=8.5))
    draw_box(ax, Node(9.1, 4.05, 4.2, 0.75, "ACTUAL STATE\n4 replicas — one node died", RED, fontsize=8.5))
    arrow(ax, (6.95, 4.7), (5.75, 4.3), color=INK, lw=1.6)
    ax.text(6.4, 5.0, "the difference\nis the work", fontsize=7.5, ha="center", color=GREY, style="italic")

    panel(ax, 7.0, 2.0, 4.7, 1.35, "#E9F7EF", GREEN, lw=1.4)
    ax.text(9.35, 3.07, "SELF-HEALING IS JUST THIS LOOP", fontsize=9, weight="bold", color=GREEN, ha="center")
    ax.text(9.35, 2.7, "nobody 'restarts' anything — a controller\nnotices a difference and corrects it",
            fontsize=8, ha="center", va="top", color=INK)

    panel(ax, 0.5, 0.1, 11.2, 1.1, "#EBF5FB", BLUE, lw=1.4)
    ax.text(6.1, 0.93, "SAME MODEL, TWO SPEEDS", fontsize=9, weight="bold", color=BLUE, ha="center")
    ax.text(6.1, 0.6, "Terraform: you run the loop (plan → apply).    Kubernetes: the loop runs continuously, forever.",
            fontsize=8.5, ha="center", va="center", color=INK)
    footnote(ax, "This is why editing a live object gets reverted, why deleting a pod is pointless, and why the cluster keeps retrying: the loop never stops.")
    save("37-reconciliation-loop", fig)


# =================================================================== 38
def scaling_levers():
    """Autoscaling levers, mesh and blast-radius isolation."""
    fig, ax = plt.subplots(figsize=(12.5, 6.4))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("Managing Services at Scale — three levers, one mesh decision, one blast radius",
                 fontsize=14.5, weight="bold", pad=14, color=INK)

    levers = [
        ("HPA", "horizontal pod autoscaler", "more PODS when a metric rises\n(CPU, memory, or custom/business)", GREEN, 2.15),
        ("CLUSTER\nAUTOSCALER", "node-level capacity", "more NODES when pods cannot\nbe scheduled; removes idle ones", BLUE, 6.25),
        ("VPA", "vertical pod autoscaler", "right-sizes requests/limits from\nobserved usage (conflicts with HPA)", PURPLE, 10.35),
    ]
    for name, sub, desc, color, x in levers:
        panel(ax, x - 1.85, 3.6, 3.7, 2.3, "white", color, lw=1.7)
        draw_box(ax, Node(x, 5.35, 3.2, 0.6, name, color, fontsize=9.5))
        ax.text(x, 4.9, sub, fontsize=8, ha="center", color=GREY, style="italic")
        ax.text(x, 4.5, desc, fontsize=7.8, ha="center", va="top", color=INK)
    ax.text(6.25, 3.3, "Prerequisite for all three: stateless, fast-starting, twelve-factor services.",
            fontsize=9, ha="center", weight="bold", color=RED)

    panel(ax, 0.35, 1.35, 5.9, 1.75, "#FEF9E7", ORANGE, lw=1.5)
    ax.text(3.3, 2.85, "SERVICE MESH — capability vs cost", fontsize=9, weight="bold", color=ORANGE, ha="center")
    ax.text(3.3, 2.45, "GET: mTLS between services, retries, timeouts,\ntraffic splitting, telemetry — without app changes",
            fontsize=7.8, ha="center", va="top", color=GREEN)
    ax.text(3.3, 1.72, "PAY: a sidecar per pod, another control plane,\nupgrades, and much harder debugging",
            fontsize=7.8, ha="center", va="top", color=RED)

    panel(ax, 6.45, 1.35, 5.7, 1.75, "#E9F7EF", GREEN, lw=1.5)
    ax.text(9.3, 2.85, "BLAST RADIUS BEFORE EXOTIC SCALING", fontsize=9, weight="bold", color=GREEN, ha="center")
    ax.text(9.3, 2.45, "namespaces + quotas → separate clusters →\nseparate regions: decide what shares fate",
            fontsize=7.8, ha="center", va="top", color=INK)
    ax.text(9.3, 1.72, "Isolation usually buys more availability\nthan another scaling mechanism does.",
            fontsize=7.8, ha="center", va="top", color=INK, style="italic")

    ax.text(6.25, 0.75, "Scale problems are PLATFORM problems — product teams should inherit the answers, not derive them.",
            fontsize=9.5, ha="center", weight="bold", color=INK)
    footnote(ax, "Adopt a mesh for a specific requirement (zero-trust between services, canary traffic control) — not because the architecture diagram looks better with it.")
    save("38-scaling-levers", fig)


# =================================================================== 39
def hardening_layers():
    """Runtime hardening: workload, cluster, secrets - as platform defaults."""
    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("Runtime Hardening — a baseline every workload inherits, not a chore per team",
                 fontsize=14.5, weight="bold", pad=14, color=INK)

    layers = [
        ("CONTAINER", GREEN, ["runAsNonRoot + explicit user", "readOnlyRootFilesystem",
                              "drop ALL capabilities", "allowPrivilegeEscalation: false",
                              "seccomp profile", "no host mounts / host network"], 4.25),
        ("CLUSTER", BLUE, ["RBAC least privilege — no wildcard admin", "NetworkPolicy: DEFAULT-DENY",
                           "namespace quotas and limit ranges", "admission control enforces the baseline",
                           "audit logging on the API server", "regular upgrade and patch cycle"], 4.25),
        ("SECRETS", PURPLE, ["a real manager (Vault / KMS / external-secrets)", "encryption at rest + tight RBAC",
                             "rotation on a schedule and on suspicion", "never printed, dumped or committed",
                             "short-lived workload identity where possible", "scanning for leaked credentials"], 4.25),
    ]
    for i, (name, color, items, top) in enumerate(layers):
        x = 2.05 + i * 3.95
        panel(ax, x - 1.85, 1.55, 3.7, 4.3, "white", color, lw=1.8)
        draw_box(ax, Node(x, 5.5, 3.3, 0.55, name, color, fontsize=10))
        for j, it in enumerate(items):
            ax.text(x, 4.95 - j * 0.52, "• " + it, fontsize=7.6, ha="center", color=INK)

    panel(ax, 0.4, 0.35, 11.3, 1.05, "#FEF9E7", ORANGE, lw=1.5)
    ax.text(6.05, 1.05, "THE GOLDEN PATH SHIPS HARDENED — teams inherit security instead of re-deriving it.",
            fontsize=10, weight="bold", color=ORANGE, ha="center")
    ax.text(6.05, 0.66, "Forty hand-configured services have forty different postures and no affordable way to assess them. One enforced baseline is assessed once.",
            fontsize=8.2, ha="center", color=INK)
    footnote(ax, "Every line on this page is checkable by the policy engine from the previous slide — which is what turns a standards document into an enforced baseline.")
    save("39-hardening-layers", fig)


# =================================================================== 40
def triage_funnel():
    """Turning scanner output into a decision."""
    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("Triage — severity is not risk; context turns findings into decisions",
                 fontsize=15, weight="bold", pad=14, color=INK)

    draw_box(ax, Node(2.2, 5.5, 3.4, 0.7, "scanner output\n(hundreds of findings)", GREY, fontsize=9))
    questions = [
        ("1.  Is it FIXABLE today?", "an upgraded package or base image exists", 4.45),
        ("2.  Is the path REACHABLE?", "does our code ever call the vulnerable function?", 3.5),
        ("3.  What is the EXPOSURE?", "internet-facing or three controls deep? what data?", 2.55),
        ("4.  Any COMPENSATING control?", "record it — do not merely assert it", 1.6),
    ]
    for q, sub, y in questions:
        draw_box(ax, Node(3.3, y, 5.6, 0.6, q, BLUE, fontsize=9))
        ax.text(6.35, y, sub, fontsize=7.5, color=GREY, va="center", ha="left")
        arrow(ax, (3.3, y + 0.55), (3.3, y + 0.33), color=INK, lw=1.5)
    arrow(ax, (2.2, 5.13), (2.2, 4.78), color=INK, lw=1.6)

    panel(ax, 8.6, 3.7, 3.1, 1.5, "#FDEDEC", RED, lw=1.5)
    ax.text(10.15, 4.95, "GATE (build fails)", fontsize=9, weight="bold", color=RED, ha="center")
    ax.text(10.15, 4.6, "fixable + critical\n= fix it now", fontsize=8, ha="center", va="top", color=INK)
    panel(ax, 8.6, 2.0, 3.1, 1.4, "#FEF9E7", ORANGE, lw=1.5)
    ax.text(10.15, 3.15, "BACKLOG (owned)", fontsize=9, weight="bold", color=ORANGE, ha="center")
    ax.text(10.15, 2.8, "unfixable or lower risk\n= tracked, with a watcher", fontsize=8, ha="center", va="top", color=INK)
    panel(ax, 8.6, 0.45, 3.1, 1.3, "#E9F7EF", GREEN, lw=1.5)
    ax.text(10.15, 1.5, "ACCEPTED (expiring)", fontsize=9, weight="bold", color=GREEN, ha="center")
    ax.text(10.15, 1.15, "owner + reason + EXPIRY date\n— never a permanent ignore", fontsize=8, ha="center", va="top", color=INK)

    ax.text(3.3, 0.75, "Reduce the SOURCE, do not just triage faster:\nslim base images · dependency-update bots · scheduled rebuilds · delete unused libraries",
            fontsize=8.5, ha="center", va="top", color=INK, weight="bold")
    footnote(ax, "Track vulnerability debt like technical debt: budget recurring capacity, and watch the TREND rather than today's count.")
    save("40-triage-funnel", fig)


# =================================================================== 41
def trace_correlation():
    """One request across services, tied together by a trace ID."""
    fig, ax = plt.subplots(figsize=(12.5, 6.2))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(-0.5, 6.4)
    ax.axis("off")
    ax.set_title("Observability in Practice — one identifier ties the whole request together",
                 fontsize=14.5, weight="bold", pad=14, color=INK)

    hops = [("gateway", 1.6), ("order service", 4.0), ("payment service", 6.4), ("ledger", 8.8), ("database", 11.2)]
    for name, x in hops:
        draw_box(ax, Node(x, 5.2, 2.05, 0.6, name, BLUE, fontsize=9))
        if x < 11:
            arrow(ax, (x + 1.05, 5.2), (x + 1.3, 5.2), color=INK, lw=1.6)
    ax.text(6.25, 5.75, "trace-id: 7f3c…  propagated on every hop, present in every log line",
            fontsize=9, ha="center", color=PURPLE, weight="bold")

    # span waterfall
    spans = [("gateway", 1.2, 9.6, GREY), ("order service", 1.9, 8.4, BLUE),
             ("payment service", 3.0, 6.2, ORANGE), ("ledger", 3.6, 1.6, GREEN), ("database", 5.6, 3.4, GREEN)]
    for i, (name, x0, w, color) in enumerate(spans):
        y = 4.22 - i * 0.4
        panel(ax, x0, y - 0.15, w, 0.3, color, color, lw=0.8, rounding=0.02)
        ax.text(0.95, y, name, fontsize=7.5, ha="right", va="center", color=INK)
    ax.text(6.4, 4.66, "the payment call is where the time went — visible without adding any logging",
            fontsize=8, ha="center", color=ORANGE, style="italic")

    panel(ax, 0.4, 0.9, 5.8, 1.5, "#E9F7EF", GREEN, lw=1.5)
    ax.text(3.3, 2.25, "WHAT MAKES NEW QUESTIONS ANSWERABLE", fontsize=8.8, weight="bold", color=GREEN, ha="center")
    for i, t in enumerate(["structured (JSON) logs with consistent fields",
                           "trace/correlation ID propagated across every hop",
                           "business context as labels: tenant, channel, version"]):
        ax.text(3.3, 1.95 - i * 0.32, "• " + t, fontsize=7.8, ha="center", color=INK)

    panel(ax, 6.4, 0.9, 5.7, 1.5, "#FEF9E7", ORANGE, lw=1.5)
    ax.text(9.25, 2.25, "COSTS TO DESIGN, NOT DISCOVER", fontsize=8.8, weight="bold", color=ORANGE, ha="center")
    for i, t in enumerate(["sample deliberately — keep errors and slow tails",
                           "retention tiers: detail for days, aggregates for months",
                           "telemetry can carry personal data: classify and scrub"]):
        ax.text(9.25, 1.95 - i * 0.32, "• " + t, fontsize=7.8, ha="center", color=INK)

    ax.text(6.25, 0.4, "The test: can you answer a question nobody anticipated — WITHOUT shipping new code?",
            fontsize=9.5, ha="center", weight="bold", color=INK)
    footnote(ax, "Instrument once with OpenTelemetry (vendor-neutral) so the backend stays a reversible decision — instrumentation is the expensive, invasive part.")
    save("41-trace-correlation", fig)


# =================================================================== 42
def platform_roi():
    """The ROI case for a platform team."""
    fig, ax = plt.subplots(figsize=(12, 6.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.5, 6.4)
    ax.axis("off")
    ax.set_title("Making the ROI Case — baseline first, or every claim is an assertion",
                 fontsize=15, weight="bold", pad=14, color=INK)

    panel(ax, 0.4, 3.7, 5.4, 2.3, "#FDEDEC", RED, lw=1.6)
    ax.text(3.1, 5.7, "BEFORE  (measure this FIRST)", fontsize=9.5, weight="bold", color=RED, ha="center")
    for i, t in enumerate(["time-to-first-deploy for a new service",
                           "number of manual setup steps and systems touched",
                           "support tickets raised per team per month",
                           "assurance findings from hand-built pipelines"]):
        ax.text(3.1, 5.3 - i * 0.38, "• " + t, fontsize=8, ha="center", color=INK)
    ax.text(3.1, 3.9, "you cannot reconstruct these afterwards", fontsize=7.8,
            ha="center", color=RED, style="italic")

    arrow(ax, (5.95, 4.85), (6.55, 4.85), color=INK, lw=2.4)

    panel(ax, 6.65, 3.7, 5.0, 2.3, "#E9F7EF", GREEN, lw=1.6)
    ax.text(9.15, 5.7, "AFTER  (same measures, same format)", fontsize=9.5, weight="bold", color=GREEN, ha="center")
    for i, t in enumerate(["time-to-first-deploy, adopters vs non-adopters",
                           "steps removed; systems consolidated",
                           "tickets falling as self-service rises",
                           "one assessed path instead of N"]):
        ax.text(9.15, 5.3 - i * 0.38, "• " + t, fontsize=8, ha="center", color=INK)

    panel(ax, 0.4, 1.35, 11.2, 2.05, "#EBF5FB", BLUE, lw=1.6)
    ax.text(6.0, 3.15, "THE ARITHMETIC", fontsize=10, weight="bold", color=BLUE, ha="center")
    terms = [("toil hours saved\nper team / month", GREEN, 1.9),
             ("×  number of\nteams", GREEN, 4.0),
             ("+  risk reduction\n(one assessed path)", PURPLE, 6.35),
             ("−  platform team\n+ infra cost", RED, 8.85),
             ("=  the number you\ntake to the board", INK, 11.0)]
    for t, c, x in terms:
        ax.text(x, 2.5, t, fontsize=8.2, ha="center", va="center", color=c, weight="bold")
    ax.text(6.0, 1.68, "Prefer a conservative number you can defend over an impressive one you cannot.",
            fontsize=8.5, ha="center", color=INK, style="italic")

    panel(ax, 1.6, 0.25, 8.8, 0.85, "#FEF9E7", ORANGE, lw=1.4)
    ax.text(6.0, 0.68, "In a regulated institution, lead with control uniformity and assurance cost —",
            fontsize=9, weight="bold", ha="center", color=INK)
    ax.text(6.0, 0.4, "then add the delivery numbers. The risk case opens the door; the speed case walks through it.",
            fontsize=8.3, ha="center", color=GREY)
    footnote(ax, "Report the same four numbers, in the same format, every quarter. Consistency is what makes the trend believable.")
    save("42-platform-roi", fig)


# =================================================================== 43
def platform_operating_model():
    """How to fund, run and evolve a platform team."""
    fig, ax = plt.subplots(figsize=(12.5, 6.4))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("Operating Model — product-funded, production-grade, and willing to say no",
                 fontsize=14.5, weight="bold", pad=14, color=INK)

    panel(ax, 0.35, 4.0, 5.8, 2.0, "#FDEDEC", RED, lw=1.6)
    ax.text(3.25, 5.72, "PROJECT-FUNDED  (fails)", fontsize=9.5, weight="bold", color=RED, ha="center")
    for i, t in enumerate(["has an end date and a deliverable",
                           "team disperses at handover",
                           "platform decays: deps move, clusters upgrade",
                           "teams built on something now unmaintained"]):
        ax.text(3.25, 5.32 - i * 0.36, "✗  " + t, fontsize=8, ha="center", color=INK)

    panel(ax, 6.35, 4.0, 5.8, 2.0, "#E9F7EF", GREEN, lw=1.6)
    ax.text(9.25, 5.72, "PRODUCT-FUNDED  (works)", fontsize=9.5, weight="bold", color=GREEN, ha="center")
    for i, t in enumerate(["standing team, roadmap, named owner",
                           "improves in response to real users",
                           "has SLOs, on-call and an incident process",
                           "versioned, with real deprecation windows"]):
        ax.text(9.25, 5.32 - i * 0.36, "✓  " + t, fontsize=8, ha="center", color=INK)

    panel(ax, 0.35, 1.95, 3.8, 1.85, "#EBF5FB", BLUE, lw=1.5)
    ax.text(2.25, 3.6, "IT IS PRODUCTION", fontsize=9, weight="bold", color=BLUE, ha="center")
    ax.text(2.25, 3.2, "when the platform is down,\nEVERY team is blocked —\nso publish support hours,\nSLOs, and change notices",
            fontsize=7.8, ha="center", va="top", color=INK)

    panel(ax, 4.35, 1.95, 3.8, 1.85, "#FEF9E7", ORANGE, lw=1.5)
    ax.text(6.25, 3.6, "DEPRECATE WITHOUT RUG-PULLS", fontsize=8.6, weight="bold", color=ORANGE, ha="center")
    ax.text(6.25, 3.2, "version templates and modules,\nannounce with a migration\nwindow, know who is on\nwhich version",
            fontsize=7.8, ha="center", va="top", color=INK)

    panel(ax, 8.35, 1.95, 3.8, 1.85, "#F4ECF7", PURPLE, lw=1.5)
    ax.text(10.25, 3.6, "SAY NO DELIBERATELY", fontsize=9, weight="bold", color=PURPLE, ha="center")
    ax.text(10.25, 3.2, "one team's exotic need stays\nwith that team (escape hatch).\nEvery yes is permanent\nmaintenance surface.",
            fontsize=7.8, ha="center", va="top", color=INK)

    panel(ax, 1.2, 0.35, 10.1, 1.35, "#E9F7EF", GREEN, lw=1.5)
    ax.text(6.25, 1.45, "INTERACTION EVOLVES", fontsize=9, weight="bold", color=GREEN, ha="center")
    draw_box(ax, Node(3.6, 0.95, 3.1, 0.5, "COLLABORATE while discovering", GREEN, fontsize=8))
    arrow(ax, (5.25, 0.95), (6.0, 0.95), color=INK, lw=1.8)
    draw_box(ax, Node(7.9, 0.95, 3.3, 0.5, "X-AS-A-SERVICE once the path exists", GREEN, fontsize=8))
    ax.text(6.25, 0.5, "Stuck in permanent collaboration = not productised.   Never collaborated = built the wrong thing.",
            fontsize=7.8, ha="center", color=GREY, style="italic")
    footnote(ax, "And the line that never changes: a platform team that deploys everyone's code is the wall of confusion, rebuilt with better tooling.")
    save("43-platform-operating-model", fig)


# =================================================================== 44
def workshops_map():
    """The three workshops and the capstone, as one path."""
    fig, ax = plt.subplots(figsize=(12.5, 6.2))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(-0.5, 6.4)
    ax.axis("off")
    ax.set_title("The Three Workshops — one application, walked all the way to a golden path",
                 fontsize=14.5, weight="bold", pad=14, color=INK)

    ws = [
        ("W1  Day 1 pm", "A BASIC PIPELINE", BLUE,
         ["GitHub Actions on a pull request", "test → build image → scan → GATE",
          "report vs gate, pinned actions,\nleast-privilege token"],
         "DONE = PR triggers it, test+build green,\nyou can explain report vs gate", 2.15),
        ("W2  Day 2 am", "BUILD & DEPLOY A SERVICE", GREEN,
         ["Dockerfile → Compose → Kubernetes", "probes, limits, Service, rolling update",
          "roll forward AND roll back"],
         "DONE = /health serves from k8s on\nlocalhost:30080, rolled back once", 6.25),
        ("W3  Day 2 pm", "INFRASTRUCTURE AS CODE", ORANGE,
         ["Terraform + local Docker provider", "init → plan → apply → drift → destroy",
          "plan as review, state as the map"],
         "DONE = plan shows 3 resources, :8090\nserves, drift seen, destroy is clean", 10.35),
    ]
    for when, title, color, items, done, x in ws:
        panel(ax, x - 1.9, 2.35, 3.8, 3.5, "white", color, lw=1.8)
        ax.text(x, 5.6, when, fontsize=8.5, color=GREY, ha="center", style="italic")
        draw_box(ax, Node(x, 5.15, 3.3, 0.55, title, color, fontsize=9))
        for i, it in enumerate(items):
            ax.text(x, 4.7 - i * 0.62, "• " + it, fontsize=7.6, ha="center", va="top", color=INK)
        panel(ax, x - 1.75, 2.5, 3.5, 0.85, "#F4F6F7", GREY, lw=0.9, rounding=0.04)
        ax.text(x, 3.15, done, fontsize=7.2, ha="center", va="top", color=INK)
        if x < 10:
            arrow(ax, (x + 1.95, 4.0), (x + 2.2, 4.0), color=INK, lw=2.0)

    panel(ax, 1.2, 0.9, 10.1, 1.2, "#E9F7EF", GREEN, lw=1.7)
    ax.text(6.25, 1.85, "CAPSTONE — all three, run as ONE golden path", fontsize=10.5,
            weight="bold", color=GREEN, ha="center")
    ax.text(6.25, 1.45, "./run-capstone.sh green end to end  +  your PLATFORM-HANDOVER.md — a platform product, in miniature",
            fontsize=8.5, ha="center", va="center", color=INK)
    for x in (2.15, 6.25, 10.35):
        arrow(ax, (x, 2.3), (x, 2.15), color=GREEN, lw=1.6)
    ax.text(6.25, 0.45, "Same application throughout: the order + payment services from the demos.",
            fontsize=9, ha="center", color=GREY, style="italic")
    footnote(ax, "Stuck? Read the error, then the troubleshooting table, then ask three neighbours, then ask me. Struggling is where the learning happens.")
    save("44-workshops-map", fig)


# =================================================================== 45
def two_day_journey():
    """What participants built across the two days."""
    fig, ax = plt.subplots(figsize=(12.5, 6.4))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(-0.5, 6.6)
    ax.axis("off")
    ax.set_title("What You Built in Two Days — the whole loop, walked once, with your own hands",
                 fontsize=14.5, weight="bold", pad=14, color=INK)

    steps = [
        ("PLAN & CODE", "Git, pull requests,\nsmall batches", BLUE, 1.5, "M1–M2"),
        ("BUILD & TEST", "pipeline: test, build,\nSHA-tagged image", BLUE, 3.75, "M5 / W1"),
        ("SECURE", "scan + real gate,\npolicy as code", RED, 6.0, "M7"),
        ("DEPLOY", "container → Kubernetes,\nrolled back on command", GREEN, 8.25, "M6 / W2"),
        ("OPERATE", "metrics, SLO, alert,\none survived incident", PURPLE, 10.5, "M8"),
    ]
    for name, what, color, x, mod in steps:
        draw_box(ax, Node(x, 4.9, 2.0, 0.6, name, color, fontsize=9))
        ax.text(x, 4.45, what, fontsize=7.8, ha="center", va="top", color=INK)
        ax.text(x, 5.35, mod, fontsize=7, ha="center", color=GREY, style="italic")
        if x < 10:
            arrow(ax, (x + 1.05, 4.9), (x + 1.2, 4.9), color=INK, lw=1.8)
    arrow(ax, (10.5, 5.35), (1.5, 5.35), color=GREY, lw=1.4, rad=0.12)
    ax.text(6.0, 5.95, "feedback closes the loop — what you learn operating feeds the next change",
            fontsize=8.2, ha="center", color=GREY, style="italic")

    panel(ax, 0.4, 2.05, 5.8, 1.6, "#EBF5FB", BLUE, lw=1.5)
    ax.text(3.3, 3.45, "UNDERNEATH IT ALL", fontsize=9, weight="bold", color=BLUE, ha="center")
    for i, t in enumerate(["infrastructure declared as code, with drift detection (W3)",
                           "one immutable artefact promoted, never rebuilt",
                           "evidence produced automatically at every step"]):
        ax.text(3.3, 3.1 - i * 0.32, "• " + t, fontsize=7.9, ha="center", color=INK)

    panel(ax, 6.4, 2.05, 5.7, 1.6, "#E9F7EF", GREEN, lw=1.5)
    ax.text(9.25, 3.45, "AND HANDED OVER AS A PRODUCT", fontsize=9, weight="bold", color=GREEN, ha="center")
    for i, t in enumerate(["the capstone runs all three workshops as one path",
                           "documented in your PLATFORM-HANDOVER.md",
                           "that is a golden path — Module 9, in miniature"]):
        ax.text(9.25, 3.1 - i * 0.32, "• " + t, fontsize=7.9, ha="center", color=INK)

    panel(ax, 1.0, 0.35, 10.5, 1.35, "#FEF9E7", ORANGE, lw=1.5)
    ax.text(6.25, 1.45, "WHAT YOU STILL HAVE TO ADD AT WORK", fontsize=9, weight="bold", color=ORANGE, ha="center")
    ax.text(6.25, 1.05, "identity & access · network zoning · data classification and masked test data · evidence retention · immovable windows",
            fontsize=8.2, ha="center", va="center", color=INK)
    ax.text(6.25, 0.65, "Prove the pattern on a low-criticality service first, then take the evidence — not the enthusiasm — to risk and audit.",
            fontsize=8.2, ha="center", va="center", color=GREY, style="italic")
    footnote(ax, "Most organisations take a year to assemble this loop for the first time. You have now done it once — the second, unaided repetition is what makes it stick.")
    save("45-two-day-journey", fig)


# =================================================================== 46
def first_90_days():
    """A sequenced plan for the first 90 days back at work."""
    fig, ax = plt.subplots(figsize=(12.5, 6.2))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(-0.5, 6.4)
    ax.axis("off")
    ax.set_title("Your First 90 Days — small and finished beats big and abandoned",
                 fontsize=15, weight="bold", pad=14, color=INK)

    arrow(ax, (0.9, 5.3), (11.9, 5.3), color=INK, lw=2.0)
    for label, x in [("WEEK 1", 2.2), ("DAYS 30", 5.6), ("DAYS 60", 8.35), ("DAYS 90", 11.15)]:
        ax.plot([x], [5.3], "o", color=INK, markersize=10, zorder=5)
        ax.text(x, 5.6, label, fontsize=9, weight="bold", color=INK, ha="center")

    cols = [
        (2.2, BLUE, ["measure a BASELINE:\ndeployment frequency and\nlead time for one service",
                     "pick ONE painful manual\npath to automate"]),
        (5.6, GREEN, ["finish that automation\nend to end, documented",
                      "add a REAL gate to one\nexisting pipeline (exit 1)"]),
        (8.35, ORANGE, ["run one blameless review\nand publish it",
                       "re-run the capstone\nunaided on a clean VM"]),
        (11.15, PURPLE, ["instrument one service,\nset one honest SLO",
                        "start the platform\nconversation with your\nbaseline in hand"]),
    ]
    for x, color, items in cols:
        for i, it in enumerate(items):
            panel(ax, x - 1.28, 3.55 - i * 1.35, 2.56, 1.15, "white", color, lw=1.5)
            ax.text(x, 4.45 - i * 1.35, it, fontsize=7.6, ha="center", va="top", color=INK)
        arrow(ax, (x, 5.15), (x, 4.75), color=color, lw=1.6)

    panel(ax, 0.6, 0.35, 11.3, 1.5, "#E9F7EF", GREEN, lw=1.6)
    ax.text(6.25, 1.6, "WHY THIS ORDER", fontsize=9.5, weight="bold", color=GREEN, ha="center")
    for i, t in enumerate([
        "the baseline costs nothing, needs no approval, and permanently changes the quality of every later argument",
        "one finished automation earns you the mandate for the next; one abandoned initiative costs you three",
        "the gate and the postmortem demonstrate the practices rather than describing them — visible, small, credible",
    ]):
        ax.text(6.25, 1.25 - i * 0.33, "• " + t, fontsize=8.2, ha="center", color=INK)
    footnote(ax, "Write down the ONE thing you will do in week one, and say it out loud to the room. Spoken commitments are kept far more often than intended ones.")
    save("46-first-90-days", fig)


def main() -> None:
    devops_loop()
    cicd_pipeline()
    iac_flow()
    k8s_architecture()
    monolith_vs_microservices()
    observability_pillars()
    devsecops_shift_left()
    platform_as_product()
    team_topologies()
    incident_lifecycle()
    lab_topology()
    dora_metrics()
    wall_of_confusion()
    three_ways()
    calms_model()
    cognitive_load()
    westrum_spectrum()
    conways_law()
    batch_size_risk()
    report_vs_gate()
    gitops_push_pull()
    terraform_mental_model()
    value_stream_wait()
    deploy_vs_release()
    container_vs_vm()
    image_layers()
    k8s_object_map()
    scanner_taxonomy()
    supply_chain()
    policy_as_code()
    slo_error_budget()
    alerting_burn_rate()
    reliability_patterns()
    platform_product()
    twelve_factor()
    service_boundaries()
    reconciliation_loop()
    scaling_levers()
    hardening_layers()
    triage_funnel()
    trace_correlation()
    platform_roi()
    platform_operating_model()
    workshops_map()
    two_day_journey()
    first_90_days()
    print("All diagrams generated.")


if __name__ == "__main__":
    main()
