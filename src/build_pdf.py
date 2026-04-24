"""
Customer Support Operations — Executive Summary PDF Generator

Builds a 1-page executive summary PDF combining the Power BI Page 1
screenshot with key findings and recommendations.

Run from project root:
    python src/build_pdf.py
"""

from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# --- Paths ---
ROOT = Path(__file__).resolve().parent.parent
SCREENSHOT = ROOT / 'outputs' / 'screenshots' / '01_executive_summary.png'
OUTPUT_PDF = ROOT / 'outputs' / 'executive_summary.pdf'

# --- Color palette (matching dashboard Executive theme) ---
NAVY = HexColor('#1F3A5F')
TEAL = HexColor('#2E86AB')
DARK_GRAY = HexColor('#333333')
LIGHT_GRAY = HexColor('#F4F4F4')

# --- Document setup ---
doc = SimpleDocTemplate(
    str(OUTPUT_PDF),
    pagesize=A4,
    leftMargin=1.5*cm, rightMargin=1.5*cm,
    topMargin=1.5*cm, bottomMargin=1.5*cm,
    title='Customer Support Operations — Executive Summary',
    author='MIS / Operations Analytics'
)

# --- Styles ---
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'CustomTitle', parent=styles['Title'],
    fontSize=20, leading=24, textColor=NAVY,
    alignment=TA_LEFT, spaceAfter=4
)

subtitle_style = ParagraphStyle(
    'CustomSubtitle', parent=styles['Normal'],
    fontSize=10, textColor=DARK_GRAY,
    alignment=TA_LEFT, spaceAfter=12
)

section_style = ParagraphStyle(
    'Section', parent=styles['Heading2'],
    fontSize=12, textColor=NAVY, spaceBefore=10, spaceAfter=6,
    fontName='Helvetica-Bold'
)

body_style = ParagraphStyle(
    'Body', parent=styles['Normal'],
    fontSize=9.5, leading=13, textColor=DARK_GRAY, alignment=TA_LEFT
)

# --- Build the story ---
story = []

# Title block
story.append(Paragraph(
    'Customer Support Operations — Executive Summary', title_style
))
story.append(Paragraph(
    'Reporting period: May 29 – Jun 4, 2023  |  Total tickets: 8,469',
    subtitle_style
))

# KPI summary table
kpi_data = [
    ['SLA Compliance', 'Avg Resolution', 'Avg CSAT', 'SLA Breaches'],
    ['82.6%', '7.74 hrs', '2.99 / 5', '481 tickets'],
]

kpi_table = Table(kpi_data, colWidths=[4.5*cm]*4, rowHeights=[0.7*cm, 1*cm])
kpi_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), NAVY),
    ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('BACKGROUND', (0, 1), (-1, 1), LIGHT_GRAY),
    ('FONTSIZE', (0, 1), (-1, 1), 14),
    ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
    ('TEXTCOLOR', (0, 1), (-1, 1), NAVY),
    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
]))
story.append(kpi_table)
story.append(Spacer(1, 0.4*cm))

# Dashboard screenshot
if SCREENSHOT.exists():
    img = Image(str(SCREENSHOT), width=17*cm, height=8.5*cm)
    img.hAlign = 'CENTER'
    story.append(img)
else:
    story.append(Paragraph(
        f'<i>Dashboard screenshot not found at {SCREENSHOT}</i>', body_style
    ))

story.append(Spacer(1, 0.4*cm))

# Key findings section
story.append(Paragraph('★ Key Findings', section_style))

findings = [
    ('SLA compliance is below the typical 85% benchmark.',
     'Overall compliance is 82.6%. Notably, all 481 SLA breaches come from '
     'Critical-priority tickets (66.3% breach rate for Critical vs. 0% for '
     'High, Medium, and Low), suggesting the issue is concentrated in one '
     'priority tier rather than distributed across the board.'),

    ('Resolution times do not appear to differ by priority.',
     'Average resolution time is roughly 7.5 hours across all four priority '
     'levels. In principle, Critical tickets should resolve faster than Low, '
     'so the near-uniform distribution is worth further investigation — it '
     'may indicate that priority labels are not influencing queue ordering.'),

    ('Channel performance shows meaningful variation.',
     'Chat leads on both speed (7.5h) and satisfaction (CSAT 3.15). '
     'Social Media trails on CSAT (2.76 for Technical Issues) despite '
     'comparable resolution times, possibly because public-facing tickets '
     'feel more urgent to customers. Email · Product Inquiry shows the '
     'weakest SLA compliance at 75.4%.'),
]
for headline, detail in findings:
    story.append(Paragraph(
        f'<b>{headline}</b> {detail}', body_style
    ))
    story.append(Spacer(1, 0.2*cm))

# Recommendations
story.append(Paragraph('Recommendations', section_style))

recommendations = [
    'Investigate whether priority-based routing is functioning as intended. '
    'Average resolution time is nearly identical across all priority levels, '
    'which suggests tickets may be processed in arrival order rather than '
    'priority order. This would warrant a review of the triage workflow.',

    'Examine the Email · Product Inquiry segment more closely. It shows the '
    'lowest SLA compliance (75.4%) in the dataset. A deeper look at the root '
    'cause — whether it\'s product-knowledge gaps, escalation delays, or '
    'high query complexity — could help identify the drag factor.',

    'Study what makes Chat the top-performing channel. With 7.5h average '
    'resolution and 3.15 CSAT (highest of any channel), Chat sets the '
    'benchmark. Understanding whether this is driven by ticket type, agent '
    'specialization, or response format may yield lessons transferable to '
    'Email and Social Media.',

    'Consider whether CSAT capture can be extended to Open/Pending tickets. '
    'Currently, satisfaction data is only available for the 32.7% of tickets '
    'that closed. Adding a mid-ticket pulse survey could provide earlier '
    'feedback for tickets at risk of breaching SLA.',
]

for i, rec in enumerate(recommendations, 1):
    story.append(Paragraph(f'<b>{i}.</b> {rec}', body_style))
    story.append(Spacer(1, 0.1*cm))



# Build PDF
doc.build(story)
print(f'✓ PDF generated: {OUTPUT_PDF}')
print(f'  File size: {OUTPUT_PDF.stat().st_size / 1024:.1f} KB')