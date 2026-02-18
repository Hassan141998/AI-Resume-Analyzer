"""
PDF Report Generator - Fixed Version
Uses fpdf2 with proper error handling and font fallbacks
"""

import os
import tempfile
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


def generate_pdf_report(data: Dict[str, Any]) -> str:
    """Generate PDF report and return temp file path."""
    try:
        return _build_pdf_with_fpdf(data)
    except Exception as exc:
        logger.exception("PDF generation failed: %s", exc)
        # Fallback to plain text
        return _text_fallback(data)


def _build_pdf_with_fpdf(data: Dict[str, Any]) -> str:
    """Build PDF using fpdf2."""
    from fpdf import FPDF

    class PDF(FPDF):
        def header(self):
            # Header background
            self.set_fill_color(15, 23, 42)
            self.rect(0, 0, 210, 30, 'F')
            
            # Title
            self.set_font('Arial', 'B', 18)
            self.set_text_color(0, 245, 212)
            self.set_y(10)
            self.cell(0, 8, 'AI Resume Analyzer', align='C', new_x='LMARGIN', new_y='NEXT')
            
            # Subtitle
            self.set_font('Arial', '', 10)
            self.set_text_color(148, 163, 184)
            self.cell(0, 6, 'Resume Analysis Report', align='C', new_x='LMARGIN', new_y='NEXT')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', '', 8)
            self.set_text_color(148, 163, 184)
            self.cell(0, 10, f'Page {self.page_no()} | Built by Hassan Ahmed', align='C')

    # Create PDF
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(15, 35, 15)

    # Get data
    score = data.get('score', 0)
    filename = data.get('filename', 'Unknown')
    job_title = data.get('job_title') or '—'
    created = data.get('created_at', datetime.utcnow().strftime('%Y-%m-%d %H:%M'))

    # Meta info box
    pdf.set_fill_color(30, 41, 59)
    pdf.set_draw_color(0, 245, 212)
    pdf.set_line_width(0.5)
    pdf.rect(14, pdf.get_y(), 182, 25, 'FD')
    
    pdf.set_font('Arial', '', 9)
    pdf.set_text_color(203, 213, 225)
    y_pos = pdf.get_y() + 5
    pdf.set_y(y_pos)
    
    # Meta data
    pdf.cell(60, 5, f'Resume: {filename[:30]}')
    pdf.cell(60, 5, f'Job: {job_title[:25]}')
    pdf.cell(62, 5, f'Date: {created}', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(12)

    # Overall Score
    _section_title(pdf, 'Overall Match Score')
    score_color = (34, 197, 94) if score >= 80 else ((245, 158, 11) if score >= 50 else (239, 68, 68))
    
    pdf.set_font('Arial', 'B', 48)
    pdf.set_text_color(*score_color)
    pdf.cell(0, 20, str(score), align='C', new_x='LMARGIN', new_y='NEXT')
    
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(148, 163, 184)
    sub_scores = (f"Keyword: {data.get('keyword_score', 0)}%  |  "
                  f"Skills: {data.get('skills_score', 0)}%  |  "
                  f"Format: {data.get('format_score', 0)}%")
    pdf.cell(0, 6, sub_scores, align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(8)

    # Matched Keywords
    _section_title(pdf, 'Matched Keywords')
    matched_kw = data.get('matched_keywords', [])
    if matched_kw:
        _tag_list(pdf, matched_kw[:20], (34, 197, 94))
    else:
        _empty_notice(pdf, 'No matched keywords found')

    # Missing Keywords
    _section_title(pdf, 'Missing Keywords')
    missing_kw = data.get('missing_keywords', [])
    if missing_kw:
        _tag_list(pdf, missing_kw[:20], (239, 68, 68))
    else:
        _empty_notice(pdf, 'No missing keywords identified')

    # Skills You Have
    _section_title(pdf, 'Skills You Have')
    matched_skills = data.get('matched_skills', [])
    if matched_skills:
        _bullet_list(pdf, matched_skills, (34, 197, 94), '+')
    else:
        _empty_notice(pdf, 'No matching skills detected')

    # Skills to Add
    _section_title(pdf, 'Skills to Add')
    missing_skills = data.get('missing_skills', [])
    if missing_skills:
        _bullet_list(pdf, missing_skills, (239, 68, 68), '-')
    else:
        _empty_notice(pdf, 'No additional skills needed')

    # AI Suggestions
    _section_title(pdf, 'AI Improvement Suggestions')
    suggestions = data.get('suggestions', [])
    if suggestions:
        for i, suggestion in enumerate(suggestions[:8], 1):
            _numbered_item(pdf, i, suggestion)
    else:
        _empty_notice(pdf, 'No suggestions available')

    # ATS Check
    _section_title(pdf, 'ATS Compatibility Check')
    ats_issues = data.get('ats_issues', [])
    if ats_issues:
        _bullet_list(pdf, ats_issues, (245, 158, 11), '!')
    else:
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(34, 197, 94)
        pdf.cell(0, 6, 'Passed - No major ATS issues detected', new_x='LMARGIN', new_y='NEXT')
        pdf.set_font('Arial', '', 9)
        pdf.set_text_color(148, 163, 184)
        pdf.cell(0, 5, 'Your resume should parse correctly in most Applicant Tracking Systems.', 
                 new_x='LMARGIN', new_y='NEXT')
    pdf.ln(4)

    # Footer note
    pdf.ln(5)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(100, 116, 139)
    pdf.multi_cell(0, 4, 
                   'This report was generated by AI Resume Analyzer. '
                   'Scores are algorithmic estimates and should be used as guidance. '
                   'Always review and tailor your resume for each specific application.')

    # Save to temp file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', mode='wb')
    pdf_output = pdf.output()
    tmp.write(pdf_output)
    tmp.close()
    
    logger.info(f"PDF generated successfully: {tmp.name}")
    return tmp.name


def _section_title(pdf, title: str):
    """Add a section title with accent bar."""
    pdf.set_fill_color(0, 245, 212)
    pdf.rect(14, pdf.get_y(), 3, 6, 'F')
    pdf.set_x(20)
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 6, title, new_x='LMARGIN', new_y='NEXT')
    pdf.ln(3)


def _tag_list(pdf, items, color):
    """Display items as inline tags."""
    if not items:
        return
    
    pdf.set_font('Arial', '', 9)
    pdf.set_text_color(*color)
    text = '  '.join(items)
    pdf.multi_cell(0, 5, text)
    pdf.ln(5)


def _bullet_list(pdf, items, color, marker='+'):
    """Display items as bulleted list."""
    if not items:
        return
    
    pdf.set_font('Arial', '', 9)
    for item in items[:15]:  # Limit to prevent overflow
        pdf.set_text_color(*color)
        pdf.cell(6, 5, marker)
        pdf.set_text_color(203, 213, 225)
        pdf.multi_cell(0, 5, item)
    pdf.ln(4)


def _numbered_item(pdf, num: int, text: str):
    """Display numbered item."""
    pdf.set_font('Arial', 'B', 9)
    pdf.set_text_color(0, 245, 212)
    pdf.cell(8, 5, f'{num}.')
    pdf.set_font('Arial', '', 9)
    pdf.set_text_color(203, 213, 225)
    pdf.multi_cell(0, 5, text)


def _empty_notice(pdf, message: str):
    """Display empty state message."""
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 5, message, new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)


def _text_fallback(data: Dict[str, Any]) -> str:
    """Generate plain text fallback report."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8')
    
    # Build ATS issues list
    ats_issues_list = data.get('ats_issues', [])
    if ats_issues_list:
        ats_lines = [f'  ! {issue}' for issue in ats_issues_list]
    else:
        ats_lines = ['  No issues detected']
    
    lines = [
        '=' * 60,
        'AI RESUME ANALYZER - ANALYSIS REPORT',
        '=' * 60,
        '',
        f"Resume: {data.get('filename', 'Unknown')}",
        f"Job: {data.get('job_title', '—')}",
        f"Score: {data.get('score', 0)}%",
        f"Date: {data.get('created_at', '')}",
        '',
        'MATCHED KEYWORDS:',
    ]
    
    # Add matched keywords
    for k in data.get('matched_keywords', [])[:20]:
        lines.append(f'  + {k}')
    
    lines.append('')
    lines.append('MISSING KEYWORDS:')
    
    # Add missing keywords
    for k in data.get('missing_keywords', [])[:20]:
        lines.append(f'  - {k}')
    
    lines.append('')
    lines.append('MATCHED SKILLS:')
    
    # Add matched skills
    for s in data.get('matched_skills', []):
        lines.append(f'  + {s}')
    
    lines.append('')
    lines.append('MISSING SKILLS:')
    
    # Add missing skills
    for s in data.get('missing_skills', []):
        lines.append(f'  - {s}')
    
    lines.append('')
    lines.append('AI SUGGESTIONS:')
    
    # Add suggestions
    for i, s in enumerate(data.get('suggestions', []), 1):
        lines.append(f'  {i}. {s}')
    
    lines.append('')
    lines.append('ATS ISSUES:')
    
    # Add ATS issues
    lines.extend(ats_lines)
    
    lines.append('')
    lines.append('=' * 60)
    lines.append('Built by Hassan Ahmed - AI Resume Analyzer')
    lines.append('=' * 60)
    
    tmp.write('\n'.join(lines))
    tmp.close()
    
    logger.warning(f"PDF generation failed, created text fallback: {tmp.name}")
    return tmp.name
