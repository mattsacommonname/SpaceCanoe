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
