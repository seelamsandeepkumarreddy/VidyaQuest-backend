import sys
import io
from app import create_app, mysql

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = create_app()
with app.app_context():
    cur = mysql.connection.cursor()
    
    # Total questions
    cur.execute("SELECT COUNT(*) FROM questions")
    row = cur.fetchone()
    total = row['COUNT(*)'] if isinstance(row, dict) else row[0]
    
    # Placeholder count
    cur.execute("SELECT COUNT(*) FROM questions WHERE question_text LIKE 'Review Question%'")
    row = cur.fetchone()
    placeholders = row['COUNT(*)'] if isinstance(row, dict) else row[0]
    
    # Good questions (not placeholders)
    cur.execute("SELECT id, question_text FROM questions WHERE question_text NOT LIKE 'Review Question%'")
    good_samples = cur.fetchall()
    
    print(f"Total Questions: {total}")
    print(f"Placeholder Questions: {placeholders}")
    print(f"Real Questions (to keep): {total - placeholders}")
    print("\nListing Real Questions:")
    for g in good_samples:
        text = g['question_text'] if isinstance(g, dict) else g[1]
        print(f" - {text}")
        
    cur.close()
