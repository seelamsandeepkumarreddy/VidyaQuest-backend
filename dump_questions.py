
import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

def check_questions_safe():
    conn = MySQLdb.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER"),
        passwd=os.getenv("MYSQL_PASSWORD"),
        db=os.getenv("MYSQL_DB")
    )
    cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    
    cur.execute("""
        SELECT q.id, q.chapter_id, c.title, c.subject_id
        FROM questions q 
        JOIN chapters c ON q.chapter_id = c.id
    """)
    rows = cur.fetchall()
    
    print(f"Total Questions Found: {len(rows)}")
    for r in rows:
        print(f"QID: {r['id']} | ChID: {r['chapter_id']} | Title: '{r['title']}' | SubID: {r['subject_id']}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_questions_safe()
