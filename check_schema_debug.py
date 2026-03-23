from app import create_app, mysql
import MySQLdb.cursors

app = create_app()
with app.app_context():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cur.execute("DESCRIBE attendance")
        columns = cur.fetchall()
        print("Attendance Table Schema:")
        for col in columns:
            print(col)
            
        cur.execute("DESCRIBE student_progress")
        print("\nStudent Progress Table Schema:")
        for col in cur.fetchall():
            print(col)
            
        cur.execute("DESCRIBE quiz_progress")
        print("\nQuiz Progress Table Schema:")
        for col in cur.fetchall():
            print(col)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
