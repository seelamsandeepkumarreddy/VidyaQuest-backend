import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = os.getenv("MYSQL_DB", "ruralquest_db")

def create_table():
    try:
        db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
        cur = db.cursor()
        
        sql = """
        CREATE TABLE IF NOT EXISTS daily_challenges (
            id INT AUTO_INCREMENT PRIMARY KEY,
            author_id INT NOT NULL,
            grade VARCHAR(10) NOT NULL,
            title VARCHAR(150) NOT NULL,
            description TEXT,
            questions JSON NOT NULL, -- JSON array of question objects
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NULL,
            FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
        cur.execute(sql)
        db.commit()
        print("Table 'daily_challenges' created successfully!")
        cur.close()
        db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_table()
