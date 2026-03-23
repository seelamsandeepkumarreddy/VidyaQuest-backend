import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = os.getenv("MYSQL_DB", "ruralquest_db")

def check_users():
    try:
        db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
        cur = db.cursor()
        
        print("Recent Students:")
        cur.execute("""
            SELECT u.id, u.full_name, u.email, s.grade 
            FROM users u 
            JOIN students s ON u.id = s.user_id 
            ORDER BY u.created_at DESC LIMIT 5
        """)
        results = cur.fetchall()
        for res in results:
            print(f"ID: {res[0]}, Name: {res[1]}, Email: {res[2]}, Grade: {res[3]}")
            
        cur.close()
        db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users()
