#coding=utf-8
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

from email.utils import COMMASPACE, formatdate
from email import encoders

from django.core.mail import send_mail

#send email

class MailSender(object):
    '''邮件发送器'''
    def __init__(self, name, user, pwd):
        self.name = name    #邮件服务器
        self.user = user    #用户名
        self.pwd = pwd      #密码

    def send(self, sender, receiver, subject, content, files=[]):
        receiver = receiver.split(',')
        # print receiver
        # send_mail(subject, content, sender, receiver,fail_silently=False)

        # msg = MIMEMultipart()
        # msg['From'] = sender
        # msg['Subject'] = subject
        # msg['To'] = receiver
        # msg['Date'] = formatdate(localtime=True)
        # msg.attach(MIMEText(content, 'html', 'utf-8'))

        # for f in files:
        #     part = MIMEBase('application', 'octet-stream')
        #     part.set_payload(open(f, 'rb', read()))
        #     encoders.encode_base64(part)
        #     part.add_header('Content-Disposition', 'attachment: filename="%s"' % os.path.basename(f))
        #     msg.attach(part)
        # import smtplib
        # try:
        #     smtp = smtplib.SMTP(self.name)
        #     smtp.login(self.user, self.pwd)
        #     smtp.sendmail(sender, receiver, msg.as_string())
        #     smtp.close()
        # except:
        #     return False
        return True