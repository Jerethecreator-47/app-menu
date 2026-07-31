from decimal import Decimal

from flask_wtf import FlaskForm
from wtforms import BooleanField, DecimalField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, URL, ValidationError

from app.models import Category, Product


class CategoryForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(max=80)])
    position = IntegerField("Posición", validators=[Optional(), NumberRange(min=0)], default=0)
    is_active = BooleanField("Visible en el menú", default=True)
    submit = SubmitField("Crear categoría")

    def __init__(self, tenant_id, *args, category_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant_id = tenant_id
        self.category_id = category_id

    def validate_name(self, field):
        query = Category.query.filter_by(tenant_id=self.tenant_id, name=field.data.strip())
        if self.category_id:
            query = query.filter(Category.id != self.category_id)
        if query.first():
            raise ValidationError("Ya existe una categoría con ese nombre.")


class ProductForm(FlaskForm):
    category_id = SelectField("Categoría", coerce=int, validators=[DataRequired()])
    name = StringField("Nombre", validators=[DataRequired(), Length(max=120)])
    description = TextAreaField("Descripción", validators=[Optional(), Length(max=1000)])
    price = DecimalField("Precio", places=2, validators=[DataRequired(), NumberRange(min=Decimal("0"))])
    image_url = StringField("URL de imagen", validators=[Optional(), URL(), Length(max=500)])
    is_available = BooleanField("Disponible", default=True)
    is_featured = BooleanField("Destacar en el menú")
    is_vegetarian = BooleanField("Vegetariano")
    is_vegan = BooleanField("Vegano")
    is_gluten_free = BooleanField("Sin TACC")
    submit = SubmitField("Crear producto")

    def __init__(self, tenant_id, *args, product_id=None, current_category_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant_id = tenant_id
        self.product_id = product_id
        categories = list(Category.query.filter_by(tenant_id=tenant_id, is_active=True).order_by(Category.position, Category.name))
        if current_category_id and current_category_id not in [c.id for c in categories]:
            current = Category.query.filter_by(id=current_category_id, tenant_id=tenant_id).first()
            if current:
                categories.append(current)
        self.category_id.choices = [(item.id, item.name) for item in categories]

    def validate_category_id(self, field):
        if not Category.query.filter_by(id=field.data, tenant_id=self.tenant_id).first():
            raise ValidationError("Elegí una categoría válida.")

    def validate_name(self, field):
        query = Product.query.filter_by(tenant_id=self.tenant_id, name=field.data.strip())
        if self.product_id:
            query = query.filter(Product.id != self.product_id)
        if query.first():
            raise ValidationError("Ya existe un producto con ese nombre.")
