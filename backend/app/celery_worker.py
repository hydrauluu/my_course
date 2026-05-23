import logging
import uuid

from sqlalchemy import select

from app.services.celery_app import celery_app
from app.config import settings
from app.database import SyncSession
from app.models.assignment import Assignment
from app.models.lecture import Lecture
from app.models.ai_review import AIReview
from app.services.ai_review import REVIEW_SYSTEM_PROMPT, parse_review_response

logger = logging.getLogger(__name__)


def _run_ai_review_sync(assignment_type: str, code_diff: str | None, pr_description: str | None, lecture_context: str) -> str:
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured — cannot run AI review")

    try:
        from google import genai

        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        user_content = f"Контекст лекции: {lecture_context}\n\n"
        if assignment_type == "A" and code_diff:
            user_content += f"Код из PR (diff):\n{code_diff}\n\n"
        elif assignment_type == "B" and pr_description:
            user_content += f"PR description (объяснение студента):\n{pr_description}\n\n"
        elif assignment_type == "AB":
            if code_diff:
                user_content += f"Код из PR (diff):\n{code_diff}\n\n"
            if pr_description:
                user_content += f"PR description (объяснение студента):\n{pr_description}\n\n"

        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=user_content,
            config=genai.types.GenerateContentConfig(
                system_instruction=REVIEW_SYSTEM_PROMPT,
                max_output_tokens=2000,
            ),
        )
        return response.text
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")


@celery_app.task(name="run_ai_review", bind=True, max_retries=3, default_retry_delay=60)
def run_ai_review_task(self, assignment_id: str):
    logger.info("Starting AI review for assignment %s", assignment_id)

    try:
        with SyncSession() as db:
            result = db.execute(
                select(Assignment).where(Assignment.id == uuid.UUID(assignment_id))
            )
            assignment = result.scalar_one_or_none()
            if not assignment:
                logger.error("Assignment %s not found", assignment_id)
                return

            lecture_result = db.execute(
                select(Lecture).where(Lecture.id == assignment.lecture_id)
            )
            lecture = lecture_result.scalar_one_or_none()
            if not lecture:
                logger.error("Lecture not found for assignment %s", assignment_id)
                return

            lecture_context = f"Лекция {lecture.number}: {lecture.title}. {lecture.description or ''}"

            review_text = _run_ai_review_sync(
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

            db.add(review)
            db.commit()

    except Exception as e:
        logger.error("AI review failed for assignment %s: %s", assignment_id, e)
        try:
            with SyncSession() as db:
                result = db.execute(
                    select(Assignment).where(Assignment.id == uuid.UUID(assignment_id))
                )
                assignment = result.scalar_one_or_none()
                if assignment:
                    review = AIReview(
                        assignment_id=assignment.id,
                        error_occurred=True,
                        raw_response=f"Error: {str(e)}",
                    )
                    assignment.needs_teacher = True
                    db.add(review)
                    db.commit()
        except Exception as db_error:
            logger.error("Failed to save error review for assignment %s: %s", assignment_id, db_error)
        self.retry(exc=e)
