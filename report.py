import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


toaddr = None  # String. Destination e-mail address

fromaddr = None  # String. E-mail address
mypass = None  # String. E-mail password
smtpserver = None  # String. E-mail smtp server
port = 465


def send():
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = 'Notification from server'

    body = 'Bot is down!'
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP_SSL(smtpserver, port)
    server.login(fromaddr, mypass)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
