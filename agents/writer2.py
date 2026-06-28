# import sqlite3
# from typing import List, Dict, Any
# from datetime import datetime
# from tools.LLM import call_llm

# from reportlab.platypus import (
#     SimpleDocTemplate,
#     Paragraph,
#     Spacer,
#     Table,
#     TableStyle,
#     PageBreak,
#     Image,
#     KeepTogether,
#     ListFlowable,
#     ListItem,
#     HRFlowable
# )
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.pagesizes import A4, letter
# from reportlab.lib.units import inch, cm
# from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
# from reportlab.pdfgen import canvas
# from reportlab.graphics.shapes import Drawing, Rect, String, Line
# from reportlab.graphics.charts.barcharts import VerticalBarChart
# from reportlab.graphics.charts.piecharts import Pie
# from reportlab.graphics.charts.lineplots import LinePlot
# from reportlab.graphics import renderPDF
# from io import BytesIO
# import re

# DB_PATH = "research.db"

# # ============================
# # FIXED DATA RETRIEVAL - Matches Analyzer Schema
# # ============================

# def get_pages(limit=100, offset=0, url_filter=None):
#     """Retrieve pages from analyzer's schema: id, url, title, content_hash, summary, created_at"""
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()

#     query = """
#     SELECT id, url, title, content_hash, summary, created_at
#     FROM pages 
#     WHERE 1=1
#     """
#     params = []

#     if url_filter:
#         query += " AND url LIKE ?"
#         params.append(f"%{url_filter}%")

#     query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
#     params.extend([limit, offset])

#     c.execute(query, params)
#     rows = c.fetchall()
#     conn.close()

#     return [{
#         "id": r[0],
#         "url": r[1],
#         "title": r[2],
#         "content_hash": r[3],
#         "summary": r[4],
#         "created_at": r[5]
#     } for r in rows]


# def get_chunks(page_ids: List[int], limit_per_page=10):
#     """Retrieve chunks from analyzer's schema: id, page_id, chunk_text, chunk_index"""
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     chunks = []

#     for pid in page_ids:
#         c.execute("""
#         SELECT chunk_text, chunk_index
#         FROM chunks
#         WHERE page_id=?
#         ORDER BY chunk_index ASC
#         LIMIT ?
#         """, (pid, limit_per_page))

#         rows = c.fetchall()
#         for r in rows:
#             chunks.append({
#                 "text": r[0],
#                 "index": r[1],
#                 "page_id": pid
#             })

#     conn.close()
#     return chunks


# def get_statistics():
#     """Get database statistics matching analyzer schema"""
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()

#     stats = {}
#     c.execute("SELECT COUNT(*) FROM pages")
#     stats["total_pages"] = c.fetchone()[0]

#     c.execute("SELECT COUNT(*) FROM chunks")
#     stats["total_chunks"] = c.fetchone()[0]

#     # Get recent pages count (last 7 days)
#     c.execute("""
#     SELECT COUNT(*) FROM pages 
#     WHERE created_at >= datetime('now', '-7 days')
#     """)
#     stats["recent_pages"] = c.fetchone()[0]

#     # Average chunks per page
#     c.execute("""
#     SELECT AVG(chunk_count) FROM (
#         SELECT page_id, COUNT(*) as chunk_count 
#         FROM chunks 
#         GROUP BY page_id
#     )
#     """)
#     stats["avg_chunks_per_page"] = round(c.fetchone()[0] or 0, 1)

#     # Content size statistics
#     c.execute("SELECT AVG(LENGTH(summary)) FROM pages")
#     stats["avg_summary_length"] = int(c.fetchone()[0] or 0)

#     c.execute("SELECT AVG(LENGTH(chunk_text)) FROM chunks")
#     stats["avg_chunk_length"] = int(c.fetchone()[0] or 0)

#     conn.close()
#     return stats


# def search_content(query_text: str, limit=20):
#     """Search pages by title or summary content"""
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()

#     search_term = f"%{query_text}%"
    
#     c.execute("""
#     SELECT id, url, title, summary, created_at
#     FROM pages
#     WHERE title LIKE ? OR summary LIKE ?
#     ORDER BY 
#         CASE 
#             WHEN title LIKE ? THEN 1
#             WHEN summary LIKE ? THEN 2
#             ELSE 3
#         END
#     LIMIT ?
#     """, (search_term, search_term, search_term, search_term, limit))
    
#     rows = c.fetchall()
#     conn.close()

#     return [{
#         "id": r[0],
#         "url": r[1],
#         "title": r[2],
#         "summary": r[3],
#         "created_at": r[4]
#     } for r in rows]


# # ============================
# # ENHANCED CONTEXT BUILDING
# # ============================

# def build_enhanced_context(pages, chunks, max_chars=30000):
#     """Build rich context with structured sections - FIXED for analyzer schema"""
#     context_parts = []

#     # Executive Summary Section - Top pages by recency
#     summary_section = "=== EXECUTIVE SUMMARY ===\n\n"
#     for p in pages[:5]:
#         block = f"TITLE: {p['title']}\n"
#         block += f"URL: {p['url']}\n"
#         block += f"DATE: {p['created_at']}\n"
#         block += f"SUMMARY: {p['summary']}\n---\n"
#         if len(summary_section) + len(block) < max_chars * 0.3:
#             summary_section += block
#     context_parts.append(summary_section)

#     # Detailed Analysis Section
#     detail_section = "\n=== DETAILED ANALYSIS ===\n\n"
#     for p in pages:
#         block = f"[{p['created_at']}] {p['title']}\n"
#         block += f"Source: {p['url']}\n"
#         block += f"Summary: {p['summary']}\n---\n"
#         if len(detail_section) + len(block) < max_chars * 0.4:
#             detail_section += block
#     context_parts.append(detail_section)

#     # Supporting Evidence Section (Chunks)
#     evidence_section = "\n=== SUPPORTING EVIDENCE ===\n\n"
#     for ch in chunks[:20]:
#         block = f"[Page {ch['page_id']} | Chunk {ch['index']}]\n"
#         block += f"{ch['text']}\n---\n"
#         if len(evidence_section) + len(block) < max_chars * 0.3:
#             evidence_section += block
#     context_parts.append(evidence_section)

#     return "\n".join(context_parts)


# def get_enhanced_styles():
#     """Comprehensive style system with professional theming"""
#     styles = getSampleStyleSheet()

#     # Color palette - professional blue-gray theme
#     PRIMARY_COLOR = colors.HexColor("#1a365d")
#     SECONDARY_COLOR = colors.HexColor("#2c5282")
#     ACCENT_COLOR = colors.HexColor("#3182ce")
#     LIGHT_BG = colors.HexColor("#ebf8ff")
#     DARK_TEXT = colors.HexColor("#1a202c")
#     GRAY_TEXT = colors.HexColor("#4a5568")
#     SUCCESS_COLOR = colors.HexColor("#38a169")
#     WARNING_COLOR = colors.HexColor("#d69e2e")

#     # Helper to safely add or replace styles
#     def add_style(name, **kwargs):
#         if name in styles:
#             # Update existing style
#             for key, value in kwargs.items():
#                 setattr(styles[name], key, value)
#         else:
#             # Add new style
#             styles.add(ParagraphStyle(name=name, **kwargs))

#     # Cover Page Styles (NEW - don't exist in sample)
#     add_style('CoverTitle',
#         fontSize=36,
#         leading=44,
#         textColor=PRIMARY_COLOR,
#         alignment=TA_CENTER,
#         spaceAfter=30,
#         fontName='Helvetica-Bold'
#     )

#     add_style('CoverSubtitle',
#         fontSize=18,
#         leading=24,
#         textColor=SECONDARY_COLOR,
#         alignment=TA_CENTER,
#         spaceAfter=20,
#         fontName='Helvetica'
#     )

#     add_style('CoverMeta',
#         fontSize=12,
#         leading=16,
#         textColor=GRAY_TEXT,
#         alignment=TA_CENTER,
#         spaceAfter=12,
#         fontName='Helvetica'
#     )

#     # Header Styles (NEW)
#     add_style('ReportTitle',
#         fontSize=28,
#         leading=34,
#         textColor=PRIMARY_COLOR,
#         spaceAfter=24,
#         fontName='Helvetica-Bold',
#         borderPadding=10
#     )

#     add_style('SectionHeader',
#         fontSize=20,
#         leading=26,
#         textColor=SECONDARY_COLOR,
#         spaceAfter=16,
#         spaceBefore=20,
#         fontName='Helvetica-Bold',
#         borderColor=ACCENT_COLOR,
#         borderWidth=2,
#         borderPadding=5,
#         leftIndent=0
#     )

#     add_style('SubSectionHeader',
#         fontSize=16,
#         leading=22,
#         textColor=ACCENT_COLOR,
#         spaceAfter=12,
#         spaceBefore=14,
#         fontName='Helvetica-Bold'
#     )

#     # Body Styles - UPDATE EXISTING (BodyText exists in sample)
#     add_style('BodyText',
#         fontSize=11,
#         leading=16,
#         textColor=DARK_TEXT,
#         alignment=TA_JUSTIFY,
#         spaceAfter=10,
#         fontName='Helvetica',
#         firstLineIndent=20
#     )

#     # BulletPoint (NEW)
#     add_style('BulletPoint',
#         fontSize=11,
#         leading=16,
#         textColor=DARK_TEXT,
#         leftIndent=30,
#         spaceAfter=6,
#         bulletIndent=15,
#         bulletFontName='Helvetica-Bold',
#         bulletColor=ACCENT_COLOR
#     )

#     # QuoteStyle (NEW)
#     add_style('QuoteStyle',
#         fontSize=10,
#         leading=15,
#         textColor=GRAY_TEXT,
#         leftIndent=40,
#         rightIndent=40,
#         spaceAfter=12,
#         fontName='Helvetica-Oblique',
#         borderColor=LIGHT_BG,
#         borderWidth=1,
#         borderPadding=10,
#         backColor=LIGHT_BG
#     )

#     # Table Styles (NEW)
#     add_style('TableHeader',
#         fontSize=10,
#         leading=14,
#         textColor=colors.white,
#         alignment=TA_CENTER,
#         fontName='Helvetica-Bold'
#     )

#     add_style('TableCell',
#         fontSize=9,
#         leading=13,
#         textColor=DARK_TEXT,
#         alignment=TA_LEFT,
#         fontName='Helvetica'
#     )

#     # Special Elements (NEW)
#     add_style('KeyInsight',
#         fontSize=12,
#         leading=18,
#         textColor=PRIMARY_COLOR,
#         alignment=TA_LEFT,
#         fontName='Helvetica-Bold',
#         borderColor=ACCENT_COLOR,
#         borderWidth=3,
#         borderPadding=15,
#         backColor=LIGHT_BG,
#         spaceAfter=20,
#         spaceBefore=10
#     )

#     add_style('Caption',
#         fontSize=9,
#         leading=12,
#         textColor=GRAY_TEXT,
#         alignment=TA_CENTER,
#         fontName='Helvetica-Oblique',
#         spaceAfter=15
#     )

#     add_style('Footer',
#         fontSize=8,
#         leading=10,
#         textColor=GRAY_TEXT,
#         alignment=TA_CENTER,
#         fontName='Helvetica'
#     )

#     return styles

# # ============================
# # ENHANCED VISUALIZATIONS
# # ============================

# def create_enhanced_bar_chart(data: List[float], labels: List[str], title: str = ""):
#     """Create professional bar chart with styling"""
#     drawing = Drawing(500, 250)

#     chart = VerticalBarChart()
#     chart.x = 60
#     chart.y = 60
#     chart.height = 150
#     chart.width = 400

#     chart.data = [data]
#     chart.categoryAxis.categoryNames = labels
#     chart.categoryAxis.labels.fontSize = 10
#     chart.categoryAxis.labels.angle = 0

#     chart.valueAxis.valueMin = 0
#     chart.valueAxis.valueMax = max(data) * 1.2 if data else 100
#     chart.valueAxis.labels.fontSize = 9

#     chart.bars[0].fillColor = colors.HexColor("#3182ce")
#     chart.bars[0].strokeColor = colors.HexColor("#2c5282")
#     chart.bars[0].strokeWidth = 1

#     if title:
#         drawing.add(String(250, 230, title, fontSize=12,
#                           fillColor=colors.HexColor("#1a365d"),
#                           textAnchor="middle", fontName="Helvetica-Bold"))

#     drawing.add(chart)
#     return drawing


# def create_pie_chart(data: List[float], labels: List[str], title: str = ""):
#     """Create pie chart for distribution"""
#     drawing = Drawing(400, 300)

#     pie = Pie()
#     pie.x = 100
#     pie.y = 50
#     pie.width = 200
#     pie.height = 200
#     pie.data = data
#     pie.labels = labels
#     pie.slices.strokeWidth = 1
#     pie.slices.strokeColor = colors.white

#     colors_list = [
#         colors.HexColor("#3182ce"),
#         colors.HexColor("#38a169"),
#         colors.HexColor("#d69e2e"),
#         colors.HexColor("#e53e3e"),
#         colors.HexColor("#805ad5"),
#         colors.HexColor("#d53f8c")
#     ]

#     for i, color in enumerate(colors_list):
#         if i < len(pie.slices):
#             pie.slices[i].fillColor = color

#     pie.sideLabels = True
#     pie.labels.fontSize = 9

#     if title:
#         drawing.add(String(200, 280, title, fontSize=12,
#                           fillColor=colors.HexColor("#1a365d"),
#                           textAnchor="middle", fontName="Helvetica-Bold"))

#     drawing.add(pie)
#     return drawing


# def create_trend_line(data_points: List[tuple], title: str = ""):
#     """Create line chart for trends over time"""
#     drawing = Drawing(500, 250)

#     lp = LinePlot()
#     lp.x = 60
#     lp.y = 60
#     lp.height = 150
#     lp.width = 400

#     lp.data = [data_points]
#     lp.lines[0].strokeColor = colors.HexColor("#3182ce")
#     lp.lines[0].strokeWidth = 2

#     lp.xValueAxis.valueMin = min([p[0] for p in data_points])
#     lp.xValueAxis.valueMax = max([p[0] for p in data_points])
#     lp.yValueAxis.valueMin = min([p[1] for p in data_points]) * 0.9
#     lp.yValueAxis.valueMax = max([p[1] for p in data_points]) * 1.1

#     if title:
#         drawing.add(String(250, 230, title, fontSize=12,
#                           fillColor=colors.HexColor("#1a365d"),
#                           textAnchor="middle", fontName="Helvetica-Bold"))

#     drawing.add(lp)
#     return drawing


# def create_dashboard_charts(stats: Dict[str, Any]):
#     """Create comprehensive dashboard with multiple charts"""
#     elements = []

#     # Database statistics bar chart
#     stat_labels = ["Pages", "Chunks", "Recent", "Avg Chunks/Page"]
#     stat_values = [
#         stats.get("total_pages", 0),
#         stats.get("total_chunks", 0),
#         stats.get("recent_pages", 0),
#         stats.get("avg_chunks_per_page", 0)
#     ]
#     elements.append(create_enhanced_bar_chart(stat_values, stat_labels, "Database Statistics"))
#     elements.append(Spacer(1, 20))

#     return elements


# # ============================
# # ENHANCED UI COMPONENTS
# # ============================

# def create_highlight_box(text: str, style_type: str = "info"):
#     """Create styled highlight boxes with different types"""
#     colors_map = {
#         "info": (colors.HexColor("#ebf8ff"), colors.HexColor("#3182ce")),
#         "success": (colors.HexColor("#f0fff4"), colors.HexColor("#38a169")),
#         "warning": (colors.HexColor("#fffaf0"), colors.HexColor("#d69e2e")),
#         "danger": (colors.HexColor("#fff5f5"), colors.HexColor("#e53e3e"))
#     }

#     bg_color, border_color = colors_map.get(style_type, colors_map["info"])
#     styles = get_enhanced_styles()
#     para = Paragraph(text, styles['KeyInsight'])

#     return para


# def create_stat_card(label: str, value: str, trend: str = None):
#     """Create statistic card for dashboard"""
#     data = [[Paragraph(f"<b>{value}</b>", ParagraphStyle(
#         name='StatValue',
#         fontSize=24,
#         textColor=colors.HexColor("#1a365d"),
#         alignment=TA_CENTER,
#         fontName='Helvetica-Bold'
#     ))],
#     [Paragraph(label, ParagraphStyle(
#         name='StatLabel',
#         fontSize=10,
#         textColor=colors.HexColor("#4a5568"),
#         alignment=TA_CENTER,
#         fontName='Helvetica'
#     ))]]

#     if trend:
#         trend_color = colors.HexColor("#38a169") if "+" in trend else colors.HexColor("#e53e3e")
#         data.append([Paragraph(trend, ParagraphStyle(
#             name='StatTrend',
#             fontSize=9,
#             textColor=trend_color,
#             alignment=TA_CENTER,
#             fontName='Helvetica'
#         ))])

#     table = Table(data, colWidths=[120])
#     table.setStyle([
#         ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7fafc")),
#         ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
#         ("TOPPADDING", (0, 0), (-1, -1), 15),
#         ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
#         ("LEFTPADDING", (0, 0), (-1, -1), 10),
#         ("RIGHTPADDING", (0, 0), (-1, -1), 10),
#     ])

#     return table


# def create_enhanced_table(data: List[List[str]], header: List[str] = None,
#                          col_widths: List[int] = None, style_type: str = "default"):
#     """Create professionally styled tables"""

#     styles = get_enhanced_styles()

#     table_data = []
#     if header:
#         table_data.append([Paragraph(h, styles['TableHeader']) for h in header])

#     for row in data:
#         table_data.append([Paragraph(str(cell), styles['TableCell']) for cell in row])

#     if not col_widths and table_data:
#         available_width = 450
#         num_cols = len(table_data[0])
#         col_widths = [available_width // num_cols] * num_cols

#     table = Table(table_data, colWidths=col_widths, repeatRows=1 if header else 0)

#     style_configs = {
#         "default": [
#             ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
#             ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5282")),
#             ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
#             ("ALIGN", (0, 0), (-1, -1), "LEFT"),
#             ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
#             ("TOPPADDING", (0, 0), (-1, -1), 8),
#             ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
#             ("LEFTPADDING", (0, 0), (-1, -1), 10),
#             ("RIGHTPADDING", (0, 0), (-1, -1), 10),
#         ],
#         "striped": [
#             ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
#             ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
#             ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
#             ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
#             ("ALIGN", (0, 0), (-1, -1), "LEFT"),
#             ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
#             ("TOPPADDING", (0, 0), (-1, -1), 8),
#             ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
#         ],
#         "minimal": [
#             ("LINEBELOW", (0, 0), (-1, 0), 2, colors.HexColor("#2c5282")),
#             ("LINEBELOW", (0, -1), (-1, -1), 1, colors.HexColor("#e2e8f0")),
#             ("ALIGN", (0, 0), (-1, -1), "LEFT"),
#             ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
#             ("TOPPADDING", (0, 0), (-1, -1), 10),
#             ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
#         ]
#     }

#     table.setStyle(TableStyle(style_configs.get(style_type, style_configs["default"])))
#     return table


# # ============================
# # ENHANCED PDF GENERATOR
# # ============================

# class PageNumCanvas(canvas.Canvas):
#     """Custom canvas for page numbers and headers"""
#     def __init__(self, *args, **kwargs):
#         canvas.Canvas.__init__(self, *args, **kwargs)
#         self.pages = []
#         self.report_title = kwargs.get('report_title', 'AI Research Report')

#     def showPage(self):
#         self.pages.append(dict(self.__dict__))
#         self._startPage()

#     def save(self):
#         page_count = len(self.pages)
#         for page in self.pages:
#             self.__dict__.update(page)
#             self.draw_page_number(page_count)
#             canvas.Canvas.showPage(self)
#         canvas.Canvas.save(self)

#     def draw_page_number(self, page_count):
#         self.setStrokeColor(colors.HexColor("#e2e8f0"))
#         self.line(50, 40, 545, 40)

#         self.setFillColor(colors.HexColor("#4a5568"))
#         self.setFont("Helvetica", 9)
#         self.drawRightString(545, 25, f"Page {self._pageNumber} of {page_count}")

#         self.setFont("Helvetica-Oblique", 8)
#         self.drawString(50, 25, self.report_title)

#         self.setFillColor(colors.HexColor("#2c5282"))
#         self.setFont("Helvetica-Bold", 10)
#         self.drawString(50, 800, "AI Research Report")
#         self.drawRightString(545, 800, datetime.now().strftime("%B %d, %Y"))
#         self.line(50, 795, 545, 795)


# def generate_enhanced_pdf(text: str, filename: str = "enhanced_report.pdf",
#                          topic: str = "", stats: Dict = None, pages_data: List[Dict] = None):
#     """Generate comprehensive multi-page PDF report"""

#     doc = SimpleDocTemplate(
#         filename,
#         pagesize=A4,
#         rightMargin=50,
#         leftMargin=50,
#         topMargin=80,
#         bottomMargin=60
#     )

#     styles = get_enhanced_styles()
#     story = []

#     # ============== COVER PAGE ==============
#     story.append(Spacer(1, 100))
#     story.append(Paragraph("AI Research Report", styles['CoverTitle']))
#     story.append(Spacer(1, 20))
#     story.append(Paragraph(f"Topic: {topic}", styles['CoverSubtitle']))
#     story.append(Spacer(1, 40))

#     meta_text = f"""
#     <b>Generated:</b> {datetime.now().strftime("%B %d, %Y at %H:%M")}<br/>
#     <b>System:</b> AI Research Assistant<br/>
#     <b>Classification:</b> Internal Research Document
#     """
#     story.append(Paragraph(meta_text, styles['CoverMeta']))
#     story.append(Spacer(1, 60))

#     if stats:
#         story.append(Paragraph("Document Overview", styles['SubSectionHeader']))
#         overview_data = [
#             create_stat_card("Total Pages", str(stats.get("total_pages", 0))),
#             create_stat_card("Data Chunks", str(stats.get("total_chunks", 0))),
#             create_stat_card("Content Sources", str(stats.get("recent_pages", 0)))
#         ]
#         story.append(Table([overview_data], colWidths=[130, 130, 130]))

#     story.append(PageBreak())

#     # ============== EXECUTIVE SUMMARY ==============
#     story.append(Paragraph("Executive Summary", styles['SectionHeader']))
#     story.append(Spacer(1, 10))

#     lines = text.split("\n")
#     summary_text = []
#     i = 0

#     while i < len(lines) and not lines[i].strip().startswith("#"):
#         if lines[i].strip():
#             summary_text.append(lines[i].strip())
#         i += 1

#     if summary_text:
#         insight_text = "<b>Key Finding:</b> " + " ".join(summary_text[:3])
#         story.append(create_highlight_box(insight_text, "info"))

#     story.append(Spacer(1, 20))

#     # ============== DASHBOARD / STATISTICS PAGE ==============
#     if stats:
#         story.append(Paragraph("Data Overview", styles['SectionHeader']))
#         story.append(Spacer(1, 15))

#         chart_elements = create_dashboard_charts(stats)
#         for elem in chart_elements:
#             story.append(elem)

#         story.append(Spacer(1, 30))

#         # Source pages table
#         if pages_data:
#             story.append(Paragraph("Source Pages", styles['SubSectionHeader']))
#             pages_table_data = [[p['title'][:40], p['url'][:50], p['created_at'][:10]] for p in pages_data[:10]]
#             story.append(create_enhanced_table(
#                 pages_table_data,
#                 header=["Title", "URL", "Date"],
#                 col_widths=[150, 200, 100],
#                 style_type="striped"
#             ))

#         story.append(PageBreak())

#     # ============== MAIN CONTENT ==============
#     content_buffer = []
#     current_section = []

#     while i < len(lines):
#         line = lines[i]

#         if line.strip().startswith("# ") and current_section:
#             if len(current_section) > 10:
#                 story.append(PageBreak())
#             for item in current_section:
#                 story.append(item)
#             current_section = []

#         if line.strip().startswith("# "):
#             current_section.append(Paragraph(line.strip()[2:], styles['ReportTitle']))
#             current_section.append(Spacer(1, 10))

#         elif line.strip().startswith("## "):
#             current_section.append(Paragraph(line.strip()[3:], styles['SectionHeader']))
#             current_section.append(Spacer(1, 8))

#         elif line.strip().startswith("### "):
#             current_section.append(Paragraph(line.strip()[4:], styles['SubSectionHeader']))
#             current_section.append(Spacer(1, 6))

#         elif line.strip().startswith("- ") or line.strip().startswith("* "):
#             bullet_text = line.strip()[2:]
#             bullet_text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", bullet_text)
#             bullet_text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", bullet_text)
#             current_section.append(Paragraph(f"• {bullet_text}", styles['BulletPoint']))

#         elif re.match(r"^\d+\.\s", line.strip()):
#             num_text = re.sub(r"^\d+\.\s", "", line.strip())
#             num_text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", num_text)
#             current_section.append(Paragraph(num_text, styles['BulletPoint']))

#         elif "|" in line and line.strip():
#             table_lines = []
#             while i < len(lines) and "|" in lines[i]:
#                 table_lines.append(lines[i])
#                 i += 1

#             table_data = parse_enhanced_table(table_lines)
#             if table_data:
#                 current_section.append(create_enhanced_table(
#                     table_data[1:] if len(table_data) > 1 else table_data,
#                     header=table_data[0] if table_data else None,
#                     style_type="striped"
#                 ))
#                 current_section.append(Spacer(1, 12))
#             continue

#         elif line.strip().startswith("> "):
#             quote_text = line.strip()[2:]
#             current_section.append(Paragraph(quote_text, styles['QuoteStyle']))

#         elif line.strip() == "---" or line.strip() == "***":
#             current_section.append(HRFlowable(width="100%", thickness=1,
#                                              color=colors.HexColor("#e2e8f0")))
#             current_section.append(Spacer(1, 10))

#         elif line.strip():
#             para_text = line.strip()
#             para_text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", para_text)
#             para_text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", para_text)
#             para_text = re.sub(r"`([^`]+)`", r"<font face='Courier'>\1</font>", para_text)

#             current_section.append(Paragraph(para_text, styles['BodyText']))

#         i += 1

#     for item in current_section:
#         story.append(item)

#     # ============== APPENDIX ==============
#     story.append(PageBreak())
#     story.append(Paragraph("Appendix", styles['SectionHeader']))
#     story.append(Spacer(1, 15))

#     appendix_text = f"""
#     <b>Document Information</b><br/>
#     This report was generated automatically by the AI Research Assistant system.<br/>
#     Generation timestamp: {datetime.now().isoformat()}<br/>
#     Data source: {DB_PATH}<br/><br/>

#     <b>Methodology</b><br/>
#     Content is synthesized from verified research database entries using
#     retrieval-augmented generation techniques. Data is stored in SQLite with
#     deduplication based on content hashing.<br/><br/>

#     <b>Disclaimer</b><br/>
#     This document is for research purposes only. Verify critical information
#     against primary sources before making decisions.
#     """
#     story.append(Paragraph(appendix_text, styles['BodyText']))

#     doc.build(story, canvasmaker=lambda *args, **kwargs: PageNumCanvas(*args, report_title=topic, **kwargs))
#     return filename


# def parse_enhanced_table(lines):
#     """Enhanced table parser supporting markdown tables"""
#     table_data = []

#     for line in lines:
#         if re.match(r"^\s*\|?[\-:|\s]+\|?\s*$", line):
#             continue

#         if "|" in line:
#             cells = [cell.strip() for cell in line.split("|")]
#             cells = [c for c in cells if c]
#             if cells:
#                 table_data.append(cells)

#     return table_data


# # ============================
# # ENHANCED WRITER AGENT - FIXED
# # ============================

# class EnhancedWriterAgent:
#     """Enhanced writer with multi-page support and rich formatting - FIXED for analyzer schema"""

#     def __init__(self):
#         self.report_history = []

#     def run(self, topic: str, options: Dict[str, Any] = None):
#         """
#         Generate comprehensive multi-page report

#         Options:
#             - detail_level: "brief", "standard", "comprehensive" (default: "comprehensive")
#             - include_charts: bool (default: True)
#             - page_limit: int (default: 50)
#             - search_query: str (filter pages by content)
#         """
#         options = options or {}
#         detail_level = options.get("detail_level", "comprehensive")
#         include_charts = options.get("include_charts", True)
#         search_query = options.get("search_query", None)

#         # Get data - FIXED: removed category filter, uses search instead
#         if search_query:
#             pages = search_content(search_query, limit=50)
#         else:
#             pages = get_pages(limit=100)

#         if not pages:
#             return {"error": "No data available for report generation. Run analyzer first to populate database."}

#         # Get statistics
#         stats = get_statistics() if include_charts else None

#         # Retrieve chunks
#         page_ids = [p["id"] for p in pages]
#         chunks_per_page = {"brief": 3, "standard": 5, "comprehensive": 10}.get(detail_level, 10)
#         chunks = get_chunks(page_ids, limit_per_page=chunks_per_page)

#         # Build rich context
#         context = build_enhanced_context(pages, chunks)

#         # Generate report with enhanced prompt
#         prompt = self._build_prompt(topic, context, detail_level)
#         report = call_llm(prompt, mode="long")

#         # Generate enhanced PDF
#         pdf_filename = f"report_{topic.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
#         pdf_path = generate_enhanced_pdf(report, filename=pdf_filename, topic=topic, stats=stats, pages_data=pages)

#         # Store in history
#         self.report_history.append({
#             "topic": topic,
#             "timestamp": datetime.now().isoformat(),
#             "pages": len(pages),
#             "chunks": len(chunks),
#             "pdf_path": pdf_path
#         })

#         return {
#             "report": report,
#             "pdf": pdf_path,
#             "stats": stats,
#             "metadata": {
#                 "pages_processed": len(pages),
#                 "chunks_included": len(chunks),
#                 "detail_level": detail_level,
#                 "generation_time": datetime.now().isoformat()
#             }
#         }

#     def _build_prompt(self, topic: str, context: str, detail_level: str) -> str:
#         """Build context-aware prompt for report generation"""

#         detail_instructions = {
#             "brief": """
#                 Create a concise 2-3 page executive summary.
#                 Focus on key findings only.
#                 Maximum 2-3 sections with brief bullet points.
#             """,
#             "standard": """
#                 Create a standard 5-7 page report.
#                 Include introduction, 3-4 main sections, and conclusion.
#                 Use tables for comparisons.
#             """,
#             "comprehensive": """
#                 Create a comprehensive 10+ page detailed report.
#                 Include: Executive Summary, Introduction, 5-7 Detailed Sections,
#                 Data Analysis, Case Studies, Recommendations, and Conclusion.
#                 Use multiple tables, structured analysis, and detailed explanations.
#             """
#         }

#         prompt = f"""
# Write a professional structured research report on: {topic}

# {detail_instructions.get(detail_level, detail_instructions["comprehensive"])}

# FORMATTING REQUIREMENTS:
# - Use markdown headers (# for title, ## for sections, ### for subsections)
# - Include at least 2-3 data tables with comparisons
# - Use bullet points (- item) for lists
# - Include blockquotes (>) for important insights
# - Add horizontal rules (---) between major sections
# - Bold (**text**) key terms and statistics
# - Italicize (*text*) emphasis points

# CONTENT GUIDELINES:
# - Start with an executive summary (not a header)
# - Provide specific data points and metrics
# - Include comparative analysis where relevant
# - Add actionable recommendations section
# - Cite confidence levels for key claims
# - Address potential limitations or caveats

# DATA CONTEXT:
# {context}

# Generate the complete report now.
# """
#         return prompt

#     def get_history(self):
#         """Return generation history"""
#         return self.report_history


# # ============================
# # BACKWARD COMPATIBILITY
# # ============================

# def generate_pdf(text, filename="report.pdf"):
#     """Backward compatible wrapper"""
#     return generate_enhanced_pdf(text, filename, topic="Research Report")


# class WriterAgent:
#     """Backward compatible wrapper"""
#     def __init__(self):
#         self._enhanced = EnhancedWriterAgent()

#     def run(self, topic: str):
#         return self._enhanced.run(topic, options={"detail_level": "standard"})


# # Export main classes
# __all__ = [
#     'EnhancedWriterAgent',
#     'WriterAgent',
#     'generate_enhanced_pdf',
#     'generate_pdf',
#     'get_enhanced_styles',
#     'create_enhanced_bar_chart',
#     'create_pie_chart',
#     'create_enhanced_table',
#     'get_pages',
#     'get_chunks',
#     'get_statistics',
#     'search_content'
# ]

import sqlite3
from typing import List, Dict, Any
from datetime import datetime
from tools.LLM import call_llm

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    Image, KeepTogether, ListFlowable, ListItem, HRFlowable
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from io import BytesIO
import re

DB_PATH = "research.db"

# ============================
# PRODUCTION TEXT SANITIZATION (CRITICAL FIXES)
# ============================

def sanitize_text_for_pdf(text: str) -> str:
    """
    Fix LLM artifacts: 'n' instead of '-', spacing issues, Unicode symbols.
    Uses specific replacements to avoid breaking valid words.
    """
    if not text:
        return ""

    # Specific replacements for patterns seen in PDFs (ORDER MATTERS - longest first)
    replacements = {
        # Multi-part compounds (fix these first)
        'humanninnthenloop': 'human-in-the-loop',
        'vitalnsignnbased': 'vital-sign-based',
        'typendiabetes': 'type-1-diabetes',

        # Standard compounds with 'n' that should be '-'
        'AIndriven': 'AI-driven',
        'expertnlevel': 'expert-level',
        'nonnrepresentative': 'non-representative',
        'renidentification': 're-identification',
        'leadnidentification': 'lead-identification',
        'timenlines': 'timelines',
        'multinomics': 'multi-omics',
        'diseasenrelevant': 'disease-relevant',
        'virtualnscreening': 'virtual-screening',
        'realntime': 'real-time',
        'earlynwarning': 'early-warning',
        '30nday': '30-day',
        'literaturenbased': 'literature-based',
        'preclinicaln': 'preclinical-',
        'postnmarket': 'post-market',
        'usernfriendly': 'user-friendly',
        'blacknbox': 'black-box',
        'spectrumnbias': 'spectrum-bias',
        'humannin': 'human-in',
        'ninthe': '-in-the',
        'nloop': '-loop',

        # Numbers
        'n1n': '-1-',
        'nn': '-',
        'n-': '-',

        # Model names and specific artifacts
        'Qwen330BIA3B': 'Qwen3-30B-A3B',
        'GPTIOSS': 'GPT-OSS',
        'ALF Research Report': 'AI Research Report',
    }

    # Apply replacements
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # Fix spacing around operators
    text = re.sub(r'=(?=\d)', '= ', text)  # =0.78 → = 0.78
    text = re.sub(r'(?<=\d)\s*vs\.\s*(?=\d)', ' vs. ', text)  # 0.78vs.0.52 → 0.78 vs. 0.52

    # Remove CJK artifacts
    text = re.sub(r'[国〡]', '', text)

    # Replace Unicode approx with tilde (PDF-safe)
    text = text.replace('≈', '~').replace('≃', '~').replace('∼', '~')

    # Remove invisible characters
    text = text.replace('\u200B', '').replace('\ufeff', '').replace('\u200C', '').replace('\u200D', '')

    # Normalize whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)

    return text.strip()


def clean_markdown_for_pdf(text: str) -> str:
    """Full pipeline for markdown → PDF text"""
    text = sanitize_text_for_pdf(text)

    # Fix bold/italic spacing
    text = re.sub(r'\*\*\s+', '**', text)
    text = re.sub(r'\s+\*\*', '**', text)
    text = re.sub(r'\*\s+', '*', text)
    text = re.sub(r'\s+\*', '*', text)

    return text


# ============================
# DATA RETRIEVAL (Unchanged)
# ============================

def get_pages(limit=100, offset=0, url_filter=None):
    """Retrieve pages from analyzer's schema"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = "SELECT id, url, title, content_hash, summary, created_at FROM pages WHERE 1=1"
    params = []
    if url_filter:
        query += " AND url LIKE ?"
        params.append(f"%{url_filter}%")
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "url": r[1], "title": r[2], "content_hash": r[3], "summary": r[4], "created_at": r[5]} for r in rows]


def get_chunks(page_ids: List[int], limit_per_page=10):
    """Retrieve chunks from analyzer's schema"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    chunks = []
    for pid in page_ids:
        c.execute("SELECT chunk_text, chunk_index FROM chunks WHERE page_id=? ORDER BY chunk_index ASC LIMIT ?", (pid, limit_per_page))
        for r in c.fetchall():
            chunks.append({"text": r[0], "index": r[1], "page_id": pid})
    conn.close()
    return chunks


def get_statistics():
    """Get database statistics"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    stats = {}
    c.execute("SELECT COUNT(*) FROM pages")
    stats["total_pages"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM chunks")
    stats["total_chunks"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM pages WHERE created_at >= datetime('now', '-7 days')")
    stats["recent_pages"] = c.fetchone()[0]
    c.execute("SELECT AVG(chunk_count) FROM (SELECT page_id, COUNT(*) as chunk_count FROM chunks GROUP BY page_id)")
    stats["avg_chunks_per_page"] = round(c.fetchone()[0] or 0, 1)
    c.execute("SELECT AVG(LENGTH(summary)) FROM pages")
    stats["avg_summary_length"] = int(c.fetchone()[0] or 0)
    c.execute("SELECT AVG(LENGTH(chunk_text)) FROM chunks")
    stats["avg_chunk_length"] = int(c.fetchone()[0] or 0)
    conn.close()
    return stats


def search_content(query_text: str, limit=20):
    """Search pages by title or summary content"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    search_term = f"%{query_text}%"
    c.execute("""SELECT id, url, title, summary, created_at FROM pages 
                 WHERE title LIKE ? OR summary LIKE ? 
                 ORDER BY CASE WHEN title LIKE ? THEN 1 WHEN summary LIKE ? THEN 2 ELSE 3 END 
                 LIMIT ?""", (search_term, search_term, search_term, search_term, limit))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "url": r[1], "title": r[2], "summary": r[3], "created_at": r[4]} for r in rows]


def build_enhanced_context(pages, chunks, max_chars=30000):
    """Build rich context with structured sections"""
    context_parts = []

    summary_section = "=== EXECUTIVE SUMMARY ===\n\n"
    for p in pages[:5]:
        block = f"TITLE: {p['title']}\nURL: {p['url']}\nDATE: {p['created_at']}\nSUMMARY: {p['summary']}\n---\n"
        if len(summary_section) + len(block) < max_chars * 0.3:
            summary_section += block
    context_parts.append(summary_section)

    detail_section = "\n=== DETAILED ANALYSIS ===\n\n"
    for p in pages:
        block = f"[{p['created_at']}] {p['title']}\nSource: {p['url']}\nSummary: {p['summary']}\n---\n"
        if len(detail_section) + len(block) < max_chars * 0.4:
            detail_section += block
    context_parts.append(detail_section)

    evidence_section = "\n=== SUPPORTING EVIDENCE ===\n\n"
    for ch in chunks[:20]:
        block = f"[Page {ch['page_id']} | Chunk {ch['index']}]\n{ch['text']}\n---\n"
        if len(evidence_section) + len(block) < max_chars * 0.3:
            evidence_section += block
    context_parts.append(evidence_section)

    return "\n".join(context_parts)


# ============================
# STYLES
# ============================

def get_enhanced_styles():
    """Comprehensive style system with professional theming"""
    styles = getSampleStyleSheet()

    PRIMARY_COLOR = colors.HexColor("#1a365d")
    SECONDARY_COLOR = colors.HexColor("#2c5282")
    ACCENT_COLOR = colors.HexColor("#3182ce")
    LIGHT_BG = colors.HexColor("#ebf8ff")
    DARK_TEXT = colors.HexColor("#1a202c")
    GRAY_TEXT = colors.HexColor("#4a5568")

    def add_style(name, **kwargs):
        if name in styles:
            for key, value in kwargs.items():
                setattr(styles[name], key, value)
        else:
            styles.add(ParagraphStyle(name=name, **kwargs))

    add_style('CoverTitle', fontSize=36, leading=44, textColor=PRIMARY_COLOR, 
              alignment=TA_CENTER, spaceAfter=30, fontName='Helvetica-Bold')
    add_style('CoverSubtitle', fontSize=18, leading=24, textColor=SECONDARY_COLOR,
              alignment=TA_CENTER, spaceAfter=20, fontName='Helvetica')
    add_style('CoverMeta', fontSize=12, leading=16, textColor=GRAY_TEXT,
              alignment=TA_CENTER, spaceAfter=12, fontName='Helvetica')
    add_style('ReportTitle', fontSize=28, leading=34, textColor=PRIMARY_COLOR,
              spaceAfter=24, fontName='Helvetica-Bold', borderPadding=10)
    add_style('SectionHeader', fontSize=20, leading=26, textColor=SECONDARY_COLOR,
              spaceAfter=16, spaceBefore=20, fontName='Helvetica-Bold',
              borderColor=ACCENT_COLOR, borderWidth=2, borderPadding=5, leftIndent=0)
    add_style('SubSectionHeader', fontSize=16, leading=22, textColor=ACCENT_COLOR,
              spaceAfter=12, spaceBefore=14, fontName='Helvetica-Bold')
    add_style('BodyText', fontSize=11, leading=16, textColor=DARK_TEXT,
              alignment=TA_JUSTIFY, spaceAfter=10, fontName='Helvetica', firstLineIndent=20)
    add_style('BulletPoint', fontSize=11, leading=16, textColor=DARK_TEXT,
              leftIndent=30, spaceAfter=6, bulletIndent=15,
              bulletFontName='Helvetica-Bold', bulletColor=ACCENT_COLOR)
    add_style('QuoteStyle', fontSize=10, leading=15, textColor=GRAY_TEXT,
              leftIndent=40, rightIndent=40, spaceAfter=12, fontName='Helvetica-Oblique',
              borderColor=LIGHT_BG, borderWidth=1, borderPadding=10, backColor=LIGHT_BG)
    add_style('TableHeader', fontSize=10, leading=14, textColor=colors.white,
              alignment=TA_CENTER, fontName='Helvetica-Bold')
    add_style('TableCell', fontSize=9, leading=13, textColor=DARK_TEXT,
              alignment=TA_LEFT, fontName='Helvetica')
    add_style('KeyInsight', fontSize=12, leading=18, textColor=PRIMARY_COLOR,
              alignment=TA_LEFT, fontName='Helvetica-Bold', borderColor=ACCENT_COLOR,
              borderWidth=3, borderPadding=15, backColor=LIGHT_BG, spaceAfter=20, spaceBefore=10)

    return styles


# ============================
# VISUALIZATIONS
# ============================

def create_enhanced_bar_chart(data: List[float], labels: List[str], title: str = ""):
    """Create professional bar chart"""
    drawing = Drawing(500, 250)
    chart = VerticalBarChart()
    chart.x, chart.y = 60, 60
    chart.height, chart.width = 150, 400
    chart.data = [data]
    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.fontSize = 10
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(data) * 1.2 if data else 100
    chart.valueAxis.labels.fontSize = 9
    chart.bars[0].fillColor = colors.HexColor("#3182ce")
    chart.bars[0].strokeColor = colors.HexColor("#2c5282")
    chart.bars[0].strokeWidth = 1
    if title:
        drawing.add(String(250, 230, title, fontSize=12,
                          fillColor=colors.HexColor("#1a365d"),
                          textAnchor="middle", fontName="Helvetica-Bold"))
    drawing.add(chart)
    return drawing


def create_dashboard_charts(stats: Dict[str, Any]):
    """Create dashboard with charts"""
    elements = []
    stat_labels = ["Pages", "Chunks", "Recent", "Avg Chunks/Page"]
    stat_values = [stats.get("total_pages", 0), stats.get("total_chunks", 0),
                   stats.get("recent_pages", 0), stats.get("avg_chunks_per_page", 0)]
    elements.append(create_enhanced_bar_chart(stat_values, stat_labels, "Database Statistics"))
    elements.append(Spacer(1, 20))
    return elements


def create_stat_card(label: str, value: str, trend: str = None):
    """Create statistic card"""
    data = [[Paragraph(f"<b>{value}</b>", ParagraphStyle(
        name='StatValue', fontSize=24, textColor=colors.HexColor("#1a365d"),
        alignment=TA_CENTER, fontName='Helvetica-Bold'))],
            [Paragraph(label, ParagraphStyle(
        name='StatLabel', fontSize=10, textColor=colors.HexColor("#4a5568"),
        alignment=TA_CENTER, fontName='Helvetica'))]]

    if trend:
        trend_color = colors.HexColor("#38a169") if "+" in trend else colors.HexColor("#e53e3e")
        data.append([Paragraph(trend, ParagraphStyle(
            name='StatTrend', fontSize=9, textColor=trend_color,
            alignment=TA_CENTER, fontName='Helvetica'))])

    table = Table(data, colWidths=[120])
    table.setStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7fafc")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 15),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ])
    return table


def create_enhanced_table(data: List[List[str]], header: List[str] = None,
                         col_widths: List[int] = None, style_type: str = "default"):
    """Create professionally styled tables"""
    styles = get_enhanced_styles()
    table_data = []
    if header:
        table_data.append([Paragraph(h, styles['TableHeader']) for h in header])
    for row in data:
        table_data.append([Paragraph(str(cell), styles['TableCell']) for cell in row])

    if not col_widths and table_data:
        available_width = 450
        num_cols = len(table_data[0])
        col_widths = [available_width // num_cols] * num_cols

    table = Table(table_data, colWidths=col_widths, repeatRows=1 if header else 0)

    style_configs = {
        "default": [
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5282")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ],
        "striped": [
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ],
    }
    table.setStyle(TableStyle(style_configs.get(style_type, style_configs["default"])))
    return table


def create_highlight_box(text: str, style_type: str = "info"):
    """Create styled highlight boxes"""
    colors_map = {
        "info": (colors.HexColor("#ebf8ff"), colors.HexColor("#3182ce")),
        "success": (colors.HexColor("#f0fff4"), colors.HexColor("#38a169")),
        "warning": (colors.HexColor("#fffaf0"), colors.HexColor("#d69e2e")),
        "danger": (colors.HexColor("#fff5f5"), colors.HexColor("#e53e3e"))
    }
    bg_color, border_color = colors_map.get(style_type, colors_map["info"])
    styles = get_enhanced_styles()
    return Paragraph(text, styles['KeyInsight'])


# ============================
# PDF GENERATION (FIXED)
# ============================

class PageNumCanvas(canvas.Canvas):
    """Custom canvas for page numbers and headers"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        self.report_title = kwargs.get('report_title', 'AI Research Report')

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.line(50, 40, 545, 40)
        self.setFillColor(colors.HexColor("#4a5568"))
        self.setFont("Helvetica", 9)
        self.drawRightString(545, 25, f"Page {self._pageNumber} of {page_count}")
        self.setFont("Helvetica-Oblique", 8)
        self.drawString(50, 25, self.report_title)
        self.setFillColor(colors.HexColor("#2c5282"))
        self.setFont("Helvetica-Bold", 10)
        self.drawString(50, 800, "AI Research Report")
        self.drawRightString(545, 800, datetime.now().strftime("%B %d, %Y"))
        self.line(50, 795, 545, 795)


def generate_enhanced_pdf(text: str, filename: str = "enhanced_report.pdf",
                         topic: str = "", stats: Dict = None, pages_data: List[Dict] = None):
    """Generate production-quality PDF with text sanitization"""

    # CRITICAL FIX: Sanitize ALL text before PDF generation
    text = clean_markdown_for_pdf(text)

    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=50,
                           leftMargin=50, topMargin=80, bottomMargin=60)
    styles = get_enhanced_styles()
    story = []

    # Cover Page
    story.append(Spacer(1, 100))
    story.append(Paragraph(sanitize_text_for_pdf("AI Research Report"), styles['CoverTitle']))
    story.append(Spacer(1, 20))
    story.append(Paragraph(sanitize_text_for_pdf(f"Topic: {topic}"), styles['CoverSubtitle']))
    story.append(Spacer(1, 40))

    meta_text = sanitize_text_for_pdf(f"""<b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %H:%M')}<br/>
    <b>System:</b> AI Research Assistant<br/>
    <b>Classification:</b> Internal Research Document""")
    story.append(Paragraph(meta_text, styles['CoverMeta']))
    story.append(Spacer(1, 60))

    if stats:
        story.append(Paragraph("Document Overview", styles['SubSectionHeader']))
        overview_data = [
            create_stat_card("Total Pages", str(stats.get("total_pages", 0))),
            create_stat_card("Data Chunks", str(stats.get("total_chunks", 0))),
            create_stat_card("Content Sources", str(stats.get("recent_pages", 0)))
        ]
        story.append(Table([overview_data], colWidths=[130, 130, 130]))
    story.append(PageBreak())

    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['SectionHeader']))
    story.append(Spacer(1, 10))

    lines = text.split("\n")
    summary_text = []
    i = 0
    while i < len(lines) and not lines[i].strip().startswith("#"):
        if lines[i].strip():
            summary_text.append(lines[i].strip())
        i += 1

    if summary_text:
        insight_text = sanitize_text_for_pdf("<b>Key Finding:</b> " + " ".join(summary_text[:3]))
        story.append(create_highlight_box(insight_text, "info"))
    story.append(Spacer(1, 20))

    # Dashboard
    if stats:
        story.append(Paragraph("Data Overview", styles['SectionHeader']))
        story.append(Spacer(1, 15))
        for elem in create_dashboard_charts(stats):
            story.append(elem)
        story.append(Spacer(1, 30))

        if pages_data:
            story.append(Paragraph("Source Pages", styles['SubSectionHeader']))
            pages_table_data = []
            for p in pages_data[:10]:
                title = sanitize_text_for_pdf(p['title'][:40])
                url = sanitize_text_for_pdf(p['url'][:50])
                date = sanitize_text_for_pdf(p['created_at'][:10])
                pages_table_data.append([title, url, date])

            story.append(create_enhanced_table(
                pages_table_data,
                header=["Title", "URL", "Date"],
                col_widths=[150, 200, 100],
                style_type="striped"
            ))
        story.append(PageBreak())

    # Main Content
    current_section = []
    while i < len(lines):
        line = lines[i]
        line = sanitize_text_for_pdf(line)

        if line.strip().startswith("# ") and current_section:
            if len(current_section) > 10:
                story.append(PageBreak())
            for item in current_section:
                story.append(item)
            current_section = []

        if line.strip().startswith("# "):
            current_section.append(Paragraph(line.strip()[2:], styles['ReportTitle']))
            current_section.append(Spacer(1, 10))
        elif line.strip().startswith("## "):
            current_section.append(Paragraph(line.strip()[3:], styles['SectionHeader']))
            current_section.append(Spacer(1, 8))
        elif line.strip().startswith("### "):
            current_section.append(Paragraph(line.strip()[4:], styles['SubSectionHeader']))
            current_section.append(Spacer(1, 6))
        elif line.strip().startswith("- ") or line.strip().startswith("* "):
            bullet_text = line.strip()[2:]
            bullet_text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", bullet_text)
            bullet_text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", bullet_text)
            current_section.append(Paragraph(f"• {bullet_text}", styles['BulletPoint']))
        elif re.match(r"^\d+\.\s", line.strip()):
            num_text = re.sub(r"^\d+\.\s", "", line.strip())
            num_text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", num_text)
            num_text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", num_text)
            current_section.append(Paragraph(num_text, styles['BulletPoint']))
        elif "|" in line and line.strip():
            table_lines = []
            while i < len(lines) and "|" in lines[i]:
                table_lines.append(sanitize_text_for_pdf(lines[i]))
                i += 1
            table_data = parse_enhanced_table(table_lines)
            if table_data:
                clean_table_data = [[sanitize_text_for_pdf(str(cell)) for cell in row] for row in table_data]
                current_section.append(create_enhanced_table(
                    clean_table_data[1:] if len(clean_table_data) > 1 else clean_table_data,
                    header=clean_table_data[0] if clean_table_data else None,
                    style_type="striped"
                ))
                current_section.append(Spacer(1, 12))
            continue
        elif line.strip().startswith("> "):
            current_section.append(Paragraph(line.strip()[2:], styles['QuoteStyle']))
        elif line.strip() in ["---", "***"]:
            current_section.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
            current_section.append(Spacer(1, 10))
        elif line.strip():
            para_text = line.strip()
            para_text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", para_text)
            para_text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", para_text)
            para_text = re.sub(r"`([^`]+)`", r"<font face='Courier'>\1</font>", para_text)
            current_section.append(Paragraph(para_text, styles['BodyText']))
        i += 1

    for item in current_section:
        story.append(item)

    # Appendix
    story.append(PageBreak())
    story.append(Paragraph("Appendix", styles['SectionHeader']))
    story.append(Spacer(1, 15))

    appendix_text = sanitize_text_for_pdf(f"""<b>Document Information</b><br/>
    This report was generated automatically by the AI Research Assistant system.<br/>
    Generation timestamp: {datetime.now().isoformat()}<br/>
    Data source: {DB_PATH}<br/><br/>
    <b>Methodology</b><br/>
    Content is synthesized from verified research database entries using
    retrieval-augmented generation techniques. Data is stored in SQLite with
    deduplication based on content hashing.<br/><br/>
    <b>Disclaimer</b><br/>
    This document is for research purposes only. Verify critical information
    against primary sources before making decisions.""")
    story.append(Paragraph(appendix_text, styles['BodyText']))

    doc.build(story, canvasmaker=lambda *args, **kwargs: PageNumCanvas(*args, report_title=topic, **kwargs))
    return filename


def parse_enhanced_table(lines):
    """Parse markdown tables"""
    table_data = []
    for line in lines:
        if re.match(r"^\s*\|?[\-:|\s]+\|?\s*$", line):
            continue
        if "|" in line:
            cells = [cell.strip() for cell in line.split("|") if cell.strip()]
            if cells:
                table_data.append(cells)
    return table_data


# ============================
# PRODUCTION WRITER AGENT
# ============================

class EnhancedWriterAgent:
    """Production-ready writer with text sanitization"""

    def __init__(self):
        self.report_history = []

    def run(self, topic: str, options: Dict[str, Any] = None):
        """
        Generate production-quality report with proper encoding.

        Options:
            - detail_level: "brief", "standard", "comprehensive" (default: "comprehensive")
            - include_charts: bool (default: True)
            - search_query: str (filter pages by content)
            - feedback: str (critic evaluation comments for revision)
        """
        options = options or {}
        detail_level = options.get("detail_level", "comprehensive")
        include_charts = options.get("include_charts", True)
        search_query = options.get("search_query", None)
        feedback = options.get("feedback", None)

        # Get data
        if search_query:
            pages = search_content(search_query, limit=50)
        else:
            pages = get_pages(limit=100)

        if not pages:
            return {"error": "No data available for report generation. Run analyzer first to populate database."}

        # Get statistics
        stats = get_statistics() if include_charts else None

        # Retrieve chunks
        page_ids = [p["id"] for p in pages]
        chunks_per_page = {"brief": 3, "standard": 5, "comprehensive": 10}.get(detail_level, 10)
        chunks = get_chunks(page_ids, limit_per_page=chunks_per_page)

        # Build rich context
        context = build_enhanced_context(pages, chunks)

        # Generate report with production prompt
        prompt = self._build_production_prompt(topic, context, detail_level, feedback)

        # CRITICAL: Get report from LLM
        report = call_llm(prompt, mode="long")

        # CRITICAL: Sanitize the LLM output before PDF generation
        report = clean_markdown_for_pdf(report)

        # Generate PDF
        pdf_filename = f"report_{topic.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        pdf_path = generate_enhanced_pdf(report, filename=pdf_filename, topic=topic, stats=stats, pages_data=pages)

        # Store in history
        self.report_history.append({
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "pages": len(pages),
            "chunks": len(chunks),
            "pdf_path": pdf_path
        })

        return {
            "report": report,
            "pdf": pdf_path,
            "stats": stats,
            "metadata": {
                "pages_processed": len(pages),
                "chunks_included": len(chunks),
                "detail_level": detail_level,
                "generation_time": datetime.now().isoformat()
            }
        }

    def _build_production_prompt(self, topic: str, context: str, detail_level: str, feedback: str = None) -> str:
        """Build production-ready prompt with strict formatting rules"""

        detail_instructions = {
            "brief": """Create a concise 2-3 page executive summary.
Focus on key findings only.
Maximum 2-3 sections with brief bullet points.""",
            "standard": """Create a standard 5-7 page report.
Include introduction, 3-4 main sections, and conclusion.
Use tables for comparisons.""",
            "comprehensive": """Create a comprehensive 10+ page detailed report.
Include: Executive Summary, Introduction, 5-7 Detailed Sections,
Data Analysis, Case Studies, Recommendations, and Conclusion.
Use multiple tables, structured analysis, and detailed explanations."""
        }

        prompt = f"""Write a professional structured research report on: {topic}

{detail_instructions.get(detail_level, detail_instructions["comprehensive"])}

FORMATTING REQUIREMENTS:
- Use markdown headers (# for title, ## for sections, ### for subsections)
- Include at least 2-3 data tables with comparisons
- Use bullet points (- item) for lists
- Include blockquotes (>) for important insights
- Add horizontal rules (---) between major sections
- Bold (**text**) key terms and statistics
- Italicize (*text*) emphasis points

STRICT CHARACTER RULES - DO NOT VIOLATE:
1. Use ONLY standard ASCII hyphens (-) for ranges and compound words
   CORRECT: "15-30%", "state-of-the-art", "AI-driven", "expert-level"
   WRONG: "15I30%", "state-of-the-art" with "n", "AIndriven", "expertnlevel"

2. Use proper spacing around operators
   CORRECT: "AUC = 0.98", "AUROC = 0.82"
   WRONG: "AUC =0.98", "AUROC =0.82"

3. Use tilde (~) for approximations
   CORRECT: "~12%", "approximately 12%"
   AVOID: "≈12%" (symbol may not render in PDF)

4. Use proper spacing after commas
   CORRECT: "genomics, imaging, and notes"
   WRONG: "genomics,imaging,and notes"

5. NO CJK characters, emojis, or special Unicode symbols

6. Use proper spacing between words in compounds
   CORRECT: "human-in-the-loop", "non-representative", "re-identification"
   WRONG: "humanninnthenloop", "nonnrepresentative", "renidentification"

CONTENT GUIDELINES:
- Start with an executive summary (not a header)
- Provide specific data points and metrics
- Include comparative analysis where relevant
- Add actionable recommendations section
- Cite confidence levels for key claims
- Address potential limitations or caveats

DATA CONTEXT:
{context}"""

        if feedback:
            prompt += f"""

CRITICAL CRITIC FEEDBACK FROM PREVIOUS DRAFT EVALUATION:
{feedback}
Please REVISE the report to address this feedback, correct any errors, resolve contradictions, and improve accuracy where requested."""

        prompt += "\n\nGenerate the complete report now following ALL formatting rules above."
        return prompt

    def get_history(self):
        """Return generation history"""
        return self.report_history



# ============================
# BUILT-IN TEST SUITE
# ============================

def run_tests(verbose: bool = True) -> dict:
    """
    Run comprehensive test suite for sanitization functions.
    Returns dict with test results.
    """
    import re

    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "tests": []
    }

    # Test cases: (input, expected, description, category)
    test_cases = [
        # === BASIC COMPOUNDS (n → -) ===
        ("AIndriven", "AI-driven", "AI compound", "basic"),
        ("expertnlevel", "expert-level", "Expert compound", "basic"),
        ("humanninnthenloop", "human-in-the-loop", "Multi-part compound", "basic"),
        ("nonnrepresentative", "non-representative", "Non- prefix", "basic"),
        ("renidentification", "re-identification", "Re- prefix", "basic"),

        # === TIME & DURATION ===
        ("30nday", "30-day", "30-day compound", "time"),
        ("realntime", "real-time", "Real-time", "time"),
        ("earlynwarning", "early-warning", "Early-warning", "time"),
        ("timenlines", "timelines", "Timelines (no hyphen)", "time"),

        # === MEDICAL/SCIENTIFIC ===
        ("leadnidentification", "lead-identification", "Lead identification", "medical"),
        ("multinomics", "multi-omics", "Multi-omics", "medical"),
        ("diseasenrelevant", "disease-relevant", "Disease-relevant", "medical"),
        ("preclinicaln", "preclinical-", "Preclinical prefix", "medical"),
        ("postnmarket", "post-market", "Post-market", "medical"),
        ("vitalnsignnbased", "vital-sign-based", "Vital-sign-based", "medical"),
        ("typendiabetes", "type-1-diabetes", "Type 1 diabetes", "medical"),

        # === TECHNICAL/IT ===
        ("virtualnscreening", "virtual-screening", "Virtual screening", "tech"),
        ("blacknbox", "black-box", "Black box", "tech"),
        ("usernfriendly", "user-friendly", "User-friendly", "tech"),

        # === RESEARCH/ACADEMIC ===
        ("literaturenbased", "literature-based", "Literature-based", "academic"),
        ("spectrumnbias", "spectrum-bias", "Spectrum bias", "academic"),

        # === SPACING & OPERATORS ===
        ("AUC =0.98", "AUC = 0.98", "Spacing after =", "spacing"),
        ("sensitivity =0.94", "sensitivity = 0.94", "Spacing in sensitivity", "spacing"),
        ("0.78vs.0.52", "0.78 vs. 0.52", "Spacing around vs.", "spacing"),
        ("0.82vs.0.76", "0.82 vs. 0.76", "Spacing vs with decimals", "spacing"),
        ("p <0.001", "p < 0.001", "Spacing after <", "spacing"),
        ("genomics,imaging", "genomics, imaging", "Comma spacing", "spacing"),

        # === UNICODE & SYMBOLS ===
        ("≈12%", "~12%", "Approx symbol", "unicode"),
        ("≃15%", "~15%", "Approx symbol variant", "unicode"),
        ("∼20%", "~20%", "Tilde variant", "unicode"),

        # === CJK & ARTIFACTS ===
        ("国", "", "CJK character 国", "cjk"),
        ("〡", "", "CJK character 〡", "cjk"),
        ("国〡", "", "Multiple CJK chars", "cjk"),
        ("AI国driven", "AIdriven", "CJK in middle", "cjk"),

        # === MODEL NAMES & TITLES ===
        ("ALF Research Report", "AI Research Report", "Title correction", "titles"),
        ("Qwen330BIA3B", "Qwen3-30B-A3B", "Qwen model name", "models"),
        ("GPTIOSS", "GPT-OSS", "GPT model name", "models"),

        # === COMPLEX/EDGE CASES ===
        ("AIndriven expertnlevel human-in-the-loop", "AI-driven expert-level human-in-the-loop", "Multiple compounds", "complex"),
        ("precision =0.78vs.0.52 nonnrepresentative", "precision = 0.78 vs. 0.52 non-representative", "Mixed issues", "complex"),
        ("30nday realntime earlynwarning", "30-day real-time early-warning", "Multiple time compounds", "complex"),
        ("timenlines leadnidentification", "timelines lead-identification", "Mixed timeline/lead", "complex"),
        ("postnmarket preclinicaln blacknbox", "post-market preclinical- black-box", "Multiple prefixes", "complex"),
        ("multinomics diseasenrelevant virtualnscreening", "multi-omics disease-relevant virtual-screening", "Scientific triple", "complex"),
        ("vitalnsignnbased 30nday readmission", "vital-sign-based 30-day readmission", "Medical + time", "complex"),

        # === WHITESPACE NORMALIZATION ===
        ("AI-driven    expert-level", "AI-driven expert-level", "Multiple spaces", "whitespace"),
        ("AI-driven\t\texpert-level", "AI-driven expert-level", "Tab characters", "whitespace"),
        ("  leading spaces", "leading spaces", "Leading spaces", "whitespace"),
        ("trailing spaces  ", "trailing spaces", "Trailing spaces", "whitespace"),

        # === INVISIBLE CHARACTERS ===
        ("AI\u200Bdriven", "AIdriven", "Zero-width space", "invisible"),
        ("expert\ufefflevel", "expertlevel", "BOM character", "invisible"),

        # === PRESERVATION (should NOT change) ===
        ("AI-driven", "AI-driven", "Already correct", "preserve"),
        ("expert-level", "expert-level", "Already correct 2", "preserve"),
        ("human-in-the-loop", "human-in-the-loop", "Already correct 3", "preserve"),
        ("non-representative", "non-representative", "Already correct 4", "preserve"),
        ("re-identification", "re-identification", "Already correct 5", "preserve"),
        ("30-day", "30-day", "Already correct 6", "preserve"),
        ("real-time", "real-time", "Already correct 7", "preserve"),
        ("~12%", "~12%", "Tilde already correct", "preserve"),
        ("p = 0.05", "p = 0.05", "Spacing already correct", "preserve"),

        # === SENTENCE CONTEXT ===
        ("This is AIndriven technology", "This is AI-driven technology", "In sentence context", "context"),
        ("We use expertnlevel analysis", "We use expert-level analysis", "In sentence 2", "context"),
        ("Results: precision =0.78vs.0.52", "Results: precision = 0.78 vs. 0.52", "In results context", "context"),
        ("Study of 30nday outcomes", "Study of 30-day outcomes", "In study context", "context"),

        # === TABLE-LIKE CONTENT ===
        ("AUC =0.98 sensitivity =0.94", "AUC = 0.98 sensitivity = 0.94", "Multiple metrics", "table"),
        ("0.94vs.0.82 0.88vs.0.76", "0.94 vs. 0.82 0.88 vs. 0.76", "Multiple vs comparisons", "table"),

        # === BOUNDARY CASES ===
        ("", "", "Empty string", "boundary"),
        ("n", "n", "Single n", "boundary"),
        ("nn", "-", "Double n", "boundary"),
        ("nnn", "-n", "Triple n", "boundary"),
        ("AI", "AI", "Just AI", "boundary"),
        ("nAI", "nAI", "n before AI", "boundary"),
    ]

    if verbose:
        print("\n" + "=" * 70)
        print("RUNNING SANITIZATION TESTS")
        print("=" * 70)

    categories = {}

    for input_text, expected, description, category in test_cases:
        result = sanitize_text_for_pdf(input_text)
        passed = result == expected

        results["total"] += 1
        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1

        # Track by category
        if category not in categories:
            categories[category] = {"total": 0, "passed": 0, "failed": 0, "tests": []}
        categories[category]["total"] += 1
        if passed:
            categories[category]["passed"] += 1
        else:
            categories[category]["failed"] += 1

        test_result = {
            "description": description,
            "input": input_text,
            "expected": expected,
            "got": result,
            "passed": passed,
            "category": category
        }
        results["tests"].append(test_result)
        categories[category]["tests"].append(test_result)

        if verbose:
            status = "✅" if passed else "❌"
            print(f"{status} [{category:12}] {description}")
            if not passed:
                print(f"      Input:    '{input_text}'")
                print(f"      Expected: '{expected}'")
                print(f"      Got:      '{result}'")

    if verbose:
        print("\n" + "=" * 70)
        print("CATEGORY SUMMARY")
        print("=" * 70)
        for cat_name, cat_data in sorted(categories.items()):
            status = "✅" if cat_data["failed"] == 0 else "⚠️ " if cat_data["passed"] > 0 else "❌"
            print(f"{status} {cat_name:15}: {cat_data['passed']}/{cat_data['total']} passed")

        print("\n" + "=" * 70)
        print(f"OVERALL: {results['passed']}/{results['total']} tests passed")
        if results['failed'] == 0:
            print("✅ ALL TESTS PASSED!")
        else:
            print(f"❌ {results['failed']} tests failed")
        print("=" * 70)

    results["categories"] = categories
    return results


def validate_report_text(text: str, verbose: bool = False) -> dict:
    """
    Validate generated report text for encoding artifacts.
    Returns dict with found issues.
    """
    issues = []
    warnings = []

    # Critical artifacts that must not be in production
    critical_patterns = [
        ('AIndriven', 'AI-driven', 'AI compound'),
        ('expertnlevel', 'expert-level', 'Expert compound'),
        ('humanninnthenloop', 'human-in-the-loop', 'Human-in-the-loop'),
        ('nonnrepresentative', 'non-representative', 'Non-representative'),
        ('renidentification', 're-identification', 'Re-identification'),
        ('realntime', 'real-time', 'Real-time'),
        ('virtualnscreening', 'virtual-screening', 'Virtual screening'),
        ('earlynwarning', 'early-warning', 'Early-warning'),
        ('30nday', '30-day', '30-day'),
        ('blacknbox', 'black-box', 'Black-box'),
        ('usernfriendly', 'user-friendly', 'User-friendly'),
        ('postnmarket', 'post-market', 'Post-market'),
        ('multinomics', 'multi-omics', 'Multi-omics'),
        ('diseasenrelevant', 'disease-relevant', 'Disease-relevant'),
        ('vitalnsignnbased', 'vital-sign-based', 'Vital-sign-based'),
        ('literaturenbased', 'literature-based', 'Literature-based'),
        ('timenlines', 'timelines', 'Timelines'),
        ('leadnidentification', 'lead-identification', 'Lead identification'),
        ('preclinicaln', 'preclinical-', 'Preclinical'),
    ]

    # Spacing issues
    spacing_patterns = [
        (r'=[0-9]', '=0.', 'Missing space after ='),
        (r'[0-9]vs\.', '0.78vs.', 'Missing space around vs.'),
        (r',[a-zA-Z]', 'genomics,imaging', 'Missing space after comma'),
    ]

    # Unicode/CJK issues
    unicode_patterns = [
        ('国', 'CJK character 国'),
        ('〡', 'CJK character 〡'),
        ('≈', 'Unicode approx (should be ~)'),
        ('≃', 'Unicode approx variant'),
    ]

    # Title issues
    title_patterns = [
        ('ALF Research Report', 'AI Research Report', 'Title typo'),
        ('Qwen330BIA3B', 'Qwen3-30B-A3B', 'Model name typo'),
        ('GPTIOSS', 'GPT-OSS', 'Model name typo'),
    ]

    # Check critical patterns
    for bad, good, desc in critical_patterns:
        if bad in text:
            issues.append({
                'severity': 'ERROR',
                'type': 'compound',
                'found': bad,
                'should_be': good,
                'description': desc
            })

    # Check spacing with regex
    import re
    for pattern, example, desc in spacing_patterns:
        if re.search(pattern, text):
            issues.append({
                'severity': 'ERROR',
                'type': 'spacing',
                'pattern': pattern,
                'example': example,
                'description': desc
            })

    # Check unicode/CJK
    for bad, desc in unicode_patterns:
        if bad in text:
            issues.append({
                'severity': 'ERROR',
                'type': 'unicode',
                'found': bad,
                'description': desc
            })

    # Check titles (warnings)
    for bad, good, desc in title_patterns:
        if bad in text:
            warnings.append({
                'severity': 'WARNING',
                'type': 'title',
                'found': bad,
                'should_be': good,
                'description': desc
            })

    result = {
        'valid': len(issues) == 0,
        'issue_count': len(issues),
        'warning_count': len(warnings),
        'issues': issues,
        'warnings': warnings,
        'text_sample': text[:500] if text else ""
    }

    if verbose:
        print("\n" + "=" * 70)
        print("REPORT VALIDATION")
        print("=" * 70)

        if issues:
            print(f"\n❌ Found {len(issues)} critical issues:")
            for issue in issues[:10]:
                print(f"   [{issue['severity']}] {issue['description']}")
                if 'found' in issue:
                    print(f"      Found: '{issue['found']}' → Should be: '{issue.get('should_be', 'fixed')}'")
        else:
            print("\n✅ No critical issues found")

        if warnings:
            print(f"\n⚠️  Found {len(warnings)} warnings:")
            for warning in warnings[:5]:
                print(f"   [{warning['severity']}] {warning['description']}: '{warning['found']}'")

        print(f"\n{'✅ VALID' if result['valid'] else '❌ INVALID'}: Report text validation")
        print("=" * 70)

    return result


# Command-line test runner
if __name__ == "__main__":
    import sys

    print("=" * 70)
    print("WRITER2.PY SELF-TEST")
    print("=" * 70)

    # Run unit tests
    test_results = run_tests(verbose=True)

    # Exit with appropriate code
    sys.exit(0 if test_results['failed'] == 0 else 1)


# ============================
# BACKWARD COMPATIBILITY
# ============================

def generate_pdf(text, filename="report.pdf"):
    """Backward compatible wrapper"""
    return generate_enhanced_pdf(text, filename, topic="Research Report")


class WriterAgent:
    """Backward compatible wrapper"""
    def __init__(self):
        self._enhanced = EnhancedWriterAgent()

    def run(self, topic: str):
        return self._enhanced.run(topic, options={"detail_level": "standard"})


# Export main classes
__all__ = [
    'EnhancedWriterAgent',
    'WriterAgent',
    'generate_enhanced_pdf',
    'generate_pdf',
    'get_enhanced_styles',
    'create_enhanced_bar_chart',
    'create_enhanced_table',
    'get_pages',
    'get_chunks',
    'get_statistics',
    'search_content',
    'sanitize_text_for_pdf',
    'clean_markdown_for_pdf',
    'run_tests',
    'validate_report_text'
]
