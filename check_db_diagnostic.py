
import os
from flask import Flask
from flask_mysqldb import MySQL
from config import Config
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
mysql = MySQL(app)

def check_db():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        print("--- Tables ---")
        cur.execute("SHOW TABLES")
        tables = cur.fetchall()
        for t in tables:
            print(t)
            
        print("\n--- Users ---")
        cur.execute("SELECT id, full_name, email, role, grade FROM users")
        users = cur.fetchall()
        for u in users:
            print(u)
            
        print("\n--- Progress ---")
        # Try both common names
        try:
            cur.execute("SELECT * FROM student_progress")
            progress = cur.fetchall()
            print("student_progress data:")
            for p in progress:
                print(p)
        except Exception as e:
            print(f"Error reading student_progress: {e}")
            
        try:
            cur.execute("SELECT * FROM progress")
            progress = cur.fetchall()
            print("progress data:")
            for p in progress:
                print(p)
        except Exception as e:
            print(f"Error reading progress: {e}")

        cur.close()

if __name__ == "__main__":
    check_db()
