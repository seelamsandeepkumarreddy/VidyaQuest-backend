from flask import Blueprint, jsonify, request
from models import SubjectModel, ChapterModel, QuizModel, DailyChallengeModel
import json

courses_bp = Blueprint('courses', __name__)

def get_subject_model():
    from app import mysql
    return SubjectModel(mysql)

def get_chapter_model():
    from app import mysql
    return ChapterModel(mysql)

def get_quiz_model():
    from app import mysql
    return QuizModel(mysql)

def get_challenge_model():
    from app import mysql
    return DailyChallengeModel(mysql)

@courses_bp.route('/subjects/<grade>', methods=['GET'])
def get_subjects(grade):
    subject_model = get_subject_model()
    subjects = subject_model.get_subjects_by_grade(grade)
    
    formatted_subjects = []
    for s in subjects:
        if isinstance(s, dict):
            id_val = s.get('id')
            title = s.get('title')
            subtitle = s.get('subtitle')
            icon_res = s.get('icon_res')
            tint = s.get('tint_color')
            bg = s.get('bg_color')
        else:
            id_val, title, subtitle, icon_res, tint, bg = s

        formatted_subjects.append({
            "id": id_val,
            "title": title,
            "subtitle": subtitle,
            "icon_res": icon_res,
            "tint_color": tint,
            "bg_color": bg
        })
    
    return jsonify({"status": "success", "data": formatted_subjects})

@courses_bp.route('/chapters/<int:subject_id>', methods=['GET'])
def get_chapters(subject_id):
    chapter_model = get_chapter_model()
    chapters = chapter_model.get_chapters_by_subject(subject_id)
    
    formatted_chapters = []
    for c in chapters:
        if isinstance(c, dict):
            id_val = c.get('id')
            num = c.get('chapter_number')
            title = c.get('title')
            lessons = c.get('lessons_count')
            offline = c.get('is_offline')
            pdf_url = c.get('pdf_url')
        else:
            id_val, num, title, lessons, offline, pdf_url = c

        formatted_chapters.append({
            "id": id_val,
            "number": num,
            "title": title,
            "lessons": f"{lessons} lessons",
            "is_offline": bool(offline),
            "pdf_url": pdf_url
        })
    
    return jsonify({"status": "success", "data": formatted_chapters})

@courses_bp.route('/quizzes/<int:chapter_id>', methods=['GET'])
def get_quiz(chapter_id):
    quiz_model = get_quiz_model()
    questions = quiz_model.get_questions_by_chapter(chapter_id)
    
    formatted_questions = []
    for q in questions:
        if isinstance(q, dict):
            id_val = q.get('id')
            text = q.get('question_text')
            options_raw = q.get('options')
            correct_idx = q.get('correct_option_index')
            review = q.get('review_text')
        else:
            id_val, text, options_raw, correct_idx, review = q

        # Parse options JSON if it's a string
        options = options_raw
        if isinstance(options_raw, str):
            try:
                options = json.loads(options_raw)
            except:
                options = []

        formatted_questions.append({
            "id": id_val,
            "text": text,
            "options": options,
            "correct_option_index": correct_idx,
            "review_text": review
        })
    return jsonify({"status": "success", "data": formatted_questions})

@courses_bp.route('/challenges', methods=['POST'])
def create_challenge():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Missing request body"}), 400
    
    author_id = data.get('author_id')
    grade = data.get('grade')
    title = data.get('title')
    description = data.get('description', '')
    questions = data.get('questions')
    expires_at = data.get('expires_at') # e.g. "2023-12-31 23:59:59"

    if not all([author_id, grade, title, questions]):
        return jsonify({"status": "error", "message": "Missing required fields: author_id, grade, title, questions"}), 400
    
    questions_json = json.dumps(questions) if isinstance(questions, list) else questions

    challenge_model = get_challenge_model()
    success = challenge_model.create_challenge(author_id, grade, title, description, questions_json, expires_at)
    
    if success:
        return jsonify({"status": "success", "message": "Daily challenge created successfully"}), 201
    else:
        return jsonify({"status": "error", "message": "Failed to create daily challenge"}), 500

@courses_bp.route('/challenges/<grade>', methods=['GET'])
def get_active_challenge(grade):
    challenge_model = get_challenge_model()
    challenge = challenge_model.get_active_challenge(grade)
    
    if not challenge:
        return jsonify({"status": "success", "data": None}), 200
        
    if isinstance(challenge, dict):
        id_val = challenge.get('id')
        title = challenge.get('title')
        desc = challenge.get('description')
        questions_raw = challenge.get('questions')
        expires_at = challenge.get('expires_at')
    else:
        id_val, title, desc, questions_raw, expires_at = challenge
        
    questions = questions_raw
    if isinstance(questions_raw, str):
        try:
            questions = json.loads(questions_raw)
        except:
            questions = []
            
    return jsonify({
        "status": "success",
        "data": {
            "id": id_val,
            "title": title,
            "description": desc,
            "questions": questions,
            "expires_at": expires_at.isoformat() if expires_at else None
        }
    }), 200

import os
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@courses_bp.route('/upload-lesson', methods=['POST'])
def upload_lesson():
    try:
        subject_id = request.form.get('subject_id')
        grade = request.form.get('grade')
        chapter_number = request.form.get('chapter_number')
        title = request.form.get('title')
        lessons_count = request.form.get('lessons_count', '1')
        
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected file"}), 400

        if file:
            filename = f"grade_{grade}_sub_{subject_id}_ch_{chapter_number}_{file.filename}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            chapter_model = get_chapter_model()
            existing_chapter_id = chapter_model.find_chapter_by_number(subject_id, chapter_number)
            
            relative_url = f"uploads/{filename}"
            
            if existing_chapter_id:
                # Update existing chapter
                success = chapter_model.update_chapter(existing_chapter_id, title=title, lessons_count=lessons_count, pdf_url=relative_url)
                chapter_id_to_return = existing_chapter_id if success else None
            else:
                # Create new chapter
                chapter_id_to_return = chapter_model.create_chapter(subject_id, chapter_number, title, lessons_count, pdf_url=relative_url)
            
            if chapter_id_to_return:
                return jsonify({
                    "status": "success", 
                    "title": title,
                    "subject": str(subject_id),
                    "grade": grade,
                    "chapter_id": chapter_id_to_return
                }), 201
            
        return jsonify({"status": "error", "message": "Failed to create chapter"}), 500
    except Exception as e:
        print(f"Upload Lesson error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@courses_bp.route('/upload-quiz', methods=['POST'])
def upload_quiz():
    try:
        data = request.json
        subject_id = data.get('subjectId')
        grade = data.get('grade')
        chapter_number = data.get('chapterNumber')
        title = data.get('title')
        questions = data.get('questions', [])
        
        # 1. Create or Update chapter first
        chapter_model = get_chapter_model()
        existing_chapter_id = chapter_model.find_chapter_by_number(subject_id, chapter_number)
        
        if existing_chapter_id:
            chapter_model.update_chapter(existing_chapter_id, title=title)
            final_chapter_id = existing_chapter_id
        else:
            final_chapter_id = chapter_model.create_chapter(subject_id, chapter_number, title, "0")
        
        if final_chapter_id:
            # 2. Save quiz questions
            quiz_model = get_quiz_model()
            success = quiz_model.save_quiz_questions(final_chapter_id, questions)
            
            if success:
                return jsonify({
                    "status": "success",
                    "title": title,
                    "subject": str(subject_id),
                    "grade": grade,
                    "chapter_id": final_chapter_id
                }), 201
        
        return jsonify({"status": "error", "message": "Failed to create quiz"}), 500
    except Exception as e:
        print(f"Upload Quiz error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@courses_bp.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected file"}), 400

        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            return jsonify({"status": "success", "url": file_path}), 201
            
        return jsonify({"status": "error", "message": "Upload failed"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
