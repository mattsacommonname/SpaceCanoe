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


from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired


OPML_FILE_EXTENSIONS = ['opml', 'xml']


class LoginForm(FlaskForm):
    name = StringField('User name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class OpmlUploadForm(FlaskForm):
    opml = FileField('OPML File', validators=[DataRequired(), FileAllowed(OPML_FILE_EXTENSIONS), FileRequired()])
