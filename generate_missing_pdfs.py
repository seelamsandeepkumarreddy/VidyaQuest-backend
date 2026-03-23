"""
Generate/copy ALL missing chapter PDFs.
1. Try to copy from Android assets/ folder (matching by keywords)
2. If no asset exists, generate a study-guide PDF using reportlab
3. Update the database pdf_url to point to the new file
"""
import sys
import io
import os
import re
import shutil
from app import create_app, mysql

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
ASSETS_DIR = r"c:\Users\sande\AndroidStudioProjects\RuralQuest\app\src\main\assets"
LOG_FILE = os.path.join(os.path.dirname(__file__), 'pdf_generate_results.txt')

def sanitize(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', '_', text)
    return text

def make_filename(subject, grade, chapter_title):
    """Create a standardized filename for a chapter PDF."""
    sub = sanitize(subject)
    ch = sanitize(chapter_title)
    return f"{sub}_{grade}_{ch}.pdf"

def find_asset_pdf(subject_title, grade, chapter_title, asset_files):
    """Try to find a matching PDF in the assets folder using keyword matching."""
    sub = sanitize(subject_title)
    ch_keywords = set(sanitize(chapter_title).split('_')) - {'the', 'of', 'and', 'in', 'a', 'an', 'to', 'is', ''}
    
    prefix = f"{sub}_{grade}_"
    best_match = None
    best_score = 0
    
    for af in asset_files:
        if not af.startswith(prefix):
            continue
        af_part = af[len(prefix):].replace('.pdf', '')
        af_keywords = set(af_part.split('_')) - {'the', 'of', 'and', 'in', 'a', 'an', 'to', 'is', ''}
        
        overlap = len(ch_keywords & af_keywords)
        if overlap > best_score:
            best_score = overlap
            best_match = af
    
    if best_match and best_score >= 1:
        return best_match
    return None

def generate_pdf(filepath, grade, subject, chapter_title):
    """Generate a simple study guide PDF using reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            topMargin=0.8*inch, bottomMargin=0.8*inch,
                            leftMargin=0.8*inch, rightMargin=0.8*inch)
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'],
                                  fontSize=20, textColor=HexColor('#1a237e'),
                                  spaceAfter=12)
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Heading2'],
                                     fontSize=14, textColor=HexColor('#4a148c'),
                                     spaceAfter=8)
    body_style = ParagraphStyle('CustomBody', parent=styles['Normal'],
                                 fontSize=11, leading=16, spaceAfter=6)
    
    elements = []
    
    # Title
    elements.append(Paragraph(f"Grade {grade} - {subject}", subtitle_style))
    elements.append(Paragraph(chapter_title, title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Study guide content
    elements.append(Paragraph("Study Guide", subtitle_style))
    elements.append(Spacer(1, 0.1*inch))
    
    tips = [
        f"This is your study guide for <b>{chapter_title}</b> from Grade {grade} {subject}.",
        "Read the chapter carefully from your textbook before attempting any exercises.",
        "Take notes on key concepts, definitions, and formulas as you read.",
        "Practice the exercises at the end of the chapter in your textbook.",
        "Discuss difficult concepts with your teacher or classmates.",
        "Use the quiz feature in the VidyaQuest app to test your understanding.",
        "Review your notes before exams for better retention.",
    ]
    
    for i, tip in enumerate(tips, 1):
        elements.append(Paragraph(f"{i}. {tip}", body_style))
        elements.append(Spacer(1, 0.05*inch))
    
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("Key Points to Remember", subtitle_style))
    elements.append(Spacer(1, 0.1*inch))
    
    key_points = [
        "Understand the core concepts before memorizing details.",
        "Practice regularly with sample problems and past papers.",
        "Create mind maps or flowcharts for complex topics.",
        "Teach what you've learned to a friend - it helps reinforce understanding.",
        "Don't hesitate to ask questions when something is unclear.",
    ]
    
    for kp in key_points:
        elements.append(Paragraph(f"\u2022 {kp}", body_style))
    
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Happy Learning! - VidyaQuest Team", 
                               ParagraphStyle('Footer', parent=styles['Normal'],
                                              fontSize=10, textColor=HexColor('#666666'),
                                              alignment=TA_CENTER)))
    
    doc.build(elements)

app = create_app()
with app.app_context():
    cur = mysql.connection.cursor()
    
    # Get available files
    upload_files = set(os.listdir(UPLOADS_DIR)) if os.path.exists(UPLOADS_DIR) else set()
    asset_files = set(f for f in os.listdir(ASSETS_DIR) if f.endswith('.pdf')) if os.path.exists(ASSETS_DIR) else set()
    
    # Get all chapters with their subject info
    cur.execute("""
        SELECT c.id, c.title, c.chapter_number, c.pdf_url, s.title as subject_title, s.grade
        FROM chapters c
        JOIN subjects s ON c.subject_id = s.id
        ORDER BY s.grade, s.title, c.chapter_number
    """)
    chapters = cur.fetchall()
    
    log_lines = []
    copied = 0
    generated = 0
    already_exists = 0
    
    for ch in chapters:
        if isinstance(ch, dict):
            ch_id, ch_title, ch_num, current_url, sub_title, grade = (
                ch['id'], ch['title'], ch['chapter_number'], ch['pdf_url'], ch['subject_title'], ch['grade']
            )
        else:
            ch_id, ch_title, ch_num, current_url, sub_title, grade = ch

        # Make target filename
        target_filename = make_filename(sub_title, grade, ch_title)
        target_path = os.path.join(UPLOADS_DIR, target_filename)
        target_url = f"/api/pdfs/{target_filename}"
        
        # Skip if the file already exists in uploads
        if target_filename in upload_files:
            already_exists += 1
            # Still fix the URL if it's wrong
            if current_url != target_url:
                cur.execute("UPDATE chapters SET pdf_url = %s WHERE id = %s", (target_url, ch_id))
                log_lines.append(f"URL FIX: [{grade}] {sub_title} Ch{ch_num}: {ch_title} -> {target_url}")
            continue
        
        # Also check if current_url file exists (different name convention like hindi vasant)
        if current_url:
            existing_filename = current_url.split('/')[-1]
            if existing_filename in upload_files:
                already_exists += 1
                continue
        
        # Try to find and copy from assets
        asset_match = find_asset_pdf(sub_title, grade, ch_title, asset_files)
        if asset_match:
            src = os.path.join(ASSETS_DIR, asset_match)
            shutil.copy2(src, target_path)
            cur.execute("UPDATE chapters SET pdf_url = %s WHERE id = %s", (target_url, ch_id))
            copied += 1
            log_lines.append(f"COPIED: [{grade}] {sub_title} Ch{ch_num}: {ch_title}")
            log_lines.append(f"  FROM: assets/{asset_match}")
            log_lines.append(f"  TO:   uploads/{target_filename}")
            upload_files.add(target_filename)  # track it
            continue
        
        # Generate a study guide PDF
        try:
            generate_pdf(target_path, grade, sub_title, ch_title)
            cur.execute("UPDATE chapters SET pdf_url = %s WHERE id = %s", (target_url, ch_id))
            generated += 1
            log_lines.append(f"GENERATED: [{grade}] {sub_title} Ch{ch_num}: {ch_title} -> {target_filename}")
            upload_files.add(target_filename)
        except Exception as e:
            log_lines.append(f"ERROR: [{grade}] {sub_title} Ch{ch_num}: {ch_title} -> {str(e)}")
    
    mysql.connection.commit()
    
    summary = [
        "",
        "=" * 50,
        "SUMMARY:",
        f"  Total chapters: {len(chapters)}",
        f"  Already had PDF: {already_exists}",
        f"  Copied from assets: {copied}",
        f"  Generated new PDF: {generated}",
        f"  Total PDFs now: {len([f for f in os.listdir(UPLOADS_DIR) if f.endswith('.pdf')])}",
    ]
    log_lines.extend(summary)
    
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines))
    
    for line in summary:
        print(line)
    
    cur.close()
