"""Generate the Day 1 and Day 2 PPTX slide decks for the training course.

Usage:
    pip install -r slides/requirements-authoring.txt
    python3 slides/build_slides.py

Design intent:
- Modules 1-9 are IN-DEPTH THEORY. Slides carry the structure; the speaker
  notes carry the depth and double as the participant reference (the decks
  are shared with participants after the course).
- Module 10 frames the three hands-on workshops; Module 11 closes the course.
- Every slide has speaker notes. The script is idempotent: re-running it
  regenerates both decks from scratch.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

ROOT = Path(__file__).parent.parent
DIAGRAMS = ROOT / "diagrams"
OUT_DIR = Path(__file__).parent

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
    slide_layout = prs.slide_layouts[0]
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
    slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(slide_layout)
    bg = slide.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
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
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = title
    _set_font(slide.shapes.title.text_frame.paragraphs[0].runs[0], 32, bold=True, color=COLOR_TITLE)

    body = slide.placeholders[1].text_frame
    body.clear()
    for i, bullet in enumerate(bullets):
        p = body.add_paragraph() if i > 0 else body.paragraphs[0]
        p.text = bullet
        p.level = 0
        p.font.size = Pt(19)
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
        col_tf = box.text_frame
        col_tf.word_wrap = True
        for i, item in enumerate(items):
            p = col_tf.add_paragraph() if i > 0 else col_tf.paragraphs[0]
            p.text = item
            p.level = 0
            p.font.size = Pt(17)
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
        slide.shapes.add_picture(str(img_path), Inches(1.0), Inches(1.2), width=Inches(8.0))
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
    p.text = f'"{quote}"'
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
                    notes="Welcome participants. These decks are shared with participants after the course; the speaker notes double as the written reference, so read them when reviewing. Modules 1-9 are theory with small demos; the three workshops and the capstone are the hands-on core.")

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


# ===========================================================================
# DAY 1
# ===========================================================================
DAY1_MODULES = [

    # ------------------------------------------------------------- Module 1
    {
        "section_title": "Module 1\nIntroduction to DevOps and Platform Engineering",
        "section_notes": "75 minutes of theory with one 5-minute demo. Goal: participants can define DevOps precisely (not 'a team' or 'a tool'), explain why platform engineering emerged, and describe how the two relate. The depth lives in these notes - they are the participant reference.",
        "slides": [
            {
                "type": "content",
                "title": "Where DevOps Came From",
                "bullets": [
                    "Pre-2009: Dev measured on change delivered, Ops measured on stability.",
                    "Opposing incentives created the 'wall of confusion' - throw releases over it.",
                    "Result: quarterly big-bang releases, weekend war rooms, mutual blame.",
                    "2009: '10+ Deploys per Day' (Flickr) and the first devopsdays (Patrick Debois).",
                    "The insight: the conflict is a SYSTEM problem, not a people problem.",
                ],
                "notes": "Spend time on the incentive conflict - it explains everything that follows. Developers were rewarded for shipping change; operations for preventing change (uptime). Both behaved rationally and the organisation suffered: infrequent, enormous, risky releases, handled by ticket queues and handoffs. The 2009 Velocity talk by John Allspaw and Paul Hammond showed Dev and Ops at Flickr cooperating to deploy more than ten times a day - unthinkable then, and it reframed frequent deployment as a SAFETY practice: small changes are easier to review, test and roll back. Patrick Debois coined 'DevOps' with the first devopsdays conference in Ghent the same year. Ask the room: how long does a change take to reach production in your organisation today, and how much of that is waiting?"
            },
            {
                "type": "content",
                "title": "What DevOps Is (and Is Not)",
                "bullets": [
                    "A set of practices + a culture that unify development and operations around flow of value.",
                    "Goal: shorten lead time from idea to production WITHOUT sacrificing stability.",
                    "It is NOT: a job title, a team you hire, a tool you buy, or 'Ops with Jenkins'.",
                    "'You build it, you run it' (Werner Vogels, Amazon 2006) - ownership follows the code.",
                    "DevOps applies lean manufacturing thinking to software delivery.",
                ],
                "notes": "Definitions matter because 'DevOps' is the most abused word in IT. The common anti-pattern is creating a third silo called 'the DevOps team' that owns pipelines and becomes a new bottleneck between Dev and Ops - the exact problem DevOps set out to remove. The Amazon principle 'you build it, you run it' captures the ownership shift: the team that writes a service carries the pager for it, which closes the feedback loop between code quality and operational pain. The lean lineage is real, not decorative: small batch sizes, limiting work in progress, pulling quality forward, and reducing handoffs come directly from manufacturing (Toyota Production System) via the book 'The Phoenix Project'. When someone in the room says 'we have a DevOps engineer', explore what that person actually does - often they are a platform engineer (Module 1, later) or a build engineer."
            },
            {
                "type": "content",
                "title": "The Three Ways (The Phoenix Project / DevOps Handbook)",
                "bullets": [
                    "1. FLOW: optimise the whole left-to-right stream - small batches, limit WIP, remove handoffs.",
                    "2. FEEDBACK: fast right-to-left signals - tests, monitoring, pager, customer telemetry.",
                    "3. CONTINUAL LEARNING: experiment safely, practise failure, turn incidents into improvement.",
                    "Every practice in this course implements one of the Three Ways.",
                ],
                "notes": "The Three Ways (Gene Kim) are the theoretical backbone; use them as a classification tool all week. Flow: CI/CD pipelines, trunk-based development, IaC - anything that moves change left-to-right faster and in smaller pieces. Feedback: automated tests, security scans, observability, SLOs - anything that tells you quickly that something is wrong, as close to the cause as possible. Continual learning: blameless postmortems, game days, error budgets - anything that converts failure into system improvement rather than fear. A good exercise: name any practice ('code review?', 'canary deploys?', 'chaos engineering?') and have the room place it. Code review is feedback; canary is flow AND feedback; chaos engineering is learning. If a practice serves none of the three ways, question why you do it."
            },
            {
                "type": "content",
                "title": "CALMS - the Five Dimensions of DevOps",
                "bullets": [
                    "Culture - shared ownership, psychological safety, blameless learning (Module 2).",
                    "Automation - pipelines, IaC, tests: make the machine do the repeatable work (Modules 4-5).",
                    "Lean - small batches, limit WIP, eliminate waste (waiting is the biggest waste).",
                    "Measurement - DORA metrics, SLOs: decide with data, not anecdotes (Modules 3, 8).",
                    "Sharing - internal open source, documentation, demos, postmortems published widely.",
                ],
                "notes": "CALMS (Jez Humble, building on Damon Edwards and John Willis) is a health-check model: organisations routinely over-invest in Automation and under-invest in Culture and Measurement, then wonder why the tooling did not change outcomes. Walk each letter with a concrete failure mode. Culture failure: pipelines exist but every deploy still needs a change-approval board meeting. Automation failure: 'we automated the deploy' but test coverage is so thin nobody trusts it, so deploys still happen quarterly. Lean failure: one release train carrying 200 changes - when it derails, which change caused it? Measurement failure: teams argue from anecdotes ('deploys feel risky') with no data. Sharing failure: three teams each build their own deployment scripts, solving the same problem three times. This course touches every letter and the notes say where."
            },
            {
                "type": "diagram",
                "title": "The DevOps Infinity Loop",
                "image": "01-devops-infinity-loop",
                "caption": "Eight phases, one continuous flow - monitoring feeds the next plan.",
                "notes": "Walk the loop phase by phase and stress two things. First, it is a loop, not a pipeline with an end: what you learn operating and monitoring the system feeds the next planning cycle - that closing of the loop IS DevOps. Second, in a handover organisation this picture is cut in the middle: Dev owns the left half, Ops the right half, and information dies at the boundary. During the course participants traverse the whole loop once with the same small application, so by Day 2 afternoon this diagram describes what they have personally done, not an abstraction."
            },
            {
                "type": "content",
                "title": "Why Platform Engineering Emerged",
                "bullets": [
                    "'You build it, you run it' collided with the cloud-native explosion (CNCF landscape: 1000+ tools).",
                    "Every product team needed Kubernetes + Terraform + pipelines + observability + security skills.",
                    "COGNITIVE LOAD became the bottleneck: too much to know before shipping any value.",
                    "Platform engineering: a dedicated team builds an Internal Developer Platform (IDP)",
                    "  so product teams get golden paths instead of blank YAML files.",
                ],
                "notes": "The theory here is cognitive load (from cognitive psychology, applied by Team Topologies): intrinsic load is the essence of the team's actual problem (their business domain); extraneous load is everything else they must wrestle with to ship (cluster setup, pipeline syntax, scanner configuration); germane load is productive learning. Pure DevOps taken literally means every team carries all the extraneous load themselves - eight teams each becoming Kubernetes experts is waste, and worse, it crowds out the intrinsic work you actually hired them for. A platform team absorbs the extraneous load ONCE and serves it as a product: templates, pipelines, runtime, observability, security defaults. Important framing: platform engineering is not a rejection of DevOps but its industrialisation - the goal (teams own their services end to end) is unchanged; the platform makes that ownership affordable."
            },
            {
                "type": "two_col",
                "title": "DevOps vs SRE vs Platform Engineering",
                "left": [
                    "DEVOPS (a philosophy)",
                    "Whose problem: the org's delivery flow.",
                    "Core question: how do we ship faster AND safer together?",
                    "Practices: CI/CD, IaC, shared ownership, blameless culture.",
                    "",
                    "SRE (a role/discipline, Google 2003)",
                    "Whose problem: reliability at scale.",
                    "Core question: how reliable must this be, and what does that cost?",
                    "Practices: SLOs, error budgets, toil elimination, incident response.",
                ],
                "right": [
                    "PLATFORM ENGINEERING (a team + product)",
                    "Whose problem: developer cognitive load.",
                    "Core question: what paved road lets teams self-serve safely?",
                    "Practices: IDP, golden paths, templates, self-service APIs.",
                    "",
                    "They compose, not compete:",
                    "SRE defines what reliable means;",
                    "the platform makes reliable the default;",
                    "DevOps culture makes teams own the result.",
                ],
                "notes": "These three terms cause endless confusion in job adverts; give participants a crisp separation. DevOps is a philosophy of shared ownership - anyone claiming to 'hire a DevOps' is usually hiring a platform or build engineer. SRE (Site Reliability Engineering, from Google) operationalises reliability as an engineering problem: Service Level Objectives quantify how reliable a service must be, error budgets convert the gap to 100% into a spendable resource, and 'toil' (manual, repetitive, automatable operational work) is systematically eliminated - Google caps toil at 50% of an SRE's time. Platform engineering packages both into a product. Concrete example with this course's material: SRE thinking gives us the 99% SLO and burn-rate alerts (Module 8); the platform bakes probes, scanning and dashboards into the golden path (Module 10); DevOps culture means the order-service team still carries responsibility for what they ship."
            },
            {
                "type": "diagram",
                "title": "Your Lab Environment for These Two Days",
                "image": "11-course-lab-topology",
                "caption": "One Ubuntu 24.04 VM per participant - every lab runs on its localhost.",
                "notes": "Orient participants before any hands-on: native Python (the 5-minute demos), Docker Compose stacks, Terraform-managed containers and a kind Kubernetes cluster all live on one VM, and every URL in the course is http://localhost:<port>. No cloud account, no shared infrastructure, and full cleanup is one command per stack. Make the pedagogical point explicitly: the WORKFLOW is what transfers to production and cloud - swapping localhost Docker for AWS changes one Terraform provider block, not the discipline. DEMO NOW (5 min, from instructor/theory-demos.md): run lab-setup/check-environment.sh together and have everyone confirm an all-PASS table - this is the course's first automated feedback loop."
            },
            {
                "type": "quote",
                "title": "Module 1 - Key Takeaway",
                "quote": "Platform engineering turns DevOps from a heroic individual effort into a repeatable, scalable organisational capability.",
                "source": "Course synthesis",
                "notes": "Pause here and collect from the room: one pain point in their organisation this module gave a name to (wall of confusion, cognitive load, third-silo DevOps team, toil). Write them somewhere visible - Module 9's platform canvas exercise reuses this list as user pain points."
            },
        ]
    },

    # ------------------------------------------------------------- Module 2
    {
        "section_title": "Module 2\nCulture and Collaboration",
        "section_notes": "60 minutes theory + a 10-minute self-assessment exercise. The research message: culture is not the soft part - it is the strongest statistical predictor of delivery performance. Give it the same rigour as the technical modules.",
        "slides": [
            {
                "type": "content",
                "title": "Culture Is Measurable: the Westrum Typology",
                "bullets": [
                    "PATHOLOGICAL (power-oriented): info hoarded, messengers shot, failure -> scapegoating.",
                    "BUREAUCRATIC (rule-oriented): info flows in channels, failure -> process and blame-shifting.",
                    "GENERATIVE (performance-oriented): info flows freely, failure -> inquiry and learning.",
                    "DORA research: generative culture statistically predicts software delivery performance.",
                    "Culture is how the organisation responds to BAD NEWS.",
                ],
                "notes": "Ron Westrum, a sociologist studying safety-critical industries (aviation, healthcare), classified organisational cultures by how information flows - especially unwelcome information. The typology matters to us because the DORA/Accelerate research program found generative culture to be one of the strongest predictors of both delivery performance and organisational performance. The operational test is beautifully simple: what happens when someone brings bad news? Pathological: the messenger is punished, so problems are hidden until they explode. Bureaucratic: the messenger is tolerated, the problem is filed into a process, ownership diffuses. Generative: the messenger is thanked, because the organisation values the information above comfort. Every technical practice this week depends on information flowing: monitoring is worthless if an engineer fears reporting what it shows; postmortems are theatre if attendees protect themselves. EXERCISE (10 min, in theory-demos.md): each participant privately scores their organisation on five Westrum questions, then pairs discuss one concrete behaviour that would move one answer one level."
            },
            {
                "type": "content",
                "title": "Psychological Safety - the Foundation Layer",
                "bullets": [
                    "Definition (Amy Edmondson): belief that the team is safe for interpersonal risk-taking.",
                    "Google's Project Aristotle: THE top factor distinguishing effective teams.",
                    "Safe teams surface problems earlier - which looks like MORE errors, and is actually fewer.",
                    "Built in small moments: how leaders react to questions, dissent, and mistakes.",
                    "Prerequisite for: honest code review, real postmortems, accurate estimates, on-call health.",
                ],
                "notes": "Edmondson's original hospital study found the counterintuitive result that better nursing teams REPORTED more medication errors - not because they made more, but because they were safe enough to report them. That inversion is the whole story: in unsafe teams the error rate looks low because information is suppressed. Google's Project Aristotle (2012-2015, 180+ teams studied) expected to find that great teams were about who was on them; instead the strongest factor was psychological safety - how the team behaved together. For our purposes: every feedback mechanism this course teaches (tests failing, scanners flagging, monitors alerting, reviews commenting) produces bad news by design. An organisation that punishes bad news will neutralise every one of these tools - people will disable flaky tests instead of fixing them, mute alerts instead of investigating, approve reviews without reading. Culture is not adjacent to the tooling; it is the operating system the tooling runs on."
            },
            {
                "type": "content",
                "title": "Conway's Law - Architecture Mirrors Communication",
                "bullets": [
                    "'Organisations design systems that mirror their own communication structures' (1968).",
                    "Four teams building a compiler produced... a four-pass compiler.",
                    "Silos in the org chart become seams, queues and outages in the architecture.",
                    "REVERSE CONWAY MANEUVER: shape teams to match the architecture you WANT.",
                    "This is why microservices without team ownership changes always disappoint.",
                ],
                "notes": "Mel Conway's 1968 observation is one of the most empirically durable laws in software. Mechanism: designing an interface between two components requires communication between their authors; where communication is expensive (different teams, buildings, time zones, reporting lines) interfaces become rigid, minimal and slow to change. Practical consequences participants will recognise: a 'database team' produces systems where every change queues behind DBA tickets; separate QA departments produce testing as an after-the-fact phase; frontend/backend team splits produce chatty, versioned internal APIs with negotiation overhead. The reverse Conway maneuver (popularised by Team Topologies) flips the law from constraint to tool: decide the architecture you want - say, independently deployable services around business domains - then restructure teams to match, and the architecture will follow. This is also why Module 6's microservices content keeps returning to team boundaries: bounded contexts are as much organisational as technical."
            },
            {
                "type": "content",
                "title": "Communication Strategies That Scale",
                "bullets": [
                    "Default to asynchronous + written: decisions travel and survive; meetings do not.",
                    "ADRs (Architecture Decision Records): short docs capturing WHAT was decided and WHY.",
                    "ChatOps: operations in shared channels - deploys, alerts, incident timelines visible to all.",
                    "Working agreements: explicit team norms (review turnaround, on-call handoff, WIP limits).",
                    "Documentation is a product: if the platform's docs are bad, the platform is bad.",
                ],
                "notes": "Concrete mechanics, not platitudes. ADRs: a one-page numbered record per significant decision - context, options considered, decision, consequences - stored in the repo next to the code it affects. Their value compounds: two years later, 'why is this a queue and not an API call?' has an answer, and newcomers onboard by reading the decision history. ChatOps means operational events flow through shared, searchable channels: the deploy bot announces releases, alerts land where humans discuss them, and an incident's timeline reconstructs itself from the channel history - which Module 8's postmortems depend on. Working agreements make implicit expectations explicit and negotiable: 'reviews answered within 4 working hours', 'no deploys after 16:00 Friday', 'WIP limit of 2 per person'. And treat documentation with product seriousness - measured, owned, maintained - because in a platform organisation, documentation IS the user interface (Module 9 returns to this). During labs, notice how every artifact in this course - policies, pipelines, infrastructure - is written down in Git: that is communication strategy, not just tooling."
            },
            {
                "type": "content",
                "title": "Breaking Silos Without Breaking the Org",
                "bullets": [
                    "Shared goals: measure Dev AND Ops on the same outcomes (DORA metrics, SLOs).",
                    "Shared pain: developers join on-call for their own services - feedback with teeth.",
                    "Embedded rotation: ops engineers embed in product teams temporarily (enabling pattern).",
                    "Internal open source: any team may propose PRs to another team's repo - platform included.",
                    "Do NOT create a 'DevOps team' silo between Dev and Ops - it recreates the wall.",
                ],
                "notes": "Silos persist because they serve real needs - specialisation, clear accountability, career paths - so 'just collaborate more' fails. What works is restructuring incentives and interfaces. Shared goals: if Dev is bonused on features and Ops on uptime, no workshop fixes that; measuring both on lead time AND change-failure rate aligns them structurally. Shared pain: a developer who is paged at 03:00 by their own unhandled exception writes different error handling forever after - this is the feedback loop 'you build it, you run it' creates. Embedded rotation is Team Topologies' enabling pattern: temporary, explicitly time-boxed, with the goal of making the receiving team self-sufficient (not creating dependency). Internal open source (sometimes 'InnerSource') keeps the platform from becoming a bottleneck: when a product team needs a pipeline feature, they can contribute it via PR instead of filing a ticket and waiting. And name the anti-pattern out loud: a 'DevOps team' that owns all pipelines and environments is a third silo - it centralises exactly what DevOps set out to distribute."
            },
            {
                "type": "diagram",
                "title": "Team Topologies - Organising for Flow",
                "image": "09-team-topologies",
                "caption": "Four team types, three interaction modes (Skelton & Pais).",
                "notes": "Team Topologies (Matthew Skelton and Manuel Pais, 2019) is the current standard vocabulary for DevOps-era org design; participants will meet these terms in the wild. Stream-aligned teams own a product or user journey end-to-end and are the point of the whole system - every other type exists to help them flow. Platform teams reduce their cognitive load by providing an internal platform as a product. Enabling teams coach through capability gaps and are deliberately temporary - success is stepping away. Complicated-subsystem teams own components genuinely requiring rare expertise (an ML model, a codec). Equally important are the three interaction modes: collaboration (working together closely - powerful but expensive, keep it temporary), X-as-a-Service (consume through an interface with minimal contact - the target state for platform consumption), and facilitating (coaching). A healthy platform relationship EVOLVES: collaboration while discovering what teams need, then X-as-a-Service once the golden path exists. A platform stuck in permanent collaboration mode has failed to productise; one that started at X-as-a-Service without ever collaborating built the wrong thing."
            },
            {
                "type": "content",
                "title": "Blameless Postmortems and Retrospectives",
                "bullets": [
                    "Premise: people made reasonable decisions given the information they had at the time.",
                    "Ask 'what made that action seem correct?' - never 'who did it?'",
                    "Counterfactuals ('should have', 'could have') are banned - they explain nothing.",
                    "Output: systemic action items with owners and dates, tracked like feature work.",
                    "Retrospectives are the same loop at team cadence - improvement as a habit, not an event.",
                ],
                "notes": "The blameless practice comes from aviation and was brought into software mainly via Etsy (John Allspaw) and Google SRE. The reasoning is hard-nosed, not soft: if the consequence of touching an incident is punishment, engineers will hide information, and you lose the only accurate account of how your system actually fails. 'Human error' is where the investigation STARTS, not where it ends - the question is what context, tooling, documentation or alerting made the error possible or invisible. Ban counterfactuals in the room: 'they should have checked the config' describes an imaginary incident, not this one; ask instead what made not-checking seem fine (it always had been? the config was 4000 lines? the diff tool hid it?). Insist that action items are systemic (add a preflight validation, fix the runbook, page earlier) with owners and due dates in the normal backlog - a postmortem whose action items die in a document was a ritual, not learning. Participants practise a 5-line version of this after the Module 8 demo, and the format is deliberately identical to a real one."
            },
            {
                "type": "quote",
                "title": "Module 2 - Key Takeaway",
                "quote": "Culture is what happens when bad news arrives. Every tool in this course produces bad news by design - your culture decides whether that information becomes learning or silence.",
                "source": "Course synthesis",
                "notes": "Bridge to Module 3: with the people-system understood, we can now look at the tool landscape - and evaluate tools by whether they strengthen flow, feedback and learning rather than by feature lists."
            },
        ]
    },

    # ------------------------------------------------------------- Module 3
    {
        "section_title": "Module 3\nTools and Technologies",
        "section_notes": "45 minutes theory + a 15-minute toolchain-mapping exercise. Goal: participants leave with a MAP of the tool landscape and principles for choosing, not a catalogue of logos. Defuse tool-worship: tools amplify a working system, they do not create one.",
        "slides": [
            {
                "type": "content",
                "title": "The DevOps Toolchain - Categories, Not Brands",
                "bullets": [
                    "Source control (Git) - the single source of truth everything else builds on.",
                    "CI/CD - pipeline engines: GitHub Actions, GitLab CI, Jenkins, Tekton, Argo Workflows.",
                    "Artifacts - registries for images and packages: GHCR, Docker Hub, Artifactory, Nexus.",
                    "IaC + config mgmt - Terraform/OpenTofu, Pulumi | Ansible, Chef, Puppet.",
                    "Runtime - Docker, Kubernetes, serverless | Secrets - Vault, cloud KMS, SOPS.",
                    "Observability - Prometheus, Grafana, Loki, OpenTelemetry, Datadog | Incident - PagerDuty.",
                ],
                "notes": "Teach the CATEGORIES; brands churn, categories are stable. A complete delivery capability needs an answer in each category - the answer may be 'deliberately nothing yet', but it should be deliberate. Walk the flow of one change through the categories: code lands in source control; CI builds and tests it; the artifact registry stores an immutable, versioned output; IaC shapes the environment it will run in; the runtime executes it; secrets management injects credentials without embedding them; observability watches it; incident management wakes someone when watching finds trouble. Two field notes worth sharing: the CNCF landscape lists well over a thousand projects, which is precisely the cognitive-load problem platform engineering answers - nobody should evaluate a thousand tools to ship a web service; and licence changes are a real category risk (Terraform's 2023 licence change produced the OpenTofu fork under the Linux Foundation) - one more argument for keeping your usage of any tool behind an interface you control."
            },
            {
                "type": "content",
                "title": "Principles for Choosing Tools",
                "bullets": [
                    "Declarative over imperative: describe the destination, let the tool drive (diffable, reviewable).",
                    "Everything as code, everything in Git: config you cannot version, review or roll back is risk.",
                    "API-first and composable: tools must integrate into pipelines, not demand humans click.",
                    "Paved road over mandate: golden defaults teams WANT, with escape hatches.",
                    "Total cost = licences + integration + operation + training + EXIT cost.",
                ],
                "notes": "Give participants an evaluation checklist rather than recommendations. Declarative matters because a desired-state description can be diffed, code-reviewed, policy-scanned and drift-detected - an imperative script can only be re-run and hoped about; this single property is why Terraform, Kubernetes manifests and Compose files dominate their categories. 'Everything in Git' is the enabler for every other practice this course teaches: if the pipeline definition, infrastructure and policies live beside the code, then review, audit and rollback come for free. API-first: any tool that requires a human in a GUI to complete a release will eventually BE the release process. Paved road over mandate previews Module 9 - mandated tools breed shadow IT; attractive defaults breed adoption. And insist on counting exit cost up front: data export, config portability, retraining - the cheapest tool to adopt is often the most expensive to leave. Close with the culture point from Module 2: a generative organisation with mediocre tools outperforms a pathological one with the best tools money can buy, because tools amplify whatever system they land in."
            },
            {
                "type": "content",
                "title": "Automation and Orchestration Platforms",
                "bullets": [
                    "CI engines differ in hosting model: SaaS runners (Actions) vs self-managed (Jenkins) vs in-cluster (Tekton).",
                    "Runtime orchestration: Kubernetes won - scheduling, self-healing, scaling, rollout as APIs.",
                    "GitOps: Git as the source of truth for RUNTIME state - agents (Argo CD, Flux) pull and converge.",
                    "Push (pipeline applies) vs pull (cluster syncs): pull gives drift-correction + audit for free.",
                    "Event-driven automation: webhooks and controllers replace humans as the glue.",
                ],
                "notes": "Distinguish the two automation layers people conflate. Delivery automation (CI/CD engines) runs jobs in response to code events; the meaningful differences are hosting and maintenance burden - GitHub Actions outsources runner management, Jenkins gives total control at the price of becoming a pet server (ask who in the room maintains a Jenkins - there is always one), Tekton and Argo Workflows run pipelines as Kubernetes-native resources. Runtime orchestration is what keeps services running afterwards: Kubernetes' actual innovation is exposing scheduling, self-healing and rollouts as declarative APIs - which is what makes it automatable at all (Module 6 goes deep). GitOps joins the layers elegantly: instead of the pipeline pushing kubectl commands, a manifest repo describes the desired runtime state and an in-cluster agent (Argo CD, Flux) continuously pulls and converges - manual changes are automatically reverted, the audit log is git log, and cluster credentials never leave the cluster. Our labs use the push model for simplicity, but name GitOps as the production-grade evolution; the mental model - desired state in Git, an agent converging - is Terraform's loop applied to runtime."
            },
            {
                "type": "diagram",
                "title": "Measurement: the Four DORA Metrics",
                "image": "12-dora-metrics",
                "caption": "Two throughput metrics, two stability metrics - always read together.",
                "notes": "This is the measurement backbone for the whole course - introduce it here, and Modules 8 and 9 will reuse it. The DORA research program (DevOps Research and Assessment; the book 'Accelerate') surveyed tens of thousands of practitioners over a decade and produced the four metrics: deployment frequency and lead time for changes (throughput), change failure rate and failed-deployment recovery time (stability). The landmark finding: speed and stability are NOT a trade-off - elite performers are better at BOTH, because the same mechanisms (small batches, automation, fast feedback) produce speed and safety simultaneously. That single result dissolves the classic Dev-vs-Ops argument ('slow down to be safe') with data. Two warnings that must accompany any metrics talk: measure the SYSTEM, not individuals - the instant DORA metrics appear in performance reviews they will be gamed into meaninglessness; and read all four together - deploy frequency alone is trivially gamed (deploy trivia hourly) and shows up immediately in change-failure rate. EXERCISE (15 min, theory-demos.md): pairs map their own organisation's toolchain onto the categories from this module and estimate their four DORA numbers; collect a show of hands on lead time - the spread across the room is usually the best discussion starter of Day 1."
            },
            {
                "type": "content",
                "title": "This Course's Toolchain (and Why)",
                "bullets": [
                    "Git + GitHub Actions - ubiquitous, free tier, local fallback with act.",
                    "Docker + Compose - the container standard; Compose for readable multi-service local stacks.",
                    "kind + kubectl - real Kubernetes API inside Docker: zero cloud cost, full fidelity.",
                    "Terraform + Ansible - both IaC halves: provisioning and configuration management.",
                    "Trivy + Conftest/OPA - scanning and policy as code | Prometheus + Grafana - observability.",
                    "Every tool here is free, runs on your VM's localhost, and is category-representative.",
                ],
                "notes": "Justify the choices so participants can translate to their own stacks. Each tool was chosen as a representative of its CATEGORY that runs locally at zero cost: what you learn about GitHub Actions' job graph transfers to GitLab CI's stages; kind serves the genuine Kubernetes API, so every kubectl command transfers unchanged to EKS/AKS/GKE; Trivy's severity/fixability triage transfers to any scanner; Rego policies transfer to admission controllers. If the room uses Azure DevOps or Jenkins, the pipeline CONCEPTS (jobs, dependencies, gates, artifact promotion) map one-to-one even where YAML syntax differs. This is also the honest answer to 'why are we not doing this on real cloud?': the workflow is identical, localhost removes cost, account friction and blast radius, and Workshop 3 shows exactly which single file changes when you point Terraform at AWS instead of local Docker."
            },
            {
                "type": "quote",
                "title": "Module 3 - Key Takeaway",
                "quote": "A fool with a tool is still a fool - but a generative team with a paved road is a force multiplier. Choose categories deliberately; let the platform choose brands once, for everyone.",
                "source": "Course synthesis (first clause: Grady Booch)",
                "notes": "Bridge to Module 4: source control and pipelines assume the thing being delivered is code - IaC is what makes the INFRASTRUCTURE itself deliverable the same way."
            },
        ]
    },

    # ------------------------------------------------------------- Module 4
    {
        "section_title": "Module 4\nInfrastructure as Code (IaC)",
        "section_notes": "75 minutes deep theory + a 10-minute basic demo (terraform plan walk-through). Workshop 3 later today is the full hands-on. Goal: participants understand WHY declarative + state + review beats scripts, and can place Terraform vs Ansible vs images correctly.",
        "slides": [
            {
                "type": "content",
                "title": "The Problem IaC Solves",
                "bullets": [
                    "Snowflake servers: hand-built, undocumented, unreproducible - 'do not reboot #3'.",
                    "Configuration drift: environments diverge silently until 'works in staging' means nothing.",
                    "ClickOps: console changes leave no diff, no review, no rollback, no audit trail.",
                    "Disaster recovery without IaC is archaeology; with IaC it is 'apply' in a new region.",
                    "Pets vs cattle: name-and-nurse servers vs numbered, replaceable, rebuildable instances.",
                ],
                "notes": "Ground this in war stories - every ops veteran in the room has a snowflake server memory; invite one. The deep problem is that manually-produced infrastructure is UNKNOWABLE: its true configuration exists only as the accumulated side effects of every hand that touched it, so you cannot review it, reproduce it, or reason about it. Drift is the slow-motion version: staging and production started identical, then three years of hotfixes, one-off firewall rules and 'temporary' changes made 'it works in staging' an empty sentence. ClickOps is the mechanism of both: console changes are invisible to code review, produce no history, and cannot be rolled back - the console is to infrastructure what editing directly on the production server is to code. The pets/cattle metaphor (Bill Baker, popularised by CERN) captures the mindset shift: pets are named, nursed back to health, irreplaceable; cattle are numbered, replaced when sick, and their definition lives elsewhere - in code. Disaster recovery is the acid test to pose to the room: if your data centre or cloud region vanished tonight, is rebuilding a git clone + terraform apply, or six months of archaeology?"
            },
            {
                "type": "content",
                "title": "Core Principles: Declarative, Idempotent, Immutable",
                "bullets": [
                    "DECLARATIVE: describe desired END STATE; the tool computes how to get there.",
                    "  -> enables diffing (plan), review, drift detection - a script can do none of these.",
                    "IDEMPOTENT: applying twice = applying once; safe to re-run, safe to automate.",
                    "IMMUTABLE: never patch in place - build a new artifact, replace the old (like containers).",
                    "Version-controlled: the Git history of your infra IS your change management system.",
                ],
                "notes": "These four properties are the module's theoretical heart - everything else is tooling. Declarative vs imperative deserves a careful contrast: an imperative script ('create a network, then start container A, then B') encodes one path from one assumed starting point, so it breaks when reality differs and can never tell you what would change; a declarative definition ('these two containers on this network should exist') lets the tool compare desire against reality and compute the minimal path - which is exactly what terraform plan prints, and why plan output is reviewable in a pull request. Idempotence is what makes automation SAFE: a converging tool can run on every commit or on a timer; a non-idempotent script needs a human to check state first, which reintroduces the human bottleneck. Immutability transfers the container insight to infrastructure: patching a running server accumulates unknowable state, so instead you bake a new image/artifact and replace - rollback becomes 'run the previous version' instead of 'undo the patch and pray'. Version control ties it together into governance regulators actually accept: who changed what, when, reviewed by whom - it is all git log."
            },
            {
                "type": "diagram",
                "title": "The IaC Loop: Code, Plan, Apply, State, Drift",
                "image": "03-iac-flow",
                "caption": "Desired state in Git; plan previews the diff; state maps names to reality.",
                "notes": "Walk each element slowly - this diagram is Workshop 3's map. Code in Git: HCL files declaring resources, reviewed like any code. Plan: the safety mechanism - Terraform refreshes reality, compares against desire, and prints +create/~update/-destroy BEFORE anything changes; a human (or CI gate) approves the diff, not the intention. Apply: executes exactly the approved plan. The STATE FILE is the piece newcomers underestimate: it maps resource names in code to real-world IDs (this docker_container resource IS container abc123), which is how Terraform knows an existing container should be updated rather than duplicated - hence the rules: never edit it by hand, store it remotely with locking when a team shares it, and treat it as sensitive (it can contain secrets in plain text). Drift detection falls out naturally: delete a managed container manually and the next plan shows '1 to add' - Terraform noticed reality diverged from state. The lock file (.terraform.lock.hcl) pins provider versions and IS committed - reproducibility across teammates and CI. Participants run this entire loop, including the drift experiment, in Workshop 3."
            },
            {
                "type": "two_col",
                "title": "Provisioning vs Configuration Management",
                "left": [
                    "PROVISIONING - Terraform, OpenTofu, Pulumi, CloudFormation, Bicep",
                    "Creates/destroys infrastructure: networks, VMs, clusters, DNS, containers.",
                    "Declarative model + state file tracking what exists.",
                    "Answers: WHAT infrastructure exists?",
                    "",
                    "Cloud-agnostic workflow; provider plugins per platform.",
                ],
                "right": [
                    "CONFIG MANAGEMENT - Ansible, Chef, Puppet, Salt",
                    "Configures existing machines: packages, files, services, users.",
                    "Idempotent tasks/modules; Ansible is agentless (SSH), no state file.",
                    "Answers: HOW is each machine configured?",
                    "",
                    "Still essential for VMs, bare metal, network devices, appliances.",
                ],
                "notes": "This split answers the outline's 'implementing IaC with configuration management tools' precisely. Provisioning tools make infrastructure exist; configuration management makes existing machines correct. Classic composition: Terraform creates the VM, then Ansible (or cloud-init, or a baked image) configures it. The modern twist: container images have absorbed much of configuration management's old territory - a Dockerfile IS the configuration of the runtime environment, applied at build time instead of continuously - which is why cloud-native shops run less Puppet than 2015 did. But config management remains essential wherever long-lived mutable machines exist: VM fleets, bare metal, network switches, and - as in our bonus lab - workstations. Mention Pulumi as the 'real programming language' alternative to HCL (TypeScript/Python/Go with the same plan/apply model) and OpenTofu as the community fork of Terraform. BASIC DEMO (10 min, theory-demos.md): run the Lab 05 bonus Ansible playbook against the VM's localhost twice - the room watches changed=N become changed=0, which makes idempotence tangible in one minute."
            },
            {
                "type": "content",
                "title": "Terraform's Mental Model in Five Concepts",
                "bullets": [
                    "PROVIDER: plugin that speaks one platform's API (docker, aws, azurerm, kubernetes...).",
                    "RESOURCE: one declared object - a network, a container, a DNS record.",
                    "VARIABLES / OUTPUTS: parameterise modules in; export facts out.",
                    "STATE: the mapping between declarations and reality (remote + locked in teams).",
                    "MODULE: a reusable, versioned package of resources - the platform team's product unit.",
                ],
                "notes": "Five concepts cover 90% of real Terraform reading. Providers are why one workflow spans platforms: our labs use kreuzwerker/docker against the local daemon, and swapping to hashicorp/aws changes the provider block and resource types while plan/apply/state stay identical - THAT is the honest cloud story for this course, and the workshop makes participants prove it to themselves by reading main.tf. Resources declare objects and, crucially, reference each other: our order container's environment references the payment container's name, and from that reference Terraform derives creation ORDER automatically - dependency graphs from data flow, no 'depends_on' choreography needed in most cases. Variables/outputs make configurations reusable across environments (the tfvars file per environment pattern). Modules are the platform-engineering unit: the capstone wraps the whole two-service stack into one module that a consuming team calls with four variables - the module encodes the platform team's decisions once (Module 9's cognitive-load story, realised in HCL). State: covered on the previous slide; in teams it lives remotely (S3+DynamoDB, Terraform Cloud, GitLab) with locking, never in laptops."
            },
            {
                "type": "content",
                "title": "IaC Best Practices (the Production Checklist)",
                "bullets": [
                    "Everything through PRs; plan runs in CI and its diff is part of the review.",
                    "Remote state with locking; never local state for shared infrastructure.",
                    "Commit the lock file; pin provider and module versions deliberately.",
                    "Scan IaC like code: trivy config / checkov / tfsec in the pipeline.",
                    "No secrets in code OR state-visible places; use a secrets manager reference.",
                    "Small, composable modules over one giant configuration; tag everything for cost/ownership.",
                ],
                "notes": "This is the checklist to photograph. PR + plan-in-CI turns infrastructure change management into code review - the reviewer approves an exact diff of reality, which is stronger governance than any change-approval-board meeting, and auditors increasingly agree. Remote state with locking prevents the two-applies-at-once corruption scenario. The lock file gets committed (we practise this) so every machine resolves identical provider builds - the infrastructure equivalent of package-lock.json. IaC scanning catches misconfigurations before they exist: public buckets, missing encryption, permissive security groups, containers without limits - Module 7 wires trivy config into the pipeline and participants see their own Terraform scanned. Secrets: state files can contain resource attributes in plain text, so secrets never go in code AND sensitive values are kept out of state where possible - inject references to a secrets manager (Vault, cloud KMS) instead of values. Small modules: a 5000-line root configuration is unreviewable; compose small modules with narrow interfaces, exactly like functions. Tagging is unglamorous and pays for itself the first time finance asks 'what is this bill?' or an incident asks 'who owns this?'."
            },
            {
                "type": "quote",
                "title": "Module 4 - Key Takeaway",
                "quote": "Infrastructure as Code is not scripts in Git. It is making your infrastructure reviewable, reproducible and disposable - the plan diff is a safety mechanism, and the Git history is your audit trail.",
                "source": "Course synthesis",
                "notes": "Bridge to Module 5: with infrastructure now deliverable-as-code, the pipeline can carry BOTH application and infrastructure through the same review-test-deploy discipline - which is what CI/CD generalises."
            },
        ]
    },

    # ------------------------------------------------------------- Module 5
    {
        "section_title": "Module 5\nContinuous Integration and Continuous Delivery",
        "section_notes": "60 minutes theory; Workshop 1 (late afternoon) builds the real pipeline. Goal: precise definitions (CI vs delivery vs deployment), pipeline anatomy including honest security gates, deployment strategies, and what the platform contributes.",
        "slides": [
            {
                "type": "content",
                "title": "Continuous Integration - Small Batches, Always Green",
                "bullets": [
                    "CI = merge to shared mainline at least daily, verified by automated build + tests.",
                    "The enemy is BATCH SIZE: risk grows super-linearly with change size.",
                    "Long-lived branches = integration debt: conflicts compound, feedback arrives weeks late.",
                    "A red mainline is a stop-the-line event (Toyota andon cord) - fixing it beats all feature work.",
                    "Trunk-based development + feature flags = integrate always, release selectively.",
                ],
                "notes": "CI is a PRACTICE, not a server - a Jenkins box building week-old feature branches is not CI. The core insight is about batch size: a 50-line change can be reviewed rigorously, tested meaningfully, and rolled back trivially; a 5000-line merge can only be skimmed and hoped about, and when it breaks, which of its 40 commits caused it? Risk compounds super-linearly, so many small integrations are structurally safer than one big one - the same lean logic as Module 1. Long-lived branches accumulate integration debt: every day unmerged is a day of conflicts building and a day of feedback not arriving. Trunk-based development is the professional consensus (and DORA-correlated with performance): branches live hours to a couple of days, and incomplete features hide behind flags rather than branches. The andon-cord norm makes CI real: when the mainline goes red, the team's top priority is green again - a team that tolerates a red build for days has CI theatre, not CI. Feature flags get a caveat: they decouple deploy from release (powerful, next slide) but are themselves technical debt with a lifecycle - flags need owners and removal dates, or you accumulate a config space nobody can reason about."
            },
            {
                "type": "content",
                "title": "Delivery vs Deployment - and Deploy vs Release",
                "bullets": [
                    "Continuous DELIVERY: every commit leaves the pipeline deployABLE; a human chooses when.",
                    "Continuous DEPLOYMENT: green pipeline -> production automatically; no human in the loop.",
                    "DEPLOY = bits are running. RELEASE = users can see it. Flags/canaries separate the two.",
                    "Build ONCE, promote the same immutable artifact through every environment.",
                    "If deploys hurt, do them more often - frequency forces the pain to be automated away.",
                ],
                "notes": "Precision here prevents years of confused meetings. Continuous delivery is a state of READINESS: the pipeline proves every commit deployable, and shipping becomes a business decision that can be taken any afternoon - most organisations should target this. Continuous deployment removes the human trigger entirely and is appropriate once test confidence, monitoring and rollback are strong (and change approval regulation permits). The deploy/release distinction is the modern unlock: code can be deployed to production dark (flagged off, or receiving only canary traffic) and released later by flipping a flag - which turns release into a reversible, low-drama act and enables testing in production safely. Build-once-promote is the artifact discipline: the image tested in staging is bit-for-bit the image that reaches production (SHA-tagged, immutable) - rebuilding per environment invites 'works in staging' bugs from dependency drift; our pipeline SHA-tags for exactly this reason. The closing aphorism (Martin Fowler's 'if it hurts, do it more often') is the module's cultural core: pain under frequency is a signal pointing at what to automate next - the organisations deploying daily did not start painless; they started frequent."
            },
            {
                "type": "diagram",
                "title": "Anatomy of the Pipeline",
                "image": "02-cicd-pipeline",
                "caption": "CI proves the change; CD promotes the artifact; every stage can say no.",
                "notes": "Trace one commit through the diagram end to end, because Workshop 1 builds the left half and the capstone adds the right. Commit/PR triggers everything - no manual pipeline starts. Build produces the SHA-tagged image once. Test executes the test pyramid (unit tests in seconds first, then API tests - fast feedback before expensive feedback). The security gate scans the artifact and can genuinely fail the build (next slide is dedicated to this, because most real pipelines get it wrong). Deploy-to-staging exercises the real deployment mechanics; the smoke test proves the deployed thing actually serves (our capstone curls /health and creates an order - a deploy that 'succeeded' but serves 500s is a failure the pipeline must catch). Production sits behind an environment gate - in GitHub Actions, an 'environment' with required approvers gives continuous DELIVERY; removing the approval gives continuous DEPLOYMENT: the difference is one setting, which makes the previous slide's distinction concrete. The feedback arrows matter as much as the forward flow: a red stage stops the line and fixing forward takes minutes because the batch is small; rollback on the right is 'redeploy the previous immutable artifact', not surgery."
            },
            {
                "type": "content",
                "title": "A Scan Is Not a Gate",
                "bullets": [
                    "Report step: results visible, build stays green (exit-code 0) - awareness only.",
                    "Gate step: build FAILS on actionable findings (exit-code 1) - behaviour change.",
                    "Gate on FIXABLE criticals; failing on unfixable CVEs teaches people to ignore red.",
                    "Pin third-party pipeline actions to versions - your pipeline is supply chain too.",
                    "Least-privilege pipeline tokens: 'permissions: contents: read' unless proven otherwise.",
                ],
                "notes": "The most common security-in-CI failure is a scanner wired with exit-code 0 and called a 'gate' in the audit deck - it is a dashboard nobody looks at, and it changes nothing. Teach the two-step pattern participants will build in Workshop 1: a REPORT step (HIGH+CRITICAL, exit-code 0) keeps full visibility for triage, and a GATE step (CRITICAL only, ignore-unfixed, exit-code 1) actually stops the line - but only for findings a developer can act on TODAY, because a gate that fails on unfixable upstream CVEs blocks all delivery indefinitely and gets bypassed within a week, taking the team's respect for red builds with it. Gates must be trustworthy to be tolerated: start narrow (fixable criticals), widen deliberately as the backlog clears. The two supply-chain lines preview Module 7 but belong in every pipeline from day one: a third-party action pinned to @master means an upstream compromise runs instantly with YOUR repository's credentials - pin versions; and default tokens with write access mean any compromised step can push code - declare least-privilege permissions explicitly. Both patterns are already in the workshop's workflow file; point at them when you get there."
            },
            {
                "type": "two_col",
                "title": "Deployment Strategies",
                "left": [
                    "ROLLING (Kubernetes default)",
                    "Replace instances gradually; zero downtime; both versions serve briefly.",
                    "Cheap; needs backwards-compatible changes.",
                    "",
                    "BLUE-GREEN",
                    "Two full environments; switch traffic atomically; rollback = switch back.",
                    "Instant reversal; double infrastructure cost; watch stateful cutover.",
                ],
                "right": [
                    "CANARY",
                    "Route 1-5-25-100% of traffic to the new version, watching metrics between steps.",
                    "Limits blast radius; needs traffic control + good metrics; automatable (progressive delivery).",
                    "",
                    "SHADOW / DARK",
                    "Mirror real traffic to the new version, discard responses.",
                    "Production validation with zero user risk; costs double compute for the path.",
                ],
                "notes": "Deployment strategies are risk-management instruments; choose per service, not per fashion. Rolling is the sensible default and what Kubernetes does out of the box - participants watch a rolling update replace pods one by one in Workshop 2 and roll it back with one command. Its constraint deserves emphasis: during the roll, old and new versions serve simultaneously, so changes must be backwards-compatible - which drives the expand/contract pattern for database migrations (add the new column first, deploy code that handles both, remove the old column later; never break-and-fix in one step). Blue-green buys atomic cutover and instant rollback at the price of doubled infrastructure - attractive for monoliths and regulated cutovers. Canary is the elite pattern: real production traffic in controlled percentages, with promotion gated on metrics (error rate, latency) between steps - tools like Argo Rollouts and Flagger automate the progression, which is called progressive delivery; note the dependency on Module 8's observability - a canary without good metrics is just a slow deploy. Shadow testing validates against real traffic patterns with zero user exposure - powerful for rewrites, expensive to mirror safely (beware side effects: shadowed writes must not hit real systems twice)."
            },
            {
                "type": "content",
                "title": "What the Platform Contributes to CI/CD",
                "bullets": [
                    "Templated/reusable pipelines: teams inherit test-build-scan-deploy, not copy-paste YAML.",
                    "Secrets management: pipeline credentials injected by the platform, never in repos.",
                    "Runners, registries, environments: operated once, consumed as a service.",
                    "Policy hooks: the golden-path pipeline enforces org rules invisibly (Module 7).",
                    "Result: a new service reaches production on day one via the paved road.",
                ],
                "notes": "This slide connects Module 5 to the course's platform thread. Without a platform, every team hand-rolls pipelines: quality varies wildly, security steps are omitted under deadline pressure, and pipeline maintenance becomes distributed toil across every team. The platform play is centralise-and-serve: reusable workflows (GitHub Actions' workflow_call, GitLab includes, shared Jenkins libraries) let a team's entire CI file be ten lines that inherit the golden path - and when the platform team improves the scan step, every consuming team gets it on the next run without a single ticket. Secrets follow the same logic: the platform wires OIDC or a secrets manager into the pipeline so credentials never appear in repositories or logs. 'Reaches production on day one' is the platform's headline metric (time-to-first-deploy) and Module 9 will treat it as a product KPI. Real-world patterns worth naming for the room: Netflix's Spinnaker, Shopify's deployment platform, and the State of DevOps reports' consistent finding that elite performers standardise their delivery tooling - the capstone's golden path is a miniature of exactly this."
            },
            {
                "type": "quote",
                "title": "Module 5 - Key Takeaway",
                "quote": "The pipeline is the only path to production - and that is a feature. Everything it checks is checked every time; everything it deploys can be rolled back; everything it does is written down.",
                "source": "Course synthesis",
                "notes": "Set up Workshop 1 (next block): participants build the test-build-scan pipeline for the order service and trigger it from a pull request - the left half of today's diagram, for real. Day 2 then containerises deeper (Module 6) and extends the pipeline's reach to Kubernetes."
            },
        ]
    },
]

# ===========================================================================
# DAY 2
# ===========================================================================
DAY2_MODULES = [

    # ------------------------------------------------------------- Module 6
    {
        "section_title": "Module 6\nMicroservices and Containerization",
        "section_notes": "75 minutes theory; Workshop 2 (mid-morning) is the big hands-on: build, compose and deploy the microservice to Kubernetes. Theory goal: when microservices are worth their cost, what containers actually are, and the Kubernetes mental model.",
        "slides": [
            {
                "type": "diagram",
                "title": "Monolith vs Microservices - the Real Trade-off",
                "image": "05-monolith-vs-microservices",
                "caption": "The unit of deployment changes everything - in both directions.",
                "notes": "Frame this as a genuine trade-off, not an upgrade path. A monolith is ONE deployable: simple to run, debug and test locally; transactions are easy; refactoring across the whole domain is an IDE operation. Its costs arrive with scale - of teams more than of traffic: every change redeploys everything, teams queue on one release train, one memory leak takes down all functionality, and technology choices are global. Microservices invert the trade: independent deploy/scale/fail per service and per team - but every arrow in the right-hand picture is a network call that can fail, be slow, or arrive out of order; transactions become sagas; debugging becomes distributed tracing; and 'run it locally' becomes a platform feature. Quote Martin Fowler's 'monolith first' honestly: most successful microservice systems were extracted from monoliths whose seams had become visible; starting greenfield with twenty services means guessing twenty boundaries you will guess wrong. And connect back to Conway (Module 2): the RIGHT reason to split is team autonomy along business domains - if one team owns everything, microservices give you distributed-systems pain with no autonomy payoff. Our two-service app is deliberately minimal: one seam (order calls payment), enough to exhibit every distributed-systems lesson without drowning in them."
            },
            {
                "type": "content",
                "title": "Microservice Design Principles",
                "bullets": [
                    "Boundaries follow BUSINESS domains (bounded contexts), not technical layers.",
                    "Independent deployability is the acid test - if two services always ship together, they are one.",
                    "Database per service: no shared tables; integration through APIs and events only.",
                    "Smart endpoints, dumb pipes: logic in services, not in a clever bus.",
                    "Design for partial failure: timeouts, retries with backoff, circuit breakers, graceful degradation.",
                ],
                "notes": "Bounded context comes from Domain-Driven Design (Eric Evans): a boundary within which a model and its language are consistent - 'order' means one precise thing inside the ordering context. Services cut along these seams change for one business reason at a time; services cut along technical layers (a 'database service', an 'API layer service') change with every feature and force lockstep deploys. Independent deployability is the honest test of any decomposition: if releasing service A always requires releasing B, you have a distributed monolith - all of the network pain, none of the autonomy. Database-per-service is what makes independence real: shared tables are the tightest possible coupling (any schema change breaks unknown others); integration happens through published APIs or events, and yes, that means accepting eventual consistency at boundaries - a price, paid consciously. 'Smart endpoints, dumb pipes' (Fowler/Lewis) encodes the ESB lesson: burying business logic in a clever middleware recreated the monolith in the worst place; keep transport simple (HTTP, plain queues) and logic in owned services. Partial failure is the defining reality: our order service demonstrates the pattern minimally - a 2-second timeout on the payment call, and a degraded-but-alive answer (payment status 'unavailable') when the dependency is down. Participants SEE this behaviour in Workshop 2 and break it on purpose in the Module 8 demo."
            },
            {
                "type": "content",
                "title": "Twelve-Factor Apps - the Portability Contract",
                "bullets": [
                    "Config in the ENVIRONMENT, never in the artifact - one image runs everywhere.",
                    "Stateless processes: state lives in backing services, so replicas are interchangeable.",
                    "Logs to stdout as event streams - the platform aggregates, the app does not manage files.",
                    "Fast startup, graceful shutdown - disposability is what makes orchestration possible.",
                    "Dev/prod parity: the same artifact and shape from laptop to production.",
                ],
                "notes": "The Twelve-Factor App (Heroku, 2011) remains the practical contract between applications and platforms - highlight the five factors that carry the most weight and show where OUR app honours each. Config in environment: the same order-service image reports env 'production' under docker run, 'compose' in the Compose stack, and 'kubernetes' under kind, because APP_ENV and PAYMENT_SERVICE_URL are injected at runtime - the artifact never changes, only its environment does; participants verify this repeatedly via /health. Stateless processes: our in-memory order list is a DELIBERATE violation - in Workshop 2, scaling the payment service to two replicas visibly splits state between them, which is the most convincing statelessness lesson available: real state belongs in a backing service (database, cache), so any replica can serve any request and scaling/rescheduling is free. Logs to stdout: docker logs and kubectl logs work because the app writes to stdout and manages no log files - the platform owns aggregation. Disposability: fast boot and clean SIGTERM handling are what let orchestrators do rolling updates and self-healing - a service that takes three minutes to boot or corrupts on kill fights its platform. Dev/prod parity is the summary factor: identical images, same ports, same probes, laptop to production."
            },
            {
                "type": "content",
                "title": "What a Container Actually Is",
                "bullets": [
                    "NOT a VM: no guest OS - processes on the host kernel, isolated by namespaces + cgroups.",
                    "Namespaces = what you can SEE (processes, network, filesystem); cgroups = what you can USE.",
                    "An image is a stack of immutable layers + metadata (OCI standard); a container is a running instance.",
                    "Layers are content-addressed and shared - 50 services on one base image store it once.",
                    "Registries distribute images by digest: the SHA is the identity, tags are mutable pointers.",
                ],
                "notes": "Demystify the technology - containers stop being magic in about three minutes. A VM virtualises hardware and boots a full guest OS (minutes, gigabytes); a container is ordinary Linux processes wearing isolation: NAMESPACES restrict what the process can see (its own PID tree, network stack, filesystem mounts, users) and CGROUPS meter what it can consume (CPU, memory - the numbers our Kubernetes limits set in Workshop 2). That is why containers start in milliseconds and share the host kernel - and why container security differs from VM security (Module 7: a kernel exploit escapes ALL containers on the host, hence non-root and seccomp defaults). Images: an immutable, content-addressed stack of filesystem layers plus metadata (entrypoint, env, ports), standardised by the OCI so any runtime runs any image. Layer sharing is the economic magic: every image FROM python:3.12-slim shares those base layers on disk and over the network - which is also why layer ORDER matters in Dockerfiles (dependencies before source code = cache hits on every code-only rebuild; participants see this in Workshop 2 when the second build takes seconds). Tags vs digests: a tag like :lab02 is a mutable pointer, the sha256 digest is the true identity - which is why production systems pin digests and why our no-latest-tag policy exists (Module 7)."
            },
            {
                "type": "content",
                "title": "Building Good Images",
                "bullets": [
                    "Multi-stage builds: compile/install in a builder stage, ship only the runtime slice.",
                    "Run as non-root; smallest sensible base (slim/distroless); pin base versions.",
                    "Order layers for cache: dependency manifest first, source code last.",
                    "HEALTHCHECK + graceful shutdown make the image orchestrator-friendly.",
                    ".dockerignore: the build context is not your whole repository.",
                ],
                "notes": "Every line here is implemented in the course's two Dockerfiles - open Dockerfile in labs/app on screen and point as you talk. Multi-stage: the builder stage pip-installs with full tooling; the final stage copies only the installed packages - smaller images pull faster, cold-start faster, and expose fewer packages to CVE scanners (participants compare Trivy findings against slim bases in the Module 7 demo). Non-root: our images create appuser (UID 1001) and USER-switch before CMD, so a container escape lands unprivileged - participants verify with whoami in Workshop 2, and Kubernetes enforces it again via runAsNonRoot (defence in depth). Base choice: slim over full (fewer packages, fewer CVEs), distroless as the next step (no shell - harder to debug, harder to exploit), alpine with the musl caveat for Python wheels. Cache ordering is the daily-life win: COPY requirements.txt + install BEFORE COPY source means editing code never re-installs dependencies. HEALTHCHECK lets Compose gate startup ordering (our depends_on: service_healthy) and mirrors the probes Kubernetes will run. The .dockerignore keeps venvs, .git and caches out of the build context - build speed and no accidental secrets in layers."
            },
            {
                "type": "content",
                "title": "Why Orchestration - What Kubernetes Actually Does",
                "bullets": [
                    "One host + docker run does not: reschedule on failure, scale, roll out, load-balance, heal.",
                    "Kubernetes = a RECONCILIATION engine: you declare desired state, controllers converge reality.",
                    "Scheduling: pods placed by resource requests, spread and affinity across nodes.",
                    "Self-healing: failed pods replaced, failed probes remove pods from traffic - automatically.",
                    "The same declarative + converge model as Terraform, applied continuously at runtime.",
                ],
                "notes": "Motivate orchestration from the gap participants have personally felt by now: Compose runs a stack on one machine, but who restarts the container at 03:00, moves it when the node dies, adds replicas under load, or shifts traffic during an update? Kubernetes' core idea - the one that makes everything else make sense - is RECONCILIATION: you write desired state (a Deployment saying 'two replicas of this image'), and controllers run an endless loop of observe-diff-act until reality matches, forever. Delete a pod and it reappears; not because something restarted it as a special case, but because the controller noticed reality (1 pod) diverged from desire (2). Connect this explicitly to Module 4: it is Terraform's declare-and-converge model, running continuously at runtime instead of on demand - one mental model, two timescales. Scheduling uses the resource REQUESTS on each container (our manifests set them) to bin-pack pods across nodes; LIMITS cap consumption via cgroups from two slides ago. Self-healing goes beyond restarts: a failing READINESS probe removes a pod from Service load-balancing without killing it; a failing LIVENESS probe restarts it - participants configure both in Workshop 2 and watch them act during the rolling update."
            },
            {
                "type": "diagram",
                "title": "Kubernetes Architecture",
                "image": "04-kubernetes-architecture",
                "caption": "Control plane decides; workers run; everything talks to the API server.",
                "notes": "Keep the tour tight and functional - the exam-level detail is less important than the shape. Control plane: the API SERVER is the single front door (kubectl, controllers, kubelets all speak to it - which is why RBAC on the API server is THE security boundary, Module 7); ETCD stores the entire cluster state (desired and observed - lose etcd without backup, lose the cluster's memory); the SCHEDULER assigns new pods to nodes; the CONTROLLER MANAGER runs the reconciliation loops from the previous slide. Workers: the KUBELET on each node makes assigned pods actually run and reports status back; KUBE-PROXY programs the routing that makes Services work. Emphasise the communication pattern: desired state flows down, observed status flows back up, and NOTHING talks directly to anything except through the API server - that uniformity is what makes Kubernetes extensible (operators, admission controllers) and auditable. Then the kind reveal: in Workshop 2, this entire picture runs inside one Docker container on the participant's VM - same API, same components, same kubectl; which is the course's fidelity claim: everything they practise transfers verbatim to EKS/AKS/GKE, where the control plane is simply someone else's problem (managed)."
            },
            {
                "type": "content",
                "title": "The Working Vocabulary: Objects You Will Touch",
                "bullets": [
                    "Pod: smallest unit - one or more containers sharing network/storage; mortal by design.",
                    "Deployment: desired replicas + template; owns rolling updates and rollback history.",
                    "Service: stable name + virtual IP load-balancing over pods selected by LABELS.",
                    "ConfigMap / Secret: configuration injected at runtime (12-factor, realised).",
                    "Probes + requests/limits: how the platform knows a pod is well and what it may consume.",
                ],
                "notes": "Five objects cover Workshop 2 completely. Pods are mortal - never hand-create them; they die and are replaced, and their IPs change, which is WHY Services exist. Deployments are what you actually write: replicas + pod template; kubectl set image triggers a rolling update (new ReplicaSet scaled up as old scales down, gated by readiness probes), and kubectl rollout undo is the one-command rollback - participants run both and watch build_id change and change back via /health. Services solve discovery: a stable DNS name (payment-service) and virtual IP, load-balancing across whatever pods currently match the label selector - the Compose DNS idea, made dynamic; label selectors are the glue, and a selector/label mismatch is the classic 'why is my service empty' bug (it is in the workshop's troubleshooting table). ConfigMaps/Secrets inject environment per-cluster while the image stays identical - our app-config supplies APP_ENV=kubernetes, and /health proves it. Probes: readiness gates traffic, liveness triggers restart - configure them differently or a slow startup becomes a restart loop. Requests/limits: requests inform scheduling, limits enforce via cgroups; both are set in our manifests and both are what Module 7's config scanner checks for."
            },
            {
                "type": "content",
                "title": "Managing Services at Scale",
                "bullets": [
                    "Autoscaling: HPA scales pods on metrics; cluster autoscaler scales nodes; VPA right-sizes.",
                    "Service mesh (Istio, Linkerd): mTLS, retries, traffic-splitting as platform features - at a cost.",
                    "GitOps deployment (Argo CD/Flux): the cluster converges on a Git repo; drift auto-corrects.",
                    "Multi-cluster/multi-region: blast-radius isolation before exotic scaling.",
                    "Scale problems are PLATFORM problems - product teams should inherit the answers.",
                ],
                "notes": "Close the module by sketching the horizon honestly - name what exists, what it costs, and who should own it. Horizontal Pod Autoscaler scales replicas on CPU or custom metrics (a direct payoff of Module 8's metrics work); the cluster autoscaler adds nodes when pods cannot schedule; note the interplay - HPA without cluster autoscaling hits a ceiling. Service meshes inject a proxy sidecar next to every pod and centralise mTLS between services, retries/timeouts, and percentage traffic-splitting (the canary mechanics from Module 5) - real capabilities with real operational cost; the honest guidance is to adopt a mesh when you need at least two of its features, not because a diagram looked good. GitOps (from Module 3) matures deployment at scale: clusters converge on declarative repos, so 'what is running in production' has a Git answer and manual drift self-corrects. Multi-cluster is usually about blast radius and data residency before raw scale. The last bullet is the module's platform thread: none of these decisions should be made twenty times by twenty teams - the platform decides once, encodes it in the golden path, and product teams inherit scale-readiness. Workshop 2 is next: build the image, compose the stack, deploy to kind, scale it, roll it, roll it back."
            },
        ]
    },

    # ------------------------------------------------------------- Module 7
    {
        "section_title": "Module 7\nSecurity and Compliance (DevSecOps)",
        "section_notes": "45 minutes theory + a 10-minute basic demo (Trivy scan + one Conftest policy). Goal: shift-left economics, the scanner taxonomy, supply-chain awareness, policy as code, and triage discipline - security as a platform default, not a checkpoint.",
        "slides": [
            {
                "type": "diagram",
                "title": "Shift Left - the Economics of Early",
                "image": "07-devsecops-shift-left",
                "caption": "The later a flaw is found, the more it costs - and the bigger its blast radius.",
                "notes": "DevSecOps in one curve: a vulnerable dependency caught at commit time is a one-line bump chosen calmly; the same flaw found in production is an incident - emergency patching across a fleet, forensics on whether it was exploited, possibly disclosure. The traditional model (a security review before release) failed for a structural reason participants now understand from Module 5: it put a slow, manual, low-context checkpoint at the END of a fast pipeline - so security became the department of 'no', teams routed around it, and reviews happened too late to change designs anyway. Shift-left redistributes security along the whole lifecycle as fast, automated feedback: threat modelling at design ('what can go wrong here?' asked in planning - even 15 informal minutes pays), secret and dependency scanning at commit, image and IaC scanning at build, policy checks at deploy, and hardened defaults at runtime. Note what shift-left does NOT mean: it does not abolish security specialists - it changes their job from gatekeeping every release to building guardrails and platform defaults (curating rules, tuning gates, handling escalations), which scales in a way manual review never can. Every stage on this diagram maps to something concrete participants touch today."
            },
            {
                "type": "content",
                "title": "The Scanner Taxonomy - What Checks What, When",
                "bullets": [
                    "SAST: reads your source for flaw patterns (injection, crypto misuse) - at PR time.",
                    "SCA: inventories dependencies against CVE databases - most real-world risk lives here.",
                    "Secret scanning: credentials in code/history - at commit AND continuously.",
                    "Container/image scanning: OS + language packages in the artifact (Trivy) - at build.",
                    "IaC/config scanning: misconfigurations in Terraform/K8s (trivy config) - at PR.",
                    "DAST: probes the RUNNING app from outside - staging, scheduled.",
                ],
                "notes": "Give participants the map so vendor noise cannot confuse them: each scanner class answers a different question at a different pipeline stage, and a mature setup layers several - they overlap little. SAST parses your first-party code for dangerous patterns; its curse is false-positive volume, so tune rulesets or teams learn to ignore it. SCA (software composition analysis) is where modern risk concentrates, because a typical service is overwhelmingly third-party code by volume - Log4Shell was an SCA problem, present in thousands of codebases that had written no vulnerable line themselves. Secret scanning runs twice: as a pre-commit/PR check (cheap prevention) and continuously over history, because a secret once pushed lives in Git history forever - the remediation is ROTATION, never just deletion; our demo plants a fake AWS key and watches Trivy catch it. Image scanning inspects the built artifact - base-image OS packages plus language dependencies - which is why slim bases (Module 6) directly shrink findings. IaC scanning catches the cloud-breach classics (public buckets, missing encryption, permissive roles, no resource limits) before anything exists; participants scan the course's own Terraform and manifests. DAST probes the running application from outside, catching what only manifests at runtime (auth flows, headers, injections through the real stack) - slower, so staging on a schedule rather than every commit."
            },
            {
                "type": "content",
                "title": "Supply Chain Security - Your Pipeline Is a Target",
                "bullets": [
                    "SolarWinds: the BUILD SYSTEM was compromised - customers shipped the attacker's code.",
                    "Attack surface: dependencies, base images, CI actions, registries, build infrastructure.",
                    "SBOM: a machine-readable inventory of everything inside your artifact (Trivy can emit one).",
                    "Countermeasures: pin versions AND digests, sign artifacts (cosign), least-privilege tokens.",
                    "SLSA: a maturity ladder for build integrity - know which level you need.",
                ],
                "notes": "Supply chain attacks target the factory rather than the product, and they scale terrifyingly: compromise one build system or one popular package and you compromise every downstream consumer at once. SolarWinds (2020) is the canonical case - attackers modified the vendor's build process so signed, official updates carried the implant to ~18,000 organisations. The dependency-level versions arrive constantly: typosquatted packages, maintainer-account takeovers, malicious updates to abandoned libraries. Walk the attack surface as a checklist of what participants' own pipelines contain: third-party dependencies (SCA scanning), base images (pin them; prefer minimal), CI actions (our @master-vs-pinned-version lesson from Module 5 - an upstream compromise of an unpinned action runs with your repo's token immediately), registries (who can push to the image your cluster pulls?), and the build system itself. SBOMs (SPDX/CycloneDX formats) answer the Log4Shell-day question - 'which of our 400 services contains this library?' - in minutes instead of weeks, and are increasingly demanded contractually and by regulation (US EO 14028, EU CRA). Signing (Sigstore/cosign) plus admission-time verification closes the loop: only artifacts provably built by YOUR pipeline run in production. SLSA gives the maturity vocabulary; most organisations should first reach 'builds are scripted, provenance exists, tokens are least-privilege' before chasing higher levels."
            },
            {
                "type": "content",
                "title": "Compliance as Code (OPA, Rego, Conftest)",
                "bullets": [
                    "Wiki rules are wishes; encoded policies are guarantees - evaluated on every change.",
                    "OPA/Rego: a general policy engine - one language for K8s, Terraform, pipelines, APIs.",
                    "Conftest in CI tests rendered configs; admission controllers enforce at the cluster door.",
                    "Test what SHIPS: rendered output, not raw files (labels added at render time!).",
                    "Audit evidence becomes: the policy file + Git history + pipeline logs. Auditors love it.",
                ],
                "notes": "Compliance as code closes the gap between what the standards document says and what production does. The traditional cycle - write a standard, hope, audit annually, discover drift, remediate in a panic - fails because enforcement is manual and sampling is sparse. Encoding the rule makes enforcement continuous and total: every deployment must carry an owner label, no container may run as root, no image may use :latest - each becomes a policy evaluated automatically on every single change, and the standards document stops being fiction. OPA (Open Policy Agent, a CNCF-graduated engine) with its Rego language is the common denominator: the same policy skills apply to Kubernetes manifests, Terraform plans, CI pipelines and even application authorisation. Enforcement lives at two doors: Conftest in the pipeline (shift-left - developers get policy feedback at PR time, cheap to fix) and admission controllers in the cluster (Gatekeeper/Kyverno - nothing enters the API server unchecked, catching whatever bypassed CI). The render-time subtlety is today's demo punchline: our raw manifests FAIL the required-label policy while the Kustomize-rendered output PASSES, because labels are stamped at render time - so policies must test what actually ships. The audit story lands especially well with anyone who has suffered an audit: evidence stops being screenshots and interviews and becomes the policy file, its Git history, and pipeline logs showing every evaluation."
            },
            {
                "type": "content",
                "title": "Runtime Hardening - Platform Defaults, Not Team Chores",
                "bullets": [
                    "Containers: non-root user, read-only root filesystem, drop ALL capabilities, seccomp.",
                    "Cluster: RBAC least-privilege, NetworkPolicies (default-deny), no wildcard admin bindings.",
                    "Secrets: a manager (Vault/KMS/external-secrets), rotation, never env-dumped or committed.",
                    "Least privilege EVERYWHERE: pipeline tokens, service accounts, registry access.",
                    "The golden path ships hardened - teams inherit security instead of re-deriving it.",
                ],
                "notes": "Runtime hardening is defence in depth for the day the earlier layers miss something. Container level - and every item here is LIVE in the course manifests, so open deployment-order.yaml and point: runAsNonRoot (an escaped attacker lands unprivileged), readOnlyRootFilesystem (nothing can be written or planted - our own app runs happily under it, proving well-built services tolerate hardening), capabilities drop ALL (Linux root is a bundle of distinct powers; drop everything not needed), seccompProfile RuntimeDefault (filters the kernel syscall surface - the shared-kernel risk from Module 6, mitigated). Cluster level: RBAC on the API server is the security boundary that matters most - least-privilege service accounts, no default-namespace sprawl, and audit any cluster-admin binding; NetworkPolicies turn the flat pod network into default-deny with explicit allowed flows (our order->payment call would be an explicit rule). Secrets deserve their own breath: base64 in a manifest is encoding, not encryption - real setups use a manager with rotation, injected via CSI or external-secrets operators. The final bullet is the module's thesis and the platform thread again: none of this should be twenty teams' homework - the golden path's templates ship hardened, so the secure configuration is the DEFAULT configuration, and teams opt out with justification rather than opting in with expertise. BASIC DEMO (10 min, theory-demos.md): trivy image on the course's own image, then the raw-vs-rendered Conftest comparison."
            },
            {
                "type": "content",
                "title": "Triage Discipline - Living With Scanner Output",
                "bullets": [
                    "Severity (CVSS) is not risk: context - exposure, reachability, data - changes everything.",
                    "First questions: is it FIXABLE? is the vulnerable path even reachable in our usage?",
                    "--ignore-unfixed in gates: block only what a developer can action today.",
                    "Accepted risks get an owner and an EXPIRY date - never a permanent ignore file.",
                    "Track vulnerability debt like tech debt; watch the trend, not just today's count.",
                ],
                "notes": "The first real scan of any mature image returns dozens of findings, and the untrained reactions - panic, or numb dismissal - are equally wrong; triage is the professional skill, and it is teachable in one slide. CVSS scores measure theoretical severity in a vacuum; RISK is severity multiplied by context: a critical RCE in an internal batch tool behind a VPN is a different animal from a medium-severity flaw in your internet-facing auth service. The triage tree: Is a fixed version released? - upgrade, usually a one-line change caught at ideal cost (the shift-left curve). No fix yet? - assess reachability: is the vulnerable function even invoked in your usage? Vendor advisories and reachability analysis help; often the honest answer is 'not exploitable in our configuration', which is an ACCEPTANCE decision - and acceptances get an owner and an expiry date, because 'ignore forever' files rot into blindness. This is exactly why the Workshop 1 gate uses --ignore-unfixed on criticals: a gate must only block what someone can action today, or it gets bypassed and takes the team's respect for red builds with it (Module 5's lesson, applied). Finally, zoom out: individual findings matter less than the TREND of vulnerability debt - a platform that auto-bumps base images weekly beats any amount of heroic patching."
            },
            {
                "type": "quote",
                "title": "Module 7 - Key Takeaway",
                "quote": "Make the secure path the easy path. Scanners inform, gates enforce, policies encode the rules, and the platform ships it all as the default - so security happens even on a deadline.",
                "source": "Course synthesis",
                "notes": "Bridge to Module 8: hardening reduces the odds of failure; observability is how you find out anyway - because something always gets through."
            },
        ]
    },

    # ------------------------------------------------------------- Module 8
    {
        "section_title": "Module 8\nObservability and Reliability",
        "section_notes": "45 minutes theory + a 15-minute basic demo (Prometheus + Grafana on localhost, then a mini incident). Goal: pillars with real depth, SLI/SLO/error budgets, alerting that respects humans, and reliability patterns - measurement in service of learning.",
        "slides": [
            {
                "type": "content",
                "title": "Monitoring Asks Known Questions; Observability Answers New Ones",
                "bullets": [
                    "Monitoring: predefined checks for failures you ANTICIPATED (disk full, service down).",
                    "Observability: can you interrogate the system about failures you NEVER predicted?",
                    "Distributed systems fail in emergent ways - the interesting outage is always novel.",
                    "Property of the system: rich telemetry with labels/context you can slice ad hoc.",
                    "Test: 'orders from one customer segment are slow - why?' answerable without a new deploy?",
                ],
                "notes": "The distinction is practical, not pedantic. Monitoring is a set of questions you wrote down in advance - is the disk full, is the process up, is latency under 500ms - and it is necessary but bounded by your imagination at dashboard-design time. In a distributed system (Module 6's world), the failures that hurt are EMERGENT: a retry storm amplifying a slow dependency, one customer's pathological request pattern, a cache stampede after a deploy - none of which had a pre-built dashboard. Observability (the term borrowed from control theory: inferring internal state from outputs) is the property of emitting telemetry rich enough to answer questions you formulate DURING the incident: metrics with meaningful labels (endpoint, status, customer-tier), structured logs with correlation IDs, traces stitching a request across services. The litmus test on the slide is worth reading aloud twice - if answering a novel question requires adding instrumentation and redeploying, you have monitoring; if you can slice existing telemetry ad hoc, you have observability. High-cardinality labels are what make slicing possible, and also what makes naive metric systems explode - a real design tension to name honestly (metrics for aggregates, logs/traces for high-cardinality detail)."
            },
            {
                "type": "diagram",
                "title": "The Three Pillars in Depth",
                "image": "06-observability-pillars",
                "caption": "Metrics: how much/how fast. Logs: what exactly. Traces: where in the chain.",
                "notes": "Give each pillar its engineering personality, because they are complements, not alternatives. METRICS are cheap aggregates over time - counters and histograms whose cost is independent of traffic volume - perfect for dashboards, alerts and SLOs; our app's middleware counts every request into order_requests_total with method/endpoint/status labels and times it into a histogram; two method points worth teaching: RED (Rate, Errors, Duration) is the request-service checklist, USE (Utilisation, Saturation, Errors) the resource-level one - and averages LIE, which is why histograms exist: mean latency of 50ms is compatible with a p99 of 4 seconds, and your unluckiest users live in the tail, so we quantile from histogram buckets (participants build the p95 panel in the demo). LOGS are discrete events with unbounded detail - the place for stack traces and request context; structure them (JSON) and carry correlation IDs so one request's story is greppable across services; they answer 'what exactly happened at 14:32'. TRACES follow ONE request across service boundaries - spans with timing per hop - answering 'WHERE in the chain did the time or error come from'; OpenTelemetry is the vendor-neutral standard worth naming (one instrumentation, any backend). Workflow in practice: a metric alert says SOMETHING is wrong, traces localise WHERE, logs explain WHY - the demo walks exactly this path."
            },
            {
                "type": "content",
                "title": "SLI, SLO, SLA - and the Error Budget",
                "bullets": [
                    "SLI: a measured indicator of user experience (success rate, p95 latency).",
                    "SLO: your internal target for it (99% of /orders requests succeed, 30-day window).",
                    "SLA: the external CONTRACT with penalties - always looser than the SLO.",
                    "Error budget: 100% minus SLO = permitted failure. 99% over 30 days = ~7.2 hours.",
                    "Budget healthy: ship fast. Budget spent: reliability work wins - by prior agreement.",
                    "100% is the wrong target: each nine multiplies cost, and users cannot tell past a point.",
                ],
                "notes": "This is SRE's crown jewel: it converts 'how reliable should we be?' from an emotional argument into an engineering budget. SLIs must measure USER experience, not machinery - 'successful responses to real requests' beats 'CPU below 80%' (users do not experience your CPU); choose 2-3 per service, typically availability and latency. Two subtleties participants hit in the course material: exclude health-check traffic from the SLI (it is high-volume and almost always succeeds, so it dilutes real user pain - our slo.md does this deliberately and says why), and measure at the point closest to the user you can. SLOs are internal targets with explicit windows; SLAs are contracts with lawyers and penalties, set LOOSER than the SLO so you breach internally before you breach contractually. The error budget reframes everything: a 99% monthly SLO GRANTS ~7.2 hours of failure - reliability stops being 'as much as possible' and becomes a resource to SPEND on velocity (deploys, experiments, migrations). The policy must be agreed BEFORE it is needed: budget healthy means ship; budget exhausted means feature work yields to reliability work - agreed in calm, enforced without a fight in crisis. The last bullet defuses the 100% instinct: each extra nine multiplies cost (redundancy, complexity, on-call) while user-perceived value flattens - your mobile user's network is less reliable than your 99.9% anyway. Ask the room what THEIR services' unwritten SLO currently is; the silence is the lesson."
            },
            {
                "type": "content",
                "title": "Alerting That Respects Humans",
                "bullets": [
                    "Page on SYMPTOMS (users hurting), ticket on causes (disk trending full).",
                    "Alert on error-budget BURN RATE, not raw thresholds - two windows: fast and slow.",
                    "Every page must be: actionable, urgent, and novel. Otherwise it is noise.",
                    "Alert fatigue is a safety failure: ignored pages are how big outages get missed.",
                    "Every alert links a runbook; every false page gets tuned or deleted - budget your alerts too.",
                ],
                "notes": "Alerting is where observability meets human factors, and most organisations get it wrong in the direction of MORE. The symptom/cause split: page a human when users are hurting (error rate up, latency exploding) because that always deserves urgency; causes that are not yet symptoms (a disk filling over days, a certificate expiring next week) become tickets - urgent-but-async work. Naive threshold alerts ('availability below 95% for 5 minutes') fail in both directions: too slow for a total outage, too twitchy for a brief blip that self-heals. Burn-RATE alerting fixes this by asking 'how fast is the error budget being consumed?': a fast-burn rule (e.g. burning at 14x budget rate over 1 hour AND 5 minutes - the two windows suppress flapping) pages because the monthly budget dies in days; a slow-burn rule (3x over 24 hours) tickets because there is time to think. Our slo.md contains these exact rules with the arithmetic worked out - point participants at it. The 'actionable, urgent, novel' test kills most existing alerts on contact, and that is the point: alert fatigue is not an annoyance but a SAFETY failure - the on-call who silences their tenth false page tonight is the one who sleeps through the real one; Module 2's psychological safety applies to machines paging humans, too. Runbook links and a standing rule that every false page produces a tuning change keep the alert set trustworthy over time."
            },
            {
                "type": "content",
                "title": "Designing for Failure - Reliability Patterns",
                "bullets": [
                    "Assume dependencies WILL fail; the design question is what happens then.",
                    "Timeouts everywhere (no infinite waits) + retries with backoff AND jitter - budgeted.",
                    "Circuit breakers: stop hammering a sick dependency; probe for recovery.",
                    "Graceful degradation: reduced service beats no service (our 'payment unavailable').",
                    "Redundancy + fast rollback: recovery speed often beats failure prevention.",
                ],
                "notes": "Reliability is designed, not hoped for - and every pattern here is visible in the course's tiny app, which is the teaching trick: point at labs/app/main.py on screen. Timeouts: our payment call carries timeout=2.0 - without it, a hung dependency consumes order-service threads until IT dies too, which is how failures cascade upward. Retries help with transient blips but are dangerous at scale: a thousand clients retrying immediately is a self-inflicted DDoS on a recovering service - hence exponential backoff with JITTER (randomisation so retries do not synchronise into waves), and retry budgets to cap amplification. Circuit breakers formalise 'stop asking': after N failures the breaker opens and calls fail fast without touching the sick dependency, then a half-open probe tests recovery - protecting both caller (no wasted waits) and callee (breathing room). Graceful degradation is the design PHILOSOPHY the mechanisms serve: decide per feature what reduced service looks like - our order service accepts the order with payment status 'unavailable' rather than erroring, a product decision (accept-and-reconcile vs reject) that engineering alone cannot make; participants watched this behaviour in Lab 00 without the payment service and will trigger it deliberately in the incident demo. The last bullet reframes the goal with DORA's stability metrics: since failure is inevitable, RECOVERY TIME is often the better investment than ever-more prevention - which is why rollback practice (Workshop 2) matters as much as tests."
            },
            {
                "type": "diagram",
                "title": "The Incident Lifecycle - and Practising It",
                "image": "10-incident-lifecycle",
                "caption": "Detect, triage, mitigate, resolve - then the learning half: postmortem, remediate.",
                "notes": "Walk the ring with emphasis on the two clocks and the learning half. MTTD (detection) is bought with Module 8's alerting - the gap between 'users hurting' and 'we know' should be minutes, not a customer email later. Triage assigns severity and a clear incident-commander role (someone coordinates, others investigate - structure beats heroics). MITIGATE before you understand: stop the bleeding with rollback, failover or a flag flip - root cause can wait; this ordering feels wrong to engineers who want to understand first, and is right anyway. Resolve fixes the cause properly. Then the half most organisations skip: the blameless POSTMORTEM (Module 2's practice, now in context) and REMEDIATE - action items shipped as real backlog work, closing the loop back to 'detect' with better alerts, runbooks and guards. This is the Third Way from Module 1: incidents as the system teaching you about itself. BASIC DEMO NOW (15 min, theory-demos.md): bring up the observability stack on localhost, generate traffic, see the dashboard - then the instructor quietly stops the payment container; the room notices via payment status flipping to 'unavailable' and the Prometheus target going down, localises it, restarts it, watches recovery, and writes a 5-line postmortem together. One full lifecycle lap, at lab scale, on localhost. Game days (rehearsed versions of exactly this) are the habit to take home."
            },
        ]
    },

    # ------------------------------------------------------------- Module 9
    {
        "section_title": "Module 9\nPlatform as a Product",
        "section_notes": "45 minutes theory + the platform canvas exercise (25 min, instructor/platform-canvas.md). This module converts the whole course's platform thread into product discipline: users, golden paths, metrics, ROI - and what to deliberately NOT build.",
        "slides": [
            {
                "type": "diagram",
                "title": "The Internal Developer Platform",
                "image": "08-platform-as-product",
                "caption": "A paved road developers CHOOSE - because it is genuinely the best way to ship.",
                "notes": "Anchor the module: an Internal Developer Platform is the productised sum of everything this course covered - templates, pipelines, runtime, IaC modules, security gates, observability - behind a self-service interface, so stream-aligned teams consume capabilities instead of building them. The product framing is the load-bearing idea: a platform has USERS (your developers), COMPETITORS (do-it-yourself, shadow IT, that one team that loves its own Jenkins), and it lives or dies by voluntary ADOPTION. The moment a platform must be mandated, it has failed as a product - mandates breed resentful compliance and workarounds; attraction breeds pull. Contrast the two failure modes participants have likely met: the rebranded ops team (a ticket queue with a new name - no self-service, no product thinking, just the old bottleneck) and the ivory-tower platform (built in isolation for a year, launched to users who never asked for it - Field of Dreams engineering). The healthy pattern, via Team Topologies' interaction modes from Module 2: COLLABORATE with two or three pilot teams to discover what is actually painful, productise that into X-as-a-Service, repeat. Cognitive load (Module 1) is the value proposition throughout: every capability the platform absorbs is capacity returned to product teams for their actual domain."
            },
            {
                "type": "content",
                "title": "User-Centric Design for Internal Platforms",
                "bullets": [
                    "Your users are developers - so do real product discovery: interviews, journey maps, personas.",
                    "Measure the journey: time-to-first-deploy for a NEW team is the flagship UX metric.",
                    "Documentation IS the interface: quickstarts, copy-paste examples, honest error messages.",
                    "Golden paths (Spotify's term): the supported, delightful default - with escape hatches.",
                    "Start from the Thinnest Viable Platform; grow by demand, not by roadmap fantasy.",
                ],
                "notes": "Treat developers with the same UX seriousness a product team gives customers - it feels strange the first time and pays immediately. Discovery: interview teams about their path to production and map the journey (idea -> repo -> pipeline -> deploy -> observe); every wait, ticket and confusion point is a product opportunity - Module 1's cognitive-load pains, now itemised. Time-to-first-deploy is the flagship metric because it compresses the whole experience into one number a CTO understands: from 'new team formed' to 'hello-world serving in production' - weeks in ticket-driven organisations, minutes on a good platform (our capstone's golden path is a working miniature: template + pipeline + runtime, and participants time it). Documentation as interface is literal: for most consumers the platform IS its docs and templates - a capable platform with poor docs is, from the user's chair, a poor platform; invest accordingly (quickstarts over reference dumps, tested copy-paste examples, error messages that say what to DO next). Golden paths, Spotify's coinage: the blessed path is supported, maintained and delightful, but not a cage - teams can step off it, accepting they then own what they leave behind; escape hatches prevent the mandate failure mode. TVP (Team Topologies): start with the smallest platform that helps - maybe one great template and one pipeline - and let real demand pull the roadmap; platforms built big-bang from imagined requirements join the ivory-tower graveyard."
            },
            {
                "type": "content",
                "title": "Measuring Success and ROI",
                "bullets": [
                    "Adoption: % of services on the golden path - and the trend. Voluntary adoption is the vote.",
                    "Speed: time-to-first-deploy; DORA metrics OF CONSUMING TEAMS (the platform's real output).",
                    "Load: support tickets per team per month should FALL as self-service rises.",
                    "Experience: developer NPS / quarterly surveys - would they recommend the platform?",
                    "ROI story: (per-team toil hours saved x teams) + risk reduction vs platform team cost.",
                ],
                "notes": "A platform consumes real headcount, so it must demonstrate value in numbers leadership respects - give participants the funding conversation on one slide. Adoption is the honest north star precisely because your platform is optional: teams choosing the paved road is a continuous referendum on whether it is actually better than DIY; falling adoption is user feedback, not user disloyalty. Speed: measure DORA metrics (Module 3) of the TEAMS USING the platform - the platform's output is not its own uptime but its customers' delivery performance; if consuming teams do not deploy more often with fewer failures, the platform is decoration. Support load falling while adoption rises is the self-service proof - a rising ticket count means you built a ticket queue with extra steps. Developer NPS and lightweight quarterly surveys catch what metrics miss; the free-text answers are roadmap gold. The ROI arithmetic is simple enough for a slide and strong enough for a budget meeting: hours of infrastructure toil saved per team per month, times number of teams, priced at loaded cost - typically dwarfing a platform team's cost at even modest scale - plus the harder-to-price but very real risk term (one prevented breach or one halved recovery time). Close the loop with Module 9's warning label: measure the SYSTEM, never individuals, and never let platform metrics become team report cards - Module 3's gaming lesson applies doubly here."
            },
            {
                "type": "content",
                "title": "Operating Model - and What NOT to Build",
                "bullets": [
                    "Product-fund the platform (a team with a roadmap), not project-fund (a deliverable that 'ends').",
                    "The platform has SLOs and support hours - it is production, with customers.",
                    "Deprecation policy: versioned templates, migration windows, no rug-pulls.",
                    "Say NO deliberately: exotic needs stay with the teams that have them (escape hatch, not feature).",
                    "The platform team is a stream-aligned team whose product is the platform.",
                ],
                "notes": "Operating-model failures kill more platforms than technical ones - four traps and their answers. Funding: a project-funded platform 'finishes', its team disbands, and the artifact rots into the legacy it was meant to replace; product funding (a standing team, a roadmap, ongoing discovery) matches the reality that a platform is never done. Production discipline: the platform sits under every team's delivery path, so it needs SLOs (Module 8, applied to yourself), an on-call story, and honest support hours - a platform that goes dark at 17:00 while its consumers are on call is not a product, and eating your own dog food here builds credibility faster than any roadshow. Deprecation: platform churn is a tax on every consumer, so version templates, announce windows, provide migration tooling - trust, once rug-pulled, does not return. Saying no is a product skill: the platform serves the COMMON 80% brilliantly; the exotic 20% uses the escape hatch and owns its choice - a platform that chases every request becomes an unmaintainable everything-store (this is canvas box 9, and it is the box groups struggle with most, which is exactly why it is there). EXERCISE NOW (25 min + debrief, instructor/platform-canvas.md): groups design a platform for an organisation someone at the table knows - then present in two minutes; debrief on boxes 8 and 9, and on whether developers would CHOOSE their platform."
            },
        ]
    },

    # ------------------------------------------------------------- Module 10
    {
        "section_title": "Module 10\nHands-On Workshops",
        "section_notes": "This module IS the hands-on core of the course, exactly as the outline promises: a basic DevOps pipeline, a microservice built and deployed, and IaC implemented - all on the participant's Ubuntu VM, all on localhost, tied together by the capstone golden path.",
        "slides": [
            {
                "type": "content",
                "title": "The Three Workshops - Map",
                "bullets": [
                    "W1 (Day 1 pm): Setting up a basic DevOps pipeline - GitHub Actions: test, build, scan+gate.",
                    "W2 (Day 2 am): Building and deploying a microservice - Docker -> Compose -> Kubernetes.",
                    "W3 (Day 2 pm): Implementing IaC - Terraform init/plan/apply/destroy + drift, on local Docker.",
                    "Same application throughout: the order+payment services you know from the demos.",
                    "Finale: the capstone runs all three as ONE golden path (workshops/ folder has the guides).",
                ],
                "notes": "Set expectations before the first workshop: these three blocks are where theory becomes muscle memory, and they use one continuous application so context never resets. Workshop 1 realises Module 5: participants copy the CI workflow into place, read it critically (job graph, permissions, pinned actions, the report-vs-gate Trivy pair), trigger it from a real pull request (or act locally), and watch it go green - Day 1 ends with a working pipeline, which matters emotionally as much as technically. Workshop 2 realises Module 6 end-to-end: build the image and inspect its layers, compose the two-service stack and watch service discovery work, then kind-deploy with probes and limits, scale, roll forward, roll back - the complete container journey in one morning. Workshop 3 realises Module 4: the full Terraform loop against local Docker including the drift experiment, plus the Ansible idempotence bonus - and the explicit read-through of what changes for cloud (one provider block). Timing guidance for the instructor: each workshop guide (workshops/ folder) marks a core path sized to fit the slot and stretch parts for fast finishers; insist on the verification checklists - done means checked, not time elapsed."
            },
            {
                "type": "content",
                "title": "Workshop Success Criteria",
                "bullets": [
                    "W1 done = PR triggers pipeline; test+build green; you can explain report vs gate.",
                    "W2 done = /health serves from Kubernetes on localhost:30080; rolled forward AND back.",
                    "W3 done = plan shows 3 resources; apply serves on :8090; drift detected; destroy leaves nothing.",
                    "Capstone done = ./run-capstone.sh green end-to-end + your PLATFORM-HANDOVER.md.",
                    "Struggling is the point - use the troubleshooting tables, then ask three, then ask me.",
                ],
                "notes": "Publish the definition of done up front so nobody optimises for 'got to the end of the page'. Each criterion is testable by the participant themselves - the pipeline is green or it is not, localhost:30080 answers or it does not, terraform destroy leaves zero tf- containers or it does not - which mirrors the whole course's philosophy: verification is automated, not vibes. The capstone at Day 2's end is the integration test of the human, not just the system: running the golden path script exercises every workshop's material in sequence (tests -> images -> scan -> cluster -> deploy -> smoke test), and the PLATFORM-HANDOVER.md document forces the platform-as-product thinking of Module 9 into writing. The last bullet sets lab culture deliberately: hitting errors is designed-in learning, the troubleshooting tables in each guide resolve the common 90%, the ask-three-before-me rule builds peer debugging habits, and instructors circulate rather than lecture. Fast finishers take the stretch goals (they are real: GHCR push, ingress, Terraform modules) rather than idling."
            },
        ]
    },

    # ------------------------------------------------------------- Module 11
    {
        "section_title": "Module 11\nSummary and Next Steps",
        "section_notes": "Close the course deliberately: recap what was built, hand participants a learning roadmap, and make the first week back at work concrete.",
        "slides": [
            {
                "type": "content",
                "title": "What You Built in Two Days",
                "bullets": [
                    "A microservice tested, containerised and orchestrated (demos + Workshop 2).",
                    "A CI pipeline with a real security gate (Workshop 1).",
                    "Infrastructure declared as code, with drift detection (Workshop 3).",
                    "A Kubernetes deployment with probes, limits and rolling updates - rolled back on command.",
                    "Policies, scans, dashboards, an SLO - and one survived incident (module demos).",
                    "A golden path handed over as a platform product (capstone).",
                ],
                "notes": "Walk the list slowly - this is the payoff slide. Every item ran on the participant's own VM and every artifact is in the course repository they keep. Invite one or two participants to say which module or workshop changed how they think about their current work."
            },
            {
                "type": "content",
                "title": "Continuing the Journey",
                "bullets": [
                    "Kubernetes: CKAD / CKA certifications; kind and minikube for practice.",
                    "IaC: HashiCorp Terraform Associate; Ansible for configuration management.",
                    "CI/CD: GitHub Actions docs and the act local runner you already installed.",
                    "Reading: Accelerate (DORA), Team Topologies, The Phoenix Project, Google SRE books (free online).",
                    "Communities: platformengineering.org, CNCF projects, local DevOps meetups.",
                ],
                "notes": "Participants keep the slides, the labs and the sample application - everything reruns on any Ubuntu 24.04 machine via lab-setup/install-ubuntu24.sh. Encourage them to re-run the capstone from scratch within two weeks; retention comes from the second unaided repetition. The reading list is ordered deliberately: Phoenix Project for narrative buy-in (give it to managers), Accelerate for the evidence, Team Topologies for org design, SRE books for depth on Module 8."
            },
            {
                "type": "content",
                "title": "Your First Week Back at Work",
                "bullets": [
                    "Pick ONE painful manual path and automate it end to end - small and finished beats big and abandoned.",
                    "Add a real gate to an existing pipeline: tests or a fixable-critical scan.",
                    "Write the first blameless postmortem after your next incident - and share it.",
                    "Measure a baseline: your team's deployment frequency and lead time this month.",
                    "Start the platform conversation: which golden path would help the most teams?",
                ],
                "notes": "End with commitments: ask each participant to write down the one action they will take in the first week and share it with the room - spoken commitments stick. Hand out the feedback survey, answer final questions, and run the Day 2 quiz if not already done."
            },
        ]
    },
]


def main() -> None:
    build_deck(
        "DevOps & Platform Engineering",
        "Day 1 — Foundations, Culture, Tools, IaC & CI/CD",
        DAY1_MODULES,
        "DevOps-PlatformEngineering-Day1.pptx",
    )
    build_deck(
        "DevOps & Platform Engineering",
        "Day 2 — Containers, Security, Observability, Platform Thinking & Workshops",
        DAY2_MODULES,
        "DevOps-PlatformEngineering-Day2.pptx",
    )


if __name__ == "__main__":
    main()
