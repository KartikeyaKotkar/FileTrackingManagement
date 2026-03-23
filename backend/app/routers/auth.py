import os

from fastapi import APIRouter, Header, HTTPException

from app.database import create_user, fetch_all, get_user_by_login
from app.errors import raise_for_write_error
from app.models.schemas import LoginRequest, UserCreate
from app.sql_loader import sql

router = APIRouter(prefix="/auth", tags=["Auth"])

# ----------------------------------------
# Master key for protected endpoints.
# Load from environment before starting the app.
# ----------------------------------------
MASTER_KEY = os.environ.get("ADMIN_KEY")


def require_admin(x_admin_key: str = Header(default=None)):
    if not MASTER_KEY:
        raise HTTPException(status_code=500, detail="ADMIN_KEY is not configured")
    if x_admin_key != MASTER_KEY:
        raise HTTPException(status_code=403, detail="Admin access required")


# ----------------------------------------
# POST /auth/login
# Body: { "login": "admin", "password": "<admin-password>" }
# Returns: user object (no password field)
# ----------------------------------------
@router.post("/login")
def login(data: LoginRequest):
    user = get_user_by_login(data.login, data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return user


# ----------------------------------------
# POST /auth/register
# PROTECTED — requires X-Admin-Key header
# Body: UserCreate schema
# Returns: { "user_id": int }
# ----------------------------------------
@router.post("/register")
def register(data: UserCreate, x_admin_key: str = Header(default=None)):
    require_admin(x_admin_key)

    try:
        user_id = create_user(
            username=data.username,
            fullname=data.fullname,
            password=data.password,
            email=data.email,
            phone=data.phone,
            role_id=data.role_id,
            created_by=data.created_by,
        )
        return {"user_id": user_id}

    except Exception as e:
        raise_for_write_error(e, duplicate_detail="Username already exists")


# ----------------------------------------
# GET /auth/users
# PROTECTED — requires X-Admin-Key header
# Returns all non-deleted users
# ----------------------------------------
@router.get("/users")
def list_users(x_admin_key: str = Header(default=None)):
    require_admin(x_admin_key)
    return fetch_all(sql.users.list_users)
