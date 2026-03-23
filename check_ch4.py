import MySQLdb

def check_chapter():
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='ruralquest_db')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # Get Social Studies Grade 8 subject
        cur.execute("SELECT id FROM subjects WHERE grade = '8' AND title = 'Social Studies'")
        sub = cur.fetchone()
        if not sub:
            print("Subject NOT FOUND")
            return
        
        # Get Chapter 4
        cur.execute("SELECT id, title, pdf_url FROM chapters WHERE subject_id = %s AND chapter_number = 4", (sub['id'],))
        ch = cur.fetchone()
        if not ch:
            print("Chapter NOT FOUND")
        else:
            print(f"Chapter: {ch['title']} | ID: {ch['id']}")
            print(f"PDF URL: {ch['pdf_url']}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_chapter()
