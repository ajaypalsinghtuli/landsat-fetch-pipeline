import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_status_email(recipient_email, task_id, status, file_path=None):
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

    msg = EmailMessage()
    msg['Subject'] = f"Landsat Fetch Pipeline - Task {status}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email

    if status == "Completed":
        content = f"Your Landsat data processing (Task ID: {task_id}) is complete.\nDownloaded to: {file_path}"
    else:
        content = f"Your Landsat data processing (Task ID: {task_id}) failed."

    msg.set_content(content)

    try:
        if SENDER_EMAIL and SENDER_PASSWORD:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()
        else:
            print(f"MOCK EMAIL SENT TO: {recipient_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")