import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = os.getenv("MYSQL_DB", "ruralquest_db")

def verify_pdfs():
    try:
        db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
        cur = db.cursor()
        
        print("Verifying PDF URLs for chapters:")
        cur.execute("SELECT id, title, pdf_url FROM chapters LIMIT 10")
        results = cur.fetchall()
        for res in results:
            print(f"ID: {res[0]}, Title: {res[1]}, PDF URL: {res[2]}")
            
        cur.close()
        db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_pdfs()
