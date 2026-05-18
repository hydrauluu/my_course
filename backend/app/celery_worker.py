import asyncio
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.celery_app import celery_app
from app.database import async_session
from app.models.assignment import Assignment
from app.models.lecture import Lecture
from app.models.ai_review import AIReview
from app.services.ai_review import run_ai_review, parse_review_response

logger = logging.getLogger(__name__)


@celery_app.task(name="run_ai_review")
def run_ai_review_task(assignment_id: str):
    asyncio.run(_process_review(assignment_id))


async def _process_review(assignment_id: str):
    logger.info("Starting AI review for assignment %s", assignment_id)
    async with async_session() as db:
        result = await db.execute(
            select(Assignment).where(Assignment.id == uuid.UUID(assignment_id))
        )
        assignment = result.scalar_one_or_none()
        if not assignment:
            logger.error("Assignment %s not found", assignment_id)
            return

        lecture_result = await db.execute(
            select(Lecture).where(Lecture.id == assignment.lecture_id)
        )
        lecture = lecture_result.scalar_one_or_none()
        if not lecture:
            logger.error("Lecture not found for assignment %s", assignment_id)
            return

        lecture_context = f"Лекция {lecture.number}: {lecture.title}. {lecture.description or ''}"

        try:
            review_text = await run_ai_review(
                assignment_type=lecture.assignment_type,
                code_diff=assignment.code_diff,
                pr_description=assignment.pr_description,
                lecture_context=lecture_context,
            )

            parsed = parse_review_response(review_text, lecture.assignment_type)

            review = AIReview(
                assignment_id=assignment.id,
                runs_without_errors=parsed["runs_without_errors"],
                tests_passed=parsed["tests_passed"],
                style_comments=parsed["style_comments"],
                logic_comments=parsed["logic_comments"],
                clarifying_question=parsed["clarifying_question"],
                predicted_level=parsed["predicted_level"],
                raw_response=parsed["raw_response"],
                error_occurred=False,
            )

            assignment.ai_level = parsed["predicted_level"]
            assignment.ai_comment = parsed["logic_comments"]
            assignment.needs_teacher = False
            logger.info("AI review completed for assignment %s: level=%s", assignment_id, parsed["predicted_level"])

        except Exception as e:
            logger.error("AI review failed for assignment %s: %s", assignment_id, e)
            review = AIReview(
                assignment_id=assignment.id,
                error_occurred=True,
                raw_response=f"Error: {str(e)}",
            )
            assignment.needs_teacher = True

        db.add(review)
        await db.commit()
