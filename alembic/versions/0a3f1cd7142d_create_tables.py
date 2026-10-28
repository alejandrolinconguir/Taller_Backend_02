"""create tables

Revision ID: 0a3f1cd7142d
Revises: 
Create Date: 2026-10-28 17:40:09.286854

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a3f1cd7142d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crear primero students, porque pets depende de esta tabla
    op.create_table(
        "students",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("username", sa.String(length=30), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("createdAt", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_students_username", "students", ["username"], unique=True)
    op.create_index("ix_students_email", "students", ["email"], unique=True)

    # Crear pets despues de students por la clave foranea.
    op.create_table(
        "pets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("studentId", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("species", sa.String(length=50), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("createdAt", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["studentId"], ["students.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "studentId", "name", name="uq_pets_studentId_name"
        ),
    )

    op.create_index("ix_pets_studentId", "pets", ["studentId"], unique=False)
    pass


def downgrade() -> None:
     # Revertir en orden inverso por la clave foránea.
    op.drop_index("ix_pets_studentId", table_name="pets")
    op.drop_table("pets")

    op.drop_index("ix_students_email", table_name="students")
    op.drop_index("ix_students_username", table_name="students")
    op.drop_table("students")
    pass
