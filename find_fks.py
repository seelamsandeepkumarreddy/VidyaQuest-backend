import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

def find_study_time_fks():
    try:
        db = MySQLdb.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            passwd=os.getenv('MYSQL_PASSWORD'),
            db=os.getenv('MYSQL_DB')
        )
        cur = db.cursor()
        
        db_name = os.getenv('MYSQL_DB')
        
        print(f"Searching for ANY foreign key referencing 'study_time' in database '{db_name}'...")
        
        # Use a literal here for simplicity
        query = (
            "SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME "
            "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
            f"WHERE REFERENCED_TABLE_SCHEMA = '{db_name}' AND REFERENCED_TABLE_NAME LIKE '%study_time%'"
        )
        
        cur.execute(query)
        fks = cur.fetchall()
        
        if fks:
            print(f"Found {len(fks)} matching foreign keys:")
            for fk in fks:
                print(f"Table: {fk[0]}, Column: {fk[1]}, Constraint: {fk[2]}, RefTable: {fk[3]}, RefColumn: {fk[4]}")
        else:
            print("No foreign keys matching 'study_time' found.")
        
        db.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")

if __name__ == "__main__":
    find_study_time_fks()
