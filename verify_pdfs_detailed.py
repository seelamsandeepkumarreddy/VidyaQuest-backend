import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = os.getenv("MYSQL_DB", "ruralquest_db")

def verify_pdfs_detailed():
    try:
        db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
        cur = db.cursor()
        
        print("Detailed PDF URL Verification:")
        cur.execute("""
            SELECT s.grade, s.title, c.title, c.pdf_url 
            FROM subjects s 
            JOIN chapters c ON s.id = c.subject_id 
            ORDER BY s.grade, s.title, c.chapter_number
        """)
        results = cur.fetchall()
        for res in results:
            print(f"Grade {res[0]} | {res[1]} | {res[2]} -> {res[3]}")
            
        cur.close()
        db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_pdfs_detailed()
