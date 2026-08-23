"""Generate the Day 1 and Day 2 PPTX slide decks for the training course.

Usage:
    source ../.venv/bin/activate
    python3 build_slides.py
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor

ROOT = Path(__file__).parent.parent
DIAGRAMS = ROOT / "diagrams"
OUT_DIR = Path(__file__).parent

# Brand-ish colors
COLOR_TITLE = RGBColor(0x1A, 0x3C, 0x6C)
COLOR_BODY = RGBColor(0x33, 0x33, 0x33)
COLOR_ACCENT = RGBColor(0x4A, 0x90, 0xD9)
COLOR_SECTION = RGBColor(0x4A, 0x90, 0xD9)
BG_SECTION = RGBColor(0xEA, 0xF2, 0xFB)


def _set_font(run, size: int, bold: bool = False, color=COLOR_BODY):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Calibri"


def add_title_slide(prs, title: str, subtitle: str, notes: str) -> None:
    slide_layout = prs.slide_layouts[0]  # Title Slide
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = title
    slide.placeholders[1].text = subtitle
    _set_font(slide.shapes.title.text_frame.paragraphs[0].runs[0], 40, bold=True, color=COLOR_TITLE)
    for p in slide.placeholders[1].text_frame.paragraphs:
        for r in p.runs:
            _set_font(r, 20, color=COLOR_BODY)
    if notes:
        slide.notes_slide.notes_text_frame.text = notes


def add_section_slide(prs, title: str, notes: str) -> None:
    slide_layout = prs.slide_layouts[5]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    # Background
    bg = slide.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)  # rectangle
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_SECTION
    bg.line.fill.background()
    tf = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(9), Inches(2)).text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.alignment = PP_ALIGN.CENTER
    _set_font(p.runs[0], 44, bold=True, color=COLOR_SECTION)
    if notes:
        slide.notes_slide.notes_text_frame.text = notes


def add_content_slide(prs, title: str, bullets: List[str], notes: str) -> None:
    slide_layout = prs.slide_layouts[1]  # Title and Content
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = title
    _set_font(slide.shapes.title.text_frame.paragraphs[0].runs[0], 32, bold=True, color=COLOR_TITLE)

    body = slide.placeholders[1].text_frame
    body.clear()
    for i, bullet in enumerate(bullets):
        p = body.add_paragraph() if i > 0 else body.paragraphs[0]
        p.text = bullet
        p.level = 0
        p.font.size = Pt(20)
        p.font.color.rgb = COLOR_BODY
        p.font.name = "Calibri"
    if notes:
        slide.notes_slide.notes_text_frame.text = notes


def add_two_column_slide(prs, title: str, left: List[str], right: List[str], notes: str) -> None:
    slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(slide_layout)
    title_shape = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    tf = title_shape.text_frame
    tf.text = title
    _set_font(tf.paragraphs[0].runs[0], 32, bold=True, color=COLOR_TITLE)

    def add_col(x, items):
        box = slide.shapes.add_textbox(Inches(x), Inches(1.3), Inches(4.3), Inches(5.5))
        tf = box.text_frame
        tf.word_wrap = True
        for i, item in enumerate(items):
            p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
            p.text = item
            p.level = 0
            p.font.size = Pt(18)
            p.font.color.rgb = COLOR_BODY
            p.font.name = "Calibri"

    add_col(0.5, left)
    add_col(5.2, right)
    if notes:
        slide.notes_slide.notes_text_frame.text = notes


def add_diagram_slide(prs, title: str, image_name: str, caption: str, notes: str) -> None:
    slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(slide_layout)
    title_shape = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    tf = title_shape.text_frame
    tf.text = title
    _set_font(tf.paragraphs[0].runs[0], 30, bold=True, color=COLOR_TITLE)

    img_path = DIAGRAMS / f"{image_name}.png"
    if img_path.exists():
        pic = slide.shapes.add_picture(str(img_path), Inches(1.0), Inches(1.2), width=Inches(8.0))
    else:
        box = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(2))
        box.text_frame.text = f"[Diagram not found: {image_name}.png]"

    cap = slide.shapes.add_textbox(Inches(0.5), Inches(6.5), Inches(9), Inches(0.8))
    cap_tf = cap.text_frame
    cap_tf.text = caption
    _set_font(cap_tf.paragraphs[0].runs[0], 16, color=COLOR_BODY)
    cap_tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    if notes:
        slide.notes_slide.notes_text_frame.text = notes


def add_quote_slide(prs, title: str, quote: str, source: str, notes: str) -> None:
    slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(slide_layout)
    title_shape = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    tf = title_shape.text_frame
    tf.text = title
    _set_font(tf.paragraphs[0].runs[0], 32, bold=True, color=COLOR_TITLE)

    quote_box = slide.shapes.add_textbox(Inches(1), Inches(2.0), Inches(8), Inches(3.5))
    qtf = quote_box.text_frame
    qtf.word_wrap = True
    p = qtf.paragraphs[0]
    p.text = f"\"{quote}\""
    p.alignment = PP_ALIGN.CENTER
    _set_font(p.runs[0], 28, color=COLOR_ACCENT)

    src_box = slide.shapes.add_textbox(Inches(1), Inches(5.5), Inches(8), Inches(0.8))
    stf = src_box.text_frame
    stf.text = f"— {source}"
    stf.paragraphs[0].alignment = PP_ALIGN.RIGHT
    _set_font(stf.paragraphs[0].runs[0], 18, color=COLOR_BODY)
    if notes:
        slide.notes_slide.notes_text_frame.text = notes


def build_deck(deck_title: str, subtitle: str, modules: List[dict], output_name: str) -> None:
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    add_title_slide(prs, deck_title, subtitle,
                    notes="Welcome participants. Explain that slides include detailed notes that also serve as the participant reference. Encourage questions and note-taking.")

    for mod in modules:
        add_section_slide(prs, mod["section_title"], notes=mod.get("section_notes", ""))
        for slide in mod["slides"]:
            stype = slide["type"]
            if stype == "content":
                add_content_slide(prs, slide["title"], slide["bullets"], slide.get("notes", ""))
            elif stype == "diagram":
                add_diagram_slide(prs, slide["title"], slide["image"], slide.get("caption", ""), slide.get("notes", ""))
            elif stype == "two_col":
                add_two_column_slide(prs, slide["title"], slide["left"], slide["right"], slide.get("notes", ""))
            elif stype == "quote":
                add_quote_slide(prs, slide["title"], slide["quote"], slide.get("source", ""), slide.get("notes", ""))

    out_path = OUT_DIR / output_name
    prs.save(out_path)
    print(f"Saved {out_path}")


# ---------------------------------------------------------------------------
# Day 1 content
# ---------------------------------------------------------------------------
DAY1_MODULES = [
    {
        "section_title": "Module 1\nIntroduction to DevOps and Platform Engineering",
        "section_notes": "Set the stage: participants will spend two days moving from principles to practice. Emphasise that DevOps is not a job title but a way of working, and platform engineering is the discipline that makes that way of working scalable.",
        "slides": [
            {
                "type": "content",
                "title": "What is DevOps?",
                "bullets": [
                    "A set of practices that combines software development (Dev) and IT operations (Ops).",
                    "Aims to shorten the systems development life cycle and deliver continuous high-quality software.",
                    "Underpinned by CALMS: Culture, Automation, Lean, Measurement, Sharing.",
                    "Not a tool, not a role — it is a way of organising work around flow and feedback.",
                    "Core loop: Plan → Create → Verify → Release → Deploy → Operate → Monitor → repeat."
                ],
                "notes": "DevOps emerged from the observation that throwing code over the wall from dev to ops creates delays and outages. CALMS is a useful checklist: if one element is missing, the transformation is fragile."
            },
            {
                "type": "diagram",
                "title": "The DevOps Infinity Loop",
                "image": "01-devops-infinity-loop",
                "caption": "DevOps is a continuous cycle of feedback, learning and improvement.",
                "notes": "Point out that the left side emphasises building the right thing and building it right, while the right side emphasises operating it safely and learning from production."
            },
            {
                "type": "content",
                "title": "What is Platform Engineering?",
                "bullets": [
                    "Platform engineering builds and maintains internal developer platforms (IDPs).",
                    "An IDP glues together tools, APIs, workflows and guard rails so stream-aligned teams can self-serve.",
                    "It reduces cognitive load: developers focus on features, not on wiring up infrastructure.",
                    "It treats the platform as a product with users, a backlog, SLOs and a roadmap.",
                    "Typical capabilities: compute, observability, CI/CD, secrets, policy, environments."
                ],
                "notes": "Use the analogy of a public cloud: AWS does not make you hand-craft every VM. A good internal platform gives the same experience inside an organisation."
            },
            {
                "type": "content",
                "title": "Synergy: DevOps + Platform Engineering",
                "bullets": [
                    "DevOps defines the culture and practices; platform engineering provides the paved road.",
                    "Without a platform, every team reinvents pipelines, monitoring and deployment patterns.",
                    "Without DevOps culture, the platform becomes a central bottleneck or ignored shelfware.",
                    "Together they enable fast flow, high quality and reduced toil at scale.",
                    "Platform teams succeed when they act as enablers, not gatekeepers."
                ],
                "notes": "A useful phrase: 'DevOps is the what and why; platform engineering is the how at scale.' Mention Team Topologies: platform teams should reduce, not increase, cognitive load."
            },
            {
                "type": "quote",
                "title": "Key Takeaway",
                "quote": "Platform engineering turns DevOps from a heroic individual effort into a repeatable, scalable organisational capability.",
                "source": "Course synthesis",
                "notes": "Pause here. Ask participants for one pain point they experience where a platform could help."
            },
        ]
    },
    {
        "section_title": "Module 2\nCulture and Collaboration",
        "section_notes": "This module shifts from technology to people. Most DevOps failures are cultural, not technical. Use this time to make the case for psychological safety and shared ownership.",
        "slides": [
            {
                "type": "content",
                "title": "Building a Collaborative Culture",
                "bullets": [
                    "Psychological safety: people can speak up, ask questions and admit mistakes without blame.",
                    "Shared ownership: the whole team owns availability, security, cost and user outcomes.",
                    "Westrum organisational culture predicts software delivery performance.",
                    "High-trust environments learn faster and recover from incidents more quickly.",
                    "Practical habits: blameless postmortems, pair/mob work, transparent metrics."
                ],
                "notes": "Reference the DORA research and the book Accelerate. Cite evidence that culture is measurable and correlates with business outcomes."
            },
            {
                "type": "content",
                "title": "Communication Strategies",
                "bullets": [
                    "Align language: devs, ops, security and product should share goals, not jargon.",
                    "Chat-ops and shared channels reduce ticket tennis and increase context.",
                    "Document decisions in lightweight ADRs (Architecture Decision Records).",
                    "Run regular ceremonies that include all disciplines: stand-ups, refinement, retros.",
                    "Visible work: Kanban or boards that show flow across teams, not just inside teams."
                ],
                "notes": "Encourage participants to map their current communication friction points. The lab will practise a pull request and retro workflow."
            },
            {
                "type": "two_col",
                "title": "Overcoming Silos",
                "left": [
                    "Symptoms of silos:",
                    "• Long hand-off queues",
                    "• 'Works on my machine'",
                    "• Separate blame cultures",
                    "• Duplicated tooling",
                    "• Slow incident response"
                ],
                "right": [
                    "Antidotes:",
                    "• Cross-functional teams",
                    "• Shared on-call rotations",
                    "• Common platforms and APIs",
                    "• Joint OKRs across functions",
                    "• Team Topologies patterns"
                ],
                "notes": "Ask the room which symptom is most familiar. Transition to the next module: tools alone cannot fix silos, but the wrong tools can reinforce them."
            },
            {
                "type": "diagram",
                "title": "Team Topologies",
                "image": "09-team-topologies",
                "caption": "Choose the right team type for the right problem.",
                "notes": "Briefly introduce stream-aligned, platform, complicated-subsystem and enabling teams. Emphasise that platform teams exist to reduce cognitive load, not to own everything."
            }
        ]
    },
    {
        "section_title": "Module 3\nTools and Technologies",
        "section_notes": "This is a survey module. The goal is not to master every tool but to understand the categories and how they compose into a toolchain.",
        "slides": [
            {
                "type": "content",
                "title": "Essential Tool Categories",
                "bullets": [
                    "Source control: Git, GitHub, GitLab, Bitbucket — the single source of truth.",
                    "CI/CD: GitHub Actions, GitLab CI, Azure DevOps, Jenkins, CircleCI, Argo Workflows.",
                    "IaC: Terraform, Pulumi, Ansible, CloudFormation, ARM/Bicep.",
                    "Containers & orchestration: Docker, containerd, Kubernetes, Helm.",
                    "Observability: Prometheus, Grafana, Datadog, Honeycomb, Jaeger, ELK/Loki."
                ],
                "notes": "Encourage participants to map their current toolchain to these categories and identify gaps."
            },
            {
                "type": "content",
                "title": "Automation and Orchestration",
                "bullets": [
                    "Automate what is repeated, error-prone or slows flow: builds, tests, deployments, provisioning.",
                    "Orchestration coordinates multiple automated tasks across systems and teams.",
                    "Workflow engines (e.g. Argo, Airflow) handle complex, event-driven pipelines.",
                    "Idempotency matters: running the same automation twice should converge to the same state.",
                    "Start with versioned scripts, evolve to declarative platforms, add guard rails."
                ],
                "notes": "Make the distinction: automation does a task; orchestration coordinates tasks. Both reduce toil and free humans for higher-value work."
            },
            {
                "type": "content",
                "title": "Monitoring & Analytics for Continuous Improvement",
                "bullets": [
                    "DORA metrics: deployment frequency, lead time, change failure rate, MTTR.",
                    "Platform engineering adds platform adoption, developer satisfaction and self-serve metrics.",
                    "Use metrics to prioritise work, not to punish people.",
                    "Dashboards should lead to action: alerts need runbooks, trends need owners.",
                    "Continuous improvement = measure, hypothesise, experiment, learn."
                ],
                "notes": "Metrics are powerful levers. If the team believes metrics will be weaponised, they will game them. Frame metrics as improvement signals."
            }
        ]
    },
    {
        "section_title": "Module 4\nInfrastructure as Code (IaC)",
        "section_notes": "IaC is often the first concrete win participants can take back. Emphasise version control, idempotency and state management.",
        "slides": [
            {
                "type": "content",
                "title": "Principles of IaC",
                "bullets": [
                    "Infrastructure is defined in files, reviewed, versioned and tested like application code.",
                    "Declarative: describe the desired state; the tool converges reality to match it.",
                    "Idempotent: repeated applies produce the same result (no drift or duplication).",
                    "Immutable infrastructure: change by replacing, not by patching in place.",
                    "GitOps: Git is the source of truth; agents reconcile actual state automatically."
                ],
                "notes": "Contrast declarative (Terraform, CloudFormation) with imperative (scripts that run commands). Declarative models are easier to reason about and drift-detect."
            },
            {
                "type": "diagram",
                "title": "IaC Declarative Workflow",
                "image": "03-iac-flow",
                "caption": "Code → Plan → Apply → State tracking → Real infrastructure.",
                "notes": "Walk through the loop. The state file is critical: it maps real-world IDs back to the code so the tool can compute diffs safely."
            },
            {
                "type": "content",
                "title": "IaC with Configuration Management",
                "bullets": [
                    "Provisioning tools (Terraform, CloudFormation) create resources.",
                    "Configuration management (Ansible, Chef, Puppet) installs software and settings.",
                    "Container images increasingly replace config management for runtime state.",
                    "Use modules to reuse patterns across environments and teams.",
                    "Separate environment-specific values (tfvars) from reusable modules."
                ],
                "notes": "In cloud-native environments, configuration management is shrinking because containers and Kubernetes handle much of it. Still useful for bare metal and VMs."
            },
            {
                "type": "content",
                "title": "IaC Best Practices",
                "bullets": [
                    "Store code in Git; use branching, PRs and code review for every change.",
                    "Run 'plan' in CI and require human approval for production 'apply'.",
                    "Use remote state with locking to prevent concurrent changes.",
                    "Lint and validate: terraform fmt, validate, tflint, checkov/tfsec.",
                    "Tag resources, use least privilege, and keep secrets out of state files."
                ],
                "notes": "These practices turn IaC from a convenience into a safety mechanism. The lab will exercise plan/apply and state with the Docker provider so no cloud account is needed."
            }
        ]
    },
    {
        "section_title": "Module 5\nContinuous Integration and Continuous Delivery (CI/CD)",
        "section_notes": "CI/CD is the engine of fast flow. Tie it back to the DevOps loop and the platform: pipelines should be products, not snowflakes.",
        "slides": [
            {
                "type": "content",
                "title": "The CI/CD Pipeline",
                "bullets": [
                    "Continuous Integration: merge code to trunk frequently, validate with automated tests.",
                    "Continuous Delivery: keep code in a deployable state; deploy to production on demand.",
                    "Continuous Deployment: deploy automatically after tests pass (higher maturity).",
                    "Pipeline stages: build, test, security scan, artifact, deploy, verify, monitor.",
                    "Fast feedback: fail early, surface root cause quickly, keep the pipeline green."
                ],
                "notes": "Differentiate CI, CD and continuous deployment. Most organisations aim for continuous delivery first; full auto-deployment requires strong automated testing and feature flags."
            },
            {
                "type": "diagram",
                "title": "CI/CD Pipeline Flow",
                "image": "02-cicd-pipeline",
                "caption": "From commit through production, with feedback and rollback loops.",
                "notes": "Trace the arrows. Security scans sit in the middle because they must be fast enough not to break flow. Feedback loops allow rollbacks and fix-forward."
            },
            {
                "type": "content",
                "title": "Integrating Platform Engineering into CI/CD",
                "bullets": [
                    "Golden templates provide approved pipeline patterns out-of-the-box.",
                    "Self-service environments let teams spin up ephemeral staging safely.",
                    "Secrets and credentials are managed by the platform, not hard-coded in repos.",
                    "Deployment targets are abstracted: teams deploy to environments, not to servers.",
                    "Observability hooks are injected by the platform so every service is monitored by default."
                ],
                "notes": "This is where platform engineering pays off: a small platform team can enable many stream-aligned teams to ship safely without becoming a ticket desk."
            },
            {
                "type": "content",
                "title": "Case Study: Successful CI/CD",
                "bullets": [
                    "Goal: reduce release lead time from weeks to hours while keeping change-failure rate low.",
                    "Approach: trunk-based development, feature flags, automated canary analysis.",
                    "Platform provided templated pipelines, artefact registry and deployment guard rails.",
                    "Outcome: higher deployment frequency, faster recovery, reduced manual toil.",
                    "Lesson: optimise for small, safe changes rather than big-bang releases."
                ],
                "notes": "This case study synthesises patterns from the State of DevOps reports. Invite participants to compare with their own release cadence."
            }
        ]
    }
]

# ---------------------------------------------------------------------------
# Day 2 content
# ---------------------------------------------------------------------------
DAY2_MODULES = [
    {
        "section_title": "Module 6\nMicroservices and Containerization",
        "section_notes": "Day 2 is hands-on. Start with concepts, then move into Docker, Compose and Kubernetes labs. Keep slides concise enough to leave time for labs.",
        "slides": [
            {
                "type": "content",
                "title": "Microservices Architecture",
                "bullets": [
                    "Services are small, independently deployable and model bounded business contexts.",
                    "Benefits: team autonomy, polyglot technology, independent scaling, faster releases.",
                    "Costs: distributed-system complexity, network latency, data consistency challenges.",
                    "Use microservices when the organisational and scaling benefits outweigh the overhead.",
                    "Monolith-first is still a valid, often recommended, starting point."
                ],
                "notes": "Avoid 'microservices are always better'. They solve organisational scaling problems as much as technical ones."
            },
            {
                "type": "diagram",
                "title": "Monolith vs Microservices",
                "image": "05-monolith-vs-microservices",
                "caption": "Microservices trade deployment independence for operational complexity.",
                "notes": "Point out that each microservice owns its data and can be scaled, deployed and owned independently."
            },
            {
                "type": "content",
                "title": "Containerization with Docker",
                "bullets": [
                    "Containers package an application plus its dependencies into a portable image.",
                    "Images are layered and immutable; containers are runtime instances.",
                    "Dockerfile best practices: small base images, multi-stage builds, non-root users, health checks.",
                    "Images belong in a registry; tags tie them to versions and pipelines.",
                    "Docker Compose orchestrates multiple containers on a single host."
                ],
                "notes": "Link to the sample app: one Dockerfile for the order service and another for the payment service, composed together."
            },
            {
                "type": "content",
                "title": "Kubernetes Fundamentals",
                "bullets": [
                    "Kubernetes automates deployment, scaling and management of containerised applications.",
                    "Control plane: API server, etcd, scheduler, controller manager.",
                    "Worker nodes run kubelet, kube-proxy and Pods (one or more containers).",
                    "Key resources: Deployment, Service, ConfigMap, Secret, Ingress, Namespace.",
                    "Declarative YAML manifests are stored in Git and applied by CI/CD or GitOps agents."
                ],
                "notes": "Do not try to cover every resource. Focus on the minimum viable mental model: desired state declared in YAML, reconciled by controllers."
            },
            {
                "type": "diagram",
                "title": "Kubernetes Architecture",
                "image": "04-kubernetes-architecture",
                "caption": "Control plane manages desired state; worker nodes run Pods.",
                "notes": "The diagram shows a four-worker cluster. Mention that control-plane components can run on dedicated nodes or as Pods themselves (in managed clouds)."
            },
            {
                "type": "content",
                "title": "Managing Services at Scale",
                "bullets": [
                    "Service discovery and load balancing are built in via Services and DNS.",
                    "Horizontal Pod Autoscaling adjusts replicas based on CPU, memory or custom metrics.",
                    "Rolling updates and rollbacks reduce deployment risk.",
                    "Resource requests and limits prevent noisy neighbours.",
                    "Namespaces isolate environments and teams on a shared cluster."
                ],
                "notes": "These capabilities turn Kubernetes from an orchestrator into a platform substrate. The platform team curates these patterns for the organisation."
            }
        ]
    },
    {
        "section_title": "Module 7\nSecurity and Compliance (DevSecOps)",
        "section_notes": "Security is often the biggest concern for production adoption. Position DevSecOps as shifting security left without shifting all responsibility onto developers.",
        "slides": [
            {
                "type": "content",
                "title": "DevSecOps: Security in the Pipeline",
                "bullets": [
                    "Security is everyone's responsibility, not a final checkpoint.",
                    "Shift left: detect vulnerabilities as early as possible, when they are cheapest to fix.",
                    "Automate scans: SAST, DAST, dependency, secrets, container image, IaC policy.",
                    "Provide fast, actionable feedback in the tools developers already use.",
                    "Maintain an audit trail through versioned code, pipelines and signed artefacts."
                ],
                "notes": "Shifting left does not mean dumping security tools on developers without support. Platform teams should integrate scanners into pipelines and offer remediation guidance."
            },
            {
                "type": "diagram",
                "title": "Shifting Security Left",
                "image": "07-devsecops-shift-left",
                "caption": "Security gates at every lifecycle stage, not just before production.",
                "notes": "Trace each stage. Emphasise that 'Operate' includes runtime threat detection and vulnerability management."
            },
            {
                "type": "content",
                "title": "Compliance as Code",
                "bullets": [
                    "Encode compliance rules in version-controlled policy definitions.",
                    "Examples: CIS benchmarks, SOC 2 controls, GDPR data-handling rules.",
                    "Tools: Open Policy Agent (OPA), Checkov, Terraform Sentinel, Falco.",
                    "Policy is evaluated automatically in CI/CD, in admission control and at runtime.",
                    "Evidence is generated continuously, making audits easier and less manual."
                ],
                "notes": "Compliance as code turns audit cycles from panic events into everyday assurance. Demonstrate that policy can reject a deployment before it reaches production."
            },
            {
                "type": "content",
                "title": "Security Best Practices for Platform Engineering",
                "bullets": [
                    "Least privilege: narrow RBAC, no shared admin credentials, short-lived tokens.",
                    "Secrets management: Vault, cloud KMS, Kubernetes External Secrets — never commit secrets.",
                    "Immutable images: scan, sign and promote images through environments.",
                    "Network segmentation: policies, service mesh mTLS, egress controls.",
                    "Supply chain security: SBOMs, signed commits, dependency pinning."
                ],
                "notes": "These practices become platform defaults: every team inherits them by using the golden path, but can still opt out with documented justification."
            }
        ]
    },
    {
        "section_title": "Module 8\nObservability and Reliability",
        "section_notes": "Reliability is not about zero incidents; it is about understanding and controlling systems well enough to recover quickly.",
        "slides": [
            {
                "type": "diagram",
                "title": "The Three Pillars of Observability",
                "image": "06-observability-pillars",
                "caption": "Metrics, logs and traces answer different operational questions.",
                "notes": "Define each pillar. Metrics show trends, logs show details, traces show causality across services. The real value is asking new questions without deploying new code."
            },
            {
                "type": "content",
                "title": "Ensuring System Reliability",
                "bullets": [
                    "Reliability is a feature, not an afterthought.",
                    "SLOs (Service Level Objectives) define acceptable reliability for user journeys.",
                    "SLIs measure it; error budgets balance innovation against stability.",
                    "Design for failure: retries, circuit breakers, bulkheads, graceful degradation.",
                    "Chaos engineering validates assumptions by injecting controlled failures."
                ],
                "notes": "Reliability engineering asks: 'How reliable does this need to be for our users, and what are we willing to pay for that reliability?'"
            },
            {
                "type": "diagram",
                "title": "Incident Response Lifecycle",
                "image": "10-incident-lifecycle",
                "caption": "Detect → Triage → Mitigate → Resolve → Postmortem → Remediate.",
                "notes": "Stress that mitigation can be a rollback or feature-flag disable; resolution fixes the root cause. Postmortems are learning opportunities, not blame sessions."
            },
            {
                "type": "content",
                "title": "Postmortems and Learning",
                "bullets": [
                    "Blameless postmortems focus on system and process, not individual fault.",
                    "Capture timeline, impact, root causes, mitigations and action items.",
                    "Publish internally to spread learning and prevent recurrence.",
                    "Track action items like any other backlog work, with owners and due dates.",
                    "Celebrate the response as well as diagnosing the cause."
                ],
                "notes": "If the culture punishes people for incidents, information will be hidden and learning will stop. Safety is the prerequisite for improvement."
            }
        ]
    },
    {
        "section_title": "Module 9\nPlatform as a Product",
        "section_notes": "This module brings together culture and platform thinking. A platform is only valuable if developers choose to use it.",
        "slides": [
            {
                "type": "diagram",
                "title": "Platform as a Product",
                "image": "08-platform-as-product",
                "caption": "A self-service internal platform accelerates stream-aligned teams.",
                "notes": "The platform team treats internal developers as customers. Capabilities are productised: documentation, APIs, CLI, templates and support."
            },
            {
                "type": "content",
                "title": "User-Centric Design for Internal Platforms",
                "bullets": [
                    "Interview teams, map developer journeys and identify pain points.",
                    "Build golden paths: the easiest way to do the right thing.",
                    "Provide clear documentation, runnable samples and sensible defaults.",
                    "Offer an escape hatch for edge cases, with documented guard rails.",
                    "Measure developer experience (DevEx) with surveys and usage metrics."
                ],
                "notes": "Platform adoption is voluntary in practice. If the platform is harder than the alternative, teams will bypass it."
            },
            {
                "type": "content",
                "title": "Measuring Success and ROI",
                "bullets": [
                    "Outcome metrics: lead time, deployment frequency, change failure rate, MTTR.",
                    "Platform metrics: adoption rate, time-to-first-service, support tickets, uptime.",
                    "Developer experience: NPS-style surveys, cognitive-load assessments.",
                    "Cost metrics: cloud spend efficiency, toil hours avoided.",
                    "Tell the story: connect platform improvements to business value."
                ],
                "notes": "ROI conversations are essential for platform funding. Combine hard metrics with qualitative stories of teams shipping faster or sleeping through incidents."
            }
        ]
    },
    {
        "section_title": "Module 10\nHands-On Workshops & Capstone",
        "section_notes": "The final module is the capstone. Participants tie together everything from both days into one end-to-end deployment.",
        "slides": [
            {
                "type": "content",
                "title": "Workshop Objectives",
                "bullets": [
                    "Set up a basic DevOps pipeline that builds, tests and publishes a container image.",
                    "Build and deploy a microservice locally and to Kubernetes.",
                    "Implement IaC for cloud-style infrastructure using Terraform.",
                    "Add security scanning and observability hooks.",
                    "Experience the 'golden path' that a platform team provides."
                ],
                "notes": "Remind participants that the capstone is not about finishing first; it is about seeing how the pieces fit together. Encourage pairing."
            },
            {
                "type": "content",
                "title": "Capstone Scenario",
                "bullets": [
                    "You are the platform team enabling a stream-aligned order-processing squad.",
                    "Provide a GitHub Actions workflow, Terraform module and Kubernetes manifests.",
                    "A developer commits code; the pipeline builds, scans, plans and deploys automatically.",
                    "Prometheus monitors the service; an SLO is defined and visible in Grafana.",
                    "Document the internal platform offering so other teams can self-serve."
                ],
                "notes": "This scenario mirrors real platform engineering work: building paved roads that abstract complexity while preserving safety."
            },
            {
                "type": "content",
                "title": "Course Summary & Next Steps",
                "bullets": [
                    "DevOps is culture + practices; platform engineering scales it through self-service.",
                    "IaC, CI/CD, containers, security, observability and product thinking are the foundations.",
                    "Start small: automate one painful path, measure it, then expand.",
                    "Invest in reliability, learning and developer experience.",
                    "Continue learning: DORA reports, Team Topologies, Platform Engineering books."
                ],
                "notes": "Close with recommended reading, communities and a feedback survey. Leave time for Q&A and certificate handover if applicable."
            }
        ]
    }
]


def main() -> None:
    build_deck(
        "DevOps & Platform Engineering",
        "Day 1 — Foundations, Culture, IaC & CI/CD",
        DAY1_MODULES,
        "DevOps-PlatformEngineering-Day1.pptx",
    )
    build_deck(
        "DevOps & Platform Engineering",
        "Day 2 — Containers, Security, Observability & Platform Thinking",
        DAY2_MODULES,
        "DevOps-PlatformEngineering-Day2.pptx",
    )


if __name__ == "__main__":
    main()
