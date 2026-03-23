import os
import shutil
import MySQLdb
import re

ASSETS_DIR = r"c:\Users\sande\AndroidStudioProjects\RuralQuest\app\src\main\assets"
UPLOADS_DIR = r"c:\Users\sande\AndroidStudioProjects\ruralquest_backend\uploads"

def sanitize(text):
    text = text.lower()
    text = text.replace(" ", "_").replace("-", "_")
    text = re.sub(r'[^a-z0-9_]', '', text)
    return text

def migrate():
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='ruralquest_db')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # Get all subjects and chapters
        cur.execute("""
            SELECT c.id as chapter_id, s.grade, s.title as subject_title, c.title as chapter_title
            FROM chapters c
            JOIN subjects s ON c.subject_id = s.id
        """)
        chapters = cur.fetchall()
        
        # Get list of asset files
        asset_files = [f for f in os.listdir(ASSETS_DIR) if f.endswith('.pdf')]
        print(f"Found {len(asset_files)} PDF assets.")
        
        matches = 0
        for ch in chapters:
            grade = ch['grade']
            sub_title = ch['subject_title']
            ch_title = ch['chapter_title']
            ch_id = ch['chapter_id']
            
            san_sub = sanitize(sub_title)
            san_ch = sanitize(ch_title)
            
            # Construct expected filename: subject_grade_chapter.pdf
            expected_filename = f"{san_sub}_{grade}_{san_ch}.pdf"
            
            if expected_filename in asset_files:
                src = os.path.join(ASSETS_DIR, expected_filename)
                dst = os.path.join(UPLOADS_DIR, expected_filename)
                
                # Copy file
                shutil.copy2(src, dst)
                
                # Update DB
                new_url = f"/api/pdfs/{expected_filename}"
                cur.execute("UPDATE chapters SET pdf_url = %s WHERE id = %s", (new_url, ch_id))
                matches += 1
                # print(f"Matched & Updated: {expected_filename}")
            else:
                # Try partial match if sanitized chapter is too long or slightly different
                # (e.g. Hindi chapters sometimes have hex codes)
                pass

        conn.commit()
        print(f"Total Matches and Updates: {matches}")
        
        # Special handling for Hindi chapters (they have hex codes in assets)
        # hindi_10_e0a4aae0a4a6.pdf etc.
        # I'll skip complex matching for now as most are standard.
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    migrate()
