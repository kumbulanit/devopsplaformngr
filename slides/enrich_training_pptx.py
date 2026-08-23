#!/usr/bin/env python3
from pathlib import Path
from pptx import Presentation
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent


def add_title(slide, title, subtitle=None):
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(0.7))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.0), Inches(12), Inches(0.4))
        tf2 = sub_box.text_frame
        p2 = tf2.paragraphs[0]
        p2.text = subtitle
        p2.font.size = Pt(12)
        p2.font.color.rgb = RGBColor(0x4F, 0x4F, 0x4F)


def add_bullets(slide, left, top, width, height, bullets, font_size=16):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for index, bullet in enumerate(bullets):
        p = tf.paragraphs[0] if index == 0 else tf.add_paragraph()
        p.text = bullet
        p.level = 0
        p.font.size = Pt(font_size)
        p.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
        p.bullet = True
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(6)


def add_box(slide, left, top, width, height, text, fill=RGBColor(0xD9, 0xEB, 0xF7), text_color=RGBColor(0x00, 0x00, 0x00), font_size=14):
    shape = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    shape.line.width = Pt(1.2)
    tb = slide.shapes.add_textbox(left + Inches(0.08), top + Inches(0.08), width - Inches(0.16), height - Inches(0.16))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = True
    p.font.color.rgb = text_color
    p.alignment = PP_ALIGN.CENTER
    return shape


def add_arrow(slide, left, top, width, height):
    arrow = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RIGHT_ARROW, left, top, width, height)
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = RGBColor(0x70, 0x9D, 0x32)
    arrow.line.color.rgb = RGBColor(0x70, 0x9D, 0x32)
    arrow.line.width = Pt(1.5)
    return arrow


def add_flow(slide, steps, colors=None):
    heading = slide.shapes.add_textbox(Inches(6.2), Inches(1.45), Inches(4.7), Inches(0.3))
    tf = heading.text_frame
    p = tf.paragraphs[0]
    p.text = 'Example flow'
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    start_x = Inches(0.6)
    y = Inches(1.8)
    box_w = Inches(1.65)
    box_h = Inches(0.9)
    gap = Inches(0.15)
    for i, step in enumerate(steps):
        left = start_x + i * (box_w + gap)
        fill = colors[i % len(colors)] if colors else RGBColor(0xD9, 0xEB, 0xF7)
        add_box(slide, left, y, box_w, box_h, step, fill=fill, font_size=12)
        if i < len(steps) - 1:
            add_arrow(slide, left + box_w, y + Inches(0.28), Inches(0.35), Inches(0.34))


def enrich_day1(prs):
    slides = prs.slides
    # Add richer details as appended slides.
    sections = [
        {
            'title': 'Deep Dive 1 — DevOps loop in practice',
            'subtitle': 'How a small change moves from commit to production',
            'bullets': [
                'Example: a developer fixes a bug in the order service and opens a pull request.',
                'The PR triggers linting, unit tests, container build and security checks before merge.',
                'Once merged, the pipeline publishes an image, deploys to staging and runs smoke tests.',
                'Observability dashboards and alerting confirm the change is healthy before a production rollout.',
                'The feedback loop closes when the team reviews metrics, incidents and customer impact.',
                'A simple rule is: every change should be observable, reversible and learnable.',
                'Teams avoid long-lived branches and use short feedback loops to keep quality high.',
            ],
            'steps': ['Plan', 'Commit', 'Build', 'Test', 'Deploy', 'Observe'],
        },
        {
            'title': 'Deep Dive 2 — Culture and incident response',
            'subtitle': 'Good collaboration turns incidents into learning opportunities',
            'bullets': [
                'Example: an API latency spike is detected during peak traffic.',
                'The incident channel opens, the on-call engineer shares symptoms, and the team assigns roles.',
                'A blameless review asks: what changed, what was affected, what evidence exists and how do we reduce risk?',
                'Action items become backlog work: dashboards, runbooks, autoscaling, alert tuning and dependency checks.',
                'The shared goal is resilience, not blame, and the learning becomes reusable for the next incident.',
                'Psychological safety encourages people to say “I don’t know” before a bad decision becomes a production outage.',
                'High-trust teams share operational context through chatops, docs and visible status boards.',
            ],
            'steps': ['Detect', 'Triage', 'Mitigate', 'Learn'],
        },
        {
            'title': 'Deep Dive 3 — Common toolchain for a modern team',
            'subtitle': 'A practical stack that supports fast flow and safe change',
            'bullets': [
                'Source control: GitHub or GitLab with PRs, branch protection and code review.',
                'CI: build, lint, test and scan on every change; use reusable workflow templates.',
                'Delivery: package artefacts to a registry and promote images through dev, staging and production.',
                'Operations: Terraform provisions infrastructure, Kubernetes runs workloads and Prometheus gives visibility.',
                'The platform provides defaults so teams can focus on product work rather than plumbing.',
                'A mature stack combines local developer ergonomics with enterprise-grade controls and compliance.',
                'The goal is not to install more tools; it is to reduce friction while keeping the right guardrails.',
            ],
            'steps': ['Git', 'CI', 'Registry', 'K8s', 'Observe'],
        },
        {
            'title': 'Deep Dive 4 — IaC with Terraform',
            'subtitle': 'Versioned infrastructure is easier to review and safer to change',
            'bullets': [
                'Example: a team defines a network, a database and a web app in Terraform modules.',
                'The plan phase shows the exact resources that will be created or changed before any apply.',
                'A remote state backend and locking prevent drift and conflicting updates from multiple operators.',
                'Variables and tfvars separate reusable modules from environment-specific values such as region and size.',
                'The result is repeatable environments that can be recreated from Git in minutes.',
                'Treat infrastructure changes like application changes: review them, test them and promote them carefully.',
                'Good IaC reduces environment drift, makes disaster recovery practical and improves auditability.',
            ],
            'steps': ['Write', 'Plan', 'Review', 'Apply', 'Verify'],
        },
        {
            'title': 'Deep Dive 5 — CI/CD pipeline flow',
            'subtitle': 'Build safety in layers so failures are obvious and fast to fix',
            'bullets': [
                'Example: a commit triggers a pipeline that builds the app, tests it, scans dependencies and packages an artefact.',
                'If the build fails, developers receive the failing stage and logs immediately.',
                'If it passes, the pipeline can deploy to staging, run smoke tests and optionally promote to production.',
                'Feature flags or canaries reduce blast radius and make rollback simple if metrics regress.',
                'This shortens feedback loops and keeps the release path repeatable.',
                'A high-performing pipeline is fast, deterministic and visible to everyone involved.',
                'The real value is not the pipeline itself but the confidence and speed it creates.',
            ],
            'steps': ['Build', 'Test', 'Scan', 'Deploy', 'Monitor'],
        },
        {
            'title': 'Deep Dive 6 — Measuring delivery effectiveness',
            'subtitle': 'Use metrics to guide improvement and avoid vanity dashboards',
            'bullets': [
                'Deployment frequency shows how often the team can safely deliver value to users.',
                'Lead time measures how quickly a change flows from idea to production.',
                'Change failure rate shows how risky the delivery model is in practice.',
                'MTTR highlights how quickly a team recovers when something goes wrong.',
                'DORA metrics work best when teams use them to improve flow and learning, not to punish people.',
                'Platform metrics such as self-service adoption and support tickets help quantify developer experience.',
            ],
            'steps': ['Measure', 'Analyse', 'Improve', 'Learn', 'Scale'],
        },
        {
            'title': 'Day 1 recap — A practical playbook',
            'subtitle': 'Use these patterns to move from theory to execution',
            'bullets': [
                'Start with one painful workflow: build, test, deploy, or incident response.',
                'Automate the repetitive steps and create a versioned source of truth for your environments.',
                'Add guardrails through PR reviews, security scanning and approval gates.',
                'Measure outcomes with DORA-like metrics, adoption and reliability indicators.',
                'Treat the platform as a product that removes toil and makes the right path the easiest path.',
                'Make the first win small, observable and easy to explain to the rest of the organisation.',
                'Then expand the pattern once the team has evidence that it works in practice.',
            ],
            'steps': ['Automate', 'Measure', 'Improve', 'Scale'],
        },
    ]
    for item in sections:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        add_title(slide, item['title'], item['subtitle'])
        add_bullets(slide, Inches(0.6), Inches(1.6), Inches(5.3), Inches(4.8), item['bullets'], font_size=16)
        add_flow(slide, item['steps'], colors=[RGBColor(230, 242, 255), RGBColor(232, 245, 233), RGBColor(253, 242, 212), RGBColor(243, 232, 255), RGBColor(253, 226, 232), RGBColor(234, 247, 250)])
        # Provide a second visual area on the right for the flow title.
        add_box(slide, Inches(6.2), Inches(2.0), Inches(4.9), Inches(2.2), 'What this looks like in practice\n\nA small change moves through review, automation and verification before release.', font_size=12)


def enrich_day2(prs):
    sections = [
        {
            'title': 'Deep Dive 6 — Containers and Compose',
            'subtitle': 'Package once, run consistently across environments',
            'bullets': [
                'Example: the order service and payment service are built from separate Dockerfiles and tested locally with docker compose.',
                'A multi-stage Dockerfile keeps the runtime image small and avoids shipping toolchains that are not needed in production.',
                'Compose helps developers bring up dependent services, environment variables and networks with one command.',
                'The image registry becomes the hand-off point between development, CI and deployment.',
                'This reduces drift and makes the local environment closer to production.',
                'Containers make dependency management explicit, which is a major benefit for teams that want repeatable environments.',
                'The same image can be promoted from local to CI to staging to production, provided the runtime contract stays stable.',
            ],
            'steps': ['Build', 'Compose', 'Test', 'Registry', 'Deploy'],
        },
        {
            'title': 'Deep Dive 7 — Kubernetes in practice',
            'subtitle': 'Declarative YAML and controllers turn intent into running services',
            'bullets': [
                'Example: a Deployment manages replicas, rolling updates and health checks for the order service.',
                'A Service exposes the pods through stable DNS, while an Ingress handles external routes and TLS termination.',
                'ConfigMaps and Secrets keep environment-specific values out of the image and enable safer rotations.',
                'Namespaces let teams isolate workloads on a shared cluster while still using the same platform services.',
                'The platform team can standardise these manifests and give developers a golden path.',
                'Kubernetes lets platform teams define desired state once and let the control plane reconcile it continuously.',
                'The result is more standardisation, but it requires a clear operating model for rollouts, upgrades and troubleshooting.',
            ],
            'steps': ['Manifest', 'Apply', 'Controller', 'Service', 'Scale'],
        },
        {
            'title': 'Deep Dive 8 — DevSecOps controls',
            'subtitle': 'Security becomes part of the release mechanism',
            'bullets': [
                'Example: every commit runs a secret scan, dependency scan and container image scan before deployment.',
                'Policies can block insecure images, enforce least privilege and require evidence before promotion.',
                'Signed images and SBOMs make supply chain integrity visible and auditable.',
                'Security checks are fast feedback loops, not a final gate at the end of the project.',
                'This shifts security left while preserving speed for the delivery teams.',
                'Platform teams usually pair policy-as-code with developer guidance so security remains an enabler rather than a blocker.',
                'Every control should have a clear owner, a clear signal and a clear remediation path.',
            ],
            'steps': ['Scan', 'Gate', 'Sign', 'Deploy', 'Audit'],
        },
        {
            'title': 'Deep Dive 9 — Observability and reliability',
            'subtitle': 'Your platform should answer what broke, why and how fast it is recovering',
            'bullets': [
                'Example: Prometheus collects metrics, Grafana visualises them and logs/traces explain the request path.',
                'SLOs and SLIs help the team define what reliability means for the user journey, not just for the server.',
                'Error budgets create a shared decision framework for balancing delivery velocity and stability.',
                'Alerts should route to runbooks, and dashboards should lead to action instead of just noise.',
                'Reliability engineering is a product discipline that protects trust and user experience.',
                'When services fail, the most valuable signals are often the ones that explain the impact quickly and accurately.',
                'Reliable systems are often designed around small, well-understood failure domains instead of heroic recovery.',
            ],
            'steps': ['Collect', 'Visualise', 'Alert', 'Mitigate', 'Learn'],
        },
        {
            'title': 'Deep Dive 10 — Platform as a product',
            'subtitle': 'A great internal platform removes friction and keeps teams moving',
            'bullets': [
                'Example: a developer clicks a self-service button to provision a new environment with a template, pipeline and monitoring.',
                'The platform team interviews users, measures adoption and prioritises the workflows that create the most value.',
                'Golden paths make the right behaviour easy, while guardrails keep the platform safe and consistent.',
                'The best platforms get better from feedback loops, usage telemetry and common service templates.',
                'This turns infrastructure from a bottleneck into an accelerant for the business.',
                'Treat the platform backlog like any product backlog: user pain, outcome metrics and adoption all matter.',
                'The best platforms show up in the developer experience as less toil and more momentum.',
            ],
            'steps': ['Discover', 'Template', 'Deploy', 'Measure', 'Improve'],
        },
        {
            'title': 'Deep Dive 11 — Operating model and governance',
            'subtitle': 'Scale adoption through standards, collaboration and feedback loops',
            'bullets': [
                'Governance should be lightweight and embedded in workflows rather than bolted on at the end.',
                'Teams need clear ownership of platforms, services and environments so incidents are easier to triage.',
                'Shared standards for naming, tagging, logging and security help teams scale without chaos.',
                'A platform council or architecture forum can help prioritise cross-cutting changes without slowing delivery.',
                'The operating model should make good defaults obvious and exceptional changes easy to review.',
                'Great platforms combine autonomy with enough coherence to prevent sprawl and duplication.',
            ],
            'steps': ['Standardise', 'Govern', 'Review', 'Improve', 'Scale'],
        },
        {
            'title': 'Day 2 recap — From tools to operating model',
            'subtitle': 'The real outcome is a faster, safer and more reliable delivery system',
            'bullets': [
                'Use containers and Kubernetes to make deployment portable and repeatable.',
                'Make security and observability part of the pipeline from the beginning, not as afterthoughts.',
                'Treat the platform as a product and improve it with real user feedback and measurable outcomes.',
                'Ensure every change has a path to verify, roll back and learn from the result.',
                'The most mature teams combine technical excellence with strong operating habits.',
                'A platform engineering maturity journey is usually incremental, visible and rooted in real team pain.',
                'Start with the next painful workflow, prove a better path and then expand the pattern.',
            ],
            'steps': ['Automate', 'Secure', 'Observe', 'Scale'],
        },
    ]
    for item in sections:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        add_title(slide, item['title'], item['subtitle'])
        add_bullets(slide, Inches(0.6), Inches(1.6), Inches(5.3), Inches(4.8), item['bullets'], font_size=16)
        add_flow(slide, item['steps'], colors=[RGBColor(230, 242, 255), RGBColor(232, 245, 233), RGBColor(253, 242, 212), RGBColor(243, 232, 255), RGBColor(253, 226, 232), RGBColor(234, 247, 250)])
        add_box(slide, Inches(6.2), Inches(2.0), Inches(4.9), Inches(2.2), 'How this helps the team\n\nThe workflow becomes easier to explain, easier to automate and easier to improve.', font_size=12)


def main():
    day1_path = ROOT / 'DevOps-PlatformEngineering-Day1.pptx'
    day2_path = ROOT / 'DevOps-PlatformEngineering-Day2.pptx'

    for path in [day1_path, day2_path]:
        prs = Presentation(str(path))
        if 'Day1' in path.name:
            enrich_day1(prs)
        else:
            enrich_day2(prs)
        prs.save(str(path))
        print(f'Updated {path.name}')


if __name__ == '__main__':
    main()
