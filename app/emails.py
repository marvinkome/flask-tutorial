from flask import render_template, current_app, copy_current_request_context
from flask_mail import Message
from . import mail
from threading import Thread

def send_email(to, subject, template, **kwargs):
    msg = Message(current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, 
                  sender=current_app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)

    @copy_current_request_context
    def send_asc_mail(msg):
        mail.send(msg)

    thr = Thread(name='emails',target=send_asc_mail, args=(msg,))
    thr.start()