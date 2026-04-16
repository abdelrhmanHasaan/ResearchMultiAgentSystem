# import sqlite3
# from typing import List
# from tools.LLM import call_llm

# from reportlab.platypus import (
#     SimpleDocTemplate,
#     Paragraph,
#     Spacer,
#     Table,
#     TableStyle
# )
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.pagesizes import A4


# DB_PATH = "research.db"


# # ------------------------
# # RETRIEVE DATA
# # ------------------------
# def get_chunks(limit=40):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()

#     c.execute("""
#     SELECT chunk_text FROM chunks
#     ORDER BY id DESC
#     LIMIT ?
#     """, (limit,))

#     rows = c.fetchall()
#     conn.close()

#     return [r[0] for r in rows]


# # ------------------------
# # BUILD CONTEXT
# # ------------------------
# def build_context(chunks: List[str], max_chars=15000):
#     context = ""
#     for ch in chunks:
#         if len(context) + len(ch) > max_chars:
#             break
#         context += ch + "\n\n---\n\n"
#     return context

# from Prompts import QUICK_FEWSHOT, DEEP_FEWSHOT,ACADEMIC_FEWSHOT

# PROMPTS = {
#     "quick": "Write a concise structured report using bullets.",
#     "deep": "Write a detailed structured report with tables and insights.",
#     "academic": "Write a formal academic research report."
# }

# FEWSHOTS = {
#     "quick": QUICK_FEWSHOT,
#     "deep": DEEP_FEWSHOT,
#     "academic": ACADEMIC_FEWSHOT
# }


# # ------------------------
# # PDF STYLES
# # ------------------------
# def get_styles():
#     styles = getSampleStyleSheet()

#     styles.add(ParagraphStyle(
#         name='TitleStyle',
#         fontSize=18,
#         leading=22,
#         spaceAfter=12,
#         spaceBefore=10
#     ))

#     styles.add(ParagraphStyle(
#         name='HeadingStyle',
#         fontSize=14,
#         leading=18,
#         spaceAfter=8,
#         spaceBefore=10
#     ))

#     styles.add(ParagraphStyle(
#         name='BodyStyle',
#         fontSize=11,
#         leading=14,
#         spaceAfter=6
#     ))

#     return styles


# # ------------------------
# # TABLE PARSER (from markdown)
# # ------------------------
# def parse_table(lines):
#     table_data = []

#     for line in lines:
#         if "|" in line:
#             row = [cell.strip() for cell in line.split("|") if cell.strip()]
#             if row:
#                 table_data.append(row)

#     return table_data


# # ------------------------
# # PDF GENERATOR
# # ------------------------
# def generate_pdf(text: str, filename="report.pdf"):
#     doc = SimpleDocTemplate(filename, pagesize=A4)
#     styles = get_styles()

#     story = []

#     lines = text.split("\n")
#     i = 0

#     while i < len(lines):
#         line = lines[i].strip()

#         # Title
#         if line.startswith("# "):
#             story.append(Paragraph(line[2:], styles["TitleStyle"]))

#         # Section
#         elif line.startswith("## "):
#             story.append(Paragraph(line[3:], styles["HeadingStyle"]))

#         # Bullet
#         elif line.startswith("- "):
#             story.append(Paragraph(f"• {line[2:]}", styles["BodyStyle"]))

#         # Table detection
#         elif "|" in line:
#             table_lines = []

#             while i < len(lines) and "|" in lines[i]:
#                 table_lines.append(lines[i])
#                 i += 1

#             table_data = parse_table(table_lines)

#             if table_data:
#                 table = Table(table_data)
#                 table.setStyle(TableStyle([
#                     ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
#                     ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey)
#                 ]))
#                 story.append(table)
#                 story.append(Spacer(1, 10))

#             continue

#         # Normal text
#         else:
#             if line:
#                 story.append(Paragraph(line, styles["BodyStyle"]))

#         story.append(Spacer(1, 6))
#         i += 1

#     doc.build(story)

#     return filename


# # ------------------------
# # WRITER AGENT
# # ------------------------
# class WriterAgent:
#     def run(self, topic: str, mode="deep"):
#         chunks = get_chunks()

#         if not chunks:
#             return {"error": "No data in DB"}

#         context = build_context(chunks)

#         prompt = f"""
# {FEWSHOTS[mode]}

# {PROMPTS[mode]}

# STRICT RULES:
# - Use markdown structure (#, ##)
# - Use bullet points
# - MUST include at least one table
# - Make it clean and professional

# TOPIC: {topic}

# DATA:
# {context}

# Generate the report.
# """

#         report = call_llm(prompt, mode="long")

#         pdf_file = generate_pdf(report, filename=f"{mode}_report.pdf")

#         return {
#             "topic": topic,
#             "mode": mode,
#             "report": report,
#             "pdf": pdf_file
#         }


######################################### Version 1

import sqlite3
from typing import List
from tools.LLM import call_llm

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart


DB_PATH = "research.db"


# ------------------------
# RETRIEVE DATA
# ------------------------
def get_pages(limit=100):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    SELECT id, title, summary FROM pages
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    rows = c.fetchall()
    conn.close()

    return [{"id": r[0], "title": r[1], "summary": r[2]} for r in rows]


def get_chunks(page_ids: List[int], limit_per_page=25):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    chunks = []

    for pid in page_ids:
        c.execute("""
        SELECT chunk_text FROM chunks
        WHERE page_id=?
        ORDER BY chunk_index ASC
        LIMIT ?
        """, (pid, limit_per_page))

        rows = c.fetchall()
        chunks.extend([r[0] for r in rows])

    conn.close()
    return chunks


# ------------------------
# CONTEXT
# ------------------------
def build_context(pages, chunks, max_chars=2000000):
    context = "=== SUMMARIES ===\n\n"

    for p in pages:
        block = f"TITLE: {p['title']}\nSUMMARY: {p['summary']}\n---\n"
        if len(context) + len(block) > max_chars:
            break
        context += block

    context += "\n=== DETAILS ===\n\n"

    for ch in chunks:
        if len(context) + len(ch) > max_chars:
            break
        context += ch + "\n---\n"

    return context


# ------------------------
# STYLES
# ------------------------
def get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='TitleStyle',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=20
    ))

    styles.add(ParagraphStyle(
        name='HeadingStyle',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#34495e"),
        spaceAfter=12
    ))

    styles.add(ParagraphStyle(
        name='BodyStyle',
        fontSize=11,
        leading=14,
        spaceAfter=6
    ))

    return styles


# ------------------------
# CHART
# ------------------------
def create_chart():
    data = [10, 20, 30, 40]
    labels = ["A", "B", "C", "D"]

    drawing = Drawing(400, 200)
    chart = VerticalBarChart()

    chart.x = 50
    chart.y = 50
    chart.height = 125
    chart.width = 300

    chart.data = [data]
    chart.categoryAxis.categoryNames = labels

    drawing.add(chart)
    return drawing


# ------------------------
# HIGHLIGHT BOX
# ------------------------
def highlight_box(text):
    table = Table([[text]], colWidths=[450])

    table.setStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ecf0f1")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#3498db")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ])

    return table


# ------------------------
# TABLE PARSER
# ------------------------
def parse_table(lines):
    table_data = []
    for line in lines:
        if "|" in line:
            row = [c.strip() for c in line.split("|") if c.strip()]
            if row:
                table_data.append(row)
    return table_data


# ------------------------
# PDF GENERATOR
# ------------------------
def generate_pdf(text, filename="report.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = get_styles()

    story = []

    # Cover Page
    story.append(Paragraph("AI Research Report", styles["TitleStyle"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Generated by AI System", styles["BodyStyle"]))
    story.append(Spacer(1, 40))

    # Highlight
    story.append(highlight_box("Key Insight: This report summarizes major findings."))
    story.append(Spacer(1, 20))

    # Chart
    story.append(create_chart())
    story.append(Spacer(1, 20))

    # Content parsing
    lines = text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("# "):
            story.append(Paragraph(line[2:], styles["TitleStyle"]))

        elif line.startswith("## "):
            story.append(Paragraph(line[3:], styles["HeadingStyle"]))

        elif line.startswith("- "):
            story.append(Paragraph(f"• {line[2:]}", styles["BodyStyle"]))

        elif "|" in line:
            table_lines = []

            while i < len(lines) and "|" in lines[i]:
                table_lines.append(lines[i])
                i += 1

            data = parse_table(table_lines)
            if data:
                table = Table(data)
                table.setStyle([
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ])
                story.append(table)
                story.append(Spacer(1, 10))
            continue

        else:
            if line:
                story.append(Paragraph(line, styles["BodyStyle"]))

        story.append(Spacer(1, 6))
        i += 1

    doc.build(story)
    return filename


# ------------------------
# WRITER AGENT
# ------------------------
class WriterAgent:
    def run(self, topic: str):
        pages = get_pages()

        if not pages:
            return {"error": "No data"}

        page_ids = [p["id"] for p in pages]
        chunks = get_chunks(page_ids)

        context = build_context(pages, chunks)

        prompt = f"""
Write a professional structured report.

RULES:
- Use markdown (#, ##)
- Use bullet points
- Include at least one table

TOPIC: {topic}

DATA:
{context}
"""

        report = call_llm(prompt, mode="long")

        pdf = generate_pdf(report)

        return {
            "report": report,
            "pdf": pdf
        }