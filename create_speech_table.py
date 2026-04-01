import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

def create_speech_table():
    try:
        conn = MySQLdb.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            passwd=os.getenv("MYSQL_PASSWORD", ""),
            db=os.getenv("MYSQL_DB", "ruralquest_db")
        )
        cur = conn.cursor()
        
        # Create speech_training_progress table
        query = """
        CREATE TABLE IF NOT EXISTS speech_training_progress (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(20) NOT NULL,
            category VARCHAR(100) NOT NULL,
            accuracy INT NOT NULL,
            words_practiced INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        cur.execute(query)
        conn.commit()
        print("✅ Table 'speech_training_progress' created successfully!")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error creating table: {e}")

if __name__ == "__main__":
    create_speech_table()
