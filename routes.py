# Copyright 2019 Matthew Bishop
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from pony.orm import db_session
from werkzeug.security import check_password_hash

from database import User as UserModel
from forms import LoginForm, OpmlUploadForm
from login import User
from opml import import_opml


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
    opml_upload_form = OpmlUploadForm()
    output = render_template('root.html', login_form=login_form, opml_upload_form=opml_upload_form)
    return output


@login_required
def upload_opml():
    url = url_for('root')
    output = redirect(url)
    form = OpmlUploadForm()
    if not form.validate_on_submit():
        flash('Form bad')
        return output

    import_opml(form.opml.data.stream)
    return output
