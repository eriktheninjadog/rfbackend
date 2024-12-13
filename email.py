import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import dbconfig

def send_email(sender_email, receiver_email, subject, message):
    """
    Sends an email using SMTP.

    Args:
        sender_email (str): The email address of the sender.
        sender_password (str): The password for the sender's email account.
        receiver_email (str): The email address of the recipient.
        subject (str): The subject of the email.
        message (str): The body of the email.
    """
    # Email server details (for Gmail, use smtp.gmail.com)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # Port for TLS

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the message body
    msg.attach(MIMEText(message, 'plain'))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Upgrade the connection to secure

        # Login to the sender's email account
        server.login(sender_email, dbconfig.get_email_password())

        # Send the email
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")

    except Exception as e:
        print(f"Error sending email: {e}")

    finally:
        # Close the connection to the server
        server.quit()

# Example Usage
if __name__ == "__main__":
    # Sender's email credentials
    sender_email = "erik.tamm@eriktamm.com"  # Replace with your email

    # Recipient's email
    receiver_email = "erik.tamm@eriktamm.com"  # Replace with the recipient's email

    # Email content
    subject = "Test Email from Python Script"
    message = "This is a test email sent from a Python script."

    # Send the email
    send_email(sender_email,receiver_email, subject, message)
