from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from pony.orm import db_session
from werkzeug.security import check_password_hash

from database import User as UserModel
from forms import LoginForm
from login import User


def login():
    url = url_for('root')
    output = redirect(url)

    form = LoginForm()
    if not form.validate_on_submit():
        flash('User login failed.', 'error')
        return output

    name = form.name.data
    password = form.password.data

    with db_session:
        model = UserModel.get(name=name)
        if not model or not check_password_hash(model.password_hash, password):
            flash('User login failed.', 'error')
            return output

        user = User(model.user_id, model.name)
        login_user(user, remember=True)
        flash(f'User "{name}" logged in.', 'info')

        return output


@login_required
def logout():
    name = current_user.name
    logout_user()
    flash(f'User "{name}" logged out.', 'info')
    url = url_for('root')
    output = redirect(url)
    return output


def root():
    login_form = LoginForm()
    output = render_template('root.html', login_form=login_form)
    return output
