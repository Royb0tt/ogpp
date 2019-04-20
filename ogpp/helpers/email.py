from threading import Thread
from flask import current_app
from flask_mail import Message
from .. import mail


def send_email(subject, recipients, text_body, html_body):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body

    thread_args = (current_app._get_current_object(), msg)
    Thread(target=send_async_mail, args=thread_args).start()


def send_async_mail(app, message):
    with app.app_context():
        mail.send(message)
