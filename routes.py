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
from werkzeug.wrappers.response import Response

from database import User as UserModel
from feeds import fetch_and_store_feed
from forms import AddFeedForm, LoginForm, OpmlUploadForm
from login import User
from opml import import_opml


def add_feed() -> Response:
    """Add feed route. Takes a URL, tries to fetch it as a feed, then adding or updating a source for that feed as
    necessary.

    :return: A redirect to the landing page.
    """

    # build the redirect, regardless of the result, we're currently always redirecting to the landing
    url = url_for('root')
    output = redirect(url)

    # validate form data
    form = AddFeedForm()
    if not form.validate_on_submit():
        flash('Invalid feed.', 'error')
        return output

    url = form.url.data
    with db_session:
        user = UserModel[current_user.user_id]
        fetch_and_store_feed(url, [], user)

    return output


def login() -> Response:
    """Login route. Processes post messages from the login form.

    :return: A redirect to the landing page.
    """

    # build the redirect, regardless of the result, we're currently always redirecting to the landing
    url = url_for('root')
    output = redirect(url)

    # validate form data
    form = LoginForm()
    if not form.validate_on_submit():
        flash('User login failed.', 'error')
        return output

    name = form.name.data
    password = form.password.data

    with db_session:
        # validate user & password
        model = UserModel.get(name=name)
        if not model or not check_password_hash(model.password_hash, password):
            flash('User login failed.', 'error')
            return output

        # login the user
        user = User(model.user_id, model.name)
        login_user(user, remember=True)
        flash(f'User "{name}" logged in.', 'info')

        return output


@login_required
def logout() -> Response:
    """Logout route. Logs the current user out.

    :return: A redirect to the landing page.
    """

    name = current_user.name
    logout_user()
    flash(f'User "{name}" logged out.', 'info')
    url = url_for('root')
    output = redirect(url)
    return output


def root() -> str:
    """Root index/landing route. Landing page for the site. Currently the only page with content.

    :return: A string of the rendered page.
    """

    context = {
        'add_feed_form': AddFeedForm(),
        'login_form': LoginForm(),
        'opml_upload_form': OpmlUploadForm()
    }
    output = render_template('root.html', **context)
    return output


@login_required
def upload_opml() -> Response:
    """OPML upload route. Handles the posting of an OPML file for importing feeds.

    :return: A redirect to the landing page.
    """

    # build the redirect
    url = url_for('root')
    output = redirect(url)

    # validate the form
    form = OpmlUploadForm()
    if not form.validate_on_submit():
        flash('Form bad')
        return output

    # import the feeds
    import_opml(form.opml.data.stream, current_user.user_id)

    return output
