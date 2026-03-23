import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = os.getenv("MYSQL_DB", "ruralquest_db")

def fix_db():
    try:
        db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
        cur = db.cursor()
        
        print("--- Force Cleaning Database ---")
        cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        tables_to_drop = ['questions', 'chapters', 'subjects', 'quizzes', 'quiz_progress']
        for table in tables_to_drop:
            print(f"Dropping table {table} if exists...")
            cur.execute(f"DROP TABLE IF EXISTS {table}")
        
        cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
        db.commit()
        cur.close()
        db.close()
        print("Done cleaning!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_db()
