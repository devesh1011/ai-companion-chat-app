from datetime import timedelta
from typing import Annotated

from contextlib import asynccontextmanager
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.core.config import get_settings
from app.models.schemas import Token, UserCreate, ValidateResponse, UserResponse
from app.db.models import User
from app.dependencies import (
    create_access_token,
    get_user,
    get_password_hash,
    authenticate_user,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="auth", version="1.0.0", lifespan=lifespan)

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


load_dotenv()


@app.post("/token", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    # 1. Check if user exists
    user = get_user(db, data.username)

    if user:
        # Changed from 401 to 409
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    # 2. Hash and Create
    hashed = get_password_hash(data.password)
    new_user = User(name=data.name, username=data.username, hashed_password=hashed)

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )


@app.post("/validate", response_model=ValidateResponse)
def validate(
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return {"username": username, "valid": True}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
