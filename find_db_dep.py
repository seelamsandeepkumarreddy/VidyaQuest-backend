import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

def find_study_time():
    try:
        db = MySQLdb.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            passwd=os.getenv('MYSQL_PASSWORD'),
            db=os.getenv('MYSQL_DB')
        )
        cur = db.cursor()
        
        db_name = os.getenv('MYSQL_DB')
        search_term = '%study_time%'
        
        print(f"Searching for '{search_term}' in INFORMATION_SCHEMA for database '{db_name}'...")
        
        # Check Views
        cur.execute("SELECT TABLE_NAME, VIEW_DEFINITION FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_SCHEMA = %s AND VIEW_DEFINITION LIKE %s", (db_name, search_term))
        views = cur.fetchall()
        print(f"Views matching: {views}")
        
        # Check Triggers
        cur.execute("SELECT TRIGGER_NAME, EVENT_OBJECT_TABLE, ACTION_STATEMENT FROM INFORMATION_SCHEMA.TRIGGERS WHERE TRIGGER_SCHEMA = %s AND ACTION_STATEMENT LIKE %s", (db_name, search_term))
        triggers = cur.fetchall()
        print(f"Triggers matching: {triggers}")
        
        # Check Procedures
        cur.execute("SELECT ROUTINE_NAME, ROUTINE_DEFINITION FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_SCHEMA = %s AND (ROUTINE_DEFINITION LIKE %s OR ROUTINE_NAME LIKE %s)", (db_name, search_term, search_term))
        routines = cur.fetchall()
        print(f"Routines matching: {routines}")
        
        # Check Table names
        cur.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s AND TABLE_NAME LIKE %s", (db_name, search_term))
        tables = cur.fetchall()
        print(f"Tables matching: {tables}")
        
        # Check Column names
        cur.execute("SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND COLUMN_NAME LIKE %s", (db_name, search_term))
        columns = cur.fetchall()
        print(f"Columns matching: {columns}")
        
        db.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")

if __name__ == "__main__":
    find_study_time()
