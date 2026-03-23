
import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

def check_schema():
    conn = MySQLdb.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER"),
        passwd=os.getenv("MYSQL_PASSWORD"),
        db=os.getenv("MYSQL_DB")
    )
    cur = conn.cursor()
    
    tables = ['quiz_progress', 'questions', 'student_progress', 'students', 'chapters']
    for table in tables:
        print(f"\n--- {table} ---")
        cur.execute(f"DESCRIBE {table}")
        cols = cur.fetchall()
        for c in cols:
            print(f"  {c[0]} ({c[1]})")
            
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_schema()
