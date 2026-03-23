
import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

def check_questions():
    conn = MySQLdb.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER"),
        passwd=os.getenv("MYSQL_PASSWORD"),
        db=os.getenv("MYSQL_DB")
    )
    cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    
    print("--- Questions by Chapter ---")
    cur.execute("""
        SELECT q.chapter_id, c.title, COUNT(*) as count 
        FROM questions q 
        JOIN chapters c ON q.chapter_id = c.id 
        GROUP BY q.chapter_id
    """)
    rows = cur.fetchall()
    for r in rows:
        print(f"ID {r['chapter_id']}: {r['title']} - {r['count']} questions")
        
    print("\nTotal Questions:", sum(r['count'] for r in rows))
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_questions()
