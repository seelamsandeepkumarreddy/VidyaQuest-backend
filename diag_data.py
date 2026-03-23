
import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

def check_data():
    conn = MySQLdb.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER"),
        passwd=os.getenv("MYSQL_PASSWORD"),
        db=os.getenv("MYSQL_DB")
    )
    cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    
    print("--- Students Table ---")
    cur.execute("SELECT user_id, grade, total_xp, quiz_count FROM students")
    rows = cur.fetchall()
    for r in rows:
        print(r)
        
    print("\n--- Student Progress (Old) ---")
    cur.execute("SELECT student_id, xp, lessons_completed FROM student_progress")
    rows = cur.fetchall()
    for r in rows:
        print(r)
        
    print("\n--- Quiz Progress (New) ---")
    cur.execute("SELECT user_id, subject, chapter, score FROM quiz_progress")
    rows = cur.fetchall()
    for r in rows:
        print(r)
        
    print("\n--- Chapters ---")
    cur.execute("SELECT id, subject_id, chapter_number, title FROM chapters")
    rows = cur.fetchall()
    for r in rows:
        print(r)
        
    print("\n--- Questions ---")
    cur.execute("SELECT chapter_id, COUNT(*) as count FROM questions GROUP BY chapter_id")
    rows = cur.fetchall()
    for r in rows:
        print(r)
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_data()
