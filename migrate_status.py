import MySQLdb
import config

def migrate():
    try:
        db = MySQLdb.connect(
            host=config.Config.MYSQL_HOST,
            user=config.Config.MYSQL_USER,
            passwd=config.Config.MYSQL_PASSWORD,
            db=config.Config.MYSQL_DB
        )
        cursor = db.cursor()
        
        # Check if status column exists
        cursor.execute("SHOW COLUMNS FROM users LIKE 'status'")
        result = cursor.fetchone()
        
        if not result:
            print("Adding 'status' column to 'users' table...")
            cursor.execute("ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active'")
            db.commit()
            print("Column 'status' added successfully.")
        else:
            print("Column 'status' already exists in 'users' table.")
            
        # Ensure all existing users are 'active'
        cursor.execute("UPDATE users SET status = 'active' WHERE status IS NULL")
        db.commit()
        print("Set existing users to 'active' status.")
        
        cursor.close()
        db.close()
    except Exception as e:
        print(f"Error migrating DB: {e}")

if __name__ == "__main__":
    migrate()
