from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str


class UserCreate(User):
    name: str
    password: str


class UserInDB(User):
    name: str
    hashed_password: str


class ValidateResponse(BaseModel):
    username: str


class UserResponse(User):
    name: str
