import smtplib
from email.message import EmailMessage

def send_status_email(recipient_email, task_id, status, file_path=None):
    """
    Constructs and sends an email notification to the user regarding their Landsat job.
    """
    # In production, these should be loaded from environment variables (e.g., .env file)
    SMTP_SERVER = "smtp.gmail.com" 
    SMTP_PORT = 587
    SENDER_EMAIL = "your-email@gmail.com" 
    SENDER_PASSWORD = "your-app-password"

    msg = EmailMessage()
    msg['Subject'] = f"Landsat Fetch Pipeline - Task {status}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email

    if status == "Completed":
        content = (
            f"Hello,\n\n"
            f"Your Landsat data processing (Task ID: {task_id}) is complete.\n\n"
            f"The image has been successfully downloaded to your local machine at:\n"
            f"{file_path}\n\n"
            f"Thank you for using the pipeline."
        )
    else:
        content = (
            f"Hello,\n\n"
            f"Your Landsat data processing (Task ID: {task_id}) failed.\n"
            f"Please try submitting again with a different date range or a smaller bounding box."
        )

    msg.set_content(content)

    try:
        # --- PRODUCTION CODE (Uncomment when you have a real sender email/password) ---
        # server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        # server.starttls()
        # server.login(SENDER_EMAIL, SENDER_PASSWORD)
        # server.send_message(msg)
        # server.quit()
        
        # --- DEVELOPMENT CODE (Mocks the email in your terminal) ---
        print("\n" + "="*50)
        print(f"MOCK EMAIL SENT TO: {recipient_email}")
        print(f"SUBJECT: {msg['Subject']}")
        print(f"CONTENT:\n{content}")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"Failed to send email: {e}")