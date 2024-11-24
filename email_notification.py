import smtplib
from email.mime.text import MIMEText
import os

def send_email(to_email, subject, message):
    try:
        # SMTP server configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv("SENDER_EMAIL")  # Ensure environment variable is set
        sender_password = os.getenv("SENDER_PASSWORD")  # Use App Password for Gmail

        if not sender_email or not sender_password:
            print("Missing sender email or password.")
            return

        # Create the email
        msg = MIMEText(message, "plain")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email

        # Debug the message
        print("Message being sent:")
        print(msg.as_string())

        # Connect to the server and send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()

        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

send_email("lopezalejandro5b@gmail.com", "Test", "This is a test")
