import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.contrib.auth.models import User
from .models import *

def send_mail(uid):
    sender_email = "veilmsg@yandex.com"
    password = "suewpzvttlkjgjax"
    recipient_email = ''
    msg_count = 0

    usrs = User.objects.filter(id=uid)
    usr = usrs[0]
    if usr.email == '':
        return 0

    recipient_email = usr.email

    dms = dm.objects.filter(sentTo=usr,opened=False).order_by("-pk")
    msg_count = len(dms)


    # Create the message
    message = MIMEMultipart("alternative")
    message["Subject"] = "You have "+str(msg_count)+" new anonymous messages - VeilMsg"
    message["From"] = sender_email
    message["To"] = recipient_email

    # Create the plain text and HTML parts
    text = "You have "+str(msg_count)+" new anonymous messages - VeilMsg"
    html = """\
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Your Email Subject</title>
        <style>
        </style>
    </head>
    <body>
        <div class="header">
            <h1>VeilMsg</h1>
        </div>
        <b>Hey there, """+usr.username+"""!</b>
        <br>
        <p>Guess what? """+str(msg_count)+""" new messages just landed in your inbox!</p>
        <p>Check your inbox to see what's waiting for you.</p>
        <br><br>
        <a href="https://veilmsg.pythonanywhere.com/inbox/" style="background-color: #00ee6e;  font-weight : 900; color: black; padding: 10px 30px; text-decoration: none; border-radius: 500px;">View Messages</a>
        <br><br><br>
        <p>from VeilMsg</p>
    </body>
    </html>

    """

    # Attach the parts to the message
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    # Send the email
    try:
        with smtplib.SMTP_SSL("smtp.yandex.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print("Error sending email:", e)
        return 1

    return 0
