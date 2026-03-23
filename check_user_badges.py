import MySQLdb
import os
from dotenv import load_dotenv

def check_user_data(user_id):
    load_dotenv()
    try:
        db = MySQLdb.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            passwd=os.getenv("MYSQL_PASSWORD", ""),
            db=os.getenv("MYSQL_DB", "ruralquest_db")
        )
        cur = db.cursor(MySQLdb.cursors.DictCursor)
        
        print(f"--- Data for User: {user_id} ---")
        
        # Check students table
        cur.execute("SELECT * FROM students WHERE user_id = %s", (user_id,))
        student = cur.fetchone()
        print(f"\nStudents Table: {student}")
        
        # Check quiz_progress table
        cur.execute("SELECT * FROM quiz_progress WHERE user_id = %s", (user_id,))
        quizzes = cur.fetchall()
        print(f"\nQuiz Progress ({len(quizzes)} entries):")
        for q in quizzes:
            print(f"  - Subject: {q['subject']}, Chapter: {q['chapter']}, Score: {q['score']}, Badge: {q['badge']}")
            
        db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_user_data("VQ-2026003")
