from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import UserModel
import re
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

auth_bp = Blueprint('auth', __name__)

# In-memory OTP storage: {email: {"otp": "123456", "verified": False}}
otp_store = {}

# Initialize UserModel inside routes or pass it via constructor
# For simplicity in this setup, we'll assume the mysql object is accessible or use a helper

def get_user_model():
    from flask import current_app
    from app import mysql
    return UserModel(mysql)

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def send_otp_email(receiver_email, otp):
    """Sends a verification code via Gmail SMTP."""
    import os
    from dotenv import load_dotenv
    # Force reload of .env right here to avoid any caching issues
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(dotenv_path=env_path, override=True)
    
    sender_email = os.getenv('MAIL_USERNAME')
    sender_password = os.getenv('MAIL_PASSWORD')
    mail_server = "smtp.gmail.com"

    # Log to a persistent file to confirm execution
    log_file = "otp_debug_log.txt"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n--- New Send Attempt: {receiver_email} ---\n")

    if not sender_email or not sender_password:
        with open(log_file, "a", encoding="utf-8") as f: f.write("❌ Email credentials missing\n")
        print("⚠️ Email credentials not set. Skipping email send.")
        return False
        
    with open(log_file, "a", encoding="utf-8") as f: 
        f.write(f"DEBUG: Using sender {sender_email}, password length: {len(sender_password)}\n")

    # Create Message
    message = MIMEMultipart("alternative")
    message["Subject"] = f"{otp} is your VidyaQuest verification code"
    message["From"] = f"VidyaQuest <{sender_email}>"
    message["To"] = receiver_email.strip()

    # Professional colorful HTML template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .container {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 600px;
                margin: 20px auto;
                padding: 20px;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                background-color: #ffffff;
                box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            }}
            .header {{
                color: #2e7d32;
                font-size: 24px;
                font-weight: bold;
                text-align: center;
                margin-bottom: 20px;
            }}
            .content {{
                color: #424242;
                font-size: 16px;
                line-height: 1.6;
                text-align: center;
            }}
            .otp-container {{
                background-color: #f1f8e9;
                border-radius: 8px;
                padding: 20px;
                margin: 30px auto;
                width: fit-content;
                min-width: 200px;
                letter-spacing: 12px;
                font-size: 36px;
                font-weight: bold;
                color: #2e7d32;
                border: 2px dashed #a5d6a7;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #eeeeee;
                font-size: 12px;
                color: #9e9e9e;
                text-align: center;
            }}
            .brand {{
                color: #2e7d32;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">Welcome to VidyaQuest!</div>
            <div class="content">
                <p>Thank you for joining our community. Please use the following One-Time Password (OTP) to verify your account:</p>
                <div class="otp-container">{otp}</div>
                <p>This code will expire shortly. If you did not request this code, please ignore this email.</p>
            </div>
            <div class="footer">
                Together we learn. Together we grow.<br>
                &copy; 2026 <span class="brand">VidyaQuest</span>. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text fallback
    text = f"Welcome to VidyaQuest! Your verification code is: {otp}"
    
    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    try:
        print(f"DEBUG: Sending professional OTP email to '{receiver_email}' via {mail_server} (SSL)...")
        with smtplib.SMTP_SSL(mail_server, 465) as server:
            server.set_debuglevel(1)
            server.login(sender_email, sender_password)
            server.send_message(message) # Better than sendmail for MIMEMultipart
        
        with open(log_file, "a", encoding="utf-8") as f: f.write(f"✅ SUCCESS: Sent to {receiver_email}\n")
        print(f"✅ SUCCESS: Professional OTP email sent to {receiver_email}")
        return True
    except Exception as e:
        error_msg = f"❌ Failed to send OTP email to {receiver_email}: {e}"
        with open(log_file, "a", encoding="utf-8") as f: f.write(f"{error_msg}\n")
        print(error_msg)
        import traceback
        traceback.print_exc()
        return False

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    full_name = (data.get('full_name') or '').strip()
    email = (data.get('email') or '').strip()
    password = (data.get('password') or '').strip()
    grade = data.get('grade')
    school_name = (data.get('school_name') or '').strip()
    subject_expertise = (data.get('subject_expertise') or '').strip()
    role = data.get('role', 'student').lower().strip()
    
    # Block admin registration — admin is a permanent account
    if role in ['admin', 'administrator']:
        return jsonify({"status": "error", "message": "Admin registration is not allowed"}), 403
    
    # All new users (students and teachers) require admin approval before login
    status = 'pending'

    # 1. Validation
    if not all([full_name, email, password]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    if not is_valid_email(email):
        return jsonify({"status": "error", "message": "Invalid email format"}), 400

    if len(password) < 6:
        return jsonify({"status": "error", "message": "Password must be at least 6 characters"}), 400

    user_model = get_user_model()

    # 2. Check if email exists
    if user_model.find_user_by_email(email):
        return jsonify({"status": "error", "message": "Email already exists"}), 409

    # 3. Hash password and save
    pw_hash = generate_password_hash(password)
    # grade might be None (not sent by teachers/admins)
    if user_model.create_user(full_name, email, pw_hash, role, grade, subject_expertise, status):
        return jsonify({"status": "success", "message": "User registered successfully"}), 201
    else:
        return jsonify({"status": "error", "message": "Database error"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password required"}), 400

    user_model = get_user_model()
    user = user_model.find_user_by_email(email)

    if not user:
        return jsonify({"status": "error", "message": "Email not registered"}), 401

    if not check_password_hash(user['password_hash'], password):
        return jsonify({"status": "error", "message": "Incorrect password"}), 401

    if user.get('status') == 'pending':
        return jsonify({"status": "error", "message": "Account pending admin approval"}), 403

    if user.get('status') == 'rejected':
        return jsonify({"status": "error", "message": "Account has been rejected by admin"}), 403

    # Set session
    session['user_id'] = user['id']
    session['user_name'] = user['full_name']
    session['user_role'] = user['role']

    return jsonify({
        "status": "success",
        "message": "Login successful",
        "user": {
            "id": user['id'],
            "full_name": user['full_name'],
            "email": user['email'],
            "role": user['role'],
            "grade": user.get('grade', "8"),
            "subject_expertise": user.get('subject_expertise', ""),
            "must_change_password": user.get('must_change_password', False)
        }
    }), 200

@auth_bp.route('/home', methods=['GET'])
def home():
    if 'user_id' in session:
        return jsonify({
            "status": "success", 
            "message": f"Welcome back, {session['user_name']}!",
            "role": session['user_role']
        }), 200
    
    return jsonify({"status": "error", "message": "Unauthorized. Please login."}), 401

@auth_bp.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return jsonify({"status": "success", "message": "Logged out successfully"}), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"status": "error", "message": "Email is required"}), 400

    user_model = get_user_model()
    user = user_model.find_user_by_email(email)
    
    if not user:
        return jsonify({"status": "error", "message": "Email not found"}), 404

    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    otp_store[email] = {"otp": otp, "verified": False}
    
    # Send actual email
    email_sent = send_otp_email(email, otp)
    
    # Still print to console for debug
    print(f"OTP for {email}: {otp}")
    
    return jsonify({
        "status": "success", 
        "message": "OTP sent successfully" if email_sent else "OTP generated (Email failed, check terminal)",
        "otp_debug": otp # Remove this in production
    }), 200

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    if not email or not otp:
        return jsonify({"status": "error", "message": "Email and OTP are required"}), 400

    if email in otp_store and otp_store[email]["otp"] == otp:
        otp_store[email]["verified"] = True
        return jsonify({"status": "success", "message": "OTP verified successfully"}), 200
    
    return jsonify({"status": "error", "message": "Invalid OTP"}), 400

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    new_password = data.get('password')

    if not email or not new_password:
        return jsonify({"status": "error", "message": "Email and new password are required"}), 400

    if email not in otp_store or not otp_store[email]["verified"]:
        return jsonify({"status": "error", "message": "OTP not verified"}), 403

    pw_hash = generate_password_hash(new_password)
    
    try:
        from app import mysql
        cur = mysql.connection.cursor()
        query = "UPDATE users SET password_hash = %s WHERE email = %s"
        cur.execute(query, (pw_hash, email))
        mysql.connection.commit()
        cur.close()
        
        # Clear OTP after reset
        del otp_store[email]
        
        return jsonify({"status": "success", "message": "Password reset successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@auth_bp.route('/students/<grade>', methods=['GET'])
def get_students(grade):
    user_model = get_user_model()
    if grade.lower() == 'all':
        try:
            from app import mysql
            cur = mysql.connection.cursor()
            query = "SELECT id, full_name, role, grade FROM users WHERE role = 'student'"
            cur.execute(query)
            students_data = cur.fetchall()
            cur.close()
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        students_data = user_model.find_students_by_grade(grade)
    
    # Format for JSON response
    formatted_students = []
    for s in students_data:
        # Check if cursor is returning dicts or tuples
        if isinstance(s, dict):
            formatted_students.append({
                "id": s.get('id'),
                "name": s.get('full_name') or s.get('name'),
                "role": s.get('role'),
                "grade": s.get('grade'),
                "avg_accuracy": s.get('avg_accuracy', 0),
                "progress": s.get('progress', 0.0)
            })
        else: # Tuples (id, full_name, role, grade)
            formatted_students.append({
                "id": s[0],
                "name": s[1],
                "role": s[2],
                "grade": s[3]
            })

    return jsonify({
        "status": "success",
        "data": formatted_students
    }), 200

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "Invalid request body"}), 400

    user_id = data.get('user_id')
    email = data.get('email')
    old_password = data.get('old_password') or data.get('current_password')
    new_password = data.get('new_password')

    if not (user_id or email) or not old_password or not new_password:
        return jsonify({"status": "error", "message": "Identifier (user_id or email), current password, and new password are required"}), 400

    user_model = get_user_model()
    user = None
    if email:
        user = user_model.find_user_by_email(email)
    
    if not user and user_id:
        # Fallback if no email but user_id exists
        try:
            from app import mysql
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()
            cur.close()
        except:
            pass

    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    # Check password
    stored_hash = user['password_hash'] if isinstance(user, dict) else user[4]
    if not check_password_hash(stored_hash, old_password):
        return jsonify({"status": "error", "message": "Current password is incorrect"}), 401

    if len(new_password) < 6:
        return jsonify({"status": "error", "message": "New password must be at least 6 characters"}), 400

    # Update password and clear must_change_password flag
    new_hash = generate_password_hash(new_password)
    identifier = user['id'] if isinstance(user, dict) else user[0]
    
    try:
        from app import mysql
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET password_hash = %s, must_change_password = 'no' WHERE id = %s", (new_hash, identifier))
        mysql.connection.commit()
        cur.close()
        return jsonify({"status": "success", "message": "Password changed successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
