__author__ = 'am6puk'
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import Encoders
import os
import ConfigParser

name = 'simple_backup.conf'
conf_path = '/etc/simple_backup/'
config = ConfigParser.ConfigParser()
config.read(conf_path+name)
SMTP_HOST = config.get('smtp', 'SMTP_HOST')
SMTP_PORT = config.get('smtp', 'SMTP_PORT')
SMTP_USER = config.get('smtp', 'SMTP_USER')
SMTP_PASS = config.get('smtp', 'SMTP_PASS')
TO = config.get('smtp', 'TO')



gmail_user = SMTP_USER
gmail_pwd = SMTP_PASS

def mail(to, subject, text, attach=None):
   msg = MIMEMultipart()
   msg['From'] = gmail_user
   msg['To'] = to
   msg['Subject'] = subject
   msg.attach(MIMEText(text))
   if attach:
      part = MIMEBase('application', 'octet-stream')
      part.set_payload(open(attach, 'rb').read())
      Encoders.encode_base64(part)
      part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attach))
      msg.attach(part)
   mailServer = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.ehlo()
   mailServer.login(gmail_user, gmail_pwd)
   mailServer.sendmail(gmail_user, to, msg.as_string())
   mailServer.close()

def send(subject, text):
    mail(TO, subject, text)
