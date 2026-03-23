"""
Final PDF Cleanup and Generation.
Ensures every single chapter in the database has a working PDF link.
If the file doesn't exist in uploads/, it generates a study guide.
"""
import sys
import io
import os
import shutil
from app import create_app, mysql

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'final_pdf_results.txt')

def generate_study_guide(filepath, grade, subject, chapter_title, chapter_num):
    """Generate a clean study guide PDF using reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER
    
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            topMargin=0.8*inch, bottomMargin=0.8*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T', parent=styles['Title'],
                                  fontSize=22, textColor=HexColor('#1a237e'), spaceAfter=12)
    sub_style = ParagraphStyle('S', parent=styles['Heading2'],
                                fontSize=14, textColor=HexColor('#4a148c'), spaceAfter=8)
    body_style = ParagraphStyle('B', parent=styles['Normal'],
                                 fontSize=12, leading=18, spaceAfter=8)
    
    elements = []
    elements.append(Paragraph(f"Study Guide: {subject}", sub_style))
    elements.append(Paragraph(f"Grade {grade} - Chapter {chapter_num}", sub_style))
    elements.append(Paragraph(chapter_title, title_style))
    elements.append(Spacer(1, 0.4*inch))
    
    elements.append(Paragraph("Key Learning Objectives", sub_style))
    elements.append(Spacer(1, 0.1*inch))
    
    points = [
        "Review the fundamental concepts introduced in this chapter.",
        "Understand the relationship between different topics covered.",
        "Practice solving the example problems step-by-step.",
        "Identify and memorize key definitions and formulas.",
        "Answer the review questions at the end of the chapter.",
        "Discuss any doubts with your fellow students or teachers.",
    ]
    
    for pt in points:
        elements.append(Paragraph(f"• {pt}", body_style))
    
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Keep studying hard! Success is just around the corner.", 
                               ParagraphStyle('F', parent=body_style, alignment=TA_CENTER, italic=True)))
    
    doc.build(elements)

app = create_app()
with app.app_context():
    cur = mysql.connection.cursor()
    
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)
        
    cur.execute("""
        SELECT c.id, c.title, c.chapter_number, c.pdf_url, s.title as subject_title, s.grade
        FROM chapters c
        JOIN subjects s ON c.subject_id = s.id
    """)
    chapters = cur.fetchall()
    
    total = len(chapters)
    ok = 0
    generated = 0
    errors = 0
    
    log_lines = [f"Starting final PDF audit for {total} chapters.\n"]
    
    for ch in chapters:
        if isinstance(ch, dict):
            cid, title, num, url, sub, grade = ch['id'], ch['title'], ch['chapter_number'], ch['pdf_url'], ch['subject_title'], ch['grade']
        else:
            cid, title, num, url, sub, grade = ch
            
        file_ok = False
        if url:
            filename = url.split('/')[-1]
            filepath = os.path.join(UPLOADS_DIR, filename)
            if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
                file_ok = True
        
        if file_ok:
            ok += 1
            continue
            
        # Needs a PDF
        clean_sub = "".join(x for x in sub.lower() if x.isalnum())
        clean_title = "".join(x for x in title.lower() if x.isalnum() or x == ' ')[:30].strip().replace(' ', '_')
        new_filename = f"{clean_sub}_{grade}_ch{num}_{clean_title}.pdf"
        new_filepath = os.path.join(UPLOADS_DIR, new_filename)
        new_url = f"/api/pdfs/{new_filename}"
        
        try:
            generate_study_guide(new_filepath, grade, sub, title, num)
            cur.execute("UPDATE chapters SET pdf_url = %s WHERE id = %s", (new_url, cid))
            generated += 1
            log_lines.append(f"GENERATED: [{grade}] {sub} - {title} -> {new_filename}")
        except Exception as e:
            errors += 1
            log_lines.append(f"ERROR: [{grade}] {sub} - {title}: {str(e)}")
            
    mysql.connection.commit()
    
    summary = [
        "\n" + "="*50,
        "FINAL SUMMARY:",
        f"  Total Chapters: {total}",
        f"  Already had valid PDF: {ok}",
        f"  Newly Generated: {generated}",
        f"  Errors: {errors}",
        "="*50
    ]
    log_lines.extend(summary)
    
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines))
    
    for s in summary:
        print(s)
        
    cur.close()
