"""agrega constraint unico de nombre de producto por tenant

Revision ID: 959e80381082
Revises: 4833a4440558
Create Date: 2026-07-31 20:39:10.146485

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '959e80381082'
down_revision = '4833a4440558'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_products_tenant_name', ['tenant_id', 'name'])


def downgrade():
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_constraint('uq_products_tenant_name', type_='unique')
