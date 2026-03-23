import MySQLdb
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

def restore_admin():
    try:
        db = MySQLdb.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            passwd=os.getenv('MYSQL_PASSWORD'),
            db=os.getenv('MYSQL_DB')
        )
        cur = db.cursor()
        
        email = 'vqadmin1@gmail.com'
        password = 'Adminvq@10'
        password_hash = generate_password_hash(password)
        
        print(f"Checking for existing user with email: {email}")
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        
        if user:
            user_id = user[0]
            print(f"User exists with ID: {user_id}. Updating password and role.")
            cur.execute("UPDATE users SET password_hash = %s, role = %s, status = %s WHERE id = %s", 
                       (password_hash, 'admin', 'active', user_id))
        else:
            print("User does not exist. Creating new admin user.")
            # Generate a new ID for admin
            cur.execute("SELECT id FROM users WHERE id LIKE 'VQA%' ORDER BY id DESC LIMIT 1")
            last_admin = cur.fetchone()
            if last_admin:
                last_id = last_admin[0]
                last_num = int(last_id[3:])
                next_num = last_num + 1
            else:
                next_num = 1
            new_id = f"VQA{next_num:03d}"
            
            cur.execute("INSERT INTO users (id, full_name, email, password_hash, role, status) VALUES (%s, %s, %s, %s, %s, %s)",
                       (new_id, 'Admin User', email, password_hash, 'admin', 'active'))
            user_id = new_id

        # Ensure entry in admins table
        cur.execute("SELECT user_id FROM admins WHERE user_id = %s", (user_id,))
        admin_entry = cur.fetchone()
        if not admin_entry:
            cur.execute("INSERT INTO admins (user_id) VALUES (%s)", (user_id,))
            
        # Deactivate any OTHER admin users
        print("Deactivating other admin accounts...")
        cur.execute("UPDATE users SET status = 'inactive' WHERE role = 'admin' AND email != %s", (email,))
        
        db.commit()
        print(f"Successfully restored admin: {email}")
        db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    restore_admin()
