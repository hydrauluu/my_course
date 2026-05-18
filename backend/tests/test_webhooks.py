import pytest


class TestWebhookHandler:
    @pytest.mark.asyncio
    async def test_ignored_no_action(self, client, mock_webhook_verify):
        payload = {"pull_request": {"head": {"ref": "hw01/testuser"}}}
        response = await client.post("/api/webhooks/github", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ignored"

    @pytest.mark.asyncio
    async def test_ignored_invalid_branch(self, client, mock_webhook_verify):
        payload = {
            "action": "opened",
            "pull_request": {"head": {"ref": "invalid-branch"}},
        }
        response = await client.post("/api/webhooks/github", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ignored"
        assert data["reason"] == "invalid branch format"

    @pytest.mark.asyncio
    async def test_ignored_lecture_not_found(self, client, mock_webhook_verify, db_session):
        payload = {
            "action": "opened",
            "pull_request": {
                "head": {"ref": "hw99/testuser"},
                "html_url": "https://github.com/test/repo/pull/1",
                "body": "Test PR",
            },
        }
        response = await client.post("/api/webhooks/github", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ignored"

    @pytest.mark.asyncio
    async def test_ignored_student_not_found(self, client, mock_webhook_verify, db_session):
        from app.models.lecture import Lecture
        lecture = Lecture(number=99, title="Test", block=1, assignment_type="A", is_published=True)
        db_session.add(lecture)
        await db_session.commit()

        payload = {
            "action": "opened",
            "pull_request": {
                "head": {"ref": "hw99/unknown_student"},
                "html_url": "https://github.com/test/repo/pull/1",
                "body": "Test PR",
            },
        }
        response = await client.post("/api/webhooks/github", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ignored"
        assert data["reason"] == "student not found"

    @pytest.mark.asyncio
    async def test_creates_assignment_on_opened(self, client, mock_webhook_verify, mock_celery, db_session):
        from app.models.lecture import Lecture
        from app.models.student import Student
        import uuid

        student_id = uuid.uuid4()
        student = Student(id=student_id, github_username="testuser")
        lecture = Lecture(number=1, title="Test", block=1, assignment_type="A", is_published=True)
        db_session.add_all([student, lecture])
        await db_session.commit()

        payload = {
            "action": "opened",
            "pull_request": {
                "head": {"ref": "hw01/testuser"},
                "html_url": "https://github.com/test/repo/pull/1",
                "body": "My homework",
            },
        }
        response = await client.post("/api/webhooks/github", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        mock_celery.assert_called_once()

    @pytest.mark.asyncio
    async def test_updates_existing_assignment(self, client, mock_webhook_verify, mock_celery, seeded_assignment):
        payload = {
            "action": "synchronize",
            "pull_request": {
                "head": {"ref": "hw01/testuser"},
                "html_url": seeded_assignment.github_pr_url,
                "body": "Updated homework",
                "state": "open",
                "merged": False,
            },
        }
        response = await client.post("/api/webhooks/github", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        mock_celery.assert_called_once()

    @pytest.mark.asyncio
    async def test_marks_merged(self, client, mock_webhook_verify, mock_celery, seeded_assignment):
        payload = {
            "action": "closed",
            "pull_request": {
                "head": {"ref": "hw01/testuser"},
                "html_url": seeded_assignment.github_pr_url,
                "body": "Final version",
                "state": "closed",
                "merged": True,
            },
        }
        response = await client.post("/api/webhooks/github", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
