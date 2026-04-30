"""add teacher to class

Revision ID: add_teacher_to_class
Revises: add_uploadthing_key
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_teacher_to_class'
down_revision = 'add_uploadthing_key'
branch_labels = None
depends_on = None


def upgrade():
    # Add teacher_id column to classes table
    op.add_column('classes', sa.Column('teacher_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_classes_teacher_id', 'classes', 'users', ['teacher_id'], ['id'], ondelete='SET NULL')


def downgrade():
    # Remove teacher_id column from classes table
    op.drop_constraint('fk_classes_teacher_id', 'classes', type_='foreignkey')
    op.drop_column('classes', 'teacher_id')
