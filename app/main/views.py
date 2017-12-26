from flask import render_template, redirect, session, url_for, flash
from . import main
from .. import db
from .forms import NameForm
from ..models import User

@main.route('/')
def index():
    name = session.get('name')
    return render_template('index.html', name=name, current_time = datetime.datetime.utcnow())

@main.route('/user', methods=['GET','POST'])
def user():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False

        else:
            session['known'] = True

        if old_name is not None and old_name != form.name.data:
            flash('Name has been changed')

        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('.user'))

    return render_template('user.html',
                            form=form,
                            user=session.get('name'),
                            known=session.get('known', False))