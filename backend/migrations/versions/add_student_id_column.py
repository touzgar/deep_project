"""add student_id column

Revision ID: add_student_id
Revises: 9700093a0f9f
Create Date: 2026-04-28

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_student_id'
down_revision = '9700093a0f9f'
branch_labels = None
depends_on = None


def upgrade():
    # Add student_id column
    op.add_column('students', sa.Column('student_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_students_student_id'), 'students', ['student_id'], unique=True)


def downgrade():
    # Remove student_id column
    op.drop_index(op.f('ix_students_student_id'), table_name='students')
    op.drop_column('students', 'student_id')
