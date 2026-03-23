-- 1. Create the Database
CREATE DATABASE IF NOT EXISTS ruralquest_db;
USE ruralquest_db;

-- 2. Create the Users Table (Core Info)
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(20) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(15),
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'faculty', 'admin', 'teacher') DEFAULT 'student',
    settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create the Students Table (Student Specific Stats & Info)
CREATE TABLE IF NOT EXISTS students (
    user_id VARCHAR(20) PRIMARY KEY,
    grade VARCHAR(10) NOT NULL,
    total_xp INT DEFAULT 0,
    perfect_quizzes INT DEFAULT 0,
    high_accuracy_quizzes INT DEFAULT 0,
    total_study_time INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Create the Teachers Table (Teacher Specific Info)
CREATE TABLE IF NOT EXISTS teachers (
    user_id VARCHAR(20) PRIMARY KEY,
    assigned_grade VARCHAR(10), -- The grade they are assigned to
    subject_expertise VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 5. Create the Attendance Table
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    grade VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    status ENUM('PRESENT', 'ABSENT') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_attendance (student_id, date)
);

-- 6. Create the Announcements Table
CREATE TABLE IF NOT EXISTS announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    author_id VARCHAR(20) NOT NULL,
    target_grade VARCHAR(10) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 7. Create the Student Progress Table (Legacy - keeping for compatibility)
CREATE TABLE IF NOT EXISTS student_progress (
    student_id VARCHAR(20) PRIMARY KEY,
    xp INT DEFAULT 0,
    lessons_completed INT DEFAULT 0,
    quiz_accuracy INT DEFAULT 0,
    study_time_minutes INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 8. Create the Quiz Progress Table
CREATE TABLE IF NOT EXISTS quiz_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    grade VARCHAR(10) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    chapter VARCHAR(150) NOT NULL,
    score INT NOT NULL,
    xp INT NOT NULL,
    badge VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 9. Create the Subjects Table
CREATE TABLE IF NOT EXISTS subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grade VARCHAR(10) NOT NULL,
    title VARCHAR(100) NOT NULL,
    subtitle VARCHAR(150),
    icon_res VARCHAR(100), -- Resource name for frontend
    tint_color VARCHAR(20), -- Hex color
    bg_color VARCHAR(20), -- Hex color
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_subject (grade, title)
);

-- 10. Create the Chapters Table
CREATE TABLE IF NOT EXISTS chapters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    chapter_number INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    lessons_count INT DEFAULT 5,
    is_offline BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- 11. Create the Questions Table
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chapter_id INT NOT NULL,
    question_text TEXT NOT NULL,
    options JSON NOT NULL, -- JSON array of strings
    correct_option_index INT NOT NULL,
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
);

-- 12. Create the Daily Challenges Table
CREATE TABLE IF NOT EXISTS daily_challenges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    author_id VARCHAR(20) NOT NULL,
    grade VARCHAR(10) NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    questions JSON NOT NULL, -- JSON array of question objects
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 13. Create the Assignments Table
CREATE TABLE IF NOT EXISTS assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    author_id VARCHAR(20) NOT NULL,
    grade VARCHAR(10) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    chapter VARCHAR(150),
    title VARCHAR(150) NOT NULL,
    description TEXT,
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);
