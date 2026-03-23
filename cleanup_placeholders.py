"""
Cleanup script to remove "Review Question" placeholder entries from the questions table.
These placeholders override the app's built-in dynamic question generator.
"""
import sys
import io
from app import create_app, mysql

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = create_app()
with app.app_context():
    cur = mysql.connection.cursor()

    # Count placeholders before deletion
    cur.execute("SELECT COUNT(*) as cnt FROM questions WHERE question_text LIKE 'Review Question%'")
    row = cur.fetchone()
    placeholder_count = row['cnt'] if isinstance(row, dict) else row[0]

    # Count total before
    cur.execute("SELECT COUNT(*) as cnt FROM questions")
    row = cur.fetchone()
    total_before = row['cnt'] if isinstance(row, dict) else row[0]

    print(f"Total questions before cleanup: {total_before}")
    print(f"Placeholder questions to delete: {placeholder_count}")
    print(f"Real questions to keep: {total_before - placeholder_count}")

    if placeholder_count > 0:
        # Delete the placeholders
        cur.execute("DELETE FROM questions WHERE question_text LIKE 'Review Question%'")
        mysql.connection.commit()
        print(f"\n✅ Successfully deleted {placeholder_count} placeholder questions.")
    else:
        print("\n✅ No placeholder questions found. Database is clean.")

    # Verify
    cur.execute("SELECT COUNT(*) as cnt FROM questions")
    row = cur.fetchone()
    total_after = row['cnt'] if isinstance(row, dict) else row[0]
    print(f"Total questions after cleanup: {total_after}")

    cur.close()
