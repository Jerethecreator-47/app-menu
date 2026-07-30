import re

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, ValidationError

from app.models import Tenant, User


class CreateBusinessForm(FlaskForm):
    business_name = StringField("Nombre del negocio", validators=[DataRequired(), Length(max=120)])
    slug = StringField(
        "Identificador",
        validators=[DataRequired(), Length(min=3, max=80), Regexp(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", message="Usá minúsculas, números y guiones.")],
    )
    admin_name = StringField("Nombre del administrador", validators=[DataRequired(), Length(max=120)])
    admin_email = StringField("Correo del administrador", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Contraseña temporal", validators=[DataRequired(), Length(min=12, max=128)])
    submit = SubmitField("Crear negocio y administrador")

    def validate_slug(self, field):
        field.data = field.data.strip().lower()
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", field.data):
            raise ValidationError("Usá minúsculas, números y guiones.")
        if Tenant.query.filter_by(slug=field.data).first():
            raise ValidationError("Ese identificador ya está en uso.")

    def validate_admin_email(self, field):
        field.data = field.data.strip().lower()
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Ya existe un usuario con ese correo.")
