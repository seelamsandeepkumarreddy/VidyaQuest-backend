import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = os.getenv("MYSQL_DB", "ruralquest_db")

def check_subjects():
    try:
        db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
        cur = db.cursor()
        
        cur.execute("SELECT grade, COUNT(*) FROM subjects GROUP BY grade")
        results = cur.fetchall()
        print("Subject counts by grade:")
        for res in results:
            print(f"Grade {res[0]}: {res[1]} subjects")
            
        cur.execute("SELECT id, grade, title FROM subjects")
        all_subs = cur.fetchall()
        print("\nAll subjects:")
        for s in all_subs:
            print(f"ID {s[0]}, Grade {s[1]}, Title: {s[2]}")
            
        cur.close()
        db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_subjects()
