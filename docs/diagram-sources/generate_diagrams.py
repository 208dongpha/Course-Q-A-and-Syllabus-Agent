#!/usr/bin/env python3
"""Generate plain technical SVG diagrams for the overview README.

The rendering is intentionally simple: white background, dark strokes and text,
rectangular nodes, compact labels and no decorative color system. PNG files are
rendered from the SVG by a browser at 2x; the 900 px previews are for checking
GitHub README readability.

The script uses only the Python standard library. It works both in the external
draft layout (overview-redesign/diagram-sources) and in the published layout
(docs/diagram-sources).
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
OUT = HERE.parent if HERE.parent.name == "docs" else HERE.parent / "docs"
OUT.mkdir(parents=True, exist_ok=True)

INK = "#111827"
MUTED = "#374151"
STROKE = "#111827"
ARROW = "#111827"
DASH = "#6b7280"
WHITE = "#ffffff"
FONT = "Helvetica, Arial, sans-serif"


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
            '<marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" '
            'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="' + ARROW + '"/></marker>',
            '<marker id="arrow-dash" markerWidth="10" markerHeight="10" refX="8" refY="5" '
            'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="' + DASH + '"/></marker>',
            "</defs>",
            f'<rect width="{width}" height="{height}" fill="{WHITE}"/>',
        ]

    def add(self, part: str) -> None:
        self.parts.append(part)

    def header(self, title: str, subtitle: str) -> None:
        self.add(
            f'<text x="30" y="34" font-family="{FONT}" font-size="24" font-weight="700" '
            f'fill="{INK}">{esc(title)}</text>'
        )
        self.add(
            f'<text x="30" y="54" font-family="{FONT}" font-size="13" fill="{MUTED}">{esc(subtitle)}</text>'
        )

    def box(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        title: str,
        body: str | list[str] = "",
        *,
        title_size: int = 18,
        body_size: float = 16.5,
    ) -> None:
        pad = 12
        title_lines = wrap(title, max(8, int((w - 2 * pad) / (title_size * 0.55))))
        body_items = [body] if isinstance(body, str) else body
        body_lines: list[str] = []
        body_width = max(10, int((w - 2 * pad) / (body_size * 0.52)))
        for item in body_items:
            body_lines.extend(wrap(item, body_width))

        title_y = y + 29
        body_y = title_y + len(title_lines) * (title_size + 3) + 4
        needed = 16 + len(title_lines) * (title_size + 3) + 4 + len(body_lines) * (body_size + 4) + 10
        if needed > h:
            raise ValueError(f"box too short for {title!r}: needs {needed}px, got {h}px")

        self.add(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{WHITE}" '
            f'stroke="{STROKE}" stroke-width="1.4"/>'
        )
        for i, line in enumerate(title_lines):
            self.add(
                f'<text x="{x + pad}" y="{title_y + i * (title_size + 3)}" '
                f'font-family="{FONT}" font-size="{title_size}" font-weight="700" '
                f'fill="{INK}">{esc(line)}</text>'
            )
        for i, line in enumerate(body_lines):
            self.add(
                f'<text x="{x + pad}" y="{body_y + i * (body_size + 4)}" '
                f'font-family="{FONT}" font-size="{body_size}" fill="{MUTED}">{esc(line)}</text>'
            )

    def diamond(self, cx: int, cy: int, w: int, h: int, text: str) -> None:
        lines = wrap(text, max(8, int((w * 0.70) / 9.3)))
        line_h = 18
        needed_h = len(lines) * line_h + 18
        if needed_h > h:
            raise ValueError(f"diamond too short for {text!r}: needs {needed_h}px, got {h}px")
        points = f"{cx},{cy - h // 2} {cx + w // 2},{cy} {cx},{cy + h // 2} {cx - w // 2},{cy}"
        self.add(
            f'<polygon points="{points}" fill="{WHITE}" stroke="{STROKE}" stroke-width="1.4"/>'
        )
        start = cy - (len(lines) - 1) * line_h / 2
        for i, line in enumerate(lines):
            self.add(
                f'<text x="{cx}" y="{start + i * line_h + 5}" text-anchor="middle" '
                f'font-family="{FONT}" font-size="16" fill="{INK}">{esc(line)}</text>'
            )

    def label(self, x: float, y: float, text: str, *, size: float = 11.5) -> None:
        width = max(22, len(text) * size * 0.53 + 8)
        self.add(
            f'<rect x="{x - width / 2}" y="{y - 11}" width="{width}" height="16" fill="{WHITE}"/>'
        )
        self.add(
            f'<text x="{x}" y="{y + 1}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" fill="{MUTED}">{esc(text)}</text>'
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
        dash = 'stroke-dasharray="6 4"' if dashed else ""
        self.add(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="1.4" marker-end="url(#{marker})" {dash}/>'
        )
        if label:
            self.label(
                label_x if label_x is not None else (x1 + x2) / 2,
                label_y if label_y is not None else (y1 + y2) / 2 - 5,
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
        dash = 'stroke-dasharray="6 4"' if dashed else ""
        d = f"M {points[0][0]},{points[0][1]} " + " ".join(f"L {x},{y}" for x, y in points[1:])
        self.add(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.4" '
            f'marker-end="url(#{marker})" {dash}/>'
        )
        if label:
            self.label(
                label_x if label_x is not None else points[-1][0],
                label_y if label_y is not None else points[-1][1] - 7,
                label,
            )

    def boundary(self, x: int, y: int, w: int, h: int, label: str) -> None:
        self.add(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" '
            f'stroke="{DASH}" stroke-width="1.2" stroke-dasharray="5 4"/>'
        )
        self.add(
            f'<text x="{x + 10}" y="{y + 18}" font-family="{FONT}" font-size="13" '
            f'font-weight="700" fill="{MUTED}">{esc(label)}</text>'
        )

    def section(self, x: int, y: int, text: str) -> None:
        self.add(
            f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="14" font-weight="700" '
            f'fill="{INK}">{esc(text)}</text>'
        )

    def note(self, x: int, y: int, text: str, *, width: int) -> None:
        lines = wrap(text, max(20, int(width / 7.0)))
        for i, line in enumerate(lines):
            self.add(
                f'<text x="{x}" y="{y + i * 18}" font-family="{FONT}" font-size="12.5" '
                f'fill="{MUTED}">{esc(line)}</text>'
            )

    def finish(self, path: Path) -> None:
        self.parts.append("</svg>")
        path.write_text("\n".join(self.parts), encoding="utf-8")


def build_overall() -> None:
    s = SVG(1100, 820)
    s.header("Course Q&A and Syllabus Agent", "Overall workflow: class setup, cited answers and optional improvement")

    s.section(30, 84, "Class setup")
    s.section(30, 304, "Ask and learn")
    s.section(30, 524, "Follow up and improve")

    row1 = [
        (30, "Admin: provision accounts/class", "users, roles, trainer"),
        (290, "Trainer: upload & approve", "materials, syllabus"),
        (550, "Platform: prepare evidence", "parse, chunk, embed, index"),
        (810, "Class knowledge base", "PostgreSQL + Qdrant"),
    ]
    for x, title, body in row1:
        s.box(x, 100, 245, 115, title, body)
    for x in (275, 535, 795):
        s.arrow(x + 2, 157, x + 17, 157)

    row2 = [
        (30, "Student: join & ask", "class-scoped question"),
        (290, "Platform: auth, quota, scope", "membership, limit, gate"),
        (550, "Platform: retrieve, rerank, route", "class, optional web, no evidence"),
        (810, "Student: receive cited answer", "history + feedback"),
    ]
    for x, title, body in row2:
        s.box(x, 315, 245, 115, title, body)
    for x in (275, 535, 795):
        s.arrow(x + 2, 372, x + 17, 372)

    row3 = [
        (30, 210, "Student: optional ticket", "after confirmation"),
        (300, 210, "Trainer: reply", "answer + resolve"),
        (570, 230, "Trainer: review/update", "optional/manual"),
        (860, 195, "Platform: re-index", "only after update"),
    ]
    for x, w, title, body in row3:
        s.box(x, 535, w, 115, title, body)
    s.arrow(240, 592, 300, 592)
    s.arrow(510, 592, 570, 592, dashed=True, label="optional", label_x=540, label_y=580)
    s.arrow(800, 592, 860, 592, dashed=True, label="if changed", label_x=830, label_y=580)

    # Knowledge base -> retrieval
    s.path_arrow(
        [(932, 215), (932, 285), (672, 285), (672, 315)],
        label="class evidence",
        label_x=800,
        label_y=275,
    )
    # Answer -> optional ticket, routed around the section label.
    s.path_arrow(
        [(932, 430), (932, 505), (18, 505), (18, 592), (30, 592)],
        dashed=True,
        label="optional",
        label_x=650,
        label_y=493,
    )
    # Optional/manual improvement loop.
    s.path_arrow(
        [(955, 535), (955, 505), (1070, 505), (1070, 157), (1055, 157)],
        dashed=True,
        label="re-index",
        label_x=1015,
        label_y=493,
    )

    s.note(
        30,
        730,
        "Solid edges are primary flow; dashed edges are optional/manual. Web search is conditional and not used for every question.",
        width=1040,
    )
    s.finish(OUT / "overall-workflow.svg")


def build_architecture() -> None:
    s = SVG(1100, 800)
    s.header("System architecture", "Two implementation repositories, one class-scoped application")

    s.add(f'<text x="25" y="92" font-family="{FONT}" font-size="13" font-weight="700" fill="{MUTED}">People</text>')
    s.boundary(235, 90, 260, 600, "Frontend (Next.js)")
    s.boundary(535, 90, 290, 600, "Backend (FastAPI)")
    s.add(f'<text x="855" y="92" font-family="{FONT}" font-size="13" font-weight="700" fill="{MUTED}">Data / external</text>')

    actors = [
        ("Student", "browser session", 115),
        ("Trainer", "class workspace", 235),
        ("Teaching assistant", "where permitted", 355),
        ("Admin", "platform settings", 475),
    ]
    for title, body, y in actors:
        s.box(35, y, 155, 105, title, body, title_size=17, body_size=15.5)

    fe_boxes = [
        ("App Router pages", "role-based workspaces", 130),
        ("Route middleware + auth guard", "role cookie + session", 255),
        ("Feature modules", "chat, materials, tickets, quizzes", 380),
        ("API clients", "REST/SSE, Bearer JWT", 505),
    ]
    for title, body, y in fe_boxes:
        s.box(250, y, 230, 110, title, body, title_size=17, body_size=15.5)

    be_boxes = [
        ("API routers", "auth, chat, documents, quizzes, tickets, admin", 130),
        ("Auth, RBAC & class scope", "JWT, membership, role checks", 255),
        ("RAG + ingestion + tickets + quizzes", "service layer", 380),
        ("Admin settings & system health", "keys, thresholds, email, probes", 505),
    ]
    for title, body, y in be_boxes:
        s.box(550, y, 260, 110, title, body, title_size=17, body_size=15.5)

    ext_boxes = [
        ("PostgreSQL", "relational data", 130),
        ("Qdrant", "vector index", 220),
        ("Gemini", "AI model calls", 310),
        ("SerpApi", "optional web", 400),
        ("SMTP", "optional email", 490),
    ]
    for title, body, y in ext_boxes:
        s.box(870, y, 200, 78, title, body, title_size=16, body_size=14.5)

    s.arrow(190, 320, 235, 320, label="browser", label_x=212, label_y=308)
    s.arrow(495, 320, 535, 320, label="HTTP/SSE", label_x=515, label_y=308)

    s.add(f'<line x1="825" y1="320" x2="845" y2="320" stroke="{ARROW}" stroke-width="1.4"/>')
    s.add(f'<line x1="845" y1="169" x2="845" y2="529" stroke="{ARROW}" stroke-width="1.4"/>')
    for y in (169, 259, 349, 439, 529):
        s.arrow(845, y, 870, y)

    s.note(
        30,
        730,
        "SerpApi and SMTP are optional. Web search is conditional and is not used for every question.",
        width=1040,
    )
    s.finish(OUT / "architecture.svg")


def build_rag() -> None:
    s = SVG(1000, 1450)
    s.header(
        "Question answering and optional web search",
        "Main RAG route; quick replies and code-help shortcuts are omitted",
    )

    s.box(30, 80, 550, 75, "Student asks a class-scoped question", "question + class_id")
    s.arrow(305, 155, 305, 170)
    s.box(30, 170, 550, 75, "Authenticate, verify class, check quota", "401 / 403 / 429 stop")
    s.arrow(305, 245, 305, 260)
    s.box(30, 260, 550, 80, "Scope gate + follow-up rewrite", "parallel; fail-open; rewrite fallback")
    s.arrow(305, 340, 305, 345)
    s.diamond(305, 390, 240, 90, "Out of scope?")
    s.box(610, 355, 360, 75, "Refuse out-of-scope", "no retrieval")
    s.arrow(425, 390, 610, 390, label="Out of scope", label_x=518, label_y=378)
    s.arrow(305, 435, 305, 470, label="Continue", label_x=326, label_y=455)

    s.box(30, 470, 550, 75, "Class-filtered retrieval", "class_id; live documents")
    s.arrow(305, 545, 305, 555)
    s.diamond(305, 600, 260, 90, "Low / empty score?")
    s.arrow(305, 645, 305, 690, label="Continue", label_x=326, label_y=665)
    s.box(30, 690, 550, 75, "Cross-Encoder rerank", "top K class passages")
    s.arrow(305, 765, 305, 790)
    s.box(30, 790, 550, 75, "Routing policy", "score + scope + syllabus")

    # Low/empty evidence bypasses the reranker and still reaches routing.
    s.path_arrow(
        [(435, 600), (590, 600), (590, 827), (580, 827)],
        label="Low / empty",
        label_x=590,
        label_y=660,
    )

    outcomes = [
        (610, 880, 360, 75, "Class answer", "strong score or roadmap"),
        (610, 970, 360, 95, "Class + optional web", "partial; class fallback if web empty"),
        (610, 1080, 360, 80, "Web search (conditional)", "only if provider configured"),
        (610, 1180, 360, 75, "No evidence", "explicit response"),
    ]
    for x, y, w, h, title, body in outcomes:
        s.box(x, y, w, h, title, body, title_size=17, body_size=15.5)

    s.arrow(580, 810, 610, 917, label="strong", label_x=595, label_y=900)
    s.arrow(580, 825, 610, 1017, label="partial", label_x=595, label_y=1000)
    s.arrow(580, 840, 610, 1120, label="low", label_x=595, label_y=1103)
    s.arrow(790, 1160, 790, 1180, label="no provider/results", label_x=790, label_y=1170)

    # Only class/web source outcomes feed generation.
    s.add(f'<line x1="970" y1="917" x2="985" y2="917" stroke="{ARROW}" stroke-width="1.4"/>')
    s.add(f'<line x1="970" y1="1017" x2="985" y2="1017" stroke="{ARROW}" stroke-width="1.4"/>')
    s.add(f'<line x1="970" y1="1120" x2="985" y2="1120" stroke="{ARROW}" stroke-width="1.4"/>')
    s.add(f'<line x1="985" y1="917" x2="985" y2="1315" stroke="{ARROW}" stroke-width="1.4"/>')
    s.arrow(985, 1315, 960, 1315)

    s.box(30, 1280, 930, 75, "Generate grounded answer and stream it", "citations, suggestions, history, feedback")

    s.note(
        30,
        1390,
        "Low or empty class evidence continues through routing; web search is conditional and no-evidence is an explicit response.",
        width=940,
    )
    s.finish(OUT / "rag-and-web-workflow.svg")


if __name__ == "__main__":
    build_overall()
    build_architecture()
    build_rag()
    print("Wrote:", ", ".join(str(p.relative_to(OUT)) for p in OUT.glob("*.svg")))
