import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

def manual_delete(user_id):
    try:
        db = MySQLdb.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            passwd=os.getenv('MYSQL_PASSWORD'),
            db=os.getenv('MYSQL_DB')
        )
        cur = db.cursor()
        
        print(f"--- Attempting manual delete for {user_id} ---")
        
        print("1. Disabling FK checks")
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        for table in ['students', 'teachers', 'quiz_progress', 'student_progress']:
            print(f"2. Deleting from {table}")
            try:
                cur.execute(f"DELETE FROM {table} WHERE user_id = %s", (user_id,))
                print(f"   {table}: OK")
            except Exception as e:
                print(f"   {table}: Error: {e}")
                # Try with student_id if user_id failed for student_progress
                if table == 'student_progress':
                    try:
                        cur.execute(f"DELETE FROM {table} WHERE student_id = %s", (user_id,))
                        print(f"   {table} (student_id): OK")
                    except Exception as e2:
                        print(f"   {table} (student_id): Error: {e2}")

        print("3. Deleting from users")
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        print("   users: OK")
        
        print("4. Enabling FK checks")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        print("5. Committing")
        db.commit()
        print("Commit: OK")
        
        db.close()
        print("Success!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Global Error: {e}")

if __name__ == "__main__":
    # Test with one of the recently created test users
    manual_delete('VQ-2026024')
