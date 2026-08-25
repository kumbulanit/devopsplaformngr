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
    tf = slide.shapes.add_textbox(Inches(0.5), Inches(2.4), Inches(9), Inches(2.2)).text_frame
    tf.word_wrap = True
    # "Module 3\nTools and Technologies" -> a large module line and a subtitle line,
    # each styled explicitly (an unstyled second paragraph inherits the layout default).
    lines = [ln for ln in title.split("\n") if ln.strip()]
    for i, line in enumerate(lines):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.text = line
        para.alignment = PP_ALIGN.CENTER
        if i == 0:
            _set_font(para.runs[0], 40, bold=True, color=COLOR_SECTION)
        else:
            _set_font(para.runs[0], 24, bold=False, color=COLOR_TITLE)
    _drop_empty_placeholders(slide)
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
    _drop_empty_placeholders(slide)
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
    _drop_empty_placeholders(slide)
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
    _drop_empty_placeholders(slide)
    if notes:
        slide.notes_slide.notes_text_frame.text = notes


def _drop_empty_placeholders(slide) -> None:
    """Remove unused layout placeholders.

    Slides built on the 'Title Only' layout get their title and body from
    explicit textboxes, which leaves the layout's own placeholder empty — and
    PowerPoint renders an empty placeholder as a 'Click to add title' prompt in
    the editing view. Deleting them keeps the authored slides clean.
    """
    for shape in list(slide.placeholders):
        if not shape.has_text_frame or not shape.text_frame.text.strip():
            shape._element.getparent().remove(shape._element)


def _set_indent(paragraph, marl: int) -> None:
    """Override the layout's indentation for one paragraph (EMU left margin)."""
    pPr = paragraph._p.get_or_add_pPr()
    pPr.set("marL", str(int(marl)))
    pPr.set("indent", "0")


def add_detail_slide(prs, title: str, sections: List[tuple], notes: str) -> None:
    """A deep-dive slide: several bold sub-headings, each with indented detail lines.

    `sections` is a list of (heading, [detail lines]) tuples. Font size adapts to
    the amount of content so a dense expansion still fits one slide.
    """
    slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(slide_layout)
    # Deep-dive titles are long by nature: shrink to keep them on one line, and
    # only fall back to two lines (with the body pushed down) when unavoidable.
    title_pt = 24 if len(title) <= 51 else 22
    two_line_title = len(title) > (51 if title_pt == 24 else 56)
    title_shape = slide.shapes.add_textbox(Inches(0.45), Inches(0.25), Inches(9.1),
                                           Inches(1.1) if two_line_title else Inches(0.75))
    tf = title_shape.text_frame
    tf.word_wrap = True
    tf.text = title
    _set_font(tf.paragraphs[0].runs[0], title_pt, bold=True, color=COLOR_TITLE)

    # Pick the largest font size at which the (wrapped) content still fits the
    # body area, so a dense expansion never spills off the slide.
    def _fits(head_size: int) -> bool:
        body_size = head_size - 2
        head_w, body_w = 626.0, 604.0          # usable points at each indent level
        rows = 0
        for heading, points in sections:
            rows += max(1, -(-len(heading) // int(head_w / (0.50 * head_size))))
            for point in points:
                rows += max(1, -(-len(point) // int(body_w / (0.46 * body_size))))
        gaps = 8 * max(len(sections) - 1, 0)
        budget = 470 - (30 if two_line_title else 0)
        return rows * 1.22 * head_size + gaps <= budget

    head_pt = next((size for size in (20, 19, 18, 17, 16, 15, 14) if _fits(size)), 13)
    body_pt = head_pt - 2

    body_top = Inches(1.45) if two_line_title else Inches(1.05)
    box = slide.shapes.add_textbox(Inches(0.55), body_top, Inches(8.9), Inches(5.7))
    body = box.text_frame
    body.word_wrap = True
    first = True
    for heading, points in sections:
        if not first:
            spacer = body.add_paragraph()
            spacer.text = ""
            spacer.font.size = Pt(6)
        p = body.paragraphs[0] if first else body.add_paragraph()
        first = False
        p.text = heading
        p.level = 0
        _set_indent(p, marl=0)
        p.font.size = Pt(head_pt)
        p.font.bold = True
        p.font.color.rgb = COLOR_TITLE
        p.font.name = "Calibri"
        for point in points:
            sub = body.add_paragraph()
            sub.text = point
            sub.level = 1
            _set_indent(sub, marl=Inches(0.3))
            sub.font.size = Pt(body_pt)
            sub.font.color.rgb = COLOR_BODY
            sub.font.name = "Calibri"
    _drop_empty_placeholders(slide)
    if notes:
        slide.notes_slide.notes_text_frame.text = notes


def _render_slide(prs, slide: dict) -> None:
    stype = slide["type"]
    if stype == "content":
        add_content_slide(prs, slide["title"], slide["bullets"], slide.get("notes", ""))
    elif stype == "diagram":
        add_diagram_slide(prs, slide["title"], slide["image"], slide.get("caption", ""), slide.get("notes", ""))
    elif stype == "two_col":
        add_two_column_slide(prs, slide["title"], slide["left"], slide["right"], slide.get("notes", ""))
    elif stype == "quote":
        add_quote_slide(prs, slide["title"], slide["quote"], slide.get("source", ""), slide.get("notes", ""))
    elif stype == "detail":
        add_detail_slide(prs, slide["title"], slide["sections"], slide.get("notes", ""))


def build_deck(deck_title: str, subtitle: str, modules: List[dict], output_name: str,
               deep_dives: dict | None = None) -> None:
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    intro_notes = ("Welcome participants. These decks are shared with participants after the course; the speaker notes "
                   "double as the written reference, so read them when reviewing. Modules 1-9 are theory with small "
                   "demos; the three workshops and the capstone are the hands-on core.")
    if deep_dives:
        intro_notes += (" NAVIGATION: each core topic is a summary slide followed by one or two 'Deep Dive' slides that "
                        "expand every bullet with mechanism, evidence, examples and anti-patterns. When running to time, "
                        "present the summary slides and use the deep dives as the participant reference and for the "
                        "discussion prompts; when the room wants depth, teach straight through them.")
    add_title_slide(prs, deck_title, subtitle, notes=intro_notes)

    for mod in modules:
        add_section_slide(prs, mod["section_title"], notes=mod.get("section_notes", ""))
        for slide in mod["slides"]:
            _render_slide(prs, slide)
            # Expansions are keyed on the summary slide's title and inserted
            # immediately after it, so each topic reads:
            #   summary -> deep dive(s) -> diagram -> central-bank worked example.
            for extra in (deep_dives or {}).get(slide.get("title", ""), []):
                _render_slide(prs, extra)

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


# ===========================================================================
# DAY 1 - DEEP DIVES
# ---------------------------------------------------------------------------
# Each entry is keyed on the title of a summary slide in DAY1_MODULES; the
# detail slides listed are inserted immediately after that slide. The summary
# slide states the point; these slides unpack every bullet with mechanism,
# evidence, examples and anti-patterns, because participants keep the deck as
# their written reference.
# ===========================================================================
DAY1_DEEP_DIVES = {

    # ----------------------------------------------------- Module 1 topics
    "Where DevOps Came From": [
        {
            "type": "detail",
            "title": "Deep Dive: The Incentive Conflict That Built the Wall",
            "sections": [
                ("Two mandates that could not both win", [
                    "Dev was appraised on change delivered: features per quarter, projects closed, scope signed off.",
                    "Ops was appraised on stability: uptime %, incident count, SLA breaches, audit findings.",
                    "Change is the single largest cause of incidents - so for Ops, 'safe' rationally meant 'slow' or 'no'.",
                    "Nobody was lazy or obstructive: two rational actors, one badly designed measurement system.",
                ]),
                ("What the handoff physically looked like", [
                    "A release was a document event: a build artefact, an install runbook, a change ticket, a war room.",
                    "Ops received software they had never run, at night, on infrastructure Dev had never seen.",
                    "Environment drift: laptop != test != production, so 'works on my machine' was literally true.",
                    "The Change Advisory Board was the only risk control - approval as a substitute for automated proof.",
                ]),
                ("The measurable cost of that design", [
                    "Lead time in months; feedback from real users arrived long after the code was written.",
                    "A release carrying 200 changes turns root-cause analysis into a combinatorial search.",
                    "Rollback meant restoring backups at 03:00 - MTTR in hours or days, not minutes.",
                    "Each side collected evidence proving the other was at fault; the system itself was never the defendant.",
                ]),
            ],
            "notes": "Slow down here - if participants internalise only one thing from Module 1, make it this: the wall of confusion was an INCENTIVE artefact, not a personality clash. Draw the two appraisal forms on the flipchart side by side; ask the room which behaviours each one rewards. The key mechanism to state explicitly: because change causes most incidents, an organisation that measures Ops purely on stability has paid them to resist the very thing Dev is paid to produce. Every downstream symptom follows from that - CAB meetings, ticket queues, quarterly release trains, environment drift, weekend deployments. Useful probe for the room: 'who here has an approval step that has never once rejected a change?' - that is approval theatre, a control that costs delay and buys no safety. Second probe: 'when did your last production issue get fixed, and how much of that time was diagnosis versus waiting for permission or for a person?' Capture the answers; you reuse them in the DORA metrics discussion in Module 3 and in the value-stream framing of the Three Ways."
        },
        {
            "type": "detail",
            "title": "Deep Dive: 2009 - the Year the Frame Flipped",
            "sections": [
                ("Velocity 2009: '10+ Deploys per Day' (Allspaw & Hammond, Flickr)", [
                    "A dev and an ops lead presented TOGETHER - the format was itself the argument.",
                    "Enablers: automated infrastructure, shared version control, a one-step build and deploy, shared metrics.",
                    "Plus chat robots announcing every deploy, and an explicit no-blame norm when one went wrong.",
                    "The claim that shocked the industry: frequent deployment makes systems SAFER, not riskier.",
                ]),
                ("devopsdays, Ghent, October 2009 (Patrick Debois)", [
                    "Debois wanted the Agile community to include operations; the conference gave the movement a room.",
                    "The word 'DevOps' spread as a hashtag from that event - a community label, never a vendor product.",
                    "It grew bottom-up from practitioners, which is why it has practices but no certification authority.",
                ]),
                ("The insight, stated precisely", [
                    "Small batch: 50 lines can be reviewed properly, tested meaningfully, and reverted in one command.",
                    "Small batch: when it breaks, the suspect list is one change, not two hundred.",
                    "Frequency builds muscle: a deploy done 30 times a week is automated, rehearsed and boring.",
                    "So the conflict dissolves: speed and stability stop being a trade-off and start reinforcing each other.",
                ]),
                ("The evidence that followed (DORA / Accelerate, 2014-present)", [
                    "Multi-year survey research found speed and stability POSITIVELY correlated across thousands of teams.",
                    "High performers deploy far more often AND fail less often AND recover faster - all at once.",
                ]),
            ],
            "notes": "The historical detail matters because it is the participants' evidence when they go home and someone says 'deploying more often is reckless'. Tell the Flickr story properly: John Allspaw (Ops) and Paul Hammond (Dev) at O'Reilly Velocity 2009, presenting jointly, listing the mechanics that made ten deploys a day possible - automated infrastructure, a shared repository, a one-step deploy, shared metrics, chat-based transparency, and a culture where a broken deploy triggered investigation rather than punishment. Note how many of those are things this course builds: version control everywhere (Module 3), automated infrastructure (Module 4), one-step pipeline deploys (Module 5), shared metrics (Module 8), transparency (Module 2). Patrick Debois then created the venue and the vocabulary at devopsdays in Ghent, Belgium, in October 2009. Emphasise the counter-intuitive reframing with a physical analogy: a surgeon who performs one operation a year is not safer than one who performs ten a week. Rehearsal, small increments and rapid feedback are the safety mechanisms. Finally, point at Accelerate (Forsgren, Humble, Kim) as the empirical backbone: the speed-versus-stability trade-off that everyone assumed exists does not appear in the data - the same practices drive both."
        },
    ],

    "What DevOps Is (and Is Not)": [
        {
            "type": "detail",
            "title": "Deep Dive: A Working Definition You Can Defend",
            "sections": [
                ("The definition, unpacked", [
                    "PRACTICES: CI, CD, IaC, automated testing, observability, incident review - the visible mechanics.",
                    "CULTURE: shared ownership, blameless learning, information flow - what makes the practices stick.",
                    "FLOW OF VALUE: the unit of interest is a customer-visible change, not a ticket or a deployment.",
                    "Both halves are required: tools without culture become expensive theatre; culture without tools stalls.",
                ]),
                ("The goal, stated as a measurable pair", [
                    "Shorten lead time (idea -> production) WITHOUT increasing change failure rate - both, or it does not count.",
                    "Optimising speed alone gives you fast outages; optimising stability alone gives you frozen systems.",
                    "This is why Module 3 introduces the four DORA metrics as a BALANCED set - two speed, two stability.",
                ]),
                ("Five things DevOps is not - and what people usually mean instead", [
                    "'A DevOps engineer' - usually a platform, build or infrastructure engineer; ask what they actually do.",
                    "'The DevOps team' - usually a renamed sysadmin team, and often a brand new third silo.",
                    "'We bought a DevOps tool' - a pipeline engine is a means; nothing about outcomes is guaranteed.",
                    "'Ops with Jenkins' - automating a broken handoff makes the handoff faster, not the system better.",
                    "'It means no ops people' - operations work does not vanish, it becomes a product other teams consume.",
                ]),
            ],
            "notes": "This slide is armour for the participants' first week back. They WILL sit in a meeting where 'DevOps' means something incoherent, and they need a precise, non-arrogant way to redirect it. Give them the reframing question rather than the correction: instead of 'that is not DevOps', ask 'what outcome are we trying to move - lead time, failure rate, recovery time?' Nobody argues with that question, and it converts a vocabulary fight into a measurement conversation. Work the anti-patterns concretely. The third-silo failure is the most common and the most damaging: an organisation creates a central 'DevOps team' that owns all pipelines and environments, product teams file tickets to it, and within a year the queue is the new wall of confusion - the exact structure DevOps exists to remove. Note the important nuance for Module 9: a PLATFORM team looks superficially similar but is defined by self-service - teams consume it without filing tickets - and that difference is the whole thing. Also handle the 'no ops people' fear honestly and early, because someone in the room is quietly worried about their job: operational work grows in a cloud-native world; what changes is its shape - from manual execution to building the systems that make execution unnecessary."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Ownership and the Lean Lineage",
            "sections": [
                ("'You build it, you run it' - what it really commits you to", [
                    "Werner Vogels, Amazon (2006 ACM Queue interview): the team that writes a service also operates it.",
                    "The mechanism is the feedback loop - the person paged at 03:00 is the person who can fix the cause.",
                    "It changes code: better error handling, useful logs, health checks, timeouts, graceful degradation.",
                    "The fair-deal caveat: ownership without authority, tooling or headcount is just blame with a pager.",
                    "So the platform (Module 9) exists to make ownership affordable, not to take ownership away.",
                ]),
                ("What software borrowed from lean manufacturing", [
                    "Small batches: reduce the size of the thing moving through the system, and everything else improves.",
                    "Limit work in progress: more parallel work means more context switching and longer queues, not more output.",
                    "Little's Law: lead time = WIP / throughput - so cutting WIP shortens lead time with no extra capacity.",
                    "Andon cord: anyone may stop the line when quality breaks; fixing it outranks new work.",
                    "Build quality in: inspect at the source (tests, review, scans) instead of a QA phase at the end.",
                ]),
                ("The biggest waste in software is WAITING", [
                    "Value-stream maps of real delivery pipelines typically show most elapsed time as queue time, not work time.",
                    "Waiting for review, for a test environment, for a CAB slot, for an ops ticket, for the release window.",
                    "So the first improvement is almost never 'code faster' - it is 'delete or automate a wait'.",
                    "Exercise back at work: map one change end to end and mark each hour as WORK or WAIT. Attack the waits.",
                ]),
            ],
            "notes": "Two ideas here that participants tend to under-rate. First, 'you build it, you run it' is not a slogan about accountability - it is a deliberately constructed feedback loop. The team feels the operational consequence of its own design decisions, at the moment those consequences occur, which is the only reliable way design quality improves. But be balanced and say the caveat out loud, because participants will be asked to implement this: giving developers the pager while withholding production access, tooling, dashboards or time to fix things creates burnout and resentment, not learning. Ownership must arrive with authority, capability and capacity - that is precisely the bargain the internal platform underwrites. Second, the lean lineage is mechanical, not metaphorical. Little's Law is the one piece of maths in this course and it is worth writing on the board: lead time = work in progress divided by throughput. It says that if a team has 12 things in flight and finishes 3 per week, work takes 4 weeks - and that halving WIP halves lead time without anyone working harder. That is the single most persuasive argument a participant can take to a manager who wants faster delivery. Then the waiting point: when teams map their real value stream, the coding is a small fraction of elapsed time; the rest is queues. Improvement effort spent anywhere other than the biggest queue is, by definition, not improving the system (Theory of Constraints - Module 1's flow discussion continues this)."
        },
    ],

    "The Three Ways (The Phoenix Project / DevOps Handbook)": [
        {
            "type": "detail",
            "title": "Deep Dive: The First Way - Flow (Left to Right)",
            "sections": [
                ("What flow optimises", [
                    "The unit of analysis is the whole value stream: idea -> code -> build -> test -> release -> operate.",
                    "Local optimisation is the trap: a team that doubles its coding speed changes nothing if QA is the constraint.",
                    "Make work VISIBLE first (a board with real queue states), because invisible queues cannot be attacked.",
                ]),
                ("The four flow levers, in the order they usually pay off", [
                    "1. Reduce batch size: smaller PRs, smaller releases, smaller migrations - risk falls faster than size.",
                    "2. Limit WIP: fewer things at once finishes more things sooner (Little's Law); stop starting, start finishing.",
                    "3. Remove handoffs: every handoff adds a queue, a context loss and a chance to lose knowledge.",
                    "4. Eliminate rework: defects found downstream cost multiples of defects found at the keyboard.",
                ]),
                ("How this course implements flow", [
                    "Trunk-based development and small PRs (Module 5) attack batch size directly.",
                    "IaC (Module 4) removes the 'wait for an environment' handoff - environments become self-service.",
                    "The pipeline (Workshop 1) replaces a chain of human handoffs with one automated path.",
                    "The platform golden path (Module 9) removes the biggest handoff of all: the ticket to another team.",
                ]),
            ],
            "notes": "Teach the Three Ways as a diagnostic instrument, not as trivia. The First Way asks: where does work slow down? Insist on the systems-thinking point that local optimisation is often value-destroying - speeding up a step that is not the constraint just grows the queue in front of the real constraint (Goldratt's Theory of Constraints, which is the intellectual ancestor of The Phoenix Project's plot). Practical facilitation: ask the room to name their constraint out loud. Common answers - 'test environments', 'the single person who knows the deploy', 'security review', 'the DBA team' - and every one of them is a handoff or a queue, not a typing-speed problem. Emphasise making work visible: teams cannot manage a queue they cannot see, which is why kanban boards with explicit WIP limits are a DevOps practice and not just an Agile ritual. Then connect each course module to the lever it pulls, so participants leave with the mapping rather than a list of tools."
        },
        {
            "type": "detail",
            "title": "Deep Dive: The Second and Third Ways",
            "sections": [
                ("SECOND WAY - Feedback (right to left)", [
                    "Principle: shorten the distance, in TIME and in PEOPLE, between causing a problem and learning about it.",
                    "Fast and cheap first: linting and unit tests in seconds, integration tests in minutes, then the slow suites.",
                    "Feedback at every altitude: type checker, test, code review, scanner, canary metrics, pager, customer telemetry.",
                    "Swarm on failure: a red mainline or a failing canary stops the line - that is the andon cord in software.",
                    "Anti-pattern: signals nobody acts on (muted alerts, ignored dashboards, skipped flaky tests) - noise trains blindness.",
                ]),
                ("THIRD WAY - Continual learning and experimentation", [
                    "Assume the system will fail; design for cheap failure instead of pretending failure is preventable.",
                    "Practise failure deliberately: game days, chaos experiments, restore-from-backup drills, incident simulations.",
                    "Convert incidents into system changes via blameless postmortems (Module 2) - the incident is the tuition fee.",
                    "Make improvement work first-class: reserve capacity for it, or it is always postponed by feature work.",
                    "Share what you learn: internal postmortems published widely turn one team's outage into org-wide immunity.",
                ]),
                ("Using the Three Ways as a checklist", [
                    "For any proposed practice ask: does it improve flow, speed feedback, or build learning? If none - why do it?",
                    "Classify examples with the room: code review (feedback), feature flags (flow + feedback), game day (learning).",
                    "The Ways are ordered on purpose: flow without feedback ships faster failures; both without learning stagnates.",
                ]),
            ],
            "notes": "Second Way: the crucial nuance is that feedback has to be fast AND trusted. A test suite that takes 90 minutes is technically feedback, but developers context-switch away and return to a stale result, so its practical value collapses - which is exactly why the test pyramid (Module 5) puts seconds-fast unit tests first. Equally, a signal that is routinely ignored is worse than no signal, because it teaches the team that red things are survivable; that is why Module 5 has an entire slide on report-versus-gate and Module 8 has one on alert quality. Third Way: the framing that lands with managers is insurance - a game day is a rehearsal you schedule at 10:00 on a Tuesday instead of one that schedules itself at 03:00 on a Sunday. Mention the classic examples: Netflix's Chaos Monkey terminating instances in production to force resilient design, Google's DiRT exercises, and the humble but powerful restore-from-backup drill (an untested backup is a hope, not a backup). Then close with the ordering argument: the Ways build on each other - fast flow without feedback means you ship defects faster, and both without learning means you keep re-solving the same incident. Participants run a miniature of the Third Way in Lab 08's game day."
        },
    ],

    "CALMS - the Five Dimensions of DevOps": [
        {
            "type": "detail",
            "title": "Deep Dive: CALMS as a Health Check (C, A, L)",
            "sections": [
                ("CULTURE - the multiplier on everything else", [
                    "What good looks like: shared goals across Dev and Ops, bad news travels fast, failure triggers inquiry.",
                    "Diagnostic questions: who gets paged? who may say 'stop'? what happened after the last serious incident?",
                    "Failure mode: a fully automated pipeline whose output still waits three weeks for an approval board.",
                    "Covered in Module 2 - Westrum typology, psychological safety, blameless postmortems.",
                ]),
                ("AUTOMATION - make the machine do the repeatable work", [
                    "Automate what is repetitive, error-prone, or done under time pressure at 03:00 - in that order.",
                    "Test: can a new engineer take a change to production on day one using only documented, automated paths?",
                    "Failure mode: 'we automated the deploy' but tests are thin, so nobody trusts it and deploys stay quarterly.",
                    "Second failure mode: automating a bad process faithfully - fix the process first, then encode it.",
                    "Covered in Modules 4 and 5 - IaC, pipelines, automated tests and scans.",
                ]),
                ("LEAN - flow, small batches, less waste", [
                    "Waste categories in delivery: waiting, handoffs, partially done work, rework, task switching, unused features.",
                    "Waiting dominates: most of a change's elapsed life is spent in a queue, not being worked on.",
                    "Test: what is the median size of a merged pull request, and how long was it open?",
                    "Failure mode: one release train carrying 200 changes - when it derails, root-causing is guesswork.",
                ]),
            ],
            "notes": "Use CALMS as an assessment framework the participants can actually run at home, not as an acronym to memorise. The observation that carries the slide: organisations over-invest in the A and under-invest in C, L, M and S - because automation is purchasable and the others require organisational change. Ask the room to privately score their organisation 1-5 on each letter, then show hands per letter. In almost every class the shape is the same: Automation is highest, Measurement and Sharing are lowest. That shape IS the diagnosis, and it explains the common complaint 'we bought all the tools and nothing got faster'. For each letter give them a single sharp diagnostic question they can ask in their own organisation - those questions are on the slide deliberately, so the deck functions as a workbook. On Automation, spend a moment on the second failure mode: encoding a broken process in Terraform makes it faster and permanent. Simplify the process, THEN automate it - otherwise you have industrialised the waste."
        },
        {
            "type": "detail",
            "title": "Deep Dive: CALMS as a Health Check (M, S)",
            "sections": [
                ("MEASUREMENT - decide with data, not anecdotes", [
                    "Baseline the four DORA metrics: deployment frequency, lead time for change, change failure rate, time to restore.",
                    "Two speed and two stability metrics, always read as a SET - improving one by wrecking another is not progress.",
                    "Add flow metrics (WIP, queue time) and reliability metrics (SLO attainment, error budget burn - Module 8).",
                    "Measure the system, never the individual: metrics used for appraisal become metrics that get gamed.",
                    "Failure mode: 'deploys feel risky' as the basis for policy, with no data on whether they actually are.",
                ]),
                ("SHARING - how one team's learning becomes everyone's", [
                    "Internal open source: any team may raise a PR on another team's repo, platform repos included.",
                    "Publish postmortems widely - an incident read by 200 engineers immunises 200 engineers.",
                    "Documentation as a product: owned, reviewed, versioned in Git, and measured by whether people succeed with it.",
                    "Cheap high-value rituals: demo days, internal tech talks, README-first design, ADRs in the repo.",
                    "Failure mode: three teams independently build three deployment scripts - the same problem, paid for three times.",
                ]),
                ("Running CALMS as a workshop back home", [
                    "Score each letter 1-5 with the team, anonymously, then discuss only the biggest gap.",
                    "Pick ONE improvement per quarter with a named owner and a metric that would move if it worked.",
                    "Re-score every quarter; the trend matters more than the absolute number.",
                ]),
            ],
            "notes": "Measurement is where most participants can make progress fastest, because a baseline costs nothing and changes the conversation immediately. Stress the balanced-set discipline: a team told to raise deployment frequency will find a way, possibly by splitting deploys meaninglessly; the change failure rate and restore time keep them honest. Also stress the Goodhart's Law warning - the moment a metric is attached to individual appraisal it stops measuring reality and starts measuring compliance; DORA metrics are for the delivery SYSTEM, presented at team or value-stream level. Sharing is the letter people skip because it has no product to buy, yet it is where compounding happens: the same problem solved once and shared beats the same problem solved five times in five teams. Give the practical minimum: a published postmortem archive anyone can read, an internal package or template registry, and a documented expectation that platform repositories accept external PRs. Close with the workshop instructions on the slide - participants can run this in their own team within two weeks, and it makes Module 9's platform canvas exercise easier because the pain points are already listed."
        },
    ],

    "Why Platform Engineering Emerged": [
        {
            "type": "detail",
            "title": "Deep Dive: Cognitive Load - the Real Bottleneck",
            "sections": [
                ("What every product team was suddenly expected to know", [
                    "Runtime: containers, Kubernetes objects, networking, ingress, storage classes, resource limits.",
                    "Delivery: pipeline syntax, artifact registries, image signing, environment promotion, rollback mechanics.",
                    "Infrastructure: Terraform, state management, cloud IAM, networking, cost controls.",
                    "Operations: metrics, logs, traces, dashboards, alert rules, SLOs, on-call process.",
                    "Security: dependency and image scanning, secrets management, policy, least privilege, compliance evidence.",
                ]),
                ("The three kinds of load (Sweller, applied by Team Topologies)", [
                    "INTRINSIC: the essential difficulty of the team's own domain - payments, orders, pricing. Reduce by training.",
                    "EXTRANEOUS: everything the environment forces on them - YAML dialects, cluster quirks, ticket queues.",
                    "GERMANE: effort that builds durable expertise - the load you actually WANT to protect.",
                    "A team's capacity is finite: extraneous load is paid for out of the intrinsic budget, i.e. out of the product.",
                ]),
                ("Why 'every team learns everything' does not scale", [
                    "Eight product teams each becoming Kubernetes experts is the same work paid for eight times.",
                    "Depth is diluted: eight part-time experts produce eight subtly different, subtly wrong configurations.",
                    "Onboarding stretches from days to months, because the prerequisite stack is enormous.",
                    "The best engineers spend their time on infrastructure yak-shaving instead of the business problem.",
                ]),
            ],
            "notes": "This is the intellectual core of the platform half of the course, so make the mechanism vivid rather than abstract. Do the arithmetic with the room: list on the flipchart everything a team must know today to take a new service to production safely, and count it. In most organisations the list runs to 20-30 distinct technologies and processes; the CNCF landscape alone contains well over a thousand projects. Then make the economic point: that knowledge is not free, and it is paid for out of the same finite team capacity that was supposed to be building the product. Cognitive load theory gives the vocabulary to say this to leadership without sounding like complaining engineers - intrinsic load is the work you hired the team for, extraneous load is the toll the environment charges, and the platform's entire reason to exist is to collapse the toll. Useful framing question for the room: 'what fraction of your last sprint went into things a customer would recognise as your product?' The gap between that number and 100% is the extraneous load, and it is the platform's addressable market. Anticipate the objection 'so developers stay ignorant of infrastructure' - the answer is that golden paths have escape hatches, teams remain accountable for what they run, and the platform removes the obligation to REBUILD the knowledge, not the permission to have it."
        },
        {
            "type": "detail",
            "title": "Deep Dive: What a Platform Actually Provides",
            "sections": [
                ("Golden path instead of a blank YAML file", [
                    "Before: a new service starts from an empty repo, and the first two weeks are plumbing.",
                    "After: one command scaffolds repo, pipeline, image build, deployment manifests, dashboards and alerts.",
                    "The paved road is opinionated but OPTIONAL - teams may leave it, and then they carry the extra weight.",
                    "Standardisation is a by-product, not the goal: teams choose the road because it is genuinely faster.",
                ]),
                ("The layers of an Internal Developer Platform (IDP)", [
                    "Interfaces: CLI, service catalogue/portal, API, templates - how developers actually consume the platform.",
                    "Golden paths: opinionated, working end-to-end journeys for the common service shapes.",
                    "Capabilities: environments, CI/CD, secrets, observability, policy, cost visibility - operated once, shared.",
                    "Infrastructure: clusters, registries, networks, cloud accounts - invisible to the consuming team.",
                ]),
                ("Platform engineering is DevOps industrialised, not DevOps abandoned", [
                    "The DevOps goal is unchanged: teams own their services end to end, including in production.",
                    "The platform makes that ownership AFFORDABLE by removing the extraneous work from every team.",
                    "The test that keeps it honest: consumption is self-service. If teams file tickets and wait, it is a silo again.",
                    "Module 9 treats the platform as a product with users, adoption metrics, a roadmap and a support model.",
                ]),
            ],
            "notes": "Make the before/after tangible, because 'golden path' is otherwise a marketing phrase. Describe the day-one experience concretely: a developer runs one command or fills one form, and within minutes has a repository with a working pipeline, a container build, deployment manifests for each environment, a dashboard, default alerts, and a running hello-service reachable on a real URL - with security scanning and policy already in the path they did not have to think about. That is what 'production on day one' means, and it is the capstone's shape in miniature. Be precise about the paved-road principle: mandates create resentment and shadow infrastructure; a genuinely faster default creates voluntary adoption, and adoption rate then becomes the platform team's honest scoreboard. Keep the escape hatch explicit - a team with a legitimately unusual requirement can step off the road, but they then own what the platform would have handled, which is a fair, transparent trade rather than a fight. Finally, defuse the identity question that always comes up in the room: platform engineering does not replace DevOps culture. If the platform team becomes the only group that can deploy anything, the organisation has rebuilt the wall of confusion with better tooling. Self-service is the difference, and it is a structural test, not an attitude."
        },
    ],

    # ----------------------------------------------------- Module 2 topics
    "Culture Is Measurable: the Westrum Typology": [
        {
            "type": "detail",
            "title": "Deep Dive: Reading the Three Westrum Cultures",
            "sections": [
                ("PATHOLOGICAL - power-oriented", [
                    "Information is a personal asset: knowing something others do not is leverage, so it is hoarded.",
                    "Messengers are shot, so problems surface only when they become undeniable - i.e. as outages.",
                    "Responsibilities are shirked; bridging between departments is discouraged as disloyalty.",
                    "Failure leads to scapegoating; novelty is crushed because it threatens the current order.",
                    "Symptom to listen for: 'who signed off on this?' is the first question after every incident.",
                ]),
                ("BUREAUCRATIC - rule-oriented", [
                    "Information travels, but only through official channels and at the speed of the process.",
                    "Messengers are tolerated but not welcomed; responsibility is narrow - 'not my department'.",
                    "Failure leads to justice-seeking and new procedure; novelty creates problems for the rulebook.",
                    "Symptom to listen for: after every incident a new approval step appears and nothing gets faster.",
                ]),
                ("GENERATIVE - performance-oriented", [
                    "Information is actively sought because the mission depends on it; bad news is treated as valuable.",
                    "Messengers are trained and thanked; cross-boundary collaboration is rewarded, not policed.",
                    "Risks are shared; failure leads to inquiry into the system; novelty is implemented and evaluated.",
                    "Symptom to listen for: 'what in our system made that outcome likely?' asked before anyone is named.",
                ]),
            ],
            "notes": "Ron Westrum was studying safety-critical domains - aviation, healthcare - when he classified organisational cultures by how they handle information, particularly unwelcome information. Give the room the three-column model and let them place their own organisation privately; almost everyone lands in bureaucratic, which is worth normalising - most large organisations are bureaucratic by default and the move to generative is a deliberate act. The most useful single line: culture is what happens when bad news arrives. Everything else is decoration. Draw out the bureaucratic failure mode carefully because it looks responsible: after each incident a new approval step is added, so the process grows monotonically, delivery slows, and the actual causes - missing tests, poor observability, brittle deploys - remain untouched. That organisation is optimising for defensibility, not reliability. Note also that DORA's research operationalised Westrum with a small survey instrument, which means culture here is not a vibe - it is measured with questions, and it predicts delivery performance and organisational performance statistically. That fact is the participants' best lever with sceptical leadership: culture work has a measurable return."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Moving Your Culture One Level",
            "sections": [
                ("The five questions to score (privately, then discuss)", [
                    "1. Is information actively sought here, or do you have to go looking for it yourself?",
                    "2. Are messengers who bring bad news thanked, tolerated, or punished?",
                    "3. Are responsibilities shared across boundaries, or does each group defend its own perimeter?",
                    "4. Is cross-functional collaboration rewarded in practice - promotions, praise, time?",
                    "5. After failure, does the organisation ask what happened, or who did it?",
                ]),
                ("Behaviours that move the needle fastest (leaders first)", [
                    "Respond to the first bad-news report of the week with visible gratitude, in public, every single time.",
                    "Say 'I do not know' and 'I was wrong' in front of the team - permission is granted by example.",
                    "Ban the question 'who did it' in incident reviews and replace it with 'what made that seem correct?'",
                    "Publish incident reviews unedited and unrestricted; secrecy signals that failure is shameful.",
                    "Fund the fix: an action item without capacity assigned teaches that reporting changes nothing.",
                ]),
                ("What generative culture buys you technically", [
                    "Accurate incident data - so the postmortems describe how the system really fails.",
                    "Early warnings - near-misses reported before they become outages.",
                    "Honest estimates and honest status - because 'this is late' is safe to say.",
                    "Working feedback loops: tests, scans and alerts only help if people act on what they say.",
                ]),
            ],
            "notes": "EXERCISE (10 minutes, described in instructor/theory-demos.md): each participant scores the five questions privately on paper, 1-5. Then pairs discuss ONE concrete behaviour that would move ONE answer by one point - concrete meaning a specific person doing a specific thing in a specific meeting, not 'improve communication'. Collect three or four out loud. Facilitation warnings: keep the scoring private (people will not honestly score their own manager's organisation aloud), and if a participant's context is genuinely pathological, do not let the room turn it into a pile-on - redirect to what is within their control, usually their own team's micro-culture, which is often measurably better than the organisation's. That is the encouraging finding worth stating: team-level culture is substantially shapeable by team-level behaviour, especially by whoever runs the meetings. Make the closing link explicit to the technical modules: every automated feedback mechanism this course installs is a machine for generating bad news at speed. In a pathological culture those machines get disabled - flaky tests deleted, alerts muted, scanners set to exit-code 0. Culture is not adjacent to the toolchain, it decides whether the toolchain functions."
        },
    ],

    "Psychological Safety - the Foundation Layer": [
        {
            "type": "detail",
            "title": "Deep Dive: The Evidence and the Common Misreading",
            "sections": [
                ("What it is - and what it is not", [
                    "Edmondson: a shared belief that the team is safe for interpersonal risk-taking.",
                    "The risks in question: asking a basic question, admitting a mistake, disagreeing, saying 'this is late'.",
                    "It is NOT niceness, comfort, or an absence of conflict - safe teams argue more, not less.",
                    "It is NOT lower standards: safety plus high standards is the learning zone; safety alone is the comfort zone.",
                ]),
                ("The hospital study that inverted the result", [
                    "Edmondson expected better nursing teams to report FEWER medication errors; the data showed more.",
                    "Cause: better teams were safe enough to report errors, so their data reflected reality.",
                    "The unsafe teams' low numbers measured silence, not quality - the errors happened, unrecorded.",
                    "Transfer this to your incident data: a suspiciously quiet system is a reporting problem until proven otherwise.",
                ]),
                ("Google's Project Aristotle (2012-2015)", [
                    "Studied 180+ teams expecting the answer to be about WHO was on the team - seniority, IQ, tenure.",
                    "The strongest differentiator was psychological safety: how the team behaved together.",
                    "Supporting factors: dependability, structure and clarity, meaning, impact.",
                    "Implication for hiring: team behaviour beats individual brilliance; a strong culture makes average teams good.",
                ]),
            ],
            "notes": "Handle the two misreadings before they take root, because both are common and both discredit the concept. First, psychological safety is not comfort or politeness - Edmondson's own two-by-two puts safety on one axis and performance standards on the other: high safety with low standards is the comfort zone, low safety with high standards is the anxiety zone, and the learning zone requires both high. Teams with genuine safety have MORE technical disagreement, not less, because dissent is cheap. Second, it is not an excuse for tolerating poor performance - accountability still exists; what changes is that failure produces investigation rather than punishment. The hospital study is the most persuasive thing you can tell a sceptical operations manager: reported error rates measure reporting culture at least as much as they measure error rates, so 'our incident numbers are low' may be excellent news or terrible news, and you cannot tell which without knowing whether people feel safe reporting. Ask the room for the tell-tale: has anyone ever fixed something quietly rather than raising it because raising it would be worse than the bug? Almost every hand goes up eventually, and that admission is the whole argument."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Building Safety, and What It Unlocks",
            "sections": [
                ("Built in small moments - the leader's behaviour is the mechanism", [
                    "How the senior person reacts to the FIRST naive question sets the price of questions for everyone.",
                    "Frame the work as a learning problem, not an execution problem: 'this is new; we will get things wrong'.",
                    "Model fallibility out loud: 'I missed that', 'I do not know', 'good catch, that was my bug'.",
                    "Invite participation by name and with real questions: 'what are we not seeing here?'",
                    "Respond productively to bad news every time - one public punishment undoes months of invitation.",
                ]),
                ("Practices that make it structural, not personal", [
                    "Blameless postmortem format with counterfactuals banned (see the Module 2 postmortem slides).",
                    "Code review norms: comment on the code, ask questions rather than issue verdicts, agreed turnaround times.",
                    "Rotate who speaks first in reviews and retros - juniors before seniors, so anchoring does not silence.",
                    "On-call handoffs and load treated as a team health metric, with fatigue openly discussed.",
                ]),
                ("What it unlocks - the operational payoff", [
                    "Honest estimates and honest status reports, so plans reflect reality and slip early instead of late.",
                    "Real postmortems, so the same outage does not recur three times under different names.",
                    "Near-miss reporting - the cheapest safety data any organisation can get.",
                    "Working feedback loops: people investigate red builds and alerts instead of routing around them.",
                    "Retention and on-call sustainability - the least measured, most expensive consequence of unsafe teams.",
                ]),
            ],
            "notes": "Give participants actionable moves rather than a value statement, because most of them cannot change their organisation but every one of them can change their own meetings. The highest-leverage behaviour is the reaction to the first naive question in a room: answer it seriously and thank the asker, and the price of questions drops for everyone present; sigh or answer curtly, and the room silently learns to stay quiet - and the next thing withheld may be a production concern rather than a question. Leaders modelling fallibility is the second lever, and it is nearly free. Then make it structural, because safety that depends on one good manager evaporates on their next promotion: the formats and norms on this slide encode the behaviour into how the team works. Close with the operational payoff framed in the language of managers - fewer repeat incidents, earlier warning, more accurate plans, lower attrition and healthier on-call. That is how a participant sells this in an organisation where 'psychological safety' would be dismissed as HR vocabulary."
        },
    ],

    "Conway's Law - Architecture Mirrors Communication": [
        {
            "type": "detail",
            "title": "Deep Dive: The Mechanism, With Examples You Will Recognise",
            "sections": [
                ("Why the law holds (the mechanism, not the mysticism)", [
                    "Designing an interface between two components requires the authors to communicate.",
                    "Where communication is cheap, interfaces stay fluid and are renegotiated freely.",
                    "Where it is expensive - different teams, buildings, time zones, budgets - interfaces freeze and thicken.",
                    "Conway 1968, 'How Do Committees Invent?': four teams building a compiler produced a four-pass compiler.",
                ]),
                ("Org structures and the architectures they produce", [
                    "A separate DBA team -> every schema change queues behind tickets; apps grow logic to avoid the queue.",
                    "A separate QA department -> testing becomes a phase at the end, and quality becomes someone else's job.",
                    "Frontend and backend split by layer -> chatty, over-negotiated internal APIs and cross-team release trains.",
                    "A central 'integration' team -> a strategic ESB that everything must pass through, and a single bottleneck.",
                    "Offshore/onshore time-zone split -> batch handoffs and interfaces designed for a 12-hour round trip.",
                ]),
                ("The seams show up as outages and delays", [
                    "Every org boundary becomes a queue in the delivery flow and a fragile seam in the runtime.",
                    "Incidents cluster at the boundaries, because nobody owns the interaction end to end.",
                    "Change that crosses three teams needs three backlogs to agree - so it takes a quarter, not a day.",
                ]),
            ],
            "notes": "Participants tend to hear Conway's Law as a witty aphorism; make them feel it as a mechanism they can predict with. The causal chain is simple: an interface requires agreement, agreement requires communication, and communication cost is set by organisational distance - so the cheapest-to-agree boundaries are where the architecture will split. Then run the recognition exercise: read out the org-structure examples and watch the room nod. Push it further by asking a participant to describe an architectural oddity in their system that nobody can justify technically ('why does the pricing logic live in the reporting service?'), and then ask what the org chart looked like when it was built. The answer is almost always an organisational story - a team that owned that codebase, a manager who had capacity, a contractor whose scope ended. That exercise converts the law from trivia into a diagnostic. Also name the inverse consequence for Module 6: teams that cannot deploy independently will not produce independently deployable services, no matter how the boxes are drawn on the architecture diagram."
        },
        {
            "type": "detail",
            "title": "Deep Dive: The Reverse Conway Maneuver in Practice",
            "sections": [
                ("The move", [
                    "Decide the architecture you WANT - say, independently deployable services aligned to business domains.",
                    "Then restructure teams and communication paths to match it, and let the law work for you.",
                    "Give each team end-to-end ownership: build, deploy, run, be paged for, and change without asking permission.",
                    "Align team boundaries with domain boundaries (bounded contexts), not with technology layers.",
                ]),
                ("Preconditions - otherwise it fails", [
                    "Each team needs the ability to deploy alone: own pipeline, own environments, own data, own release cadence.",
                    "Interfaces must be explicit and versioned - APIs and events with contracts, not shared database tables.",
                    "The platform must remove the infrastructure cost of independence, or 'independent' means 'each team suffers alone'.",
                    "Team size should stay within a trusted-relationship limit (roughly 7-9) and cognitive load must fit.",
                ]),
                ("Why microservices without org change disappoints", [
                    "Services split, teams unchanged: one team owns twelve services and now suffers distributed-systems pain for free.",
                    "A shared release train across services = a distributed monolith - all the cost, none of the independence.",
                    "Shared database between services keeps the tightest coupling of all, whatever the deployment diagram says.",
                    "The honest test: can one team ship a change to production today without another team's calendar?",
                ]),
            ],
            "notes": "The reverse Conway maneuver, popularised by Team Topologies, flips the law from a constraint into a design tool - and it is the single most practical thing in this module for anyone with organisational influence. Be precise about preconditions, because half-done versions are worse than doing nothing: teams reorganised around domains but still sharing a database, a release train or a single deployment gatekeeper get all the coordination cost of the new structure and none of the autonomy. Give the room the one-question test on the slide - can one team ship today without another team's calendar? - and let them answer for their own system. It usually reveals the real architecture, which is rarely the one on the wall. Connect this forward twice: Module 6 argues that microservice boundaries should be business-domain boundaries (bounded contexts from Domain-Driven Design), which is Conway's Law applied deliberately; and Module 9 shows the platform team's role in this - independence only becomes affordable when every team does not have to rebuild pipelines, environments and observability for themselves."
        },
    ],

    "Communication Strategies That Scale": [
        {
            "type": "detail",
            "title": "Deep Dive: Written, Asynchronous, Durable",
            "sections": [
                ("Why async-written beats synchronous-verbal at scale", [
                    "A decision made in a meeting reaches the attendees; a decision written down reaches everyone, forever.",
                    "Writing forces precision: vague thinking survives conversation but dies in a paragraph.",
                    "Time zones, part-time colleagues and future joiners can all read; none of them can attend a past meeting.",
                    "Meetings are still right for: disagreement, ambiguity, trust-building, and anything emotionally loaded.",
                    "Rule of thumb: if the outcome must persist, it must be written - the meeting produces the document.",
                ]),
                ("ADRs - Architecture Decision Records", [
                    "One short numbered file per significant decision, in the repo, next to the code it governs.",
                    "Sections: context, options considered, decision, status, consequences. One page, not a design document.",
                    "The value is WHY, not what - code shows what was done; only the ADR shows what was rejected and why.",
                    "Immutable: decisions are superseded by a new ADR, never edited into a comfortable retelling.",
                    "Payoff two years later: 'why a queue and not a call?' has an answer, and onboarding reads as a story.",
                ]),
                ("Documentation is a product", [
                    "It has users, a maintainer, a review process and a lifecycle - not a wiki page written once in 2019.",
                    "Measure it by outcomes: can a new engineer complete the golden path unaided, in one sitting?",
                    "Docs live in Git alongside the thing they describe, so a PR that changes behaviour changes the docs.",
                    "Platform rule (Module 9): if the platform's docs are bad, the platform is bad - the docs ARE the interface.",
                ]),
            ],
            "notes": "Make ADRs concrete by showing the shape rather than describing it - a numbered markdown file, five headings, one page. Emphasise the discipline that makes them valuable: capture the options you rejected and the reason, because the expensive question later is never 'what did we build' (the code answers that) but 'did they consider X, and if so why not?' Without ADRs, teams re-litigate settled decisions annually and revert them without knowing why they were made. Emphasise immutability: an ADR is a historical record; when the decision changes you write ADR-0042 superseding ADR-0017, and the pair together tell the truth about how thinking evolved. On async-first, do not overstate it - some things genuinely need a room, and the failure mode of async-everything is unresolved conflict and cold, slow disagreement. The workable rule is on the slide: use the meeting for the argument, use the document for the decision. On documentation-as-product, the participants will meet this again in Module 9 as a measured platform KPI, so plant it here: the platform's docs are not a description of the interface, they ARE the interface, and the honest metric is whether an unaided newcomer succeeds."
        },
        {
            "type": "detail",
            "title": "Deep Dive: ChatOps and Working Agreements",
            "sections": [
                ("ChatOps - operations in the open", [
                    "Deploys, alerts, pipeline results and incident timelines all land in shared, searchable channels.",
                    "Effects: shared situational awareness, passive learning for newcomers, and an automatic audit trail.",
                    "During an incident the channel IS the timeline - the postmortem reconstructs itself from timestamps.",
                    "Guardrails: sensitive data never in chat; bots act with least privilege; channel per incident, not per person.",
                    "Anti-pattern: private DMs for operational decisions - the knowledge dies with the conversation.",
                ]),
                ("Working agreements - the team's explicit norms", [
                    "Examples: PRs reviewed within 4 working hours; WIP limit of 2; no deploys after 16:00 on Friday.",
                    "More examples: on-call handoff includes a written summary; every incident gets a postmortem within 5 days.",
                    "Written down, visible, and revisited in retrospectives - a norm nobody can quote is not a norm.",
                    "Agreed by the team, not imposed: the point is that expectations become explicit and negotiable.",
                ]),
                ("Applying this during the labs", [
                    "Every artifact you produce in this course is written and versioned: pipelines, infrastructure, policy, runbooks.",
                    "That is a communication strategy, not just tooling - Git history is the durable record of what changed and why.",
                    "Commit messages and PR descriptions are documentation with the best possible retention rate.",
                ]),
            ],
            "notes": "ChatOps is easy to demonstrate and easy to get wrong. The genuine benefit is that operational reality becomes ambient: a newcomer who sits in the channel for two weeks absorbs how deploys go, what breaks, who to ask, and what normal looks like - none of which is in any document. It also produces an incident timeline for free, which matters directly for the blameless postmortem practice a few slides later, because arguing about what happened when is the most tedious and least useful part of an incident review. Name the guardrails explicitly since organisations have got this wrong publicly: no secrets in chat, bots with narrowly scoped permissions, and destructive actions requiring confirmation. On working agreements, the trick is to keep them few, specific and testable - three agreements a team actually follows beat fifteen aspirational ones. Recommend the retrospective as the place to add and delete them. Finally, tie it back to the labs: participants may not notice that writing everything into Git is a communication practice as much as an engineering one, so point at it when you get to Terraform and pipeline files - those files answer 'what is our infrastructure and why' for everyone in the organisation, permanently."
        },
    ],

    "Breaking Silos Without Breaking the Org": [
        {
            "type": "detail",
            "title": "Deep Dive: Change the Incentives, Not the Slogans",
            "sections": [
                ("Why 'collaborate more' fails", [
                    "Silos exist for real reasons: specialisation, clear accountability, career paths, budget ownership.",
                    "Exhortation cannot beat an appraisal form - people follow what they are measured and paid on.",
                    "So change the structures: shared goals, shared consequences, shared interfaces. Behaviour follows.",
                ]),
                ("SHARED GOALS - measure both groups on the same outcomes", [
                    "Give Dev and Ops the same scoreboard: lead time and deployment frequency AND failure rate and restore time.",
                    "Now neither side can win by hurting the other - speed with breakage fails, stability with paralysis fails.",
                    "Add joint service-level objectives so reliability is a shared budget rather than a shared argument (Module 8).",
                ]),
                ("SHARED PAIN - developers on call for their own services", [
                    "The feedback loop with teeth: whoever is paged by an unhandled exception designs differently afterwards.",
                    "Introduce it fairly: adequate runbooks, real dashboards, working alerts, sane rotation, time to fix causes.",
                    "Compensate and cap it - on-call is work; unpaid, unbounded rotations are how good engineers leave.",
                    "Ops does not disappear: their expertise shifts to platform, tooling and reliability engineering.",
                ]),
            ],
            "notes": "The framing to hold onto is that silos are a rational response to how organisations are structured, so the counter-move must also be structural. Shared goals first, because it is the cheapest and most under-used lever: many organisations discover that Dev's bonus and Ops' bonus are literally in opposition, and simply putting the same four DORA numbers on both scorecards changes meeting behaviour within a quarter. Shared pain is the most contentious item on this slide and you should let the room push back on it - participants who have been on badly-run rotations have earned their scepticism. The honest position: developer on-call is one of the strongest quality feedback loops known, AND it is frequently implemented abusively. The conditions on the slide are non-negotiable prerequisites, not nice-to-haves. A useful compromise pattern for organisations easing into it: developers join the rotation in business hours first, or shadow an experienced responder for a cycle, with a hard rule that fixing the causes of pages ranks above feature work in the following sprint - which is what converts pain into improvement rather than into attrition."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Interfaces Between Teams - and the Anti-Pattern",
            "sections": [
                ("EMBEDDED ROTATION - the enabling pattern", [
                    "An ops or platform engineer joins a product team temporarily to build a capability WITH them.",
                    "Explicitly time-boxed with a success criterion: the team is self-sufficient and the engineer leaves.",
                    "Success is measured by their absence being fine - permanent embedding recreates dependency.",
                    "Works both ways: developers rotating into the platform team return as informed, sympathetic users.",
                ]),
                ("INTERNAL OPEN SOURCE (InnerSource)", [
                    "Any team may raise a PR against another team's repository, including the platform's.",
                    "The owning team keeps review and merge rights - contribution without loss of ownership.",
                    "It replaces 'file a ticket and wait a quarter' with 'send the change and get it reviewed'.",
                    "Requires the basics: readable README, contribution guide, tests that run for outsiders, fast review SLA.",
                ]),
                ("THE ANTI-PATTERN: a 'DevOps team' between Dev and Ops", [
                    "It centralises pipelines and environments, so every team's delivery queues behind one team's backlog.",
                    "It is the wall of confusion rebuilt with better tooling - now with two handoffs instead of one.",
                    "The distinguishing test versus a platform team: can teams self-serve, or must they file a ticket and wait?",
                    "Also watch for the rebrand-only version: the sysadmin team renamed, with the same tickets and the same queue.",
                ]),
            ],
            "notes": "Embedded rotation is Team Topologies' facilitating interaction mode, and the discipline that makes it work is the exit criterion - agreed at the start, in writing, with a date. Without it the embedded engineer becomes the team's permanent infrastructure person, the team never learns, and the platform team slowly dissolves into staff augmentation. Mention the reverse direction too: rotating a product developer into the platform team for a quarter produces the best possible platform user research, free. InnerSource is the pressure valve that keeps a platform from becoming a bottleneck as adoption grows - if the golden path needs a new capability, the consuming team can build it and submit it rather than queue for it. Note the preconditions honestly: it only works if the platform repo is genuinely contributable - documented, tested, with a stated review turnaround - which is more work than most platform teams expect. Then land the anti-pattern hard, because it is the most common structural mistake in this whole course and participants may be about to be assigned to one: state the self-service test as the diagnostic, and if the answer is 'they file tickets', the organisation has built a third silo regardless of what the team is called."
        },
    ],

    "Blameless Postmortems and Retrospectives": [
        {
            "type": "detail",
            "title": "Deep Dive: Why Blameless Is Hard-Nosed, Not Soft",
            "sections": [
                ("The argument from information", [
                    "If touching an incident risks punishment, engineers withhold detail - and you lose the only true account.",
                    "You cannot fix what you cannot see; blame is therefore expensive, whatever it does for feelings.",
                    "Aviation learned it first: confidential, non-punitive reporting is why flying became so safe.",
                    "Etsy and Google SRE brought the practice into software; it is now standard at high-performing organisations.",
                ]),
                ("'Human error' is where the investigation starts", [
                    "Nobody comes to work intending to break production - so the action made sense to them at the time.",
                    "Ask: what information did they have? what did the tooling show? what did the docs say? what was normal here?",
                    "Second victim effect: the engineer involved is often the most motivated to fix the system - keep them in the room.",
                    "If one person's mistake can take production down, the SYSTEM has a single point of failure - that is the finding.",
                ]),
                ("Ban counterfactuals - they explain nothing", [
                    "'They should have checked the config' describes an incident that did not happen.",
                    "'We could have caught it in review' is a wish, not a cause - and it stops the inquiry early.",
                    "Replace with: what made not-checking reasonable? (it always had been / the diff was 4000 lines / no validation existed)",
                    "Language test for the facilitator: if a sentence contains 'should have', it is a judgement, not an observation.",
                ]),
            ],
            "notes": "Anchor the practice in self-interest, because 'blameless' sounds like leniency to managers who feel someone must answer for an outage. The argument is informational: the accurate story of how a system failed exists only inside the heads of the people who were there, and punishment guarantees you get a sanitised version. You are choosing between accountability theatre and actually knowing how your system fails. The aviation lineage helps: confidential non-punitive incident reporting transformed flight safety precisely because pilots report near-misses they would otherwise hide. On 'human error', give the room the reframe that changes rooms: if a single engineer's single command could take down production, the interesting fact is not the command - it is that such a command was possible, undetected, unguarded and unrecoverable. That is a system finding with system fixes: validation, staged rollout, permissions, a faster rollback. The counterfactual ban is the most practical facilitation tool on this slide, so give the facilitator a script: when someone says 'should have', ask 'what would have made that the obvious thing to do?' It redirects from judgement to design without shaming the speaker. Participants practise this in Module 8 with the deliberately real five-line format."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Running the Meeting and Closing the Loop",
            "sections": [
                ("The postmortem structure that works", [
                    "Timeline first, from data: alerts, deploys, chat messages, graphs - facts before interpretation.",
                    "Impact in user terms: who was affected, how, for how long - not just 'the service was degraded'.",
                    "Contributing factors, plural: real incidents have several; 'the root cause' is usually an oversimplification.",
                    "What went WELL: detection, rollback, teamwork - name the things worth keeping deliberately.",
                    "Action items: systemic, owned, dated, and placed in the normal backlog like any other work.",
                ]),
                ("Making the actions real", [
                    "Each item names a person, not a team, and a date - unowned actions are decoration.",
                    "Prefer fixes that remove the failure MODE over fixes that remove this instance of it.",
                    "Track completion and report it: an organisation that ignores its own action items has stopped learning.",
                    "If nothing changes, the postmortem was a ritual - and people will start treating it as one.",
                ]),
                ("Retrospectives - the same loop, at team cadence", [
                    "Postmortems learn from failures; retros learn from ordinary work, without waiting for an outage.",
                    "Same discipline required: psychological safety, systemic focus, a small number of owned actions.",
                    "One improvement carried to completion per iteration beats ten discussed and abandoned.",
                    "Feed the flow metrics into it: what waited longest this sprint, and what would remove that wait?",
                ]),
            ],
            "notes": "Give participants the running order because that is what they need on their first attempt: facts, impact, contributing factors, what went well, actions. Two facilitation points make the difference between a useful hour and a defensive one. First, build the timeline from artefacts - alerts, deploy logs, chat history, graphs - before anyone narrates from memory; memory reconstructs incidents to make the narrator look reasonable, and artefacts do not. Second, insist on 'contributing factors' rather than 'the root cause': complex systems fail from combinations - a latent bug plus a config change plus an alert that did not fire plus a runbook that was out of date - and the search for a single cause usually stops at the last human who touched it. Include 'what went well' honestly; teams that only catalogue failures burn out on their own reviews, and knowing that rollback worked in 90 seconds is genuinely actionable information. Then push hardest on the action items, because this is where most organisations fail: named owner, date, tracked in the same backlog as feature work, reported on. Postmortems whose actions never ship train the organisation that reporting incidents accomplishes nothing, which is how you quietly return to a pathological culture with excellent documentation."
        },
    ],

    # ----------------------------------------------------- Module 3 topics
    "The DevOps Toolchain - Categories, Not Brands": [
        {
            "type": "detail",
            "title": "Deep Dive: The Toolchain by Job to Be Done (1/2)",
            "sections": [
                ("SOURCE CONTROL - the foundation everything else assumes", [
                    "Job: one auditable history of every change, with branching, review and rollback.",
                    "Git won; the choice left is the forge - GitHub, GitLab, Bitbucket, Gitea - and its review and CI integration.",
                    "Everything downstream keys off it: pipelines trigger on commits, GitOps reconciles to a commit, audits cite commits.",
                    "Rule for the course: if it is not in Git, it does not exist - config, policy, infrastructure, docs, runbooks.",
                ]),
                ("CI/CD ENGINES - run work in response to events", [
                    "Job: on every commit, build, test, scan, and promote an artifact through environments.",
                    "GitHub Actions / GitLab CI: tightly coupled to the forge, YAML pipelines, hosted or self-hosted runners.",
                    "Jenkins: maximum flexibility and plugins, at the cost of operating a server that becomes a pet.",
                    "Tekton / Argo Workflows: pipelines as Kubernetes custom resources - cloud-native, in-cluster, scalable.",
                    "Choose on hosting model and maintenance burden first; syntax is the smallest difference between them.",
                ]),
                ("ARTIFACT REGISTRIES - the promotion boundary", [
                    "Job: store the immutable build output that gets promoted from staging to production unchanged.",
                    "Container images (GHCR, Docker Hub, ECR), packages (npm, PyPI, Maven), charts and modules.",
                    "Also the natural place for supply-chain controls: immutable tags, signatures, provenance, retention.",
                    "If the pipeline rebuilds per environment instead of promoting one artifact, the registry is doing nothing for you.",
                ]),
            ],
            "notes": "The purpose of these two slides is to give participants a MAP they can use for years, because the specific brands will rotate and the categories will not. Teach it as jobs-to-be-done: name the job, then a few representative tools, then the one property that actually differentiates them. Two points worth dwelling on. First, source control as the substrate: nearly every practice in this course is expressed as 'a file in Git plus something that reacts to it', which is why 'if it is not in Git it does not exist' is a workable law rather than a slogan. Second, the artifact registry is the piece juniors overlook - it is the physical embodiment of build-once-promote-many, and Module 5 will insist on it. A good room exercise here (15 minutes, and the outline's toolchain-mapping activity): have each participant draw the six category boxes and write in what their organisation actually uses, including 'nothing' and 'a person does it manually'. The empty boxes are their backlog; the boxes with three different answers are their standardisation opportunity, and both feed Module 9's platform canvas."
        },
        {
            "type": "detail",
            "title": "Deep Dive: The Toolchain by Job to Be Done (2/2)",
            "sections": [
                ("IaC AND CONFIGURATION MANAGEMENT - two different jobs", [
                    "Provisioning (Terraform/OpenTofu, Pulumi, CloudFormation): make infrastructure EXIST, declaratively.",
                    "Configuration management (Ansible, Chef, Puppet, Salt): make existing machines CORRECT and keep them so.",
                    "Composition in practice: Terraform creates the VM, Ansible or a baked image configures it (Module 4).",
                    "Containers absorbed much of the second job - a Dockerfile is configuration applied at build time.",
                ]),
                ("RUNTIME AND SECRETS", [
                    "Runtime: Docker (single host), Kubernetes (scheduling, self-healing, rollout as APIs), serverless (no servers to run).",
                    "The runtime choice sets your operational model - do not adopt Kubernetes for three services and one team.",
                    "Secrets: Vault, cloud KMS/Secrets Manager, SOPS or Sealed Secrets for Git-stored encrypted values.",
                    "Non-negotiables: no secrets in repos or images, short-lived credentials, rotation, access audited.",
                ]),
                ("OBSERVABILITY AND INCIDENT RESPONSE", [
                    "Metrics (Prometheus), dashboards (Grafana), logs (Loki, ELK), traces and instrumentation (OpenTelemetry).",
                    "OpenTelemetry is the important bet: vendor-neutral instrumentation, so the backend becomes swappable.",
                    "Commercial all-in-ones (Datadog, New Relic, Dynatrace) trade cost for integration and less operating burden.",
                    "Incident response (PagerDuty, Opsgenie, Grafana OnCall): routing, escalation, schedules - the human side of the loop.",
                ]),
            ],
            "notes": "Continue the mapping and add the judgement calls the categories hide. On IaC versus config management, do not let the room believe one replaced the other - they answer different questions, and the modern pattern is provisioning plus immutable images, with config management still essential wherever long-lived mutable machines exist (VM estates, bare metal, network gear, Windows fleets). On runtime, say the unpopular thing clearly: Kubernetes is the right answer at a certain scale and organisational maturity and an expensive mistake below it; a small team running four services is usually better served by containers on a managed platform. That honesty buys credibility for the rest of the course, and it is exactly the sort of judgement the platform team is supposed to make on behalf of everyone else. On secrets, state the non-negotiables as a checklist because it is the most common audit finding in real pipelines. On observability, flag OpenTelemetry as the strategically important choice: instrumentation is the expensive, invasive part, so instrumenting once in a vendor-neutral way is what keeps the backend decision reversible - which is directly the 'exit cost' principle on the next slide."
        },
    ],

    "Principles for Choosing Tools": [
        {
            "type": "detail",
            "title": "Deep Dive: Four Properties That Predict Regret",
            "sections": [
                ("DECLARATIVE over imperative", [
                    "Declarative = describe the destination; the tool computes the path and can re-compute it after drift.",
                    "This one property gives you diffs (terraform plan), reviewable change, policy scanning and drift detection.",
                    "An imperative script can only be run and hoped about - it cannot answer 'what would this change?'",
                    "Test when evaluating: can I see a dry-run diff, and can that diff be attached to a pull request?",
                ]),
                ("EVERYTHING AS CODE, EVERYTHING IN GIT", [
                    "Config that cannot be versioned, reviewed or reverted is risk with a friendly GUI.",
                    "Git gives you, for free: history, blame, review, approval records, rollback, and an audit trail auditors accept.",
                    "It also gives newcomers a readable account of how the system got this way.",
                    "Test when evaluating: is the tool's entire configuration expressible as files I can commit?",
                ]),
                ("API-FIRST AND COMPOSABLE", [
                    "If a step requires a human in a GUI, that human eventually IS the release process - and their holiday is an outage.",
                    "Prefer tools with a documented API/CLI, sane exit codes, and machine-readable output (JSON, SARIF, JUnit).",
                    "Composability beats feature breadth: small tools that pipe together outlive suites that own everything.",
                    "Test when evaluating: can I drive 100% of it from a pipeline with no clicks?",
                ]),
            ],
            "notes": "Frame this as a purchasing checklist participants can literally take into a vendor meeting, because the alternative - choosing on feature lists and demos - is how organisations end up with tooling they cannot automate. The declarative property is the highest-value single filter and it is worth explaining why: only a tool that knows the desired state can tell you the difference between desired and actual, and that difference is what makes review, approval, drift detection and reconciliation possible at all. Everything-in-Git is the enabler for the compliance story that Module 7 develops - a pull request with a plan diff and two approvals is stronger evidence than a change-approval-board minute, and increasingly auditors accept it. On API-first, tell the anecdote pattern everyone recognises: the deployment that only Sipho knows how to do, from a console, with a checklist in his head. That is not a people problem to be solved by documentation; it is a tooling choice that made automation impossible. Give the room the four evaluation tests on the slide - they are deliberately phrased as questions to ask a vendor or a proof-of-concept."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Paved Roads and the True Cost of a Tool",
            "sections": [
                ("PAVED ROAD over mandate", [
                    "A mandate produces compliance, resentment and shadow infrastructure built quietly around it.",
                    "A paved road produces adoption because it is genuinely the fastest way to get to production.",
                    "Always leave escape hatches: unusual needs step off the road and accept carrying what the road handled.",
                    "Adoption rate is therefore the honest scoreboard for a platform team (Module 9 makes it a KPI).",
                ]),
                ("TOTAL COST = licences + integration + operation + training + EXIT", [
                    "Licences are the visible, smallest and most negotiated part - and the least predictive of regret.",
                    "Integration: wiring into identity, secrets, pipelines, registries, monitoring, cost reporting.",
                    "Operation: who upgrades it, patches it, restores it, and carries the pager when it is down at 09:00?",
                    "Training and cognitive load: every tool is a thing every engineer must learn - count it as a real cost.",
                    "EXIT cost: how much of your data, config and workflow would you lose if you had to leave in two years?",
                ]),
                ("Practical selection habits", [
                    "Prefer boring, widely-adopted tools with a hiring pool and an answer for every error message.",
                    "Standardise deliberately: two CI engines is a tax, five is a tax with interest and no benefit.",
                    "Run a time-boxed proof of concept with real workloads and a written decision record (ADR) at the end.",
                    "Ask 'what problem is this solving, and how will we know it worked?' before any evaluation starts.",
                ]),
            ],
            "notes": "The paved-road principle is the bridge between this module and the platform half of the course, so state the psychology behind it: engineers route around mandates, and the routing is invisible until an incident exposes it. Roads earn traffic. On total cost, walk the five components with a concrete example the room can price - adopting a new observability vendor is not the licence; it is instrumentation work across every service, dashboards rebuilt, alert rules migrated, engineers retrained, and two years later a migration project if you leave. Exit cost is the one nobody estimates and the one that hurts, which is exactly why OpenTelemetry mattered on the previous slide - it makes the expensive part portable. Finish with the selection habits, especially 'choose boring technology': widely-adopted tools come with an enormous free asset - every error message you will hit is already answered somewhere, and you can hire people who already know it. If time allows, ask the room for a tool they regret adopting and which of the five cost components they under-estimated; the answer is almost never licences."
        },
    ],

    "Automation and Orchestration Platforms": [
        {
            "type": "detail",
            "title": "Deep Dive: Two Layers People Conflate",
            "sections": [
                ("LAYER 1 - delivery automation (CI/CD engines)", [
                    "Job: run jobs in response to code events, and stop the line when a job fails.",
                    "SaaS runners (GitHub Actions, GitLab SaaS): no runner fleet to operate; watch minutes cost and egress.",
                    "Self-managed (Jenkins, self-hosted runners): full control, private network access - and you own the upgrades.",
                    "In-cluster (Tekton, Argo Workflows): pipelines are Kubernetes resources - same RBAC, same scaling, same YAML fatigue.",
                    "Decision drivers: where your code and secrets may run, who operates it, and how it reaches private networks.",
                ]),
                ("LAYER 2 - runtime orchestration (Kubernetes and friends)", [
                    "Job: keep the right things running in the right numbers, and change them safely.",
                    "Kubernetes' real contribution: scheduling, self-healing, scaling and rollout exposed as declarative APIs.",
                    "Because they are APIs, everything above them can be automated - operators, controllers, autoscalers, policy.",
                    "Control loop: observe actual state, compare to desired state, act to close the gap. Repeat forever.",
                ]),
                ("How the layers meet", [
                    "CI produces an immutable artifact; CD changes the desired state of the runtime; the runtime converges.",
                    "That separation is why rollback is 'set the desired state back', not 'undo a series of steps'.",
                    "Keep the boundary clean: build in the pipeline, deploy by declaring state - not by SSH-ing anywhere.",
                ]),
            ],
            "notes": "Participants routinely say 'our CI/CD' and 'our orchestration' as if they were one thing, and untangling the two layers makes the rest of the course easier. Layer one is event-driven job execution and its differentiator is the HOSTING model - who runs the compute, where it can reach, and who patches it - not the YAML syntax; ask the room who operates their Jenkins, because there is always one person and they always have opinions. Layer two is a continuously running control loop, and the important conceptual leap is that Kubernetes is not a deployment tool but a reconciliation engine that never stops: you declare intent, controllers keep reality matching it, and self-healing is simply that loop noticing a difference. Module 6 develops this. Make the joining point explicit because it explains the entire modern deployment model: the pipeline's job ends when it has published an immutable artifact and changed a declaration; the runtime's job is to converge on it. Rollback becomes a state change rather than a reverse-engineered undo, which is why elite performers restore service in minutes."
        },
        {
            "type": "detail",
            "title": "Deep Dive: GitOps and Event-Driven Automation",
            "sections": [
                ("GitOps - Git as the source of truth for RUNTIME state", [
                    "The desired state of every environment lives in a Git repository, declaratively.",
                    "An in-cluster agent (Argo CD, Flux) continuously compares cluster reality to that repository.",
                    "Differences are reported and, if configured, corrected automatically - drift heals itself.",
                    "Deployment becomes a merge; rollback becomes a revert; the audit trail is the commit history.",
                ]),
                ("PUSH versus PULL - what pull buys you", [
                    "Push: the pipeline holds cluster credentials and applies changes outward. Simple, and widely used.",
                    "Pull: the agent inside the cluster fetches the desired state - so no cluster credentials leave the cluster.",
                    "Pull adds continuous drift correction: a manual kubectl edit is reverted, not silently kept.",
                    "Pull gives audit for free: what is running is provably what is in the repository, at a known commit.",
                    "Cost: another component to operate, plus discipline - out-of-band changes genuinely stop working.",
                ]),
                ("EVENT-DRIVEN AUTOMATION - controllers instead of humans as glue", [
                    "Webhooks, controllers and operators react to events: a merge, an alert, a new resource, a schedule.",
                    "The pattern generalises the control loop: encode the operational response, do not page a human for it.",
                    "Examples: autoscaling on load, certificate renewal, dependency-update PRs, auto-rollback on SLO burn.",
                    "The test of maturity: how many of your routine operational actions still require a person to notice?",
                ]),
            ],
            "notes": "GitOps is worth precision because the term gets applied to any pipeline that touches Git. The defining properties are: declarative desired state, versioned and immutable in Git, pulled automatically by an agent, and continuously reconciled. The last one is what separates it from 'we run kubectl apply in CI'. Sell the pull model on its two concrete wins - credentials never leave the cluster (a compromised CI runner cannot deploy to production), and drift is corrected rather than accumulated, so the emergency 03:00 kubectl edit that everyone forgets to put back gets reverted by a machine that never forgets. Be honest about the cost: teams must genuinely stop making out-of-band changes, and during an incident that discipline is tested. Then widen to event-driven automation as the general principle behind the whole module: humans are poor glue - slow, expensive, inconsistent, asleep at 03:00 - so encode the routine response and reserve humans for judgement. Close with the maturity question on the slide; it is a good one for participants to take back to their own operations meeting."
        },
    ],

    "This Course's Toolchain (and Why)": [
        {
            "type": "detail",
            "title": "Deep Dive: Why These Tools, and What Transfers",
            "sections": [
                ("Selection rules for every tool in this course", [
                    "Free and open source, no account, no credit card - so every participant can rebuild the labs at home.",
                    "Runs entirely on one Ubuntu 24.04 VM's localhost - no shared infrastructure, no cloud dependency.",
                    "Category-representative: what you learn is the pattern, not the vendor's dialect.",
                    "Installed once by lab-setup/install-ubuntu24.sh and verified by lab-setup/check-environment.sh.",
                ]),
                ("What transfers to your workplace, tool by tool", [
                    "GitHub Actions -> GitLab CI / Azure DevOps / Jenkins: jobs, dependencies, gates, artifacts map one-to-one.",
                    "Docker + Compose -> any container platform: the image contract and the multi-service stack are universal.",
                    "kind + kubectl -> EKS / AKS / GKE: kind serves the real Kubernetes API, so every command transfers unchanged.",
                    "Terraform (docker provider) -> AWS/Azure/GCP: swap the provider block; plan, apply, state and modules are identical.",
                    "Trivy and Conftest/OPA -> any scanner or admission controller: severity triage and policy-as-code are the skills.",
                    "Prometheus + Grafana -> Datadog / Cloud Monitoring: the SLI/SLO reasoning is the part that matters.",
                ]),
                ("The honest answer to 'why not real cloud?'", [
                    "Cloud accounts add cost, IAM setup, quota limits and shared-blast-radius risk to a two-day class.",
                    "None of that teaches the WORKFLOW, which is the transferable skill; localhost teaches it with faster feedback.",
                    "You leave with a package you can re-run for free, which is what makes the second, unaided repetition possible.",
                ]),
            ],
            "notes": "Handle the credibility question directly, because a sceptic in the room is thinking 'this is a toy setup'. The argument has three parts. First, fidelity where it matters: kind runs genuine upstream Kubernetes, so kubectl, manifests, RBAC, probes and rollouts behave exactly as they do on a managed cluster; Terraform's plan/apply/state workflow is provider-independent by design; Trivy's output and triage logic are the same against any registry. Second, feedback speed: a localhost lab has a ten-second cycle and no quota, so participants iterate far more times in two days than a cloud lab would allow, and repetition is what builds skill. Third, ownership: they leave with a package that runs on any Ubuntu machine for free, which is what makes the recommended second unaided run realistic. Say clearly what does NOT transfer, because honesty here is worth more than the claim: cloud IAM, networking, quotas, managed-service specifics and cost management are real skills this course does not teach, and participants should plan to learn them next - the Module 11 next-steps slide names them."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Your Toolchain Map - a 15-Minute Exercise",
            "sections": [
                ("Step 1 - draw your current map (5 min, individually)", [
                    "Draw eight boxes: source control, CI/CD, artifacts, IaC, config mgmt, runtime, secrets, observability.",
                    "Write in what your organisation ACTUALLY uses - including 'nothing' and 'a person does this by hand'.",
                    "Mark any box where two teams use different tools for the same job.",
                ]),
                ("Step 2 - score each box (5 min)", [
                    "Is it declarative? Is its configuration in Git? Can it be driven entirely from a pipeline?",
                    "Who operates it, and what happens if that person is unavailable for two weeks?",
                    "Would a new engineer find it on day one without asking a human?",
                ]),
                ("Step 3 - pick one move (5 min, share with a neighbour)", [
                    "Empty boxes are your gaps; boxes with three answers are your standardisation opportunity.",
                    "Boxes marked 'a person does this' are your automation backlog, ordered by how often the person does it.",
                    "Choose ONE change you could start in your first week back, and name what metric would move if it worked.",
                ]),
            ],
            "notes": "This is the 15-minute toolchain-mapping exercise the module allows for; run it now rather than describing it. Facilitation notes: keep step one strictly individual and honest - the point is the real map, not the architecture diagram from the strategy deck, and the differences between the two are themselves the finding. In step two, the four questions come from the tool-choice principles two slides earlier, so participants are applying the framework rather than opining. In step three, insist on ONE change and on naming the metric, because the failure mode of a mapping exercise is a wish list nobody starts. Collect three or four aloud and note them on the flipchart next to the Module 1 pain points - both lists get reused in Module 9's platform canvas, where they become user needs for a golden path. If the room is from a single organisation, run steps one and two as a group on one shared map instead; the disagreements about what is actually in use are usually the most valuable ten minutes of the module."
        },
    ],

    # ----------------------------------------------------- Module 4 topics
    "The Problem IaC Solves": [
        {
            "type": "detail",
            "title": "Deep Dive: Four Failure Modes of Hand-Built Infrastructure",
            "sections": [
                ("SNOWFLAKE SERVERS - unknowable by construction", [
                    "The true configuration exists only as the accumulated side effects of every hand that ever touched it.",
                    "Nobody can review it, reproduce it, or reason about it - so nobody dares change or reboot it.",
                    "Knowledge lives in individuals; when they leave, the server becomes an artefact to be excavated.",
                    "The tell: a machine with a name, a legend, and an informal rule that only one person may touch it.",
                ]),
                ("CONFIGURATION DRIFT - the slow divergence", [
                    "Environments start identical and diverge with every hotfix, 'temporary' rule and manual tweak.",
                    "Eventually 'it works in staging' predicts nothing, and staging stops being a test of anything.",
                    "Drift is silent: there is no alert for it, because nothing declared what correct was supposed to be.",
                    "IaC makes drift detectable - a plan against reality prints the divergence as a diff.",
                ]),
                ("CLICKOPS AND DISASTER RECOVERY", [
                    "A console change leaves no diff, no review, no reason, no rollback and no audit trail.",
                    "The console is to infrastructure what editing production files over SSH is to source code.",
                    "Without IaC, recovery in a new region is archaeology: reconstruct from memory, tickets and screenshots.",
                    "With IaC it is 'apply the same code, change the region variable' - and you can rehearse it on a Tuesday.",
                ]),
            ],
            "notes": "Ground this in war stories - invite one from the room, because every operations veteran has a snowflake memory and the telling does more than any slide. Then make the deep point: hand-built infrastructure is not merely undocumented, it is UNKNOWABLE, because its state is the sum of every undocumented action ever taken on it. That is why the fear of rebooting is rational. Drift deserves the most time because it is the failure participants live with daily and rarely name: the environments diverge invisibly, and the whole value of a staging environment - that passing there predicts passing in production - quietly evaporates. Note the asymmetry that makes IaC powerful here: drift only becomes visible once something has DECLARED the intended state, which is why plan output is a monitoring tool as much as a change tool. On disaster recovery, give the rehearsal framing that sells IaC to management: with code, recovery is a routine you can practise on a scheduled afternoon; without it, it is an untested plan in a binder, and untested plans fail at exactly the moment they are needed."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Pets vs Cattle, and What IaC Gives You Back",
            "sections": [
                ("PETS vs CATTLE - the mental shift", [
                    "Pets: named, unique, nursed back to health when sick; downtime is a crisis and an all-nighter.",
                    "Cattle: numbered, identical, replaced when sick; failure is routine and handled automatically.",
                    "The shift is not cruelty to servers - it is refusing to keep state and knowledge in a machine's local disk.",
                    "Containers are cattle by default, which is why the discipline came with the cloud-native wave.",
                    "Honest caveat: databases and stateful systems still need care - cattle thinking applies to the compute tier first.",
                ]),
                ("What you get once infrastructure is code", [
                    "Reproducibility: identical environments from one definition, differing only by explicit variables.",
                    "Review: infrastructure change goes through pull request, with a diff a colleague can actually read.",
                    "Rollback: revert the commit, apply - the same recovery model as application code.",
                    "Testing and scanning: policy checks and misconfiguration scanners run before anything exists (Module 7).",
                    "Speed with safety: an environment in minutes, and the same path used for the twentieth as for the first.",
                ]),
                ("What IaC does NOT solve", [
                    "Bad architecture written in HCL is still bad architecture, now reproduced perfectly at scale.",
                    "State files, credentials and blast radius become new things to manage carefully.",
                    "Skills shift rather than vanish: your team now needs to read code and reason about plans.",
                    "Partial adoption is dangerous: manual changes on top of IaC-managed resources cause the worst surprises.",
                ]),
            ],
            "notes": "The pets-and-cattle analogy is well known, so add value by stating what it actually demands: no important state on local disk, no manual configuration after boot, no machine that cannot be destroyed and recreated on a whim. Give the practical test - could you terminate any one instance right now, at random, during business hours, and would anything other than a graph move? Netflix's Chaos Monkey exists to enforce exactly that answer. Include the caveat about stateful systems so the room does not over-apply the metaphor; databases are the classic legitimate pet, and treating them as cattle without careful backup, replication and migration design is how people lose data. On the benefits list, emphasise the governance point that plays well with auditors and change boards: a reviewed pull request containing an exact plan diff, with approval recorded, is stronger evidence of controlled change than a meeting minute. Then be honest about limits - this keeps you credible and pre-empts the disappointment of teams who adopt Terraform and expect their architecture problems to disappear. The last bullet is the operationally important one: mixing manual changes with IaC-managed resources produces the worst of both worlds, which is exactly what drift detection and GitOps reconciliation exist to prevent."
        },
    ],

    "Core Principles: Declarative, Idempotent, Immutable": [
        {
            "type": "detail",
            "title": "Deep Dive: Declarative and Idempotent",
            "sections": [
                ("DECLARATIVE - describe the destination, not the journey", [
                    "Imperative: 'create a network, then start container A, then container B' - one path from one assumed start.",
                    "It breaks whenever reality differs from the assumption, and it can never tell you what it would change.",
                    "Declarative: 'these two containers on this network exist, with these settings' - the tool computes the delta.",
                    "That delta is the whole payoff: plan output, code review of infrastructure, policy checks, drift detection.",
                    "Rule of thumb: if you cannot get a dry-run diff, you are holding an imperative tool.",
                ]),
                ("IDEMPOTENT - applying twice equals applying once", [
                    "Safe to re-run: on a timer, in a pipeline, after a partial failure, or by a nervous engineer at 03:00.",
                    "This is what makes automation trustworthy - convergence rather than accumulation of side effects.",
                    "Counter-example: a shell script that appends a firewall rule adds it again on every run, forever.",
                    "Ansible modules are written to be idempotent for this reason; Terraform gets it from desired-state design.",
                    "Test it in the lab: run terraform apply twice and read 'No changes' - that sentence is the principle working.",
                ]),
                ("Why these two properties enable everything else", [
                    "Reviewable change: a diff that a colleague can approve BEFORE it touches anything real.",
                    "Continuous reconciliation: GitOps agents can re-apply forever precisely because re-applying is safe.",
                    "Automated remediation: drift can be corrected by machine, because correction is just another apply.",
                ]),
            ],
            "notes": "These properties are the module's theoretical heart, so make participants feel the difference rather than memorise definitions. The most convincing demonstration is the one they do in the lab: run terraform apply, then run it again and read 'No changes. Your infrastructure matches the configuration.' That message is only possible because the tool holds a model of desired state and compares it to reality - a script fundamentally cannot say it. Use the firewall-rule counter-example for idempotence because everyone has been bitten by an appending script. Be precise about why the pair matters together: declarative gives you the diff, idempotence makes acting on it safe repeatedly, and together they enable the two most valuable modern practices - reviewing infrastructure change as a diff before it happens, and letting an agent continuously reconcile reality without human involvement. Also note the honest edge: idempotence is a property of well-written resources, not a magic guarantee - provisioners running arbitrary shell commands inside Terraform are the classic way people smuggle imperative, non-idempotent behaviour back in, which is why they are a last resort."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Immutable Infrastructure and Versioned Change",
            "sections": [
                ("IMMUTABLE - replace, never patch in place", [
                    "Mutable: SSH in, patch, restart - and now this machine differs from every other machine, undocumeneted.",
                    "Immutable: build a new artifact (image), deploy it, remove the old one - the change is the artifact.",
                    "Consequences: identical instances, trivial rollback (redeploy the previous image), no configuration archaeology.",
                    "Containers made this the default: you rebuild an image, you do not apt-get upgrade inside a running container.",
                    "Cost: you need a fast, reliable build-and-deploy path - immutability without automation is just slow.",
                ]),
                ("VERSION-CONTROLLED - Git history IS change management", [
                    "Every infrastructure change is a commit: who, what, when, why, reviewed by whom.",
                    "Rollback is revert-and-apply; investigation is git log; approval is the PR record.",
                    "This is the compliance story: an exact diff plus recorded approval beats a change-board minute.",
                    "It is also the onboarding story: the history explains how the estate reached its current shape.",
                ]),
                ("Applying the three properties as a review checklist", [
                    "Can I see the intended end state in a file, without reading a procedure? (declarative)",
                    "Can I run this again safely, right now, twice? (idempotent)",
                    "Does a change produce a new artifact rather than editing a live one? (immutable)",
                    "Is the change a reviewed commit, and could I revert it in one command? (versioned)",
                ]),
            ],
            "notes": "Immutability is the property with the biggest cultural resistance because it contradicts a career's worth of operational instinct - fixing the sick machine is what good operators did. Make the trade explicit: immutability buys uniformity and trivially reversible change, and it charges a fast, dependable build-and-deploy pipeline as the price. That is why this course teaches CI/CD before it teaches Kubernetes rollouts; without the pipeline, immutable infrastructure is just a slower way to make changes. Give the concrete pattern: the golden image or container image is built once, versioned, scanned, promoted unchanged, and replaced wholesale on the next change - which is exactly the build-once-promote-many rule from Module 5. On version control, emphasise that participants can use this as an argument in regulated environments: auditors care about evidence of controlled, reviewed, reversible change, and a pull request containing a plan diff with named approvers is better evidence than most manual processes produce. Finish with the four-question checklist on the slide - it is a genuinely useful review lens for any automation a participant meets afterwards, including tooling they did not write."
        },
    ],

    "Terraform's Mental Model in Five Concepts": [
        {
            "type": "detail",
            "title": "Deep Dive: Providers, Resources, Variables and Outputs",
            "sections": [
                ("PROVIDER - the plugin that speaks one platform's API", [
                    "One workflow, many platforms: docker, aws, azurerm, google, kubernetes, github, cloudflare and hundreds more.",
                    "Declared and version-pinned in required_providers; downloaded by terraform init into .terraform/.",
                    "Our labs use kreuzwerker/docker against the local daemon - same workflow, zero cloud cost.",
                    "Moving to AWS changes the provider block and the resource types; plan, apply, state and modules are unchanged.",
                ]),
                ("RESOURCE - one declared object, plus the dependency graph", [
                    "resource \"docker_container\" \"order\" { ... } declares one object and names it for reference.",
                    "Resources reference each other's attributes, and Terraform DERIVES creation order from those references.",
                    "So you rarely write depends_on - the data flow is the dependency graph.",
                    "Data sources are the read-only sibling: look up something that already exists without owning it.",
                ]),
                ("VARIABLES and OUTPUTS - the module's interface", [
                    "Variables parameterise: environment names, image tags, replica counts, ports - with types and defaults.",
                    "Never put secrets in variable defaults or .tfvars in Git; reference a secrets manager instead.",
                    "Outputs export facts for humans and for other configurations (a URL, an ID, a generated name).",
                    "Together they turn a directory of resources into a reusable component with a documented contract.",
                ]),
            ],
            "notes": "Five concepts cover the overwhelming majority of real Terraform reading, so aim for fluency rather than completeness - participants should be able to open an unfamiliar repository and orient themselves. The provider point is the honest cloud story of this course and it is worth proving rather than asserting: in Workshop 3 have participants open main.tf and identify exactly which lines would change if the target were AWS instead of Docker - it is a small, bounded set, and the discovery is more convincing than any slide. The dependency-graph point is the one that produces genuine 'ah' moments: newcomers assume they must order operations, and the fact that referencing another resource's attribute creates the ordering automatically is what makes Terraform feel declarative in practice. Mention data sources briefly because real codebases are full of them and their distinction from resources - reading versus owning - is a common source of confusion. On variables, plant the secrets warning early and repeat it in the best-practices slide; the most frequent real-world Terraform incident is a credential committed in a .tfvars file."
        },
        {
            "type": "detail",
            "title": "Deep Dive: State and Modules - the Two That Bite",
            "sections": [
                ("STATE - the map between your code and reality", [
                    "It records that resource docker_container.order IS container abc123 in the real world.",
                    "Without it, Terraform could not tell 'update the existing thing' from 'create a second thing'.",
                    "Rules: never hand-edit it; it may contain secrets, so protect it like a credential.",
                    "For teams: remote backend with LOCKING, so two simultaneous applies cannot corrupt it.",
                    "Recovery tools exist for when reality and state diverge: terraform state list/rm/mv, and import for adoption.",
                ]),
                ("MODULE - the reusable, versioned unit", [
                    "A module is a directory of resources with variables in and outputs out - a component with an interface.",
                    "The platform team's product unit: 'the standard service module' encodes networking, tagging, limits and policy.",
                    "Consumers pin a version; improvements ship as a new version, adopted deliberately, not by surprise.",
                    "Design small and composable: a giant root configuration is slow to plan and dangerous to change.",
                    "Blast-radius rule: separate state per environment and per bounded area, so one apply cannot reach everything.",
                ]),
                ("The mental model in one sentence", [
                    "Code declares desire, state records reality, plan is the difference, apply closes it, modules make it reusable.",
                    "Every other Terraform feature you meet later is a variation on those five ideas.",
                ]),
            ],
            "notes": "State is where beginners get hurt, so give it the airtime. Explain what it is with the concrete mapping - a resource address in code to an ID in the real world - and then the consequences fall out naturally: hand-editing it makes Terraform believe things that are not true; losing it makes Terraform think nothing exists and try to create duplicates; sharing it without locking lets two engineers corrupt it simultaneously; and it can contain secrets in plain text, which is why remote state must be encrypted and access-controlled. Mention the recovery commands so participants know a path exists when things go wrong - state list, state rm, state mv, and import for bringing existing hand-built infrastructure under management, which is how most real adoptions begin. Modules are where the platform thread reappears: a versioned module is exactly the 'golden path as a product' idea from Module 9, expressed in Terraform, and the version pin is what lets the platform team improve the default without breaking consumers on a random Tuesday. Close with the one-sentence model on the slide and ask the room to repeat it back - it is the single most useful thing they can carry into Workshop 3."
        },
    ],

    "IaC Best Practices (the Production Checklist)": [
        {
            "type": "detail",
            "title": "Deep Dive: Workflow, State and Versions",
            "sections": [
                ("EVERYTHING THROUGH PULL REQUESTS, WITH PLAN IN CI", [
                    "The pipeline runs fmt, validate, lint and plan on every PR, and posts the plan diff into the review.",
                    "Reviewers approve an exact diff of reality, not an intention - stronger control than any approval meeting.",
                    "Apply runs only from the main branch, from CI, with credentials no human holds locally.",
                    "Nobody applies from a laptop against shared environments - that is how state and reality diverge.",
                ]),
                ("REMOTE STATE WITH LOCKING", [
                    "Shared infrastructure never uses local state - one laptop failure should not lose the map of production.",
                    "Locking serialises applies so two people cannot mutate the same state simultaneously.",
                    "Encrypt at rest, restrict access, enable versioning on the backend so you can recover a previous state.",
                    "Separate state per environment: a plan for staging must be structurally incapable of touching production.",
                ]),
                ("PIN VERSIONS DELIBERATELY, COMMIT THE LOCK FILE", [
                    "Pin provider and module versions; commit .terraform.lock.hcl so every machine resolves identical builds.",
                    "It is the infrastructure equivalent of package-lock.json - reproducible plans, no surprise upgrades in CI.",
                    "Upgrade as a deliberate, reviewed change with its own plan, not as an accident of a runner's cache.",
                ]),
            ],
            "notes": "This is the checklist to photograph, so present it as operational practice rather than opinion, and say which items are non-negotiable in production: PR-plus-plan, remote locked state, and separate state per environment. The plan-in-review point deserves emphasis for anyone in a regulated organisation, because it is a genuine upgrade to their control environment - the reviewer sees the precise resources to be created, changed and destroyed, and the approval is recorded against that exact diff. Watch for the destroy count in the plan; teach participants to read plans defensively, because '3 to destroy' on a production plan is the moment to stop and think, and many real incidents were previewed accurately in a plan nobody read. On state separation, give the blast-radius framing: the goal is that the worst possible mistake in a staging apply cannot reach production, which is a structural guarantee rather than a matter of care. The lock file often gets waved away as detail; connect it to a failure participants recognise - the pipeline that suddenly breaks or, worse, silently produces a different plan because a provider released a new minor version overnight."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Security, Structure and Ownership",
            "sections": [
                ("SCAN INFRASTRUCTURE CODE LIKE APPLICATION CODE", [
                    "trivy config, checkov or tfsec in the pipeline, on every pull request.",
                    "They catch misconfiguration before it exists: public storage, missing encryption, open security groups.",
                    "Also: containers without resource limits, privileged flags, missing tags, unrestricted egress.",
                    "Same report-versus-gate discipline as Module 5 - gate on what a developer can actually fix today.",
                ]),
                ("NO SECRETS IN CODE, OR ANYWHERE STATE CAN SEE", [
                    "No credentials in .tf files, .tfvars, defaults, or committed environment files - assume Git is forever.",
                    "Reference a secrets manager (Vault, cloud secret store) or inject at runtime; keep the value out of state.",
                    "Remember state itself may store resource attributes in plain text - encrypt and restrict the backend.",
                    "Rotate anything that ever touched a repository; deletion from Git history does not undo exposure.",
                ]),
                ("STRUCTURE AND OWNERSHIP", [
                    "Small composable modules over one giant configuration - faster plans, smaller blast radius, easier review.",
                    "Tag/label everything with owner, environment, cost centre and service - untagged resources become orphans.",
                    "CODEOWNERS on infrastructure directories so the right people are required reviewers automatically.",
                    "A documented adoption path for existing hand-built resources: import, verify with a no-change plan, then own it.",
                ]),
            ],
            "notes": "Two of these items prevent the incidents that actually happen. First, IaC scanning: the finding is cheap now and expensive later - a misconfigured bucket caught in a pull request costs a comment, and the same misconfiguration caught by a researcher costs a disclosure process. Apply the report-versus-gate pattern from Module 5 so the gate stays trustworthy: fail on the fixable, report the rest, widen deliberately. Second, secrets - state the rule in its strongest form because the half-version fails: anything committed to a repository must be considered compromised and rotated, regardless of whether the commit was reverted or the history rewritten, because clones, forks, caches and CI logs are outside your control. Tagging looks like bureaucracy until the first cost review or the first orphaned-resource cleanup, so give the concrete payoff: tags are how you answer 'who owns this and can we delete it?' without a meeting. Finally, mention the adoption path, because most participants are not starting from an empty account - terraform import plus a verifying no-change plan is the realistic route from a hand-built estate to a managed one, one resource group at a time."
        },
    ],

    # ----------------------------------------------------- Module 5 topics
    "Continuous Integration - Small Batches, Always Green": [
        {
            "type": "detail",
            "title": "Deep Dive: CI Is a Practice, Not a Server",
            "sections": [
                ("The definition, with its three obligations", [
                    "Every engineer merges to the shared mainline at least daily - integration is continuous, not eventual.",
                    "Every merge is verified automatically: build, unit tests, integration tests, static checks, scans.",
                    "A failing mainline is fixed immediately, ahead of any feature work - the whole team's top priority.",
                    "A build server running week-old feature branches satisfies none of these; it is automation, not CI.",
                ]),
                ("Why BATCH SIZE is the real enemy", [
                    "A 50-line change can be genuinely reviewed, meaningfully tested and reverted in one command.",
                    "A 5000-line merge can only be skimmed - and when it breaks, which of its 40 commits did it?",
                    "Risk grows faster than size: interactions between changes, not the changes themselves, cause surprises.",
                    "Small batches also shrink recovery: rollback discards minutes of work, not a fortnight of it.",
                    "Practical target: pull requests measured in hundreds of lines and hours-to-days of age, not weeks.",
                ]),
                ("Integration debt on long-lived branches", [
                    "Every day unmerged is a day of conflicts accumulating and feedback not arriving.",
                    "The merge at the end is a big-bang release in miniature - the exact pattern DevOps set out to remove.",
                    "Worse, the branch is tested against a mainline that no longer exists by the time it lands.",
                    "The cure is structural: branch for hours, integrate constantly, and hide unfinished work behind flags.",
                ]),
            ],
            "notes": "Open by separating the practice from the tooling, because most organisations that say 'we do CI' mean 'we own a Jenkins'. Give the three obligations as a test participants can apply on Monday: do people merge daily, is every merge verified automatically, and does a red mainline actually stop other work? Most rooms fail the first and third. The batch-size argument is the intellectual centre of the module and connects straight back to the lean thinking in Module 1: risk is super-linear in change size because the danger lives in interactions, so twenty small integrations are structurally safer than one large one even though the total change is identical. Make it concrete with the review point - ask the room what they actually do when a 3000-line pull request appears, and let someone admit they approve it, because everyone does. That admission is the argument. On integration debt, note the subtle failure people miss: a long-lived branch is validated against a mainline that has moved on, so its green build is a claim about a system that no longer exists."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Andon Cord, Trunk-Based Development and Flags",
            "sections": [
                ("A RED MAINLINE IS A STOP-THE-LINE EVENT", [
                    "Toyota's andon cord: any worker may halt the line when quality breaks, and fixing it outranks output.",
                    "In software: nobody merges onto a broken mainline, and the fix takes priority over feature work.",
                    "Fix forward or revert fast - reverting is not failure, it is the cheapest way to restore a known-good line.",
                    "Tolerating red for days is CI theatre: the signal stops meaning anything and people learn to ignore it.",
                    "Protect the signal: flaky tests are a defect to be fixed or quarantined, never routinely re-run until green.",
                ]),
                ("TRUNK-BASED DEVELOPMENT", [
                    "Short-lived branches (hours to a couple of days) merged into one trunk that is always releasable.",
                    "DORA research consistently associates it with higher delivery performance than long-lived branching models.",
                    "It requires the supporting practices: fast reliable tests, small changes, good review turnaround.",
                    "Review turnaround becomes a team commitment - a working agreement, because a slow review forces long branches.",
                ]),
                ("FEATURE FLAGS - integrate always, release selectively", [
                    "Unfinished work ships to production disabled, instead of living on a branch for three weeks.",
                    "Flags also enable canary exposure, per-tenant rollout, and instant kill switches without a deploy.",
                    "They are technical debt with a lifecycle: every flag needs an owner, a purpose and a removal date.",
                    "Left unmanaged, flags multiply into a configuration space nobody can reason about or test.",
                    "Rule of thumb: a release flag lives weeks, not quarters; long-lived flags must be a deliberate decision.",
                ]),
            ],
            "notes": "The andon-cord norm is what makes CI real, and it is a cultural commitment more than a technical one - which is why it belongs in the same course as Module 2. Give the room the diagnostic: how long has your mainline been red for, at worst, in the last year? Answers measured in days mean the team has already learned that red is survivable, and every automated check they own has lost its authority. Flaky tests deserve their own moment because they are the most common way teams lose that authority accidentally: a test that fails randomly teaches engineers to re-run rather than investigate, and once that habit exists it applies to real failures too. On trunk-based development, expect pushback from teams committed to elaborate branching models; the useful framing is not ideological but mechanical - long branches mean delayed feedback and painful merges, and every practice that shortens them helps. Note the dependency on review turnaround, which is why the working-agreements idea from Module 2 reappears here. On feature flags, give the balanced view: they are the key that separates deploy from release (next slide), and they are a real maintenance burden with real incidents attached - unowned flags have caused outages when someone flipped one nobody understood."
        },
    ],

    "Delivery vs Deployment - and Deploy vs Release": [
        {
            "type": "detail",
            "title": "Deep Dive: Four Terms People Use Interchangeably",
            "sections": [
                ("CONTINUOUS DELIVERY - a state of readiness", [
                    "Every commit that passes the pipeline is proven deployable and sits ready as an immutable artifact.",
                    "A human decides WHEN to ship, but never whether it would work - the pipeline already answered that.",
                    "Shipping becomes a business decision available any afternoon, instead of an engineering event.",
                    "This is the right target for most organisations, including regulated ones.",
                ]),
                ("CONTINUOUS DEPLOYMENT - no human in the loop", [
                    "Green pipeline goes to production automatically; the last human decision was the code review.",
                    "Prerequisites: trustworthy tests, real observability, automated rollback, and small changes by default.",
                    "It is a capability, not a virtue - plenty of excellent teams deliberately keep a human gate.",
                    "In GitHub Actions the difference is literally one setting: required reviewers on the production environment.",
                ]),
                ("DEPLOY vs RELEASE - the distinction that unlocks the rest", [
                    "DEPLOY: the bits are running in production. RELEASE: users can actually see the behaviour.",
                    "Separating them turns release into a reversible, low-drama act - flip a flag, shift a percentage.",
                    "It enables dark launches, canaries, per-tenant rollout, kill switches and testing in production safely.",
                    "It also decouples engineering cadence from marketing dates, which removes a whole category of arguments.",
                ]),
            ],
            "notes": "Precision here prevents years of confused meetings, so make participants say the definitions back. The most valuable one commercially is continuous delivery as READINESS: it changes the conversation with the business from 'when can engineering ship?' to 'when do we want it visible?', and that is a shift most product organisations would pay for. Be careful not to present continuous deployment as the superior end state - it is a capability appropriate to certain contexts, and organisations with regulatory approval requirements or very high blast radius reasonably retain a human decision. The deploy-versus-release distinction is the one that most often produces a visible shift in the room: once people see that code can be in production but not exposed, a whole set of previously impossible options appears - testing with real production data and traffic, gradual exposure, instant rollback without a deployment, and dark launching a rewrite alongside the original. Point at the GitHub Actions environment setting as the concrete artefact so the distinction stops being theoretical: participants will see exactly that gate in the capstone."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Build Once, Promote Many - and the Frequency Rule",
            "sections": [
                ("BUILD ONCE, PROMOTE THE SAME ARTIFACT", [
                    "The image tested in staging must be bit-for-bit the image that reaches production - same digest.",
                    "Tag by commit SHA (immutable), not by 'latest' - a moving tag makes deployments unreproducible.",
                    "Rebuilding per environment reintroduces dependency drift: a base image or package can change between builds.",
                    "Environment differences belong in CONFIGURATION injected at runtime, never in separate builds.",
                    "Rollback then means redeploying a previous digest that has already been tested - not rebuilding history.",
                ]),
                ("'IF IT HURTS, DO IT MORE OFTEN'", [
                    "Martin Fowler's rule turns pain into a signal: the painful step is the one to automate next.",
                    "Rare deploys stay manual, undocumented and frightening; frequent deploys force the pain out of the system.",
                    "Frequency also shrinks batch size automatically, which shrinks risk - the two reinforce each other.",
                    "Organisations deploying daily did not begin painless; they began frequent and fixed what hurt each time.",
                    "The same logic applies to restores, failovers, certificate rotations and disaster recovery drills.",
                ]),
                ("How this shows up in the labs", [
                    "The workshop pipeline builds one SHA-tagged image and promotes it - watch the tag flow through the stages.",
                    "The production step sits behind an environment gate: continuous delivery today, deployment by removing it.",
                    "The smoke test after deploy proves the deployed artifact actually serves - a green deploy is not proof.",
                ]),
            ],
            "notes": "Build-once-promote-many is a discipline that sounds obvious and is violated constantly, usually by pipelines that run a docker build in each environment's job. Explain the failure it prevents concretely: two builds from the same commit can differ because a base image was updated, a package index moved, or a transitive dependency published a new patch - so the artifact you tested is not the artifact you shipped, and 'works in staging' becomes unreliable in a way that is very hard to debug. The rule also gives rollback its speed: redeploying a known digest is seconds and carries no build risk. Then the frequency aphorism, which is the cultural core of the module: pain is diagnostic information pointing precisely at the next thing to automate, and the instinct to reduce frequency because deploys hurt is exactly backwards - it preserves the pain and grows the batch. Extend it beyond deploys, because the same reasoning applies to every rare, frightening operation an organisation performs: restores, failovers, key rotations, region evacuations. Anything practised annually is, in practice, untested. Finish by pointing at the workshop artefacts so participants know where to look when they build it."
        },
    ],

    "A Scan Is Not a Gate": [
        {
            "type": "detail",
            "title": "Deep Dive: Report vs Gate, and Gating Without Losing the Room",
            "sections": [
                ("The two-step pattern you will build in Workshop 1", [
                    "REPORT step: scan at HIGH and CRITICAL, print everything, exit 0 - full visibility, build stays green.",
                    "GATE step: scan CRITICAL only, ignore-unfixed, exit 1 - the build genuinely stops.",
                    "Report gives triage data; gate changes behaviour. A scanner with exit 0 alone changes nothing.",
                    "Publish machine-readable output (SARIF/JSON) so findings land in the security dashboard, not only in logs.",
                ]),
                ("GATE ON WHAT A DEVELOPER CAN FIX TODAY", [
                    "Fixable means an upgraded package or base image exists right now - the fix is a version bump.",
                    "Gating on unfixable upstream CVEs blocks all delivery indefinitely and will be bypassed within a week.",
                    "The real cost of a bad gate is not the delay - it is teaching the team that red builds are negotiable.",
                    "Start narrow and widen deliberately: fixable criticals first, then highs, as the backlog actually clears.",
                    "Provide an explicit, audited exception path with an expiry date, or people will invent an unaudited one.",
                ]),
                ("Making findings actionable rather than decorative", [
                    "Every finding needs an owner, a severity that means something locally, and a route to a fix.",
                    "Reduce noise at the source: slim base images (distroless, alpine) shrink the CVE surface dramatically.",
                    "Automate the boring fixes: dependency-update bots turn most findings into a reviewed pull request.",
                    "Track the trend, not the absolute number - is the fixable-critical backlog shrinking week on week?",
                ]),
            ],
            "notes": "This slide describes the single most common security-in-CI failure, so be blunt about it: a scanner wired with exit code 0, described in the audit deck as a gate, producing a report that nobody opens. It creates the appearance of control while changing nothing, which is worse than having no scanner, because the organisation believes it is covered. The two-step pattern is what participants will actually build, and the design intent behind it is worth stating: keep the visibility broad and the enforcement narrow. Then dwell on trust, because it is the part teams get wrong: gates are tolerated only when they are fair and actionable, and the fastest way to destroy the authority of every automated check you own is to block delivery on something the developer cannot fix. Once people learn to bypass one gate, they have learned to bypass gates. Give the exception path as a practical requirement rather than a concession - a documented, time-limited, reviewed exception is how mature organisations keep the gate honest while remaining shippable. Finally, the noise-reduction advice is where the real leverage lives: a slimmer base image can remove dozens of findings at once, which does more for the backlog than any triage meeting."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Your Pipeline Is Supply Chain Too",
            "sections": [
                ("PIN THIRD-PARTY PIPELINE ACTIONS", [
                    "An action referenced as @master runs whatever its author pushes, inside YOUR pipeline, today.",
                    "That code sees your repository, your secrets and your registry credentials - it is a full trust relationship.",
                    "Pin to a released version at minimum; pin to a commit SHA for anything touching secrets or publishing.",
                    "Real incidents have followed exactly this path - a compromised popular action exfiltrating CI secrets.",
                    "Review new actions like dependencies: who maintains it, how many stars is not the question, what does it do?",
                ]),
                ("LEAST-PRIVILEGE PIPELINE TOKENS", [
                    "Default tokens are often far more powerful than any single job needs - frequently write access to the repo.",
                    "Declare permissions explicitly (contents: read) and add only what a job proves it needs.",
                    "Scope secrets to the job and the environment that uses them, never repository-wide by default.",
                    "Prefer short-lived OIDC federation to long-lived static cloud credentials stored as secrets.",
                    "Assume every step can read every secret it is given - so give each step as little as possible.",
                ]),
                ("Other pipeline hygiene worth adopting on day one", [
                    "Never echo secrets; be careful with debug modes and with printing environment variables in logs.",
                    "Treat pull requests from forks as untrusted - do not expose secrets to workflows they can trigger.",
                    "Protect the main branch: required reviews, required status checks, no force pushes.",
                    "Record what you built: image digests, SBOMs and provenance make later questions answerable (Module 7).",
                ]),
            ],
            "notes": "The framing that lands here: your pipeline has production credentials, so it IS production, and everything it executes is code you have chosen to trust. Most teams review application dependencies far more carefully than the third-party actions they wire into their workflows, which is backwards given what those actions can reach. Explain the mechanism plainly - a floating reference like @master or @v3 on a mutable tag means the code executed tomorrow is whatever the maintainer pushes tonight, and if that account is compromised, the attacker's code runs with your secrets. Pinning to a commit SHA removes that class of risk entirely for the cost of a dependency-bot pull request now and then. On permissions, make the point that this is one line of YAML and it is the cheapest security improvement available - most jobs need only read access, and declaring it explicitly means a compromised step cannot push code or publish images. OIDC federation deserves a mention as the strategic direction: short-lived, workload-scoped credentials remove the standing secret entirely. Both patterns are already present in the workshop's workflow file, so point at them when you get there rather than only describing them - participants remember the file they ran."
        },
    ],

    "What the Platform Contributes to CI/CD": [
        {
            "type": "detail",
            "title": "Deep Dive: From Copy-Paste YAML to an Inherited Path",
            "sections": [
                ("The problem without a platform", [
                    "Every team hand-rolls a pipeline; quality varies with whoever happened to write it.",
                    "Security steps are the first thing dropped under deadline pressure, silently and per team.",
                    "Pipeline maintenance becomes distributed toil - the same upgrade performed forty times, badly.",
                    "A fix discovered by one team never reaches the other thirty-nine.",
                ]),
                ("TEMPLATED, REUSABLE PIPELINES", [
                    "Mechanisms: GitHub Actions reusable workflows (workflow_call), GitLab includes, Jenkins shared libraries.",
                    "A consuming team's CI file becomes ten lines that inherit test, build, scan, sign and deploy.",
                    "When the platform improves the scan step, every consumer gets it on their next run - no tickets, no migration.",
                    "Version the templates so consumers can pin and upgrade deliberately, exactly like a library.",
                ]),
                ("SECRETS, RUNNERS, REGISTRIES AND ENVIRONMENTS AS A SERVICE", [
                    "Credentials are injected by the platform via OIDC or a managed secrets store - never pasted into repos.",
                    "Runners, registries and environment definitions are operated once and consumed by everyone.",
                    "Environment promotion, approvals and audit records come with the path rather than being reinvented.",
                    "Result: a team gets production-grade delivery mechanics without employing a delivery expert.",
                ]),
            ],
            "notes": "This slide connects the CI/CD module to the platform thread that Day 2 develops, so make the economics explicit. Without a platform, pipeline work is duplicated across every team and the duplication is not merely wasteful - it is uneven, and the unevenness is invisible until an incident or an audit exposes which team quietly dropped the scanning step in a busy quarter. The reusable-workflow mechanism is the practical answer and it is worth showing the shape: a ten-line workflow file that calls a versioned platform workflow, with a handful of inputs. Emphasise the compounding property, because it is the real argument: an improvement made once by the platform team propagates to every consumer without a migration project, which is the opposite of how copy-pasted pipelines behave. Mention versioning of templates so participants do not swing to the other failure - a platform that changes shared behaviour without warning breaks trust just as fast as no platform at all. Then the services around the pipeline: secrets, runners, registries and environments are exactly the things each team should not be operating, and centralising them is what makes least-privilege and audit achievable at all."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Policy in the Path, and Production on Day One",
            "sections": [
                ("POLICY HOOKS - org rules enforced invisibly", [
                    "The golden path carries the rules: signed images, scanned dependencies, resource limits, required labels.",
                    "Teams comply by using the road, not by reading a standards document and remembering it.",
                    "Backstop at admission: policy re-checked where it is enforceable, so off-road work cannot bypass it (Module 7).",
                    "Compliance evidence becomes a by-product of the pipeline - artifacts, approvals and scans, all recorded.",
                ]),
                ("PRODUCTION ON DAY ONE - the headline metric", [
                    "Time-to-first-deploy for a new service is the platform's clearest product KPI (Module 9 measures it).",
                    "The target experience: scaffold, commit, and a running, monitored, scanned service exists within a day.",
                    "Compare honestly with your own organisation's current answer - most are measured in weeks.",
                    "Every week saved is repeated for every new service, forever - that is where the platform ROI comes from.",
                ]),
                ("Guardrails so the platform does not become the new bottleneck", [
                    "Self-service is the test: if teams file tickets and wait, you have built a silo with better branding.",
                    "Escape hatches are mandatory: unusual services may leave the road and carry the extra weight knowingly.",
                    "InnerSource the platform repos so consuming teams can contribute the capability they need.",
                    "Measure adoption and satisfaction, not mandate compliance - a road nobody chooses is a failed product.",
                ]),
            ],
            "notes": "Policy-in-the-path is the idea that makes security and compliance sustainable, so state it as the design principle it is: the easiest way to do the work should also be the compliant way, because standards documents do not survive a deadline and paved roads do. Note the necessary backstop - enforcement at admission or in the platform itself - since a golden path alone only governs those who use it, which is why Module 7 pairs pipeline policy with admission control. The compliance-as-by-product point is worth spelling out for anyone in a regulated organisation: the pipeline naturally produces the evidence auditors ask for - what was built, from which commit, scanned with what result, approved by whom, deployed when - and producing it automatically is both cheaper and more truthful than assembling it by hand at audit time. Then the day-one metric, which is the most persuasive number a platform team can publish: ask the room what their organisation's current time-to-first-deploy is for a brand new service, and let the answers land. Close on the guardrails, because they are the difference between a platform and a bottleneck, and repeat the self-service test one final time - it is the sentence you most want participants to remember from the platform thread of Day 1."
        },
    ],
}


# ===========================================================================
# DAY 1 - SARB CONTEXT + DIAGRAM SLIDES
# ---------------------------------------------------------------------------
# Same keying as DAY1_DEEP_DIVES: these are appended AFTER the deep dives for
# each topic, so each topic reads: summary -> deep dive(s) -> diagram -> the
# central-bank worked example.
#
# NOTE ON THE EXAMPLES: every SARB scenario below is an ILLUSTRATIVE teaching
# example built from publicly known central-bank functions (settlement, the
# national payment system, supervision returns, currency, published statistics
# and market-sensitive announcements). They are not descriptions of the Bank's
# internal systems, vendors or processes.
# ===========================================================================
DAY1_CONTEXT = {

    "Where DevOps Came From": [
        {
            "type": "diagram",
            "title": "The Wall of Confusion",
            "image": "13-wall-of-confusion",
            "caption": "Two teams behaving rationally under opposing measures - the system is the problem.",
            "notes": "Use the picture to make the incentive argument physical. Point at the two measurement lists and ask the room which of the two they are measured on today - in most institutions the split is real and visible in the KPIs. Then point at the orange arrow: the release crossing the wall is where all the risk concentrates, because it is large, rare, rehearsed nowhere, and handled by people who did not build it. Finally the red arrow back: blame is the only feedback that crosses in the other direction, and it carries no information anyone can act on. Close on the amber panel - the fix is structural (shared measures, shared pipeline, shared pager), not attitudinal."
        },
        {
            "type": "detail",
            "title": "In Context: the Wall Inside a Central Bank",
            "sections": [
                ("Where the wall shows up in a central-bank estate", [
                    "Payments and settlement platforms: changes touch a system the whole banking industry depends on daily.",
                    "Supervisory data (returns submitted by banks): a delayed schema change delays the analysis it feeds.",
                    "Published statistics and market-sensitive releases: timing is fixed, so engineering absorbs all the slack.",
                    "Currency and cash operations: physical logistics with software behind them - failure is visible in branches.",
                ]),
                ("What the pre-2009 pattern looks like here", [
                    "Quarterly or window-bound releases: one large change set, weekend cutover, standby war room.",
                    "The delivery team hands over an install pack; the operations team runs it in an environment it owns alone.",
                    "Every environment differs, so 'it passed in test' does not predict production behaviour.",
                    "After an incident, the reflex is a new approval step - process grows, lead time grows, causes remain.",
                ]),
                ("The honest counter-argument, and the answer", [
                    "'We are systemically important - we cannot deploy casually.' Correct, and unchanged by anything today.",
                    "The claim is narrower: LARGE, RARE changes are the risky ones; small, automated, reversible ones are safer.",
                    "So the goal is not 'deploy fast', it is 'make each change small enough to reason about and undo'.",
                    "Criticality raises the bar for evidence and rollback - it is an argument FOR automation, not against it.",
                ]),
            ],
            "notes": "This is the slide where the room decides whether the course applies to them, so handle the objection head-on and early. Every participant in a central bank knows their systems are systemically important, and they are right to be sceptical of anything that sounds like 'move fast and break things'. Make the distinction explicit: DevOps as taught here is not an argument for less control, it is an argument about the SHAPE of change - many small verified changes with automated evidence and a tested rollback, instead of few large ones with manual evidence and a restore-from-backup plan. Ask the room to name where their own wall sits: between a delivery function and an operations function, between an internal team and a vendor, between two departments that share a system, or between the institution and the industry participants it serves. Capture two or three concrete answers on the flipchart - they get reused in the Module 3 toolchain mapping and again in Module 9's platform canvas. Remind the room that these SARB examples are teaching scenarios built from public information, so nobody should treat them as statements about internal systems, and invite participants to correct them with their own reality - that correction IS the value of the discussion."
        },
    ],

    "What DevOps Is (and Is Not)": [
        {
            "type": "diagram",
            "title": "Where the Lead Time Actually Goes",
            "image": "23-value-stream-wait",
            "caption": "Flow efficiency around 2% - the improvement is in the red boxes, not the green ones.",
            "notes": "Walk the map left to right and let the arithmetic do the work: roughly 15 hours of value-adding effort spread across roughly 27 elapsed days, giving a flow efficiency of about 2%. Then make the point that changes behaviour: pressure is almost always applied to the green boxes ('developers must deliver faster'), which are already the smallest term in the equation. Halving all coding time saves under a day; removing one seven-day queue saves a week. Ask the room to estimate their own numbers roughly - people usually guess their flow efficiency is around 30-40% and are startled when the map lands at single digits. The follow-up question is the useful one: which of these waits exists because of a genuine control requirement, and which exists because of calendars, capacity and habit? Controls can usually be automated into the pipeline (evidence produced continuously); calendars usually cannot be defended once they are visible on a chart like this."
        },
        {
            "type": "detail",
            "title": "In Context: Ownership and Flow at SARB",
            "sections": [
                ("'You build it, you run it' where segregation of duties applies", [
                    "The principle is about FEEDBACK, not about handing production access to everyone who writes code.",
                    "Compatible pattern: the team owns the service's health, alerts, error budget, runbooks and postmortems...",
                    "...while the pipeline (not the person) holds deployment rights - people approve, the machine executes.",
                    "That satisfies segregation of duties AND closes the loop: the builder feels the operational consequence.",
                    "Anti-pattern to avoid: pager without authority - accountability handed over with no ability to fix causes.",
                ]),
                ("Lean thinking on a regulated value stream", [
                    "Little's Law still holds: lead time = WIP / throughput - cutting parallel work shortens delivery, free.",
                    "Batch the CONTROLS, not the changes: run evidence generation continuously, ship the change small.",
                    "Every handoff between department, vendor and operations is a queue - count them before optimising code.",
                    "Waiting for a shared test environment is the classic wait that IaC (Module 4) deletes outright.",
                ]),
                ("Language that travels well inside the institution", [
                    "Say 'change failure rate' and 'time to restore' rather than 'move fast' - they are risk words, and true.",
                    "Say 'evidence produced automatically on every change' rather than 'less governance'.",
                    "Say 'smaller blast radius per change' rather than 'more deploys' - the same fact, heard correctly.",
                ]),
            ],
            "notes": "Two things to land here. First, the segregation-of-duties reconciliation, because it is the most common blocker in supervised institutions and it has a clean answer: modern practice separates the AUTHOR of a change from the EXECUTOR by making the executor a pipeline rather than a person. The developer proposes, a reviewer approves, the automation applies, and every step is logged immutably - which is stronger, not weaker, than a human with production credentials and a checklist. Say plainly that this reading is compatible with typical supervisory expectations around change management, and that participants should validate the specifics with their own risk, audit and compliance colleagues rather than take a trainer's word for it. Second, coach the room on vocabulary. Engineers lose these arguments by using words that sound like recklessness to a risk committee. The third section is deliberately phrased as translations: the same practice, framed in the institution's own risk language, is usually approved rather than resisted. Encourage participants to write their next proposal in that vocabulary and see how differently it is received."
        },
    ],

    "The Three Ways (The Phoenix Project / DevOps Handbook)": [
        {
            "type": "diagram",
            "title": "The Three Ways at a Glance",
            "image": "14-three-ways",
            "caption": "Flow left to right, feedback right to left, learning around the whole loop.",
            "notes": "Use this as the classification exercise rather than a lecture slide. Call out practices at random - code review, canary release, error budget, change advisory board, game day, dependency scanning, on-call rotation - and have the room place each one in a band. Two answers are worth arguing about deliberately. A change advisory board is intended as feedback but usually functions as a queue, so it belongs in the flow band as a constraint; that is a useful, non-confrontational way to discuss it. And a canary release is both flow and feedback, which shows the bands are lenses rather than boxes. Finish with the footnote question: if a practice serves none of the three, why does the institution pay for it? Ask that gently - the point is to examine inherited process, not to attack colleagues who maintain it."
        },
        {
            "type": "detail",
            "title": "In Context: the Three Ways on SARB Work",
            "sections": [
                ("FLOW - what to attack first in a central bank", [
                    "Environment provisioning: if a test environment takes weeks, that queue dwarfs every coding improvement.",
                    "Data for testing: masked, POPIA-compliant test data as a self-service capability removes a standing wait.",
                    "Approval choreography: replace document-based approval with reviewed pull requests carrying plan diffs.",
                    "Vendor handoffs: contracted deliverables that arrive as artefacts, not tickets, keep the stream moving.",
                ]),
                ("FEEDBACK - signals that matter in this setting", [
                    "Automated checks on data-quality rules before supervisory or statistical data is published anywhere.",
                    "Reconciliation and settlement checks running continuously, not only at end of day.",
                    "Availability and latency SLOs on industry-facing services, alerting on burn rate rather than on spikes.",
                    "Security signals: dependency and image scanning, secret detection, and drift alerts on infrastructure.",
                ]),
                ("CONTINUAL LEARNING - practising failure safely", [
                    "Game days on the recovery path: restore a database, fail over a service, rehearse the DR runbook.",
                    "Blameless postmortems feeding a shared, readable archive across departments, not one team's folder.",
                    "Time-boxed technical experiments with a written decision at the end - the same discipline as a proof of concept.",
                    "Publish the learning: an incident understood by one team should immunise every team that shares the pattern.",
                ]),
            ],
            "notes": "Make this the practical bridge between theory and their Monday. For FLOW, the two highest-value targets in most regulated institutions are environments and test data - both are usually multi-week queues, both are solvable with the IaC and containerisation work in Modules 4 and 6, and both unblock everything downstream. Mention POPIA explicitly when discussing test data, because the compliant answer (masked or synthetic data provisioned automatically) is both safer and faster than the common informal alternatives, and that is a rare win-win worth naming. For FEEDBACK, steer the room toward signals tied to the institution's actual obligations - data quality before publication, reconciliation, availability of industry-facing services - rather than generic infrastructure metrics, because those are the failures that matter to the mandate. For LEARNING, the restore drill is the recommendation to push hardest: almost every institution has backups, far fewer have recent evidence of a successful restore under time pressure, and the gap between those two is where disaster-recovery plans fail. Lab 08's game day is a small rehearsal of exactly this."
        },
    ],

    "CALMS - the Five Dimensions of DevOps": [
        {
            "type": "diagram",
            "title": "CALMS - Five Dimensions, Five Failure Modes",
            "image": "15-calms-model",
            "caption": "Score each pillar honestly; the lowest letter is your constraint, not the one you are buying.",
            "notes": "Run the scoring live if time allows: read each letter, ask for a private 1-5, then show of hands per band. The near-universal pattern - Automation highest, Measurement and Sharing lowest - is the diagnosis, and it explains the complaint that tooling investment did not change outcomes. Note the failure-mode boxes are deliberately drawn as the SAME size as the virtues: each pillar fails in a specific, recognisable way, and naming the failure is how a team spots itself on the chart. In a central-bank context, the Culture failure mode on the slide - a fully automated pipeline whose output still waits weeks for an approval meeting - is the one that lands hardest, because it is so common and so measurable."
        },
        {
            "type": "detail",
            "title": "In Context: CALMS Read for a Central Bank",
            "sections": [
                ("What each letter looks like when it is healthy here", [
                    "CULTURE: risk, audit and delivery in the same conversation early, rather than as a late gate.",
                    "AUTOMATION: controls executed and evidenced by machines - the same run produces the change and the proof.",
                    "LEAN: the shortest safe path from approved intent to running change, with queues measured and attacked.",
                    "MEASUREMENT: DORA metrics per value stream, plus availability and data-quality SLOs on public obligations.",
                    "SHARING: one internal catalogue of reusable pipelines, modules and runbooks across departments.",
                ]),
                ("Where regulated institutions typically score lowest", [
                    "MEASUREMENT: change volumes are counted, but lead time and change-failure rate are rarely baselined.",
                    "SHARING: several departments solve the same delivery problem in isolation, with no shared artefacts.",
                    "LEAN: WIP is high because everything is in flight waiting for something else - nothing is finished.",
                    "Automation is usually the strongest letter, which is exactly why more of it changes so little.",
                ]),
                ("A first-quarter plan you could actually run", [
                    "Baseline the four DORA metrics for ONE service - no tooling purchase required, just the numbers.",
                    "Pick the single largest queue from your value-stream map and remove or automate it.",
                    "Publish one blameless postmortem widely enough that another department reads it.",
                    "Re-score CALMS at quarter end and show the trend, not the absolute numbers, to your leadership.",
                ]),
            ],
            "notes": "The value of CALMS in a supervised institution is that it gives engineers a language leadership already understands - a balanced scorecard across five dimensions, with a clear statement that over-investing in one produces no return. Push the Measurement point hardest, because it is both the cheapest to start and the most persuasive: an institution that can state its lead time and change-failure rate per value stream can have an evidence-based conversation about risk appetite, and one that cannot is guessing in both directions - it may be accepting far more risk than it thinks in some places while blocking harmless changes in others. On Sharing, the central-bank angle is strong: departments often have genuinely similar delivery needs (a service, a pipeline, a database, a dashboard, an audit trail), and a shared internal catalogue is exactly the platform argument the course builds toward in Module 9. Keep the first-quarter plan modest and finishable - the failure mode of assessment frameworks is a 30-item improvement backlog that nobody starts."
        },
    ],

    "Why Platform Engineering Emerged": [
        {
            "type": "diagram",
            "title": "Cognitive Load - Before and After a Platform",
            "image": "16-cognitive-load",
            "caption": "The platform absorbs the extraneous load once, so teams can spend capacity on the mandate.",
            "notes": "Do the counting exercise against the left panel: ask the room to add anything missing for their environment - and in a supervised institution the additions come fast (audit evidence, POPIA handling, records retention, vendor management, network zoning, change records). Every addition strengthens the argument, because the left panel is the tax each team pays before delivering anything. Then the right panel: note that ownership does not move - the product team still runs its service, still carries the consequences - what moves is the obligation to REBUILD the machinery. The arrow between panels is the platform team's entire value proposition, and Module 9 turns it into measurable product KPIs."
        },
        {
            "type": "detail",
            "title": "In Context: Cognitive Load Across SARB Departments",
            "sections": [
                ("The load a delivery team carries in a central bank", [
                    "Everything on the standard list: runtime, pipelines, IaC, observability, secrets, scanning, policy.",
                    "Plus institution-specific load: network zoning, change records, evidence for audit, records retention.",
                    "Plus data obligations: POPIA handling, classification, masking for test, retention and access control.",
                    "Plus assurance cycles: internal audit, external audit, and supervisory or industry assessments.",
                ]),
                ("What a golden path removes for every team, once", [
                    "A scaffolded service: repository, pipeline, build, deployment manifests, dashboards, alerts, runbook stub.",
                    "Controls pre-wired: scanning, policy checks, approvals, immutable logs - compliant because it is the default.",
                    "Standard environments and masked test data provisioned on request instead of requested by ticket.",
                    "Evidence generated automatically as a by-product of delivering - the audit pack builds itself.",
                ]),
                ("Why this matters more, not less, in a regulated institution", [
                    "Uniformity is a control: forty hand-built pipelines have forty different weaknesses nobody can enumerate.",
                    "One paved road is inspectable end to end; departmental variety is not, at any reasonable audit cost.",
                    "Scarce specialists (security, SRE, data protection) scale by encoding their expertise into the road.",
                    "The measurable prize: time-to-first-deploy for a new service, from weeks or months to a day.",
                ]),
            ],
            "notes": "The strongest platform argument in a supervised institution is not developer happiness - it is control uniformity, so lead with that. Forty teams each assembling their own pipeline produces forty different control postures, and no audit function can meaningfully assess forty; one golden path can be assessed once, deeply, and every consumer inherits the result. That reframing turns the platform from an engineering nicety into a risk-reduction programme, which is how it gets funded. The second argument is scarcity: a central bank has a small number of deep specialists in security, data protection and reliability, and the only way their expertise reaches every delivery team is to encode it into defaults rather than schedule it into meetings. Then give the metric - time-to-first-deploy - and ask the room what their honest current answer is for a brand-new internal service; the number is usually measured in weeks or months, and it is the number that makes the case without any further argument. Close by repeating the self-service test, because it is what separates a platform from a new bottleneck: teams must be able to consume it without filing a ticket and waiting."
        },
    ],

    "Culture Is Measurable: the Westrum Typology": [
        {
            "type": "diagram",
            "title": "The Westrum Spectrum",
            "image": "17-westrum-spectrum",
            "caption": "Four behaviours, three cultures - and a research-backed direction of travel.",
            "notes": "Read the table by ROW rather than by column: information, messengers, failure, novelty. Reading down a column invites people to label their organisation with one word, which is both unfair and unhelpful; reading across a row lets them see that most institutions are pathological on one behaviour, bureaucratic on two and generative on another - which is a far more actionable picture. Ask which single row they would most like to move and what one behaviour would move it. In supervised institutions the 'failure' row is usually the hardest, because formal incident reporting obligations sit next to it and people conflate the two - separate them explicitly: the regulatory report answers what happened and what was done, the blameless review answers why it made sense at the time. Both can be true at once."
        },
        {
            "type": "detail",
            "title": "In Context: Bad News in a Systemically Important Institution",
            "sections": [
                ("Why information flow matters more here than almost anywhere", [
                    "The institution's core products are trust, stability and accurate information - all degraded by hidden problems.",
                    "Industry-facing services mean a suppressed problem becomes several organisations' problem, not just yours.",
                    "Supervisory credibility depends on the institution knowing its own weaknesses before anyone else finds them.",
                    "Near-misses are the cheapest data available - and the first thing an unsafe culture stops producing.",
                ]),
                ("The trap: formal reporting is not the same as free information flow", [
                    "Mandatory incident reporting produces a channel; it does not by itself produce candour.",
                    "Bureaucratic reflex after an incident: add an approval step, file the report, close the item - nothing learns.",
                    "Generative reflex: report as required AND investigate the system honestly, then publish what was learned.",
                    "Run both tracks deliberately, with the blameless review feeding facts to the formal one, never the reverse.",
                ]),
                ("Behaviours that move a supervised institution toward generative", [
                    "Senior leaders visibly thanking the first person to raise a problem - repeatedly, in public, over months.",
                    "Publishing internal postmortems across departments rather than restricting them to the affected team.",
                    "Rewarding the engineer who reports a near-miss in a control as loudly as the one who ships a feature.",
                    "Making it normal to say 'this deadline is at risk' early - the alternative is discovering it at the window.",
                ]),
            ],
            "notes": "The nuance to teach here is the difference between a reporting OBLIGATION and an information CULTURE, because supervised institutions frequently have excellent versions of the former and weak versions of the latter, and mistake one for the other. The formal report answers what happened, what the impact was and what was done - it is compliance information, written carefully, with an audience that includes people who can sanction. The blameless review answers what made the actions seem correct at the time - it is engineering information, and it only exists if people believe it will not be used against them. Both are legitimate; the mistake is running only the first and assuming the organisation is learning. Recommend the two-track pattern explicitly: run the blameless review first and fast, then draw the factual timeline into whatever formal report is required, never the other way around, because a document written for a sanctioning audience will not contain the honest 'we didn't understand this system' sentence that actually prevents the next incident. Encourage participants to raise this with their risk colleagues rather than around them - in practice risk functions usually welcome better causal information."
        },
    ],

    "Psychological Safety - the Foundation Layer": [
        {
            "type": "detail",
            "title": "In Context: Safety, Audit and the Fear of Being Named",
            "sections": [
                ("What suppresses candour in an audited environment", [
                    "The reasonable fear that an honest account becomes an audit finding with someone's name attached.",
                    "Formal wording habits: 'the control operated as designed' is safer to write than 'we did not understand it'.",
                    "Hierarchy: in many institutions the most senior voice in the room speaks first and the analysis stops there.",
                    "Consequence: the organisation's written record of failure is accurate about WHAT and silent about WHY.",
                ]),
                ("Practical ways to create safety without weakening accountability", [
                    "Separate the tracks: blameless engineering review for causes; formal report for obligations and actions.",
                    "Agree in advance, in writing, that review notes are used to change systems, not to assess individuals.",
                    "In reviews, ask juniors and operators to speak before managers - anchoring silences the best evidence.",
                    "Accountability stays at the level it belongs: the team owns the fix, leadership owns the conditions.",
                ]),
                ("The measurable payoff for a central bank", [
                    "Earlier warning on control weaknesses - found internally rather than by an assessment or an incident.",
                    "Accurate estimates and honest status, so delivery risk is visible while there is still time to act.",
                    "Sustainable on-call: people report fatigue and single points of knowledge before they become outages.",
                    "Better data for supervisors and auditors, because the underlying record is truthful.",
                ]),
            ],
            "notes": "Handle this with care and without naivety: participants work in an environment where written words genuinely carry consequences, so telling them to 'just be open' is useless advice. The workable move is structural separation - a review whose explicit, agreed purpose is system improvement, whose notes are not a personnel record, feeding facts into whatever formal reporting is required. Encourage participants to get that separation agreed in advance with risk and audit colleagues, in writing, rather than assuming it. Say clearly that this is not about hiding anything from oversight: the formal obligations are met in full, and the quality of the information improves, because people can explain what actually confused them. The speaking-order tip is small and unusually effective in hierarchical institutions - the operator who was on the keyboard has the best evidence and is usually the last to speak, by which time the senior interpretation has already framed the discussion. Finally, connect safety to the technical modules once more: every automated signal this course installs generates bad news by design, and the organisation's response to bad news determines whether those signals get investigated or quietly disabled."
        },
    ],

    "Conway's Law - Architecture Mirrors Communication": [
        {
            "type": "diagram",
            "title": "Conway's Law and the Reverse Maneuver",
            "image": "18-conways-law",
            "caption": "Silos produce seams; teams shaped for the target architecture produce that architecture.",
            "notes": "Work the left panel first and let the room recognise itself, then ask the diagnostic question in the blue box on the right: can one team ship a change to production today without another team's calendar? In departmental institutions the honest answer is usually no, and the reasons are organisational rather than technical - which is exactly Conway's point. Be careful not to imply that the answer is a reorganisation; those are expensive, disruptive and rarely within participants' control. The realistic move is smaller: identify one system where the seam causes the most pain, and change the INTERFACE rather than the org chart - a documented API with a contract, a shared repository with InnerSource rights, or a temporary embedded engineer. Conway's law responds to communication paths, and those can be changed without moving a single reporting line."
        },
        {
            "type": "detail",
            "title": "In Context: Conway's Law in a Departmental Institution",
            "sections": [
                ("Structures that shape central-bank systems", [
                    "Departmental ownership by function produces systems that mirror the departmental split, seams included.",
                    "A central data or database function turns every schema change into a queued request across teams.",
                    "Separate delivery and operations functions produce a designed-for-handover architecture with a cliff edge.",
                    "Vendor boundaries are org boundaries too: contracted scope becomes an interface nobody can change quickly.",
                ]),
                ("What to do when reorganising is not on the table", [
                    "Change the interface, not the org chart: publish contracts and versioned APIs between departmental systems.",
                    "InnerSource across departmental repositories so a needed change can be proposed instead of requested.",
                    "Temporary embedded engineers to build a capability WITH a team, with an agreed end date.",
                    "Shared platform components remove the most-crossed seams entirely - nobody queues for what they self-serve.",
                ]),
                ("Reverse Conway where you DO get a choice", [
                    "New initiatives are the opportunity: shape the team around the service it will own from day one.",
                    "Give that team the full set - repository, pipeline, environments, data, alerts and the operational duty.",
                    "Keep it within cognitive-load limits; if it needs to know everything, the platform is not doing its job.",
                    "Then measure it honestly against the diagnostic: can it ship today without another team's calendar?",
                ]),
            ],
            "notes": "Most participants cannot reorganise their institution, so the practical value of Conway's Law for them is predictive and tactical rather than structural. Predictive: they can now anticipate where the architecture will resist change, because it will resist exactly where the organisation has expensive communication. Tactical: communication paths can be changed far more cheaply than reporting lines - a published contract, a shared repository with contribution rights, a temporary embedded specialist, or a platform capability that removes the crossing altogether. Spend the most time on the vendor point, because it is under-discussed and very real in this sector: a contract boundary is an organisational boundary, so architecture will crystallise along it, and a scope defined in a procurement document three years ago is still shaping today's system. The implication for participants is to think about contract structure as architecture, and to prefer contracts that deliver artefacts and capability transfer over those that deliver tickets. On the last section, remind them that new work is where Conway's Law can be used deliberately - shaping a new team around a service is far easier than re-cutting an existing estate."
        },
    ],

    "Communication Strategies That Scale": [
        {
            "type": "detail",
            "title": "In Context: Written Decisions and the Audit Trail",
            "sections": [
                ("ADRs are governance you get for free", [
                    "One page per significant decision: context, options considered, decision, consequences, status.",
                    "Stored in the repository beside the code, versioned, reviewed - so the record cannot drift from reality.",
                    "This is exactly the 'why' evidence auditors and assessors ask for, produced as a by-product of working.",
                    "Two years later it answers 'was this considered?' without depending on who is still in the role.",
                    "Superseded, never edited: ADR-0042 replaces ADR-0017, and the pair shows how thinking evolved.",
                ]),
                ("ChatOps and the incident timeline", [
                    "Deploys, alerts and incident discussion in shared channels create a timestamped record automatically.",
                    "That record is the backbone of both the blameless review and any formal incident report.",
                    "Guardrails that matter here: no sensitive data in channels, least-privilege bots, confirmation on destructive actions.",
                    "Watch classification: shared does not mean unrestricted - channel scope should match information sensitivity.",
                ]),
                ("Documentation as a product, in an institution that runs on documents", [
                    "The difference is lifecycle: owned, reviewed, versioned with the system, and measured by whether people succeed.",
                    "Runbooks live next to the service and change in the same pull request that changes behaviour.",
                    "Test it the honest way: can a new joiner complete the task unaided, using only the document?",
                    "For a platform, documentation IS the user interface - and Module 9 measures it as a product KPI.",
                ]),
            ],
            "notes": "In an institution that already produces a great deal of documentation, the ADR argument has to be about a different KIND of document, not more of them: short, decision-scoped, versioned with the code, and immutable once superseded. Make the governance link explicit, because it is the reason this practice gets adopted rather than tolerated - the questions auditors and assessors ask about architectural choices are answered directly by an ADR archive, and the answer is contemporaneous rather than reconstructed. On ChatOps, be pragmatic about classification: the practice is valuable because it produces an automatic timeline, and it must be implemented within the institution's information-classification rules, which usually means restricted channels for restricted work rather than abandoning the pattern. The runbook point deserves emphasis for operations-heavy audiences: a runbook that lives in a separate document store drifts from the system within months, whereas one that lives in the repository and changes in the same pull request as the behaviour stays true - and that reliability is what makes it usable at 03:00."
        },
    ],

    "Breaking Silos Without Breaking the Org": [
        {
            "type": "detail",
            "title": "In Context: Shared Goals, Segregation of Duties Intact",
            "sections": [
                ("Aligning measures without merging responsibilities", [
                    "Put the same four DORA numbers in front of delivery AND operations for the same value stream.",
                    "Add shared availability and data-quality objectives for the services the institution is accountable for.",
                    "Neither side can then win by hurting the other - speed with breakage fails, stability with paralysis fails.",
                    "None of this requires changing who approves what; it changes what everyone is trying to improve.",
                ]),
                ("Shared pain, adapted to a supervised environment", [
                    "Developers join the response path for their own services - starting in business hours, shadowing first.",
                    "They diagnose and propose; execution in production follows the institution's approval and access rules.",
                    "The feedback loop survives that adaptation intact: whoever explains the outage tends to prevent the next one.",
                    "Non-negotiables: runbooks, dashboards, working alerts, fair rotation, and time to fix the causes of pages.",
                ]),
                ("Interfaces that work between departments", [
                    "InnerSource: propose a change to another department's repository instead of raising a request and waiting.",
                    "Time-boxed embedding to transfer a capability, with an explicit end date and a self-sufficiency test.",
                    "And the anti-pattern to name out loud: a central 'DevOps team' that owns every pipeline becomes the new wall.",
                    "The test stays the same: can a team self-serve, or must it file a ticket and wait for someone's backlog?",
                ]),
            ],
            "notes": "The reconciliation to teach here is that shared GOALS and separated DUTIES are independent choices, and institutions often assume they are the same conversation. You can put identical metrics in front of two functions that retain completely separate approval authority - and doing so removes the structural conflict without touching a single control. That is usually the easiest high-value change available to a participant with any influence. On developer involvement in incident response, present the adapted version rather than the purist one, because the purist version stalls in supervised environments and the adapted version keeps almost all the value: the developer is in the response path as the person who understands the system, diagnoses the cause and proposes the fix, while the execution follows the institution's access rules. Be firm about the prerequisites - anyone asked to carry operational responsibility needs the tools, information and capacity to discharge it, and an institution that skips those is transferring stress rather than ownership. Close on the third-silo warning, since several participants may be sitting inside or near a team recently renamed with 'DevOps' in the title; give them the self-service test as a neutral, non-personal way to assess it."
        },
    ],

    "Blameless Postmortems and Retrospectives": [
        {
            "type": "detail",
            "title": "In Context: Blameless Reviews Alongside Formal Reporting",
            "sections": [
                ("Running two tracks that do not fight each other", [
                    "Track 1 - blameless engineering review: fast, honest, causal. Purpose: change the system.",
                    "Track 2 - formal incident record: obligations, impact, actions, timelines. Purpose: accountability and reporting.",
                    "Order matters: hold the blameless review FIRST, then draw its factual timeline into the formal record.",
                    "Reverse that order and the honest sentences never get written, because the audience is wrong.",
                    "Agree the separation with risk and audit colleagues in advance, in writing - do not improvise it after an incident.",
                ]),
                ("What a good central-bank postmortem produces", [
                    "A timeline built from artefacts: alerts, deploys, chat, graphs, change records - not from memory.",
                    "Impact stated in mandate terms: who was affected, which obligations were at risk, for how long.",
                    "Contributing factors, plural - single-root-cause narratives usually stop at the last person who touched it.",
                    "Systemic actions with named owners and dates, tracked in the normal backlog and reported on.",
                    "What went WELL, named explicitly: detection, rollback, escalation - keep what worked deliberately.",
                ]),
                ("Retrospectives: the same loop without waiting for an outage", [
                    "Team cadence, same discipline: safety, systemic focus, a small number of owned improvements.",
                    "Feed the flow data in: what waited longest this cycle, and what would remove that wait next cycle?",
                    "One improvement finished per cycle beats ten discussed - improvement must be scheduled, not squeezed.",
                ]),
            ],
            "notes": "This is the practical heart of Module 2 for this audience, so give it the time. The two-track model is what makes blameless practice implementable in a supervised institution: nothing about it reduces the formal record, and everything about it improves the quality of the information that record contains. State the sequencing rule and the reason - a document written first for a sanctioning audience will never contain 'we did not understand how this component behaved under load', which is precisely the sentence that prevents recurrence. Push participants to agree the boundary with risk and audit BEFORE their next incident, because negotiating it during one guarantees the cautious default. On the postmortem contents, emphasise building the timeline from artefacts, which is also where ChatOps and pipeline logs pay off, and insist on the plural 'contributing factors' - in complex systems the single-root-cause habit reliably terminates the investigation at the last human action rather than at the conditions that made it likely. Finally, the action items: named owner, date, normal backlog, reported. A review whose actions never ship teaches the organisation that reporting incidents accomplishes nothing, which is how a bureaucratic culture quietly becomes a pathological one."
        },
    ],

    "The DevOps Toolchain - Categories, Not Brands": [
        {
            "type": "detail",
            "title": "In Context: The Toolchain a Central Bank Needs",
            "sections": [
                ("Categories that carry extra weight in this sector", [
                    "Source control: the system of record for change - and the evidence base for every audit question.",
                    "Artifact registry: immutable, versioned, scannable - the promotion boundary that proves what shipped.",
                    "Secrets management: centralised, rotated, audited - never in repositories, images, tickets or chat.",
                    "Policy as code: institutional rules expressed as checks that run on every change (Module 7).",
                    "Observability: availability and data-quality evidence for services the institution is accountable for.",
                ]),
                ("Deployment and hosting questions to settle early", [
                    "Where may code, data and secrets physically run - and does that differ per classification tier?",
                    "Self-managed runners inside the network versus hosted runners: reachability, data residency, maintenance.",
                    "Vendor concentration and exit: how much of the delivery chain depends on one supplier remaining available?",
                    "Support model and lifecycle: who patches it, who is accountable when it is down during a critical window?",
                ]),
                ("A pragmatic default posture", [
                    "Standardise on ONE toolchain per category, with a documented exception path - variety is an audit cost.",
                    "Prefer tools whose entire configuration is code, so the control posture itself is reviewable and diffable.",
                    "Prefer open standards at the expensive layers (instrumentation, containers, IaC) to keep exit affordable.",
                    "Buy where the problem is generic; build only where the institution's mandate makes it genuinely specific.",
                ]),
            ],
            "notes": "Frame the toolchain conversation in this sector around three questions that differ from a commercial context: where things may run, who is accountable when they break, and how much it costs to leave. Data residency and network reachability decide the hosting model far more often than features do, so put that decision first - it determines whether hosted runners are usable at all and whether the pipeline can reach the environments it must deploy to. Vendor concentration deserves airtime because supervised institutions think about it for their banking counterparties and often not about their own delivery chain: it is a legitimate resilience question to ask what happens if a single supplier's service is unavailable during a critical settlement or publication window. On standardisation, make the audit argument again - each additional tool in a category multiplies the assessment surface, and the institution pays that cost forever. Close with buy-versus-build: the mandate is monetary policy, financial stability, payments oversight and currency, not building pipeline engines, so the default should be to consume generic capability and reserve engineering for what only this institution can do."
        },
    ],

    "Principles for Choosing Tools": [
        {
            "type": "detail",
            "title": "In Context: Choosing Tools Under Procurement and Assurance",
            "sections": [
                ("Add these questions to the standard evaluation", [
                    "Can 100% of it be driven from a pipeline, with no human clicking a console? (automation and evidence)",
                    "Is the whole configuration expressible as files we can version, review and diff? (control posture as code)",
                    "Does it emit machine-readable output and immutable logs? (evidence, not screenshots)",
                    "What identity, access and audit integration does it support - and does it fit our access model?",
                    "What is the exit cost in data, configuration and retrained people, two years from now?",
                ]),
                ("Procurement realities to plan for, not around", [
                    "Evaluation and procurement cycles are long: run a time-boxed proof of concept and record an ADR.",
                    "Total cost includes integration, operation, training and exit - licences are the smallest visible part.",
                    "Support and lifecycle commitments matter more than feature lists when a window cannot move.",
                    "Third-party risk assessment applies to delivery tooling too - your pipeline has production credentials.",
                ]),
                ("Paved road, not mandate - even here", [
                    "A mandate produces compliance plus quiet workarounds you will discover during an incident.",
                    "A road that is genuinely the fastest safe path produces adoption, and adoption is measurable.",
                    "Keep an explicit, documented exception path: unusual needs step off and carry what the road handled.",
                    "Adoption rate then becomes an honest control indicator: how much of delivery runs through the assessed path?",
                ]),
            ],
            "notes": "The five evaluation questions on the first section are deliberately phrased so they can be pasted into a requirements document, and each maps to something the institution already cares about: pipeline-drivability is automation and repeatability, configuration-as-code makes the control posture reviewable, machine-readable output replaces screenshot evidence, identity integration fits the access model, and exit cost is concentration risk. Encourage participants to add them to whatever evaluation template they already use rather than proposing a new process. On procurement, be realistic and sympathetic: cycles are long and cannot be wished away, so the practical advice is to shorten the technical part with a genuinely time-boxed proof of concept against real workloads, and to write the decision down in an ADR so the next evaluation does not start from zero. The last section is worth repeating even in an institution that can mandate: mandates produce shadow practice, which is invisible until it appears in an incident timeline. A measured adoption rate for the paved road is a better control indicator than a policy statement, because it reflects what is actually happening."
        },
    ],

    "Automation and Orchestration Platforms": [
        {
            "type": "diagram",
            "title": "Push vs Pull Deployment (GitOps)",
            "image": "21-gitops-push-pull",
            "caption": "Pull keeps credentials in the cluster, corrects drift, and makes 'what runs' provable.",
            "notes": "Trace both models and then focus on the three properties that matter in a supervised institution. First, credential location: in the push model a CI runner holds production credentials, in the pull model it does not, and that difference is a genuine reduction in the blast radius of a compromised pipeline. Second, drift: the emergency manual change that everyone intends to put back is reverted automatically rather than remembered, which converts a recurring control weakness into a non-event. Third, provability: 'what is running is what is in Git at commit X' is an assertion a machine can verify continuously, which is a stronger statement than most manual attestations. Be honest about the cost - the agent is another component to operate, and out-of-band changes genuinely stop working, which is uncomfortable during an incident until the team trusts the path."
        },
        {
            "type": "detail",
            "title": "In Context: GitOps and Segregation of Duties",
            "sections": [
                ("How the pipeline satisfies separation of author and executor", [
                    "The author proposes a change; a different person approves it; the automation executes it. Nobody bypasses.",
                    "Human production credentials become unnecessary for routine change - a control improvement, not a relaxation.",
                    "Every step leaves an immutable record: commit, review, approval, run, artefact digest, deployment result.",
                    "Emergency access still exists, but as a break-glass exception that is logged, alerted and reviewed after.",
                ]),
                ("Why drift correction is a control, not a convenience", [
                    "Manual changes made under pressure are the classic source of undocumented divergence between environments.",
                    "A reconciling agent either reverts them or reports them - either way the divergence stops being invisible.",
                    "'What runs equals what is in the repository at commit X' can be verified continuously rather than attested annually.",
                    "Environment parity becomes structural, so a test result predicts production behaviour again.",
                ]),
                ("Where to start in an institution that is not on Kubernetes", [
                    "The pattern generalises: declarative desired state in Git plus an agent that converges reality toward it.",
                    "Start with configuration and infrastructure (Terraform, Ansible) reconciled on a schedule from the repository.",
                    "Even a scheduled 'plan and report drift' job creates the visibility, before you enable automatic correction.",
                    "Sequence it: report drift -> agree what is allowed to differ -> then enable correction on the safe categories.",
                ]),
            ],
            "notes": "This slide converts a technical model into a governance argument, which is how it gets approved. The essential point is that pipeline-executed change is a stronger control than human-executed change: the separation between who writes and who applies is enforced by a machine that cannot be persuaded, tired or in a hurry, and the record is generated automatically rather than assembled afterwards. Say clearly that break-glass access must still exist - a control model with no emergency path gets bypassed informally, which is worse - and that the right treatment is to make it logged, alerted and reviewed rather than to pretend it will not be used. The drift-correction framing is the one to spend time on with operations-heavy audiences: everyone in the room has lived through the temporary change that stayed for a year, and a reconciling agent is simply a mechanism that never forgets. The last section matters because most participants are not running Kubernetes yet: give them the intermediate step of a scheduled drift-report job, which delivers most of the visibility with none of the risk, and makes the case for the next step with data."
        },
    ],

    "This Course's Toolchain (and Why)": [
        {
            "type": "detail",
            "title": "In Context: From These Labs to SARB Environments",
            "sections": [
                ("What transfers unchanged", [
                    "The WORKFLOW: propose, review, verify automatically, promote an immutable artefact, observe, roll back.",
                    "Pipeline concepts: jobs, dependencies, gates, environments, approvals - identical across engines.",
                    "Kubernetes API skills from kind: manifests, probes, rollouts, RBAC behave the same on any conformant cluster.",
                    "Terraform's plan/apply/state/modules workflow, whatever the target provider turns out to be.",
                    "Triage discipline for scanners, and policy-as-code thinking for institutional rules.",
                ]),
                ("What you will have to add back at work", [
                    "Identity integration, network zoning, and whatever access model your environments require.",
                    "Data protection in practice: classification, masking or synthetic data for test, retention rules.",
                    "Change records and evidence retention wired into the pipeline rather than produced by hand afterwards.",
                    "Availability expectations for industry-facing services, including windows the institution cannot move.",
                ]),
                ("A sensible first target after the course", [
                    "Choose an INTERNAL, low-criticality service as the first end-to-end golden path - never settlement-critical.",
                    "Prove the full loop on it: pipeline, IaC, scanning, deploy, dashboard, alert, rollback, postmortem format.",
                    "Then take the evidence - not the enthusiasm - to risk and audit colleagues and agree the pattern.",
                    "Only then extend the pattern toward more critical systems, one control conversation at a time.",
                ]),
            ],
            "notes": "Set expectations honestly at this point in the day, because participants are about to spend the afternoon in labs on localhost and some will privately wonder how it relates to their estate. Be explicit about the split: the workflow, the concepts and the tool skills transfer directly; the institutional wrapping - identity, zoning, classification, evidence, windows - does not exist in the labs and has to be added deliberately. That admission increases credibility rather than reducing it. The last section is the most useful advice in the module: the way this pattern succeeds in a supervised institution is by proving it end to end on something genuinely low-risk, then presenting evidence rather than argument to the colleagues who own control assurance. Teams that try to start with a critical system spend a year in meetings; teams that arrive with a working pipeline, a reproducible environment, an audit trail that generates itself and a rollback they have demonstrated tend to find the conversation much shorter. Encourage participants to identify a candidate service before they leave."
        },
    ],

    "The Problem IaC Solves": [
        {
            "type": "detail",
            "title": "In Context: Snowflakes, Drift and DR in a Regulated Estate",
            "sections": [
                ("The snowflake problem in a long-lived institution", [
                    "Systems that have run for a decade accumulate undocumented, hand-applied configuration nobody dares touch.",
                    "The knowledge lives with a few individuals - a concentration risk the institution would never accept elsewhere.",
                    "Environments diverge, so testing loses predictive power exactly where predictability matters most.",
                    "Key-person dependency on infrastructure knowledge is a risk finding waiting to be written.",
                ]),
                ("Disaster recovery: the difference IaC makes", [
                    "Without IaC, recovery is reconstruction from memory, tickets and screenshots - untested and slow.",
                    "With IaC, recovery is 'apply the same definitions to a different target' - and it can be REHEARSED.",
                    "Rehearsal is the point: a plan exercised quarterly is a capability; one exercised never is a document.",
                    "The same code that builds production builds the DR environment, so parity is structural, not aspirational.",
                ]),
                ("What auditors and assessors get out of it", [
                    "A reviewable definition of the intended configuration, with history, authorship and approvals attached.",
                    "Drift detection: a scheduled plan proves whether reality still matches the approved definition.",
                    "Change evidence generated continuously instead of assembled into a pack once a year.",
                    "Reproducibility: the same environment can be stood up for testing, forensics or recovery on demand.",
                ]),
            ],
            "notes": "Lead with the risk framing, because in this audience it is both true and persuasive. Undocumented, hand-built infrastructure is a key-person and reconstruction risk of exactly the kind the institution scrutinises in others, and IaC is the mitigation. The disaster-recovery argument is the strongest single business case available for IaC in a central bank: recovery capability is a supervisory and board-level concern, and the difference between a documented plan and a rehearsed capability is enormous. Make the rehearsal point concrete - with infrastructure as code, standing up a parallel environment is a routine operation that can be scheduled on a Tuesday morning, which means the recovery path is exercised by people who are awake, in daylight, with time to fix what does not work. Then the assurance angle: drift detection is genuinely novel for many control environments, because it converts an annual attestation into a continuous, evidenced check. Encourage participants to bring that specific capability to their next control conversation - a scheduled job that proves reality still matches the approved definition is easy to explain and hard to argue with."
        },
    ],

    "Core Principles: Declarative, Idempotent, Immutable": [
        {
            "type": "detail",
            "title": "In Context: Immutability and Change Control",
            "sections": [
                ("Mapping the principles onto change management", [
                    "DECLARATIVE gives you a diff: the change record can contain the exact resources to be added, changed, destroyed.",
                    "IDEMPOTENT makes re-running safe, so recovery and reconciliation are routine rather than risky.",
                    "IMMUTABLE means the artefact promoted to production is the artefact that was tested - provable by digest.",
                    "VERSIONED means the approval, the change and the evidence are the same record, not three systems.",
                ]),
                ("Why 'no patching in place' improves assurance", [
                    "Patch-in-place creates a system whose true state is the sum of undocumented interventions.",
                    "Replace-the-artefact keeps every running instance identical to a definition someone reviewed.",
                    "Rollback becomes 'redeploy the previous digest' - a tested state, not a repair under pressure.",
                    "The cost is honest: immutability requires a reliable build-and-deploy path, which is why CI/CD comes first.",
                ]),
                ("A change record that writes itself", [
                    "What changed: the plan diff and the artefact digest, both machine-generated.",
                    "Why: the pull request description and the linked ADR or work item.",
                    "Who approved: the recorded review, enforced by branch protection rather than by convention.",
                    "Result: pipeline run, deployment outcome, smoke-test result, and the rollback path if it was used.",
                ]),
            ],
            "notes": "The third section is the one to leave on screen: it lists, item by item, what a mature change record contains and shows that every element can be produced automatically by the practices in this course. That is a genuinely attractive proposition in an institution where change records are assembled by hand and are therefore both expensive and, quietly, less accurate than everyone would like. Make the honesty point about immutability's cost - it demands a build-and-deploy path that works reliably, and an institution that adopts immutability without investing in that path has simply made changes slower. That is why the course sequences CI/CD before runtime. On declarative and idempotent, the practical demonstration is the one participants will run in the lab: a second apply that reports no changes proves the tool holds a model of intent, and that same mechanism is what makes drift detection and automated recovery possible. Keep tying the principles back to control language - diffable, reviewable, provable, reversible - because those four words are what the risk conversation is actually about."
        },
    ],

    "Terraform's Mental Model in Five Concepts": [
        {
            "type": "diagram",
            "title": "Terraform's Five Concepts",
            "image": "22-terraform-mental-model",
            "caption": "Code declares desire, state records reality, plan is the difference, apply closes it.",
            "notes": "Use the picture to fix the mental model before anyone touches syntax in Workshop 3. Trace the loop out loud: the module holds resources and a documented interface, the provider translates to a platform API, plan compares desire against the state's view of reality, apply executes the approved difference, and state is updated to match. Then point at the amber panel and give the operational habit that matters most: read plan output defensively, and treat any unexpected destroy count as a stop signal. Many real infrastructure incidents were described accurately in a plan that nobody read carefully. In a supervised institution that habit has a second benefit - the plan diff is exactly the artefact to attach to a change record, so reading it properly is both engineering discipline and governance."
        },
        {
            "type": "detail",
            "title": "In Context: Terraform in a Bank-Grade Environment",
            "sections": [
                ("State is a sensitive asset - treat it like one", [
                    "State can contain resource attributes in clear text, so it inherits the classification of what it describes.",
                    "Remote backend, encrypted at rest, access-controlled, versioned - never a laptop, never an email attachment.",
                    "Locking prevents two simultaneous applies from corrupting the record of reality.",
                    "Separate state per environment so a staging apply is structurally incapable of touching production.",
                ]),
                ("Modules as the institution's paved road for infrastructure", [
                    "The platform team publishes versioned modules that encode zoning, tagging, logging and policy defaults.",
                    "A delivery team consumes a module and gets a compliant-by-default resource set without reading a standard.",
                    "Improvements ship as new versions and are adopted deliberately - consumers pin, so nothing changes by surprise.",
                    "This is the single highest-leverage artefact a platform team can produce for a regulated estate.",
                ]),
                ("Adopting an existing hand-built estate", [
                    "Start with terraform import on a bounded, low-criticality area - do not attempt the whole estate at once.",
                    "Verify by producing a plan that reports NO changes; that no-change plan is the proof of an accurate model.",
                    "Then own it: all further change flows through the repository, and manual changes are treated as incidents.",
                    "Sequence areas by risk and by how often they change - frequently-changed, low-risk areas pay back first.",
                ]),
            ],
            "notes": "Three practical points, all of which prevent real damage. First, state as a classified asset: teams routinely under-protect it because it looks like a working file, and it can contain sensitive attributes of the infrastructure it describes - so it belongs in an encrypted, access-controlled, versioned backend with locking, and separate per environment. The blast-radius argument for separate state is the one that persuades: the goal is that the worst possible mistake in a lower environment cannot reach production, guaranteed structurally rather than by care. Second, versioned modules as the infrastructure golden path - this is where Module 4 and Module 9 meet, and it is the most valuable thing a platform team in a supervised institution can build, because it makes the compliant configuration also the easiest configuration. Third, adoption: almost nobody starts from an empty estate, so give them the import-then-verify-with-a-no-change-plan recipe and the advice to sequence by change frequency, since the areas that change often are where automation pays back fastest and where drift is most damaging."
        },
    ],

    "IaC Best Practices (the Production Checklist)": [
        {
            "type": "detail",
            "title": "In Context: IaC Controls Your Auditors Will Like",
            "sections": [
                ("Controls that come free with the workflow", [
                    "Four-eyes review enforced by branch protection - not a policy statement, a technical control.",
                    "The exact change diff attached to the approval, so the reviewer approves reality rather than intent.",
                    "Apply executed only from the pipeline, with credentials no individual holds - author and executor separated.",
                    "Immutable history of who changed what, when, why and who approved it, retained as long as the repository.",
                    "Scheduled drift detection proving that production still matches the approved definition.",
                ]),
                ("Where secrets go wrong, and the rule that prevents it", [
                    "Never in .tf files, .tfvars, defaults, committed environment files, or pipeline logs - assume Git is forever.",
                    "Reference a secrets manager and inject at runtime; keep values out of state and out of plan output.",
                    "Anything ever committed must be rotated - reverting the commit or rewriting history does not undo exposure.",
                    "Detect automatically: secret scanning on every pull request, not a periodic manual review.",
                ]),
                ("Structure that keeps blast radius small", [
                    "Small composable modules over one giant configuration - faster plans, smaller failures, easier review.",
                    "Tag every resource with owner, environment, classification and cost centre - untagged resources become orphans.",
                    "CODEOWNERS so the accountable team is automatically a required reviewer on its own infrastructure.",
                    "IaC scanning (trivy config, checkov) on every pull request, gated on what a team can fix today.",
                ]),
            ],
            "notes": "The first section is deliberately written in control language so participants can lift it directly into a discussion with internal audit: five controls, each technically enforced, each producing evidence automatically. Compare that honestly with the manual equivalent - a change form, a meeting, a signature and a screenshot pack - and note that the automated version is both cheaper and more truthful, because it cannot be completed after the fact. That comparison is the argument. The secrets section is the one that prevents the most damaging single incident type in IaC adoption, so state the rotation rule in its strongest form and do not soften it: once a credential is committed it must be treated as compromised regardless of whether the commit was reverted or the history rewritten, because clones, forks, caches and logs are beyond anyone's control. Recommend automated secret scanning on pull requests as the only reliable defence, since human review misses it consistently. On structure, the tagging point pays off in the first cost review or estate cleanup, and the classification tag is the one specific to this sector - knowing the classification of what a resource holds is what makes automated policy possible."
        },
    ],

    "Continuous Integration - Small Batches, Always Green": [
        {
            "type": "diagram",
            "title": "Why Batch Size Is the Enemy",
            "image": "19-batch-size-risk",
            "caption": "The same total change, split differently, carries radically different risk.",
            "notes": "This curve is the single most useful picture for a risk-aware audience, because it makes the safety argument visually rather than rhetorically. Walk it from left to right: small changes sit in the flat region where review is genuine, tests are meaningful and reversal is one command; large changes sit in the steep region where review becomes skimming and diagnosis becomes archaeology. Then give the green panel, which is the argument that wins the meeting: the same total volume of change, delivered as twenty small increments rather than one large release, is not merely faster - it is materially safer, because each increment is individually understood and individually reversible. Note the amber panel for infrastructure and database work, where the equivalent discipline is expand/contract: add the new structure, run both, migrate, then remove the old - never break and fix in a single step during a window."
        },
        {
            "type": "detail",
            "title": "In Context: Small Batches Inside a Window Culture",
            "sections": [
                ("The genuine constraints - and what they do NOT require", [
                    "Some systems can only be CHANGED inside agreed windows: settlement cycles, industry-coordinated releases.",
                    "That constrains WHEN production changes, and says nothing about how large each change must be.",
                    "Integrating daily, testing continuously and keeping the trunk releasable are compatible with any window.",
                    "So the goal becomes: arrive at the window with many small, individually verified, individually reversible changes.",
                ]),
                ("Practices that fit a window culture", [
                    "Trunk-based development with short-lived branches - integration debt is what makes windows terrifying.",
                    "Feature flags so unfinished work is deployed dark rather than parked on a branch for a quarter.",
                    "Expand/contract for schema and interface changes, so nothing needs a big-bang cutover inside the window.",
                    "Continuous verification against a production-like environment, built by the same IaC as production.",
                ]),
                ("A red mainline is a stop-the-line event", [
                    "If the trunk is broken, the institution has lost its ability to ship a fix - including an urgent one.",
                    "Treat green trunk as an availability control, not a developer preference: it is your route to production.",
                    "Flaky tests are a defect, not an inconvenience - re-running until green trains people to ignore real failures.",
                    "Measure it: how long was the mainline red, at worst, in the last quarter? That number is a risk indicator.",
                ]),
            ],
            "notes": "Lead with the distinction that unlocks the module for this audience: a release window constrains the timing of production change, not the size of each change or the frequency of integration. Teams in window cultures often conclude that continuous integration does not apply to them, and then arrive at the window with a quarter of unintegrated work, which is precisely the scenario the window was meant to make safe and precisely the one it cannot. The reframing is that CI is how you make the window boring - by the time it arrives, every change has been integrated, tested and, where possible, already deployed dark. The last section reframes the green trunk as an availability control, which is unusually persuasive here: if the mainline is broken, the institution cannot ship anything, including an urgent fix during an incident, so the state of the trunk is an operational risk indicator rather than an engineering hygiene preference. Encourage participants to measure worst-case red duration and put it on the same report as their other operational indicators - it changes how the organisation treats a broken build."
        },
    ],

    "Delivery vs Deployment - and Deploy vs Release": [
        {
            "type": "diagram",
            "title": "Deploy vs Release - the Embargo Pattern",
            "image": "24-deploy-vs-release",
            "caption": "Deploy days early in daylight; release at the appointed minute with a flag flip.",
            "notes": "This pattern is worth the time because it maps so directly onto work where the timing of publication is fixed and consequential - a scheduled announcement, a statistical release, an industry-coordinated change. The current default in most institutions is to do the risky thing (deploying software) at the same moment as the timed thing (making it visible), usually late at night, under pressure, with no margin. The pattern separates them: deploy on Monday morning with everyone awake, verify in production while the content stays dark, and let the timed moment be a flag flip that carries no build, no restart and no deployment risk - and that can be reversed in seconds if something is wrong at one minute past. Also flag the discipline requirement on screen: flags are debt, so each one needs an owner and a removal date, and dark content must be genuinely unreachable, which is a security review question rather than an assumption."
        },
        {
            "type": "detail",
            "title": "In Context: Delivery, Deployment and Embargoes",
            "sections": [
                ("Continuous DELIVERY is the realistic target here", [
                    "Every change is proven deployable by the pipeline; a human still chooses when it goes.",
                    "That keeps approval authority exactly where the institution wants it, while removing the technical uncertainty.",
                    "'Can we ship this?' stops being an engineering question and becomes a scheduling and risk decision.",
                    "Continuous DEPLOYMENT (no human trigger) is a later, service-by-service choice - not a prerequisite for any of this.",
                ]),
                ("Build once, promote the same artefact - and prove it", [
                    "The image tested in the lower environment must be the one that reaches production, verified by digest.",
                    "Rebuilding per environment reintroduces drift: a base image or dependency can change between builds.",
                    "Environment differences belong in injected configuration, never in a separate build.",
                    "The digest is also the evidence: the change record can state exactly which artefact was promoted where.",
                ]),
                ("Frequency as a risk-reduction strategy", [
                    "'If it hurts, do it more often' applies hardest to the operations everyone dreads: restores, failovers, cutovers.",
                    "An operation performed annually is untested; one performed monthly is a capability with known duration.",
                    "Rehearsal converts unknown recovery time into a measured number you can put in a resilience report.",
                    "Start with the safest rehearsal available - restore a backup into an IaC-built environment and time it.",
                ]),
            ],
            "notes": "Position continuous delivery, not continuous deployment, as the target for this audience, and say so plainly - it removes the objection that this course is asking a systemically important institution to let machines ship to production unattended. The distinction is precise and worth repeating: continuous delivery means the pipeline has proven the change deployable and a human decides when, which preserves every approval authority the institution has while eliminating the technical uncertainty that makes those approvals stressful. The build-once-promote point has an evidence dimension that is specific to regulated environments: an artefact digest is a stronger statement about what was deployed than any build log, and it belongs in the change record. Finally, extend the frequency argument beyond deployment to the operations this sector genuinely dreads - restores, failovers, DR invocations, industry cutovers. Ask the room when their last unrehearsed recovery took place and how long it took; if the answer is 'we have never timed it', that is the first improvement, and it is one they can start without any tooling investment."
        },
    ],

    "A Scan Is Not a Gate": [
        {
            "type": "diagram",
            "title": "Report vs Gate",
            "image": "20-report-vs-gate",
            "caption": "Broad visibility, narrow enforcement - the only way a gate stays trusted.",
            "notes": "Show the two branches and be blunt about which one most organisations actually have: a scanner wired with exit code 0, described in the assurance pack as a control, producing a report nobody opens. That is a control in name only, and naming it plainly gives the room permission to check their own pipelines this week. Then the design principle: keep visibility broad and enforcement narrow, gate only on findings a developer can act on today, and widen deliberately as the backlog clears. The amber panel is the adoption sequence, and the fourth item - an audited exception path with expiry dates - is the one that keeps the gate honest in a regulated institution: without a sanctioned exception route, teams invent an unsanctioned one, and then the control exists on paper only."
        },
        {
            "type": "detail",
            "title": "In Context: Gates, Evidence and Supervisory Expectations",
            "sections": [
                ("Turning scanning into an assurable control", [
                    "A report step proves visibility; a gate step proves enforcement - assurance needs both, and they are different.",
                    "Machine-readable output (SARIF/JSON) retained per build IS your evidence - screenshots are not.",
                    "Exceptions must be explicit, owned, time-limited and reviewed, or the gate becomes decorative within weeks.",
                    "Report the trend: is the fixable-critical backlog shrinking? That is the indicator worth putting in a pack.",
                ]),
                ("Your pipeline is part of the supply chain", [
                    "Pin third-party pipeline actions to a version, and to a commit digest for anything touching secrets.",
                    "An action referenced by a moving tag runs whatever its maintainer pushes tonight, with your credentials.",
                    "Declare least-privilege permissions per job explicitly; default tokens are usually far too powerful.",
                    "Prefer short-lived federated credentials over long-lived static secrets stored in the pipeline.",
                    "Treat fork-originated pull requests as untrusted, and never expose secrets to workflows they can trigger.",
                ]),
                ("Where this connects to institutional obligations", [
                    "Change and vulnerability management expectations are satisfied more convincingly by automated evidence.",
                    "Supplier and third-party risk thinking applies to your delivery toolchain, not only to business vendors.",
                    "Software inventory (SBOM) answers 'are we exposed to this component?' in minutes rather than weeks.",
                    "Confirm the specifics with your risk, security and compliance colleagues - patterns here, not legal advice.",
                ]),
            ],
            "notes": "Two arguments to make and one caution. First, the assurance argument: a scanner that cannot fail a build is not a control, and calling it one in an assurance pack is a finding waiting to happen; the two-step pattern gives genuine enforcement while keeping the gate fair enough to survive. Push the evidence point too - retained machine-readable scan output per build is stronger, cheaper and more complete than the screenshot practice many teams still use. Second, the supply-chain argument, which is under-appreciated: the delivery pipeline holds production credentials and executes third-party code on every run, so it deserves the same third-party risk thinking the institution applies to its business suppliers. The SBOM point lands well with anyone who lived through a widespread vulnerability disclosure - the difference between answering 'are we exposed?' in minutes versus weeks is entirely a function of whether the inventory was generated automatically. The caution: be explicit that you are teaching engineering patterns, not interpreting the institution's regulatory obligations, and that participants must validate specifics with their own risk, security and compliance colleagues."
        },
    ],

    "What the Platform Contributes to CI/CD": [
        {
            "type": "detail",
            "title": "In Context: A Golden Path for SARB Delivery Teams",
            "sections": [
                ("What the paved road would carry in this institution", [
                    "A scaffolded service: repository, pipeline, build, deploy manifests, dashboard, alerts, runbook stub.",
                    "Controls pre-wired: scanning, policy checks, four-eyes enforcement, immutable logs, evidence retention.",
                    "Standard environments from versioned IaC modules, with zoning, tagging and classification already correct.",
                    "Secrets injected by the platform; no team ever handles a production credential to deploy.",
                    "Change records and audit evidence generated by the pipeline rather than assembled by people afterwards.",
                ]),
                ("Why this is a control programme, not a convenience programme", [
                    "One assessed path beats forty hand-built ones: uniformity is what makes assurance affordable at all.",
                    "Improvements propagate: when the platform hardens a step, every consumer inherits it on the next run.",
                    "Scarce expertise (security, reliability, data protection) scales by being encoded, not by being scheduled.",
                    "Adoption rate becomes a meaningful indicator: how much delivery flows through the assessed path?",
                ]),
                ("Keeping the platform from becoming the new bottleneck", [
                    "Self-service is the test - if teams file tickets and wait, the wall has been rebuilt with better tooling.",
                    "Escape hatches stay open and documented: step off the road, and carry what the road was handling.",
                    "InnerSource the platform repositories so consuming teams contribute capability instead of queueing for it.",
                    "Measure time-to-first-deploy for a new service - it is the platform's clearest product KPI (Module 9).",
                ]),
            ],
            "notes": "Close Day 1 by pulling the two threads together, because this slide is the bridge into Day 2 and into the workshops. The central argument for a supervised institution is control uniformity: a single assessed golden path can be examined once, deeply, and every service that uses it inherits the result, whereas forty independently assembled pipelines cannot be assessed at any affordable cost. That reframing is what turns a platform initiative from an engineering preference into a fundable risk programme, and participants should take that sentence with them. The second point - propagation - is the compounding benefit: a hardening applied once reaches every consumer on their next run, which is the opposite of how copy-pasted pipelines behave. Then repeat the self-service test one final time, because it is the single most important idea in the platform half of the course and the easiest to lose: a platform that teams must queue for is a silo with better branding. Finish by naming time-to-first-deploy as the metric to baseline, and ask participants to find out their institution's current answer before Day 2 - it makes Module 9's platform canvas exercise concrete rather than theoretical."
        },
    ],
}


# ===========================================================================
# DAY 2 - DEEP DIVES
# Same convention as Day 1: keyed on the summary slide's title, inserted
# immediately after it.
# ===========================================================================
DAY2_DEEP_DIVES = {

    "Microservice Design Principles": [
        {
            "type": "detail",
            "title": "Deep Dive: Where to Draw the Boundary",
            "sections": [
                ("Boundaries follow BUSINESS domains, not technical layers", [
                    "A bounded context (Domain-Driven Design) owns one coherent business capability and its language.",
                    "Good: orders, payments, accounts, settlement, reporting - each with its own vocabulary and rules.",
                    "Bad: 'the API service', 'the worker service', 'the UI service' - one capability split across three deployments.",
                    "The heuristic: if a single business change needs edits in three services, the boundary is wrong.",
                ]),
                ("Independent deployability is the acid test", [
                    "Can this service be released today, alone, without coordinating another team's calendar? If not, it is not separate.",
                    "Two services that always ship together are ONE service paying the full cost of being two.",
                    "That cost is real: network calls, serialisation, partial failure, distributed tracing, more pipelines to run.",
                    "So the question is never 'should we do microservices?' but 'does this boundary buy independence?'",
                ]),
                ("Database per service - the rule people break first", [
                    "No shared tables. Integration happens through APIs and events, never through someone else's schema.",
                    "A shared database is the tightest coupling that exists: any schema change is a multi-team release.",
                    "It also destroys the failure isolation the split was supposed to buy - one bad query hurts everyone.",
                    "Cost to accept honestly: data consistency becomes eventual, and reporting needs a deliberate answer.",
                ]),
            ],
            "notes": "This is the slide that prevents the most expensive mistake in the module, so be direct: most disappointing microservice programmes failed at the boundary, not at the technology. Give the room the domain-versus-layer contrast and let them test their own systems against it - the split by technical layer is extremely common because it matches how teams are often organised, which is Conway's Law arriving on schedule. The independent-deployability test is the one sentence worth memorising, because it is falsifiable: participants can answer it today about their own services, and the answer is usually uncomfortable. On database-per-service, expect pushback - it is the hardest rule and the one most often broken for pragmatic reasons - so be balanced: the rule exists because a shared schema recreates the coupling the split was meant to remove, and if a team cannot accept it, that is a strong signal the boundary should not exist yet. Say plainly that a well-structured monolith with clear internal modules is a perfectly respectable architecture, and often the right one; the distributed version should be earned by a specific need (independent scaling, independent release cadence, or genuinely separate teams), not adopted as a default."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Integration and Partial Failure",
            "sections": [
                ("Smart endpoints, dumb pipes", [
                    "Business logic belongs in the services; the transport should be boring - HTTP, gRPC, a plain message broker.",
                    "The anti-pattern is the clever bus: orchestration, transformation and routing rules living in middleware.",
                    "That middleware becomes a shared, central, hard-to-change component owned by nobody and feared by everyone.",
                    "Choreography (events) or thin orchestration in a service is easier to reason about and to change.",
                ]),
                ("Synchronous or asynchronous - pick deliberately", [
                    "Synchronous request/response: simple, immediate, but couples availability - your caller inherits your downtime.",
                    "Asynchronous events: decoupled in time, resilient to outages, but eventual and harder to trace.",
                    "Rule of thumb: use sync when the caller genuinely needs the answer now; use events to notify that something happened.",
                    "Version your contracts and events from day one - a schema change is a public API change to somebody.",
                ]),
                ("Design for partial failure, because it is the normal state", [
                    "In a distributed system, something is always degraded somewhere - that is the operating condition, not an incident.",
                    "Timeouts on every call, retries with backoff AND jitter, circuit breakers on unhealthy dependencies.",
                    "Idempotency is essential once retries exist: the same request may genuinely arrive twice.",
                    "Graceful degradation is a product decision as much as a technical one - decide what 'reduced service' means.",
                ]),
            ],
            "notes": "Two ideas here that participants will meet immediately in the labs. First, smart endpoints and dumb pipes, which is a direct reaction to a generation of enterprise service buses that centralised logic and became change bottlenecks - a lesson worth naming carefully in institutions that still run integration platforms, because the point is not that middleware is bad but that BUSINESS logic in shared middleware is owned by nobody and slows everyone. Second, the sync/async decision: this is where distributed-system pain is decided, and the useful framing is availability coupling - a synchronous call means your service's availability is the product of everything downstream, whereas an event means the downstream can be down without you noticing. Introduce idempotency here rather than later, because it is the most commonly missed consequence of retries and it causes duplicate-processing incidents that are painful in any financial context: if a request can be retried, the receiver must be able to recognise and discard the duplicate, usually via a client-supplied key. Lab 07 makes graceful degradation concrete when the payment service is stopped and the order service keeps working with a reduced promise."
        },
    ],

    "Twelve-Factor Apps - the Portability Contract": [
        {
            "type": "detail",
            "title": "Deep Dive: The Factors That Actually Bite",
            "sections": [
                ("CONFIG in the environment, not in the artifact", [
                    "One image, many environments: endpoints, credentials and tuning are injected at runtime.",
                    "Test: could this exact image run in production and in test, with only the injected values differing?",
                    "If a rebuild is needed to change a setting, you have lost build-once-promote-many and its evidence trail.",
                    "Corollary: no environment names compiled into the code, and no 'if production' branches in business logic.",
                ]),
                ("STATELESS processes and backing services", [
                    "No user session, uploaded file or cached truth on the container's local disk - replicas must be interchangeable.",
                    "State goes to a declared backing service: database, cache, object store, message broker.",
                    "This is what allows the platform to kill, move, scale and reschedule your process without asking you.",
                    "Sticky sessions are a smell: they pin users to instances and quietly break rolling updates.",
                ]),
                ("LOGS as event streams to stdout", [
                    "The application writes to stdout/stderr; the platform collects, ships, indexes and retains.",
                    "Applications that manage their own log files fight the platform, fill disks, and lose data when a pod dies.",
                    "Structured (JSON) logs with correlation IDs make the difference between searchable and merely stored.",
                    "Retention, classification and access control then become platform concerns - handled once, correctly.",
                ]),
            ],
            "notes": "Twelve-factor predates Kubernetes by years but describes precisely the contract Kubernetes assumes your application already honours - so present these as the preconditions for everything in Module 6 rather than as style advice. Config-in-the-environment is the factor with the clearest business consequence: it is what makes build-once-promote-many possible, which is what makes the artefact digest a meaningful piece of change evidence. Statelessness is the factor most often violated by older applications, and it is worth being explicit that the violation is usually invisible until the first rolling update, when users are silently logged out or an upload lands on a pod that is about to disappear. On logs, the point that lands with operations audiences is ownership: an application that writes and rotates its own log files is doing a job the platform does better, and doing it in a way that loses data exactly when a container dies - which is exactly when you need it. Recommend structured logs with correlation IDs early, because retrofitting them across services is far more expensive than starting with them."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Disposability and Dev/Prod Parity",
            "sections": [
                ("Fast startup, graceful shutdown", [
                    "Orchestrators start and stop processes constantly - scaling, rolling, rescheduling, draining nodes.",
                    "Slow startup delays every rollout and every recovery; a 3-minute boot makes autoscaling useless.",
                    "On SIGTERM: stop accepting new work, finish in-flight requests, close connections, then exit.",
                    "Ignoring SIGTERM means the platform kills you mid-request - visible to users as random errors during deploys.",
                    "Combine with a readiness probe so traffic is removed BEFORE shutdown begins.",
                ]),
                ("Dev/prod parity - the gap that produces 'works in test'", [
                    "Same artefact, same shape, same backing-service types from laptop to production.",
                    "Containers plus IaC are what make parity achievable rather than aspirational.",
                    "Remaining differences must be deliberate and known: data volume, scale, network policy, real integrations.",
                    "The lab pattern (Compose locally, kind for Kubernetes) is exactly this principle at training scale.",
                ]),
                ("Using the contract as a review checklist", [
                    "Config injected, not baked? Stateless? Logs to stdout? Handles SIGTERM? Starts fast?",
                    "Any 'no' predicts a specific operational failure - name it, and the fix becomes obvious.",
                    "For legacy applications, treat the list as a migration backlog, not a pass/fail gate.",
                ]),
            ],
            "notes": "Disposability is the factor that connects most directly to the deployment strategies from Day 1: a service that cannot start quickly and shut down cleanly cannot participate in a rolling update without dropping requests, which is why teams conclude that 'zero-downtime deployment does not work here'. Walk the SIGTERM sequence explicitly, because most developers have never written it: stop accepting new work, drain in-flight requests, close resources, exit - and pair it with a readiness probe that removes the pod from traffic first. On parity, be honest that perfect parity is impossible and undesirable - production has data volumes, real integrations and network policy that no laptop should have - so the goal is that differences are deliberate and enumerated rather than accidental and discovered. The last section is the practical takeaway for institutions with a large legacy estate: nobody is going to rewrite everything, so use the checklist to predict which specific operational pain a given application will exhibit, and to sequence remediation by what hurts most."
        },
    ],

    "What a Container Actually Is": [
        {
            "type": "detail",
            "title": "Deep Dive: Processes, Not Machines",
            "sections": [
                ("The mechanism, in one paragraph", [
                    "A container is just a process (or a few) on the host kernel, with a restricted view and a resource budget.",
                    "NAMESPACES restrict what it can SEE: its own process tree, network stack, mounts, hostname, users.",
                    "CGROUPS restrict what it can USE: CPU shares, memory limits, I/O - enforced by the kernel.",
                    "There is no guest OS and no hypervisor, which is why start-up is milliseconds and overhead is negligible.",
                    "The image supplies the filesystem the process sees - not a kernel, just userland files.",
                ]),
                ("What follows from 'shared kernel'", [
                    "The kernel is the trust boundary: a container escape is a HOST compromise, not a VM breakout.",
                    "So least privilege matters more, not less: non-root, dropped capabilities, read-only filesystem, seccomp.",
                    "Sensitive multi-tenancy may still justify VM-level isolation, or hardened runtimes - it is a risk decision.",
                    "Kernel patching remains a host responsibility that containers do not remove.",
                ]),
                ("Images: layers, digests and tags", [
                    "An image is an ordered stack of immutable layers plus metadata, standardised by the OCI specification.",
                    "Layers are content-addressed and shared: fifty services on one base image store that base once.",
                    "The DIGEST (sha256:...) is the identity; a TAG is a mutable pointer that can be moved by anyone with push rights.",
                    "So promote and deploy by digest, and treat 'latest' as meaning 'unknown' in any controlled environment.",
                ]),
            ],
            "notes": "Get the mental model right here and everything in Module 7's hardening slide becomes obvious rather than arbitrary. The single most useful correction is that a container is not a small VM: it is a normal process with a restricted view, sharing the host kernel, which is why it starts in milliseconds and why its isolation is weaker than a hypervisor's. Say the security consequence plainly, because it is the reason the runtime-hardening controls exist: if a process escapes its namespace it is on the host, so non-root execution, dropped capabilities and seccomp profiles are baseline hygiene rather than paranoia. The tag-versus-digest point is the one that matters most operationally in a controlled environment: a tag is a pointer that someone can move, so 'we deployed version 1.4.2' is only true if nobody re-pushed that tag, whereas a digest is cryptographic identity. Recommend digest-based promotion in pipelines and digest recording in change records - it converts a claim into evidence."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Registries, Promotion and What Containers Do Not Fix",
            "sections": [
                ("Registries as the promotion boundary", [
                    "The registry stores the immutable artefact that moves, unchanged, from test to production.",
                    "Access control, retention, immutability settings and scanning all belong at this boundary.",
                    "Signing (cosign) and provenance attach 'who built this, from what commit' to the artefact itself.",
                    "Private registries or pull-through caches also remove a dependency on an external service at deploy time.",
                ]),
                ("What containers give you", [
                    "Environment parity: the dependency set travels with the application instead of living in a runbook.",
                    "Density and speed: many workloads per host, starting in milliseconds, scaling in seconds.",
                    "Immutability by default: you rebuild rather than patch, so instances stay identical to a reviewed definition.",
                    "Portability across hosts and clouds - the workload is decoupled from the machine it happens to run on.",
                ]),
                ("What containers do NOT give you", [
                    "They do not make an application stateless, well-designed, or safe to run twice - that is 12-factor work.",
                    "They do not remove the need to patch: your base image ages, and yesterday's clean scan is not today's.",
                    "They do not provide isolation equivalent to a VM - see the trust-boundary point on the previous slide.",
                    "They do not fix data: databases, migrations and backups need the same care they always did.",
                ]),
            ],
            "notes": "The registry deserves more attention than it usually gets, because it is where several controls naturally belong: access, immutability, retention, scanning, signing and provenance. Frame it as the promotion boundary - the physical embodiment of build-once-promote-many from Day 1 - and note that in a controlled environment the ability to state 'this exact digest, built from this commit, scanned with this result, signed by this pipeline' is a complete answer to a whole category of audit questions. The what-containers-do-not-give-you section is there to prevent overselling, which is how technology adoptions lose credibility: containers are a packaging and isolation mechanism, not an architecture, and a badly behaved application in a container is a badly behaved application that now starts faster. The patching point is worth dwelling on with security-minded participants: an image is a frozen snapshot of a distribution at build time, so a service that has not been rebuilt for six months is running six-month-old packages regardless of how clean its original scan was - which is the argument for regular automated rebuilds."
        },
    ],

    "Building Good Images": [
        {
            "type": "detail",
            "title": "Deep Dive: Small, Fast, Cacheable",
            "sections": [
                ("MULTI-STAGE builds - ship the runtime, not the workshop", [
                    "Stage 1 (builder): compilers, headers, build tools, test dependencies - everything needed to produce the artefact.",
                    "Stage 2 (runtime): a slim base plus the built artefact, copied across. Nothing else travels.",
                    "Result: a smaller image, a much smaller CVE surface, and no compiler available to an attacker in production.",
                    "This single practice usually removes more scanner findings than any triage effort.",
                ]),
                ("LAYER ORDER decides your build time", [
                    "Layers are cached and invalidated in order: change one, and everything after it rebuilds.",
                    "So copy the dependency manifest and install dependencies BEFORE copying source code.",
                    "Reversed, every one-line code change reinstalls the full dependency tree - minutes wasted on every commit.",
                    "Same reasoning applies to CI cache keys: cache on the manifest hash, not on the whole repository.",
                ]),
                ("BASE IMAGE choice is a security decision", [
                    "Smallest sensible base: slim variants, or distroless where the language runtime allows it.",
                    "Fewer packages = fewer CVEs to triage, and less for an attacker to use if they land inside.",
                    "PIN the base version (and ideally the digest) - 'python:3' silently changes underneath you.",
                    "Rebuild regularly on a schedule: an image that has not been rebuilt is accumulating known vulnerabilities.",
                ]),
            ],
            "notes": "These are the practices with the largest measurable payoff in the whole containerisation module, so make them concrete with numbers where you can: a naive image often runs to several hundred megabytes and hundreds of scanner findings, while a multi-stage build onto a slim or distroless base commonly lands an order of magnitude smaller with a fraction of the findings - and the reduction costs nothing but a better Dockerfile. Link it directly to Module 7's triage discipline: the cheapest way to reduce vulnerability backlog is to ship less software, not to argue about severities. The layer-ordering point is what participants will feel first in the labs, because it is the difference between a ten-second and a three-minute rebuild loop, and that difference compounds across every commit of every team. On base images, the scheduled-rebuild recommendation is the one most organisations miss: images are frozen snapshots, so without an automated periodic rebuild your fleet's vulnerability posture degrades even when nobody changes any code."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Orchestrator-Friendly and Safe by Default",
            "sections": [
                ("Run as NON-ROOT, and mean it", [
                    "Create a user in the image and declare USER - root inside a container is root on the kernel it shares.",
                    "Add a read-only root filesystem and writable volumes only where genuinely needed.",
                    "Drop all Linux capabilities and add back only what is required - almost always nothing.",
                    "These are image-level choices that make the runtime controls in Module 7 possible rather than aspirational.",
                ]),
                ("Make the image easy for the platform to operate", [
                    "HEALTHCHECK / probe endpoints so the orchestrator can tell 'started' from 'actually serving'.",
                    "Handle SIGTERM and shut down gracefully, or expect dropped requests on every rollout.",
                    "Log to stdout, exit with meaningful codes, and keep start-up fast.",
                    "Declare resource expectations honestly so requests and limits can be set from evidence, not guesswork.",
                ]),
                ("Build hygiene that prevents leaks", [
                    "Use .dockerignore: the build context is not your whole repository, and secrets hide in .git and .env.",
                    "A secret added in one layer and deleted in the next is STILL in the image history - never bake credentials.",
                    "Use build secrets or runtime injection; scan images for secrets as part of the pipeline.",
                    "Label images with the commit SHA and build metadata so a running container can be traced to its source.",
                ]),
            ],
            "notes": "The non-root discussion connects straight back to the shared-kernel point: root in a container is root on the host kernel if anything escapes, so the image-level USER declaration is the foundation that the cluster-level security context enforces. Point out that this is a shared responsibility between the image author and the platform, which is why Module 7 argues for platform defaults - the golden path should make the safe configuration the default one, so teams inherit it. The build-hygiene section prevents a specific, common and painful incident: credentials committed into image layers. Say the layer-history point explicitly because it surprises people - deleting a file in a later layer does not remove it from the image, it merely hides it from the final filesystem view, and anyone who pulls the image can extract it. That is why secret scanning belongs in the pipeline and why credentials must be injected at runtime rather than built in. Finally, the labelling advice pays for itself the first time someone needs to know which commit produced the container currently misbehaving in production."
        },
    ],

    "Why Orchestration - What Kubernetes Actually Does": [
        {
            "type": "detail",
            "title": "Deep Dive: The Reconciliation Engine",
            "sections": [
                ("What one host and 'docker run' cannot do", [
                    "Reschedule your workload when the machine dies - somebody has to notice and act.",
                    "Scale out and back with demand, and place work where there is actually capacity.",
                    "Roll out a new version gradually, verify it, and roll back without downtime.",
                    "Load-balance across replicas, and remove unhealthy ones from traffic automatically.",
                ]),
                ("The control loop, which is the whole idea", [
                    "You declare DESIRED state ('five replicas of this image, these limits, these probes').",
                    "Controllers observe ACTUAL state, compute the difference, and act to close it. Forever.",
                    "Self-healing is not a feature bolted on - it is that loop noticing a difference and correcting it.",
                    "Same model as Terraform (Day 1), but running continuously instead of when a human types apply.",
                ]),
                ("Why declarative APIs matter more than the scheduler", [
                    "Everything is an object with a spec and a status, reachable through one consistent API.",
                    "So everything above it can be automated: GitOps agents, operators, autoscalers, policy admission.",
                    "That extensibility - not container scheduling - is why the ecosystem consolidated on Kubernetes.",
                    "And the honest caveat: this power costs real operational complexity, which the next slide prices.",
                ]),
            ],
            "notes": "Land the reconciliation model rather than a feature list, because it explains behaviour participants will otherwise find surprising - why deleting a pod does not remove it, why editing a live object gets reverted by a controller, why the cluster keeps trying forever. Draw the loop on the flipchart: observe, compare, act, repeat. Then connect it explicitly to Terraform from Day 1: the same declarative-plus-converge idea, with the difference that Kubernetes runs the loop continuously rather than on demand, which is precisely what makes self-healing possible. The third section is the strategic point worth making to senior participants: Kubernetes won not because it schedules containers well but because it exposed everything as a uniform declarative API, which turned operations into programmable objects and allowed an ecosystem of controllers, operators and policy engines to grow on top. Finish by flagging the cost honestly - complexity is real and must be justified - because the next deep dive is precisely about when NOT to adopt it, and stating that early buys credibility for everything else in the module."
        },
        {
            "type": "detail",
            "title": "Deep Dive: What It Costs, and When Not to Use It",
            "sections": [
                ("What the platform gives you, concretely", [
                    "Scheduling by declared resource requests, with spread, affinity and node selection rules.",
                    "Self-healing: failed pods replaced, failed liveness probes restarted, unready pods pulled from traffic.",
                    "Rollouts and rollbacks as first-class operations with revision history.",
                    "Service discovery and load balancing without any application-level registry.",
                    "A uniform place to apply policy, quotas, network rules and identity across every workload.",
                ]),
                ("What it costs - say this out loud before adopting", [
                    "A cluster is production infrastructure: upgrades, certificates, capacity, backups, security patching.",
                    "A steep vocabulary: every team must learn objects, probes, limits, RBAC, networking, storage classes.",
                    "New failure modes: scheduling pressure, evictions, DNS, network policy, misconfigured probes.",
                    "This is exactly the cognitive load a platform team exists to absorb (Day 1, Module 1).",
                ]),
                ("When something simpler is the professional choice", [
                    "A handful of stable services on a few hosts: containers plus a managed runtime is often enough.",
                    "One team, one deployable, predictable load: an orchestrator adds cost with little return.",
                    "Adopt when you have real scale, real elasticity needs, or many teams needing a common runtime contract.",
                    "If you do adopt, prefer managed control planes and let the platform team own the cluster, not each team.",
                ]),
            ],
            "notes": "Being honest about cost is what makes the recommendation credible, and this audience will respect it. Kubernetes is production infrastructure with its own upgrade cycle, certificate expiries, capacity planning and security patching - adopting it means someone signs up to operate it forever, and 'the team that also builds our services' is usually the wrong answer. Give the room permission to conclude that they do not need it yet: a small number of stable services on managed container hosting is a perfectly professional architecture, and choosing it deliberately is better engineering than adopting an orchestrator because it is expected. Then give the conditions that genuinely justify it - multiple teams needing a common runtime contract, real elasticity, or a scale that makes manual placement untenable - and the adoption advice that follows: a managed control plane where available, and cluster operation owned centrally so that product teams consume a runtime rather than run one. That is the cognitive-load argument from Day 1 applied to the single biggest source of it."
        },
    ],

    "The Working Vocabulary: Objects You Will Touch": [
        {
            "type": "detail",
            "title": "Deep Dive: Pods, Deployments and Services",
            "sections": [
                ("POD - the unit of scheduling, and mortal by design", [
                    "One or more containers that share a network namespace and can share volumes - always co-scheduled.",
                    "Pods are cattle: replaced, never repaired. No stable IP, no stable identity, no attachment.",
                    "Sidecar pattern: a second container for logging, proxying or secrets - powerful, but it is still one unit.",
                    "You will rarely create pods directly; a controller creates them from a template.",
                ]),
                ("DEPLOYMENT - desired replicas plus rollout behaviour", [
                    "Holds the pod template, the replica count and the update strategy (maxSurge / maxUnavailable).",
                    "Creates a ReplicaSet per revision, which is what makes rollback a first-class operation.",
                    "kubectl rollout undo returns to the previous ReplicaSet - seconds, not a rebuild.",
                    "For stateful workloads, StatefulSet gives stable identity and ordered rollout - different rules apply.",
                ]),
                ("SERVICE - a stable address over a moving set of pods", [
                    "Pods come and go; the Service name and virtual IP stay constant for the life of the service.",
                    "Selection is by LABEL, which is why label discipline matters more than it first appears.",
                    "ClusterIP for internal, NodePort for simple external access (our labs), LoadBalancer/Ingress in real clusters.",
                    "Readiness probes decide membership: an unready pod is removed from the Service's endpoints automatically.",
                ]),
            ],
            "notes": "Teach the ownership chain as a single sentence participants can repeat: a Deployment owns ReplicaSets, a ReplicaSet keeps N Pods running, and a Service load-balances over Pods selected by label. Almost every confusing Kubernetes behaviour becomes obvious once that chain is clear - why deleting a pod is pointless, why a rollback is instant, why a service silently returns nothing when a label is misspelled. The mortality of pods deserves emphasis for participants with a VM background, because the instinct to log in and fix a sick instance is exactly wrong here and produces state that the next reconciliation discards. Mention StatefulSet briefly so the room knows the stateful path exists and has different rules, without going deep - most first workloads are stateless, and stateful services in a cluster deserve their own careful conversation. In Workshop 2 participants create all of these objects and then deliberately break a label selector, which is the fastest way to internalise why the Service found no endpoints."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Config, Probes and Resource Limits",
            "sections": [
                ("ConfigMap and Secret - twelve-factor, realised", [
                    "Configuration injected as environment variables or mounted files, so one image serves every environment.",
                    "Secrets are base64-ENCODED, not encrypted, by default - treat them as sensitive objects and control access.",
                    "For real secret management, integrate a manager (Vault, cloud KMS, external-secrets) rather than committing values.",
                    "Changing a ConfigMap does not restart pods by itself - roll the Deployment or use a checksum annotation.",
                ]),
                ("PROBES - how the platform knows what is happening", [
                    "Readiness: 'send me traffic'. Fails -> removed from the Service, but NOT restarted.",
                    "Liveness: 'I am alive'. Fails -> the container is restarted. Get this wrong and you get restart loops.",
                    "Startup: for slow starters, so a long boot is not mistaken for a liveness failure.",
                    "Probe endpoints must be cheap and must not depend on downstream systems, or one outage cascades everywhere.",
                ]),
                ("REQUESTS and LIMITS - the resource contract", [
                    "Requests are what the scheduler reserves for you; limits are the ceiling you may not exceed.",
                    "No requests means the scheduler is guessing, and your pod is first to be evicted under pressure.",
                    "Exceeding a memory limit is an immediate kill (OOMKilled); exceeding CPU means throttling, not death.",
                    "Set them from observed usage, revisit them, and let the platform default sensible values for new services.",
                ]),
            ],
            "notes": "Three areas where mistakes are common and consequences are visible. On Secrets, correct the widespread misunderstanding immediately: Kubernetes Secrets are encoded rather than encrypted at rest by default, so they protect against accidental display, not against someone with cluster access - which is why a real secrets manager and tight RBAC belong in the golden path. On probes, the liveness-versus-readiness distinction causes more self-inflicted outages than almost anything else: a liveness probe that checks a downstream dependency will restart healthy containers during someone else's outage and turn a partial degradation into a full one, so probes must be cheap, local and honest about what they assert. On resources, give the practical guidance - set requests from observed usage, understand that memory limits kill instantly while CPU limits merely throttle, and expect to iterate. Note that all three of these are exactly the kind of thing the golden path should set sensible defaults for, so that a new service is well-behaved before anyone has read the documentation."
        },
    ],

    "Managing Services at Scale": [
        {
            "type": "detail",
            "title": "Deep Dive: Scaling, Meshes and Blast Radius",
            "sections": [
                ("AUTOSCALING - three different levers", [
                    "HPA scales the number of pods on observed metrics (CPU, memory, or custom/business metrics).",
                    "Cluster autoscaler adds and removes NODES when pods cannot be scheduled or capacity is idle.",
                    "VPA right-sizes requests and limits from observed usage - useful, and it conflicts with HPA on the same metric.",
                    "Autoscaling only works if start-up is fast and the app is stateless - twelve-factor is the prerequisite.",
                ]),
                ("SERVICE MESH - real capability, real cost", [
                    "Gives you mTLS between services, retries and timeouts, traffic splitting and rich telemetry - without app changes.",
                    "Costs: a sidecar per pod, another control plane to operate, upgrade cycles, and much harder debugging.",
                    "Adopt when you have a specific need - zero-trust between services, or canary traffic control at scale.",
                    "Do not adopt because the architecture diagram looks better with it; a handful of services rarely justifies it.",
                ]),
                ("BLAST RADIUS before exotic scaling", [
                    "Multiple clusters or regions isolate failure long before they solve a scaling problem.",
                    "Separate environments and, where justified, separate clusters for critical and non-critical workloads.",
                    "Namespace, quota and network-policy boundaries are the cheap version of the same idea.",
                    "Decide deliberately what shares fate with what - that decision IS your availability design.",
                ]),
            ],
            "notes": "The theme of this slide is that scale problems are platform problems, and product teams should inherit answers rather than derive them. On autoscaling, the prerequisite deserves emphasis: horizontal scaling assumes interchangeable, fast-starting, stateless replicas, so an application that violates twelve-factor cannot be autoscaled no matter what the configuration says. Mention the HPA/VPA conflict because teams hit it and are baffled. On service mesh, take a clear position: it is a genuinely powerful capability with a genuinely large operating cost, and the honest test is whether there is a specific requirement - mutual TLS between services as a security control, or fine-grained traffic shifting for progressive delivery - that cannot be met more simply. In a supervised institution, service-to-service mTLS is often that requirement, so the conversation is legitimate; the mistake is adopting it before the basics are stable. The blast-radius section is the most valuable one for this audience: deciding what shares fate with what is an availability design decision, and it is usually made by accident."
        },
        {
            "type": "detail",
            "title": "Deep Dive: GitOps and the Platform's Share of the Work",
            "sections": [
                ("GITOPS at runtime", [
                    "The desired state of each environment lives in Git; an in-cluster agent (Argo CD, Flux) reconciles continuously.",
                    "Deployment becomes a merge, rollback becomes a revert, and the audit trail is the commit history.",
                    "Drift is corrected automatically, so the emergency manual change does not quietly become permanent.",
                    "No cluster credentials leave the cluster - the pipeline never needs production access.",
                ]),
                ("What the platform should own, not each team", [
                    "Cluster lifecycle: version upgrades, certificates, node images, capacity, backups and restore drills.",
                    "Baseline policy: pod security defaults, network policy, quotas, admission control, image provenance.",
                    "Shared services: ingress, DNS, certificates, secrets integration, observability stack, log retention.",
                    "Golden-path templates so a new service arrives with sane probes, limits, labels and dashboards.",
                ]),
                ("What each product team should still own", [
                    "Their service's behaviour: probes, resource needs, dependencies, degradation strategy, runbook.",
                    "Their SLOs and their alerts - reliability targets are a product decision, not a platform default.",
                    "Their own rollout choices within the paved road, and the consequences of stepping off it.",
                    "The pager for their service: ownership follows the code, and the platform makes that affordable.",
                ]),
            ],
            "notes": "Close Module 6 by drawing the ownership line explicitly, because it is the question participants will face the moment they get back: who does what. The platform owns everything that is identical for every team and expensive to get right - cluster lifecycle, baseline policy, shared services, templates - and product teams own everything specific to their service's behaviour and reliability. Getting that line wrong in either direction causes predictable pain: platform teams that own service configuration become a ticket queue, and product teams that own cluster upgrades stop shipping features. On GitOps, repeat the two properties that matter in a controlled environment - credentials stay in the cluster, and drift is corrected rather than accumulated - and note the practical prerequisite that out-of-band changes genuinely stop working, which requires agreement before it is switched on. This slide also sets up Module 9 nicely: everything on the platform's list is a product with users, and the next module is about treating it that way."
        },
    ],

    "The Scanner Taxonomy - What Checks What, When": [
        {
            "type": "detail",
            "title": "Deep Dive: Six Scanners, Six Different Questions",
            "sections": [
                ("Code and dependencies", [
                    "SAST reads YOUR source for flaw patterns - injection, unsafe deserialisation, crypto misuse. Runs at PR time.",
                    "Its weakness is false positives: tune it, or developers learn to ignore the whole category.",
                    "SCA inventories your DEPENDENCIES against vulnerability databases - and this is where most real risk lives.",
                    "You write thousands of lines; you import millions. The imported millions are the larger attack surface.",
                ]),
                ("Secrets and configuration", [
                    "Secret scanning finds credentials in code AND in history - run it on every commit and continuously.",
                    "History matters: a key committed last year is still exposed today, and rotation is the only real fix.",
                    "IaC/config scanning (trivy config, checkov) catches misconfiguration BEFORE the resource exists.",
                    "Typical finds: public storage, missing encryption, permissive rules, containers without limits or as root.",
                ]),
                ("Artefact and running system", [
                    "Image scanning (Trivy) inspects the built artefact's OS and language packages - at build, on every image.",
                    "It sees what actually ships, including whatever the base image dragged along - which is why slim bases win.",
                    "DAST probes the RUNNING application from outside: authentication, headers, injection against a live target.",
                    "DAST belongs in staging on a schedule - it is slower, noisier, and needs a deployed environment.",
                ]),
            ],
            "notes": "The point of the taxonomy is to stop the common failure of buying one scanner and believing security is handled. Each tool answers a different question about a different artefact at a different moment, and the gaps between them are where incidents live. Emphasise the SCA point hard, because it reallocates effort correctly: the overwhelming majority of exploitable vulnerability in modern applications arrives through dependencies rather than through code the team wrote, so an organisation with limited capacity should start with dependency and secret scanning rather than the most sophisticated static analyser on the market. On SAST, be honest about false positives - an untuned SAST rollout is the fastest way to teach an organisation to ignore security tooling, which is worse than not deploying it. On secret scanning, stress history: the default assumption must be that anything ever committed is compromised, so detection must be paired with a rotation process, not just an alert."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Placing Scanners Where They Pay",
            "sections": [
                ("Earlier is cheaper - the economics that drive shift-left", [
                    "At the keyboard: a linter or pre-commit hook costs seconds and nobody else ever sees the defect.",
                    "At PR time: a comment and a fix in the same context the developer is already holding in their head.",
                    "At build: a rebuild, which is minutes and mildly annoying.",
                    "In production: an incident, a disclosure process, and everyone's afternoon. Same defect, wildly different cost.",
                ]),
                ("Speed decides adoption", [
                    "Anything on the PR path must be fast - a scanner that adds ten minutes will be routed around.",
                    "Put fast, high-signal checks in the PR gate; run the slow, thorough sweeps on a schedule.",
                    "Cache vulnerability databases in CI (our labs pre-pull the Trivy DB) so scans are seconds, not minutes.",
                    "Deduplicate: the same finding reported by three tools in three formats trains people to ignore all three.",
                ]),
                ("Make the output usable, or it will be ignored", [
                    "Emit machine-readable results (SARIF/JSON), retained per build - that is your evidence trail.",
                    "Route findings to owners automatically; an unowned finding is a finding nobody will fix.",
                    "Report broadly, gate narrowly - the Day 1 rule, applied to every scanner in the taxonomy.",
                    "Watch the TREND, not today's count: is the fixable backlog shrinking week on week?",
                ]),
            ],
            "notes": "This slide is about making scanning stick rather than about scanning itself. The cost curve is the argument that funds the work, and it is worth stating in the room's own terms: the same defect costs seconds at the keyboard, minutes in a pull request and an incident in production, so every step earlier is a multiplier on the security budget you already spend. The speed point is the practical constraint everyone underestimates - developers experience the PR gate on every change, so a slow scanner is not merely irritating, it actively erodes the practice as people find ways around it. Give the concrete mitigations: cache the databases, split fast gates from scheduled deep sweeps, and deduplicate across tools. On output, repeat the report-versus-gate discipline from Day 1 and add the ownership point, which is where most programmes quietly fail: findings that arrive in a shared dashboard with no owner accumulate indefinitely, and the accumulating number then becomes an argument against the tooling rather than against the vulnerabilities."
        },
    ],

    "Supply Chain Security - Your Pipeline Is a Target": [
        {
            "type": "detail",
            "title": "Deep Dive: How Build Systems Get Compromised",
            "sections": [
                ("The lesson of the SolarWinds compromise", [
                    "Attackers did not breach the customers - they breached the BUILD system of a trusted supplier.",
                    "Legitimately signed updates then carried the attacker's code into thousands of environments.",
                    "The insight: your build infrastructure has the same privilege as everything it can deploy to.",
                    "So the pipeline deserves the protection you give production - because it effectively IS production.",
                ]),
                ("The links in your own chain", [
                    "Dependencies: typosquatting, hijacked maintainer accounts, malicious post-install scripts.",
                    "Base images: a tag that moves under you, or an unmaintained image nobody owns.",
                    "CI actions and plugins: third-party code executing with your repository and registry credentials.",
                    "Build infrastructure: runners, caches, and anything with push rights to your registry.",
                    "Registries: a tag repointed to a different artefact after approval - which digests prevent.",
                ]),
                ("Countermeasures in the order they pay off", [
                    "PIN everything - versions and digests. A moving reference is an unreviewed change with production access.",
                    "LEAST PRIVILEGE - scope tokens per job, prefer short-lived federated credentials over stored secrets.",
                    "SBOM on every build - a machine-readable inventory of what is actually inside the artefact.",
                    "SIGN and VERIFY (cosign) - so the cluster accepts only artefacts your pipeline actually produced.",
                    "SLSA levels give you a maturity ladder: decide which level each service needs, then work toward it.",
                ]),
            ],
            "notes": "Use SolarWinds because it changed how the industry thinks: the attack succeeded by compromising a build system rather than any customer, and the resulting artefacts were legitimately signed, which defeated every downstream control that trusted the signature. The generalisable lesson for participants is that their pipeline holds production credentials and executes third-party code on every run, so it deserves production-grade protection and third-party risk assessment - the same scrutiny their institution applies to suppliers. Walk the links and ask the room which ones they could currently enumerate: most organisations cannot list the third-party actions running in their pipelines, which is itself the finding. Then give the ordered countermeasures, because sequencing matters when capacity is limited: pinning and least privilege are cheap and remove whole categories of risk today, SBOM makes the next widespread disclosure survivable, and signing plus verification closes the loop between what the pipeline built and what the runtime accepts. SLSA is worth naming as the maturity framework so participants have a vocabulary for setting targets rather than arguing about perfection."
        },
        {
            "type": "detail",
            "title": "Deep Dive: SBOM, Provenance and the Disclosure Test",
            "sections": [
                ("SBOM - the inventory you will wish you had", [
                    "A machine-readable list of every component in an artefact, with versions - Trivy can emit one per build.",
                    "Store it with the artefact, keyed by digest, so any historical image can be queried later.",
                    "The test that proves its value: 'a critical flaw was announced this morning - where are we exposed?'",
                    "With SBOMs, that is a query answered in minutes. Without them, it is a survey answered in weeks.",
                ]),
                ("Provenance and signing", [
                    "Provenance records HOW an artefact was built: which commit, which pipeline, which inputs.",
                    "Signing (cosign) binds identity to the artefact so consumers can verify origin cryptographically.",
                    "Verification at admission means the cluster rejects anything not built by your pipeline - a real control.",
                    "Together they answer 'is this artefact ours, and what is it made of?' without trusting a spreadsheet.",
                ]),
                ("Where to start on Monday", [
                    "Pin your CI actions to digests - an afternoon of work, and it removes a standing exposure.",
                    "Declare least-privilege permissions on every workflow - one line each, immediate risk reduction.",
                    "Turn on SBOM generation and retention in the pipeline - cheap now, decisive during the next disclosure.",
                    "Then, deliberately: signing on push, verification at admission, and a documented SLSA target.",
                ]),
            ],
            "notes": "The disclosure test is the most persuasive thing on this slide for anyone who lived through a widespread vulnerability announcement: the organisations that answered 'are we exposed?' in hours were the ones with artefact inventories, and the ones that answered in weeks did so by emailing teams and reading build logs. Frame SBOM as insurance whose premium is a single pipeline step, and note the storage detail that makes it useful - keyed by digest, retained with the artefact, queryable for historical images, because the question always arrives about something built months ago. On signing and verification, emphasise that the value comes from the pair: signing alone is a claim, while verification at admission turns it into an enforced control that a compromised registry entry cannot bypass. Close with the Monday list, deliberately ordered by effort-to-value, so participants leave with two changes they can genuinely make this week and a longer-term direction that does not require a programme to start."
        },
    ],

    "Compliance as Code (OPA, Rego, Conftest)": [
        {
            "type": "detail",
            "title": "Deep Dive: From Wiki Rules to Enforced Guarantees",
            "sections": [
                ("Why written standards decay", [
                    "A standard in a document is checked by humans, occasionally, under deadline pressure - so it drifts.",
                    "Nobody knows the compliance rate; the honest answer to 'are we compliant?' is 'probably, mostly'.",
                    "Encoded policy is evaluated on EVERY change, automatically, with a recorded result. The answer becomes exact.",
                    "The standard stops being a document people should have read and becomes a check they cannot forget.",
                ]),
                ("OPA and Rego - one engine, many targets", [
                    "Open Policy Agent evaluates rules written in Rego against any JSON/YAML input.",
                    "That means one policy language for Kubernetes manifests, Terraform plans, pipeline configs and API requests.",
                    "Policies are code: reviewed, versioned, TESTED with their own unit tests, and released deliberately.",
                    "Write the failure message for a human: it must say what is wrong and how to fix it, or it will be resented.",
                ]),
                ("Two enforcement points, one rule", [
                    "Conftest in CI evaluates the change before merge - the developer fixes it in context, cheaply.",
                    "An admission controller in the cluster rejects non-conforming objects however they arrived - the backstop.",
                    "CI alone governs only those who use CI; admission alone gives feedback far too late. Use both.",
                    "Same policy file feeding both, so there is exactly one definition of the rule in the institution.",
                ]),
            ],
            "notes": "The opening argument is the one that wins over governance colleagues: a standard written in a document has an unknown compliance rate, while an encoded policy has an exact one, evaluated on every change and recorded. That is a genuine improvement in control effectiveness, not merely an engineering convenience. On Rego, do not attempt to teach the language - participants only need to know that policies are code with tests and reviews, and that one engine covers manifests, infrastructure plans and pipelines, which avoids three separate policy tools with three separate rule sets. The advice about failure messages is small and disproportionately important: a policy that fails with an opaque expression evaluation error generates support tickets and resentment, while one that says 'container must set resource limits - add resources.limits.memory' generates a fix. On enforcement points, insist on both and on a single shared policy definition, because the failure mode is two drifting copies of the same rule that disagree at the worst moment."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Test What Ships, and Evidence for Free",
            "sections": [
                ("Evaluate the RENDERED output, not the source", [
                    "Helm, Kustomize and templating add labels, defaults and patches at render time.",
                    "A policy run against raw templates is testing a draft that never reaches the cluster.",
                    "So render first (helm template / kustomize build), then evaluate the result - that is what actually ships.",
                    "Same principle for Terraform: evaluate the PLAN output, not the .tf source, for the same reason.",
                ]),
                ("Rolling out policy without a revolt", [
                    "Start in warn/dry-run mode and publish the current violation count - measure before enforcing.",
                    "Fix the backlog with the teams, or provide an automated migration, before you flip to blocking.",
                    "Then enforce for NEW resources first, with a dated deadline for existing ones.",
                    "Keep an explicit exception path: owned, time-limited, reviewed - never a permanent silent bypass.",
                ]),
                ("The audit story writes itself", [
                    "What the rule is: the policy file, in Git, with its version history and reviewers.",
                    "That it was enforced: the pipeline run and admission logs, per change, retained.",
                    "What was excepted and why: the exception record, with owner and expiry date.",
                    "That is a stronger control narrative than a document plus a sample-based annual review.",
                ]),
            ],
            "notes": "The render-first point prevents a subtle and common failure where teams believe they are enforcing a rule while testing something that never ships - templating tools inject exactly the labels, defaults and security contexts that policies most often check, so evaluating raw templates produces false confidence. The rollout advice is what makes policy programmes survive contact with real teams: measure first in warning mode so you know the size of the problem, fix or migrate the backlog, then enforce for new resources with a dated deadline for the rest. Flipping a blocking policy on across an existing estate is how a security team spends its credibility in one afternoon. The exception path is non-negotiable in a regulated institution and should be presented as a control rather than a weakness: owned, time-limited and reviewed exceptions are visible and manageable, while the alternative is invisible workarounds. Close on the audit narrative, which is the reason this practice is worth the effort here: policy as code turns 'we have a standard' into 'here is the rule, here is every evaluation of it, and here is every exception with its expiry'."
        },
    ],

    "Runtime Hardening - Platform Defaults, Not Team Chores": [
        {
            "type": "detail",
            "title": "Deep Dive: Hardening the Workload and the Cluster",
            "sections": [
                ("Container-level defaults every workload should inherit", [
                    "runAsNonRoot with an explicit user - root in a container is root on the shared kernel if anything escapes.",
                    "readOnlyRootFilesystem, with writable volumes only where genuinely required.",
                    "drop ALL capabilities, then add back only what is proven necessary (usually nothing).",
                    "allowPrivilegeEscalation: false, plus a seccomp profile to restrict available syscalls.",
                    "No host mounts, no host network, no privileged containers - these are escapes with a friendly name.",
                ]),
                ("Cluster-level controls", [
                    "RBAC with least privilege: no wildcard cluster-admin bindings, and service accounts scoped per workload.",
                    "NetworkPolicies with a DEFAULT-DENY posture - without them, every pod can reach every other pod.",
                    "Namespaces with quotas and limits so one workload cannot starve the rest.",
                    "Admission control to enforce the above, so a non-conforming workload simply cannot be created.",
                ]),
                ("Secrets, properly", [
                    "Use a manager (Vault, cloud KMS, external-secrets) rather than raw Kubernetes Secret objects.",
                    "Kubernetes Secrets are base64-encoded, not encrypted by default - enable encryption at rest and tight RBAC.",
                    "Rotate on a schedule and on every suspicion; never print secrets to logs or dump the environment.",
                    "Prefer short-lived, workload-identity-based credentials over long-lived static ones wherever available.",
                ]),
            ],
            "notes": "Present these as a specification for the golden path rather than as a checklist for every team, because that is the module's whole argument: expecting forty teams to independently derive and maintain the same security context guarantees inconsistency, while encoding it once in a template and enforcing it at admission guarantees the opposite. The default-deny network policy point deserves emphasis for anyone assuming cluster networking is segmented: by default every pod can reach every other pod, which surprises people whose mental model comes from network zones, and it is one of the highest-value controls to enable early. On secrets, correct the encoding-versus-encryption misunderstanding again if it did not land in Module 6, and push workload identity as the strategic direction: short-lived credentials issued to a workload identity remove the standing secret entirely, which is a stronger control than rotating a stored one. Note that everything here is verifiable by the policy engine from the previous slide, which is what turns this list from advice into an enforced baseline."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Why Defaults Beat Documentation",
            "sections": [
                ("The failure of the standards-document model", [
                    "Every team re-derives the same configuration, differently, with different mistakes.",
                    "Under deadline pressure the security section is the first thing quietly dropped.",
                    "Nobody can enumerate the resulting posture, so assurance is sampling rather than knowing.",
                    "And the burden falls on the people with the least security context - the delivery teams.",
                ]),
                ("What 'secure by default' looks like in practice", [
                    "The scaffolded service arrives with the security context, network policy and limits already set.",
                    "Admission control enforces the baseline, so an unsafe workload cannot be created by accident.",
                    "Deviations are explicit, owned and reviewed - visible instead of invented.",
                    "The compliant configuration is also the easiest one, which is the only sustainable design.",
                ]),
                ("Verify continuously, not annually", [
                    "Policy evaluation on every change; drift detection on what is actually running.",
                    "Scheduled rebuilds so images do not silently age into vulnerability.",
                    "Periodic RBAC and network-policy review - permissions accumulate quietly over time.",
                    "Report the posture as a trend to leadership: coverage, exceptions, and their expiry dates.",
                ]),
            ],
            "notes": "This slide is the security half of the platform argument, and it deserves to be made in control language: forty independently-configured services have forty different security postures and no affordable way to assess them, while one enforced baseline can be assessed once and inherited everywhere. That is a reduction in both risk and assurance cost, which is the combination that gets funded. The point about burden is worth saying out loud with delivery teams in the room: expecting product engineers to become security specialists is neither fair nor effective, and the platform's job is to make the secure configuration the path of least resistance so that doing the right thing requires no security expertise at all. On continuous verification, the scheduled-rebuild item is the one most often missing: a hardened image built six months ago is no longer hardened against six months of disclosures, and only automation fixes that. Close by suggesting the posture report - coverage, exceptions, expiries - as the artefact that makes this work visible to leadership without requiring them to read any YAML."
        },
    ],

    "Triage Discipline - Living With Scanner Output": [
        {
            "type": "detail",
            "title": "Deep Dive: Severity Is Not Risk",
            "sections": [
                ("Why CVSS alone misleads", [
                    "CVSS scores the vulnerability in the abstract; risk depends on YOUR context.",
                    "Exposure: is the component reachable from outside, or on an internal path behind three controls?",
                    "Reachability: is the vulnerable function even called by your code, or is it dead weight in a library?",
                    "Data: what would an attacker reach from there - public reference data, or sensitive records?",
                    "A 'critical' in an unreachable path may matter less than a 'medium' on your front door.",
                ]),
                ("The triage questions, in order", [
                    "1. Is it FIXABLE today? (an upgraded package or base image exists) - if yes, this is usually just a version bump.",
                    "2. Is the vulnerable path REACHABLE in our usage? - reachability analysis removes a great deal of noise.",
                    "3. What is the EXPOSURE and the data at stake? - this sets the deadline, not the CVSS number alone.",
                    "4. Is there a compensating control already in place? - record it, do not merely assert it.",
                ]),
                ("Gating on what people can action", [
                    "--ignore-unfixed in the gate: block only what a developer can resolve today.",
                    "Unfixable findings go to the report and the backlog, with an owner watching for an upstream fix.",
                    "Blocking on the unfixable teaches teams to bypass gates - and they will bypass the useful ones too.",
                    "Widen the gate deliberately as the fixable backlog clears - narrow and trusted beats broad and ignored.",
                ]),
            ],
            "notes": "This is the slide that keeps a security programme sustainable, because the alternative - treating every high-severity finding as an emergency - burns out teams and destroys the credibility of the whole practice within a quarter. Teach the distinction between severity and risk carefully: CVSS describes the flaw, not your exposure to it, and a mature programme applies context to prioritise. The reachability question is the one that removes the most noise in practice, since a large share of dependency findings are in code paths the application never calls. Be clear that context-based prioritisation is not an excuse to ignore findings - everything is recorded, owned and tracked - it is how limited capacity gets pointed at the things that actually matter. Repeat the gate discipline from Day 1 once more, because it is the operational expression of all of this: gate on the fixable, report the rest, and protect the meaning of a red build. In a supervised institution, add that documented compensating controls belong in the record rather than in someone's memory."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Managing Vulnerability Debt",
            "sections": [
                ("Treat it exactly like technical debt", [
                    "It accumulates silently, it has interest, and it must be budgeted - not handled in occasional panics.",
                    "Reserve recurring capacity for remediation, or it will always lose to feature work.",
                    "Track the TREND: is the fixable backlog shrinking? A rising count with a falling trend is progress.",
                    "Report at portfolio level - which services carry the most, and are they the ones that matter most?",
                ]),
                ("Accepted risks need owners and EXPIRY dates", [
                    "Every acceptance records: what, why, who owns it, what compensates for it, and when it is revisited.",
                    "No permanent ignore files - a permanent exception is an undocumented decision waiting to be discovered.",
                    "Expiry forces re-evaluation, which is exactly what should happen when an upstream fix appears.",
                    "This is also precisely the evidence an assessor asks for, produced as a by-product of working.",
                ]),
                ("Reduce the source, do not just triage faster", [
                    "Slimmer base images and multi-stage builds remove whole classes of findings at once.",
                    "Automated dependency-update pull requests turn most findings into a reviewed, tested version bump.",
                    "Scheduled rebuilds keep images current without anyone remembering to do it.",
                    "Remove unused dependencies - the cheapest vulnerability is the library you deleted.",
                ]),
            ],
            "notes": "The framing that makes this manageable is debt: vulnerability findings accumulate like technical debt, they have interest, and they need budgeted capacity rather than heroics. Recommend a standing allocation - a fixed share of each iteration - because remediation work that competes with features on a case-by-case basis always loses until it becomes an emergency. The expiry-dated acceptance is the single most important process detail on this slide, and it is worth insisting on: permanent ignores are how organisations end up carrying a known-critical vulnerability for years without any record of who decided that was acceptable or why. An expiry forces the decision back onto someone's desk when circumstances have changed. Finish with the reduction strategies, because they are where the leverage is: teams that slim their base images and automate dependency updates typically remove the majority of their findings without triaging them individually, which is a far better use of scarce security attention than a longer meeting about severities."
        },
    ],

    "Monitoring Asks Known Questions; Observability Answers New Ones": [
        {
            "type": "detail",
            "title": "Deep Dive: Known Unknowns vs Unknown Unknowns",
            "sections": [
                ("MONITORING - checks you designed in advance", [
                    "Predefined questions with predefined answers: is it up, is the disk full, is the queue growing?",
                    "Excellent for failures you have already seen and can enumerate - and you should absolutely have it.",
                    "Its limit is definitional: it can only tell you about conditions somebody thought to check for.",
                    "Dashboards full of green while users are complaining is the classic symptom of monitoring-only.",
                ]),
                ("OBSERVABILITY - the ability to ask NEW questions", [
                    "A property of the SYSTEM, not a product you buy: can you interrogate it about behaviour you never predicted?",
                    "Requires rich telemetry with high-cardinality context: customer, tenant, endpoint, version, region, feature flag.",
                    "The test: 'requests from one specific segment are slow' - can you answer that WITHOUT shipping new code?",
                    "If the answer is 'we would need to add logging and redeploy', you have monitoring, not observability.",
                ]),
                ("Why distributed systems force the change", [
                    "In a monolith, the failure is usually in the one process you are already watching.",
                    "In a distributed system, failures are emergent: a slow dependency, a retry storm, one bad replica, a partial outage.",
                    "The interesting outage is always the novel one - by definition nobody wrote a check for it.",
                    "So invest in the ability to explore, not only in the list of things you already fear.",
                ]),
            ],
            "notes": "Make the distinction operationally rather than philosophically, because participants will otherwise hear it as vocabulary. Monitoring answers questions you wrote down in advance; observability lets you ask questions you had not thought of, during the incident, without deploying code. The high-cardinality point is where the two genuinely diverge and where tooling cost appears: being able to slice by customer, tenant, version or feature flag is what turns 'the service is slow' into 'requests from this tenant on this version are slow', and that dimensionality is expensive for traditional metric systems, which is why tracing and structured events matter. Use the test on the slide as the diagnostic and let the room answer honestly for their own systems - most will admit that novel questions require a code change and a deploy, which is precisely the gap. Be clear that this is not an argument to discard monitoring: you need both, and the known checks are cheap, fast and often sufficient. The investment argument is about the incidents that matter most, which are always the ones nobody anticipated."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Instrumentation That Makes It Possible",
            "sections": [
                ("Structured, correlated telemetry", [
                    "Structured logs (JSON) with consistent field names - grep-able becomes query-able.",
                    "A correlation/trace ID propagated across every service hop, and included in every log line.",
                    "Metrics with meaningful labels, and traces that show where the time actually went.",
                    "Context that matters to YOUR business: tenant, product, channel, version, feature flag.",
                ]),
                ("OpenTelemetry as the strategic bet", [
                    "Vendor-neutral instrumentation: instrument once, then choose (and change) the backend later.",
                    "Instrumentation is the expensive, invasive part - so keeping it portable protects the investment.",
                    "It also standardises semantics across languages and teams, which is what makes data joinable.",
                    "This is the 'exit cost' principle from Day 1, applied where the lock-in would otherwise be worst.",
                ]),
                ("Costs and controls to plan for", [
                    "Telemetry volume is a real budget line: sample deliberately, and keep tail/error sampling high.",
                    "Retention tiers: detailed data for days, aggregates for months, per what questions you must answer.",
                    "Data protection: telemetry can carry personal data - classify it, scrub it, control access to it.",
                    "Cardinality discipline: unbounded label values will melt a metrics backend - budget them consciously.",
                ]),
            ],
            "notes": "Instrumentation is where the module becomes actionable, and the highest-value single practice is trace-ID propagation with structured logs: without it, an investigation across five services is manual archaeology; with it, one identifier reconstructs the whole request path. Recommend OpenTelemetry explicitly as the strategic choice, using the Day 1 exit-cost argument - the instrumentation work is expensive and invasive, so making it vendor-neutral keeps the backend decision reversible, which matters in an institution whose procurement cycles are long. The cost and control section is essential for this audience and is often skipped in observability talks: telemetry is a budget line that grows with traffic, retention must be designed rather than defaulted, and telemetry can carry personal data, so classification and scrubbing belong in the design rather than in a later remediation. Mention cardinality explicitly - an unbounded label such as a raw user identifier will overwhelm a metrics system - because it is the most common self-inflicted observability outage."
        },
    ],

    "SLI, SLO, SLA - and the Error Budget": [
        {
            "type": "detail",
            "title": "Deep Dive: Choosing Indicators and Targets",
            "sections": [
                ("Pick SLIs that reflect USER experience", [
                    "Good SLIs: request success rate, latency at p95/p99, freshness of data, completeness of a batch.",
                    "Bad SLIs: CPU utilisation, memory, pod count - these are causes, and users do not experience them.",
                    "Measure as close to the user as possible: at the edge or the client, not deep inside one component.",
                    "For batch and data work, the right indicators are timeliness, completeness and correctness - not uptime.",
                ]),
                ("Setting the SLO honestly", [
                    "Start from what users actually need, not from what sounds impressive in a steering pack.",
                    "Use historical data: if you have been at 99.5% and nobody complained, 99.9% may be spending money for nothing.",
                    "Each additional nine multiplies cost - in redundancy, in engineering time, and in operational restraint.",
                    "State the WINDOW (rolling 30 days) and the measurement method, or the number means nothing.",
                    "Different services deserve different targets: a settlement path and an internal report are not the same.",
                ]),
                ("SLA is a different animal", [
                    "The SLA is the external commitment with consequences; the SLO is your internal target.",
                    "Always set the SLO tighter than the SLA, so you find out you are in trouble before your counterparty does.",
                    "Not every service needs an SLA, but every service that matters deserves an SLO.",
                ]),
            ],
            "notes": "The most common mistake is choosing indicators that are easy to measure rather than ones that reflect what users experience, so spend time on the good-versus-bad SLI contrast. CPU utilisation is a cause, not an experience: a service can be at 90% CPU and perfectly healthy, or at 10% and failing every request. For this audience, add the batch and data dimension explicitly, because a great deal of central-bank work is not request-response: for a data pipeline or a scheduled publication, the meaningful indicators are timeliness, completeness and correctness, and framing those as SLIs is often a genuinely new idea. On target setting, push back against reflexive nines: each additional nine costs real money and real engineering restraint, and a target chosen because it looks good in a report will either be missed constantly or will over-constrain delivery. The SLO-tighter-than-SLA rule is simple, memorable and prevents the situation where the first indication of a contractual breach is the counterparty telling you about it."
        },
        {
            "type": "detail",
            "title": "Deep Dive: The Error Budget as a Decision Rule",
            "sections": [
                ("The arithmetic, and why it is liberating", [
                    "Error budget = 100% minus the SLO. At 99% over 30 days, that is roughly 7.2 hours of permitted failure.",
                    "Permitted, not accidental: it is a resource you may deliberately spend on change and experimentation.",
                    "Budget healthy -> ship, take risks, run experiments. Budget exhausted -> reliability work takes priority.",
                    "The policy is agreed IN ADVANCE, when everyone is calm - not negotiated during an incident.",
                ]),
                ("What it changes in the organisation", [
                    "It ends the oldest argument in IT by converting 'faster vs safer' into one number both sides own.",
                    "It makes reliability a shared, quantified goal rather than a matter of temperament or seniority.",
                    "It gives engineers a defensible answer to 'why are you not shipping features this sprint?'",
                    "It gives leadership an honest signal that is not a subjective status colour.",
                ]),
                ("Making it real", [
                    "Publish burn on a dashboard everyone can see, including the people who set delivery priorities.",
                    "Alert on BURN RATE, not on threshold breaches - fast burn pages, slow burn tickets (next slide).",
                    "Review SLOs quarterly: consistently untouched budget means the target is too loose or too expensive.",
                    "Consequences must be real - a budget policy nobody honours is worse than none, because it teaches cynicism.",
                ]),
            ],
            "notes": "The error budget is the single most useful management idea in the observability module, so give it room. The framing that lands is that reliability becomes a spendable resource with an agreed policy rather than an argument between people with different instincts - and crucially, the policy is set while everyone is calm, which is why it survives contact with a bad week. Be honest that the mechanism only works if the consequences are real: an organisation that declares a budget policy and then ignores it when the budget is exhausted has taught its engineers that the whole framework is decorative, which is worse than never starting. For this audience, note that different services warrant genuinely different targets, and that having an explicit, evidenced conversation about how reliable something needs to be is itself valuable - many institutions have never had it, and default to an implicit and unfunded expectation of perfection. The quarterly review point matters too: an untouched budget is not a triumph, it usually means the target is set below what the system already delivers."
        },
    ],

    "Alerting That Respects Humans": [
        {
            "type": "detail",
            "title": "Deep Dive: Symptoms, Causes and Burn Rate",
            "sections": [
                ("Page on symptoms, ticket on causes", [
                    "Symptom: users cannot complete payments; the journey is broken NOW. That is worth waking someone.",
                    "Cause: disk will be full in six days, one replica restarted, a certificate expires in three weeks. That is a ticket.",
                    "Cause-based paging produces alerts that fire when nothing is wrong and stay silent when something is.",
                    "A useful filter: if the user experience is unaffected and it can wait until morning, it is not a page.",
                ]),
                ("Burn-rate alerting on the error budget", [
                    "Alert on how fast the budget is being consumed, not on a raw threshold crossing.",
                    "Two windows: a fast one (high burn over a short period) pages; a slow one (moderate burn over hours) tickets.",
                    "This catches both the sudden outage and the slow leak, without paging for a brief harmless blip.",
                    "It also ties every page directly to something the organisation already agreed matters.",
                ]),
                ("The three tests every page must pass", [
                    "ACTIONABLE: there is something a human can do right now. If not, it is a notification.",
                    "URGENT: it genuinely cannot wait until working hours.",
                    "NOVEL: it is not the fifth copy of a known condition - deduplicate and group.",
                    "Fail any test and the alert should be downgraded, tuned or deleted - not tolerated.",
                ]),
            ],
            "notes": "This slide protects people, and it is worth saying that plainly: alert design is an occupational-health issue as much as an engineering one. The symptom-versus-cause rule is the most valuable single heuristic, because most legacy alerting is cause-based, which produces the worst possible combination - frequent pages that do not matter, and silence during the failures that do. Burn-rate alerting is the modern refinement and connects the pager directly to the error budget from the previous slide, which means every page is tied to something the organisation already agreed was important. Give the three tests as a review tool participants can apply to their existing alert set this month: take the alerts that fired last quarter, ask which were actionable, urgent and novel, and delete or downgrade the rest. That exercise routinely removes a large share of an organisation's pages and improves detection, because the remaining signal is trusted. In a supervised institution, add that alert quality is genuinely an operational-resilience control - an on-call engineer who has learned to ignore the pager is a control failure with a human face."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Alert Fatigue Is a Safety Failure",
            "sections": [
                ("How organisations get here", [
                    "Every incident adds an alert; almost nothing is ever removed. The set only grows.",
                    "Alerts are added for reassurance rather than for action - 'so we know it happened'.",
                    "Thresholds are copied between services without checking whether they mean anything there.",
                    "Result: hundreds of alerts, most ignored, and the important one arrives in the same noisy channel.",
                ]),
                ("The discipline that fixes it", [
                    "Every alert links a RUNBOOK that says what to check and what to do - no runbook, no page.",
                    "Every false page is a defect: tune it or delete it, in the week it happened.",
                    "Budget your alerts like any other finite resource - a rising page count is a regression, not a sign of diligence.",
                    "Review the alert set with the same seriousness as the code: quarterly, with deletions.",
                ]),
                ("Measure the human side", [
                    "Pages per on-call shift, and how many arrived outside working hours - track it, publish it.",
                    "Time to acknowledge and time to resolve, split by alert type, shows where the runbooks are failing.",
                    "Fair, compensated, adequately staffed rotations - fatigue is a control weakness, not a badge of honour.",
                    "Feed the numbers into retrospectives: on-call health is a team metric, not an individual's problem.",
                ]),
            ],
            "notes": "The purpose of this slide is to give participants permission and a method to delete alerts, which most organisations find surprisingly hard. Name the accumulation mechanism honestly - every incident adds an alert and nothing is ever removed - because once people see the ratchet they can argue against it. The no-runbook-no-page rule is the most enforceable discipline available: it forces the author to articulate what the responder should actually do, and if they cannot, the alert was never actionable. On measurement, pages per shift and the out-of-hours split are the numbers that make the problem visible to leadership, and they belong alongside the other operational indicators rather than in a private team spreadsheet. Be explicit that alert fatigue is a safety failure: an engineer who has been trained by months of noise to dismiss pages will dismiss the one that matters, and every large outage retrospective in the industry contains a version of that sentence. Finish by placing on-call health in the retrospective, so it becomes a system to improve rather than an endurance test individuals are expected to pass."
        },
    ],

    "Designing for Failure - Reliability Patterns": [
        {
            "type": "detail",
            "title": "Deep Dive: The Patterns, and How They Fail",
            "sections": [
                ("TIMEOUTS - the one nobody sets until it hurts", [
                    "Every network call needs a bounded wait; the default in most libraries is effectively forever.",
                    "Without them, one slow dependency exhausts your threads or connections and takes YOU down with it.",
                    "Budget them: the caller's timeout should be shorter than its own caller's, or the chain is pointless.",
                    "Slow is worse than down - a dead dependency fails fast, a sick one holds every resource you have.",
                ]),
                ("RETRIES - useful, and dangerous", [
                    "Retry transient faults only, with exponential backoff AND jitter so callers do not synchronise.",
                    "Cap total attempts and total time - unbounded retries are a self-inflicted denial of service.",
                    "The receiver must be idempotent, or a retry becomes a duplicate transaction.",
                    "Never retry on a definite failure (a 400-class response) - you are just repeating the same mistake faster.",
                ]),
                ("CIRCUIT BREAKERS and BULKHEADS", [
                    "Circuit breaker: after N failures, stop calling for a cooling period, then probe cautiously.",
                    "It protects both sides - you fail fast, and the sick dependency gets room to recover.",
                    "Bulkheads: separate connection pools and thread pools per dependency, so one failure cannot drain everything.",
                    "Together they turn a cascading outage into a localised, visible degradation.",
                ]),
            ],
            "notes": "The sentence to leave with the room is that slow is worse than down: a dead dependency fails immediately and your circuit breaker handles it, while a sick one holds your connections, threads and memory until you fall over too - which is why timeouts are the foundational pattern and why 'no timeout' is a latent outage in every service that lacks one. On retries, be equally blunt about the danger: naive retry logic has turned many minor incidents into major ones by multiplying load precisely when a dependency was struggling, and the jitter detail matters because synchronised retries from many clients arrive as a coordinated wave. Idempotency deserves its own emphasis in any financial context - if a request can be retried, the receiver must be able to detect and discard the duplicate, usually with a client-supplied key - because the failure mode here is not an outage but a duplicated transaction, which is far more expensive to unwind. Circuit breakers and bulkheads are the containment layer, and the framing that helps is that they convert cascading failure into localised, observable degradation."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Degradation, Recovery and Practice",
            "sections": [
                ("GRACEFUL DEGRADATION is a product decision", [
                    "Decide in advance what reduced service means for each dependency failure - and who decides.",
                    "Our lab example: payments unavailable, so the order is accepted and queued, with an honest message.",
                    "Serve cached or stale data with a clear indication, rather than an error page, where that is acceptable.",
                    "The wrong time to invent the degraded mode is during the incident, at 03:00, under pressure.",
                ]),
                ("RECOVER FAST usually beats PREVENT HARDER", [
                    "Prevention has diminishing returns; recovery speed compounds across every incident you will ever have.",
                    "Redundancy plus a rollback measured in seconds returns more availability than another layer of checks.",
                    "This is why Day 1's immutable artefacts and one-command rollback are reliability engineering, not just delivery.",
                    "Measure recovery, not just failure: time-to-restore is one of the four metrics for good reason.",
                ]),
                ("PRACTISE, or none of this is real", [
                    "Game days: schedule the failure at 10:00 on a Tuesday instead of waiting for 03:00 on a Sunday.",
                    "Start small and safe: stop a dependency in a lower environment and watch what the system actually does.",
                    "Restore drills: an untested backup is a hope. Time the restore and record the number.",
                    "Every drill produces either confidence or a defect - both are worth more than the plan document.",
                ]),
            ],
            "notes": "Graceful degradation is presented as a product decision on purpose: engineers cannot unilaterally decide that an order may be accepted without a payment confirmation, so the degraded modes must be designed with the business owner, in advance, and written down. That conversation is often the most valuable output of this module for a regulated institution, because it forces an explicit answer to 'what may we still do when this dependency is unavailable?' - a question that otherwise gets answered improvised, at 03:00, by whoever is on call. The recover-fast argument is the one that reframes Day 1's content as reliability engineering: immutable artefacts, small batches and one-command rollback are what make recovery measured in seconds possible, and recovery speed compounds across every future incident while prevention has diminishing returns. Close on practice, and make the ask concrete and small: stop one dependency in a lower environment this month and watch what happens, then time a restore. Lab 08's game day is exactly this rehearsal, and it usually surprises people - which is the point of doing it on a Tuesday."
        },
    ],

    "User-Centric Design for Internal Platforms": [
        {
            "type": "detail",
            "title": "Deep Dive: Your Users Are Developers - Treat Them Like Users",
            "sections": [
                ("Do real product discovery", [
                    "Interview delivery teams about their actual workflow - do not design from an architecture diagram.",
                    "Map the journey from 'we need a new service' to 'it is serving traffic', and time every step.",
                    "Build personas honestly: the experienced platform-native team and the team maintaining a 12-year-old system.",
                    "Watch someone use your platform for the first time, in silence. It is uncomfortable and it is the best data you get.",
                ]),
                ("Measure the journey, not the components", [
                    "Time-to-first-deploy for a NEW team is the flagship UX metric - end to end, including access and approvals.",
                    "Instrument the funnel: aware -> tried -> running in production -> would recommend. Every drop-off is a defect.",
                    "Count the steps a developer must perform, and the number of different systems they must touch.",
                    "Ask what they did INSTEAD when they gave up - the workaround tells you what your product is missing.",
                ]),
                ("Documentation IS the interface", [
                    "A quickstart that works, verbatim, in under 30 minutes - tested in CI like any other product feature.",
                    "Copy-pasteable examples over prose descriptions; a working sample beats three pages of explanation.",
                    "Honest, actionable error messages: what failed, why, and the exact next step.",
                    "Test with a real newcomer each quarter: can they succeed unaided? If not, the platform failed, not the person.",
                ]),
            ],
            "notes": "The mindset shift is the whole slide: platform teams that treat their output as infrastructure build things that are technically correct and unused, while teams that treat it as a product build things people choose. Push the discovery point hard, because engineers find it unnatural - interviewing colleagues about their workflow feels like overhead until the first session reveals that half the golden path is unused because of one confusing step. The silent-observation technique is worth recommending explicitly: watch a developer attempt the quickstart without helping them, and write down every place they hesitate. On measurement, time-to-first-deploy must be measured end to end including access requests and approvals, because that is what the user experiences - a platform that provisions in five minutes but sits behind a three-week access request has a three-week time-to-first-deploy. The documentation point deserves emphasis in an institution with strong documentation culture: the difference is that platform docs are a product surface, tested in CI, owned, and measured by whether newcomers succeed - not a deliverable that was completed once."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Golden Paths and the Thinnest Viable Platform",
            "sections": [
                ("What a golden path actually is", [
                    "The supported, opinionated, genuinely delightful default route for the most common service shape.",
                    "Not the only way - the SUPPORTED way, with escape hatches that are documented and legitimate.",
                    "It should be the fastest route to production, or teams will rationally go around it.",
                    "One path per common shape (web API, batch job, data pipeline) - not one path for every conceivable need.",
                ]),
                ("Start from the Thinnest Viable Platform", [
                    "The smallest thing that removes real pain for real teams - often a documented way plus one template.",
                    "A wiki page that describes the one good way IS a platform, and it is a legitimate first version.",
                    "Automate where the pain actually is, evidenced by the journey map - not where the architecture looks elegant.",
                    "Grow by demand: the second team asking for the same thing is the signal to productise it.",
                ]),
                ("Failure modes to avoid on purpose", [
                    "Building the complete platform before anyone uses it - two years of work, no users, no feedback.",
                    "Copying a big tech company's platform without their scale, teams, or problems.",
                    "Mandating adoption instead of earning it - producing compliance plus invisible shadow practice.",
                    "Solving the platform team's interesting problems rather than the delivery teams' painful ones.",
                ]),
            ],
            "notes": "Spotify's term 'golden path' is useful because it carries the right connotation - a route that is pleasant to walk, not a fence. Be precise that it is the supported way rather than the only way, and that escape hatches must be legitimate and documented, because an unofficial escape hatch is just shadow infrastructure with extra steps. The Thinnest Viable Platform idea, from Team Topologies, is the antidote to the most expensive failure mode in this space: a platform team disappearing for two years to build a comprehensive system that nobody asked for and nobody adopts. Give participants permission to start embarrassingly small - a documented standard way plus one working template is a real first version, and it produces feedback immediately. The 'copying big tech' warning is worth stating for this audience: the platforms published by very large technology companies solve the problems of hundreds of teams and enormous scale, and importing that design into an institution with a dozen delivery teams imports the cost without the benefit."
        },
    ],

    "Measuring Success and ROI": [
        {
            "type": "detail",
            "title": "Deep Dive: The Four Numbers Worth Publishing",
            "sections": [
                ("ADOPTION - the honest vote", [
                    "Percentage of services on the golden path, and the trend over quarters.",
                    "Voluntary adoption is the strongest signal a platform team can produce - people chose it.",
                    "If adoption is mandated, measure SATISFACTION instead, because the choice signal is gone.",
                    "Segment it: which kinds of team adopt, which do not, and what the non-adopters chose instead.",
                ]),
                ("SPEED - the output that matters", [
                    "Time-to-first-deploy for a new team or service, measured end to end.",
                    "The DORA metrics OF CONSUMING TEAMS - the platform's real output is their delivery performance.",
                    "Compare adopters with non-adopters; the gap is your value proposition, in numbers.",
                    "Track lead-time contribution: how much of a team's lead time is spent in platform-owned steps?",
                ]),
                ("LOAD and EXPERIENCE", [
                    "Support tickets per team per month should FALL as self-service rises - a rising count is a product defect.",
                    "Categorise tickets: each recurring category is a missing feature or a documentation failure.",
                    "Developer satisfaction or NPS, surveyed quarterly, with the verbatim comments read by the whole team.",
                    "Time-to-answer for platform support - the platform is production, and its users are waiting.",
                ]),
            ],
            "notes": "The reason to publish these four numbers is that platform teams are chronically bad at demonstrating value and therefore chronically vulnerable at budget time. Adoption is the headline because it is the honest vote, and the nuance about mandated adoption matters in institutions that can compel usage: once you mandate, adoption stops being evidence of quality and satisfaction becomes the only trustworthy signal. The DORA-metrics-of-consuming-teams point is the conceptual core - a platform team produces no customer value directly, so its output is measured in what its users can now do, and the comparison between adopters and non-adopters is the most persuasive chart available. On load, reframe rising ticket volume correctly: it is not a sign of a busy, useful team, it is a sign that self-service is failing somewhere specific, and categorising tickets turns that into a roadmap. Recommend that the whole platform team reads the survey verbatims rather than a summary, because the summary always loses the sentence that changes someone's mind."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Building the ROI Case",
            "sections": [
                ("The arithmetic, stated plainly", [
                    "Toil hours saved per team per month × number of teams × loaded cost per hour.",
                    "Plus risk reduction: one assessed path instead of N hand-built ones - fewer, and cheaper, assurance findings.",
                    "Plus opportunity: capacity returned to product work, expressed in what that capacity delivered.",
                    "Minus the platform team's fully loaded cost, including the infrastructure it operates.",
                ]),
                ("Evidence that survives scrutiny", [
                    "Baseline BEFORE you build: time-to-first-deploy, setup steps, tickets, incident counts. You cannot re-measure the past.",
                    "Use the journey map's timings as the before-picture, agreed with the teams themselves.",
                    "Prefer conservative numbers you can defend over impressive ones you cannot.",
                    "Report trends quarterly in the same format - consistency is what makes the story believable.",
                ]),
                ("Framing that works in a regulated institution", [
                    "Lead with control uniformity and assurance cost, not developer happiness - it is the stronger argument here.",
                    "One path assessed deeply beats forty assessed by sampling; that is a genuine risk reduction.",
                    "Automated evidence lowers the cost of every audit cycle, permanently, for every consuming team.",
                    "Then add the delivery numbers - they land better once the risk case has been accepted.",
                ]),
            ],
            "notes": "The single most common mistake platform teams make is failing to baseline before they start, so say it early and firmly: measure time-to-first-deploy, the number of setup steps, ticket volume and incident counts BEFORE the platform exists, because you cannot reconstruct those numbers afterwards and without them every claim is an assertion. Agreeing the baseline with the delivery teams also makes the later comparison credible rather than self-reported. On the arithmetic, advise conservatism - a defensible modest number survives a finance review, while an impressive one invites a challenge that undermines the whole case. The framing section is specific to this audience and matters: in a supervised institution, the risk and assurance argument is stronger than the productivity argument, because it speaks to obligations the institution already carries, and it converts the platform from a cost centre into a control investment. Lead with that, then present the delivery numbers as the additional benefit."
        },
    ],

    "Operating Model - and What NOT to Build": [
        {
            "type": "detail",
            "title": "Deep Dive: Fund It and Run It Like a Product",
            "sections": [
                ("Product funding, not project funding", [
                    "A project ends, hands over a deliverable, and the team disperses - leaving an unmaintained platform.",
                    "A product is funded continuously, has a roadmap, an owner, and improves in response to users.",
                    "Platforms decay faster than most software: dependencies move, clusters upgrade, needs change.",
                    "If the funding model cannot support a standing team, build something smaller that a standing team can keep.",
                ]),
                ("The platform is production - with customers", [
                    "It needs its own SLOs, monitoring, on-call and incident process. When it is down, every team is blocked.",
                    "Publish support hours and response expectations - and meet them, because trust is the product.",
                    "Run change management on the platform itself: your users experience your outages as their outages.",
                    "Communicate proactively: planned changes, deprecations and incidents, in a channel users actually read.",
                ]),
                ("Deprecation without rug-pulls", [
                    "Version everything teams depend on: templates, modules, pipeline workflows, base images.",
                    "Announce deprecation with a real migration window, migration guidance and, ideally, automated migration.",
                    "Never change shared behaviour silently - one surprise breakage costs more trust than a year of good work.",
                    "Track who is on which version, so you know exactly who a change affects before you make it.",
                ]),
            ],
            "notes": "Funding model is the structural point that decides whether a platform survives, so make it explicit: project funding produces a deliverable and then leaves it to rot, and a rotting platform is worse than none because teams built on it. If the institution genuinely cannot fund a standing team, the right response is to build something smaller and more durable rather than a large system with no maintainer - that is honest engineering advice, not defeatism. The 'platform is production' framing is the one that changes behaviour inside the platform team: their outages are everyone's outages, so they need the same SLOs, alerting, on-call and change discipline they are advocating to everyone else, and nothing damages credibility faster than a platform team that does not practise its own advice. On deprecation, the versioning and migration-window discipline is what preserves trust over years: teams will accept change they can plan for, and will not forgive silent breakage. The knowledge of who is on which version is the operational prerequisite for all of it."
        },
        {
            "type": "detail",
            "title": "Deep Dive: Saying No, and the Team's Place in the Org",
            "sections": [
                ("Say NO deliberately - it is a product skill", [
                    "Every exotic request served becomes permanent surface area the platform must maintain forever.",
                    "The test: how many teams need this? One team's unique need belongs with that team, via the escape hatch.",
                    "Offer the alternative rather than a flat refusal: here is the escape hatch, here is what you take on.",
                    "A platform that says yes to everything becomes an unmaintainable custom-integration department.",
                ]),
                ("Where the platform team sits", [
                    "It is a stream-aligned team whose stream is the platform, and whose users are internal delivery teams.",
                    "Interaction with teams evolves: collaborate while discovering, then X-as-a-Service once the path exists.",
                    "A platform stuck in permanent collaboration mode has not productised; one that never collaborated built the wrong thing.",
                    "It is NOT the team that deploys everyone's code - that is the third-silo anti-pattern from Day 1.",
                ]),
                ("Staffing and skills that make it work", [
                    "Needs product skills as much as engineering: discovery, prioritisation, documentation, communication.",
                    "Needs enough operational depth to run production infrastructure credibly.",
                    "Rotate delivery engineers through it - the best user research is a former user on the team.",
                    "Accept contributions (InnerSource) so the platform can grow faster than its own headcount.",
                ]),
            ],
            "notes": "Saying no is the skill that separates a sustainable platform from an internal consulting queue, and engineers generally find it uncomfortable, so give them the framing and the language: every accepted exotic request is permanent maintenance surface, the test is how many teams share the need, and the answer is not a refusal but a redirection to the documented escape hatch with a clear statement of what the team then owns. On organisational placement, reuse the Team Topologies vocabulary from Day 1 and stress the evolution of interaction modes - close collaboration while discovering what teams need, moving deliberately to a self-service relationship once the path exists. Repeat the anti-pattern one final time because it is the most consequential structural mistake in this whole course: a platform team that deploys everyone's code is the wall of confusion rebuilt with better tooling. On staffing, the product-skills point is worth arguing for in an engineering-heavy institution - a platform team without someone doing discovery, prioritisation and documentation will build technically excellent things that nobody adopts, and InnerSource is how the platform grows beyond the headcount it will realistically be given."
        },
    ],

    "The Three Workshops - Map": [
        {
            "type": "detail",
            "title": "Deep Dive: What Each Workshop Proves",
            "sections": [
                ("W1 - a basic DevOps pipeline (Day 1 afternoon)", [
                    "Build: GitHub Actions workflow triggered by a pull request - test, build the image, scan, gate.",
                    "Proves: automated verification on every change, and the difference between a report and a real gate.",
                    "Concepts made real: small batches, fast feedback, build-once, least-privilege tokens, pinned actions.",
                    "Transfers to: any CI engine - the job graph, gates and artefact promotion are universal.",
                ]),
                ("W2 - build and deploy a microservice (Day 2 morning)", [
                    "Build: Dockerfile -> Compose stack -> Kubernetes manifests on a local kind cluster.",
                    "Proves: the same artefact runs everywhere, and the orchestrator heals and rolls back on command.",
                    "Concepts made real: twelve-factor config, probes, limits, Services, rolling update and rollback.",
                    "Transfers to: any conformant Kubernetes - the API and manifests are identical on managed clusters.",
                ]),
                ("W3 - infrastructure as code (Day 2 afternoon)", [
                    "Build: Terraform against the local Docker provider - init, plan, apply, drift, destroy.",
                    "Proves: declarative infrastructure, plan-as-review, state as the map of reality, drift detection.",
                    "Concepts made real: idempotence, immutability, blast radius, the plan diff as change evidence.",
                    "Transfers to: any provider - swap the provider block; the workflow does not change.",
                ]),
            ],
            "notes": "Set the workshops up by saying what each one PROVES rather than what participants will type, because the typing is in the guide and the proving is what they take home. One application runs through all three - the order and payment services from the demos - which is deliberate: by the end of Day 2 participants have taken a single service from source, through a pipeline, into a container, onto an orchestrator, with its infrastructure declared as code, which is the whole DevOps loop walked once with their own hands. Emphasise the transfer statement in each block, because that is the answer to 'this is a local toy' - the pipeline concepts, the Kubernetes API and the Terraform workflow are the same at any scale and on any provider. Mention that the capstone at the end runs all three as a single golden path, which is the module 9 idea made concrete: a new service reaching production through one assessed route. Point participants at the workshops folder for the guides and the troubleshooting tables before they start."
        },
        {
            "type": "detail",
            "title": "Deep Dive: How to Work Through Them",
            "sections": [
                ("Working method", [
                    "Read the whole exercise first, then start - the context makes the individual steps make sense.",
                    "Type the commands rather than pasting them where you can; muscle memory is part of the point.",
                    "When something fails, READ the error before searching - the message is usually the answer.",
                    "Check the troubleshooting table in the workshop guide next; the common failures are already documented.",
                ]),
                ("The three-then-me rule", [
                    "Stuck? Ask three neighbours before you ask the instructor - explaining the problem often solves it.",
                    "Struggling is not a sign the material is too hard; it is where the learning actually happens.",
                    "Pair up if you prefer - one drives, one navigates, swap at each checkpoint.",
                    "If you finish early, help someone else; teaching it is the strongest way to retain it.",
                ]),
                ("Afterwards", [
                    "Keep everything: the repo runs on any Ubuntu 24.04 machine via the setup script, at no cost.",
                    "Re-run the capstone unaided within two weeks - the second, unassisted repetition is what makes it stick.",
                    "Then rebuild it for something in your own environment, starting with a low-criticality internal service.",
                    "Record what you had to add for your institution - that list is the start of your own golden path.",
                ]),
            ],
            "notes": "This slide is facilitation, so keep it brief in the room and let it do its work in the deck. The read-first instruction genuinely matters: participants who dive into step one without context ask far more questions about why they are doing something. The three-then-me rule protects the instructor's attention and, more importantly, builds the habit of explaining a problem out loud, which resolves a surprising share of them. Be explicit that struggling is expected and is the point - in a room of senior people there is real reluctance to appear stuck, and naming that up front makes the afternoon far more productive. The 'afterwards' section is the highest-value part: retention comes from the second, unaided repetition, so ask participants to diary an hour within two weeks to re-run the capstone from scratch. And the last line sets up their real work - the list of what they had to add for their own environment (identity, zoning, evidence, approvals) is the first specification of their institution's own golden path."
        },
    ],

    "Workshop Success Criteria": [
        {
            "type": "detail",
            "title": "Deep Dive: Done Means Verified, Not Finished",
            "sections": [
                ("Why explicit criteria matter", [
                    "'Done' in this course means an observable, verifiable outcome - not 'I ran all the commands'.",
                    "This mirrors the professional discipline: a deploy that 'succeeded' but serves errors has not succeeded.",
                    "Each criterion is something you can demonstrate to a colleague in under a minute.",
                    "If you cannot demonstrate it, something is genuinely not working - and finding out now is the point.",
                ]),
                ("The checks, and what each one proves", [
                    "W1: a PR triggers the pipeline, test and build are green, and you can explain report versus gate in your own words.",
                    "W2: /health responds from Kubernetes on localhost:30080, and you rolled forward AND back.",
                    "W3: plan shows 3 resources, apply serves on :8090, drift is detected, destroy leaves nothing behind.",
                    "Capstone: run-capstone.sh is green end to end, and your PLATFORM-HANDOVER.md is written.",
                ]),
                ("The handover document is the real deliverable", [
                    "Writing down what you built, how to run it and what it guarantees is the platform-as-product skill.",
                    "It is also the artefact you can show a colleague, a manager or an auditor back at work.",
                    "Keep it short and honest: what works, what does not, what you would do next.",
                    "A capstone that runs but is undocumented is a demo; documented, it is a platform.",
                ]),
            ],
            "notes": "The pedagogical point behind explicit success criteria is that they replace the vague feeling of having finished with a demonstrable outcome, and they mirror exactly the discipline the course teaches - a smoke test after deployment, because a green pipeline is not proof that anything serves. Encourage participants to actually run the checks and, better, to demonstrate them to a neighbour, which catches the case where something appears to work only in the participant's own terminal history. Give particular attention to the handover document in the capstone: it is the artefact that turns a working setup into a product, it is the deliverable they can show their own organisation, and writing it is the skill Module 9 has been arguing for all afternoon. Encourage brevity and honesty - what works, what does not, what is next - because an honest one-page handover is more useful and more credible than an aspirational ten-page one."
        },
    ],

    "What You Built in Two Days": [
        {
            "type": "detail",
            "title": "Deep Dive: The Loop You Walked, End to End",
            "sections": [
                ("Plan and code -> build and test", [
                    "Version control as the single source of truth, with change proposed and reviewed as a pull request.",
                    "A pipeline that runs on every change: tests, build, scan, gate - feedback in minutes, not weeks.",
                    "One immutable, SHA-tagged artefact produced once and promoted unchanged.",
                    "Concepts proven: small batches, fast feedback, build-once-promote-many, report versus gate.",
                ]),
                ("Package and run", [
                    "A twelve-factor service containerised with a multi-stage build, running as non-root.",
                    "Deployed to a real Kubernetes API with probes, resource limits, a Service and a rolling update.",
                    "Rolled forward and rolled BACK on command - recovery demonstrated, not assumed.",
                    "Concepts proven: portability, disposability, reconciliation, blast-radius thinking.",
                ]),
                ("Secure, observe, operate - and hand over", [
                    "Infrastructure declared in Terraform, with plan-as-review, drift detection and clean destroy.",
                    "Policy as code, image and IaC scanning wired into the path, gated on what is fixable.",
                    "Metrics, a dashboard, an SLO, an alert - and one incident survived in the game day.",
                    "All of it assembled as ONE golden path, documented in your handover: a platform product, in miniature.",
                ]),
            ],
            "notes": "Close the course by making the achievement concrete, because participants routinely under-estimate what they covered. Walk the loop in the same order as the Day 1 infinity-loop diagram and name the module each piece came from - it converts two days of separate exercises into one coherent story they can retell to a manager. The line worth saying out loud: in two days they took a service from source to production through an automated, scanned, policy-checked, observable, reversible path, and then documented it as a product. That is the full DevOps loop, and most organisations take a year to assemble it for the first time. Emphasise the rolled-back and survived-an-incident items specifically, because recovery demonstrated is the difference between a demo and a capability. Then set up the last two slides: what to learn next, and what to do in week one."
        },
        {
            "type": "detail",
            "title": "Deep Dive: What Transfers, and What You Must Still Add",
            "sections": [
                ("Transfers directly to your workplace", [
                    "The workflow and its discipline: propose, review, verify automatically, promote, observe, roll back.",
                    "Pipeline concepts across any engine; Kubernetes API skills on any conformant cluster.",
                    "Terraform's plan/apply/state/module workflow against any provider.",
                    "The reasoning: batch size, gates that are trusted, SLOs and error budgets, blameless learning.",
                ]),
                ("You must still add, in your own environment", [
                    "Identity, access model, network zoning and whatever segmentation your environments require.",
                    "Data protection in practice: classification, masked or synthetic test data, retention rules.",
                    "Change records and evidence retention wired into the pipeline instead of assembled by hand.",
                    "Availability expectations and windows that the institution genuinely cannot move.",
                ]),
                ("The bridge between the two", [
                    "Prove the pattern on a low-criticality internal service first - never on a critical path.",
                    "Bring evidence, not enthusiasm, to your risk, security and audit colleagues: a working path they can inspect.",
                    "Agree the control mapping once, then reuse it for every subsequent service on that path.",
                    "That agreed path IS your institution's first golden path - and Module 9 told you how to run it as a product.",
                ]),
            ],
            "notes": "Honesty about the gap is what makes the course useful rather than inspiring. Be explicit that the labs deliberately omit the institutional wrapping - identity, zoning, classification, evidence, windows - and that adding it is the real work waiting for them. Then give the bridge, which is the most actionable advice in the closing module: prove the pattern end to end on something genuinely low-risk, then take the working artefact to the colleagues who own control assurance and agree the mapping once. Teams that argue from principle spend months in meetings; teams that arrive with a running pipeline, a reproducible environment, automatically generated evidence and a demonstrated rollback have a much shorter conversation. Note that the mapping, once agreed, is reusable for every subsequent service - which is exactly why the golden-path idea compounds, and why the platform framing from Module 9 is the right way to run it."
        },
    ],

    "Continuing the Journey": [
        {
            "type": "detail",
            "title": "Deep Dive: A Sequenced Learning Path",
            "sections": [
                ("Next 30 days - consolidate what you have", [
                    "Re-run the capstone from scratch, unaided, on a clean VM. The second repetition is what makes it stick.",
                    "Read Accelerate (Forsgren, Humble, Kim) - it is short, evidence-based, and it arms you for the conversations.",
                    "Practise Kubernetes daily in small doses with kind or minikube; kubectl fluency comes from repetition.",
                    "Write one ADR and one blameless postmortem in your real work - the habits matter more than the tools.",
                ]),
                ("Next 90 days - go deeper where you will actually work", [
                    "Kubernetes: CKAD if you deploy applications, CKA if you will operate clusters.",
                    "IaC: HashiCorp Terraform Associate, plus Ansible for configuration management on existing estates.",
                    "CI/CD: your own engine's documentation end to end, and the act runner for local iteration.",
                    "Observability: instrument one real service with OpenTelemetry and build one honest SLO.",
                ]),
                ("Beyond - the books and communities that repay the time", [
                    "Team Topologies for org design; The Phoenix Project for the narrative to hand a manager.",
                    "The Google SRE books - free online, and the definitive treatment of SLOs and error budgets.",
                    "platformengineering.org, CNCF project documentation, and local DevOps or SRE meetups.",
                    "Follow the annual DORA State of DevOps report - it is the evidence base that keeps updating.",
                ]),
            ],
            "notes": "Sequence the advice rather than listing resources, because an unordered list of twenty things produces no action. The 30-day items are deliberately small and habit-forming, and the most important one is the unaided repetition of the capstone - retention research and everyone's experience agree that the second, unassisted run is where the material moves from recognition to capability. Recommend Accelerate first among the books because it is short and because it gives participants evidence rather than opinion when they are challenged internally, and The Phoenix Project as the one to hand to a sceptical manager because it works as a story. Steer certification advice by role: CKAD for people deploying applications, CKA for those who will operate clusters, and be honest that certifications demonstrate baseline knowledge rather than capability. The observability item - instrument one real service and set one honest SLO - is the single highest-value 90-day action for most participants, because it changes how their team talks about reliability."
        },
    ],

    "Your First Week Back at Work": [
        {
            "type": "detail",
            "title": "Deep Dive: Five Actions, Sized to Actually Finish",
            "sections": [
                ("1. Automate ONE painful manual path, end to end", [
                    "Choose by frequency × pain, not by how interesting it is - the boring repetitive one wins.",
                    "Finish it completely, including the documentation, before starting anything else.",
                    "Small and finished beats large and abandoned; the finished one earns you the mandate for the next.",
                    "Time the before and after - that number is your evidence for the following conversation.",
                ]),
                ("2 and 3. Add a real gate, and write a real postmortem", [
                    "Add tests or a fixable-critical scan as an actual gate on an existing pipeline - exit code 1, not 0.",
                    "Start narrow so it is trusted; widen deliberately once the backlog clears.",
                    "After your next incident, run a blameless review before the formal record, and publish what you learned.",
                    "Both are small, visible changes that demonstrate the practices rather than describing them.",
                ]),
                ("4 and 5. Baseline, and start the platform conversation", [
                    "Measure deployment frequency and lead time for ONE service this month - no tooling purchase required.",
                    "A baseline changes the conversation from opinions to evidence, permanently.",
                    "Ask around: which golden path would help the most teams? Two teams with the same need is a product signal.",
                    "Bring that answer, plus your baseline, to whoever funds platform work.",
                ]),
            ],
            "notes": "End with commitment rather than summary. Ask each participant to write down the ONE action they will take in their first week and to say it out loud to the room - spoken commitments are kept far more often than intended ones, and hearing five colleagues commit makes the sixth more likely to follow through. Push them toward the smallest finishable version of each item, because the most common failure after training is an ambitious initiative that stalls in week three and quietly discredits everything the person learned. Emphasise the baseline as the highest-leverage and cheapest action: measuring deployment frequency and lead time for a single service costs nothing, requires no approval, and permanently changes the quality of every subsequent discussion about delivery. Then hand out the feedback survey, answer the last questions, and close by reminding them that the package runs anywhere and is theirs to keep."
        },
    ],
}


# ===========================================================================
# DAY 2 - DIAGRAM + CENTRAL-BANK CONTEXT SLIDES
# Same convention and the same caveat as Day 1: the SARB scenarios are
# ILLUSTRATIVE teaching examples built from publicly known central-bank
# functions, not descriptions of internal systems.
# ===========================================================================
DAY2_CONTEXT = {

    "Microservice Design Principles": [
        {
            "type": "diagram",
            "title": "Service Boundaries - Bounded Contexts vs Distributed Monolith",
            "image": "36-service-boundaries",
            "caption": "Split by business domain and the split buys independence; split by layer and it buys only latency.",
            "notes": "Work the left panel first, because it is where most disappointing microservice programmes end up: services split by technical layer, sharing one database, released together. Every cost of distribution has been paid and no independence has been bought. Then the right panel: domains with private data, integrating through APIs and events, each team shipping alone. Land on the acid test in the blue box and let the room apply it to their own systems - if two services must always be released together, they are one service in two deployments. Close with the footnote, which is the responsible engineering advice: start with a well-structured monolith and split where you have a specific reason, because a distributed system is a permanent tax that should buy something concrete."
        },
        {
            "type": "detail",
            "title": "In Context: Service Boundaries in a Central Bank",
            "sections": [
                ("Domains that suggest themselves in this environment", [
                    "Settlement and payment processing; participant and account management; collateral; reporting.",
                    "Supervisory data intake, validation, and analysis - each a distinct capability with its own language.",
                    "Statistics production and publication; currency and cash logistics; internal corporate services.",
                    "The test remains: does each boundary let one team change and release without another team's calendar?",
                ]),
                ("Where the boundary conversation gets difficult here", [
                    "Shared reference data (participants, instruments, calendars) that everything needs - resist a shared schema.",
                    "Serve it as an owned service with an API and events, and let consumers keep their own read models.",
                    "Regulatory reporting that cuts across every domain - integrate from events rather than by joining databases.",
                    "Long-lived core systems that cannot be split - wrap them behind an API and split around them over time.",
                ]),
                ("Honest guidance for a systemically important estate", [
                    "Do not distribute a system just to modernise it; distribution adds failure modes you must then operate.",
                    "A well-structured monolith with clear internal modules is a legitimate and often superior choice.",
                    "Where you do split, split at a seam that a single team can own end to end - Conway's Law, used deliberately.",
                    "Every split must answer: what does independence buy us here, and can we operate the extra moving parts?",
                ]),
            ],
            "notes": "This audience does not need encouragement to adopt microservices; they need help deciding where a split is justified and where it is a liability. Be explicit that in a systemically important environment the added failure modes of distribution - partial failure, network latency, eventual consistency, distributed debugging - are real operational obligations, and that adding them without a specific benefit is poor engineering. The shared-reference-data problem is the one that comes up in every institution: everything needs participants, instruments and calendars, and the temptation is a shared database that every service reads. Give them the alternative - one owning service with an API and published events, with consumers keeping their own read models - and be honest that it is more work up front and far cheaper afterwards. The strangler pattern deserves a mention for core systems that cannot be split: wrap the existing system behind an interface, build new capability around it, and migrate function by function rather than attempting a rewrite."
        },
    ],

    "Twelve-Factor Apps - the Portability Contract": [
        {
            "type": "diagram",
            "title": "Build, Release, Run - the Portability Contract",
            "image": "35-twelve-factor",
            "caption": "One image digest, four configurations - and the properties that let a platform operate it.",
            "notes": "Use the top row to reinforce the Day 1 build-once-promote-many discipline, now with the reason spelled out: build produces the artefact, release binds it to an environment's configuration, and run starts processes from that release - strictly separate, so the artefact never changes as it moves. The fan-out to four environments is the payoff: the same digest everywhere, differing only in injected values, which is what makes a test result predictive and an artefact digest meaningful as change evidence. The two panels at the bottom are the properties Kubernetes assumes, so present them as prerequisites rather than advice - a stateful, slow-starting service that writes its own log files cannot be scheduled, scaled or healed, whatever the manifests say."
        },
        {
            "type": "detail",
            "title": "In Context: Twelve-Factor Against a Legacy Estate",
            "sections": [
                ("What usually blocks older applications", [
                    "Configuration compiled into the artefact or read from a machine-specific path on a named server.",
                    "Local state: sessions in memory, files on local disk, caches assumed to be warm and singular.",
                    "Log files written and rotated by the application, on a volume somebody has to manage.",
                    "Long start-up (minutes) and no signal handling, so restarts are disruptive and manual.",
                ]),
                ("A pragmatic migration order", [
                    "1. Externalise configuration first - it is the least invasive and it unlocks one-artefact promotion.",
                    "2. Move logs to stdout next; the platform then handles collection, retention and access control.",
                    "3. Extract state to a backing service - the hardest step, and the one that enables scaling and healing.",
                    "4. Add signal handling and health endpoints - small changes that make rollouts non-disruptive.",
                ]),
                ("Judgement calls in a regulated estate", [
                    "Not every system should be modernised - some are stable, low-change, and best left alone deliberately.",
                    "Prioritise by change frequency: applications that change often repay portability work fastest.",
                    "Vendor products may not honour the contract at all; then containerise what you can and be honest about the rest.",
                    "Record the decision (an ADR) so the next team knows what was chosen and why.",
                ]),
            ],
            "notes": "Most participants are not starting with greenfield services, so the value of this slide is sequencing rather than aspiration. Externalising configuration first is deliberate: it is the least invasive change, it usually requires no architectural work, and it immediately unlocks the one-artefact-many-environments discipline that everything else depends on. Extracting state is genuinely hard and often needs design work, so it belongs later, when the earlier wins have built confidence and credibility. Be explicit that not everything should be modernised - a stable system that changes twice a year and works is a poor investment target, and saying so protects the credibility of the recommendations you do make. Prioritise by change frequency, because portability work pays back per change. And for vendor products that cannot honour the contract, the honest answer is to containerise what is possible, document what is not, and design the operational model around the constraint rather than pretending it away."
        },
    ],

    "What a Container Actually Is": [
        {
            "type": "diagram",
            "title": "Container vs Virtual Machine",
            "image": "25-container-vs-vm",
            "caption": "No guest OS: processes on a shared kernel, isolated by namespaces and cgroups.",
            "notes": "Put the two stacks side by side and let the missing layer do the teaching: there is no guest operating system in the container stack, which is why images are megabytes rather than gigabytes and why start-up is milliseconds rather than tens of seconds. Then make the security consequence explicit, because it is the reason for everything in Module 7's hardening slide: the kernel is shared, so it is the trust boundary, and a container escape means host compromise rather than a hypervisor breakout. In an institution that runs mixed workloads with different sensitivity, that is a genuine design input - VM-level isolation remains the stronger boundary, and choosing between them is a risk decision rather than a fashion decision."
        },
        {
            "type": "detail",
            "title": "In Context: Containers Under Institutional Controls",
            "sections": [
                ("Questions your security colleagues will ask - and good answers", [
                    "'What is running?' - the image digest, its SBOM, and the commit it was built from. All machine-generated.",
                    "'Who can change it?' - nobody: images are immutable, and a change means a new digest through the pipeline.",
                    "'How do we patch?' - rebuild and redeploy on a schedule, not by logging in; patching becomes a pipeline run.",
                    "'What is the isolation?' - namespaces and cgroups on a shared kernel, hardened by policy (Module 7).",
                ]),
                ("Where containers genuinely improve control", [
                    "Environment parity: the dependency set travels with the application instead of living in a runbook.",
                    "Immutability: no in-place patching, so no undocumented divergence between instances.",
                    "Traceability: digest plus labels tie a running workload back to a commit and a pipeline run.",
                    "Rebuild-to-patch replaces a manual estate-wide task with an automated, evidenced one.",
                ]),
                ("Where you must be careful", [
                    "Registry governance: who may push, what is retained, is a tag immutable, are images signed?",
                    "Base image provenance: prefer curated, internally mirrored bases over arbitrary public images.",
                    "Ageing images: a service not rebuilt for months is running months-old packages - schedule rebuilds.",
                    "Classification: an image can carry embedded data or credentials - scan for secrets, and control access.",
                ]),
            ],
            "notes": "Frame containers in the language of the control conversations participants will actually have. The four questions in the first section are the ones security and audit colleagues ask, and containers answer them better than the alternative: what is running is a digest with an inventory, nobody can change it in place, patching is a rebuild through the reviewed path, and isolation is explicit and enforceable. Present that as a control improvement over long-lived mutable servers, because it is one. Then be balanced about the new obligations, which are real and often overlooked: registry governance (who can push, retention, tag immutability, signing), base image provenance - which in a supervised institution usually means an internally curated and mirrored set rather than pulling arbitrary public images - and the ageing problem, which needs a scheduled rebuild to solve. Ending on those obligations rather than on the benefits is what makes the recommendation credible to the people who have to approve it."
        },
    ],

    "Building Good Images": [
        {
            "type": "diagram",
            "title": "Image Layers, Cache Order and Multi-Stage Builds",
            "image": "26-image-layers",
            "caption": "Ship the runtime slice, not the workshop - and order layers so the cache actually works.",
            "notes": "Three ideas on one page. The layer stack explains sharing and why base image choice matters so much - fifty services on one base store that base once, and every CVE in it is inherited fifty times. The cache-ordering panel is the one participants feel immediately in the labs, because it is the difference between a ten-second and a three-minute rebuild on every commit. The multi-stage panel is the one with the largest security payoff: build tools, compilers and test dependencies never reach production, which both shrinks the image and removes the tooling an attacker would otherwise find waiting inside. Finish on the checklist, and point out the footnote about layer history - a secret added and then deleted is still in the image, which surprises almost everyone the first time."
        },
        {
            "type": "detail",
            "title": "In Context: An Institutional Base-Image Standard",
            "sections": [
                ("What a curated base-image set gives the institution", [
                    "A small number of approved, internally mirrored bases - patched, scanned and rebuilt centrally.",
                    "Teams inherit a hardened starting point instead of choosing from the whole internet.",
                    "One place to fix a widespread vulnerability, rather than forty repositories to chase.",
                    "Provenance: internally built and signed, so the supply chain starts inside the institution.",
                ]),
                ("The operating discipline that keeps it useful", [
                    "Rebuild the bases on a schedule, and publish new versions with clear release notes.",
                    "Notify consumers and track who is on which version - you cannot manage what you cannot see.",
                    "Automate the downstream rebuild, or teams will pin an old base forever and the effort is wasted.",
                    "Measure: what share of running images is on a base built in the last 30 days?",
                ]),
                ("What each delivery team still owns", [
                    "Multi-stage builds, non-root user, .dockerignore, and no credentials baked into any layer.",
                    "Health endpoints, graceful shutdown, fast start-up - the operability contract from twelve-factor.",
                    "Honest resource declarations so requests and limits can be set from evidence.",
                    "Keeping their own dependencies current - the base only covers the layers beneath them.",
                ]),
            ],
            "notes": "The curated base-image set is one of the highest-value, lowest-controversy platform products a regulated institution can build, so make the case concretely. It converts a widespread vulnerability response from 'contact forty teams and hope' into 'rebuild the bases, trigger downstream rebuilds, measure coverage', which is a dramatic improvement in both response time and evidence quality. Stress the operating discipline, because a curated base set that is not rebuilt and not adopted is worse than none: it creates the appearance of control while teams quietly pin an old version. The metric on the slide - the share of running images on a recently built base - is the honest measure, and it is the kind of number that belongs in an operational risk pack. Close by keeping the division of responsibility clear: the platform owns the bases and the automation, and each team still owns its own dependencies, its Dockerfile discipline, and the operability of its service."
        },
    ],

    "Why Orchestration - What Kubernetes Actually Does": [
        {
            "type": "diagram",
            "title": "The Reconciliation Loop",
            "image": "37-reconciliation-loop",
            "caption": "Declare the desired state; controllers observe, compare and act - continuously, forever.",
            "notes": "This is the mental model that makes Kubernetes predictable rather than mysterious. Trace the loop, then use the right-hand example: desired is five replicas, actual is four because a node died, and the difference is the work the controller does without anyone being paged. Say explicitly that self-healing is not a feature bolted on top - it is this loop noticing a difference. The bottom panel ties it back to Day 1: Terraform runs the same model on demand when a human types apply, and Kubernetes runs it continuously. Once participants hold that model, the surprising behaviours become obvious: a manually edited object gets reverted, a deleted pod comes back, and the cluster keeps retrying because the loop has no end state."
        },
        {
            "type": "detail",
            "title": "In Context: Should a Central Bank Run Kubernetes?",
            "sections": [
                ("The honest decision criteria", [
                    "Many teams needing a common runtime contract - that is the strongest argument for it.",
                    "Genuine elasticity or density requirements that manual placement cannot serve.",
                    "A platform team that can own cluster lifecycle properly - upgrades, certificates, capacity, patching, restores.",
                    "If none of these hold, containers on a simpler managed runtime is the professional choice, not a lesser one.",
                ]),
                ("What adopting it commits the institution to", [
                    "A cluster is production infrastructure with its own upgrade cadence and end-of-support dates.",
                    "New operational skills and new failure modes: scheduling, evictions, DNS, network policy, storage.",
                    "Security work that is genuinely different: RBAC, admission control, network policy, workload identity.",
                    "A support model: when the cluster is unwell, every service on it is unwell at the same time.",
                ]),
                ("If you do adopt - the sensible shape", [
                    "Managed control planes where available; keep cluster operation with the platform team, not with delivery teams.",
                    "Separate clusters by blast radius: critical vs non-critical, production vs everything else.",
                    "Start with internal, low-criticality workloads and build operational evidence before anything important moves.",
                    "Rehearse the unglamorous paths early: upgrade, certificate rotation, node loss, and restore from backup.",
                ]),
            ],
            "notes": "Give the room permission to say no, because a trainer who recommends Kubernetes universally loses credibility with an audience that carries real operational risk. Kubernetes is justified by multiple teams needing a common runtime contract and by real elasticity requirements, and it commits the institution to operating production infrastructure with a fast-moving upgrade cadence - which is a standing cost, not a project. Where the criteria are not met, containers on a simpler runtime deliver most of the portability benefit at a fraction of the operational burden, and choosing that deliberately is good engineering. If the institution does adopt, the shape on the slide matters: managed control planes reduce the hardest part, cluster operation belongs with a platform team rather than distributed across delivery teams, blast-radius separation should be designed rather than discovered, and the first workloads should be internal and low-criticality so that operational evidence accumulates before anything important depends on it. Rehearsing upgrades and restores early is the difference between a capability and a hope."
        },
    ],

    "The Working Vocabulary: Objects You Will Touch": [
        {
            "type": "diagram",
            "title": "The Objects and How They Relate",
            "image": "27-k8s-object-map",
            "caption": "Deployment owns ReplicaSets, ReplicaSets keep Pods, Services find Pods by label.",
            "notes": "Teach the ownership chain from this picture and have the room say it back: a Deployment owns ReplicaSets, a ReplicaSet keeps N Pods running, and a Service load-balances over Pods selected by label. Nearly every confusing behaviour becomes obvious from that chain - why rollback is instant (the previous ReplicaSet still exists), why deleting a pod achieves nothing, and why a Service silently serves nothing when a label is misspelled. The two bottom panels carry the operational content: configuration injected at runtime, and the probe/resource contract that tells the platform whether you are well and what you may consume. Workshop 2 creates every object on this page, and deliberately breaks a label selector, which is the fastest way to make the label-matching rule permanent."
        },
        {
            "type": "detail",
            "title": "In Context: Defaults Worth Setting Institution-Wide",
            "sections": [
                ("Make these the template defaults, not per-team decisions", [
                    "Probes present and correct on every workload - readiness separate from liveness, both cheap and local.",
                    "Resource requests and limits always set, with sensible starting values the team can tune from evidence.",
                    "Labels that the institution needs: owner, service, environment, classification, cost centre.",
                    "Security context (non-root, read-only root filesystem, dropped capabilities) already applied.",
                ]),
                ("Secrets - the specific caution", [
                    "Kubernetes Secrets are base64-ENCODED, not encrypted by default - do not let anyone assume otherwise.",
                    "Enable encryption at rest, restrict RBAC tightly, and integrate a real secrets manager for anything sensitive.",
                    "Prefer short-lived credentials issued to a workload identity over long-lived stored values.",
                    "Never dump the environment in logs or error pages - it is the most common accidental disclosure.",
                ]),
                ("Why defaults beat documentation here", [
                    "A template that already sets these means a new service is well-behaved before anyone reads a standard.",
                    "Admission policy then makes the baseline enforceable rather than advisory.",
                    "Assurance can examine one path rather than sampling forty independently-configured services.",
                    "And the delivery team spends its attention on the business problem, which is the entire point.",
                ]),
            ],
            "notes": "This slide converts the vocabulary into a platform specification, which is how it becomes useful rather than academic. Everything in the first section is something that should arrive with a scaffolded service rather than being derived by each team, and each item maps to a real failure the institution would otherwise meet: missing probes cause traffic to unhealthy pods, missing limits cause noisy-neighbour incidents, missing labels make ownership and cost unanswerable, and a missing security context leaves workloads running as root. The Secrets caution is worth repeating even if you covered it earlier, because the base64 misunderstanding is widespread and consequential - people genuinely believe the value is protected. Push workload identity as the strategic direction, since it removes the standing credential rather than merely rotating it. Close by restating the platform argument in assurance terms, because that is what makes this list fundable: one enforced baseline is inspectable, and forty hand-configured services are not."
        },
    ],

    "Managing Services at Scale": [
        {
            "type": "diagram",
            "title": "Scaling Levers, Mesh Trade-offs and Blast Radius",
            "image": "38-scaling-levers",
            "caption": "Three autoscaling levers, one expensive mesh decision, and isolation before exotic scaling.",
            "notes": "Take the three levers in turn and stress the shared prerequisite in red: none of them work on a service that is stateful or slow to start, so twelve-factor is the entry ticket to scaling. Mention the HPA/VPA conflict, because teams enable both on the same metric and are baffled by the result. On the mesh panel, keep the balance explicit - genuine capability on one side, a sidecar per pod and another control plane on the other - and give the decision rule: adopt for a specific requirement such as service-to-service mTLS or fine-grained traffic control, not for architectural completeness. The blast-radius panel carries the most valuable point for this audience: isolation usually buys more availability than another scaling mechanism, and deciding what shares fate with what is an availability design decision most institutions make by accident."
        },
        {
            "type": "detail",
            "title": "In Context: Scale, Isolation and Who Owns the Answers",
            "sections": [
                ("Scale in a central bank is usually about PEAKS, not growth", [
                    "Predictable peaks: settlement cycles, month and year end, reporting deadlines, publication windows.",
                    "So capacity planning and headroom often matter more than elastic autoscaling.",
                    "Test at peak shape, not at average load - and rehearse the peak before it arrives.",
                    "Where load is predictable, scheduled scaling is simpler and more reliable than reactive autoscaling.",
                ]),
                ("Isolation decisions worth making deliberately", [
                    "Separate critical industry-facing services from internal workloads - at cluster or cell level.",
                    "Separate environments completely; a lower environment must not be able to affect production.",
                    "Namespace quotas so one team's workload cannot starve another's during a peak.",
                    "Multi-region or multi-site is a resilience decision made with the business, not an engineering preference.",
                ]),
                ("Who owns which answer", [
                    "The platform owns cluster lifecycle, baseline policy, shared services and the scaling mechanisms.",
                    "The delivery team owns its service's resource profile, degradation behaviour and SLOs.",
                    "Neither owns the other: platform teams that tune application resources become a ticket queue.",
                    "Write the split down - ambiguity here produces gaps precisely during incidents.",
                ]),
            ],
            "notes": "The peaks-not-growth observation is the most useful reframing for this audience, and it changes the technical answer: where load is predictable and cyclical, scheduled scaling with generous headroom is more reliable than reactive autoscaling, which always lags the event it is reacting to. Encourage testing at peak shape rather than average, and rehearsing before known peaks, which is the same 'practise the thing you fear' principle from Module 8. The isolation section is where participants can make genuinely consequential decisions: separating critical industry-facing services from everything else, at cluster or cell level, is a resilience choice with a clear rationale that risk colleagues understand immediately. Finish by writing down the ownership split, because the ambiguity between platform and delivery responsibilities is invisible during normal operations and extremely expensive during an incident, when nobody is sure who is supposed to act."
        },
    ],

    "The Scanner Taxonomy - What Checks What, When": [
        {
            "type": "diagram",
            "title": "Where Each Scanner Runs",
            "image": "28-scanner-taxonomy",
            "caption": "Six different questions, six different moments - and two rules that decide whether any of it matters.",
            "notes": "Read the pipeline left to right and place each scanner at the moment it answers its question. The two rules at the bottom are the ones to repeat: earlier is cheaper, and report broadly while gating narrowly. Point out that the taxonomy also exposes gaps - most institutions have image scanning because it is easy to buy, and are much weaker on secret scanning of history and on IaC scanning, which are cheaper and often catch more consequential problems. Use the footnote to redirect effort: dependencies and secrets carry most real-world risk, so an organisation with limited capacity should start there rather than with the most sophisticated tool available."
        },
        {
            "type": "detail",
            "title": "In Context: A Scanning Programme That Survives",
            "sections": [
                ("Sequence the rollout by value and by cost of failure", [
                    "1. Secret scanning, including history - cheapest to run, and the findings are unambiguous.",
                    "2. Dependency (SCA) scanning on every pull request - where most exploitable risk actually lives.",
                    "3. Image scanning at build, with the report/gate split from Day 1.",
                    "4. IaC scanning on infrastructure changes; then SAST, tuned, once the earlier backlogs are under control.",
                    "5. DAST on a schedule against a staging environment - slower, noisier, still valuable.",
                ]),
                ("Making the output count as evidence", [
                    "Retain machine-readable results per build, keyed to the artefact digest - not screenshots in a document.",
                    "Route findings to the owning team automatically; unowned findings are never fixed.",
                    "Record exceptions with owner, rationale, compensating control and expiry - the assurance conversation, prepared.",
                    "Report the trend to leadership: fixable-critical backlog over time, per portfolio.",
                ]),
                ("Institutional realities to plan around", [
                    "Air-gapped or restricted networks need mirrored vulnerability databases - plan the update path.",
                    "False positives cost credibility fastest; budget tuning time from the start, not after the complaints.",
                    "Third-party and vendor-supplied software needs its own answer - scanning what you cannot rebuild.",
                    "Confirm specifics with your security and compliance colleagues - these are patterns, not policy advice.",
                ]),
            ],
            "notes": "Sequencing is the practical content here: institutions that turn everything on at once generate thousands of findings, no capacity to act, and a rapid loss of faith in the whole programme. Starting with secret scanning is deliberate - the findings are unambiguous, the remediation is well-defined, and the risk is severe - and dependency scanning next puts effort where most exploitable risk lives. Leave SAST until the earlier backlogs are under control, because its false-positive burden is what most often discredits security tooling with developers. On evidence, keep pushing the point that machine-readable results retained per digest are both cheaper and more credible than manual evidence packs. The institutional realities section matters for this audience specifically: restricted network environments need a planned mirror for vulnerability databases, and vendor-supplied software that cannot be rebuilt needs a different answer - usually contractual, plus compensating controls - which is worth raising with procurement colleagues rather than discovering later."
        },
    ],

    "Supply Chain Security - Your Pipeline Is a Target": [
        {
            "type": "diagram",
            "title": "The Supply Chain, Link by Link",
            "image": "29-supply-chain",
            "caption": "Every link is code you execute with production credentials - and five countermeasures in payoff order.",
            "notes": "Walk the links and ask the room, honestly, which ones they could enumerate today for one of their own pipelines - most institutions cannot list the third-party actions running in CI, and that inability is itself the finding. Then the countermeasures in payoff order: pinning and least privilege are cheap and remove standing exposure immediately, SBOM makes the next disclosure survivable, and signing with verification closes the loop between what the pipeline built and what the runtime will accept. The amber box at the bottom is the question to leave in the room: what would happen if your CI runner were compromised tonight? In a supervised institution, that is a legitimate third-party and operational risk question, and it usually has not been asked."
        },
        {
            "type": "detail",
            "title": "In Context: Supply Chain Risk as Third-Party Risk",
            "sections": [
                ("Use the language the institution already has", [
                    "Your delivery toolchain is a third party with production access - assess it the way you assess suppliers.",
                    "Concentration risk applies: what happens if one provider is unavailable during a critical window?",
                    "Change management applies: an unpinned action is an unreviewed change entering production daily.",
                    "Provenance and integrity are exactly the properties financial controls already care about.",
                ]),
                ("Controls that map cleanly to institutional expectations", [
                    "Pinned dependencies and actions = controlled change; nothing enters without review.",
                    "Least-privilege, short-lived pipeline credentials = access control and segregation of duties.",
                    "SBOM retained per artefact = asset inventory, answerable during a disclosure event.",
                    "Signing plus admission verification = only artefacts this institution built may run.",
                    "Internal mirrors for packages and base images = availability and provenance, together.",
                ]),
                ("Where to start given real constraints", [
                    "This week: pin actions to digests and declare least-privilege permissions per job.",
                    "This quarter: SBOM generation and retention; internal mirroring of bases and critical packages.",
                    "Next: signing on push and verification at admission; agree a target maturity level per service tier.",
                    "Document the target and the gap - a stated, evidenced roadmap is itself a strong assurance position.",
                ]),
            ],
            "notes": "The reframing on this slide is the one that gets supply-chain work funded in a regulated institution: the delivery toolchain is a third party with production access, and every concept the institution already applies to suppliers - concentration risk, change control, access control, asset inventory, provenance - maps directly onto it. Presenting the countermeasures in that vocabulary turns an engineering wish list into a recognisable control programme. Internal mirroring deserves specific mention here because it serves two institutional concerns at once: availability, since a build no longer depends on an external service being reachable during a critical window, and provenance, since the mirrored content is curated. Keep the starting advice modest and immediate - pinning and permissions are an afternoon's work - and stress that a documented target with an honest gap analysis is a far stronger assurance position than an aspiration, because it demonstrates that the institution understands its own exposure."
        },
    ],

    "Compliance as Code (OPA, Rego, Conftest)": [
        {
            "type": "diagram",
            "title": "One Rule, Two Enforcement Points",
            "image": "30-policy-as-code",
            "caption": "Written once, gated in the pipeline, backstopped at the cluster door - and the evidence writes itself.",
            "notes": "Follow the rule from left to right: written once in Git, evaluated in CI against the rendered output so the developer fixes it cheaply, and enforced again at admission so nothing that arrived another way can bypass it. The two-enforcement-point design is what makes the control complete - CI alone governs only those who use CI, and admission alone gives feedback far too late. The render-first panel prevents a subtle false-confidence failure, since templating adds exactly the labels and defaults that policies check. Land on the evidence panel, which is the reason this practice is worth the effort in a supervised institution: the rule, its history, every evaluation of it, and every exception, all produced as a by-product of working rather than assembled for an audit."
        },
        {
            "type": "detail",
            "title": "In Context: Encoding the Institution's Own Rules",
            "sections": [
                ("Rules that are natural candidates to encode", [
                    "Every workload sets resource limits, runs as non-root, and has probes.",
                    "Required labels present: owner, service, environment, data classification, cost centre.",
                    "Only images from approved internal registries, referenced by digest, and signed by our pipeline.",
                    "Network policy present; no privileged containers, host mounts or host networking.",
                    "Infrastructure: encryption enabled, no public exposure, tagging complete, retention configured.",
                ]),
                ("How to introduce it without a revolt", [
                    "Run in warn mode first and publish the current violation count - measure before enforcing anything.",
                    "Fix or automate the backlog with the teams, then enforce for NEW resources with a dated deadline for the rest.",
                    "Write failure messages that state the fix, not just the violation - a good message prevents a support ticket.",
                    "Keep exceptions owned, time-limited and reviewed; invisible workarounds are the alternative.",
                ]),
                ("What this replaces, and why it is stronger", [
                    "It replaces a standards document with an unknown compliance rate and a sample-based annual review.",
                    "It gives an exact, continuous answer: every change evaluated, every result recorded.",
                    "The rule and its history are reviewable by the people accountable for the standard.",
                    "Agree the mapping between institutional standards and policy files once - then reuse it everywhere.",
                ]),
            ],
            "notes": "The candidate rules on this slide are deliberately mundane and universally applicable, because that is where policy as code produces value fastest: they are unambiguous, machine-checkable, and currently enforced - if at all - by human review. Encourage participants to pick two or three, encode them, and run in warning mode to see the real violation count, which is almost always higher than expected and makes the case by itself. The rollout advice protects the programme: measuring before enforcing, fixing the backlog with teams, enforcing for new resources first, and writing failure messages that state the fix. The last section is the argument to take to whoever owns the standards: this does not weaken the standard, it converts it from a document with an unknown compliance rate into a control with an exact and continuous one. Recommend agreeing the mapping between written institutional standards and policy files once, formally, so that every future service inherits an already-accepted control position rather than reopening the discussion."
        },
    ],

    "Runtime Hardening - Platform Defaults, Not Team Chores": [
        {
            "type": "diagram",
            "title": "Hardening in Three Layers",
            "image": "39-hardening-layers",
            "caption": "Container, cluster and secrets - specified once, enforced by policy, inherited by every team.",
            "notes": "Present this as a specification for the golden path rather than a checklist for each team, because that is the argument: forty independently hardened services have forty different postures, and one enforced baseline is assessed once and inherited everywhere. Highlight two items that surprise people. Default-deny network policy: without it every pod can reach every other pod, which contradicts the mental model of anyone whose background is network zoning. And the secrets column, where the base64 misunderstanding lives - encoded is not encrypted, so encryption at rest, tight RBAC and a real secrets manager are all required. Everything on the page is checkable by the policy engine from the previous slide, which is what turns it from advice into an enforced baseline."
        },
        {
            "type": "detail",
            "title": "In Context: Hardening Under Supervisory Expectations",
            "sections": [
                ("Map the technical controls to the institution's concerns", [
                    "Least privilege everywhere - workloads, service accounts, pipeline tokens, registry and cluster access.",
                    "Segregation: network policy between environments and between critical and non-critical workloads.",
                    "Cryptographic protection: encryption at rest and in transit, with keys managed by a proper service.",
                    "Auditability: API server audit logs, immutable pipeline records, and change traceable to a person.",
                ]),
                ("Operational hygiene that is easy to neglect", [
                    "Cluster and node patching on a schedule, with the upgrade path rehearsed before it is needed.",
                    "Certificate lifecycle - expiries are a classic self-inflicted outage; automate issuance and renewal.",
                    "Periodic RBAC review: permissions accumulate quietly, and nobody notices until an assessment.",
                    "Scheduled image rebuilds so the hardened baseline does not silently age.",
                ]),
                ("Getting it agreed rather than imposed", [
                    "Bring security colleagues in while designing the baseline, not at the approval gate afterwards.",
                    "Show the enforcement mechanism, not just the intention - a policy that fails a build is persuasive.",
                    "Agree the exception process up front, including who approves and how expiry is tracked.",
                    "Then reuse the agreed baseline for every subsequent service - the second conversation is far shorter.",
                ]),
            ],
            "notes": "The mapping in the first section is what lets participants have this conversation in their institution's language rather than in Kubernetes vocabulary: least privilege, segregation, cryptographic protection and auditability are concerns the organisation already has policies about, and the technical controls implement them. The operational hygiene section covers the things that cause real incidents and are easy to defer - certificate expiry in particular has taken down more services in this sector than any exotic attack, and it is entirely automatable. The final section is process advice worth stating plainly: security colleagues brought in during design become co-authors of the baseline and its strongest advocates, while the same people brought in at an approval gate become an obstacle, through no fault of their own. Showing a policy that actually fails a build is far more persuasive than describing an intention, and agreeing the exception process before it is needed prevents the first exception from becoming a precedent nobody tracks."
        },
    ],

    "Triage Discipline - Living With Scanner Output": [
        {
            "type": "diagram",
            "title": "From Findings to Decisions",
            "image": "40-triage-funnel",
            "caption": "Four questions turn hundreds of findings into three actionable buckets.",
            "notes": "The funnel converts an unmanageable list into three decisions: fix now, track with an owner, or accept with an expiry. Walk the four questions in order and stress the first two, because they remove most of the noise - fixable findings are usually a version bump, and unreachable code paths are genuinely lower risk however alarming the score. The three outcome boxes are the operational content: the gate blocks only the fixable and critical, the backlog is owned and watched, and acceptances carry an owner, a reason and an expiry date. Finish on the reduction line at the bottom, because it is where the leverage is - slimmer bases, dependency bots and scheduled rebuilds remove more findings than any amount of triage meeting time."
        },
        {
            "type": "detail",
            "title": "In Context: Vulnerability Debt in a Supervised Institution",
            "sections": [
                ("Reporting that stands up to scrutiny", [
                    "Report by service tier: critical industry-facing services held to tighter deadlines than internal tools.",
                    "Show the trend and the ageing profile, not just today's count - direction of travel is the real signal.",
                    "Name owners; an unowned finding on a report is an unowned risk in the estate.",
                    "Publish the exception register with expiry dates, and review it on a fixed cadence.",
                ]),
                ("Remediation deadlines that are actually achievable", [
                    "Set them by severity AND exposure AND tier - a single institution-wide deadline satisfies nobody.",
                    "Budget standing capacity for remediation, or it will always lose to delivery until it becomes an emergency.",
                    "Automate the routine path: dependency-update pull requests plus a reliable test suite do most of the work.",
                    "Escalate on ageing, not only on severity - a medium finding open for a year is a process failure.",
                ]),
                ("Third-party and unsupported software", [
                    "Vendor products you cannot rebuild need a different answer: contractual expectations plus compensating controls.",
                    "Track end-of-support dates as a first-class risk - unsupported software is an accepted risk by default.",
                    "Keep an inventory that includes what you did not build; SBOMs help, but procurement records matter too.",
                    "Raise this with vendor management colleagues - it is their process, and it needs your technical input.",
                ]),
            ],
            "notes": "This slide is about making vulnerability management sustainable and reportable in an environment where someone will eventually ask hard questions about it. Tiered reporting and tiered deadlines are the key ideas: a single institution-wide remediation deadline is either impossible for critical systems or absurdly lax for internal tools, and tiering by exposure and criticality is both more defensible and more achievable. The ageing-based escalation is worth emphasising because most programmes escalate on severity alone and therefore never notice the medium finding that has been open for eighteen months, which is exactly the pattern an assessor will find. The third-party section addresses the gap most technical discussions skip: a large share of a central bank's software is bought rather than built, cannot be rebuilt to fix a dependency, and needs contractual and compensating-control answers. Encourage participants to bring their technical inventory to the colleagues who own vendor management, because neither group can solve it alone."
        },
    ],

    "Monitoring Asks Known Questions; Observability Answers New Ones": [
        {
            "type": "diagram",
            "title": "One Request, One Trace",
            "image": "41-trace-correlation",
            "caption": "A propagated trace ID turns five services' logs into one answerable story.",
            "notes": "The waterfall makes the value obvious in a way that no definition does: one identifier, propagated across every hop, shows exactly where the time went - and the answer required no new logging and no deploy. Ask the room how they would answer the same question today, and the usual honest answer is 'add logging and redeploy', which is precisely the gap. The two bottom panels split the work into what makes new questions answerable (structured logs, propagated IDs, business context as labels) and what must be designed rather than discovered (sampling, retention tiers, and personal data in telemetry). That last point matters here: telemetry carrying personal data is a data-protection question, and it is far cheaper to design for than to remediate."
        },
        {
            "type": "detail",
            "title": "In Context: Observability for Payments, Data and Publications",
            "sections": [
                ("What 'the user experience' means for central-bank workloads", [
                    "For a transactional service: request success rate and latency, per participant and per channel.",
                    "For settlement and batch: completion within the window, and the margin left before the cut-off.",
                    "For data intake: submissions received, validation pass rate, and time to a usable dataset.",
                    "For publications: readiness before the scheduled time, and correctness checks passing.",
                ]),
                ("Context labels worth carrying from the start", [
                    "Participant or counterparty identifier, channel, message or instruction type, and service version.",
                    "Business date and cycle - a great deal of this work is date-bound rather than continuous.",
                    "Environment and data classification, so telemetry access controls can be applied automatically.",
                    "Keep cardinality bounded deliberately: use identifiers as trace attributes, not as metric labels.",
                ]),
                ("Data protection in telemetry", [
                    "Assume logs and traces will carry personal or confidential data unless you actively prevent it.",
                    "Scrub or tokenise at the source; do not rely on downstream redaction you cannot verify.",
                    "Apply retention and access control to telemetry as you would to the underlying records.",
                    "Agree the approach with your data-protection colleagues before you instrument broadly, not after.",
                ]),
            ],
            "notes": "The first section is the one that makes this module land for a central-bank audience, because most observability material assumes a web request-response world and a great deal of this institution's work is scheduled, batch and date-bound. Reframing the indicators accordingly - completion before a cut-off, margin remaining, validation pass rate, readiness before a publication time - turns observability from a web-service concept into something directly applicable to settlement windows, supervisory data intake and statistical releases. The context labels section is practical advice with a trap attached: business identifiers are exactly the dimensions you want to slice by, and putting high-cardinality identifiers into metric labels is the fastest way to overwhelm a metrics backend, so the guidance is to keep them as trace and log attributes. The data-protection section should be raised early and firmly: telemetry routinely carries personal data, scrubbing belongs at the source, and agreeing the approach with data-protection colleagues before broad instrumentation avoids an expensive retrofit."
        },
    ],

    "SLI, SLO, SLA - and the Error Budget": [
        {
            "type": "diagram",
            "title": "SLI, SLO and the Error Budget",
            "image": "31-slo-error-budget",
            "caption": "Reliability becomes a spendable, agreed number instead of an argument between temperaments.",
            "notes": "Walk the ladder - measurement, internal target, external contract - and stress that the SLO is chosen rather than inherited, which is where most of the value lies. The budget bar is the idea to leave in the room: the gap between the target and 100% is a resource that may be deliberately spent on change, and when it is exhausted, reliability work takes priority by prior agreement. Emphasise 'prior agreement' - the policy is set while everyone is calm, so nobody negotiates during an incident. The red box on the right is worth arguing for explicitly in a risk-averse institution: 100% is not a target, it is an unfunded aspiration, and each additional nine multiplies cost while users often cannot perceive the difference."
        },
        {
            "type": "detail",
            "title": "In Context: SLOs Where the Deadline Is the Mandate",
            "sections": [
                ("Time-bound obligations need time-bound indicators", [
                    "For a settlement or clearing window: proportion of cycles completed before the cut-off, and the margin left.",
                    "For a scheduled publication: readiness at a fixed time, with correctness checks passed beforehand.",
                    "For supervisory data: submissions processed within the agreed turnaround, and validation quality.",
                    "'Availability' alone is a poor indicator when the real obligation is 'finished, correctly, before a time'.",
                ]),
                ("Setting targets in a low-tolerance environment", [
                    "Differentiate by service tier: an industry-facing payment path and an internal dashboard are not comparable.",
                    "Use history: what has the service actually delivered, and did anyone experience the gap?",
                    "Where the obligation is absolute (a legal or industry deadline), the SLO is about MARGIN, not about failure.",
                    "Then the budget conversation becomes: how much margin are we prepared to erode with change this month?",
                ]),
                ("Using the budget without weakening the mandate", [
                    "The budget governs discretionary CHANGE, not the obligation - it is a change-risk policy, not a licence to fail.",
                    "Exhausted budget means: freeze non-essential change, fix reliability, and say so openly.",
                    "Healthy budget means: proceed with planned change, with the evidence to support that decision.",
                    "Agree the policy in advance with the business owners - that agreement is what makes it usable under pressure.",
                ]),
            ],
            "notes": "The reframing that makes SLOs work in this environment is margin rather than failure. Where an obligation is effectively absolute - an industry cut-off, a legally scheduled publication - it is unhelpful to talk about a permitted failure rate, and far more useful to define the indicator as margin before the deadline and the objective as maintaining that margin. The error budget then governs how much discretionary change the team is prepared to make against that margin, which is exactly the right conversation and one that business owners understand immediately. Be very clear about what the budget is not: it is not permission to miss a mandated obligation, it is a change-risk policy. Making that distinction explicit is what allows the practice to be adopted in a supervised institution rather than rejected as inappropriate. Encourage participants to define one indicator this way for a real service and take it to the business owner - the conversation itself usually surfaces that nobody had ever stated the reliability expectation quantitatively."
        },
    ],

    "Alerting That Respects Humans": [
        {
            "type": "diagram",
            "title": "Page on Symptoms, Ticket on Causes",
            "image": "32-alerting-burn-rate",
            "caption": "Two windows, two urgencies - and three tests every page must pass.",
            "notes": "The left/right split is the heuristic to take home, and the burn-rate panel is the modern refinement: a fast window catches the sudden outage and pages, a slow window catches the steady leak and raises a ticket, and neither fires for a brief harmless blip. Tie each page back to the error budget so that every interruption is connected to something the organisation already agreed matters. The three tests at the bottom - actionable, urgent, novel - are a review tool participants can apply to their existing alert set this month, and the exercise typically removes a large share of their pages while improving detection. Close on the last line and mean it: alert fatigue is a safety failure, not a personal resilience problem."
        },
        {
            "type": "detail",
            "title": "In Context: On-Call in a 24-Hour Obligation Environment",
            "sections": [
                ("Design the rotation before the alerts", [
                    "Follow the obligation: cover the hours the service actually matters, including settlement and batch windows.",
                    "Adequate depth: a rotation with two people is not a rotation, it is two people with no holidays.",
                    "Compensate on-call, cap consecutive shifts, and track load - fatigue is an operational risk, not a virtue.",
                    "Developers in the response path for their own services, with execution following the institution's access rules.",
                ]),
                ("What every alert needs before it is allowed to page", [
                    "A runbook: what this means, what to check first, what to do, and who to escalate to.",
                    "A named owning team, so nobody receives a page for a system they do not own.",
                    "An escalation path with a time limit, and a documented decision authority for out-of-hours action.",
                    "A statement of business impact, so the responder knows what is actually at stake.",
                ]),
                ("Measure the human side and report it", [
                    "Pages per shift, out-of-hours share, and time to acknowledge - published alongside other operational metrics.",
                    "Every false page reviewed in the following week: tuned or deleted, never merely tolerated.",
                    "Rising page volume is a regression to be investigated, not evidence of diligence.",
                    "Review on-call health in retrospectives - it is a system property, not an individual's endurance.",
                ]),
            ],
            "notes": "In an institution with time-critical obligations, on-call is a real operational capability and deserves to be designed rather than improvised. The rotation-depth point is worth making bluntly: a rotation resting on two people is a single point of failure with a holiday calendar attached, and it will fail at the worst moment. The requirement that every alert carries a runbook, an owner, an escalation path and a statement of business impact is what turns a page into an actionable event, and the out-of-hours decision authority is specific to this environment - a responder at 03:00 needs to know what they are permitted to do without waking three managers, and that should be written down in advance. On measurement, publishing pages per shift and the out-of-hours share alongside other operational indicators makes an invisible burden visible, and it is usually the fastest route to getting the alert-tuning work funded."
        },
    ],

    "Designing for Failure - Reliability Patterns": [
        {
            "type": "diagram",
            "title": "Patterns for Partial Failure",
            "image": "33-reliability-patterns",
            "caption": "Timeouts, retries with jitter, circuit breakers, bulkheads - and recovering fast beats all of them.",
            "notes": "Take the four patterns in order and give each its failure mode as well as its purpose, because each one can make things worse when applied naively - especially retries, which have turned many minor incidents into major ones by multiplying load on a struggling dependency. The sentence to repeat is on the first card: slow is worse than down, because a dead dependency fails fast while a sick one holds your threads and connections until you fall over too. The green panel at the bottom is the strategic point and connects Day 1 to Day 2: redundancy plus a rollback measured in seconds returns more availability than another layer of prevention, which is why immutable artefacts and one-command rollback are reliability engineering rather than merely delivery convenience."
        },
        {
            "type": "detail",
            "title": "In Context: Degradation and Recovery Where Correctness Is Absolute",
            "sections": [
                ("Idempotency is not optional in financial flows", [
                    "Once retries exist, the same instruction WILL arrive twice - design for it explicitly.",
                    "Client-supplied idempotency keys, deduplication windows, and durable records of what was already processed.",
                    "The failure mode here is not an outage, it is a duplicate transaction - far more expensive to unwind.",
                    "Test it deliberately: replay the same request and assert that nothing happens twice.",
                ]),
                ("Degradation modes must be agreed with the business", [
                    "Decide in advance what reduced service is permitted: queue and confirm later, read-only mode, reject cleanly.",
                    "Where correctness is absolute, the right degraded mode is often an honest, immediate rejection - not a guess.",
                    "Write it down per dependency, and make the behaviour visible to operators and to counterparties.",
                    "The wrong time to invent this is at 03:00 during the incident, by whoever happens to be on call.",
                ]),
                ("Recovery is the capability worth rehearsing", [
                    "Time your restore, your failover and your rollback - a plan without a measured time is a hope.",
                    "Rehearse before the peaks you already know about: settlement cycles, month end, publication dates.",
                    "Game days on a scheduled Tuesday morning surface the gaps while everyone is awake and calm.",
                    "Record what you learned and fix one thing after each drill - that is the Third Way, made concrete.",
                ]),
            ],
            "notes": "Idempotency deserves the most airtime here because the consequence in this environment is different from a typical web application: a duplicated instruction in a financial flow is not an availability incident, it is a correctness incident, and unwinding it is expensive and visible. Make the requirement explicit - client-supplied keys, deduplication windows, durable processing records - and recommend testing it by deliberate replay rather than assuming it. The degradation section carries a nuance worth stating carefully: in domains where correctness is absolute, graceful degradation often means refusing cleanly and immediately rather than accepting work you cannot complete, and that is a business decision the engineering team must not make alone. The rehearsal section is the practical close: participants can time a restore this month without any tooling investment, and the number they get is the most useful reliability metric they do not currently have."
        },
    ],

    "User-Centric Design for Internal Platforms": [
        {
            "type": "diagram",
            "title": "Platform as a Product",
            "image": "34-platform-product",
            "caption": "An adoption funnel, four published numbers, and the ROI sentence.",
            "notes": "The funnel is the frame: aware, tried, running in production, would recommend. Every drop-off between those stages is a product problem with a specific cause - discoverability, friction, documentation or trust - and locating the drop-off tells the platform team what to fix next, which is far more useful than a roadmap written from architectural preference. The four numbers on the right are what a platform team should publish every quarter, and the ROI sentence underneath is how the work gets funded. Close on the orange band: start from the thinnest viable platform, because the most expensive failure in this space is two years of building followed by no adoption."
        },
        {
            "type": "detail",
            "title": "In Context: Discovering What SARB Teams Actually Need",
            "sections": [
                ("Where to look for the real pain", [
                    "Time a real change end to end with one team, marking every hour as work or wait (the Day 1 exercise).",
                    "Count the systems a developer must touch to get a new service into a test environment.",
                    "Ask what they built themselves because nothing existed - shadow tooling is a requirements document.",
                    "Ask what they gave up on. The abandoned attempt is usually the most valuable story you will hear.",
                ]),
                ("Likely first golden paths in this environment", [
                    "A standard internal web service or API: repository, pipeline, environments, dashboard, alerts.",
                    "A scheduled batch or data-processing job with logging, retries, monitoring and evidence built in.",
                    "A reporting or publication pipeline with validation, approval and an auditable release step.",
                    "Pick the shape that the most teams need - the second team asking for the same thing is the signal.",
                ]),
                ("Documentation as the interface, here specifically", [
                    "A quickstart that works verbatim, tested in CI, and reachable without asking anyone where it is.",
                    "Explicit statements of what the path guarantees: which controls it satisfies, and what the team still owns.",
                    "That control statement is what lets a team adopt the path without reopening the assurance conversation.",
                    "Test it with a genuine newcomer each quarter: can they succeed unaided in one sitting?",
                ]),
            ],
            "notes": "Discovery advice tailored to this environment: the pain in a supervised institution is rarely in writing code, it is in the surrounding process - environments, access, test data, approvals, evidence - so the value-stream timing exercise is the right instrument, and it produces numbers rather than opinions. The question about what teams built themselves is the most productive one in any platform interview, because shadow tooling is a precise statement of unmet need. On golden paths, note that a batch or data-processing path may serve more teams here than a web service path, which is a genuine difference from the typical technology-company platform and worth checking rather than assuming. The documentation point has a specific twist for this audience that is worth emphasising: the docs should state which institutional controls the path satisfies and what the consuming team still owns, because that statement is what allows a team to adopt without re-running the whole assurance conversation - and it is the single feature that most accelerates adoption in a regulated organisation."
        },
    ],

    "Measuring Success and ROI": [
        {
            "type": "diagram",
            "title": "Baseline First, Then Prove It",
            "image": "42-platform-roi",
            "caption": "You cannot reconstruct the before-picture afterwards - measure it while it still exists.",
            "notes": "The single most important instruction on this slide is the red panel: measure the before-picture now, because it cannot be reconstructed later and without it every subsequent claim is an assertion. Agreeing those numbers with the delivery teams themselves also makes the later comparison credible rather than self-reported. The arithmetic band is deliberately simple so it survives a finance conversation, and the advice to prefer a conservative defensible number over an impressive fragile one is worth repeating. Close on the amber band, which is the framing for this institution: lead with control uniformity and assurance cost, then add the delivery numbers - the risk case opens the door, and the speed case walks through it."
        },
        {
            "type": "detail",
            "title": "In Context: Proving Platform Value to a Central Bank",
            "sections": [
                ("Numbers this institution will find persuasive", [
                    "Time-to-first-deploy for a new internal service, before and after - measured end to end, including access.",
                    "Number of independently-built pipelines reduced to one assessed path - an assurance-scope reduction.",
                    "Audit evidence produced automatically versus assembled by hand - hours saved every cycle, every service.",
                    "Consistency: percentage of services meeting the security baseline, measured continuously rather than sampled.",
                ]),
                ("Risk-framed benefits, stated in the institution's own terms", [
                    "Fewer distinct control implementations means a smaller assessment surface and fewer findings.",
                    "Continuous evidence replaces point-in-time sampling - a genuine improvement in control assurance.",
                    "Faster, rehearsed recovery paths reduce operational risk exposure in a measurable way.",
                    "Reduced key-person dependency: the path is documented, automated and inspectable rather than remembered.",
                ]),
                ("Keeping the story honest", [
                    "Report the same measures in the same format every quarter; consistency is what builds belief.",
                    "Include what is NOT working - a platform report that is entirely positive is not read as credible.",
                    "Segment by team so you can see who is not adopting and find out why, rather than averaging it away.",
                    "Tie the numbers to decisions: what will you build next because of what this told you?",
                ]),
            ],
            "notes": "Adapt the ROI argument to what this institution values. Delivery speed matters, but assurance scope and control consistency matter more to the people who approve budgets and carry the risk, so lead with them: reducing forty independently-built pipelines to one assessed path is a direct reduction in assessment surface, and continuous evidence replacing point-in-time sampling is a genuine improvement in control assurance rather than a productivity claim. The key-person dependency point also lands well here, because it is a risk category the institution already tracks in other contexts. On honesty, the advice to include what is not working is practical rather than moral: entirely positive internal reports are discounted by experienced readers, while a report that names its own gaps and shows the trend earns credibility - and credibility is what secures the next quarter's funding."
        },
    ],

    "Operating Model - and What NOT to Build": [
        {
            "type": "diagram",
            "title": "Funding, Running and Evolving the Platform",
            "image": "43-platform-operating-model",
            "caption": "Product-funded, production-grade, deprecating carefully, and willing to say no.",
            "notes": "The left/right comparison at the top is the structural decision that determines whether a platform survives: project funding produces a deliverable and then leaves it to decay, while product funding sustains a team that keeps it alive. The three middle panels are the operating disciplines - the platform is production, deprecation needs versioning and migration windows, and saying no is a product skill rather than unhelpfulness. The bottom band is the Team Topologies point: the relationship with each team should evolve from collaboration during discovery to a self-service relationship once the path exists, and being stuck at either end is a diagnosable failure. Close on the footnote - a platform team that deploys everyone's code has rebuilt the wall with better tooling."
        },
        {
            "type": "detail",
            "title": "In Context: A Platform Operating Model That Fits SARB",
            "sections": [
                ("Funding and mandate", [
                    "Fund it as a standing product team with an owner and a roadmap, not as a time-boxed project.",
                    "Give it an explicit mandate covering the golden paths, and an explicit list of what it will NOT own.",
                    "Include the assurance relationship in the mandate: the platform maintains the agreed control mapping.",
                    "If a standing team cannot be funded, build something smaller that a small team can genuinely sustain.",
                ]),
                ("Running it as production", [
                    "SLOs, monitoring, on-call and an incident process for the platform itself - its outages are everyone's outages.",
                    "Published support hours and response expectations, and a change calendar users can see.",
                    "Versioned templates and modules with real migration windows - never silent breaking changes.",
                    "Its own disaster-recovery position: if the pipeline and registry are unavailable, what can still be deployed?",
                ]),
                ("Relationship with the rest of the institution", [
                    "Collaborate closely while discovering; move deliberately to self-service once the path is proven.",
                    "InnerSource so delivery teams can contribute capability instead of queueing for it.",
                    "Rotate engineers through the platform team - former users make the best platform product decisions.",
                    "And keep the test in view: if teams file tickets and wait, it is a silo, whatever the org chart calls it.",
                ]),
            ],
            "notes": "Three points specific to this institution. First, the mandate should state what the platform will NOT own as clearly as what it will, because in an organisation with many specialised departments an unbounded platform mandate becomes an internal consulting queue within a year. Second, the disaster-recovery question for the platform itself is one almost nobody asks and this audience will appreciate: if the pipeline, registry or cluster control plane is unavailable during an incident, what can still be deployed, and by what route? That question deserves a documented answer, and rehearsing it is a legitimate resilience exercise. Third, the assurance relationship belongs in the mandate: the platform team maintaining the agreed mapping between institutional standards and enforced controls is what allows every consuming team to inherit an accepted control position, and it is arguably the platform's single most valuable output in a supervised environment."
        },
    ],

    "The Three Workshops - Map": [
        {
            "type": "diagram",
            "title": "The Three Workshops and the Capstone",
            "image": "44-workshops-map",
            "caption": "One application, three workshops, one golden path at the end.",
            "notes": "Use this as the map for the rest of the course. Each column states what participants build, the concepts it makes real, and the explicit success criterion - and the criteria are deliberately observable, because 'done' in this course means demonstrable rather than 'I ran the commands'. The arrows into the capstone are the point: the three workshops are not separate exercises but the three halves of one delivery path, assembled at the end into something that resembles a golden path with a handover document. Remind the room of the working method in the footnote before they start - read the error, check the troubleshooting table, ask three neighbours, then ask you."
        },
        {
            "type": "detail",
            "title": "In Context: Mapping the Workshops to Your Own Estate",
            "sections": [
                ("As you work, keep a second list", [
                    "For every step, note what your own environment would additionally require - access, zoning, approval, evidence.",
                    "That list is the gap between this lab and your institution's first real golden path.",
                    "It is also the agenda for your first conversation with risk, security and audit colleagues.",
                    "Two participants doing this for different departments will produce a strikingly similar list.",
                ]),
                ("Candidate first services back at work", [
                    "Internal, low-criticality, changed reasonably often, with a team willing to try it.",
                    "Avoid anything on a settlement, publication or supervisory-deadline path for the first attempt.",
                    "Prefer a service where you already control the repository, the pipeline and the target environment.",
                    "Success here buys the mandate for the second, more consequential one.",
                ]),
                ("What to capture for the handover", [
                    "What the path does automatically, and which institutional controls that satisfies.",
                    "What the consuming team still owns - explicitly, so nothing falls between the two.",
                    "How to run it, how to roll back, and who to call when it misbehaves.",
                    "What you would build next, and why - the beginning of a platform roadmap.",
                ]),
            ],
            "notes": "This slide turns the workshops from an exercise into preparation for real work. The second list - what your own environment would additionally require at each step - is the single most useful artefact participants can produce today, because it converts a vague sense that 'this would be harder at work' into a specific, discussable inventory: identity integration, network zoning, masked test data, change records, evidence retention, approval gates. Encourage them to write it in the margin as they go rather than trying to reconstruct it afterwards. The candidate-service guidance is deliberately conservative, and worth saying plainly: the first attempt should not be on a critical path, both because the risk is unnecessary and because the conversation with assurance colleagues is far easier when the stakes are low and the evidence is real. The handover capture list is what makes the difference between a personal experiment and something the institution can build on."
        },
    ],

    "Workshop Success Criteria": [
        {
            "type": "detail",
            "title": "In Context: What 'Done' Should Mean Back at Work",
            "sections": [
                ("Carry the verification habit home", [
                    "A pipeline that is green is not proof - a smoke test against the deployed thing is.",
                    "A backup that exists is not proof - a timed restore is.",
                    "A policy that is written is not proof - a build it actually failed is.",
                    "A runbook that exists is not proof - someone unfamiliar completing it unaided is.",
                ]),
                ("What to demonstrate to your own stakeholders", [
                    "Show the pipeline failing on purpose, then passing - controls are more convincing when seen to bite.",
                    "Show a rollback performed live, and state the measured time it took.",
                    "Show the evidence trail: commit, review, approval, scan result, artefact digest, deployment record.",
                    "Show the drift detection reporting a manual change - that one lands with auditors immediately.",
                ]),
                ("Write it down while it is fresh", [
                    "Your handover document is the deliverable, not the running system - systems without documents do not transfer.",
                    "Short and honest: what works, what does not, what you would do next.",
                    "Include the gap list from the previous slide - it makes the next conversation concrete.",
                    "Then diary an hour within two weeks to run the whole thing again, unaided.",
                ]),
            ],
            "notes": "The verification habit is the durable skill in this course, so state it in the four forms on the slide - green is not proof, a backup is not proof, a written policy is not proof, an existing runbook is not proof. Each pair names a specific complacency that causes real incidents. The demonstration advice is practical politics: technical stakeholders and assurance colleagues are far more convinced by seeing a gate fail and then pass, a rollback timed live, and drift detection catching a manual change, than by any slide describing those capabilities. Encourage participants to prepare exactly those three demonstrations for their own organisation. Close by pushing the handover document and the diarised unaided repetition, because those two habits are what determine whether this course produces a changed practice or a pleasant memory."
        },
    ],

    "What You Built in Two Days": [
        {
            "type": "diagram",
            "title": "The Loop You Walked",
            "image": "45-two-day-journey",
            "caption": "Plan, build, secure, deploy, operate - once, end to end, with your own hands.",
            "notes": "Walk the loop and name the module and workshop behind each step, so two days of separate exercises become one coherent story participants can retell. Emphasise the two items people undersell: they rolled a deployment back on command, and they survived a deliberately induced incident - recovery demonstrated rather than assumed, which is the difference between a demo and a capability. The amber band at the bottom is the honest part, and it should not be skipped: identity, zoning, data classification, evidence retention and immovable windows are the institutional wrapping this lab deliberately omitted, and adding them is the real work waiting at home. Finish on the advice in the band - prove the pattern on something low-criticality, then bring evidence rather than enthusiasm to the assurance conversation."
        },
        {
            "type": "detail",
            "title": "In Context: Turning Two Days Into an Institutional Capability",
            "sections": [
                ("What one person can start alone", [
                    "Baseline your own team's deployment frequency and lead time - no permission needed.",
                    "Add a real gate to one pipeline you already own, starting narrow so it is trusted.",
                    "Write one ADR and run one blameless review after the next incident.",
                    "Automate one repeated manual task, finish it completely, and time the before and after.",
                ]),
                ("What needs two or three people", [
                    "An end-to-end proof on one low-criticality service: pipeline, IaC, scan, deploy, dashboard, rollback.",
                    "The control mapping conversation with risk, security and audit - bring the working thing, not a proposal.",
                    "A shared base image or pipeline template that a second team can reuse without asking you.",
                    "A short written record of the pattern so the next team does not start from zero.",
                ]),
                ("What needs institutional backing", [
                    "A standing platform team with a product mandate and funding.",
                    "Shared services operated once: registry, secrets, observability, runners, environments.",
                    "An agreed control mapping that every service on the path inherits.",
                    "Consistent measurement across value streams, reported like any other operational indicator.",
                ]),
            ],
            "notes": "This slide answers the question that determines whether the course changes anything: what can I actually do, given my position? The three tiers are deliberate. Almost everyone in the room can do everything in the first column alone, this month, without asking permission - and the baseline in particular costs nothing and changes every later conversation. The second column needs a small coalition and produces the artefact that unlocks the third: a working, evidenced, low-risk implementation that assurance colleagues can inspect. The third column needs leadership backing, and the way to get it is not a proposal document but the evidence produced by the second column plus the measurements from the first. Say that sequence explicitly, because the common failure is to start at the third tier with a strategy paper, which stalls, rather than at the first tier with a measurement, which compounds."
        },
    ],

    "Continuing the Journey": [
        {
            "type": "detail",
            "title": "In Context: Building Depth Where This Institution Needs It",
            "sections": [
                ("Skills this environment will reward most", [
                    "Reliability engineering: SLOs for time-bound obligations, error budgets, incident practice.",
                    "Policy as code and automated evidence - the intersection of engineering and assurance is scarce and valuable.",
                    "Data-aware delivery: masked test data, classification, retention, and pipelines that respect them.",
                    "Resilience engineering: rehearsed recovery, failover, and capacity for known peaks.",
                ]),
                ("Learn together, not alone", [
                    "Start an internal community of practice - a monthly hour to share what worked and what did not.",
                    "Publish internally: a short write-up of your first pipeline is worth more to colleagues than any external blog.",
                    "Pair across departments; the second team to try something goes far faster than the first.",
                    "Bring risk, security and audit colleagues into the community - shared understanding beats negotiation.",
                ]),
                ("External anchors worth the time", [
                    "The DORA State of DevOps reports for evidence that keeps updating.",
                    "The Google SRE books for SLOs, error budgets and incident practice - free online.",
                    "Team Topologies for org design, and platformengineering.org for the platform conversation.",
                    "Vendor-neutral standards: OpenTelemetry, OCI, SLSA - they outlast individual products.",
                ]),
            ],
            "notes": "Point participants at the skills this specific environment rewards, which are not always the ones that get the most attention online: reliability engineering for time-bound obligations, policy as code and automated evidence, data-aware delivery, and rehearsed recovery. The intersection of engineering and assurance is genuinely scarce and is where someone in this institution can become disproportionately valuable. The community-of-practice advice is the highest-leverage item on the slide, because a single trained person usually reverts to the surrounding norms while a small group changes them - and explicitly including risk, security and audit colleagues in that community turns the most common source of friction into shared context. On external material, steer toward the evidence base and the vendor-neutral standards, since those retain their value as products come and go."
        },
    ],

    "Your First Week Back at Work": [
        {
            "type": "diagram",
            "title": "Your First 90 Days",
            "image": "46-first-90-days",
            "caption": "Baseline, automate one thing, gate one pipeline, publish one review, then start the platform conversation.",
            "notes": "Close the course on this. The sequence is deliberate and the reasoning is in the green band: the baseline costs nothing and permanently improves every later argument, one finished automation earns the mandate for the next while one abandoned initiative costs three, and the gate plus the published review demonstrate the practices rather than describing them. Ask each participant to pick the ONE item they will start in week one and say it out loud - spoken commitments are kept far more often than intended ones, and hearing colleagues commit makes the next person more likely to follow through. Then hand out the feedback survey and close."
        },
        {
            "type": "detail",
            "title": "In Context: Your First Week at SARB, Concretely",
            "sections": [
                ("Day one back - things you can do without asking anyone", [
                    "Count deployments and measure lead time for one service over the last month, from the repository history.",
                    "List every wait in your team's last significant change, and mark the longest one.",
                    "Check one pipeline: is any scanner running with exit code 0 and being described as a control?",
                    "Check one repository: are third-party pipeline actions pinned, and are token permissions declared?",
                ]),
                ("The first conversation to have", [
                    "With your team: agree the ONE improvement for this month and who owns it.",
                    "With your manager: present the baseline, not an opinion - numbers change the tone immediately.",
                    "With risk, security and audit: ask what evidence they currently receive by hand that a pipeline could produce.",
                    "That last question is often where the whole programme starts, because the answer is usually 'most of it'.",
                ]),
                ("Then keep it going", [
                    "Re-run the capstone unaided within two weeks - the second repetition is what makes the skill durable.",
                    "Write the gap list from the workshops into a short internal note and share it.",
                    "Find the second person in another department doing the same thing, and compare notes monthly.",
                    "Revisit your baseline in 90 days. The trend is the story you will tell to get the next thing funded.",
                ]),
            ],
            "notes": "End with something each participant can do on Monday morning without anyone's permission, because the gap between training and practice is almost always the first step rather than the ambition. The four checks in the first section take under an hour combined and each one typically produces an actionable finding - the exit-code-zero scanner in particular is present in a surprising number of pipelines that are described as gated. The question to ask assurance colleagues is the most strategically useful sentence in the whole closing module: asking what evidence they currently assemble by hand that a pipeline could produce automatically reframes the relationship from negotiation to collaboration, and the answer usually reveals a large amount of manual work that everyone would be glad to eliminate. Close by asking for the spoken commitment, thanking the room, and reminding them that the entire package is theirs to keep and rerun."
        },
    ],
}


def _merge_expansions(*sources: dict) -> dict:
    """Combine expansion dicts keyed on summary-slide title, preserving order."""
    merged: dict = {}
    for source in sources:
        for title, slides in source.items():
            merged.setdefault(title, []).extend(slides)
    return merged


def main() -> None:
    build_deck(
        "DevOps & Platform Engineering",
        "Day 1 — Foundations, Culture, Tools, IaC & CI/CD",
        DAY1_MODULES,
        "DevOps-PlatformEngineering-Day1.pptx",
        deep_dives=_merge_expansions(DAY1_DEEP_DIVES, DAY1_CONTEXT),
    )
    build_deck(
        "DevOps & Platform Engineering",
        "Day 2 — Containers, Security, Observability, Platform Thinking & Workshops",
        DAY2_MODULES,
        "DevOps-PlatformEngineering-Day2.pptx",
        deep_dives=_merge_expansions(DAY2_DEEP_DIVES, DAY2_CONTEXT),
    )


if __name__ == "__main__":
    main()
