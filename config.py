import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    POSTS_PER_PAGE = os.environ.get('POSTS_PER_PAGE', 5)

    SECRET_KEY = os.environ.get('SECRET KEY', os.urandom(16).hex())

    RIOT_API_KEY = os.environ.get('RIOT_API_KEY')

    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = os.environ.get('MAIL_PORT', 465)
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', True)
    # email ogppsupport@gmail.com
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'email-test@example.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'your-password')

    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
    MAIL_ADMIN = os.environ.get('MAIL_ADMIN', MAIL_USERNAME)
