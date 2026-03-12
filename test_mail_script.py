import smtplib
from email.message import EmailMessage

sender_email = "libraria.lmsystem@gmail.com"
sender_password = "lviskuzebhmekair"
smtp_server = "smtp.gmail.com"
smtp_port = 587

msg = EmailMessage()
msg['Subject'] = "Test"
msg['From'] = sender_email
msg['To'] = sender_email
msg.set_content("Test message works perfectly!")

try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        print("Success! Email works.")
except Exception as e:
    print("Error:", e)
