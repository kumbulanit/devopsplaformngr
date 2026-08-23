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
    print("All diagrams generated.")


if __name__ == "__main__":
    main()
