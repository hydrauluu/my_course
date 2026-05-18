import pytest


class TestLectures:
    @pytest.mark.asyncio
    async def test_list_lectures(self, client, db_session):
        from app.models.lecture import Lecture
        db_session.add_all([
            Lecture(number=0, title="Lecture 0", block=1, assignment_type="B", is_published=True),
            Lecture(number=1, title="Lecture 1", block=1, assignment_type="A", is_published=True),
        ])
        await db_session.commit()

        response = await client.get("/api/lectures")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["number"] == 0
        assert data[1]["number"] == 1

    @pytest.mark.asyncio
    async def test_get_lectures_by_block(self, client, db_session):
        from app.models.lecture import Lecture
        db_session.add_all([
            Lecture(number=0, title="Lecture 0", block=1, assignment_type="B", is_published=True),
            Lecture(number=4, title="Lecture 4", block=2, assignment_type="A", is_published=True),
        ])
        await db_session.commit()

        response = await client.get("/api/lectures/blocks")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["block"] == 1
        assert data[1]["block"] == 2

    @pytest.mark.asyncio
    async def test_get_lecture_by_number(self, client, db_session):
        from app.models.lecture import Lecture
        lecture = Lecture(number=5, title="Test Lecture", block=2, assignment_type="A", is_published=True)
        db_session.add(lecture)
        await db_session.commit()

        response = await client.get("/api/lectures/number/5")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Lecture"

    @pytest.mark.asyncio
    async def test_get_lecture_by_number_not_found(self, client):
        response = await client.get("/api/lectures/number/999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_lecture_by_id(self, client, db_session):
        from app.models.lecture import Lecture
        lecture = Lecture(number=3, title="ByID Lecture", block=1, assignment_type="B", is_published=True)
        db_session.add(lecture)
        await db_session.commit()

        response = await client.get(f"/api/lectures/{lecture.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "ByID Lecture"

    @pytest.mark.asyncio
    async def test_create_lecture_requires_teacher(self, client, auth_headers):
        response = await client.post(
            "/api/lectures",
            headers=auth_headers,
            json={"number": 10, "title": "New", "block": 1, "assignment_type": "A"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_lecture_as_teacher(self, client, teacher_headers):
        response = await client.post(
            "/api/lectures",
            headers=teacher_headers,
            json={"number": 10, "title": "New Lecture", "block": 4, "assignment_type": "A"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Lecture"
        assert data["number"] == 10

    @pytest.mark.asyncio
    async def test_update_lecture_requires_teacher(self, client, auth_headers, db_session):
        from app.models.lecture import Lecture
        lecture = Lecture(number=7, title="Old Title", block=3, assignment_type="A", is_published=True)
        db_session.add(lecture)
        await db_session.commit()

        response = await client.patch(
            f"/api/lectures/{lecture.id}",
            headers=auth_headers,
            json={"title": "New Title"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_lecture_as_teacher(self, client, teacher_headers, db_session):
        from app.models.lecture import Lecture
        lecture = Lecture(number=8, title="Old Title", block=3, assignment_type="B", is_published=True)
        db_session.add(lecture)
        await db_session.commit()

        response = await client.patch(
            f"/api/lectures/{lecture.id}",
            headers=teacher_headers,
            json={"title": "Updated Title"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
