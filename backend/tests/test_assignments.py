import pytest


class TestAssignments:
    @pytest.mark.asyncio
    async def test_list_assignments_unauthorized(self, client):
        response = await client.get("/api/assignments")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_assignments_empty(self, client, auth_headers):
        response = await client.get("/api/assignments", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_list_assignments_returns_user_only(
        self, client, auth_headers, db_session, seeded_assignment, student_id
    ):
        import uuid
        from app.models.student import Student
        from app.models.lecture import Lecture
        from app.models.assignment import Assignment

        other_student = Student(id=uuid.uuid4(), github_username="otheruser")
        db_session.add(other_student)
        await db_session.flush()

        other_lecture = Lecture(number=2, title="Other", block=1, assignment_type="B", is_published=True)
        db_session.add(other_lecture)
        await db_session.flush()

        other_assignment = Assignment(
            lecture_id=other_lecture.id,
            student_id=other_student.id,
            status="open",
        )
        db_session.add(other_assignment)
        await db_session.commit()

        response = await client.get("/api/assignments", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(seeded_assignment.id)

    @pytest.mark.asyncio
    async def test_get_assignment_not_found(self, client, auth_headers):
        import uuid
        response = await client.get(f"/api/assignments/{uuid.uuid4()}", headers=auth_headers)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_assignment(self, client, auth_headers, seeded_assignment):
        response = await client.get(f"/api/assignments/{seeded_assignment.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(seeded_assignment.id)
        assert data["status"] == "open"

    @pytest.mark.asyncio
    async def test_trigger_review(self, client, auth_headers, seeded_assignment, mock_celery):
        response = await client.post(
            f"/api/assignments/{seeded_assignment.id}/review",
            headers=auth_headers,
        )
        assert response.status_code == 200
        mock_celery.assert_called_once()
