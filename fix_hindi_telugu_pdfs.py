"""
Refined Fix for Hindi and Telugu PDF mappings.
Handles truncated hex filenames in assets.
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
LOG_FILE = os.path.join(os.path.dirname(__file__), 'hindi_telugu_fix_results.txt')

def get_hex_prefix(text):
    """Convert a string to its UTF-8 hex prefix."""
    try:
        return text.encode('utf-8').hex()
    except Exception:
        return ""

def sanitize_english(text):
    """Keep only a-z0-9 and underscores."""
    return re.sub(r'[^a-z0-9_]', '', text.lower().replace(' ', '_'))

app = create_app()
with app.app_context():
    cur = mysql.connection.cursor()
    
    # Get all Hindi and Telugu chapters
    cur.execute("""
        SELECT c.id, c.title, c.chapter_number, s.title as subject_title, s.grade
        FROM chapters c
        JOIN subjects s ON c.subject_id = s.id
        WHERE s.title IN ('Hindi', 'Telugu')
    """)
    chapters = cur.fetchall()
    
    ch_data = []
    for ch in chapters:
        if isinstance(ch, dict):
            id_val, title, num, sub, grade = ch['id'], ch['title'], ch['chapter_number'], ch['subject_title'], ch['grade']
        else:
            id_val, title, num, sub, grade = ch
            
        ch_data.append({
            'id': id_val,
            'title': title,
            'num': num,
            'sub': sub.lower(),
            'grade': str(grade),
            'hex': get_hex_prefix(title)
        })
    
    # Asset files
    asset_files = [f for f in os.listdir(ASSETS_DIR) if f.endswith('.pdf') and (f.startswith('hindi_') or f.startswith('telugu_'))]
    
    log_lines = []
    fixed_count = 0
    
    used_assets = set()
    used_chapters = set()
    
    for af in sorted(asset_files):
        parts = af.replace('.pdf', '').split('_')
        if len(parts) < 3: continue
        
        lang = parts[0]
        grade = parts[1]
        hex_part = '_'.join(parts[2:])
        clean_hex = hex_part.replace('_', '')
        
        best_match = None
        
        # Try hex prefix matching first (handle truncation)
        if re.match(r'^[0-9a-f]+$', clean_hex):
            for ch in ch_data:
                if ch['id'] in used_chapters: continue
                if ch['sub'] == lang and ch['grade'] == grade:
                    # Match if clean_hex is a prefix of chapter hex
                    # OR if chapter hex is a prefix (unlikely given truncation)
                    if ch['hex'].startswith(clean_hex) or clean_hex.startswith(ch['hex'][:len(clean_hex)]):
                        best_match = ch
                        break
        
        # If no hex match, try English keyword matching in the filename
        if not best_match:
            # e.g. akbari_lota matches "अकबरी लोटा" if I had a transliteration, 
            # but let's try matching against chapter number if it's there? 
            # No, let's try matching against English-named assets
            name_part = sanitize_english(hex_part)
            if name_part:
                for ch in ch_data:
                    if ch['id'] in used_chapters: continue
                    if ch['sub'] == lang and ch['grade'] == grade:
                        # This is harder without a mapping.
                        # Let's check if the chapter title is already "Chapter X"
                        if str(ch['num']) in name_part:
                            best_match = ch
                            break
        
        if best_match:
            target_filename = f"{lang}_{grade}_chapter_{best_match['num']}.pdf"
            target_path = os.path.join(UPLOADS_DIR, target_filename)
            target_url = f"/api/pdfs/{target_filename}"
            
            shutil.copy2(os.path.join(ASSETS_DIR, af), target_path)
            cur.execute("UPDATE chapters SET pdf_url = %s WHERE id = %s", (target_url, best_match['id']))
            
            fixed_count += 1
            used_chapters.add(best_match['id'])
            log_lines.append(f"FIXED: [{grade}] {lang} Ch{best_match['num']}: {best_match['title']} <- {af}")
        else:
            log_lines.append(f"UNMATCHED ASSET: {af} (hex: {clean_hex})")

    # For still missing chapters, generate study guides
    # Actually, let's just commit the fixes first.
    mysql.connection.commit()
    
    print(f"Fixed {fixed_count} chapters.")
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines))
        
    cur.close()
