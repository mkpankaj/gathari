from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import create_access_token, hash_password, verify_password
from app.deps import get_db
from app.models import User
from app.schemas import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.user_id == body.user_id)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User ID already taken")
    user = User(
        user_id=body.user_id,
        user_name=body.user_name,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    return {"message": "Registration successful"}


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.user_id == body.user_id))
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User ID or password invalid")
    return TokenResponse(access_token=create_access_token(user.user_id))
