from pydantic import BaseModel


class GitHubLoginRequest(BaseModel):
    code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    id: int
    github_username: str
    email: str | None = None
    full_name: str | None = None
    role: str = "student"
