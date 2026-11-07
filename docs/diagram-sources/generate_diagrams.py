#!/usr/bin/env python3
"""Generate the overview README diagrams as deterministic SVG.

The SVG is authored here with the Python standard library; PNG files are
rendered separately from the SVG by a browser at 2x scale. The diagrams are
sized for a GitHub README content width of roughly 900 CSS pixels: the SVGs are
1200-1300 px wide and use 20-24 px body text, so they remain readable when
scaled down.
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
# Works both in the external draft layout (overview-redesign/diagram-sources)
# and in the published layout (docs/diagram-sources).
OUT = HERE.parent if HERE.parent.name == "docs" else HERE.parent / "docs"
OUT.mkdir(parents=True, exist_ok=True)

INK = "#0f2742"
MUTED = "#475569"
LINE = "#cbd5e1"
ARROW = "#475569"
DASH = "#94a3b8"
WHITE = "#ffffff"
PAGE = "#f8fafc"

KINDS = {
    "admin": ("#dbeafe", "#1d4ed8", "ADMIN"),
    "trainer": ("#dcfce7", "#15803d", "TRAINER"),
    "student": ("#ede9fe", "#6d28d9", "STUDENT"),
    "assistant": ("#ccfbf1", "#0d9488", "ASSISTANT"),
    "platform": ("#ffedd5", "#c2410c", "PLATFORM"),
    "frontend": ("#e0f2fe", "#0369a1", "FRONTEND"),
    "backend": ("#ffedd5", "#c2410c", "BACKEND"),
    "data": ("#ccfbf1", "#0f766e", "DATA"),
    "external": ("#fae8ff", "#a21caf", "EXTERNAL"),
    "neutral": ("#f1f5f9", "#64748b", "SYSTEM"),
}


def esc(text: str) -> str:
    return escape(text, {'"': "&quot;"})


def wrap(text: str, width: int) -> list[str]:
    if not text:
        return []
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False)


class SVG:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.parts: list[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img">',
            "<defs>",
            '<marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" '
            'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L12,6 L0,12 z" fill="' + ARROW + '"/></marker>',
            '<marker id="arrow-dash" markerWidth="12" markerHeight="12" refX="10" refY="6" '
            'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L12,6 L0,12 z" fill="' + DASH + '"/></marker>',
            "</defs>",
            f'<rect width="{width}" height="{height}" fill="{PAGE}"/>',
        ]

    def add(self, part: str) -> None:
        self.parts.append(part)

    def header(self, title: str, subtitle: str) -> None:
        self.add(
            f'<text x="40" y="52" font-family="Segoe UI, Arial, Helvetica, sans-serif" '
            f'font-size="34" font-weight="700" fill="{INK}">{esc(title)}</text>'
        )
        self.add(
            f'<text x="40" y="84" font-family="Segoe UI, Arial, Helvetica, sans-serif" '
            f'font-size="18" fill="{MUTED}">{esc(subtitle)}</text>'
        )

    def box(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        title: str,
        body: list[str] | str,
        kind: str = "neutral",
        *,
        tag: str | None = None,
        title_size: int = 22,
        body_size: int = 19,
        num: int | None = None,
        dashed: bool = False,
    ) -> None:
        fill, stroke, default_tag = KINDS[kind]
        pad = 14
        tag_text = tag or default_tag
        tag_w = max(56, int(len(tag_text) * 7.8) + 22)
        title_lines = wrap(title, max(8, int((w - 2 * pad) / (title_size * 0.55))))
        body_lines: list[str] = []
        body_items = [body] if isinstance(body, str) else body
        body_width = max(10, int((w - 2 * pad) / (body_size * 0.52)))
        for item in body_items:
            body_lines.extend(wrap(item, body_width))

        title_y = y + 52
        body_y = title_y + len(title_lines) * (title_size + 5) + 6
        needed = 14 + 23 + len(title_lines) * (title_size + 5) + 6 + len(body_lines) * (body_size + 5) + 14
        if needed > h:
            raise ValueError(
                f"box too short for {title!r}: needs {needed}px, got {h}px"
            )

        border = 'stroke-dasharray="10 7"' if dashed else ""
        self.add(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="2.5" {border}/>'
        )
        self.add(
            f'<rect x="{x + 13}" y="{y + 10}" width="{tag_w}" height="22" rx="11" '
            f'fill="{stroke}" opacity="0.13"/>'
        )
        self.add(
            f'<text x="{x + 23}" y="{y + 26}" font-family="Segoe UI, Arial, Helvetica, sans-serif" '
            f'font-size="11.5" font-weight="700" letter-spacing="0.7" fill="{stroke}">{esc(tag_text)}</text>'
        )
        for i, line in enumerate(title_lines):
            self.add(
                f'<text x="{x + pad}" y="{title_y + i * (title_size + 5)}" '
                f'font-family="Segoe UI, Arial, Helvetica, sans-serif" font-size="{title_size}" '
                f'font-weight="650" fill="{INK}">{esc(line)}</text>'
            )
        for i, line in enumerate(body_lines):
            self.add(
                f'<text x="{x + pad}" y="{body_y + i * (body_size + 5)}" '
                f'font-family="Segoe UI, Arial, Helvetica, sans-serif" font-size="{body_size}" '
                f'fill="#334155">{esc(line)}</text>'
            )
        if num is not None:
            self.add(f'<circle cx="{x + w - 25}" cy="{y + 25}" r="15" fill="{stroke}"/>')
            self.add(
                f'<text x="{x + w - 25}" y="{y + 30}" text-anchor="middle" '
                f'font-family="Segoe UI, Arial, Helvetica, sans-serif" font-size="14" '
                f'font-weight="700" fill="{WHITE}">{num}</text>'
            )

    def arrow(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        *,
        dashed: bool = False,
        label: str | None = None,
        label_x: float | None = None,
        label_y: float | None = None,
    ) -> None:
        color = DASH if dashed else ARROW
        marker = "arrow-dash" if dashed else "arrow"
        dash = 'stroke-dasharray="10 7"' if dashed else ""
        self.add(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="2.8" stroke-linecap="round" marker-end="url(#{marker})" {dash}/>'
        )
        if label:
            self.tag_label(
                label_x if label_x is not None else (x1 + x2) / 2,
                label_y if label_y is not None else (y1 + y2) / 2 - 12,
                label,
            )

    def path_arrow(
        self,
        points: list[tuple[float, float]],
        *,
        dashed: bool = False,
        label: str | None = None,
        label_x: float | None = None,
        label_y: float | None = None,
    ) -> None:
        color = DASH if dashed else ARROW
        marker = "arrow-dash" if dashed else "arrow"
        dash = 'stroke-dasharray="10 7"' if dashed else ""
        d = f"M {points[0][0]},{points[0][1]} " + " ".join(
            f"L {x},{y}" for x, y in points[1:]
        )
        self.add(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.8" '
            f'stroke-linecap="round" stroke-linejoin="round" marker-end="url(#{marker})" {dash}/>'
        )
        if label:
            self.tag_label(
                label_x if label_x is not None else points[-1][0],
                label_y if label_y is not None else points[-1][1] - 14,
                label,
            )

    def tag_label(self, x: float, y: float, text: str, *, size: int = 14) -> None:
        w = max(28, len(text) * 7.4 + 16)
        self.add(
            f'<rect x="{x - w / 2}" y="{y - 15}" width="{w}" height="24" rx="12" '
            f'fill="{WHITE}" stroke="{LINE}" stroke-width="1"/>'
        )
        self.add(
            f'<text x="{x}" y="{y + 2}" text-anchor="middle" '
            f'font-family="Segoe UI, Arial, Helvetica, sans-serif" font-size="{size}" '
            f'font-weight="600" fill="{MUTED}">{esc(text)}</text>'
        )

    def phase(self, x: int, y: int, w: int, h: int, label: str) -> None:
        self.add(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="{WHITE}" '
            f'stroke="#e2e8f0" stroke-width="1.5"/>'
        )
        self.add(
            f'<text x="{x + 20}" y="{y + 34}" font-family="Segoe UI, Arial, Helvetica, sans-serif" '
            f'font-size="22" font-weight="700" fill="{INK}">{esc(label)}</text>'
        )

    def boundary(self, x: int, y: int, w: int, h: int, label: str, color: str = "#64748b") -> None:
        self.add(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="none" '
            f'stroke="{color}" stroke-width="2" stroke-dasharray="11 8"/>'
        )
        self.add(
            f'<text x="{x + 18}" y="{y + 27}" font-family="Segoe UI, Arial, Helvetica, sans-serif" '
            f'font-size="17" font-weight="700" fill="{color}">{esc(label)}</text>'
        )

    def legend(self, x: int, y: int, items: list[tuple[str, str]]) -> None:
        cx = x
        for label, color in items:
            self.add(
                f'<rect x="{cx}" y="{y - 16}" width="20" height="20" rx="5" fill="{color}"/>'
            )
            self.add(
                f'<text x="{cx + 28}" y="{y}" font-family="Segoe UI, Arial, Helvetica, sans-serif" '
                f'font-size="17" fill="{MUTED}">{esc(label)}</text>'
            )
            cx += 30 + len(label) * 8.8 + 30

    def line_legend(self, x: int, y: int) -> None:
        self.add(
            f'<line x1="{x}" y1="{y - 6}" x2="{x + 48}" y2="{y - 6}" stroke="{ARROW}" '
            f'stroke-width="2.8" marker-end="url(#arrow)"/>'
        )
        self.add(
            f'<text x="{x + 56}" y="{y}" font-family="Segoe UI, Arial, Helvetica, sans-serif" '
            f'font-size="16" fill="{MUTED}">primary flow</text>'
        )
        self.add(
            f'<line x1="{x + 190}" y1="{y - 6}" x2="{x + 238}" y2="{y - 6}" stroke="{DASH}" '
            f'stroke-width="2.8" stroke-dasharray="9 6" marker-end="url(#arrow-dash)"/>'
        )
        self.add(
            f'<text x="{x + 246}" y="{y}" font-family="Segoe UI, Arial, Helvetica, sans-serif" '
            f'font-size="16" fill="{MUTED}">optional / manual</text>'
        )

    def note(self, x: int, y: int, text: str, *, width: int, size: int = 16) -> None:
        lines = wrap(text, max(10, int((width - 28) / (size * 0.52))))
        h = 16 + len(lines) * (size + 5)
        self.add(
            f'<rect x="{x}" y="{y}" width="{width}" height="{h}" rx="12" fill="{WHITE}" '
            f'stroke="{LINE}" stroke-width="1.2"/>'
        )
        for i, line in enumerate(lines):
            self.add(
                f'<text x="{x + 14}" y="{y + 24 + i * (size + 5)}" '
                f'font-family="Segoe UI, Arial, Helvetica, sans-serif" font-size="{size}" '
                f'fill="{MUTED}">{esc(line)}</text>'
            )

    def finish(self, path: Path) -> None:
        self.parts.append("</svg>")
        path.write_text("\n".join(self.parts), encoding="utf-8")


def build_overall() -> None:
    s = SVG(1300, 1100)
    s.header(
        "Course Q&A and Syllabus Agent",
        "From class setup to cited answers and an optional improvement loop",
    )

    s.phase(30, 110, 1240, 260, "1  SET UP & PREPARE")
    s.phase(30, 400, 1240, 270, "2  ASK & LEARN")
    s.phase(30, 700, 1240, 230, "3  FOLLOW UP & IMPROVE")

    row1 = [
        (50, 250, "Admin provisions class", ["accounts, roles, trainer"], "admin", 1),
        (330, 280, "Trainer uploads & approves", ["materials and syllabus"], "trainer", 2),
        (640, 300, "Platform prepares evidence", ["validate, parse, chunk, embed, index"], "platform", 3),
        (970, 280, "Class knowledge base", ["PostgreSQL metadata; Qdrant vectors"], "data", 4),
    ]
    for x, w, title, body, kind, num in row1:
        s.box(x, 170, w, 170, title, body, kind, num=num, title_size=24, body_size=20)
    for i in range(len(row1) - 1):
        x1 = row1[i][0] + row1[i][1]
        x2 = row1[i + 1][0]
        s.arrow(x1 + 3, 255, x2 - 3, 255)

    row2 = [
        (50, 250, "Student joins & asks", ["class-scoped question"], "student", 5),
        (330, 300, "Auth + quota + scope", ["membership, quota, scope gate"], "platform", 6),
        (660, 320, "Retrieve, rerank, route", ["class material, optional web, no evidence"], "platform", 7),
        (1010, 240, "Stream cited answer", ["history + feedback"], "student", 8),
    ]
    for x, w, title, body, kind, num in row2:
        s.box(x, 460, w, 170, title, body, kind, num=num, title_size=24, body_size=20)
    for i in range(len(row2) - 1):
        x1 = row2[i][0] + row2[i][1]
        x2 = row2[i + 1][0]
        s.arrow(x1 + 3, 545, x2 - 3, 545)

    # knowledge base -> retrieval
    s.path_arrow(
        [(1110, 340), (1110, 378), (820, 378), (820, 460)],
        dashed=True,
        label="class evidence",
        label_x=960,
        label_y=368,
    )
    # answer -> optional ticket
    s.path_arrow(
        [(1130, 630), (1130, 674), (28, 674), (28, 820), (50, 820)],
        dashed=True,
        label="optional",
        label_x=650,
        label_y=662,
    )

    row3 = [
        (50, 230, "Optional teacher ticket", ["student confirms first"], "student", 9),
        (340, 230, "Trainer replies", ["answer and resolve"], "trainer", 10),
        (630, 270, "Review gaps or update material", ["optional / manual trainer action"], "trainer", 11),
        (960, 290, "Re-index updated material", ["only after a material update"], "platform", 12),
    ]
    for x, w, title, body, kind, num in row3:
        s.box(x, 745, w, 160, title, body, kind, num=num, title_size=22, body_size=19)
    s.arrow(280, 820, 340, 820)
    s.arrow(570, 820, 630, 820, dashed=True, label="optional", label_x=600, label_y=807)
    s.arrow(900, 820, 960, 820, dashed=True, label="if updated", label_x=930, label_y=807)
    s.path_arrow(
        [(1105, 745), (1105, 690), (1285, 690), (1285, 255), (1250, 255)],
        dashed=True,
        label="re-index",
        label_x=1180,
        label_y=678,
    )

    s.legend(
        50,
        970,
        [
            ("Admin", KINDS["admin"][1]),
            ("Trainer", KINDS["trainer"][1]),
            ("Student", KINDS["student"][1]),
            ("Platform", KINDS["platform"][1]),
            ("Data", KINDS["data"][1]),
        ],
    )
    s.line_legend(50, 1005)
    s.note(
        50,
        1018,
        "Web search is optional and routing-dependent. Trainer review and material updates are optional/manual; they are not an automatic ticket pipeline.",
        width=1200,
        size=16,
    )
    s.finish(OUT / "overall-workflow.svg")


def build_architecture() -> None:
    s = SVG(1300, 1000)
    s.header(
        "System architecture",
        "Two implementation repositories, one class-scoped application",
    )

    s.boundary(30, 120, 210, 690, "PEOPLE")
    s.boundary(260, 120, 350, 690, "course-qa-agent-fe  ·  Next.js", "#0369a1")
    s.boundary(640, 120, 400, 690, "course-qa-agent-be  ·  FastAPI", "#c2410c")
    s.boundary(1070, 120, 200, 690, "DATA & EXTERNAL")

    actors = [
        ("Student", ["browser session"], "student", 170),
        ("Trainer", ["class workspace"], "trainer", 315),
        ("Teaching assistant", ["where permitted"], "assistant", 460),
        ("Admin", ["platform settings"], "admin", 605),
    ]
    for title, body, kind, y in actors:
        s.box(50, y, 170, 135, title, body, kind, title_size=21, body_size=18)

    fe_boxes = [
        ("App Router pages", ["role-based workspaces"], 170),
        ("Route middleware + auth guard", ["role cookie + client session"], 315),
        ("Feature modules", ["chat, materials, tickets, quizzes"], 460),
        ("API clients", ["REST + SSE · Bearer JWT"], 605),
    ]
    for title, body, y in fe_boxes:
        s.box(280, y, 310, 140, title, body, "frontend", title_size=22, body_size=19)

    be_boxes = [
        ("API routers", ["auth, chat, documents, quizzes,", "tickets, admin"], 170),
        ("Auth, RBAC & class scope", ["JWT · membership · role checks"], 315),
        ("RAG + ingestion + tickets + quizzes", ["service layer"], 460),
        ("Admin settings & system health", ["keys, thresholds, email, probes"], 605),
    ]
    for title, body, y in be_boxes:
        s.box(660, y, 360, 140, title, body, "backend", title_size=22, body_size=19)

    ext_boxes = [
        ("PostgreSQL", ["relational"], "data", 170),
        ("Qdrant", ["vectors"], "data", 280),
        ("Gemini", ["AI model calls"], "external", 390),
        ("SerpApi", ["optional web"], "external", 500),
        ("SMTP", ["optional email"], "external", 610),
    ]
    for title, body, kind, y in ext_boxes:
        s.box(1090, y, 160, 105, title, body, kind, title_size=19, body_size=17)

    s.arrow(240, 470, 260, 470, label="browser", label_x=250, label_y=458)
    s.arrow(610, 470, 640, 470, label="REST + SSE", label_x=625, label_y=458)

    s.add(f'<line x1="1040" y1="470" x2="1055" y2="470" stroke="{ARROW}" stroke-width="2.8"/>')
    s.add(f'<line x1="1055" y1="215" x2="1055" y2="655" stroke="{ARROW}" stroke-width="2.8"/>')
    for y in (215, 325, 435, 545, 655):
        s.arrow(1055, y, 1090, y)

    s.legend(
        50,
        875,
        [
            ("People", "#64748b"),
            ("Frontend", KINDS["frontend"][1]),
            ("Backend", KINDS["backend"][1]),
            ("Data", KINDS["data"][1]),
            ("External", KINDS["external"][1]),
        ],
    )
    s.line_legend(50, 910)
    s.note(
        50,
        923,
        "SerpApi and SMTP are optional integrations. Web search is routing-dependent and is not used for every question.",
        width=1200,
        size=16,
    )
    s.finish(OUT / "architecture.svg")


def build_rag() -> None:
    s = SVG(1200, 2000)
    s.header(
        "Question answering and optional web search",
        "The main RAG route; quick predefined replies and code-help shortcuts are omitted for readability",
    )

    main = [
        (110, 120, "Student asks a class-scoped question", ["question + class_id"], "student", 1),
        (250, 120, "Authenticate, verify class, check quota", ["401 / 403 / 429 stop here"], "platform", 2),
        (390, 120, "Scope gate + follow-up rewrite", ["parallel; gate fails open; rewrite falls back"], "platform", 3),
        (540, 120, "Class-filtered retrieval", ["Qdrant · class_id · live documents"], "platform", 4),
        (680, 120, "Low or empty vector score?", ["skip rerank; continue routing"], "platform", 5),
        (820, 120, "Cross-Encoder rerank", ["top K class passages"], "platform", 6),
        (960, 140, "Routing policy", ["scope + score + syllabus; strong/roadmap -> class", "partial -> class + web; low/empty -> web/no evidence"], "platform", 7),
    ]
    for y, h, title, body, kind, num in main:
        s.box(40, y, 620, h, title, body, kind, num=num, title_size=24, body_size=21)

    # Main vertical links.
    s.arrow(350, 230, 350, 246)
    s.arrow(350, 370, 350, 386, label="yes", label_x=368, label_y=376)
    s.arrow(350, 510, 350, 536, label="Continue", label_x=368, label_y=526)
    s.arrow(350, 660, 350, 676)
    s.arrow(350, 800, 350, 816, label="no", label_x=368, label_y=802)
    s.arrow(350, 940, 350, 956)

    # Out-of-scope branch.
    s.box(780, 390, 380, 120, "Refuse out-of-scope", ["no retrieval"], "neutral", tag="OUTCOME", title_size=22, body_size=19)
    s.arrow(660, 450, 780, 450, label="Out of scope", label_x=720, label_y=438)

    # Low/empty score skips the reranker and still goes to routing.
    s.path_arrow(
        [(660, 740), (690, 740), (690, 1020), (660, 1020)],
        label="Low / empty",
        label_x=710,
        label_y=900,
    )

    outcomes = [
        (730, 1120, 430, 120, "Class answer", ["strong score or syllabus roadmap"], "data", 8),
        (730, 1260, 430, 140, "Class + optional web", ["partial score; fall back to class if web empty"], "data", 9),
        (730, 1420, 430, 140, "Optional web search", ["web enabled + configured only", "empty result -> no evidence"], "external", 10),
        (730, 1600, 430, 120, "No evidence", ["explicit insufficient-source response"], "neutral", 11),
    ]
    for x, y, w, h, title, body, kind, num in outcomes:
        s.box(x, y, w, h, title, body, kind, num=num, title_size=22, body_size=19)

    s.arrow(660, 1000, 730, 1180, label="strong", label_x=695, label_y=1090)
    s.arrow(660, 1020, 730, 1330, label="partial", label_x=695, label_y=1240)
    s.arrow(660, 1040, 730, 1490, label="low/empty", label_x=695, label_y=1390)
    s.arrow(945, 1560, 945, 1600, label="no web / no results", label_x=945, label_y=1580)

    # Outcomes that produce sources feed the grounded answer.
    s.add(f'<line x1="1160" y1="1180" x2="1180" y2="1180" stroke="{ARROW}" stroke-width="2.8"/>')
    s.add(f'<line x1="1160" y1="1330" x2="1180" y2="1330" stroke="{ARROW}" stroke-width="2.8"/>')
    s.add(f'<line x1="1160" y1="1490" x2="1180" y2="1490" stroke="{ARROW}" stroke-width="2.8"/>')
    s.add(f'<line x1="1180" y1="1180" x2="1180" y2="1800" stroke="{ARROW}" stroke-width="2.8"/>')
    s.arrow(1180, 1800, 1160, 1800)

    s.box(40, 1740, 1120, 120, "Generate grounded answer + stream it", ["citations, suggestions, history, feedback; only numbered sources"], "external", tag="DELIVERY", title_size=24, body_size=21, num=12)

    s.legend(
        40,
        1900,
        [
            ("Student", KINDS["student"][1]),
            ("Platform", KINDS["platform"][1]),
            ("Class evidence", KINDS["data"][1]),
            ("Web / generation", KINDS["external"][1]),
            ("Outcome", "#64748b"),
        ],
    )
    s.note(
        40,
        1925,
        "Web search is optional and appears only on routes that permit it. Low or empty class evidence is not an automatic final answer; it still goes through routing.",
        width=1120,
        size=16,
    )
    s.finish(OUT / "rag-and-web-workflow.svg")


if __name__ == "__main__":
    build_overall()
    build_architecture()
    build_rag()
    print("Wrote:", ", ".join(str(p.relative_to(OUT)) for p in OUT.glob("*.svg")))
