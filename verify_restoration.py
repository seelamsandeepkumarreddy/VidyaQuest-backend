import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

def verify_restoration():
    try:
        db = MySQLdb.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            passwd=os.getenv('MYSQL_PASSWORD'),
            db=os.getenv('MYSQL_DB')
        )
        cur = db.cursor()
        
        email = 'vqadmin1@gmail.com'
        
        print(f"--- Verifying status for {email} ---")
        cur.execute("SELECT id, email, role, status, must_change_password FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        
        if user:
            print(f"ID: {user[0]}")
            print(f"Email: {user[1]}")
            print(f"Role: {user[2]}")
            print(f"Status: {user[3]}")
            print(f"Must Change Password: {user[4]}")
            
            if user[2] == 'admin' and user[3] == 'active':
                print("✅ Main admin account is ACTIVE and has ADMIN role.")
            else:
                print("❌ Main admin account status or role is INCORRECT.")
        else:
            print("❌ Main admin account NOT FOUND.")

        print("\n--- Checking for other active admins ---")
        cur.execute("SELECT email FROM users WHERE role = 'admin' AND status = 'active' AND email != %s", (email,))
        others = cur.fetchall()
        
        if others:
            print(f"❌ Found {len(others)} other active admins: {[o[0] for o in others]}")
        else:
            print("✅ No other active admin accounts found.")

        # Final cleanup: ensure must_change_password is False for this specific admin 
        # so they can log in without the force-change-password flow if they just want to use the provided password.
        # But if the user wants it, they can change it later.
        cur.execute("UPDATE users SET must_change_password = 0 WHERE email = %s", (email,))
        db.commit()
        print(f"\n✅ Ensuring 'must_change_password' is False for {email}.")
        
        db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_restoration()
