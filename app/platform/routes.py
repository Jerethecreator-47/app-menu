from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import AuditLog, Tenant, User, ensure_default_roles
from app.platform.forms import CreateBusinessForm

platform_bp = Blueprint("platform", __name__)


def platform_admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_platform_admin:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@platform_bp.get("/")
@login_required
@platform_admin_required
def dashboard():
    return render_template(
        "platform/dashboard.html",
        tenant_count=Tenant.query.count(),
        user_count=User.query.count(),
        tenants=Tenant.query.order_by(Tenant.created_at.desc()).all(),
    )


@platform_bp.route("/businesses/new", methods=["GET", "POST"])
@login_required
@platform_admin_required
def create_business():
    form = CreateBusinessForm()
    if form.validate_on_submit():
        roles = ensure_default_roles()
        tenant = Tenant(name=form.business_name.data.strip(), slug=form.slug.data)
        admin = User(
            tenant=tenant,
            email=form.admin_email.data,
            full_name=form.admin_name.data.strip(),
        )
        admin.set_password(form.password.data)
        admin.roles.append(roles["restaurant_admin"])
        db.session.add_all([tenant, admin])
        db.session.flush()
        db.session.add(AuditLog(
            tenant_id=tenant.id,
            actor_id=current_user.id,
            action="business.created",
            resource_type="tenant",
            resource_id=str(tenant.id),
        ))
        db.session.commit()
        flash("El negocio y su administrador fueron creados.", "success")
        return redirect(url_for("platform.dashboard"))
    return render_template("platform/create_business.html", form=form)
