
import os
from flask import Flask
from flask_mysqldb import MySQL
from config import Config
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
mysql = MySQL(app)

def check_schema():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        print("SCHEMA FOR users:")
        cur.execute("DESCRIBE users")
        schema = cur.fetchall()
        for field in schema:
            print(field)
            
        print("\nSCHEMA FOR student_progress:")
        try:
            cur.execute("DESCRIBE student_progress")
            schema = cur.fetchall()
            for field in schema:
                print(field)
        except Exception as e:
            print(f"Error: {e}")

        cur.close()

if __name__ == "__main__":
    check_schema()
