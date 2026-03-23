from app import create_app, mysql
import MySQLdb.cursors

app = create_app()
with app.app_context():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    tables = ['attendance', 'student_progress']
    for table in tables:
        try:
            print(f"\n--- {table} ---")
            cur.execute(f"DESCRIBE {table}")
            for row in cur.fetchall():
                print(f"{row['Field']} ({row['Type']})")
        except Exception as e:
            print(f"Error {table}: {e}")
    cur.close()
