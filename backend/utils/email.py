import os

from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailUtils:
    def __init__(self):
        self.sender = os.environ.get('EMAIL_SENDER')
        self.password = os.environ.get('EMAIL_PASSWORD')
        self.smtp_server = os.environ.get('SMTP_SERVER')

    def confirm_user(self, email: str, user_id: str, confirmation_code: str):
        subject = '[TokComp] Please Confirm Your E-mail Address'
        body = '''Hello from TokComp!

You're receiving this e-mail because user {email} has registered an account on https://tokcomp.io

To confirm this is correct, go to https://app.tokcomp.io/confirm_user/{user_id}/{confirmation_code}

Thank you for using TokComp!
https://tokcomp.io
'''.format(email=email, user_id=user_id, confirmation_code=confirmation_code)

        message = MIMEMultipart()
        message['Subject'] = subject
        message.attach(MIMEText(body))
        msg = message.as_string()

        server = SMTP(self.smtp_server)
        server.starttls()
        server.login(self.sender, self.password)
        server.sendmail(self.sender, email, msg)
        server.quit()

    def forgot_password(self, email: str, user_id: str, change_password_code: str):
        subject = '[TokComp] Reset your Password'
        body = '''Hello from TokComp!

You're receiving this e-mail because you have requested a password reset on https://tokcomp.io

To reset your password, go to https://app.tokcomp.io/reset_password/{user_id}/{change_password_code}

The link will expire in 1 hour if not used.

Thank you for using TokComp!
https://tokcomp.io
'''.format(email=email, user_id=user_id, change_password_code=change_password_code)

        message = MIMEMultipart()
        message['Subject'] = subject
        message.attach(MIMEText(body))
        msg = message.as_string()

        server = SMTP(self.smtp_server)
        server.starttls()
        server.login(self.sender, self.password)
        server.sendmail(self.sender, email, msg)
        server.quit()
