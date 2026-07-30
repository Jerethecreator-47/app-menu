from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db

DEFAULT_ROLES = {
    "platform_admin": "Administrador general",
    "restaurant_admin": "Administrador del restaurante",
    "manager": "Gerente",
    "waiter": "Mozo",
    "cashier": "Cajero",
    "cook": "Cocinero",
}

user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.ForeignKey("users.id"), primary_key=True),
    db.Column("role_id", db.ForeignKey("roles.id"), primary_key=True),
)


class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class Tenant(TimestampMixin, db.Model):
    __tablename__ = "tenants"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    timezone = db.Column(db.String(64), nullable=False, default="America/Argentina/Buenos_Aires")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    users = db.relationship("User", back_populates="tenant", lazy="select")
    categories = db.relationship("Category", back_populates="tenant", lazy="select", cascade="all, delete-orphan")
    products = db.relationship("Product", back_populates="tenant", lazy="select", cascade="all, delete-orphan")


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(40), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)


class Category(TimestampMixin, db.Model):
    __tablename__ = "categories"
    __table_args__ = (db.UniqueConstraint("tenant_id", "name", name="uq_categories_tenant_name"),)
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    name = db.Column(db.String(80), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    tenant = db.relationship("Tenant", back_populates="categories")
    products = db.relationship("Product", back_populates="category", lazy="select")


class Product(TimestampMixin, db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    price_cents = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    is_available = db.Column(db.Boolean, nullable=False, default=True)
    is_featured = db.Column(db.Boolean, nullable=False, default=False)
    is_vegetarian = db.Column(db.Boolean, nullable=False, default=False)
    is_vegan = db.Column(db.Boolean, nullable=False, default=False)
    is_gluten_free = db.Column(db.Boolean, nullable=False, default=False)
    tenant = db.relationship("Tenant", back_populates="products")
    category = db.relationship("Category", back_populates="products")

    @property
    def price_display(self):
        return f"${self.price_cents / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class User(TimestampMixin, UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=True, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_platform_admin = db.Column(db.Boolean, nullable=False, default=False)
    tenant = db.relationship("Tenant", back_populates="users")
    roles = db.relationship("Role", secondary=user_roles, lazy="selectin")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, code):
        return self.is_platform_admin or any(role.code == code for role in self.roles)


class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    # SQLite requiere INTEGER para que una clave primaria se autoincremente.
    # PostgreSQL conserva el comportamiento de secuencia al migrar este campo.
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=True, index=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(100), nullable=False)
    resource_id = db.Column(db.String(64), nullable=True)
    occurred_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


def ensure_default_roles():
    """Crea los roles base si aún no existen y devuelve un diccionario por código."""
    roles = {role.code: role for role in Role.query.all()}
    for code, name in DEFAULT_ROLES.items():
        if code not in roles:
            roles[code] = Role(code=code, name=name)
            db.session.add(roles[code])
    return roles
