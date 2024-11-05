from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import List
from pydantic import BaseModel
from datetime import timedelta

from app import schemas, models, crud
from app.database import get_db
from app.dependencies import get_current_user
from app.core.jwt import (
    create_access_token,
    create_refresh_token,
    verify_password,
    SECRET_KEY,
    ALGORITHM,
)

router = APIRouter(tags=["users"])


class UserLogin(BaseModel):
    username: str
    password: str


@router.post("/users/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)


@router.post("/users/login")
def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.username)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(user.username)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


@router.post("/users/reset-password", response_model=schemas.User)
def reset_password(email: str, db: Session = Depends(get_db)):
    return crud.reset_user_password(db, email, "")


@router.delete("/users/deactivate/{username}", response_model=schemas.User)
def deactivate_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    return crud.deactivate_user(db, username)


@router.post("/users/token/refresh")
def refresh_token(
    request: Request, current_user: schemas.User = Depends(get_current_user)
):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token_type, refresh_token = auth_header.split()
        if token_type.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise JWTError
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    new_access_token = create_access_token(data={"sub": username})
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.get("/users/me", response_model=schemas.User)
def get_current_user_profile(current_user: schemas.User = Depends(get_current_user)):
    return current_user
