import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

def find_all_fks():
    try:
        db = MySQLdb.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            passwd=os.getenv('MYSQL_PASSWORD'),
            db=os.getenv('MYSQL_DB')
        )
        cur = db.cursor()
        
        db_name = os.getenv('MYSQL_DB')
        
        print(f"Finding ALL foreign keys in database '{db_name}'...")
        
        query = (
            "SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME "
            "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
            "WHERE REFERENCED_TABLE_SCHEMA = %s"
        )
        
        cur.execute(query, (db_name,))
        fks = cur.fetchall()
        
        print("Foreign Keys Found:")
        for fk in fks:
            print(f"Table: {fk[0]}, Column: {fk[1]}, Constraint: {fk[2]}, RefTable: {fk[3]}, RefColumn: {fk[4]}")
            if fk[3] == 'study_time':
                print(">>> FOUND REFERENCE TO study_time!")
        
        db.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")

if __name__ == "__main__":
    find_all_fks()
