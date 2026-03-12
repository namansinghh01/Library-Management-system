import smtplib
from email.message import EmailMessage
import os
import threading

def send_email_async(to_email, subject, body):
    sender_email = os.environ.get("SMTP_EMAIL", "libraria.lmsystem@gmail.com")
    sender_password = os.environ.get("SMTP_PASSWORD", "lviskuzebhmekair")
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    
    if sender_email == "your_email@gmail.com":
         print("WARNING: SMTP_EMAIL not configured, skipping email.")
         return

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f"Email successfully sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {e}")

def send_registration_email(to_email, name, role):
    subject = "Welcome to the Library Management System!"
    if role == "student":
        body = f"Hello {name},\n\nYour student account has been successfully created. You can now login to the system using your email address.\n\nBest regards,\nLibraria Team"
    elif role == "author":
        body = f"Hello {name},\n\nYour author account has been successfully created. You can now login to the system and manage your books.\n\nBest regards,\nLibraria Team"
    else:
        body = f"Hello {name},\n\nYour account has been successfully created.\n\nBest regards,\nLibraria Team"
        
    # Run in a separate thread so it doesn't block the request response
    thread = threading.Thread(target=send_email_async, args=(to_email, subject, body))
    thread.daemon = True
    thread.start()

def send_otp_email(to_email, otp):
    subject = "Your Registration OTP - Libraria"
    body = f"Hello,\n\nYour One-Time Password (OTP) for registration is: {otp}\n\nPlease enter this OTP to complete your registration process.\n\nBest regards,\nLibrary Management Team"
    thread = threading.Thread(target=send_email_async, args=(to_email, subject, body))
    thread.daemon = True
    thread.start()

def send_otp_sms(phone, otp):
    # This is a simulated SMS sender since we don't have a real gateway configured like Twilio
    print(f"\n=========================================")
    print(f"📡 SIMULATED SMS SENT TO {phone}")
    print(f"💬 OTP is: {otp}")
    print(f"=========================================\n")
