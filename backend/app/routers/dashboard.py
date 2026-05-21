from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.lecture import Lecture
from app.models.assignment import Assignment
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/student")
async def student_dashboard(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    lectures_result = await db.execute(
        select(Lecture).where(Lecture.is_published == True).order_by(Lecture.number)
    )
    lectures = {l.id: l for l in lectures_result.scalars().all()}

    assignments_result = await db.execute(
        select(Assignment)
        .where(Assignment.student_id == current_user["student_id"])
        .options(selectinload(Assignment.reviews))
        .order_by(Assignment.created_at.desc())
    )
    assignments = assignments_result.scalars().all()

    total = len(lectures)
    completed = sum(1 for a in assignments if a.status == "merged")
    needs_review = sum(1 for a in assignments if a.needs_teacher)
    avg_iterations = (
        round(sum(a.iteration_count for a in assignments) / len(assignments), 1)
        if assignments else 0
    )

    latest_review = None
    if assignments:
        last_assign = assignments[0]
        lecture = lectures.get(last_assign.lecture_id)
        if last_assign.reviews:
            latest = last_assign.reviews[-1]
            latest_review = {
                "assignment_id": str(last_assign.id),
                "lecture_number": lecture.number if lecture else None,
                "lecture_title": lecture.title if lecture else None,
                "predicted_level": latest.predicted_level,
                "style_comments": latest.style_comments,
                "clarifying_question": latest.clarifying_question,
                "triggered_at": latest.triggered_at.isoformat() if latest.triggered_at else None,
            }

    progress_chart = []
    for lid, lecture in sorted(lectures.items(), key=lambda x: x[1].number):
        assign = next((a for a in assignments if a.lecture_id == lid), None)
        level = assign.ai_level if assign else None
        progress_chart.append({
            "lecture_number": lecture.number,
            "lecture_title": lecture.title,
            "ai_level": level,
            "status": assign.status if assign else "pending",
            "iteration_count": assign.iteration_count if assign else 0,
        })

    assignments_data = []
    for a in assignments:
        lecture = lectures.get(a.lecture_id)
        assignments_data.append({
            "id": str(a.id),
            "lecture_number": lecture.number if lecture else None,
            "lecture_title": lecture.title if lecture else None,
            "status": a.status,
            "iteration_count": a.iteration_count,
            "ai_level": a.ai_level,
            "teacher_level": a.teacher_level,
            "submitted_at": a.submitted_at.isoformat() if a.submitted_at else None,
            "needs_teacher": a.needs_teacher,
        })

    return {
        "total_lectures": total,
        "completed_lectures": completed,
        "progress_percentage": round(completed / total * 100) if total > 0 else 0,
        "needs_review": needs_review,
        "avg_iterations": avg_iterations,
        "progress_chart": progress_chart,
        "assignments": assignments_data,
        "latest_review": latest_review,
    }
