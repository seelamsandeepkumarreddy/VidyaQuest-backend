import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

def list_views():
    try:
        db = MySQLdb.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            passwd=os.getenv('MYSQL_PASSWORD'),
            db=os.getenv('MYSQL_DB')
        )
        cur = db.cursor()
        
        print("Listing all views in the database...")
        cur.execute("SHOW FULL TABLES WHERE TABLE_TYPE = 'VIEW'")
        views = cur.fetchall()
        
        if not views:
            print("No views found.")
        else:
            for view in views:
                print(f"View Name: {view[0]}")
                # Get view definition
                try:
                    cur.execute(f"SHOW CREATE VIEW {view[0]}")
                    print(f"Definition: {cur.fetchone()[1]}")
                except Exception as e:
                    print(f"Error reading view {view[0]}: {e}")
        
        db.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")

if __name__ == "__main__":
    list_views()
