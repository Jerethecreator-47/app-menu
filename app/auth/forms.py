from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField("Correo electrónico", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Ingresar")