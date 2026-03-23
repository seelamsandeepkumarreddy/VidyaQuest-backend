from app import create_app, mysql

app = create_app()
with app.app_context():
    cur = mysql.connection.cursor()
    try:
        print("Migrating attendance table...")
        # Check if table exists and drop it to recreate simply, or alter. 
        # Recreating is cleaner if we don't care about data.
        cur.execute("DROP TABLE IF EXISTS attendance")
        cur.execute("""
            CREATE TABLE attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(20) NOT NULL,
                grade VARCHAR(10) NOT NULL,
                date DATE NOT NULL,
                status VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_attendance (student_id, date)
            )
        """)
        mysql.connection.commit()
        print("Attendance table migrated successfully.")
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        cur.close()
