from app import create_app, mysql
import MySQLdb.cursors
import json

app = create_app()
with app.app_context():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    tables = ['attendance', 'students', 'users', 'student_progress', 'quiz_progress']
    schema = {}
    for table in tables:
        try:
            cur.execute(f"DESCRIBE {table}")
            schema[table] = cur.fetchall()
        except Exception as e:
            schema[table] = str(e)
    
    print(json.dumps(schema, indent=2, default=str))
    cur.close()
