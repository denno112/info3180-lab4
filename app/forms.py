from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import InputRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class UploadForm(FlaskForm):
    upload = FileField(validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])