import MySQLdb

def final_audit():
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='ruralquest_db')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # 1. Total chapters check
        cur.execute("SELECT COUNT(*) as total FROM chapters")
        total = cur.fetchone()['total']
        
        # 2. Check for missing or empty PDF URLs
        cur.execute("SELECT COUNT(*) as missing FROM chapters WHERE pdf_url IS NULL OR pdf_url = ''")
        missing = cur.fetchone()['missing']
        
        # 3. Check for the placeholder /api/pdfs/sample.pdf
        cur.execute("SELECT COUNT(*) as placeholders FROM chapters WHERE pdf_url = '/api/pdfs/sample.pdf'")
        placeholders = cur.fetchone()['placeholders']
        
        # 4. Find anything else (actual uploads)
        cur.execute("SELECT COUNT(*) as uploads FROM chapters WHERE pdf_url IS NOT NULL AND pdf_url != '' AND pdf_url != '/api/pdfs/sample.pdf'")
        uploads = cur.fetchone()['uploads']
        
        print(f"Audit Results:")
        print(f"Total Chapters in DB: {total}")
        print(f"Missing (empty/NULL): {missing}")
        print(f"Using placeholder (/api/pdfs/sample.pdf): {placeholders}")
        print(f"Using specific uploads: {uploads}")
        
        if missing > 0:
            print("\nUpdating missing chapters to use /api/pdfs/sample.pdf...")
            cur.execute("UPDATE chapters SET pdf_url = '/api/pdfs/sample.pdf' WHERE pdf_url IS NULL OR pdf_url = ''")
            conn.commit()
            print(f"Fixed {missing} chapters.")
            
        conn.close()
    except Exception as e:
        print(f"Audit error: {e}")

if __name__ == '__main__':
    final_audit()
