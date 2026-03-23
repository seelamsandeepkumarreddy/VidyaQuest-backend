import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = os.getenv("MYSQL_DB", "ruralquest_db")

def check_chapters():
    try:
        db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
        cur = db.cursor()
        
        cur.execute("""
            SELECT s.grade, s.title, COUNT(c.id) 
            FROM subjects s 
            LEFT JOIN chapters c ON s.id = c.subject_id 
            GROUP BY s.grade, s.title
        """)
        results = cur.fetchall()
        print("Chapter counts by Subject and Grade:")
        for res in results:
            print(f"Grade {res[0]} - {res[1]}: {res[2]} chapters")
            
        cur.close()
        db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_chapters()
