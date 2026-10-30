from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class ProblemCreate(BaseModel):
    title: str
    description: str
    location: str
    image_url: str | None = None
    latitude: float | None = None
    longitude: float | None = None



class ProblemResponse(BaseModel):
    id: int
    title: str
    description: str
    location: str
    category: str | None = None
    image_url: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    status: str
    user_id: int


    class Config:
        from_attributes = True