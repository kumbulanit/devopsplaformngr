"""Generate original PNG diagrams for the training course.

Run with: python3 diagrams/build_diagrams.py
All output is written to diagrams/.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle

OUT_DIR = Path(__file__).parent
OUT_DIR.mkdir(exist_ok=True)


def save(name: str, fig: plt.Figure) -> None:
    path = OUT_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {path}")


@dataclass
class Node:
    x: float
    y: float
    w: float
    h: float
    text: str
    color: str = "#4A90D9"
    text_color: str = "white"
    fontsize: int = 10
    radius: float = 0.05


def draw_box(ax, node: Node) -> None:
    box = FancyBboxPatch(
        (node.x - node.w / 2, node.y - node.h / 2),
        node.w,
        node.h,
        boxstyle=f"round,pad=0.02,rounding_size={node.radius}",
        facecolor=node.color,
        edgecolor="black",
        linewidth=1.2,
    )
    ax.add_patch(box)
    ax.text(
        node.x,
        node.y,
        node.text,
        ha="center",
        va="center",
        color=node.text_color,
        fontsize=node.fontsize,
        weight="bold",
        wrap=True,
    )


def arrow(ax, start: Tuple[float, float], end: Tuple[float, float], color: str = "#333333") -> None:
    ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", color=color, lw=2))


def devops_loop():
    """DevOps infinity loop with phases."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.0, 1.0)
    ax.axis("off")
    ax.set_title("DevOps Infinity Loop", fontsize=18, weight="bold", pad=20)

    # Two halves
    theta = [i / 100 * 3.14159 for i in range(101)]
    left_x = [-0.9 * (1 - t / 3.14159) for t in theta]
    left_y = [0.7 * ((t / 3.14159) * 2 - 1) for t in theta]
    right_x = [0.9 * (t / 3.14159) for t in theta]
    right_y = [0.7 * (1 - 2 * t / 3.14159) for t in theta]

    ax.plot(left_x, left_y, color="#4A90D9", lw=6, solid_capstyle="round")
    ax.plot(right_x, right_y, color="#F5A623", lw=6, solid_capstyle="round")

    phases_left = [("Plan", -0.7, 0.75), ("Create", -0.95, 0.0), ("Verify", -0.7, -0.75)]
    phases_right = [("Release", 0.7, 0.75), ("Deploy", 0.95, 0.0), ("Operate", 0.7, -0.75), ("Monitor", 0.4, -0.35)]

    for text, x, y in phases_left:
        ax.text(x, y, text, ha="center", va="center", fontsize=11, weight="bold", color="#1a3c6c")
    for text, x, y in phases_right:
        ax.text(x, y, text, ha="center", va="center", fontsize=11, weight="bold", color="#7a4d00")

    ax.text(0, 0, "Continuous\nImprovement", ha="center", va="center", fontsize=12, style="italic", color="#333")
    save("01-devops-infinity-loop", fig)


def cicd_pipeline():
    """Linear CI/CD pipeline diagram."""
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4)
    ax.axis("off")
    ax.set_title("CI/CD Pipeline: From Commit to Production", fontsize=18, weight="bold", pad=20)

    steps = [
        (1.0, "Commit\n& PR", "#4A90D9"),
        (3.0, "Build", "#50C878"),
        (5.0, "Test", "#F5A623"),
        (7.0, "Security\nScan", "#9B59B6"),
        (9.0, "Deploy\nStaging", "#E74C3C"),
        (11.0, "Deploy\nProduction", "#2ECC71"),
    ]
    nodes = []
    for x, text, color in steps:
        node = Node(x=x, y=2.0, w=1.4, h=1.0, text=text, color=color)
        draw_box(ax, node)
        nodes.append((x, text))
    for i in range(len(steps) - 1):
        arrow(ax, (steps[i][0] + 0.75, 2.0), (steps[i + 1][0] - 0.75, 2.0))

    # Feedback loops
    ax.annotate("", xy=(3.0, 1.0), xytext=(9.0, 1.0),
                arrowprops=dict(arrowstyle="->", color="gray", lw=1.5, connectionstyle="arc3,rad=-0.3"))
    ax.text(6.0, 0.45, "Feedback / Rollback", ha="center", fontsize=9, color="gray")
    save("02-cicd-pipeline", fig)


def iac_flow():
    """IaC declarative workflow."""
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5)
    ax.axis("off")
    ax.set_title("Infrastructure as Code: Declarative Desired State", fontsize=16, weight="bold", pad=20)

    nodes = [
        Node(1.5, 3.5, 2.0, 0.8, "Source Code\n(Git)", "#4A90D9"),
        Node(4.5, 3.5, 2.0, 0.8, "Terraform Plan\n(dry run)", "#F5A623"),
        Node(7.5, 3.5, 2.0, 0.8, "Terraform Apply\n(provision)", "#50C878"),
        Node(9.5, 1.5, 1.6, 0.8, "Actual\nInfrastructure", "#E74C3C"),
    ]
    for n in nodes:
        draw_box(ax, n)

    arrow(ax, (2.6, 3.5), (3.4, 3.5))
    arrow(ax, (5.6, 3.5), (6.4, 3.5))
    arrow(ax, (8.6, 3.1), (9.0, 2.0))

    # State file
    state = FancyBboxPatch((5.0, 1.1), 3.0, 0.7, boxstyle="round,pad=0.02,rounding_size=0.05",
                           facecolor="#ECF0F1", edgecolor="black", linewidth=1)
    ax.add_patch(state)
    ax.text(6.5, 1.45, "State file tracks IDs & dependencies", ha="center", va="center", fontsize=9)

    ax.text(5.5, 0.5, "Desired state is described in code. Terraform computes diffs and converges reality.",
            ha="center", fontsize=10, style="italic", color="#333")
    save("03-iac-flow", fig)


def k8s_architecture():
    """Simplified Kubernetes cluster diagram."""
    fig, ax = plt.subplots(figsize=(12, 6.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.5)
    ax.axis("off")
    ax.set_title("Kubernetes Architecture Overview", fontsize=18, weight="bold", pad=20)

    # Control plane box
    cp = FancyBboxPatch((0.5, 3.6), 11.0, 2.6, boxstyle="round,pad=0.02,rounding_size=0.1",
                        facecolor="#D6EAF8", edgecolor="#2874A6", linewidth=2)
    ax.add_patch(cp)
    ax.text(1.0, 5.8, "Control Plane", fontsize=13, weight="bold", color="#1B4F72")

    cp_nodes = [
        Node(2.2, 4.6, 2.0, 0.7, "API Server", "#2874A6"),
        Node(5.0, 4.6, 2.0, 0.7, "etcd\n(cluster state)", "#2874A6"),
        Node(7.8, 4.6, 2.0, 0.7, "Scheduler", "#2874A6"),
        Node(10.3, 4.6, 1.6, 0.7, "Controller\nManager", "#2874A6"),
    ]
    for n in cp_nodes:
        draw_box(ax, n)

    # Worker boxes
    for i, wx in enumerate([1.5, 4.5, 7.5, 10.5]):
        worker = FancyBboxPatch((wx - 1.2, 0.5), 2.4, 2.4, boxstyle="round,pad=0.02,rounding_size=0.1",
                                facecolor="#D5F5E3", edgecolor="#1E8449", linewidth=2)
        ax.add_patch(worker)
        ax.text(wx, 2.6, f"Worker Node {i+1}", fontsize=10, weight="bold", color="#145A32", ha="center")
        draw_box(ax, Node(wx, 1.7, 1.6, 0.45, "Pod", "#1E8449", fontsize=9))
        draw_box(ax, Node(wx, 1.0, 1.8, 0.45, "kubelet / kube-proxy", "#58D68D", text_color="#145A32", fontsize=8))

    # Arrows control -> workers
    for wx in [1.5, 4.5, 7.5, 10.5]:
        ax.annotate("", xy=(wx, 2.95), xytext=(6.0, 3.95),
                    arrowprops=dict(arrowstyle="->", color="#666", lw=1.2, connectionstyle="arc3,rad=0.05"))

    save("04-kubernetes-architecture", fig)


def monolith_vs_microservices():
    """Comparison diagram."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Monolith vs Microservices", fontsize=18, weight="bold")

    for ax, title, boxes in [
        (axes[0], "Monolith", [("UI", 0.5), ("Business\nLogic", 0.5), ("Data", 0.5)]),
        (axes[1], "Microservices", [("Web", 0.28), ("Orders", 0.28), ("Payments", 0.28), ("Inventory", 0.28)]),
    ]:
        ax.set_xlim(0, 6)
        ax.set_ylim(0, 5)
        ax.axis("off")
        ax.set_title(title, fontsize=14, weight="bold")
        big = FancyBboxPatch((0.8, 1.0), 4.4, 3.0, boxstyle="round,pad=0.02,rounding_size=0.1",
                             facecolor="#FADBD8" if title == "Monolith" else "#D6EAF8",
                             edgecolor="black", linewidth=1.5)
        ax.add_patch(big)
        y = 3.6
        colors = ["#E74C3C", "#F5A623", "#4A90D9", "#50C878"]
        for idx, (text, h) in enumerate(boxes):
            draw_box(ax, Node(3.0, y, 3.0, h, text, colors[idx % len(colors)], fontsize=10))
            y -= h + 0.2

    save("05-monolith-vs-microservices", fig)


def observability_pillars():
    """Three pillars of observability."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("The Three Pillars of Observability", fontsize=18, weight="bold", pad=20)

    pillars = [
        (1.8, "Metrics", "Numerical data\nover time\n(e.g. CPU %, requests/sec)", "#E74C3C"),
        (5.0, "Logs", "Discrete events\nwith timestamps\n(e.g. error stack traces)", "#F5A623"),
        (8.2, "Traces", "Request flow\nacross services\n(e.g. OpenTelemetry)", "#4A90D9"),
    ]
    for x, title, desc, color in pillars:
        pillar = FancyBboxPatch((x - 1.1, 1.2), 2.2, 3.6, boxstyle="round,pad=0.02,rounding_size=0.1",
                                facecolor=color, edgecolor="black", linewidth=1.5, alpha=0.85)
        ax.add_patch(pillar)
        ax.text(x, 4.3, title, ha="center", va="center", fontsize=14, weight="bold", color="white")
        ax.text(x, 2.7, desc, ha="center", va="center", fontsize=9, color="white", multialignment="center")

    ax.text(5.0, 0.5, "Together they answer: what is broken and why?", ha="center", fontsize=11, style="italic")
    save("06-observability-pillars", fig)


def devsecops_shift_left():
    """Security integrated early."""
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.5)
    ax.axis("off")
    ax.set_title("DevSecOps: Shifting Security Left", fontsize=18, weight="bold", pad=20)

    stages = [
        (1.5, "Design\nThreat model"),
        (3.5, "Code\nSecrets scan"),
        (5.5, "Build\nSAST / dependency"),
        (7.5, "Test\nDAST / fuzzing"),
        (9.5, "Deploy\nRuntime policy"),
        (11.2, "Operate\nVuln mgmt"),
    ]
    for x, text in stages:
        draw_box(ax, Node(x, 2.5, 1.5, 0.9, text, "#4A90D9", fontsize=9))
    for i in range(len(stages) - 1):
        arrow(ax, (stages[i][0] + 0.8, 2.5), (stages[i + 1][0] - 0.8, 2.5))

    # Security badge above
    sec = FancyBboxPatch((0.5, 3.5), 11.0, 0.7, boxstyle="round,pad=0.02,rounding_size=0.1",
                         facecolor="#E74C3C", edgecolor="black", linewidth=1.5)
    ax.add_patch(sec)
    ax.text(6.0, 3.85, "Security gates and automated feedback at every stage", ha="center", va="center",
            fontsize=11, weight="bold", color="white")

    ax.text(6.0, 0.8, "Fixing vulnerabilities earlier is faster, cheaper and safer.",
            ha="center", fontsize=10, style="italic", color="#333")
    save("07-devsecops-shift-left", fig)


def platform_as_product():
    """Internal platform as a product."""
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("Platform as a Product: Self-Service Internal Platform", fontsize=16, weight="bold", pad=20)

    # Platform box
    platform = FancyBboxPatch((2.5, 1.5), 6.0, 3.5, boxstyle="round,pad=0.02,rounding_size=0.15",
                              facecolor="#D6EAF8", edgecolor="#2874A6", linewidth=2)
    ax.add_patch(platform)
    ax.text(5.5, 4.5, "Internal Developer Platform", ha="center", fontsize=13, weight="bold", color="#1B4F72")

    platform_caps = [
        (3.8, 3.3, "CI/CD\nPipelines"),
        (5.5, 3.3, "Golden\nTemplates"),
        (7.2, 3.3, "Observability\nStack"),
        (4.6, 2.1, "Security\nPolicies"),
        (6.4, 2.1, "IaC /\nEnvironments"),
    ]
    for x, y, text in platform_caps:
        draw_box(ax, Node(x, y, 1.3, 0.7, text, "#2874A6", fontsize=9))

    # Developers/users left
    users = [(0.8, 4.5, "Stream-aligned\nteam A"), (0.8, 3.0, "Stream-aligned\nteam B"), (0.8, 1.5, "Stream-aligned\nteam C")]
    for x, y, text in users:
        draw_box(ax, Node(x, y, 1.4, 0.7, text, "#58D68D", text_color="#145A32", fontsize=9))
        ax.annotate("", xy=(3.2, y), xytext=(1.55, y),
                    arrowprops=dict(arrowstyle="->", color="#666", lw=1.5))

    # Outcome right
    draw_box(ax, Node(10.0, 3.0, 1.5, 1.0, "Ship\nValue\nFast", "#F5A623", fontsize=11))
    ax.annotate("", xy=(9.2, 3.0), xytext=(5.8, 3.0),
                arrowprops=dict(arrowstyle="->", color="#666", lw=2))

    ax.text(5.5, 0.6, "Treat the platform like a product: backlog, UX, SLOs, and a roadmap.",
            ha="center", fontsize=10, style="italic", color="#333")
    save("08-platform-as-product", fig)


def team_topologies():
    """Core team types."""
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.5)
    ax.axis("off")
    ax.set_title("Team Topologies for DevOps & Platform Engineering", fontsize=16, weight="bold", pad=20)

    teams = [
        (2.0, "Stream-aligned\nteam", "Delivers value\n(feature teams)", "#50C878"),
        (5.0, "Platform\nteam", "Provides internal\nplatform services", "#4A90D9"),
        (8.0, "Complicated\nsubsystem team", "Deep expertise\n(e.g. ML, video)", "#9B59B6"),
        (10.8, "Enabling\nteam", "Coaches &\nupskills others", "#F5A623"),
    ]
    for x, title, desc, color in teams:
        draw_box(ax, Node(x, 2.5, 2.2, 1.2, title, color, fontsize=11))
        ax.text(x, 1.0, desc, ha="center", va="center", fontsize=8, color="#333", multialignment="center")

    save("09-team-topologies", fig)


def incident_lifecycle():
    """Incident response lifecycle."""
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.1, 1.1)
    ax.axis("off")
    ax.set_title("Incident Response & Reliability Lifecycle", fontsize=16, weight="bold", pad=20)

    steps = ["Detect", "Triage", "Mitigate", "Resolve", "Postmortem", "Remediate"]
    n = len(steps)
    radius = 0.8
    for i, label in enumerate(steps):
        angle = i * (2 * 3.14159 / n) - 3.14159 / 2
        x = radius * 1.3 * (angle)
    # simpler circular layout
    angles = [i * 2 * 3.14159 / n - 3.14159 / 2 for i in range(n)]
    coords = [(0.95 * (a), 0.95 * 3.14159 / 2 * (a)) for a in angles]  # placeholder; recalc below

    coords = []
    for a in angles:
        x = 0.85 * (a)
        # Use actual trig
        import math
        x = 0.85 * math.cos(a)
        y = 0.85 * math.sin(a)
        coords.append((x, y))

    import math
    for i, label in enumerate(steps):
        angle = i * 2 * math.pi / n - math.pi / 2
        x = 0.85 * math.cos(angle)
        y = 0.85 * math.sin(angle)
        circle = Circle((x, y), 0.22, color="#E74C3C" if "Postmortem" in label or "Remediate" in label else "#4A90D9", ec="black", lw=1.2)
        ax.add_patch(circle)
        ax.text(x, y, label, ha="center", va="center", fontsize=8, weight="bold", color="white")
        # arrows
        next_angle = ((i + 1) % n) * 2 * math.pi / n - math.pi / 2
        x2 = 0.85 * math.cos(next_angle)
        y2 = 0.85 * math.sin(next_angle)
        ax.annotate("", xy=(x2, y2), xytext=(x, y),
                    arrowprops=dict(arrowstyle="->", color="gray", lw=1.2,
                                    connectionstyle="arc3,rad=0.15"))

    ax.text(0, 0, "Continuous\nReliability", ha="center", va="center", fontsize=11, style="italic", color="#333")
    save("10-incident-lifecycle", fig)


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
    print("All diagrams generated.")


if __name__ == "__main__":
    main()
