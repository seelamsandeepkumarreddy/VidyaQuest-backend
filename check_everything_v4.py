
import os
import json
from flask import Flask
from flask_mysqldb import MySQL
from config import Config
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
mysql = MySQL(app)

def check_everything():
    output = []
    with app.app_context():
        cur = mysql.connection.cursor()
        
        output.append("=== TABLES ===")
        cur.execute("SHOW TABLES")
        tables = [t[0] if isinstance(t, tuple) else list(t.values())[0] for t in cur.fetchall()]
        for t in tables:
            output.append(f" - {t}")
            
        for t in tables:
            output.append(f"\n=== SCHEMA FOR {t} ===")
            try:
                cur.execute(f"DESCRIBE {t}")
                for f in cur.fetchall():
                    output.append(str(f))
            except Exception as e:
                output.append(f"Error: {e}")
            
        output.append("\n=== ALL USERS DATA ===")
        cur.execute("SELECT id, full_name, role, grade FROM users")
        for u in cur.fetchall():
            output.append(str(u))
            
        output.append("\n=== STUDENT PROGRESS DATA ===")
        try:
            cur.execute("SELECT * FROM student_progress")
            for p in cur.fetchall():
                output.append(str(p))
        except Exception as e:
            output.append(f"Error: {e}")

        cur.close()

    with open("db_complete_status_v4.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    check_everything()
