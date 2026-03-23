
import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

def check_users():
    conn = MySQLdb.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER"),
        passwd=os.getenv("MYSQL_PASSWORD"),
        db=os.getenv("MYSQL_DB")
    )
    cur = conn.cursor()
    cur.execute("SELECT id, full_name, role, status FROM users")
    users = cur.fetchall()
    print(f"Total Users: {len(users)}")
    for u in users:
        print(f"ID: {u[0]}, Name: {u[1]}, Role: '{u[2]}', Status: {u[3]}")
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_users()
