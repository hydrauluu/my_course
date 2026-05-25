import pytest


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_returns_response(self, client):
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert "redis" in data["checks"]

    @pytest.mark.asyncio
    async def test_health_version(self, client):
        response = await client.get("/api/health")
        data = response.json()
        assert data["version"] == "1.0.0"

    @pytest.mark.asyncio
    async def test_health_returns_json(self, client):
        response = await client.get("/api/health")
        assert response.headers["content-type"].startswith("application/json")
