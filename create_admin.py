from app import create_app, mysql
from werkzeug.security import generate_password_hash

app = create_app()

ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "Adm@10"
ADMIN_NAME = "System Admin"

with app.app_context():
    cur = mysql.connection.cursor()
    
    # Delete any existing admin accounts
    cur.execute("DELETE FROM users WHERE role = 'admin' OR role = 'administrator'")
    mysql.connection.commit()
    
    # Create the one permanent admin
    hashed_pw = generate_password_hash(ADMIN_PASSWORD)
    cur.execute(
        "INSERT INTO users (id, full_name, email, password_hash, role, status) VALUES (%s, %s, %s, %s, %s, %s)",
        ('ADMIN-001', ADMIN_NAME, ADMIN_EMAIL, hashed_pw, 'admin', 'active')
    )
    mysql.connection.commit()
    print(f"Admin account created!\nEmail: {ADMIN_EMAIL}\nPassword: {ADMIN_PASSWORD}")
    
    cur.close()
