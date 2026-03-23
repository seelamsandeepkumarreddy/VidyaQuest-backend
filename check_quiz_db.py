import sys
import io
from app import create_app, mysql
import json

# Force UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = create_app()
with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("DESCRIBE questions")
    schema = cur.fetchall()
    print("Schema of 'questions' table:")
    for column in schema:
        print(column)
    
    cur.execute("SELECT COUNT(*) FROM questions")
    count = cur.fetchone()
    print(f"\nTotal questions in DB: {count}")
    
    cur.execute("SELECT id, chapter_id, question_text FROM questions LIMIT 5")
    sample = cur.fetchall()
    print("\nSample questions (first 5):")
    for s in sample:
        print(s)
        
    cur.close()
