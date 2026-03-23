import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    # MySQL Configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'ruralquest_db')
    MYSQL_CURSORCLASS = 'DictCursor'
    
    # Secret Key for session handling
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key_change_me')

    # Email Service (Gmail SMTP)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_SENDER = os.getenv('MAIL_USERNAME')
