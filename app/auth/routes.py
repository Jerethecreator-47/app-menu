from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app.auth.forms import LoginForm
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        endpoint = "platform.dashboard" if current_user.is_platform_admin else "admin.dashboard"
        return redirect(url_for(endpoint))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.is_active and user.check_password(form.password.data):
            login_user(user)
            destination = request.args.get("next")
            if destination and destination.startswith("/"):
                return redirect(destination)
            endpoint = "platform.dashboard" if user.is_platform_admin else "admin.dashboard"
            return redirect(url_for(endpoint))
        flash("Correo o contraseña inválidos.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.post("/logout")
def logout():
    logout_user()
    flash("La sesión se cerró correctamente.", "success")
    return redirect(url_for("auth.login"))
