import uuid
from datetime import datetime

from sqlalchemy import String, Float, DateTime, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Slice(Base):
    __tablename__ = "slices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    slice_type: Mapped[str] = mapped_column(String(10), nullable=False)
    task1_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    task2_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    task3_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    teacher_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="slices")
