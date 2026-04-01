import MySQLdb
from flask_mysqldb import MySQL

class UserModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def create_user(self, full_name, email, password_hash, role='student', grade=None, subject_expertise=None, status='active', must_change_password='no'):
        try:
            cur = self.mysql.connection.cursor()
            
            # --- CUSTOM ID GENERATION ---
            prefix = "VQ-" if role.lower() == 'student' else "VQT-"
            year = "2026"
            
            query_max = f"SELECT id FROM users WHERE id LIKE '{prefix}{year}%' ORDER BY id DESC LIMIT 1"
            cur.execute(query_max)
            last_user = cur.fetchone()
            
            if last_user:
                last_id = last_user['id'] if isinstance(last_user, dict) else last_user[0]
                offset = len(prefix) + len(year)
                last_num = int(last_id[offset:])
                next_num = last_num + 1
            else:
                next_num = 1
                
            new_id = f"{prefix}{year}{next_num:03d}"
            # ----------------------------

            # 1. Insert into core 'users' table (omitting phone)
            clean_role = role.lower().strip()
            query_user = "INSERT INTO users (id, full_name, email, password_hash, role, status, must_change_password) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cur.execute(query_user, (new_id, full_name, email, password_hash, clean_role, status.strip(), must_change_password))

            # 2. Insert into role-specific table
            if clean_role == 'student':
                query_student = "INSERT INTO students (user_id, grade) VALUES (%s, %s)"
                cur.execute(query_student, (new_id, grade))
            elif clean_role in ['teacher', 'faculty']:
                query_teacher = "INSERT INTO teachers (user_id, assigned_grade, subject_expertise) VALUES (%s, %s, %s)"
                cur.execute(query_teacher, (new_id, grade, subject_expertise))

            self.mysql.connection.commit()
            cur.close()
            return True
        except MySQLdb.Error as e:
            print(f"Error creating user: {e}")
            return False

    def approve_user(self, user_id):
        try:
            cur = self.mysql.connection.cursor()
            query = "UPDATE users SET status = 'active' WHERE id = %s"
            cur.execute(query, (user_id,))
            self.mysql.connection.commit()
            cur.close()
            return True
        except MySQLdb.Error as e:
            print(f"Error approving user: {e}")
            return False

    def delete_user(self, user_id):
        try:
            conn = self.mysql.connection
            # Temporarily disable FK checks
            cur = conn.cursor()
            cur.execute("SET FOREIGN_KEY_CHECKS = 0")
            cur.close()
            
            # Delete from related tables, each with fresh cursor
            for table in ['students', 'teachers', 'quiz_progress']:
                try:
                    c = conn.cursor()
                    c.execute(f"DELETE FROM {table} WHERE user_id = %s", (user_id,))
                    c.close()
                except Exception as e:
                    print(f"  Skipping {table}: {e}")

            # Delete the user
            cur2 = conn.cursor()
            cur2.execute("DELETE FROM users WHERE id = %s", (user_id,))
            cur2.close()
            
            # Re-enable FK checks
            cur3 = conn.cursor()
            cur3.execute("SET FOREIGN_KEY_CHECKS = 1")
            cur3.close()
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting user {user_id}: {e}")
            import traceback
            traceback.print_exc()
            try:
                c = self.mysql.connection.cursor()
                c.execute("SET FOREIGN_KEY_CHECKS = 1")
                self.mysql.connection.commit()
            except:
                pass
            return False

    def update_user(self, user_id, data):
        try:
            cur = self.mysql.connection.cursor()
            full_name = data.get('fullName') or data.get('full_name')
            email = data.get('email')
            role = data.get('role')
            details = data.get('details', '')

            updates = []
            params = []
            if full_name:
                updates.append("full_name = %s")
                params.append(full_name)
            if email:
                updates.append("email = %s")
                params.append(email)
            if role:
                updates.append("role = %s")
                params.append(role.lower().strip())

            if updates:
                params.append(user_id)
                query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
                cur.execute(query, tuple(params))

            self.mysql.connection.commit()
            cur.close()
            return True
        except MySQLdb.Error as e:
            print(f"Error updating user: {e}")
            return False

    def find_user_by_email(self, email):
        try:
            cur = self.mysql.connection.cursor()
            query = """
                SELECT u.id, u.full_name, u.email, u.role, u.password_hash, u.status, u.must_change_password,
                       s.grade as student_grade,
                       t.assigned_grade as teacher_grade,
                       t.subject_expertise
                FROM users u
                LEFT JOIN students s ON u.id = s.user_id
                LEFT JOIN teachers t ON u.id = t.user_id
                WHERE u.email = %s
            """
            cur.execute(query, (email,))
            user = cur.fetchone()
            cur.close()
            
            if user:
                # Map back to a consistent dictionary/object for the frontend
                must_change_val = user['must_change_password'] if isinstance(user, dict) else user[6]
                is_must_change = (must_change_val == 'yes') if isinstance(must_change_val, str) else bool(must_change_val)

                final_user = {
                    'id': user['id'] if isinstance(user, dict) else user[0],
                    'full_name': user['full_name'] if isinstance(user, dict) else user[1],
                    'email': user['email'] if isinstance(user, dict) else user[2],
                    'role': user['role'] if isinstance(user, dict) else user[3],
                    'password_hash': user['password_hash'] if isinstance(user, dict) else user[4],
                    'status': user['status'] if isinstance(user, dict) else user[5],
                    'must_change_password': is_must_change
                }
                
                if final_user['role'] == 'student':
                    final_user['grade'] = user['student_grade'] if isinstance(user, dict) else user[7]
                else:
                    final_user['grade'] = user['teacher_grade'] if isinstance(user, dict) else user[8]
                    final_user['subject_expertise'] = user['subject_expertise'] if isinstance(user, dict) else user[9]
                
                return final_user
            return None
        except MySQLdb.Error as e:
            print(f"Error finding user: {e}")
            return None

    def find_students_by_grade(self, grade):
        try:
            cur = self.mysql.connection.cursor()
            
            # 1. Get total chapters for this grade to calculate progress
            cur.execute("""
                SELECT COUNT(*) as total 
                FROM chapters c 
                JOIN subjects s ON c.subject_id = s.id 
                WHERE s.grade = %s
            """, (grade,))
            total_row = cur.fetchone()
            total_chapters = (total_row['total'] if isinstance(total_row, dict) else total_row[0]) or 1
            
            # 2. Get students with their individual stats
            query = """
                SELECT u.id, u.full_name, u.role, s.grade,
                       COALESCE(qp.avg_acc, 0) as avg_accuracy,
                       COALESCE(qp.chap_count, 0) as completed_chapters
                FROM users u
                JOIN students s ON u.id = s.user_id
                LEFT JOIN (
                    SELECT user_id, AVG(score) as avg_acc, COUNT(DISTINCT chapter) as chap_count
                    FROM quiz_progress 
                    WHERE grade = %s
                    GROUP BY user_id
                ) qp ON u.id = qp.user_id
                WHERE u.role = 'student' AND s.grade = %s
            """
            cur.execute(query, (grade, grade))
            students_raw = cur.fetchall()
            cur.close()
            
            students = []
            for s in students_raw:
                if isinstance(s, dict):
                    avg_acc = int(s.get('avg_accuracy', 0))
                    comp_chap = s.get('completed_chapters', 0)
                    students.append({
                        "id": s.get('id'),
                        "full_name": s.get('full_name'),
                        "role": s.get('role'),
                        "grade": s.get('grade'),
                        "avg_accuracy": avg_acc,
                        "progress": float(comp_chap) / total_chapters
                    })
                else:
                    avg_acc = int(s[4])
                    comp_chap = s[5]
                    students.append({
                        "id": s[0],
                        "full_name": s[1],
                        "role": s[2],
                        "grade": s[3],
                        "avg_accuracy": avg_acc,
                        "progress": float(comp_chap) / total_chapters
                    })
            return students
        except MySQLdb.Error as e:
            print(f"Error finding students: {e}")
            return []

    def get_user_full_details(self, user_id):
        try:
            cur = self.mysql.connection.cursor()
            # 1. Get base user info
            cur.execute("SELECT id, full_name, role, email, status, created_at FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()
            if not user:
                cur.close()
                return None
            
            if isinstance(user, dict):
                data = {
                    "id": user['id'], "name": user['full_name'], "role": user['role'],
                    "email": user['email'], "status": user['status'], 
                    "created_at": user['created_at'].strftime("%Y-%m-%d") if user['created_at'] else ""
                }
            else:
                data = {
                    "id": user[0], "name": user[1], "role": user[2],
                    "email": user[3], "status": user[4], 
                    "created_at": user[5].strftime("%Y-%m-%d") if user[5] else ""
                }
            
            role = data['role'].lower()
            if role == 'student':
                # Fetch from students table + quiz stats
                cur.execute("""
                    SELECT s.grade, s.total_xp, s.perfect_quizzes, s.high_accuracy_quizzes, s.total_study_time,
                           COALESCE(qp.avg_acc, 0) as avg_accuracy,
                           COALESCE(qp.q_count, 0) as quiz_count,
                           COALESCE(qp.chap_count, 0) as chapters_completed
                    FROM students s
                    LEFT JOIN (
                        SELECT user_id, AVG(score) as avg_acc, COUNT(*) as q_count, COUNT(DISTINCT chapter) as chap_count
                        FROM quiz_progress WHERE user_id = %s
                    ) qp ON s.user_id = qp.user_id
                    WHERE s.user_id = %s
                """, (user_id, user_id))
                ext = cur.fetchone()
                if ext:
                    if isinstance(ext, dict):
                        data.update({
                            "grade": ext['grade'],
                            "total_xp": ext['total_xp'], "perfect_quizzes": ext['perfect_quizzes'],
                            "high_accuracy": ext['avg_accuracy'], "quiz_count": ext['quiz_count'],
                            "chapters_completed": ext['chapters_completed'], "study_time": ext['total_study_time']
                        })
                    else:
                        data.update({
                            "grade": ext[0], "total_xp": ext[1], 
                            "perfect_quizzes": ext[2], "high_accuracy": ext[5], 
                            "quiz_count": ext[6], "chapters_completed": ext[7],
                            "study_time": ext[4]
                        })
            elif role in ['teacher', 'faculty']:
                cur.execute("SELECT assigned_grade, subject_expertise FROM teachers WHERE user_id = %s", (user_id,))
                ext = cur.fetchone()
                if ext:
                    if isinstance(ext, dict):
                        data.update({
                            "assigned_grade": ext['assigned_grade'],
                            "subject_expertise": ext['subject_expertise']
                        })
                    else:
                        data.update({
                            "assigned_grade": ext[0],
                            "subject_expertise": ext[1]
                        })
            
            cur.close()
            return data
        except Exception as e:
            print(f"Error getting user full details: {e}")
            return None

    def get_admin_stats(self):
        try:
            cur = self.mysql.connection.cursor()
            
            # Count students
            cur.execute("SELECT COUNT(*) FROM users WHERE role = 'student'")
            row = cur.fetchone()
            student_count = row['COUNT(*)'] if isinstance(row, dict) else row[0]
            student_count = int(student_count) if student_count else 0
            
            # Count teachers
            cur.execute("SELECT COUNT(*) FROM users WHERE role IN ('teacher', 'faculty')")
            row = cur.fetchone()
            teacher_count = row['COUNT(*)'] if isinstance(row, dict) else row[0]
            teacher_count = int(teacher_count) if teacher_count else 0
            
            # Avg Accuracy from quiz_progress
            cur.execute("SELECT AVG(score) FROM quiz_progress")
            row = cur.fetchone()
            final_acc = (row['AVG(score)'] if isinstance(row, dict) else row[0]) if row else 0
            
            # School Progress
            cur.execute("SELECT COUNT(DISTINCT user_id, chapter, subject) FROM quiz_progress")
            total_completed = cur.fetchone()
            total_completed = list(total_completed.values())[0] if isinstance(total_completed, dict) else total_completed[0]
            
            cur.execute("SELECT COUNT(*) FROM chapters")
            total_chapters = cur.fetchone()
            total_chapters = list(total_chapters.values())[0] if isinstance(total_chapters, dict) else total_chapters[0]
            
            school_progress = 0.0
            if student_count > 0 and total_chapters > 0:
                school_progress = min(1.0, float(total_completed) / (student_count * total_chapters))
                
            # Quiz Completion Rate (Active quizzers in last 7 days)
            cur.execute("SELECT COUNT(DISTINCT user_id) FROM quiz_progress WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
            recent_quizzers = cur.fetchone()
            recent_quizzers = list(recent_quizzers.values())[0] if isinstance(recent_quizzers, dict) else recent_quizzers[0]
            
            quiz_completion_rate = 0.0
            if student_count > 0:
                quiz_completion_rate = min(1.0, float(recent_quizzers) / student_count)
                
            # Daily Active Users (Students returning today)
            cur.execute("SELECT COUNT(DISTINCT student_id) FROM attendance WHERE DATE(date) = CURDATE()")
            active_today = cur.fetchone()
            active_today = list(active_today.values())[0] if isinstance(active_today, dict) else active_today[0]
            
            daily_active_users = 0.0
            if student_count > 0:
                daily_active_users = min(1.0, float(active_today) / student_count)
            
            cur.close()
            return {
                "student_count": student_count,
                "teacher_count": teacher_count,
                "avg_accuracy": int(final_acc or 0),
                "school_progress": round(school_progress, 2),
                "quiz_completion_rate": round(quiz_completion_rate, 2),
                "daily_active_users": round(daily_active_users, 2)
            }
        except Exception as e:
            print(f"Error fetching admin stats: {e}")
            return None

    def get_all_users(self):
        try:
            cur = self.mysql.connection.cursor()
            query = """
                SELECT u.id, u.full_name, u.email, u.role, u.status, 
                       COALESCE(s.grade, t.assigned_grade) as grade,
                       t.subject_expertise
                FROM users u
                LEFT JOIN students s ON u.id = s.user_id
                LEFT JOIN teachers t ON u.id = t.user_id
                ORDER BY u.created_at DESC
            """
            cur.execute(query)
            users = cur.fetchall()
            cur.close()
            return users
        except MySQLdb.Error as e:
            print(f"Error fetching all users: {e}")
            return []

    def get_recent_uploads(self, limit=5):
        try:
            cur = self.mysql.connection.cursor()
            # Placeholder: fetch announcements as "content" for now
            query = "SELECT content as title, 'Announcement' as type, created_at FROM announcements ORDER BY created_at DESC LIMIT %s"
            cur.execute(query, (limit,))
            uploads = cur.fetchall()
            cur.close()
            return uploads
        except MySQLdb.Error as e:
            print(f"Error fetching recent uploads: {e}")
            return []

    def get_detailed_analytics(self):
        # Initialize defaults
        res = {
            "total_users": 0,
            "active_today": 0,
            "lessons_taken": 0,
            "avg_session": 0,
            "growth": [
                {"month": "Jan", "count": 0},
                {"month": "Feb", "count": 0},
                {"month": "Mar", "count": 0},
                {"month": "Apr", "count": 0},
                {"month": "May", "count": 0}
            ],
            "engagement": {
                "retention": 85,
                "quiz_completion": 100,
                "offline_usage": 45
            },
            "system_health": {
                "server_status": "Operational",
                "db_status": "Checking...",
                "storage_pct": 5,
                "total_records": 0
            }
        }
        
        try:
            cur = self.mysql.connection.cursor()
            res["system_health"]["db_status"] = "Healthy"
            
            # Simple Counts
            try:
                cur.execute("SELECT COUNT(*) as count FROM users")
                row = cur.fetchone()
                res["total_users"] = (row['count'] if isinstance(row, dict) else row[0]) or 0
                
                cur.execute("SELECT COUNT(DISTINCT user_id) as count FROM quiz_progress WHERE DATE(created_at) = CURDATE()")
                row = cur.fetchone()
                res["active_today"] = (row['count'] if isinstance(row, dict) else row[0]) or 0
                
                cur.execute("SELECT COUNT(*) as count FROM quiz_progress")
                row = cur.fetchone()
                res["lessons_taken"] = (row['count'] if isinstance(row, dict) else row[0]) or 0
                
                cur.execute("SELECT AVG(study_time_minutes) as avg_min FROM student_progress")
                row = cur.fetchone()
                if row:
                    res["avg_session"] = int((row['avg_min'] if isinstance(row, dict) else row[0]) or 0)
            except Exception as e:
                print(f"Error fetching base stats: {e}")

            # Growth Data
            try:
                growth_query = """
                    SELECT DATE_FORMAT(created_at, '%b') as month, COUNT(*) as count
                    FROM users
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 5 MONTH)
                    GROUP BY month
                    ORDER BY MIN(created_at)
                """
                cur.execute(growth_query)
                growth_rows = cur.fetchall()
                if growth_rows:
                    res["growth"] = []
                    for row in growth_rows:
                        if isinstance(row, dict):
                            res["growth"].append({"month": row['month'], "count": row['count']})
                        else:
                            res["growth"].append({"month": row[0], "count": row[1]})
            except Exception as e:
                print(f"Error fetching growth: {e}")

            # Engagement Data
            try:
                # Retention
                cur.execute("""
                    SELECT COUNT(DISTINCT user_id) * 100.0 / NULLIF((SELECT COUNT(*) FROM users WHERE role = 'student'), 0) as rate
                    FROM quiz_progress WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                """)
                row = cur.fetchone()
                if row:
                    val = (row['rate'] if isinstance(row, dict) else row[0])
                    if val is not None: res["engagement"]["retention"] = int(val)
                
                # Completion
                cur.execute("""
                    SELECT COUNT(*) * 100.0 / NULLIF(COUNT(id), 0) as rate
                    FROM quiz_progress WHERE score >= 80
                """)
                row = cur.fetchone()
                if row:
                    val = (row['rate'] if isinstance(row, dict) else row[0])
                    if val is not None: res["engagement"]["quiz_completion"] = int(val)

                # Offline Usage (Limit to unique quiz progress per chapter)
                cur.execute("""
                    SELECT LEAST(100, COUNT(DISTINCT qp.id) * 100.0 / NULLIF((SELECT COUNT(*) FROM quiz_progress), 0)) as rate
                    FROM quiz_progress qp
                    JOIN subjects s ON qp.subject = s.title AND qp.grade = s.grade
                    JOIN chapters c ON s.id = c.subject_id AND qp.chapter = c.title
                    WHERE c.is_offline = 1
                """)
                row = cur.fetchone()
                if row:
                    val = (row['rate'] if isinstance(row, dict) else row[0])
                    if val is not None: res["engagement"]["offline_usage"] = int(val)
            except Exception as e:
                print(f"Error fetching engagement: {e}")

            # System Health Counts
            try:
                cur.execute("SELECT COUNT(*) as count FROM assignments")
                a_row = cur.fetchone()
                ta = (a_row['count'] if a_row and isinstance(a_row, dict) else (a_row[0] if a_row else 0)) or 0
                
                cur.execute("SELECT COUNT(*) as count FROM announcements")
                n_row = cur.fetchone()
                tn = (n_row['count'] if n_row and isinstance(n_row, dict) else (n_row[0] if n_row else 0)) or 0

                cur.execute("SELECT COUNT(*) as count FROM chapters")
                c_row = cur.fetchone()
                tc = (c_row['count'] if c_row and isinstance(c_row, dict) else (c_row[0] if c_row else 0)) or 0

                tr = res["total_users"] + res["lessons_taken"] + ta + tn + tc
                res["system_health"]["total_records"] = tr
                res["system_health"]["storage_pct"] = min(99, max(4, int(tr / 100)))
            except Exception as e:
                print(f"Error fetching health details: {e}")

            cur.close()
            return res
        except Exception as e:
            print(f"Global analytics error (DB likely down): {e}")
            res["system_health"]["db_status"] = "Unavailable"
            return res


    def get_admin_notifications(self):
        try:
            cur = self.mysql.connection.cursor()
            # Generate system notifications from recent teacher signups and announcements
            query = """
                (SELECT 'System' as type, 'Teacher Joined' as title, full_name as message, created_at FROM users WHERE role IN ('teacher', 'faculty') AND status = 'pending')
                UNION
                (SELECT 'Bulletin' as type, 'New Announcement' as title, content as message, created_at FROM announcements)
                ORDER BY created_at DESC LIMIT 10
            """
            cur.execute(query)
            notifications = cur.fetchall()
            cur.close()
            return notifications
        except Exception as e:
            print(f"Error fetching admin notifications: {e}")
            return []

    def update_user_stats(self, user_id, xp, score):
        try:
            cur = self.mysql.connection.cursor()
            # 0. Ensure student exists in students table
            cur.execute("SELECT user_id FROM students WHERE user_id = %s", (user_id,))
            if not cur.fetchone():
                # If missing (e.g. from legacy migration), try to get grade from users or default
                cur.execute("SELECT role FROM users WHERE id = %s", (user_id,))
                user_role = cur.fetchone()
                if user_role and (user_role['role'] if isinstance(user_role, dict) else user_role[0]) == 'student':
                    cur.execute("INSERT INTO students (user_id, grade) VALUES (%s, '8')", (user_id,))

            # 1. Determine if it's a perfect or high accuracy quiz
            perfect = 1 if score >= 100 else 0
            high_acc = 1 if score >= 80 else 0
            
            # 2. Update the students table which contains the performance metrics
            # Increment quiz_count alongside XP and badges
            query = """
                UPDATE students 
                SET total_xp = total_xp + %s,
                    perfect_quizzes = perfect_quizzes + %s,
                    high_accuracy_quizzes = high_accuracy_quizzes + %s,
                    quiz_count = quiz_count + 1
                WHERE user_id = %s
            """
            cur.execute(query, (xp, perfect, high_acc, user_id))
            self.mysql.connection.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"Error updating user stats: {e}")
            return False

    def save_study_time(self, user_id, minutes):
        try:
            cur = self.mysql.connection.cursor()
            query = "UPDATE students SET total_study_time = total_study_time + %s WHERE user_id = %s"
            cur.execute(query, (minutes, user_id))
            self.mysql.connection.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"Error saving study time: {e}")
            return False

    def get_user_progress(self, user_id):
        try:
            cur = self.mysql.connection.cursor()
            
            # 1. Get aggregate stats and grade from students table
            query = "SELECT total_xp, perfect_quizzes, high_accuracy_quizzes, total_study_time, grade FROM students WHERE user_id = %s"
            cur.execute(query, (user_id,))
            user = cur.fetchone()
            
            if not user:
                cur.close()
                return None
            
            if isinstance(user, dict):
                total_xp = user.get('total_xp', 0) or 0
                perfect_quizzes = user.get('perfect_quizzes', 0) or 0
                high_accuracy_quizzes = user.get('high_accuracy_quizzes', 0) or 0
                total_study_time = user.get('total_study_time', 0) or 0
                grade = user.get('grade')
            else:
                total_xp = user[0] or 0
                perfect_quizzes = user[1] or 0
                high_accuracy_quizzes = user[2] or 0
                total_study_time = user[3] or 0
                grade = user[4]
            
            # 2. Get detailed quiz history to build completed_chapters and earned_badges
            quiz_query = "SELECT grade, subject, chapter, score, badge FROM quiz_progress WHERE user_id = %s"
            cur.execute(quiz_query, (user_id,))
            quiz_rows = cur.fetchall()
            
            completed_chapters = {}  # "grade-subject" -> [chapter1, chapter2, ...]
            earned_badges = {}       # "subject" -> {"chapter": "badge", ...}
            total_score = 0
            quiz_count = len(quiz_rows)
            
            for row in quiz_rows:
                if isinstance(row, dict):
                    q_grade = row.get('grade', '')
                    subject = row.get('subject', '')
                    chapter = row.get('chapter', '')
                    score = row.get('score', 0) or 0
                    badge = row.get('badge')
                else:
                    q_grade = row[0] or ''
                    subject = row[1] or ''
                    chapter = row[2] or ''
                    score = row[3] or 0
                    badge = row[4]
                
                total_score += score
                
                # Build completed_chapters
                key = f"{q_grade}-{subject}"
                if key not in completed_chapters:
                    completed_chapters[key] = []
                if chapter and chapter not in completed_chapters[key]:
                    completed_chapters[key].append(chapter)
                
                # Build earned_badges
                if badge:
                    if subject not in earned_badges:
                        earned_badges[subject] = {}
                    earned_badges[subject][chapter] = badge
            
            average_accuracy = (total_score // quiz_count) if quiz_count > 0 else 0
            
            # 3. Get Recent Subjects for "Continue Learning"
            recent_subjects = []
            cur.execute("""
                SELECT DISTINCT subject, chapter, MAX(created_at) as last_time
                FROM quiz_progress
                WHERE user_id = %s
                GROUP BY subject, chapter
                ORDER BY last_time DESC
                LIMIT 2
            """, (user_id,))
            recent_rows = cur.fetchall()
            
            for rr in recent_rows:
                if isinstance(rr, dict):
                    subj_name = rr.get('subject')
                    last_chap = rr.get('chapter')
                else:
                    subj_name = rr[0]
                    last_chap = rr[1]
                
                # Calculate progress for this subject
                # Need subject_id first
                cur.execute("SELECT id FROM subjects WHERE grade = %s AND title = %s", (grade, subj_name))
                subj_res = cur.fetchone()
                if subj_res:
                    s_id = subj_res['id'] if isinstance(subj_res, dict) else subj_res[0]
                    cur.execute("SELECT COUNT(*) FROM chapters WHERE subject_id = %s", (s_id,))
                    total_ch = cur.fetchone()
                    total_ch_count = (total_ch['COUNT(*)'] if isinstance(total_ch, dict) else total_ch[0]) or 1
                    
                    comp_key = f"{grade}-{subj_name}"
                    comp_count = len(completed_chapters.get(comp_key, []))
                    prog_percent = int((comp_count / total_ch_count) * 100)
                    
                    recent_subjects.append({
                        "name": subj_name,
                        "chapter": last_chap,
                        "progress": prog_percent
                    })

            # 4. Get Actual Chapter Counts for Reports
            subject_chapter_counts = {}
            cur.execute("SELECT title, id FROM subjects WHERE grade = %s", (grade,))
            subj_list = cur.fetchall()
            for s in subj_list:
                s_name = s['title'] if isinstance(s, dict) else s[0]
                s_id = s['id'] if isinstance(s, dict) else s[1]
                cur.execute("SELECT COUNT(*) FROM chapters WHERE subject_id = %s", (s_id,))
                c_row = cur.fetchone()
                c_count = (c_row['COUNT(*)'] if isinstance(c_row, dict) else c_row[0]) or 10
                subject_chapter_counts[s_name] = c_count

            # 5. Compute weekly XP breakdown (Mon-Sun)
            import datetime
            today = datetime.date.today()
            # Monday is 0, Sunday is 6
            days_since_monday = today.weekday()
            monday = today - datetime.timedelta(days=days_since_monday)
            
            weekly_xp_days = [0] * 7
            cur.execute("""
                SELECT DAYOFWEEK(created_at) as dow, SUM(xp) as total_xp, DATE(created_at) as d
                FROM quiz_progress 
                WHERE user_id = %s AND created_at >= %s
                GROUP BY d
            """, (user_id, monday))
            rows = cur.fetchall()
            
            # MySQL DAYOFWEEK: 1=Sun, 2=Mon, 3=Tue, 4=Wed, 5=Thu, 6=Fri, 7=Sat
            # We want: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
            for row in rows:
                dow = row['dow'] if isinstance(row, dict) else row[0]
                txp = row['total_xp'] if isinstance(row, dict) else row[1]
                # Map 2->0, 3->1, 4->2, 5->3, 6->4, 7->5, 1->6
                idx = (dow - 2 + 7) % 7
                if idx < 7:
                    weekly_xp_days[idx] = int(txp or 0)
            
            weekly_xp = sum(weekly_xp_days)
            
            # 6. Calculate subject_mastery accurately
            subject_mastery = {}
            for subj_name, total_ch_count in subject_chapter_counts.items():
                comp_key = f"{grade}-{subj_name}"
                comp_count = len(completed_chapters.get(comp_key, []))
                prog_percent = min(1.0, float(comp_count) / max(1, total_ch_count))
                subject_mastery[subj_name] = round(prog_percent, 2)
                
            # 7. Calculate Streak
            ist_today = (datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)).date()
            cur.execute("""
                SELECT DISTINCT DATE(created_at) as d 
                FROM quiz_progress 
                WHERE user_id = %s 
                ORDER BY d DESC
            """, (user_id,))
            date_rows = cur.fetchall()
            
            streak = 0
            if date_rows:
                active_dates = [row['d'] if isinstance(row, dict) else row[0] for row in date_rows]
                active_dates = [d for d in active_dates if d <= ist_today]
                
                if active_dates:
                    if active_dates[0] == ist_today or active_dates[0] == ist_today - datetime.timedelta(days=1):
                        streak = 1
                        current = active_dates[0]
                        for d in active_dates[1:]:
                            if d == current - datetime.timedelta(days=1):
                                streak += 1
                                current = d
                            else:
                                break

            cur.close()
            return {
                "total_xp": total_xp,
                "streak": streak,
                "perfect_quizzes": perfect_quizzes,
                "high_accuracy_quizzes": high_accuracy_quizzes,
                "average_accuracy": average_accuracy,
                "quiz_count": quiz_count,
                "total_study_time": total_study_time,
                "weekly_xp": weekly_xp,
                "weekly_xp_days": weekly_xp_days,
                "completed_chapters": completed_chapters,
                "earned_badges": earned_badges,
                "recent_subjects": recent_subjects,
                "subject_chapter_counts": subject_chapter_counts,
                "subject_mastery": subject_mastery
            }
        except Exception as e:
            print(f"Error fetching user progress: {e}")
            return None

    def get_grade_analytics(self, grade):
        try:
            cur = self.mysql.connection.cursor()
            # 1. Basic counts
            cur.execute("SELECT COUNT(*) as count FROM users u JOIN students s ON u.id = s.user_id WHERE u.role = 'student' AND s.grade = %s", (grade,))
            student_count_row = cur.fetchone()
            if isinstance(student_count_row, dict):
                student_count = student_count_row.get('count', 0)
            else:
                student_count = student_count_row[0] if student_count_row else 0

            # 2. Avg Accuracy from quiz_progress
            cur.execute("SELECT AVG(score) as avg_score FROM quiz_progress WHERE grade = %s", (grade,))
            avg_accuracy_row = cur.fetchone()
            if isinstance(avg_accuracy_row, dict):
                avg_accuracy = avg_accuracy_row.get('avg_score', 0)
            else:
                avg_accuracy = avg_accuracy_row[0] if avg_accuracy_row else 0
            avg_accuracy = int(avg_accuracy) if avg_accuracy else 0

            # 3. Total Lessons Completed
            cur.execute("SELECT COUNT(*) as count FROM quiz_progress WHERE grade = %s", (grade,))
            lessons_completed_row = cur.fetchone()
            if isinstance(lessons_completed_row, dict):
                lessons_completed = lessons_completed_row.get('count', 0)
            else:
                lessons_completed = lessons_completed_row[0] if lessons_completed_row else 0

            # 4. Total Study Time
            cur.execute("SELECT SUM(total_study_time) as total_time FROM students WHERE grade = %s", (grade,))
            total_study_time_row = cur.fetchone()
            if isinstance(total_study_time_row, dict):
                total_study_time = total_study_time_row.get('total_time', 0)
            else:
                total_study_time = total_study_time_row[0] if total_study_time_row else 0
            total_study_time = int(total_study_time) if total_study_time else 0

            # 5. Low Performers Count (Avg accuracy < 70%)
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM (
                    SELECT user_id, AVG(score) as avg_acc 
                    FROM quiz_progress 
                    WHERE grade = %s 
                    GROUP BY user_id 
                    HAVING avg_acc < 70
                ) as low_perf
            """, (grade,))
            row = cur.fetchone()
            low_performers_count = (row['count'] if isinstance(row, dict) else row[0]) if row else 0

            # 6. Subject Performance (All subjects for the grade)
            cur.execute("""
                SELECT s.title, AVG(qp.score) as avg_score 
                FROM subjects s
                LEFT JOIN quiz_progress qp ON s.title = qp.subject AND s.grade = qp.grade
                WHERE s.grade = %s 
                GROUP BY s.title
            """, (grade,))
            subject_rows = cur.fetchall()
            subject_performance = {}
            for row in subject_rows:
                title = row['title'] if isinstance(row, dict) else row[0]
                avg = row['avg_score'] if isinstance(row, dict) else row[1]
                subject_performance[title] = float(avg) if avg else 0.0

            # 7. Performance Distribution
            cur.execute("""
                SELECT 
                    SUM(CASE WHEN avg_acc >= 80 THEN 1 ELSE 0 END) as high,
                    SUM(CASE WHEN avg_acc >= 50 AND avg_acc < 80 THEN 1 ELSE 0 END) as medium,
                    SUM(CASE WHEN avg_acc < 50 THEN 1 ELSE 0 END) as low
                FROM (
                    SELECT user_id, AVG(score) as avg_acc 
                    FROM quiz_progress 
                    WHERE grade = %s 
                    GROUP BY user_id
                ) as student_accs
            """, (grade,))
            dist_row = cur.fetchone()
            if dist_row:
                performance_distribution = {
                    "High": int(dist_row['high'] or 0) if isinstance(dist_row, dict) else int(dist_row[0] or 0),
                    "Medium": int(dist_row['medium'] or 0) if isinstance(dist_row, dict) else int(dist_row[1] or 0),
                    "Low": int(dist_row['low'] or 0) if isinstance(dist_row, dict) else int(dist_row[2] or 0)
                }
            else:
                performance_distribution = {"High": 0, "Medium": 0, "Low": 0}

            # 8. Recent Activities (Real student activity for the grade)
            cur.execute("""
                SELECT u.full_name, qp.subject, qp.chapter, qp.score, qp.created_at
                FROM quiz_progress qp
                JOIN users u ON qp.user_id = u.id
                WHERE qp.grade = %s
                ORDER BY qp.created_at DESC
                LIMIT 5
            """, (grade,))
            activity_rows = cur.fetchall()
            recent_activities = []
            for row in activity_rows:
                name = row['full_name'] if isinstance(row, dict) else row[0]
                subject = row['subject'] if isinstance(row, dict) else row[1]
                chapter = row['chapter'] if isinstance(row, dict) else row[2]
                score = row['score'] if isinstance(row, dict) else row[3]
                created_at = row['created_at'] if isinstance(row, dict) else row[4]
                
                time_str = created_at.strftime("%I:%M %p") if created_at else "Just now"
                
                recent_activities.append({
                    "title": f"{name} completed {chapter}",
                    "desc": f"{subject} - {score}%",
                    "time": time_str
                })

            cur.close()
            return {
                "student_count": student_count,
                "average_accuracy": avg_accuracy,
                "lessons_completed": lessons_completed,
                "total_study_time": total_study_time,
                "low_performers_count": low_performers_count,
                "subject_performance": subject_performance,
                "performance_distribution": performance_distribution,
                "recent_activities": recent_activities
            }
        except Exception as e:
            print(f"Error in get_grade_analytics: {e}")
            return None

    def update_user_settings(self, user_id, settings):
        try:
            cur = self.mysql.connection.cursor()
            import json
            query = "UPDATE users SET settings = %s WHERE id = %s"
            cur.execute(query, (json.dumps(settings), user_id))
            self.mysql.connection.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"Error updating user settings: {e}")
            return False

    def get_user_settings(self, user_id):
        try:
            cur = self.mysql.connection.cursor()
            cur.execute("SELECT settings FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            cur.close()
            if row:
                import json
                settings_str = row.get('settings') if isinstance(row, dict) else row[0]
                return json.loads(settings_str) if settings_str else {}
            return {}
        except Exception as e:
            print(f"Error fetching user settings: {e}")
            return {}

class AttendanceModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def mark_attendance(self, student_id, grade, date, status, created_at=None):
        try:
            cur = self.mysql.connection.cursor()
            if created_at:
                query = """
                    INSERT INTO attendance (student_id, grade, date, status, created_at) 
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE status = VALUES(status), created_at = VALUES(created_at)
                """
                cur.execute(query, (student_id, grade, date, status, created_at))
            else:
                query = """
                    INSERT INTO attendance (student_id, grade, date, status) 
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE status = VALUES(status)
                """
                cur.execute(query, (student_id, grade, date, status))
            self.mysql.connection.commit()
            cur.close()
            return True
        except MySQLdb.Error as e:
            print(f"Error marking attendance: {e}")
            return False

    def get_overall_attendance_stats(self):
        try:
            cur = self.mysql.connection.cursor()
            # Get average attendance across all grades
            cur.execute("SELECT (SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) / COUNT(*)) * 100 as rate FROM attendance")
            row = cur.fetchone()
            rate = row['rate'] if isinstance(row, dict) else row[0]
            cur.close()
            return int(rate or 0)
        except Exception as e:
            print(f"Error fetching overall attendance: {e}")
            return 0

    def get_attendance(self, grade, date):
        try:
            cur = self.mysql.connection.cursor()
            query = """
                SELECT a.student_id, u.full_name, a.status 
                FROM attendance a
                JOIN users u ON a.student_id = u.id
                WHERE a.grade = %s AND a.date = %s
            """
            cur.execute(query, (grade, date))
            records = cur.fetchall()
            cur.close()
            return records
        except MySQLdb.Error as e:
            print(f"Error fetching attendance: {e}")
            return []

    def get_attendance_history(self, grade, limit=10):
        try:
            cur = self.mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor if hasattr(MySQLdb.cursors, 'DictCursor') else None)
            query = """
                SELECT 
                    DATE_FORMAT(MAX(created_at), '%%b %%d, %%h:%%i %%p') as date_str,
                    DAYNAME(date) as day_name,
                    COUNT(*) as total, 
                    SUM(CASE WHEN status = 'PRESENT' THEN 1 ELSE 0 END) as present
                FROM attendance
                WHERE grade = %s
                GROUP BY date
                ORDER BY date DESC
                LIMIT %s
            """
            cur.execute(query, (grade, limit))
            records = cur.fetchall()
            cur.close()
            
            formatted_records = []
            for r in records:
                if isinstance(r, dict):
                    formatted_records.append({
                        "date_str": r.get('date_str') or str(r.get('date', '')),
                        "day_name": r.get('day_name') or "",
                        "total": int(r.get('total', 0) or 0),
                        "present": int(r.get('present', 0) or 0)
                    })
                else:
                    # Fallback for tuple results if DictCursor was not available
                    formatted_records.append({
                        "date_str": r[0],
                        "day_name": r[1],
                        "total": int(r[2] or 0),
                        "present": int(r[3] or 0)
                    })
            return formatted_records
        except MySQLdb.Error as e:
            print(f"Error fetching attendance history: {e}")
            return []

class AssignmentModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def create_assignment(self, author_id, grade, subject, chapter, title, description, due_date):
        try:
            cur = self.mysql.connection.cursor()
            query = """
                INSERT INTO assignments (author_id, grade, subject, chapter, title, description, due_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(query, (author_id, grade, subject, chapter, title, description, due_date))
            self.mysql.connection.commit()
            cur.close()
            return True
        except MySQLdb.Error as e:
            print(f"Error creating assignment: {e}")
            return False

    def get_assignments_by_grade(self, grade):
        try:
            cur = self.mysql.connection.cursor()
            query = """
                SELECT a.id, a.author_id, u.full_name as author_name, a.subject, a.title, a.description, a.due_date, a.created_at 
                FROM assignments a
                JOIN users u ON a.author_id = u.id
                WHERE a.grade = %s
                ORDER BY a.created_at DESC
            """
            cur.execute(query, (grade,))
            records = cur.fetchall()
            cur.close()
            return records
        except MySQLdb.Error as e:
            print(f"Error fetching assignments: {e}")
            return []

class AnnouncementModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def create_announcement(self, author_id, target_grade, content):
        try:
            cur = self.mysql.connection.cursor()
            query = "INSERT INTO announcements (author_id, target_grade, content) VALUES (%s, %s, %s)"
            cur.execute(query, (author_id, target_grade, content))
            self.mysql.connection.commit()
            cur.close()
            return True
        except MySQLdb.Error as e:
            print(f"Error creating announcement: {e}")
            return False

    def get_announcements_by_grade(self, target_grade):
        try:
            cur = self.mysql.connection.cursor()
            query = """
                SELECT a.id, a.content, a.created_at, u.full_name as author_name 
                FROM announcements a 
                JOIN users u ON a.author_id = u.id 
                WHERE a.target_grade = %s
                ORDER BY a.created_at DESC
            """
            cur.execute(query, (target_grade,))
            records = cur.fetchall()
            cur.close()
            return records
        except MySQLdb.Error as e:
            print(f"Error fetching announcements: {e}")
            return []

class ProgressModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_progress(self, student_id):
        try:
            cur = self.mysql.connection.cursor()
            query = "SELECT xp, lessons_completed, quiz_accuracy, study_time_minutes FROM student_progress WHERE student_id = %s"
            cur.execute(query, (student_id,))
            progress = cur.fetchone()
            cur.close()
            if not progress:
                # Return default zeroed progress if no record exists yet
                return (0, 0, 0, 0)
            return progress
        except MySQLdb.Error as e:
            print(f"Error fetching progress: {e}")
            return None

    def update_progress(self, student_id, xp, lessons_completed, quiz_accuracy, study_time_minutes):
        try:
            cur = self.mysql.connection.cursor()
            query = """
                INSERT INTO student_progress (student_id, xp, lessons_completed, quiz_accuracy, study_time_minutes) 
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    xp = xp + VALUES(xp), 
                    lessons_completed = lessons_completed + VALUES(lessons_completed),
                    quiz_accuracy = (quiz_accuracy + VALUES(quiz_accuracy)) / 2,
                    study_time_minutes = study_time_minutes + VALUES(study_time_minutes)
            """
            cur.execute(query, (student_id, xp, lessons_completed, quiz_accuracy, study_time_minutes))
            self.mysql.connection.commit()
            cur.close()
            return True
        except MySQLdb.Error as e:
            print(f"Error updating progress: {e}")
            return False

class SubjectModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_subjects_by_grade(self, grade):
        try:
            cur = self.mysql.connection.cursor()
            query = "SELECT id, title, subtitle, icon_res, tint_color, bg_color FROM subjects WHERE grade = %s"
            cur.execute(query, (grade,))
            subjects = cur.fetchall()
            cur.close()
            return subjects
        except MySQLdb.Error as e:
            print(f"Error fetching subjects: {e}")
            return []

class ChapterModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_chapters_by_subject(self, subject_id):
        try:
            cur = self.mysql.connection.cursor()
            # Group by chapter_number to avoid showing duplicates in UI
            query = """
                SELECT id, chapter_number, title, MAX(lessons_count) as lessons_count, is_offline, pdf_url 
                FROM chapters 
                WHERE subject_id = %s 
                GROUP BY chapter_number 
                ORDER BY chapter_number ASC
            """
            cur.execute(query, (subject_id,))
            chapters = cur.fetchall()
            cur.close()
            return chapters
        except MySQLdb.Error as e:
            print(f"Error fetching chapters: {e}")
            return []

    def create_chapter(self, subject_id, chapter_number, title, lessons_count, is_offline=False, pdf_url=None):
        try:
            cur = self.mysql.connection.cursor()
            query = """
                INSERT INTO chapters (subject_id, chapter_number, title, lessons_count, is_offline, pdf_url)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.execute(query, (subject_id, chapter_number, title, lessons_count, is_offline, pdf_url))
            self.mysql.connection.commit()
            new_id = cur.lastrowid
            cur.close()
            return new_id
        except MySQLdb.Error as e:
            print(f"Error creating chapter: {e}")
            return None

    def find_chapter_by_number(self, subject_id, chapter_number):
        try:
            cur = self.mysql.connection.cursor()
            query = "SELECT id FROM chapters WHERE subject_id = %s AND chapter_number = %s LIMIT 1"
            cur.execute(query, (subject_id, chapter_number))
            res = cur.fetchone()
            cur.close()
            if res:
                return res['id'] if isinstance(res, dict) else res[0]
            return None
        except:
            return None

    def update_chapter(self, chapter_id, title=None, lessons_count=None, pdf_url=None):
        try:
            cur = self.mysql.connection.cursor()
            updates = []
            params = []
            if title:
                updates.append("title = %s")
                params.append(title)
            if lessons_count is not None:
                updates.append("lessons_count = %s")
                params.append(lessons_count)
            if pdf_url:
                updates.append("pdf_url = %s")
                params.append(pdf_url)
            
            if not updates:
                return True
                
            query = f"UPDATE chapters SET {', '.join(updates)} WHERE id = %s"
            params.append(chapter_id)
            cur.execute(query, tuple(params))
            self.mysql.connection.commit()
            cur.close()
            return True
        except MySQLdb.Error as e:
            print(f"Error updating chapter: {e}")
            return False

class QuizModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_questions_by_chapter(self, chapter_id):
        try:
            cur = self.mysql.connection.cursor()
            query = "SELECT id, question_text, options, correct_option_index, review_text FROM questions WHERE chapter_id = %s"
            cur.execute(query, (chapter_id,))
            questions = cur.fetchall()
            cur.close()
            return questions
        except MySQLdb.Error as e:
            print(f"Error fetching questions: {e}")
            return []

    def save_quiz_questions(self, chapter_id, questions):
        """
        questions: list of dicts with {text, options, correct_option_index, review_text}
        """
        try:
            cur = self.mysql.connection.cursor()
            import json
            for q in questions:
                query = """
                    INSERT INTO questions (chapter_id, question_text, options, correct_option_index, review_text)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cur.execute(query, (
                    chapter_id, 
                    q.get('text'), 
                    json.dumps(q.get('options')), 
                    q.get('correct_option_index'), 
                    q.get('review_text')
                ))
            self.mysql.connection.commit()
            cur.close()
            return True
        except MySQLdb.Error as e:
            print(f"Error saving quiz questions: {e}")
            return False
class QuizProgressModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def save_quiz_result(self, user_id, grade, subject, chapter, score, xp, badge):
        try:
            cur = self.mysql.connection.cursor()
            query = """
                INSERT INTO quiz_progress (user_id, grade, subject, chapter, score, xp, badge, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """
            cur.execute(query, (user_id, grade, subject, chapter, score, xp, badge))
            self.mysql.connection.commit()
            cur.close()
            return True
        except MySQLdb.Error as e:
            print(f"Error saving quiz progress: {e}")
            return False

    def get_recent_quiz_results(self, user_id, limit=10):
        try:
            cur = self.mysql.connection.cursor()
            query = "SELECT * FROM quiz_progress WHERE user_id = %s ORDER BY created_at DESC LIMIT %s"
            cur.execute(query, (user_id, limit))
            results = cur.fetchall()
            cur.close()
            return results
            return results
        except MySQLdb.Error as e:
            print(f"Error fetching quiz results: {e}")
            return []

class DailyChallengeModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def create_challenge(self, author_id, grade, title, description, questions_json, expires_at):
        try:
            cur = self.mysql.connection.cursor()
            query = """
                INSERT INTO daily_challenges (author_id, grade, title, description, questions, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.execute(query, (author_id, grade, title, description, questions_json, expires_at))
            self.mysql.connection.commit()
            cur.close()
            return True
        except MySQLdb.Error as e:
            print(f"Error creating daily challenge: {e}")
            return False

    def get_active_challenge(self, grade):
        try:
            cur = self.mysql.connection.cursor()
            query = """
                SELECT id, title, description, questions, expires_at 
                FROM daily_challenges 
                WHERE grade = %s AND (expires_at IS NULL OR expires_at > NOW())
                ORDER BY created_at DESC LIMIT 1
            """
            cur.execute(query, (grade,))
            challenge = cur.fetchone()
            cur.close()
            return challenge
        except MySQLdb.Error as e:
            print(f"Error fetching daily challenge: {e}")
            return None

class SpeechProgressModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def save_speech_session(self, user_id, category, accuracy, words_count):
        try:
            cur = self.mysql.connection.cursor()
            # Ensure the table is created if it hasn't been yet (robustness)
            create_query = """
            CREATE TABLE IF NOT EXISTS speech_training_progress (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(20) NOT NULL,
                category VARCHAR(100) NOT NULL,
                accuracy INT NOT NULL,
                words_practiced INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
            cur.execute(create_query)
            
            # Save the session
            insert_query = """
                INSERT INTO speech_training_progress (user_id, category, accuracy, words_practiced)
                VALUES (%s, %s, %s, %s)
            """
            cur.execute(insert_query, (user_id, category, accuracy, words_count))
            self.mysql.connection.commit()
            cur.close()
            return True
        except MySQLdb.Error as e:
            print(f"Error saving speech session: {e}")
            return False

    def get_speech_stats(self, user_id):
        try:
            cur = self.mysql.connection.cursor()
            # Check if table exists first
            cur.execute("SHOW TABLES LIKE 'speech_training_progress'")
            if not cur.fetchone():
                cur.close()
                return []
            
            # Aggregate stats per category
            query = """
                SELECT category, AVG(accuracy) as avg_accuracy, SUM(words_practiced) as total_words
                FROM speech_training_progress
                WHERE user_id = %s
                GROUP BY category
            """
            cur.execute(query, (user_id,))
            results = cur.fetchall()
            cur.close()
            return results
        except MySQLdb.Error as e:
            print(f"Error fetching speech stats: {e}")
            return []
