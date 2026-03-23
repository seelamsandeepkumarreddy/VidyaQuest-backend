import sys
import io
from app import create_app, mysql

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = create_app()
with app.app_context():
    cur = mysql.connection.cursor()
    # Find unique question texts that are likely placeholders
    cur.execute("""
        SELECT question_text, COUNT(*) as cnt
        FROM questions 
        GROUP BY question_text 
        HAVING cnt > 1 OR question_text LIKE 'Review Question%'
    """)
    placeholders = cur.fetchall()
    print("Potential placeholders found:")
    for p in placeholders:
        text = p['question_text'] if isinstance(p, dict) else p[0]
        cnt = p['cnt'] if isinstance(p, dict) else p[1]
        print(f"Text: '{text}' | Count: {cnt}")
        
    cur.close()
