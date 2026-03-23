
import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

def cleanup_db():
    conn = MySQLdb.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER"),
        passwd=os.getenv("MYSQL_PASSWORD"),
        db=os.getenv("MYSQL_DB")
    )
    cur = conn.cursor()
    
    # 1. Strip all roles, statuses, and full names
    cur.execute("SELECT id, role, status, full_name FROM users")
    users = cur.fetchall()
    for u in users:
        id_val = u[0]
        role = str(u[1]).strip().lower()
        status = str(u[2]).strip().lower()
        name = str(u[3]).strip()
        
        # Correct role for ADMIN-001 if needed
        if id_val == 'ADMIN-001':
            role = 'admin'
            
        cur.execute("UPDATE users SET role = %s, status = %s, full_name = %s WHERE id = %s", (role, status, name, id_val))
    
    conn.commit()
    print(f"Cleaned up {len(users)} users.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    cleanup_db()
