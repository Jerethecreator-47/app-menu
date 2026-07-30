from flask import Blueprint, render_template

from app.models import Category, Product, Tenant

menu_bp = Blueprint("menu", __name__)


@menu_bp.get("/<tenant_slug>")
def public_menu(tenant_slug):
    tenant = Tenant.query.filter_by(slug=tenant_slug, is_active=True).first_or_404()
    categories = Category.query.filter_by(tenant_id=tenant.id, is_active=True).order_by(Category.position, Category.name).all()
    products = Product.query.filter_by(tenant_id=tenant.id, is_available=True).order_by(Product.is_featured.desc(), Product.name).all()
    return render_template("menu/public_menu.html", tenant=tenant, categories=categories, products=products)
