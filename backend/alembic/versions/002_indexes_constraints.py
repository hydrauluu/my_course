"""add indexes and check constraints

Revision ID: 002_indexes_constraints
Revises: 001_initial
Create Date: 2026-05-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_indexes_constraints"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_assignments_student_id", "assignments", ["student_id"])
    op.create_index("ix_assignments_lecture_id", "assignments", ["lecture_id"])
    op.create_index("ix_assignments_github_pr_url", "assignments", ["github_pr_url"])
    op.create_index("ix_assignments_status", "assignments", ["status"])
    op.create_index("ix_ai_reviews_assignment_id", "ai_reviews", ["assignment_id"])
    op.create_index("ix_slices_student_id", "slices", ["student_id"])

    op.create_unique_constraint(
        "uq_assignments_student_lecture",
        "assignments",
        ["student_id", "lecture_id"],
    )

    op.create_check_constraint(
        "ck_lectures_assignment_type",
        "lectures",
        "assignment_type IN ('A', 'B', 'C')",
    )

    op.create_check_constraint(
        "ck_assignments_status",
        "assignments",
        "status IN ('open', 'merged', 'rejected', 'needs_work', 'pending')",
    )

    op.create_check_constraint(
        "ck_students_role",
        "students",
        "role IN ('student', 'teacher', 'admin')",
    )

    op.create_check_constraint(
        "ck_slices_slice_type",
        "slices",
        "slice_type IN ('entry', 'exit')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_slices_slice_type", "slices", type_="check")
    op.drop_constraint("ck_students_role", "students", type_="check")
    op.drop_constraint("ck_assignments_status", "assignments", type_="check")
    op.drop_constraint("ck_lectures_assignment_type", "lectures", type_="check")
    op.drop_constraint("uq_assignments_student_lecture", "assignments", type_="unique")
    op.drop_index("ix_slices_student_id", table_name="slices")
    op.drop_index("ix_ai_reviews_assignment_id", table_name="ai_reviews")
    op.drop_index("ix_assignments_status", table_name="assignments")
    op.drop_index("ix_assignments_github_pr_url", table_name="assignments")
    op.drop_index("ix_assignments_lecture_id", table_name="assignments")
    op.drop_index("ix_assignments_student_id", table_name="assignments")
