"""add assignment_type AB

Revision ID: 003_add_assignment_type_ab
Revises: 002_indexes_constraints
Create Date: 2026-05-21
"""
from typing import Sequence, Union

from alembic import op


revision: str = "003_add_assignment_type_ab"
down_revision: Union[str, None] = "002_indexes_constraints"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE lectures ALTER COLUMN assignment_type TYPE VARCHAR(2)")
    op.execute(
        "ALTER TABLE lectures ADD CONSTRAINT ck_lectures_assignment_type "
        "CHECK (assignment_type IN ('A', 'B', 'C', 'AB'))"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE lectures DROP CONSTRAINT ck_lectures_assignment_type")
    op.execute("ALTER TABLE lectures ALTER COLUMN assignment_type TYPE VARCHAR(1)")
    op.execute(
        "ALTER TABLE lectures ADD CONSTRAINT ck_lectures_assignment_type "
        "CHECK (assignment_type IN ('A', 'B', 'C'))"
    )
