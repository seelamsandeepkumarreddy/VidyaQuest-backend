import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

def find_study_time_reference():
    try:
        db = MySQLdb.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            passwd=os.getenv('MYSQL_PASSWORD'),
            db=os.getenv('MYSQL_DB')
        )
        cur = db.cursor()
        
        db_name = os.getenv('MYSQL_DB')
        
        print(f"Searching for 'study_time' references in database '{db_name}'...")
        
        # Check Views definitions - use %% for literal %
        cur.execute("SELECT TABLE_NAME, VIEW_DEFINITION FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_SCHEMA = %s AND VIEW_DEFINITION LIKE '%%study_time%%'", (db_name,))
        print("Views matching:", cur.fetchall())
        
        # Check Trigger definitions
        cur.execute("SELECT TRIGGER_NAME, ACTION_STATEMENT FROM INFORMATION_SCHEMA.TRIGGERS WHERE TRIGGER_SCHEMA = %s AND ACTION_STATEMENT LIKE '%%study_time%%'", (db_name,))
        print("Triggers matching:", cur.fetchall())
        
        # Check Foreign Key Constraints - correcting the LIKE parameter counts
        cur.execute("SELECT TABLE_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA = %s AND (TABLE_NAME LIKE '%%study_time%%' OR REFERENCED_TABLE_NAME LIKE '%%study_time%%')", (db_name,))
        print("FKs matching:", cur.fetchall())
        
        db.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")

if __name__ == "__main__":
    find_study_time_reference()
