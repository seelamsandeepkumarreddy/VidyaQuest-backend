from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from config import Config
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Extensions
mysql = MySQL()

# Configure Gemini AI - Support for multiple keys
api_keys = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3"),
    os.getenv("GEMINI_API_KEY_4"),
    os.getenv("GEMINI_API_KEY_5")
]
api_keys = [k for k in api_keys if k and k != "your_api_key_here"]

if not api_keys:
    print("WARNING: No GEMINI_API_KEYs found. AI will not work.")
    current_key_index = -1
else:
    genai.configure(api_key=api_keys[0])
    current_key_index = 0

# Initialize the model with a STRICT system instruction
SYSTEM_INSTRUCTION = """
You are the RuralQuest Learning Assistant, a specialized AI tutor for Grade 8, 9, and 10 students.

STRICT DOMAIN POLICY:
1. ONLY answer questions related to school subjects (Math, Science, English, Social Studies, etc.) and the RuralQuest app features (XP, Leaderboard, Courses, etc.).
2. If a student asks anything UNRELATED to education or the app (e.g., entertainment, food, general trivia, politics, sports), you MUST refuse politely.
3. REFUSAL MESSAGE: "I am sorry, I can only help you with questions related to your studies or the RuralQuest app. Let's get back to learning! 😊"
4. Use simple English and rural-friendly examples.
5. Keep answers concise.
"""

def get_gemini_model(key):
    genai.configure(api_key=key)
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )

model = get_gemini_model(api_keys[0]) if api_keys else None

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize MySQL with app
    mysql.init_app(app)

    # Enable CORS
    CORS(app)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.courses import courses_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(courses_bp, url_prefix='/api/courses')

    # --- Root Status Page ---
    @app.route('/')
    def index():
        return '''<!DOCTYPE html>
<html>
<head>
    <title>VidyaQuest Backend</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; color: #fff; }
        .card { background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius: 24px; padding: 48px; text-align: center; max-width: 500px; box-shadow: 0 8px 32px rgba(0,0,0,0.2); }
        h1 { font-size: 32px; margin-bottom: 8px; }
        .status { display: inline-block; background: #4CAF50; color: #fff; padding: 8px 24px; border-radius: 20px; font-weight: bold; font-size: 14px; margin: 16px 0; }
        p { opacity: 0.85; line-height: 1.6; }
        .endpoints { text-align: left; background: rgba(0,0,0,0.2); border-radius: 12px; padding: 16px 24px; margin-top: 24px; font-size: 13px; }
        .endpoints code { background: rgba(255,255,255,0.15); padding: 2px 8px; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🎓 VidyaQuest</h1>
        <p style="font-size:18px; opacity:1;">Backend API Server</p>
        <div class="status">✅ RUNNING</div>
        <p>The backend is online and ready to serve the VidyaQuest mobile app.</p>
        <div class="endpoints">
            <strong>API Endpoints:</strong><br>
            <code>GET /api/health</code> — Health check<br>
            <code>POST /api/login</code> — User login<br>
            <code>POST /api/register</code> — Registration<br>
            <code>GET /api/courses/subjects/:grade</code> — Get subjects<br>
            <code>GET /api/progress/:user_id</code> — Get progress
        </div>
    </div>
</body>
</html>''', 200

    @app.route('/api/health')
    def health_check():
        return jsonify({"status": "success", "message": "VidyaQuest Backend is running"}), 200

    @app.before_request
    def log_request_info():
        print(f"DEBUG: Request to {request.path} [{request.method}]")

    # --- PROGRESS & STUDY ROUTES (Handling both /api and non-api just in case) ---
    # Import the new models
    from models import AttendanceModel, AnnouncementModel, ProgressModel, QuizProgressModel, UserModel, AssignmentModel, DailyChallengeModel, SpeechProgressModel
    attendance_model = AttendanceModel(mysql)
    announcements_model = AnnouncementModel(mysql)
    progress_model = ProgressModel(mysql)
    quiz_progress_model = QuizProgressModel(mysql)
    user_model = UserModel(mysql)
    assignment_model = AssignmentModel(mysql)
    challenge_model = DailyChallengeModel(mysql)
    speech_model = SpeechProgressModel(mysql)

    # --- SPEECH TRAINING ROUTES ---
    @app.route('/api/speech/save', methods=['POST'])
    def save_speech_progress():
        try:
            data = request.json
            user_id = data.get('user_id')
            category = data.get('category')
            accuracy = data.get('accuracy')
            words_count = data.get('words_count')
            
            if not all([user_id, category, accuracy is not None, words_count is not None]):
                return jsonify({"status": "error", "message": "Missing required fields"}), 400
                
            success = speech_model.save_speech_session(user_id, category, accuracy, words_count)
            if success:
                return jsonify({"status": "success", "message": "Speech session saved"}), 200
            return jsonify({"status": "error", "message": "Failed to save session"}), 500
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/api/speech/stats/<string:user_id>', methods=['GET'])
    def get_speech_stats(user_id):
        try:
            stats = speech_model.get_speech_stats(user_id)
            formatted_stats = []
            for s in stats:
                if isinstance(s, dict):
                    formatted_stats.append({
                        "category": s['category'],
                        "avg_accuracy": int(s['avg_accuracy']),
                        "total_words": int(s['total_words'])
                    })
                else:
                    # MySQL tuple: (category, avg_accuracy, total_words)
                    formatted_stats.append({
                        "category": s[0],
                        "avg_accuracy": int(s[1]),
                        "total_words": int(s[2])
                    })
            return jsonify({"status": "success", "data": formatted_stats}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    # --- PROGRESS ROUTES ---
    @app.route('/api/progress/<string:user_id>', methods=['GET'])
    @app.route('/progress/<string:user_id>', methods=['GET'])
    def get_progress(user_id):
        try:
            # First try to get aggregate stats from user table
            progress = user_model.get_user_progress(user_id)
            if progress:
                return jsonify({
                    "status": "success",
                    "data": progress
                }), 200
            
            # Fallback to old progress model if student stats are zero or missing
            # A student might exist in 'students' table but have no recorded XP yet (new table setup)
            if not progress or (progress.get('total_xp', 0) == 0 and progress.get('quiz_count', 0) == 0):
                progress_old = progress_model.get_progress(user_id)
                if progress_old:
                    # Handle both dict and tuple returns
                    if isinstance(progress_old, dict):
                        old_data = {
                            "total_xp": progress_old.get('xp', 0) or 0,
                            "lessons_completed": progress_old.get('lessons_completed', 0) or 0,
                            "average_accuracy": progress_old.get('quiz_accuracy', 0) or 0,
                            "total_study_time": progress_old.get('study_time_minutes', 0) or 0
                        }
                    else:
                        old_data = {
                            "total_xp": progress_old[0] or 0,
                            "lessons_completed": progress_old[1] or 0,
                            "average_accuracy": progress_old[2] or 0,
                            "total_study_time": progress_old[3] or 0
                        }
                    
                    if progress:
                        # We have the new model format, just patch in the old XP if it's there
                        if old_data["total_xp"] > 0:
                            progress.update(old_data)
                            progress["quiz_count"] = old_data["lessons_completed"]
                        return jsonify({"status": "success", "data": progress}), 200
                    else:
                        # Standardize to full ProgressData model if only old data exists
                        return jsonify({
                            "status": "success",
                            "data": {
                                "total_xp": old_data["total_xp"],
                                "streak": 0,
                                "perfect_quizzes": 0,
                                "high_accuracy_quizzes": 0,
                                "average_accuracy": old_data["average_accuracy"],
                                "quiz_count": old_data["lessons_completed"],
                                "total_study_time": old_data["total_study_time"],
                                "weekly_xp": 0,
                                "completed_chapters": {},
                                "earned_badges": {}
                            }
                        }), 200
            
            if progress:
                return jsonify({
                    "status": "success",
                    "data": progress
                }), 200
            return jsonify({"status": "error", "message": "Progress not found"}), 404
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/api/progress/save', methods=['POST'])
    @app.route('/progress/save', methods=['POST'])
    def save_progress():
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "Data required"}), 400
            
        # Support both 'user_id' (Android) and 'student_id' (Legacy)
        user_id = data.get('user_id') or data.get('student_id')
        if not user_id:
            return jsonify({"status": "error", "message": "user_id is required"}), 400
            
        xp = data.get('xp', 0)
        score = data.get('score', data.get('quiz_accuracy', 0))
        grade = data.get('grade')
        subject = data.get('subject')
        chapter = data.get('chapter')
        badge = data.get('badge')
        study_time = data.get('study_time_minutes', 5)

        # 1. Update Aggregate Stats in Students Table
        user_model.update_user_stats(user_id, xp, score)
        user_model.save_study_time(user_id, study_time)
        
        # 2. Save Detailed Quiz History
        quiz_progress_model.save_quiz_result(user_id, grade, subject, chapter, score, xp, badge)
        
        # 3. Update legacy progress table for backward compatibility
        progress_model.update_progress(
            student_id=user_id,
            xp=xp,
            lessons_completed=data.get('lessons_completed', 1 if chapter else 0),
            quiz_accuracy=score,
            study_time_minutes=study_time
        )
        
        return jsonify({"status": "success", "message": "Progress saved"}), 200

    @app.route('/api/study/save', methods=['POST'])
    def save_study_time():
        data = request.json
        if not data or 'user_id' not in data or 'minutes' not in data:
            return jsonify({"status": "error", "message": "user_id and minutes required"}), 400
            
        success = user_model.save_study_time(data['user_id'], data['minutes'])
        if success:
            return jsonify({"status": "success", "message": "Study time saved"}), 200
        return jsonify({"status": "error", "message": "Failed to save study time"}), 500

    # --- ANALYTICS ROUTE ---
    @app.route('/api/analytics/grade/<grade>', methods=['GET'])
    def get_grade_analytics(grade):
        try:
            stats = user_model.get_grade_analytics(grade)
            if stats:
                return jsonify({
                    "status": "success",
                    "data": stats
                }), 200
            return jsonify({"status": "error", "message": "Analytics not found"}), 404
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    # --- USER SETTINGS ROUTES ---
    @app.route('/api/user/settings/<string:user_id>', methods=['GET'])
    def get_user_settings(user_id):
        try:
            settings = user_model.get_user_settings(user_id)
            return jsonify({
                "status": "success",
                "data": settings
            }), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/api/user/settings', methods=['POST'])
    def update_user_settings():
        try:
            data = request.json
            user_id = data.get('user_id')
            settings = data.get('settings')
            if not user_id or settings is None:
                return jsonify({"status": "error", "message": "user_id and settings required"}), 400
            
            success = user_model.update_user_settings(user_id, settings)
            if success:
                return jsonify({"status": "success", "message": "Settings updated"}), 200
            return jsonify({"status": "error", "message": "Failed to update settings"}), 500
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    # --- LEADERBOARD ROUTE ---
    @app.route('/api/leaderboard/<grade>', methods=['GET'])
    def get_leaderboard(grade):
        try:
            cur = mysql.connection.cursor()
            # Get all students for this grade with their XP
            cur.execute("""
                SELECT u.id, u.full_name, COALESCE(s.total_xp, 0) as total_xp
                FROM users u
                JOIN students s ON u.id = s.user_id
                WHERE u.role = 'student' AND s.grade = %s
                ORDER BY total_xp DESC
            """, (grade,))
            rows = cur.fetchall()
            
            students = []
            for row in rows:
                if isinstance(row, dict):
                    students.append({
                        "id": row['id'],
                        "name": row['full_name'],
                        "xp": row.get('total_xp', 0) or 0
                    })
                else:
                    students.append({
                        "id": row[0],
                        "name": row[1],
                        "xp": row[2] or 0
                    })
            cur.close()
            return jsonify({"status": "success", "data": students}), 200
        except Exception as e:
            print(f"Leaderboard error: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    # --- ATTENDANCE ROUTES ---
    @app.route('/api/attendance', methods=['POST'])
    def submit_attendance():
        data = request.json
        if not data or 'grade' not in data:
            return jsonify({"status": "error", "message": "Grade is required"}), 400
            
        grade = data['grade']
        # Default to today if date not provided
        from datetime import date as dt, datetime, timedelta
        date = data.get('date') or dt.today().isoformat()
        
        ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
        
        # New Batch Format Support (from Android AttendanceRequest)
        absent_ids = []
        if 'absent_students' in data and data['absent_students']:
            # absent_students is List<Pair<String, Int>> or similar, usually [["Name", "ID"], ...]
            for pair in data['absent_students']:
                if isinstance(pair, list) and len(pair) > 1:
                    absent_ids.append(pair[1])
                elif isinstance(pair, dict) and 'second' in pair: # Retrofit Pair serialization
                    absent_ids.append(pair['second'])

        # Fetch all students for this grade to mark everyone
        students = user_model.find_students_by_grade(grade)
        
        success_count = 0
        for s in students:
            # s is (id, full_name, role, grade) or dict
            s_id = s['id'] if isinstance(s, dict) else s[0]
            status = 'ABSENT' if s_id in absent_ids else 'PRESENT'
            if attendance_model.mark_attendance(s_id, grade, date, status, created_at=ist_now):
                success_count += 1
                
        return jsonify({"status": "success", "message": f"Attendance marked for {success_count} students"})

    @app.route('/api/attendance/<grade>/<date>', methods=['GET'])
    def get_attendance(grade, date):
        records = attendance_model.get_attendance(grade, date)
        return jsonify({"status": "success", "data": records})

    @app.route('/api/attendance/history/<grade>', methods=['GET'])
    def get_attendance_history(grade):
        records = attendance_model.get_attendance_history(grade)
        return jsonify({"status": "success", "data": records})

    # --- ANNOUNCEMENT ROUTES ---
    @app.route('/api/announcements', methods=['POST'])
    def create_announcement():
        data = request.json
        if not data or 'author_id' not in data or 'target_grade' not in data or 'content' not in data:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
            
        success = announcements_model.create_announcement(
            author_id=data['author_id'],
            target_grade=data['target_grade'],
            content=data['content']
        )
        if success:
            return jsonify({"status": "success", "message": "Announcement created"})
        return jsonify({"status": "error", "message": "Failed to create announcement"}), 500

    # --- ASSIGNMENT ROUTES ---
    @app.route('/api/assignments', methods=['POST'])
    def create_assignment():
        data = request.json
        required = ['author_id', 'grade', 'subject', 'title', 'due_date']
        if not data or not all(k in data for k in required):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
            
        success = assignment_model.create_assignment(
            author_id=data['author_id'],
            grade=data['grade'],
            subject=data['subject'],
            chapter=data.get('chapter'),
            title=data['title'],
            description=data.get('description', ''),
            due_date=data['due_date']
        )
        if success:
            return jsonify({"status": "success", "message": "Assignment created"})
        return jsonify({"status": "error", "message": "Failed to create assignment"}), 500

    @app.route('/api/assignments/<grade>', methods=['GET'])
    def get_assignments(grade):
        records = assignment_model.get_assignments_by_grade(grade)
        return jsonify({"status": "success", "data": records})


    @app.route('/api/announcements/<grade>', methods=['GET'])
    def get_announcements(grade):
        try:
            user_id = request.args.get('user_id', type=str)
            user_role = request.args.get('role', 'student').lower()
            
            # 1. Get real announcements from DB
            records = announcements_model.get_announcements_by_grade(grade)
            notifications = []
            
            for r in records:
                if isinstance(r, dict):
                    ann_id = r.get('id')
                    author_name = r.get('author_name')
                    content = r.get('content')
                    created_at = r.get('created_at')
                else:
                    # r is (id, content, created_at, author_name)
                    ann_id, content, created_at, author_name = r
                
                notifications.append({
                    "id": ann_id,
                    "title": f"Announcement from {author_name}",
                    "message": content,
                    "type": "Announcement",
                    "timestamp": int(created_at.timestamp() * 1000) if created_at else 0,
                    "target_grade": grade
                })

            # 2. Get real assignments from DB (treat as notifications too)
            assignments = assignment_model.get_assignments_by_grade(grade)
            for a in assignments:
                if isinstance(a, dict):
                    ass_id = a.get('id')
                    title = a.get('title')
                    subject = a.get('subject')
                    desc = a.get('description', '')
                    created_at = a.get('created_at')
                else:
                    # a is (id, author_id, author_name, subject, title, description, due_date, created_at)
                    ass_id, _, _, subject, title, desc, _, created_at = a

                notifications.append({
                    "id": 50000 + ass_id,
                    "title": f"New Assignment: {title}",
                    "message": f"Subject: {subject} - {desc or ''}",
                    "type": "Assignment",
                    "timestamp": int(created_at.timestamp() * 1000) if created_at else 0,
                    "target_grade": grade,
                    "target_role": "student"
                })

            # 3. Add "New Challenge" notification if one exists for today
            active_challenge = challenge_model.get_active_challenge(grade)
            if active_challenge:
                if isinstance(active_challenge, dict):
                    ch_id = active_challenge.get('id')
                    ch_title = active_challenge.get('title')
                else:
                    # challenge returns (id, title, description, questions, expires_at)
                    ch_id, ch_title, _, _, _ = active_challenge

                notifications.append({
                    "id": 10000 + ch_id,
                    "title": "New Daily Challenge!",
                    "message": ch_title,
                    "type": "Quiz",
                    "timestamp": 0,
                    "target_grade": grade,
                    "target_role": "student"
                })

            # 4. Add Teacher-specific notifications
            if user_role in ['teacher', 'faculty']:
                from datetime import date
                today = date.today().isoformat()
                att_records = attendance_model.get_attendance(grade, today)
                if not att_records:
                    notifications.insert(0, {
                        "id": 20001,
                        "title": "📋 Attendance Reminder",
                        "message": f"Please mark attendance for Grade {grade} today.",
                        "type": "Attendance",
                        "timestamp": 0,
                        "target_grade": grade
                    })
            
            return jsonify({"status": "success", "data": notifications})
        except Exception as e:
            print(f"Error fetching notifications: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500


    # --- CHATBOT ROUTES (Handling both /api and non-api) ---
    @app.route('/api/chatbot/ask', methods=['POST'])
    @app.route('/chatbot/ask', methods=['POST'])
    def ask_chatbot():
        global model, api_keys, current_key_index
        
        # Reload keys if needed (dynamic)
        if not api_keys or not model:
            from dotenv import load_dotenv
            import os
            env_path = os.path.join(os.path.dirname(__file__), '.env')
            load_dotenv(dotenv_path=env_path, override=True)
            api_keys = [
                os.getenv("GEMINI_API_KEY_1"), 
                os.getenv("GEMINI_API_KEY_2"),
                os.getenv("GEMINI_API_KEY_3"),
                os.getenv("GEMINI_API_KEY_4"),
                os.getenv("GEMINI_API_KEY_5")
            ]
            api_keys = [k for k in api_keys if k and k != "your_api_key_here"]
            if api_keys:
                current_key_index = 0
                model = get_gemini_model(api_keys[0])

        try:
            data = request.json
            question = data.get('question', '')
            if not question:
                return jsonify({"answer": "Please ask a question!"}), 200

            print(f"Asking Gemini: {question} (Using Key {current_key_index + 1})")
            
            # Multi-Key Fallback Logic
            response = None
            last_error = ""
            
            for attempt in range(len(api_keys)):
                try:
                    response = model.generate_content(question)
                    if response: break
                except Exception as e:
                    last_error = str(e)
                    if "429" in last_error or "quota" in last_error.lower():
                        print(f"Key {current_key_index + 1} quota hit. Switching to next key...")
                        current_key_index = (current_key_index + 1) % len(api_keys)
                        model = get_gemini_model(api_keys[current_key_index])
                        continue
                    else:
                        break
            
            if not response:
                if "429" in last_error or "quota" in last_error.lower():
                    return jsonify({"answer": "All assistant brains are busy right now. Please wait a minute! 😊"}), 200
                return jsonify({"answer": f"Backend Error: {last_error}"}), 200

            try:
                answer = response.text
            except Exception as e:
                print(f"Gemini response.text error: {e}")
                if response.candidates:
                    answer = "I am sorry, I can only help you with questions related to your studies or the RuralQuest app. Let's get back to learning! 😊"
                else:
                    answer = "I'm sorry, I couldn't generate a response. Please try a different question."
                
            print(f"Gemini Answer: {answer}")
            return jsonify({"answer": answer}), 200
        except Exception as e:
            error_msg = str(e)
            print(f"!!! Chatbot Exception !!!: {error_msg}")
            
            if "429" in error_msg or "quota" in error_msg.lower():
                return jsonify({"answer": "The assistant is momentarily busy. Please try your question again in a minute."}), 200
            
            return jsonify({"answer": f"Backend Error: {error_msg}"}), 200


    @app.route('/uploads/<path:filename>')
    @app.route('/api/pdfs/<path:filename>')
    def serve_pdf(filename):
        try:
            from flask import send_from_directory
            # If the filename already contains 'uploads/', strip it because we are serving FROM 'uploads'
            if filename.startswith('uploads/'):
                filename = filename[len('uploads/'):]
            return send_from_directory('uploads', filename)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 404

    return app

if __name__ == '__main__':
    import socket
    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try: s.connect(('8.8.8.8', 1)); ip = s.getsockname()[0]
        except Exception: ip = '127.0.0.1'
        finally: s.close()
        return ip

    app = create_app()
    port = 5001
    ip = get_ip()
    
    print("=" * 50)
    print(" RuralQuest Backend is running!")
    print(f" Access from your phone: http://{ip}:{port}")
    print(f" Local access:           http://127.0.0.1:{port}")
    print("=" * 50)
    
    app.run(host='0.0.0.0', debug=True, port=port)

