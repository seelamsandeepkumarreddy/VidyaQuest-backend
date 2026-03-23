"""
Fix all mismatched pdf_url entries in the chapters table.
Matches each chapter to the correct PDF file in the uploads/ folder
using fuzzy name matching based on subject, grade, and chapter title.
"""
import sys
import io
import os
import re
from app import create_app, mysql

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'pdf_fix_results.txt')

def sanitize(text):
    """Normalize text for comparison: lowercase, remove special chars, collapse spaces."""
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', '_', text)
    return text

def find_best_pdf(subject_title, grade, chapter_title, chapter_number, available_pdfs):
    """Find the best matching PDF for a given chapter."""
    sub = sanitize(subject_title)
    ch = sanitize(chapter_title)
    
    # Strategy 1: Exact match using seed_content convention
    candidate = f"{sub}_{grade}_{ch}.pdf"
    if candidate in available_pdfs:
        return candidate
    
    # Strategy 2: Try with ampersands replaced
    ch_amp = sanitize(chapter_title.replace('&', 'and'))
    candidate = f"{sub}_{grade}_{ch_amp}.pdf"
    if candidate in available_pdfs:
        return candidate
    
    # Strategy 3: For Hindi/Telugu, chapters use numbered naming
    if sub == 'hindi':
        candidate = f"hindi_{grade}_vasant_-_chapter_{chapter_number}.pdf"
        if candidate in available_pdfs:
            return candidate
    if sub == 'telugu':
        candidate = f"telugu_{grade}_telugu_chapter_{chapter_number}.pdf"
        if candidate in available_pdfs:
            return candidate
    
    # Strategy 4: Fuzzy substring match — find PDFs that share the most keywords
    chapter_keywords = set(ch.split('_')) - {'the', 'of', 'and', 'in', 'a', 'an', 'to', 'is', ''}
    best_match = None
    best_score = 0
    
    prefix = f"{sub}_{grade}_"
    for pdf in available_pdfs:
        if not pdf.startswith(prefix):
            continue
        pdf_chapter_part = pdf[len(prefix):].replace('.pdf', '')
        pdf_keywords = set(pdf_chapter_part.split('_')) - {'the', 'of', 'and', 'in', 'a', 'an', 'to', 'is', ''}
        
        overlap = len(chapter_keywords & pdf_keywords)
        if overlap > best_score:
            best_score = overlap
            best_match = pdf
    
    if best_match and best_score >= 1:
        return best_match
    
    return None

app = create_app()
with app.app_context():
    cur = mysql.connection.cursor()
    
    available_pdfs = set()
    if os.path.exists(UPLOADS_DIR):
        available_pdfs = {f for f in os.listdir(UPLOADS_DIR) if f.endswith('.pdf')}
    
    log_lines = [f"Found {len(available_pdfs)} PDFs in uploads/\n"]
    
    cur.execute("""
        SELECT c.id, c.title, c.chapter_number, c.pdf_url, s.title as subject_title, s.grade
        FROM chapters c
        JOIN subjects s ON c.subject_id = s.id
        ORDER BY s.grade, s.title, c.chapter_number
    """)
    chapters = cur.fetchall()
    
    fixed = 0
    already_correct = 0
    no_match = 0
    
    for ch in chapters:
        if isinstance(ch, dict):
            ch_id, ch_title, ch_num, current_url, sub_title, grade = (
                ch['id'], ch['title'], ch['chapter_number'], ch['pdf_url'], ch['subject_title'], ch['grade']
            )
        else:
            ch_id, ch_title, ch_num, current_url, sub_title, grade = ch
        
        best_pdf = find_best_pdf(sub_title, grade, ch_title, ch_num, available_pdfs)
        
        if best_pdf:
            correct_url = f"/api/pdfs/{best_pdf}"
            if current_url == correct_url:
                already_correct += 1
            else:
                cur.execute("UPDATE chapters SET pdf_url = %s WHERE id = %s", (correct_url, ch_id))
                fixed += 1
                log_lines.append(f"FIXED: [{grade}] {sub_title} Ch{ch_num}: {ch_title}")
                log_lines.append(f"  OLD: {current_url}")
                log_lines.append(f"  NEW: {correct_url}")
        else:
            no_match += 1
            log_lines.append(f"NO MATCH: [{grade}] {sub_title} Ch{ch_num}: {ch_title} (current: {current_url})")
    
    mysql.connection.commit()
    
    summary = [
        "",
        "=" * 50,
        "SUMMARY:",
        f"  Total chapters: {len(chapters)}",
        f"  Already correct: {already_correct}",
        f"  Fixed: {fixed}",
        f"  No matching PDF: {no_match}",
    ]
    log_lines.extend(summary)
    
    # Write to log file
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines))
    
    # Print summary to console
    for line in summary:
        print(line)
    
    cur.close()
