import MySQLdb

def update_ch4():
    try:
        conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='ruralquest_db')
        cur = conn.cursor()
        
        # ID 100 is "Tribal Diku" (Grade 8 Social Studies Ch 4)
        new_url = "/api/pdfs/social_studies_8_tribal_diku.pdf"
        cur.execute("UPDATE chapters SET pdf_url = %s WHERE id = 100", (new_url,))
        conn.commit()
        print(f"Updated Chapter 100 to {new_url}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    update_ch4()
