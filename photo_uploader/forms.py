from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class UploadForm(FlaskForm):
    files = MultipleFileField("Wählen Sie Fotos aus", validators=[DataRequired()])
    submit = SubmitField("Hochladen")

class LoginForm(FlaskForm):
    username = StringField("Benutzername", validators=[DataRequired()])
    password = PasswordField("Passwort", validators=[DataRequired()])
    submit = SubmitField("Anmelden")