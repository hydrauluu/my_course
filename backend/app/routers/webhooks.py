import re
import hmac
import hashlib
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, get_db
from app.config import settings
from app.rate_limiter import limiter
from app.models.student import Student
from app.models.lecture import Lecture
from app.models.assignment import Assignment
from app.services.celery_app import celery_app
from app.services.github import get_pr_diff

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

BRANCH_PATTERN = re.compile(r"^hw(\d{2})/(.+)$")
PR_URL_PATTERN = re.compile(r"https://github\.com/([^/]+/[^/]+)/pull/(\d+)")


async def verify_webhook(request: Request):
    if not settings.GITHUB_WEBHOOK_SECRET:
        return

    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")

    expected = hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(f"sha256={expected}", signature):
        raise HTTPException(status_code=400, detail="Invalid signature")


async def _fetch_pr_diff(pr_url: str) -> str | None:
    if not settings.GITHUB_BOT_TOKEN:
        logger.warning("GITHUB_BOT_TOKEN not set, cannot fetch PR diff")
        return None
    match = PR_URL_PATTERN.match(pr_url)
    if not match:
        logger.warning("Invalid PR URL format: %s", pr_url)
        return None
    repo_full_name = match.group(1)
    pr_number = int(match.group(2))
    try:
        return await get_pr_diff(repo_full_name, pr_number, settings.GITHUB_BOT_TOKEN)
    except Exception as e:
        logger.error("Failed to fetch PR diff: %s", e)
        return None


@router.post("/github")
@limiter.limit("100/minute")
async def github_webhook(request: Request):
    await verify_webhook(request)
    payload = await request.json()
    action = payload.get("action")
    pr = payload.get("pull_request", {})

    if not pr or not action:
        return {"status": "ignored"}

    branch_name = pr.get("head", {}).get("ref", "")
    match = BRANCH_PATTERN.match(branch_name)

    if not match:
        logger.info("Ignoring webhook: invalid branch format '%s'", branch_name)
        return {"status": "ignored", "reason": "invalid branch format"}

    lecture_number = int(match.group(1))
    student_last_name = match.group(2)
    logger.info("Processing webhook: lecture=%d student=%s action=%s", lecture_number, student_last_name, action)

    pr_url = pr.get("html_url", "")
    pr_description = pr.get("body", "") or ""
    pr_state = pr.get("state", "open")
    merged = pr.get("merged", False)

    status_map = {
        "open": "open",
        "closed": "merged" if merged else "rejected",
    }
    new_status = status_map.get(pr_state, "open")

    async with async_session() as db:
        result = await db.execute(select(Lecture).where(Lecture.number == lecture_number))
        lecture = result.scalar_one_or_none()
        if not lecture:
            return {"status": "ignored", "reason": "lecture not found"}

        result = await db.execute(
            select(Assignment).where(Assignment.github_pr_url == pr_url)
        )
        assignment = result.scalar_one_or_none()

        if assignment:
            assignment.status = new_status
            assignment.pr_description = pr_description
            if action in ("opened", "synchronize", "edited"):
                diff = await _fetch_pr_diff(pr_url)
                if diff:
                    assignment.code_diff = diff
                assignment.iteration_count += 1
                celery_app.send_task("run_ai_review", args=[str(assignment.id)])
            if merged:
                assignment.merged_at = datetime.now(timezone.utc)
            await db.commit()
            logger.info("Updated assignment %s: status=%s", assignment.id, new_status)
        elif action == "opened":
            result = await db.execute(
                select(Student).where(Student.github_username == student_last_name)
            )
            student = result.scalar_one_or_none()
            if not student:
                return {"status": "ignored", "reason": "student not found"}

            diff = await _fetch_pr_diff(pr_url)
            assignment = Assignment(
                lecture_id=lecture.id,
                student_id=student.id,
                github_pr_url=pr_url,
                branch_name=branch_name,
                status="open",
                pr_description=pr_description,
                code_diff=diff,
                iteration_count=1,
            )
            db.add(assignment)
            await db.commit()
            celery_app.send_task("run_ai_review", args=[str(assignment.id)])
            logger.info("Created assignment %s for student %s", assignment.id, student_last_name)
        else:
            logger.info("No action taken: assignment exists=%s, action=%s", assignment is not None, action)

    return {"status": "ok"}
