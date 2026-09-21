from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether, HRFlowable
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from .config import REPORT_DIR

GREEN = colors.HexColor("#173F35")
GREEN2 = colors.HexColor("#245C4D")
ORANGE = colors.HexColor("#E88A3D")
CREAM = colors.HexColor("#F7F2E8")
PAPER = colors.HexColor("#FFFDF8")
INK = colors.HexColor("#17201D")
MUTED = colors.HexColor("#6D7A73")
LINE = colors.HexColor("#DDE4DE")
LAV = colors.HexColor("#8870D8")


def _p(text):
    return escape(str(text or "")).replace("\n", "<br/>")


def _footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 13 * mm, w - 18 * mm, 13 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 8 * mm, "EssayScorer • Writing Evaluation Report")
    canvas.drawRightString(w - 18 * mm, 8 * mm, f"Page {doc.page}")
    canvas.restoreState()


def _score_table(score):
    score_text = f"{score:.2f} / 10" if isinstance(score, (int, float)) else "Unavailable"
    if isinstance(score, (int, float)):
        width = max(0, min(100, score * 10))
        return [
            [Paragraph("<b>OVERALL SCORE</b>", ParagraphStyle("s", fontSize=9, textColor=MUTED)),
             Paragraph(f"<font size='25' color='#173F35'><b>{score_text}</b></font>", ParagraphStyle("x", alignment=TA_CENTER))],
            [Paragraph("<b>Performance scale</b>", ParagraphStyle("s2", fontSize=9, textColor=MUTED)),
             Paragraph(f"<font color='#245C4D'>{'▰' * int(width/10)}{'▱' * (10-int(width/10))}</font>", ParagraphStyle("bar", fontSize=11, alignment=TA_CENTER))]
        ]
    return [[Paragraph("<b>OVERALL SCORE</b>", ParagraphStyle("s3", fontSize=9, textColor=MUTED)), Paragraph("Unavailable")]]


def generate_report(evaluation):
    path = REPORT_DIR / f"essay_evaluation_{evaluation['id']}.pdf"
    doc = SimpleDocTemplate(
        str(path), pagesize=A4,
        rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=20 * mm,
        title="EssayScorer Writing Evaluation Report",
        author="EssayScorer",
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle("CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold",
                           fontSize=30, leading=34, textColor=GREEN, alignment=TA_LEFT, spaceAfter=8)
    sub = ParagraphStyle("CoverSub", parent=styles["BodyText"], fontSize=12, leading=18, textColor=MUTED)
    h = ParagraphStyle("Section", parent=styles["Heading2"], fontName="Helvetica-Bold",
                       fontSize=16, leading=20, textColor=GREEN, spaceBefore=8, spaceAfter=10)
    h3 = ParagraphStyle("H3", parent=styles["Heading3"], fontName="Helvetica-Bold",
                        fontSize=11, leading=14, textColor=GREEN2, spaceBefore=6, spaceAfter=6)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=9.5, leading=14, textColor=INK)
    small = ParagraphStyle("Small", parent=body, fontSize=8.5, leading=12, textColor=MUTED)
    quote = ParagraphStyle("Quote", parent=body, fontSize=10, leading=15, textColor=GREEN2,
                           leftIndent=10, borderPadding=8, backColor=colors.HexColor("#EEF5EF"))

    score = evaluation.get("predicted_score")
    analysis = evaluation.get("analysis", {}) or {}
    human = evaluation.get("humanization", {}) or {}
    topic = analysis.get("topic_relevance", {}) or {}
    generated = datetime.now().strftime("%d %B %Y • %I:%M %p")

    story = []
    # Cover
    story += [Spacer(1, 18 * mm), Paragraph("ESSAYSCORER", ParagraphStyle("eyebrow", parent=small, fontSize=9, textColor=ORANGE, tracking=2)),
              Paragraph("Writing Evaluation\nReport", title),
              Paragraph("A visual summary of your essay score, writing patterns and practical revision ideas.", sub),
              Spacer(1, 12 * mm)]

    cover_meta = Table([
        [Paragraph("Generated", small), Paragraph(generated, body)],
        [Paragraph("Evaluation", small), Paragraph(f"#{evaluation['id']}", body)],
        [Paragraph("Topic", small), Paragraph(_p(evaluation.get("topic") or "General essay"), body)],
    ], colWidths=[38 * mm, 120 * mm])
    cover_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PAPER),
        ("BOX", (0, 0), (-1, -1), .6, LINE),
        ("INNERGRID", (0, 0), (-1, -1), .3, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [cover_meta, Spacer(1, 12 * mm)]

    score_card = Table(_score_table(score), colWidths=[55 * mm, 103 * mm])
    score_card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EAF3EC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CFE0D3")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story += [score_card, Spacer(1, 9 * mm), Paragraph("“Small edits can create clearer ideas.”", quote), PageBreak()]

    # Snapshot
    story += [Paragraph("01  Writing Snapshot", h)]
    snapshot = [
        ["Words", str(analysis.get("word_count", 0)), "Sentences", str(analysis.get("sentence_count", 0))],
        ["Paragraphs", str(analysis.get("paragraph_count", 0)), "Characters", str(analysis.get("character_count", 0))],
        ["Unique words", str(analysis.get("unique_word_count", 0)), "Vocabulary richness", str(analysis.get("vocabulary_richness", 0))],
        ["Avg sentence length", str(analysis.get("avg_sentence_length", 0)), "Avg word length", str(analysis.get("avg_word_length", 0))],
    ]
    t = Table(snapshot, colWidths=[43 * mm, 36 * mm, 50 * mm, 29 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7F4EC")),
        ("GRID", (0, 0), (-1, -1), .4, LINE),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [t, Spacer(1, 7 * mm)]

    # Metric bars
    story += [Paragraph("Writing profile", h3)]
    metrics = [
        ("Vocabulary richness", float(analysis.get("vocabulary_richness", 0)), 1),
        ("Average word length", float(analysis.get("avg_word_length", 0)), 10),
        ("Long-word ratio", float(analysis.get("long_word_ratio", 0)), 1),
        ("Punctuation density", float(analysis.get("punctuation_density", 0)), 0.1),
    ]
    metric_rows = []
    for label, value, maxv in metrics:
        pct = max(0, min(100, value / maxv * 100))
        metric_rows.append([Paragraph(_p(label), small), Paragraph(f"<b>{value:.3f}</b>", body), Paragraph("■" * max(1, int(pct / 10)), ParagraphStyle("bars", textColor=GREEN2, fontSize=8))])
    mt = Table(metric_rows, colWidths=[57 * mm, 28 * mm, 73 * mm])
    mt.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), .3, LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("PADDING", (0, 0), (-1, -1), 6)]))
    story += [mt, Spacer(1, 7 * mm)]

    if topic.get("available"):
        story += [Paragraph("Topic relevance", h3), Paragraph(f"Topic overlap signal: <b>{topic.get('score', 0)}%</b>", body), Spacer(1, 5 * mm)]
    else:
        story += [Paragraph("Topic relevance", h3), Paragraph("No topic was supplied for this evaluation.", small), Spacer(1, 5 * mm)]

    story += [Paragraph("Model information", h3)]
    model_rows = [
        ["Algorithm", "Linear Regression"],
        ["Feature pipeline", "TF-IDF + 15 linguistic features"],
        ["Primary metric", "RMSE"],
        ["Additional metrics", "MAE, R²"],
        ["Displayed score", "1–10 normalized from training score scale"],
    ]
    tm = Table(model_rows, colWidths=[55 * mm, 103 * mm])
    tm.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF5EF")), ("GRID", (0, 0), (-1, -1), .4, LINE), ("PADDING", (0, 0), (-1, -1), 7), ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold")]))
    story += [tm, PageBreak()]

    # Humanization / generated revision
    story += [Paragraph("02  Natural-Writing Revision", h)]
    story += [Paragraph("Generated revision", h3)]
    story += [Paragraph(_p(human.get("improved", evaluation.get("essay", ""))), body), Spacer(1, 7 * mm)]
    story += [Paragraph("Revision notes", h3)]
    suggestions = human.get("suggestions", [])
    if suggestions:
        rows = [[Paragraph("Type", small), Paragraph("Suggestion", small)]]
        for item in suggestions:
            rows.append([Paragraph(_p(item.get("type", "Writing")), body), Paragraph(_p(item.get("suggestion", "")), body)])
        st = Table(rows, colWidths=[42 * mm, 116 * mm], repeatRows=1)
        st.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F3EBDD")),
            ("GRID", (0, 0), (-1, -1), .4, LINE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(st)
    else:
        story.append(Paragraph("No rule-based revision suggestions were triggered.", small))
    story += [Spacer(1, 8 * mm), Paragraph(_p(human.get("note", "")), small), PageBreak()]

    # Original excerpt + conclusion
    story += [Paragraph("03  Original Essay", h), Paragraph("The submitted essay is preserved below for reference.", small), Spacer(1, 5 * mm)]
    original = evaluation.get("essay", "")
    # Keep report readable while preserving a substantial excerpt.
    excerpt = original if len(original) <= 12000 else original[:12000] + "\n\n[Excerpt shortened for report layout.]"
    story += [Paragraph(_p(excerpt), body), Spacer(1, 8 * mm), HRFlowable(width="100%", thickness=.5, color=LINE), Spacer(1, 5 * mm)]
    story += [Paragraph("Report note", h3), Paragraph(
        "This report combines a trained machine-learning score with transparent text statistics and rule-based natural-writing suggestions. "
        "The revision is intended to improve clarity and readability; it does not claim to conceal authorship or bypass AI-detection systems.", small
    )]

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return path
