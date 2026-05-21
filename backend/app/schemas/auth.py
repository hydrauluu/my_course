from uuid import UUID
from pydantic import BaseModel, Field


class GitHubLoginRequest(BaseModel):
    code: str = Field(max_length=100)
    state: str = Field(default="", max_length=200)


class UserInfo(BaseModel):
    id: UUID
    github_username: str = Field(max_length=100)
    email: str | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    role: str = Field(default="student", max_length=20)
