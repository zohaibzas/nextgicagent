"""Auth routes: POST /auth/login, GET /auth/me."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.jwt_utils import create_access_token, decode_token
from auth.models import DashboardUser, verify_password
from db.database import SessionLocal

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> DashboardUser:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(DashboardUser).filter(DashboardUser.email == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(DashboardUser).filter(DashboardUser.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user.last_login = datetime.utcnow()
    db.commit()
    token = create_access_token(
        user.email,
        extra={"role": user.role, "name": user.name, "user_id": user.id},
    )
    return LoginResponse(
        access_token=token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
        },
    )


@router.get("/me")
def me(user: DashboardUser = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }
