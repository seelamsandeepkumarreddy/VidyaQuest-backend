import MySQLdb
import json

def audit():
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='ruralquest_db')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # 1. Audit missing PDFs per Grade/Subject
        query = """
            SELECT s.grade, s.title as subject, COUNT(*) as missing_count
            FROM chapters c
            JOIN subjects s ON c.subject_id = s.id
            WHERE c.pdf_url IS NULL OR c.pdf_url = ''
            GROUP BY s.grade, s.title
            ORDER BY s.grade, s.title
        """
        cur.execute(query)
        missing_by_subject = cur.fetchall()
        
        # 2. Get total count
        cur.execute("SELECT COUNT(*) as total FROM chapters")
        total_chapters = cur.fetchone()['total']
        
        cur.execute("SELECT COUNT(*) as total_missing FROM chapters WHERE pdf_url IS NULL OR pdf_url = ''")
        total_missing = cur.fetchone()['total_missing']
        
        # 3. List some sample PDF URLs for Grade 8 Math
        cur.execute("""
            SELECT s.title as subject, c.chapter_number, c.title as chapter, c.pdf_url
            FROM chapters c
            JOIN subjects s ON c.subject_id = s.id
            WHERE s.grade = '8' AND s.title = 'Mathematics'
            LIMIT 20
        """)
        math_pdfs = cur.fetchall()
        
        print(f"Total Chapters: {total_chapters}")
        print(f"Total Missing PDFs: {total_missing}")
        print("\nMissing by Subject:")
        for row in missing_by_subject:
            print(f"Grade {row['grade']} - {row['subject']}: {row['missing_count']} missing")
            
        print("\nMath PDFs for Grade 8:")
        for row in math_pdfs:
            print(f"Ch {row['chapter_number']}: {row['pdf_url']}")
            
        conn.close()
    except Exception as e:
        print('Error:', e)

if __name__ == '__main__':
    audit()
