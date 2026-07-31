from decimal import Decimal
from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.admin.forms import CategoryForm, ProductForm
from app.extensions import db
from app.models import AuditLog, Category, Product
admin_bp = Blueprint("admin", __name__)


def restaurant_access(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user.is_platform_admin or current_user.tenant_id is None:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def catalog_manager_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not (current_user.has_role("restaurant_admin") or current_user.has_role("manager")):
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@admin_bp.get("/")
@login_required
@restaurant_access
def dashboard():
    return render_template("admin/dashboard.html", tenant=current_user.tenant, category_count=Category.query.filter_by(tenant_id=current_user.tenant_id).count(), product_count=Product.query.filter_by(tenant_id=current_user.tenant_id).count())


@admin_bp.get("/catalog")
@login_required
@restaurant_access
@catalog_manager_required
def catalog():
    tenant_id = current_user.tenant_id
    return render_template("admin/catalog.html", categories=Category.query.filter_by(tenant_id=tenant_id).order_by(Category.position, Category.name).all(), products=Product.query.filter_by(tenant_id=tenant_id).order_by(Product.name).all())


@admin_bp.route("/catalog/categories/new", methods=["GET", "POST"])
@login_required
@restaurant_access
@catalog_manager_required
def create_category():
    form = CategoryForm(current_user.tenant_id)
    if form.validate_on_submit():
        category = Category(tenant_id=current_user.tenant_id, name=form.name.data.strip())
        db.session.add(category)
        db.session.flush()
        db.session.add(AuditLog(tenant_id=current_user.tenant_id, actor_id=current_user.id, action="category.created", resource_type="category", resource_id=str(category.id)))
        db.session.commit()
        flash("La categoría fue creada.", "success")
        return redirect(url_for("admin.catalog"))
    return render_template("admin/category_form.html", form=form)


@admin_bp.route("/catalog/categories/<int:category_id>/edit", methods=["GET", "POST"])
@login_required
@restaurant_access
@catalog_manager_required
def edit_category(category_id):
    category = Category.query.filter_by(id=category_id, tenant_id=current_user.tenant_id).first_or_404()
    form = CategoryForm(current_user.tenant_id, category_id=category.id, obj=category)
    form.submit.label.text = "Guardar cambios"
    if form.validate_on_submit():
        category.name = form.name.data.strip()
        category.position = form.position.data or 0
        category.is_active = form.is_active.data
        db.session.add(AuditLog(tenant_id=current_user.tenant_id, actor_id=current_user.id, action="category.updated", resource_type="category", resource_id=str(category.id)))
        db.session.commit()
        flash("La categoría fue actualizada.", "success")
        return redirect(url_for("admin.catalog"))
    return render_template("admin/category_form.html", form=form, category=category)


@admin_bp.post("/catalog/categories/<int:category_id>/delete")
@login_required
@restaurant_access
@catalog_manager_required
def delete_category(category_id):
    category = Category.query.filter_by(id=category_id, tenant_id=current_user.tenant_id).first_or_404()
    if category.products:
        flash("No se puede eliminar una categoría con productos. Movelos o borralos primero, o desactivá la categoría.", "danger")
        return redirect(url_for("admin.catalog"))
    db.session.add(AuditLog(tenant_id=current_user.tenant_id, actor_id=current_user.id, action="category.deleted", resource_type="category", resource_id=str(category.id)))
    db.session.delete(category)
    db.session.commit()
    flash("La categoría fue eliminada.", "success")
    return redirect(url_for("admin.catalog"))


@admin_bp.route("/catalog/products/new", methods=["GET", "POST"])
@login_required
@restaurant_access
@catalog_manager_required
def create_product():
    form = ProductForm(current_user.tenant_id)
    if form.validate_on_submit():
        product = Product(tenant_id=current_user.tenant_id, category_id=form.category_id.data, name=form.name.data.strip(), description=form.description.data.strip(), price_cents=int(form.price.data * 100), image_url=form.image_url.data or None, is_available=form.is_available.data, is_featured=form.is_featured.data, is_vegetarian=form.is_vegetarian.data, is_vegan=form.is_vegan.data, is_gluten_free=form.is_gluten_free.data)
        db.session.add(product)
        db.session.flush()
        db.session.add(AuditLog(tenant_id=current_user.tenant_id, actor_id=current_user.id, action="product.created", resource_type="product", resource_id=str(product.id)))
        db.session.commit()
        flash("El producto fue creado.", "success")
        return redirect(url_for("admin.catalog"))
    return render_template("admin/product_form.html", form=form)


@admin_bp.route("/catalog/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
@restaurant_access
@catalog_manager_required
def edit_product(product_id):
    product = Product.query.filter_by(id=product_id, tenant_id=current_user.tenant_id).first_or_404()
    form = ProductForm(current_user.tenant_id, product_id=product.id, current_category_id=product.category_id, obj=product, price=Decimal(product.price_cents) / 100)
    form.submit.label.text = "Guardar cambios"
    if form.validate_on_submit():
        product.category_id = form.category_id.data
        product.name = form.name.data.strip()
        product.description = form.description.data.strip()
        product.price_cents = int(form.price.data * 100)
        product.image_url = form.image_url.data or None
        product.is_available = form.is_available.data
        product.is_featured = form.is_featured.data
        product.is_vegetarian = form.is_vegetarian.data
        product.is_vegan = form.is_vegan.data
        product.is_gluten_free = form.is_gluten_free.data
        db.session.add(AuditLog(tenant_id=current_user.tenant_id, actor_id=current_user.id, action="product.updated", resource_type="product", resource_id=str(product.id)))
        db.session.commit()
        flash("El producto fue actualizado.", "success")
        return redirect(url_for("admin.catalog"))
    return render_template("admin/product_form.html", form=form, product=product)


@admin_bp.post("/catalog/products/<int:product_id>/delete")
@login_required
@restaurant_access
@catalog_manager_required
def delete_product(product_id):
    product = Product.query.filter_by(id=product_id, tenant_id=current_user.tenant_id).first_or_404()
    db.session.add(AuditLog(tenant_id=current_user.tenant_id, actor_id=current_user.id, action="product.deleted", resource_type="product", resource_id=str(product.id)))
    db.session.delete(product)
    db.session.commit()
    flash("El producto fue eliminado.", "success")
    return redirect(url_for("admin.catalog"))
