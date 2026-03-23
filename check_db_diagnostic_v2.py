
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
        
        print("TABLES:")
        cur.execute("SHOW TABLES")
        for (table,) in cur.fetchall():
            print(f" - {table}")
            
        print("\nSTUDENTS (role='student'):")
        cur.execute("SELECT id, full_name, email, grade FROM users WHERE role='student'")
        students = cur.fetchall()
        for s in students:
            print(f" {s}")
            
        print("\nSTUDENT_PROGRESS CONTENT:")
        try:
            cur.execute("SELECT * FROM student_progress")
            progress = cur.fetchall()
            for p in progress:
                print(f" {p}")
        except Exception as e:
            print(f" Error: {e}")

        cur.close()

if __name__ == "__main__":
    check_db()
