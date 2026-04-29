"""add uploadthing_key to face_images

Revision ID: add_uploadthing_key
Revises: add_student_id
Create Date: 2026-04-28

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_uploadthing_key'
down_revision = 'add_student_id'
branch_labels = None
depends_on = None


def upgrade():
    # Add uploadthing_key column to face_images table
    op.add_column('face_images', sa.Column('uploadthing_key', sa.String(), nullable=True))


def downgrade():
    # Remove uploadthing_key column
    op.drop_column('face_images', 'uploadthing_key')