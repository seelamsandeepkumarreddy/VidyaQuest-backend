import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

def test_otp_delivery(receiver_email):
    sender_email = os.getenv('MAIL_USERNAME')
    sender_password = os.getenv('MAIL_PASSWORD')
    otp = "123456"

    if not sender_email or not sender_password:
        print("❌ ERROR: MAIL_USERNAME or MAIL_PASSWORD not set in .env")
        return

    message = MIMEMultipart("alternative")
    message["Subject"] = f"{otp} is your RuralQuest verification code"
    message["From"] = f"RuralQuest <{sender_email}>"
    message["To"] = receiver_email

    text = f"Your RuralQuest verification code is: {otp}"
    html = f"""
    <html>
      <body>
        <h1>RuralQuest</h1>
        <p>Your verification code is: <strong>{otp}</strong></p>
      </body>
    </html>
    """
    
    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    print(f"Testing OTP delivery to {receiver_email} using SSL/465...")
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.set_debuglevel(1)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("✅ SUCCESS: OTP email sent!")
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    email = os.getenv('MAIL_USERNAME') # Send to self for test
    test_otp_delivery(email)
