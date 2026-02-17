"""
PDF Report Generator
Uses fpdf2 (~2 MB) instead of reportlab (~15 MB) for Vercel size limits.
"""

import os
import tempfile
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

# ── Color palette ─────────────────────────────────────────────────────────────
C_NAVY   = (15,  23,  42)
C_SLATE  = (30,  41,  59)
C_AQUA   = (0,   200, 180)
C_PINK   = (220, 50,  120)
C_GREEN  = (34,  197, 94)
C_RED    = (220, 60,  60)
C_YELLOW = (245, 158, 11)
C_WHITE  = (255, 255, 255)
C_LIGHT  = (203, 213, 225)
C_MUTED  = (148, 163, 184)


def generate_pdf_report(data: Dict[str, Any]) -> str:
    """Generate a PDF report and return its temp file path."""
    try:
        return _build_fpdf(data)
    except Exception as exc:
        logger.exception("fpdf2 report failed: %s", exc)
        return _text_fallback(data)


def _build_fpdf(data: Dict[str, Any]) -> str:
    from fpdf import FPDF

    class PDF(FPDF):
        def header(self):
            self.set_fill_color(*C_NAVY)
            self.rect(0, 0, 210, 28, "F")
            self.set_font("Helvetica", "B", 16)
            self.set_text_color(*C_AQUA)
            self.set_y(8)
            self.cell(0, 8, "AI Resume Analyzer", align="C", new_x="LMARGIN", new_y="NEXT")
            self.set_font("Helvetica", "", 9)
            self.set_text_color(*C_MUTED)
            self.cell(0, 5, "Smart CV Screening Report  |  Built by Hassan Ahmed",
                      align="C", new_x="LMARGIN", new_y="NEXT")
            self.ln(6)

        def footer(self):
            self.set_y(-14)
            self.set_font("Helvetica", "", 8)
            self.set_text_color(*C_MUTED)
            self.cell(0, 6,
                      f"Page {self.page_no()}  |  AI Resume Analyzer  |  Hassan Ahmed",
                      align="C")

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_margins(16, 32, 16)

    score     = data.get("score", 0)
    filename  = data.get("filename", "—")
    job_title = data.get("job_title") or "—"
    created   = data.get("created_at", datetime.utcnow().strftime("%Y-%m-%d %H:%M"))

    # ── Meta block ─────────────────────────────────────────────────────────────
    pdf.set_fill_color(30, 41, 59)
    pdf.set_draw_color(*C_AQUA)
    pdf.set_line_width(0.3)
    pdf.rounded_rect(14, pdf.get_y(), 182, 22, 4, "FD")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_MUTED)
    pdf.set_y(pdf.get_y() + 3)
    pdf.cell(60, 5, f"Resume:  {filename[:35]}")
    pdf.cell(60, 5, f"Job:  {job_title[:30]}")
    pdf.cell(62, 5, f"Date:  {created}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # ── Score ──────────────────────────────────────────────────────────────────
    _section_title(pdf, "Overall Match Score")
    score_col = C_GREEN if score >= 80 else (C_YELLOW if score >= 50 else C_RED)
    pdf.set_font("Helvetica", "B", 52)
    pdf.set_text_color(*score_col)
    pdf.cell(50, 20, str(score), align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*C_MUTED)
    pdf.set_x(66)
    pdf.set_y(pdf.get_y())
    sub_y = pdf.get_y()
    pdf.cell(0, 6,
             f"Keyword Match:  {data.get('keyword_score', 0)}%   |   "
             f"Skills Match:  {data.get('skills_score', 0)}%   |   "
             f"Format Score:  {data.get('format_score', 0)}%")
    pdf.ln(16)

    # ── Keyword sections ───────────────────────────────────────────────────────
    _section_title(pdf, "Matched Keywords")
    _tag_list(pdf, data.get("matched_keywords", []), C_GREEN)

    _section_title(pdf, "Missing Keywords")
    _tag_list(pdf, data.get("missing_keywords", []), C_RED)

    _section_title(pdf, "Skills You Have")
    _bullet_list(pdf, data.get("matched_skills", []), C_GREEN, "✓")

    _section_title(pdf, "Skills to Add")
    _bullet_list(pdf, data.get("missing_skills", []), C_RED, "✗")

    _section_title(pdf, "AI Improvement Suggestions")
    for i, s in enumerate(data.get("suggestions", []), 1):
        _numbered_item(pdf, i, s)

    _section_title(pdf, "ATS Compatibility")
    ats = data.get("ats_issues", [])
    if ats:
        _bullet_list(pdf, ats, C_YELLOW, "!")
    else:
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*C_GREEN)
        pdf.cell(0, 6, "No major ATS issues detected. Your resume should parse correctly.",
                 new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.close()
    pdf.output(tmp.name)
    return tmp.name


def _section_title(pdf, title: str):
    pdf.set_fill_color(0, 200, 180)
    pdf.rect(14, pdf.get_y(), 3, 6, "F")
    pdf.set_x(20)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*C_WHITE)
    pdf.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def _tag_list(pdf, items, color):
    if not items:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(*C_MUTED)
        pdf.cell(0, 5, "None identified.", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        return
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*color)
    line = "  ".join(items)
    pdf.multi_cell(0, 5, line)
    pdf.ln(4)


def _bullet_list(pdf, items, color, marker="•"):
    if not items:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(*C_MUTED)
        pdf.cell(0, 5, "None identified.", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        return
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*color)
    for item in items:
        pdf.cell(6, 5, marker)
        pdf.set_text_color(203, 213, 225)
        pdf.multi_cell(0, 5, item)
        pdf.set_text_color(*color)
    pdf.ln(4)


def _numbered_item(pdf, n: int, text: str):
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*C_AQUA)
    pdf.cell(8, 5, f"{n}.")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(203, 213, 225)
    pdf.multi_cell(0, 5, text)


def _text_fallback(data: Dict[str, Any]) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    lines = [
        "AI Resume Analyzer – Report",
        "=" * 40,
        f"File  : {data.get('filename','—')}",
        f"Score : {data.get('score',0)}%",
        f"Date  : {data.get('created_at','')}",
        "",
        "Matched Keywords:",
        *[f"  - {k}" for k in data.get("matched_keywords", [])],
        "",
        "Missing Keywords:",
        *[f"  - {k}" for k in data.get("missing_keywords", [])],
        "",
        "Suggestions:",
        *[f"  {i+1}. {s}" for i, s in enumerate(data.get("suggestions", []))],
        "",
        "Built by Hassan Ahmed – AI Resume Analyzer",
    ]
    tmp.write("\n".join(lines))
    tmp.close()
    return tmp.name
