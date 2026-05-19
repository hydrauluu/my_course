import httpx
from fastapi import HTTPException

from app.config import settings


async def exchange_code_for_token(code: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        data = resp.json()
        if "error" in data:
            raise HTTPException(status_code=400, detail=data["error_description"])
        return data


async def get_github_user(access_token: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        return resp.json()


async def get_pr_diff(repo_full_name: str, pr_number: int, token: str) -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3.diff",
            },
        )
        resp.raise_for_status()
        return resp.text
