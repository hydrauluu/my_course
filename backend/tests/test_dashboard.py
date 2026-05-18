import pytest


class TestDashboard:
    @pytest.mark.asyncio
    async def test_dashboard_unauthorized(self, client):
        response = await client.get("/api/dashboard/student")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_dashboard_empty(self, client, auth_headers, db_session):
        from app.models.lecture import Lecture
        db_session.add_all([
            Lecture(number=i, title=f"Lecture {i}", block=1, assignment_type="A", is_published=True)
            for i in range(3)
        ])
        await db_session.commit()

        response = await client.get("/api/dashboard/student", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_lectures"] == 3
        assert data["completed_lectures"] == 0
        assert data["progress_percentage"] == 0
        assert len(data["assignments"]) == 0

    @pytest.mark.asyncio
    async def test_dashboard_with_assignments(
        self, client, auth_headers, db_session, seeded_lecture, student_id
    ):
        from app.models.assignment import Assignment
        from app.models.ai_review import AIReview

        assignment = Assignment(
            lecture_id=seeded_lecture.id,
            student_id=student_id,
            status="merged",
            iteration_count=2,
            ai_level=2.0,
        )
        db_session.add(assignment)
        await db_session.flush()

        review = AIReview(
            assignment_id=assignment.id,
            predicted_level=2.0,
            style_comments="Good style",
            clarifying_question="Why this approach?",
        )
        db_session.add(review)
        await db_session.commit()

        response = await client.get("/api/dashboard/student", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["completed_lectures"] == 1
        assert data["assignments"][0]["status"] == "merged"
        assert data["assignments"][0]["ai_level"] == 2.0
        assert data["latest_review"] is not None
        assert data["latest_review"]["predicted_level"] == 2.0

    @pytest.mark.asyncio
    async def test_dashboard_progress_chart(self, client, auth_headers, db_session):
        from app.models.lecture import Lecture
        for i in range(5):
            db_session.add(
                Lecture(number=i, title=f"Lecture {i}", block=1, assignment_type="A", is_published=True)
            )
        await db_session.commit()

        response = await client.get("/api/dashboard/student", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["progress_chart"]) == 5
        assert all("lecture_number" in p for p in data["progress_chart"])
        assert all("ai_level" in p for p in data["progress_chart"])
