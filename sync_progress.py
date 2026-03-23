
import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

def sync_data():
    conn = MySQLdb.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER"),
        passwd=os.getenv("MYSQL_PASSWORD"),
        db=os.getenv("MYSQL_DB")
    )
    cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    
    # 1. Sync from quiz_progress to students
    print("--- Syncing from quiz_progress to students ---")
    cur.execute("""
        SELECT 
            user_id, 
            SUM(xp) as total_xp, 
            COUNT(*) as q_count,
            SUM(CASE WHEN score = 100 THEN 1 ELSE 0 END) as perfects,
            SUM(CASE WHEN score >= 80 THEN 1 ELSE 0 END) as high_acc
        FROM quiz_progress
        GROUP BY user_id
    """)
    quiz_stats = cur.fetchall()
    
    for s in quiz_stats:
        print(f"Updating user {s['user_id']}: XP={s['total_xp']}, Quizzes={s['q_count']}")
        cur.execute("""
            UPDATE students 
            SET total_xp = %s, quiz_count = %s, perfect_quizzes = %s, high_accuracy_quizzes = %s
            WHERE user_id = %s
        """, (s['total_xp'], s['q_count'], s['perfects'], s['high_acc'], s['user_id']))

    # 2. Migration from student_progress (legacy) if values are higher
    print("\n--- Migrating from legacy student_progress ---")
    cur.execute("SELECT student_id, xp, lessons_completed, quiz_accuracy, study_time_minutes FROM student_progress")
    legacy_data = cur.fetchall()
    
    for ld in legacy_data:
        # Check if student exists in current students table
        cur.execute("SELECT total_xp FROM students WHERE user_id = %s", (ld['student_id'],))
        current = cur.fetchone()
        
        if current:
            # If legacy XP is higher, we update it to preserve progress
            if ld['xp'] > current['total_xp']:
                print(f"Overriding XP for {ld['student_id']}: {current['total_xp']} -> {ld['xp']} (Legacy)")
                cur.execute("UPDATE students SET total_xp = %s WHERE user_id = %s", (ld['xp'], ld['student_id']))
            
            # Update study time if not set
            cur.execute("UPDATE students SET total_study_time = total_study_time + %s WHERE user_id = %s", (ld['study_time_minutes'], ld['student_id']))
        else:
            print(f"User {ld['student_id']} from legacy table not found in current students table.")

    conn.commit()
    print("\nSync Complete!")
    cur.close()
    conn.close()

if __name__ == "__main__":
    sync_data()
