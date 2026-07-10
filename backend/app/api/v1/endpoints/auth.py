from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.security import create_access_token
from app.core.settings import settings
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import authenticate_user, create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)) -> User:
    try:
        return create_user(db, user_in)
    except ValueError as exc:
        if str(exc) == "email":
            detail = "User with this email already exists"
        elif str(exc) == "phone":
            detail = "User with this phone already exists"
        else:
            raise
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        ) from exc


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Authenticate a user and return a JWT",
)
def login_access_token(user_in: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = authenticate_user(db, user_in.email, user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=str(user.id), expires_delta=access_token_expires)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse, summary="Get the current authenticated user")
def read_current_user(current_user: User = Depends(get_current_active_user)) -> User:
    return current_user
