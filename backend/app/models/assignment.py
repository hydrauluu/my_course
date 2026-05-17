import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Float, DateTime, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lecture_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lectures.id"), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    github_pr_url: Mapped[str] = mapped_column(String(500), nullable=True)
    branch_name: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open")
    pr_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    iteration_count: Mapped[int] = mapped_column(Integer, default=0)
    ai_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    teacher_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    teacher_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    needs_teacher: Mapped[bool] = mapped_column(default=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    merged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="assignments")
    lecture = relationship("Lecture")
    reviews = relationship("AIReview", back_populates="assignment")
