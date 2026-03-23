
import os
from flask import Flask
from flask_mysqldb import MySQL
from config import Config
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
mysql = MySQL(app)

def migrate_data():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        print("Migrating existing students with NULL grade...")
        query = "UPDATE users SET grade = '8' WHERE role = 'student' AND (grade IS NULL OR grade = '')"
        cur.execute(query)
        affected = cur.rowcount
        print(f"Updated {affected} students to Grade 8.")
        
        print("\nSyncing total_xp from student_progress to users table...")
        query = """
            UPDATE users u
            JOIN student_progress sp ON u.id = sp.student_id
            SET u.total_xp = sp.xp
            WHERE u.total_xp = 0 OR u.total_xp IS NULL
        """
        cur.execute(query)
        affected = cur.rowcount
        print(f"Synced XP for {affected} users.")
        
        mysql.connection.commit()
        cur.close()
        print("\nMigration complete.")

if __name__ == "__main__":
    migrate_data()
