"""initial migration — create all tables

Revision ID: 001_initial
Revises:
Create Date: 2026-05-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lectures",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("number", sa.Integer(), unique=True, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("block", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("topics", sa.Text(), nullable=True),
        sa.Column("real_code_link", sa.String(500), nullable=True),
        sa.Column("assignment_type", sa.String(1), nullable=False),
        sa.Column("assignment_description", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("is_published", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("lecture_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "students",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("github_username", sa.String(100), unique=True, nullable=False),
        sa.Column("role", sa.String(20), server_default=sa.text("'student'")),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("cohort_year", sa.Integer(), server_default=sa.text("2026")),
        sa.Column("entry_slice_score", sa.Float(), nullable=True),
        sa.Column("exit_slice_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "slices",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("slice_type", sa.String(10), nullable=False),
        sa.Column("task1_answer", sa.Text(), nullable=True),
        sa.Column("task2_code", sa.Text(), nullable=True),
        sa.Column("task3_answer", sa.Text(), nullable=True),
        sa.Column("ai_level", sa.Float(), nullable=True),
        sa.Column("teacher_level", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "assignments",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("lecture_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("lectures.id"), nullable=False),
        sa.Column("student_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("github_pr_url", sa.String(500), nullable=True),
        sa.Column("branch_name", sa.String(255), nullable=True),
        sa.Column("status", sa.String(20), server_default=sa.text("'open'")),
        sa.Column("pr_description", sa.Text(), nullable=True),
        sa.Column("code_diff", sa.Text(), nullable=True),
        sa.Column("iteration_count", sa.Integer(), server_default=sa.text("0")),
        sa.Column("ai_level", sa.Float(), nullable=True),
        sa.Column("teacher_level", sa.Float(), nullable=True),
        sa.Column("ai_comment", sa.Text(), nullable=True),
        sa.Column("teacher_comment", sa.Text(), nullable=True),
        sa.Column("needs_teacher", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("merged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "ai_reviews",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("assignment_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("assignments.id"), nullable=False),
        sa.Column("triggered_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("runs_without_errors", sa.Boolean(), nullable=True),
        sa.Column("tests_passed", sa.String(50), nullable=True),
        sa.Column("style_comments", sa.Text(), nullable=True),
        sa.Column("logic_comments", sa.Text(), nullable=True),
        sa.Column("clarifying_question", sa.Text(), nullable=True),
        sa.Column("predicted_level", sa.Float(), nullable=True),
        sa.Column("raw_response", sa.Text(), nullable=True),
        sa.Column("error_occurred", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("ai_reviews")
    op.drop_table("assignments")
    op.drop_table("slices")
    op.drop_table("students")
    op.drop_table("lectures")
