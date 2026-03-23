import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = os.getenv("MYSQL_DB", "ruralquest_db")

def check_db():
    try:
        db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
        cur = db.cursor()
        
        print("--- Tables ---")
        cur.execute("SHOW TABLES")
        for table in cur.fetchall():
            print(table[0])
            
        print("\n--- Columns in subjects ---")
        try:
            cur.execute("DESCRIBE subjects")
            for col in cur.fetchall():
                print(col)
        except Exception as e:
            print(f"Error describing subjects: {e}")

        cur.close()
        db.close()
    except Exception as e:
        print(f"Error connecting: {e}")

if __name__ == "__main__":
    check_db()
