from flask import url_for, Blueprint, current_app, render_template, redirect
from ..forms import SummonerSearchForm, ContactForm
from ..email_helpers import send_email


index_bp = Blueprint('home', __name__)


@index_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    contact_form = ContactForm()
    if contact_form.validate_on_submit():
        sender_email = contact_form.email.data
        sender_name = contact_form.name.data
        email_subject = contact_form.subject.data
        email_message = contact_form.message.data
        recipients = [current_app.config['MAIL_ADMIN']]

        email_template = '''
        From: {} <{}>

        Message:
        {}
        '''
        email_body = email_template.format(sender_name, sender_email, email_message)

        send_email(email_subject, recipients, email_body, html_body=None)
        return render_template('contact.html', success=True)

    return render_template('contact.html', contact_form=contact_form)


@index_bp.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@index_bp.route('/', methods=['GET', 'POST'])
@index_bp.route('/home', methods=['GET', 'POST'])
def index():
    title = 'ogpp: The Old Games & Player Profiles League Database'
    form = SummonerSearchForm()
    if form.validate_on_submit():
        return redirect(url_for('summoner.summoner', name=form.summoner.data))

    return render_template('index.html', title=title, form=form, index=True)
