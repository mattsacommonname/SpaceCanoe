from flask_wtf import FlaskForm
from wtforms import FileField, PasswordField, StringField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    name = StringField('User name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class OpmlUploadForm(FlaskForm):
    opml = FileField('OPML File', validators=[DataRequired()])
