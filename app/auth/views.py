from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from ..models import User
from ..emails import send_email
from .forms import LoginForm, RegistrationForm
from . import auth
from .. import db

@auth.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))

        flash('Invalid username or password')

    return render_template('auth/login.html', form=form)

@auth.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash('You have been looged out')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm your account', 'auth/email/confirm', user=user, token=token)
        flash('We\'ve send a confimation mail to you')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account, Thanks')
    else:
        flash('Your confirmation link is invalid or expired')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping() 
        print(request.endpoint)
        if not current_user.confirmed and request.endpoint is not None:
            if request.endpoint[:5] != 'auth.':
                return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirm():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm your account', 'auth/email/confirm', token=token)
    flash('A new confirmation has been sent')
    return redirect(url_for('main.index'))
