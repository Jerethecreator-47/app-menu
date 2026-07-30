from flask import Flask

from config import Config
from app.extensions import csrf, db, jwt, login_manager, migrate
from app.models import User, ensure_default_roles


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    jwt.init_app(app)
    login_manager.init_app(app)

    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.platform.routes import platform_bp
    from app.menu.routes import menu_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(platform_bp, url_prefix="/platform")
    app.register_blueprint(menu_bp, url_prefix="/r")

    @app.cli.command("seed-superadmin")
    def seed_superadmin():
        """Crea el rol y usuario administrador general inicial."""
        from getpass import getpass
        roles = ensure_default_roles()
        email = input("Correo del administrador: ").strip().lower()
        if User.query.filter_by(email=email).first():
            raise RuntimeError("Ya existe un usuario con ese correo.")
        user = User(email=email, full_name=input("Nombre completo: ").strip(), is_platform_admin=True)
        user.set_password(getpass("Contraseña: "))
        user.roles.append(roles["platform_admin"])
        db.session.add(user)
        db.session.commit()

    @app.cli.command("seed-roles")
    def seed_roles():
        """Crea los roles base del sistema."""
        ensure_default_roles()
        db.session.commit()

    return app


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
