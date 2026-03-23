import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()

def test_smtp():
    server_addr = "smtp.gmail.com"
    port = 587
    user = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')

    if not user or not password or "your-email" in user:
        print("❌ ERROR: Please set valid MAIL_USERNAME and MAIL_PASSWORD in your .env file first!")
        return

    print(f"Testing SMTP_SSL connection for {user} on port 465...")
    try:
        msg = MIMEText("Test SSL connection from RuralQuest Backend")
        msg['Subject'] = "SMTP SSL Test"
        msg['From'] = user
        msg['To'] = user

        with smtplib.SMTP_SSL(server_addr, 465) as server:
            server.login(user, password)
            server.send_message(msg)
            
        print("✅ SUCCESS: SMTP connection and login verified! Test email sent to yourself.")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print("\nCommon fixes:")
        print("1. Ensure you are using a 'Google App Password', not your regular login password.")
        print("2. Verify your internet connection.")

if __name__ == "__main__":
    test_smtp()
