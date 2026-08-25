"""ReportLab PDF generation with LLM-output sanitization."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# Text sanitization
# ---------------------------------------------------------------------------

_REPLACEMENTS = {
    "humanninnthenloop": "human-in-the-loop",
    "vitalnsignnbased": "vital-sign-based",
    "AIndriven": "AI-driven",
    "expertnlevel": "expert-level",
    "nonnrepresentative": "non-representative",
    "renidentification": "re-identification",
    "leadnidentification": "lead-identification",
    "multinomics": "multi-omics",
    "diseasenrelevant": "disease-relevant",
    "virtualnscreening": "virtual-screening",
    "realntime": "real-time",
    "earlynwarning": "early-warning",
    "30nday": "30-day",
    "literaturenbased": "literature-based",
    "postnmarket": "post-market",
    "usernfriendly": "user-friendly",
    "blacknbox": "black-box",
    "spectrumnbias": "spectrum-bias",
    "timenlines": "timelines",
    "Qwen330BIA3B": "Qwen3-30B-A3B",
    "GPTIOSS": "GPT-OSS",
}


def sanitize_text_for_pdf(text: str) -> str:
    """Fix common LLM encoding artifacts before PDF rendering."""
    if not text:
        return ""
    for bad, good in _REPLACEMENTS.items():
        text = text.replace(bad, good)

    text = re.sub(r"=(?=\d)", "= ", text)                       # =0.78  -> = 0.78
    text = re.sub(r"(?<=\d)\s*vs\.\s*(?=\d)", " vs. ", text)     # 0.7vs.0.5
    text = re.sub(r",[a-zA-Z]", lambda m: m.group(0)[0] + " " + m.group(0)[1], text)
    text = re.sub(r"[国〡]", "", text)                            # CJK artifacts
    text = text.replace("≈", "~").replace("≃", "~").replace("∼", "~")
    for invisible in ("\u200b", "\ufeff", "\u200c", "\u200d"):
        text = text.replace(invisible, "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n", "\n\n", text)
    return text.strip()


def clean_markdown_for_pdf(text: str) -> str:
    """Sanitize plus normalize markdown emphasis spacing."""
    text = sanitize_text_for_pdf(text)
    text = re.sub(r"\*\*\s+", "**", text)
    text = re.sub(r"\s+\*\*", "**", text)
    return text


def _inline(text: str) -> str:
    """Convert inline markdown to ReportLab markup."""
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    text = re.sub(r"`([^`]+)`", r"<font face='Courier'>\1</font>", text)
    return text


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

PRIMARY = colors.HexColor("#1a365d")
SECONDARY = colors.HexColor("#2c5282")
ACCENT = colors.HexColor("#3182ce")
LIGHT_BG = colors.HexColor("#ebf8ff")
DARK_TEXT = colors.HexColor("#1a202c")
GRAY_TEXT = colors.HexColor("#4a5568")
GRID = colors.HexColor("#e2e8f0")


def get_styles():
    styles = getSampleStyleSheet()

    def add(name: str, **kwargs):
        if name in styles:
            for key, value in kwargs.items():
                setattr(styles[name], key, value)
        else:
            styles.add(ParagraphStyle(name=name, **kwargs))

    add("CoverTitle", fontSize=36, leading=44, textColor=PRIMARY, alignment=TA_CENTER,
        spaceAfter=30, fontName="Helvetica-Bold")
    add("CoverSubtitle", fontSize=18, leading=24, textColor=SECONDARY, alignment=TA_CENTER,
        spaceAfter=20)
    add("CoverMeta", fontSize=12, leading=16, textColor=GRAY_TEXT, alignment=TA_CENTER, spaceAfter=12)
    add("ReportTitle", fontSize=28, leading=34, textColor=PRIMARY, spaceAfter=24,
        fontName="Helvetica-Bold", borderPadding=10)
    add("SectionHeader", fontSize=20, leading=26, textColor=SECONDARY, spaceAfter=16,
        spaceBefore=20, fontName="Helvetica-Bold", borderColor=ACCENT, borderWidth=2, borderPadding=5)
    add("SubSectionHeader", fontSize=16, leading=22, textColor=ACCENT, spaceAfter=12,
        spaceBefore=14, fontName="Helvetica-Bold")
    add("BodyTextX", fontSize=11, leading=16, textColor=DARK_TEXT, alignment=TA_JUSTIFY,
        spaceAfter=10, fontName="Helvetica", firstLineIndent=20)
    add("BulletPoint", fontSize=11, leading=16, textColor=DARK_TEXT, leftIndent=30, spaceAfter=6,
        bulletIndent=15, bulletFontName="Helvetica-Bold", bulletColor=ACCENT)
    add("QuoteStyleX", fontSize=10, leading=15, textColor=GRAY_TEXT, leftIndent=40, rightIndent=40,
        spaceAfter=12, fontName="Helvetica-Oblique", borderColor=LIGHT_BG, borderWidth=1,
        borderPadding=10, backColor=LIGHT_BG)
    add("TableHeader", fontSize=10, leading=14, textColor=colors.white, alignment=TA_CENTER,
        fontName="Helvetica-Bold")
    add("TableCell", fontSize=9, leading=13, textColor=DARK_TEXT, alignment=TA_CENTER)
    add("KeyInsight", fontSize=12, leading=18, textColor=PRIMARY, fontName="Helvetica-Bold",
        borderColor=ACCENT, borderWidth=3, borderPadding=15, backColor=LIGHT_BG,
        spaceAfter=20, spaceBefore=10)
    return styles


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------

def create_bar_chart(data: list[float], labels: list[str], title: str = "") -> Drawing:
    drawing = Drawing(500, 250)
    chart = VerticalBarChart()
    chart.x, chart.y = 60, 60
    chart.height, chart.width = 150, 400
    chart.data = [data]
    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.fontSize = 10
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(data) * 1.2 if data and max(data) > 0 else 100
    chart.valueAxis.labels.fontSize = 9
    chart.bars[0].fillColor = ACCENT
    chart.bars[0].strokeColor = SECONDARY
    drawing.add(chart)
    if title:
        drawing.add(String(250, 230, title, fontSize=12, fillColor=PRIMARY,
                           textAnchor="middle", fontName="Helvetica-Bold"))
    return drawing


def create_stat_card(label: str, value: str) -> Table:
    styles = get_styles()
    data = [
        [Paragraph(f"<b>{value}</b>",
                   ParagraphStyle(name="StatValue", fontSize=24, textColor=PRIMARY,
                                  alignment=TA_CENTER, fontName="Helvetica-Bold"))],
        [Paragraph(label, ParagraphStyle(name="StatLabel", fontSize=10, textColor=GRAY_TEXT,
                                         alignment=TA_CENTER))],
    ]
    table = Table(data, colWidths=[130])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7fafc")),
        ("BOX", (0, 0), (-1, -1), 1, GRID),
        ("TOPPADDING", (0, 0), (-1, -1), 15),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
    ]))
    return table


def create_table(data: list[list[str]], header: list[str] | None = None,
                 col_widths: list[int] | None = None) -> Table:
    styles = get_styles()
    table_data: list[list[Paragraph]] = []
    if header:
        table_data.append([Paragraph(h, styles["TableHeader"]) for h in header])
    for row in data:
        table_data.append([Paragraph(str(cell), styles["TableCell"]) for cell in row])

    if not col_widths and table_data:
        num_cols = len(table_data[0])
        col_widths = [450 // num_cols] * num_cols

    table = Table(table_data, colWidths=col_widths, repeatRows=1 if header else 0)
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, GRID),
        ("BACKGROUND", (0, 0), (-1, 0), SECONDARY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def parse_markdown_table(lines: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in lines:
        if re.match(r"^\s*\|?[\-:|\s]+\|?\s*$", line):
            continue
        cells = [cell.strip() for cell in line.split("|") if cell.strip()]
        if cells:
            rows.append(cells)
    return rows


class _PageNumCanvas(pdfcanvas.Canvas):
    def __init__(self, *args, **kwargs):
        self._report_title = kwargs.pop("report_title", "AI Research Report")
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict] = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_decorations(total)
            super().showPage()
        super().save()

    def _draw_decorations(self, total: int):
        self.setStrokeColor(GRID)
        self.line(50, 40, 545, 40)
        self.setFillColor(GRAY_TEXT)
        self.setFont("Helvetica", 9)
        self.drawRightString(545, 25, f"Page {self._pageNumber} of {total}")
        self.setFont("Helvetica-Oblique", 8)
        self.drawString(50, 25, self._report_title[:90])
        self.setFillColor(SECONDARY)
        self.setFont("Helvetica-Bold", 10)
        self.drawString(50, 800, "AI Research Report")
        self.drawRightString(545, 800, datetime.now().strftime("%B %d, %Y"))
        self.line(50, 795, 545, 795)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_pdf(
    text: str,
    output_path: str | Path,
    *,
    topic: str = "",
    stats: dict[str, Any] | None = None,
    pages_data: list[dict[str, Any]] | None = None,
) -> Path:
    """Render sanitized markdown into a styled multi-page PDF."""
    text = clean_markdown_for_pdf(text)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        rightMargin=50, leftMargin=50, topMargin=80, bottomMargin=60,
    )
    styles = get_styles()
    story: list = []

    # Cover page
    story.append(Spacer(1, 100))
    story.append(Paragraph(sanitize_text_for_pdf("AI Research Report"), styles["CoverTitle"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Topic: {topic}", styles["CoverSubtitle"]))
    story.append(Spacer(1, 40))
    story.append(Paragraph(
        f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %H:%M')}<br/>"
        "<b>System:</b> Autonomous Research Platform",
        styles["CoverMeta"],
    ))
    story.append(Spacer(1, 60))

    if stats:
        story.append(Paragraph("Document Overview", styles["SubSectionHeader"]))
        story.append(Table([[
            create_stat_card("Total Pages", str(stats.get("total_pages", 0))),
            create_stat_card("Data Chunks", str(stats.get("total_chunks", 0))),
            create_stat_card("Recent Sources", str(stats.get("recent_pages", 0))),
        ]]))
        story.append(PageBreak())

    # Executive summary highlight
    lines = text.split("\n")
    i = 0
    summary_lines: list[str] = []
    while i < len(lines) and not lines[i].strip().startswith("#"):
        if lines[i].strip():
            summary_lines.append(lines[i].strip())
        i += 1
    story.append(Paragraph("Executive Summary", styles["SectionHeader"]))
    if summary_lines:
        story.append(Paragraph("<b>Key Finding:</b> " + " ".join(summary_lines[:3]), styles["KeyInsight"]))
    story.append(Spacer(1, 20))

    # Dashboard + sources
    if stats:
        story.append(Paragraph("Data Overview", styles["SectionHeader"]))
        story.append(Spacer(1, 15))
        story.append(create_bar_chart(
            [stats.get("total_pages", 0), stats.get("total_chunks", 0),
             stats.get("recent_pages", 0)],
            ["Pages", "Chunks", "Recent"], "Database Statistics"))
        story.append(Spacer(1, 30))
        if pages_data:
            story.append(Paragraph("Source Pages", styles["SubSectionHeader"]))
            rows = [[p.get("title", "")[:40], p.get("url", "")[:50]] for p in pages_data[:10]]
            story.append(create_table(rows, header=["Title", "URL"], col_widths=[180, 270]))
        story.append(PageBreak())

    # Main markdown body
    section: list = []
    while i < len(lines):
        raw = sanitize_text_for_pdf(lines[i])
        stripped = raw.strip()

        if stripped.startswith("# ") or stripped.startswith("## ") or stripped.startswith("### "):
            if stripped.startswith("### "):
                section.append(Paragraph(_inline(stripped[4:]), styles["SubSectionHeader"]))
            elif stripped.startswith("## "):
                section.append(Paragraph(stripped[3:], styles["SectionHeader"]))
            else:
                section.append(Paragraph(stripped[2:], styles["ReportTitle"]))
            section.append(Spacer(1, 8))
        elif stripped.startswith("- ") or stripped.startswith("* "):
            section.append(Paragraph("\u2022 " + _inline(stripped[2:]), styles["BulletPoint"]))
        elif re.match(r"^\d+\.\s", stripped):
            section.append(Paragraph(_inline(re.sub(r"^\d+\.\s", "", stripped)), styles["BulletPoint"]))
        elif "|" in stripped and stripped:
            table_lines = []
            while i < len(lines) and "|" in lines[i]:
                table_lines.append(lines[i])
                i += 1
            i -= 1
            rows = parse_markdown_table(table_lines)
            if rows:
                header, body = rows[0], rows[1:] if len(rows) > 1 else []
                section.append(create_table(body or [[""]], header=header))
                section.append(Spacer(1, 12))
        elif stripped.startswith("> "):
            section.append(Paragraph(_inline(stripped[2:]), styles["QuoteStyleX"]))
        elif stripped in ("---", "***"):
            section.append(HRFlowable(width="100%", thickness=1, color=GRID))
            section.append(Spacer(1, 10))
        elif stripped:
            section.append(Paragraph(_inline(stripped), styles["BodyTextX"]))
        i += 1

    story.extend(section)

    # Appendix
    story.append(PageBreak())
    story.append(Paragraph("Appendix", styles["SectionHeader"]))
    story.append(Spacer(1, 15))
    story.append(Paragraph(
        f"<b>Document Information</b><br/>"
        f"This report was generated automatically by the Autonomous Research Platform.<br/>"
        f"Generation timestamp: {datetime.now().isoformat()}<br/><br/>"
        f"<b>Methodology</b><br/>"
        "Content is synthesized from verified research database entries using "
        "retrieval-augmented generation techniques with content-hash deduplication.<br/><br/>"
        f"<b>Disclaimer</b><br/>"
        "This document is for research purposes only. Verify critical information "
        "against primary sources before making decisions.",
        styles["BodyTextX"],
    ))

    doc.build(
        story,
        canvasmaker=lambda *args, **kwargs: _PageNumCanvas(*args, report_title=topic, **kwargs),
    )
    return output_path
