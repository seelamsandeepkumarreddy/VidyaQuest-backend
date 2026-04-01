from flask import Blueprint, jsonify, request
from models import UserModel

admin_bp = Blueprint('admin', __name__)

def get_user_model():
    from app import mysql
    return UserModel(mysql)

def get_attendance_model():
    from app import mysql
    from models import AttendanceModel
    return AttendanceModel(mysql)

@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    user_model = get_user_model()
    stats = user_model.get_admin_stats()

    if stats:
        return jsonify({
            "status": "success",
            "data": {
                "student_count": stats['student_count'],
                "teacher_count": stats['teacher_count'],
                "avg_accuracy": stats['avg_accuracy'],
                "school_progress": stats.get('school_progress', 0.0),
                "quiz_completion_rate": stats.get('quiz_completion_rate', 0.0),
                "daily_active_users": stats.get('daily_active_users', 0.0),
                "recent_activities": []
            }
        }), 200
    
    return jsonify({"status": "error", "message": "Failed to fetch stats"}), 500

@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    user_model = get_user_model()
    users = user_model.get_all_users()
    
    # Optional role filter from query param: ?role=student or ?role=teacher
    role_filter = request.args.get('role', '').lower()
    
    formatted_users = []
    for u in users:
        if isinstance(u, dict):
            id_val = u.get('id')
            name = u.get('full_name', '')
            email = u.get('email', '')
            role = (u.get('role', '') or '').strip()
            status = (u.get('status', 'active') or 'active').strip()
            grade = u.get('grade', '')
            subject_expertise = u.get('subject_expertise', '')
        else:
            id_val = u[0]
            name = u[1]
            email = u[2]
            role = (u[3] or '').strip()
            status = (u[4] or 'active').strip()
            grade = u[5]
            subject_expertise = u[6] if len(u) > 6 else ''

        # Apply role filter if specified
        if role_filter:
            if role_filter == 'student' and role.lower() != 'student':
                continue
            if role_filter in ('teacher', 'faculty') and role.lower() not in ('teacher', 'faculty'):
                continue

        # Determine display role and details
        low_role = role.lower()
        display_role = role.capitalize() if role else 'Unknown'
        if low_role == 'student':
            details = f"Grade {grade}" if grade else "Student"
        elif low_role in ('faculty', 'teacher'):
            # Show both subject and assigned grade for teachers
            expertise_str = f"Exp: {subject_expertise}" if subject_expertise else ""
            grade_str = f"Grade: {grade}" if grade else ""
            details = " | ".join(filter(None, [expertise_str, grade_str])) or "Teacher"
        elif low_role in ('admin', 'administrator'):
            details = "Administrator"
        else:
            details = "Staff"

        formatted_users.append({
            "id": str(id_val),
            "name": str(name).strip(),
            "email": str(email).strip(),
            "role": display_role,
            "details": str(details).strip(),
            "status": status
        })
    
    return jsonify({"status": "success", "data": formatted_users}), 200

@admin_bp.route('/approve-user/<user_id>', methods=['POST'])
def approve_user(user_id):
    user_model = get_user_model()
    success = user_model.approve_user(user_id)
    if success:
        return jsonify({"status": "success", "message": "User approved successfully"}), 200
    return jsonify({"status": "error", "message": "Failed to approve user"}), 500

@admin_bp.route('/create-user', methods=['POST'])
def create_user_admin():
    data = request.get_json()
    full_name = (data.get('full_name') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password')
    role = data.get('role', 'student').lower()
    grade = data.get('grade')
    subject_expertise = (data.get('subject_expertise') or '').strip()

    # Email Validation - Accept allowed domains
    allowed_domains = ['@gmail.com', '@saveetha.com', '@saveetha.ac.in', '@yahoo.com', '@outlook.com']
    if not any(email.lower().endswith(domain) for domain in allowed_domains):
        print(f"DEBUG: Rejected non-allowed email: '{email}'")
        return jsonify({"status": "error", "message": "Email is not valid"}), 400

    if not all([full_name, email]):
        return jsonify({"status": "error", "message": "Missing name or email"}), 400

    user_model = get_user_model()
    
    # Check if email exists
    if user_model.find_user_by_email(email):
        return jsonify({"status": "error", "message": "Email already exists"}), 409

    # Password Handling - Always force change for admin-created users
    must_change = 'yes'
    if not password:
        # Auto-generate password (Generic 8-char random alphanumeric)
        import random
        import string
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    from werkzeug.security import generate_password_hash
    pw_hash = generate_password_hash(password)
    
    # Admin-created users are 'active' by default
    success = user_model.create_user(
        full_name, email, pw_hash, role, 
        grade, subject_expertise, 
        status='active',
        must_change_password=must_change
    )
    
    if success:
        msg = f"User created successfully. Temporary Password: {password}" if must_change else "User created successfully"
        return jsonify({"status": "success", "message": msg}), 200
    return jsonify({"status": "error", "message": "Failed to create user"}), 500

@admin_bp.route('/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_user(user_id):
    user_model = get_user_model()
    if request.method == 'GET':
        user_details = user_model.get_user_full_details(user_id)
        if user_details:
            return jsonify({"status": "success", "data": user_details}), 200
        return jsonify({"status": "error", "message": "User not found"}), 404
    
    if request.method == 'DELETE':
        success = user_model.delete_user(user_id)
        if success:
            return jsonify({"status": "success", "message": "User deleted successfully"}), 200
        return jsonify({"status": "error", "message": "Failed to delete user"}), 500
    
    elif request.method == 'PUT':
        data = request.json
        success = user_model.update_user(user_id, data)
        if success:
            return jsonify({"status": "success", "message": "User updated successfully"}), 200
        return jsonify({"status": "error", "message": "Failed to update user"}), 500

@admin_bp.route('/content/recent', methods=['GET'])
def get_recent_content():
    user_model = get_user_model()
    uploads = user_model.get_recent_uploads()
    
    formatted_uploads = []
    for up in uploads:
        if isinstance(up, dict):
            title = up.get('title')
            content_type = up.get('type')
            time = up.get('created_at').strftime("%Y-%m-%d %H:%M") if up.get('created_at') else "Just now"
        else:
            title = up[0]
            content_type = up[1]
            time = up[2].strftime("%Y-%m-%d %H:%M") if up[2] else "Just now"
            
        formatted_uploads.append({
            "title": title[:30] + "..." if len(title) > 30 else title,
            "subject": "System",
            "type": content_type,
            "time": time
        })
        
    return jsonify({"status": "success", "data": formatted_uploads}), 200

@admin_bp.route('/analytics/detailed', methods=['GET'])
def get_detailed_analytics():
    user_model = get_user_model()
    analytics = user_model.get_detailed_analytics()
    if analytics:
        return jsonify({"status": "success", "data": analytics}), 200
    return jsonify({"status": "error", "message": "Failed to fetch analytics"}), 500

@admin_bp.route('/attendance/summary', methods=['GET'])
def get_attendance_summary():
    attendance_model = get_attendance_model()
    rate = attendance_model.get_overall_attendance_stats()
    return jsonify({"status": "success", "data": {"overall_rate": rate}}), 200

@admin_bp.route('/notifications', methods=['GET'])
def get_notifications():
    user_model = get_user_model()
    notifications = user_model.get_admin_notifications()
    
    formatted = []
    for n in notifications:
        if isinstance(n, dict):
            ntype = n.get('type')
            title = n.get('title')
            msg = n.get('message')
            time = n.get('created_at').strftime("%Y-%m-%d %H:%M") if n.get('created_at') else "Just now"
        else:
            ntype = n[0]
            title = n[1]
            msg = n[2]
            time = n[3].strftime("%Y-%m-%d %H:%M") if n[3] else "Just now"
            
        formatted.append({
            "type": ntype,
            "title": title,
            "message": msg,
            "time": time
        })
        
    return jsonify({"status": "success", "data": formatted}), 200
