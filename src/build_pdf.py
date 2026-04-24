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
    ('SLA compliance below benchmark.',
     'Overall SLA compliance is 82.6%, 2.4 percentage points below the '
     '85% industry standard. All 481 SLA breaches are concentrated in '
     'Critical-priority tickets (66.3% breach rate for Critical vs. 0% '
     'for High, Medium, and Low).'),

    ('Priority queues are not being respected.',
     'Average resolution time is essentially flat across all four priority '
     'levels (~7.5 hours each). In a healthy support operation, Critical '
     'tickets should resolve 2–3× faster than Low. The flat distribution '
     'indicates agents are processing tickets in arrival order rather than '
     'priority order.'),

    ('Channel performance varies meaningfully.',
     'Chat delivers the strongest combination of speed (7.5h) and CSAT (3.15). '
     'Social Media has the lowest CSAT (2.76 for Technical Issues) despite '
     'comparable resolution times — public visibility likely amplifies '
     'frustration. Email · Product Inquiry shows the worst SLA compliance '
     '(75.4%) and warrants immediate review.'),
]

for headline, detail in findings:
    story.append(Paragraph(
        f'<b>{headline}</b> {detail}', body_style
    ))
    story.append(Spacer(1, 0.2*cm))

# Recommendations
story.append(Paragraph('Recommendations', section_style))

recommendations = [
    'Audit Critical-priority triage workflow. Likely root cause: manual '
    'assignment latency. Implement SLA-first routing rules with a dedicated '
    'Critical queue.',

    'Reinforce priority-based handling with agents. Update queue dashboards '
    'to surface Critical tickets first; consider time-on-ticket alerts when '
    'agents spend >2h on a Low while Critical sits unworked.',

    'Investigate Email · Product Inquiry workflow. The 75.4% compliance '
    'and below-average CSAT (2.94) suggest Tier 1 escalation friction or '
    'product-spec lookup delays.',

    'Replicate Chat success patterns. Chat\'s strong CSAT (3.15) likely '
    'reflects faster acknowledgment and shorter back-and-forth. Apply '
    'similar response templates to Email and Social Media channels.',
]

for i, rec in enumerate(recommendations, 1):
    story.append(Paragraph(f'<b>{i}.</b> {rec}', body_style))
    story.append(Spacer(1, 0.1*cm))



# Build PDF
doc.build(story)
print(f'✓ PDF generated: {OUTPUT_PDF}')
print(f'  File size: {OUTPUT_PDF.stat().st_size / 1024:.1f} KB')