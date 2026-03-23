import MySQLdb
import config
from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config.from_object(config.Config)

mysql = MySQL(app)

def run_setup():
    with app.app_context():
        try:
            # First, raw connection to create DB if not exists
            db = MySQLdb.connect(host=config.Config.MYSQL_HOST, user=config.Config.MYSQL_USER, passwd=config.Config.MYSQL_PASSWORD)
            cursor = db.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.Config.MYSQL_DB};")
            db.commit()
            cursor.close()
            db.close()
            
            # Now use MySQL extension
            cur = mysql.connection.cursor()
            
            with open('db_setup.sql', 'r') as f:
                sql_file = f.read()
                
            # Split into individual statements
            sql_commands = sql_file.split(';')
            
            for command in sql_commands:
                try:
                    if command.strip() != '':
                        cur.execute(command)
                except Exception as e:
                    print(f"Skipped execution of command: {e}")
                    
            mysql.connection.commit()
            cur.close()
            print("Successfully executed db_setup.sql!")
        except Exception as e:
            print(f"Failed to setup DB: {e}")

if __name__ == '__main__':
    run_setup()
