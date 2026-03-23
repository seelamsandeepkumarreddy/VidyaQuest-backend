import sys
import io
from app import create_app, mysql

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = create_app()
with app.app_context():
    cur = mysql.connection.cursor()
    # Find chapter 'The Tsunami'
    cur.execute("SELECT id, title, subject_id FROM chapters WHERE title LIKE '%Tsunami%'")
    chapters = cur.fetchall()
    print("Chapters matching 'Tsunami':", chapters)
    
    if chapters:
        for ch in chapters:
            ch_id = ch['id'] if isinstance(ch, dict) else ch[0]
            cur.execute("SELECT COUNT(*) FROM questions WHERE chapter_id = %s", (ch_id,))
            count = cur.fetchone()
            print(f"Questions for chapter {ch_id} ('{ch['title'] if isinstance(ch, dict) else ch[1]}'): {count}")
            
            cur.execute("SELECT id, question_text FROM questions WHERE chapter_id = %s", (ch_id,))
            questions = cur.fetchall()
            for q in questions:
                print(f"  - {q}")
                
    cur.close()
