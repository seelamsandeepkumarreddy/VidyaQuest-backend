from app import create_app, mysql
from models import UserModel
from werkzeug.security import check_password_hash

app = create_app()

with app.app_context():
    email = "admin@gmail.com"
    password = "Adm@10"
    
    user_model = UserModel(mysql)
    user = user_model.find_user_by_email(email)
    
    if not user:
        print("FAIL: User not found in DB")
    else:
        print(f"DEBUG: Found user: {user}")
        if check_password_hash(user['password_hash'], password):
            print("SUCCESS: Password verified")
            # Mimic the jsonify part
            try:
                user_data = {
                    "id": user['id'],
                    "full_name": user['full_name'],
                    "email": user['email'],
                    "role": user['role'],
                    "grade": user.get('grade', "8"),
                    "school_name": user.get('school_name', ""),
                    "subject_expertise": user.get('subject_expertise', ""),
                    "experience": user.get('experience', "")
                }
                print(f"DEBUG: User data for response: {user_data}")
            except Exception as e:
                print(f"FAIL: Error constructing response data: {e}")
        else:
            print("FAIL: Password verification failed")
