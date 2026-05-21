from uuid import UUID
from pydantic import BaseModel


class GitHubLoginRequest(BaseModel):
    code: str
    state: str = ""


class UserInfo(BaseModel):
    id: UUID
    github_username: str
    email: str | None = None
    full_name: str | None = None
    role: str = "student"
