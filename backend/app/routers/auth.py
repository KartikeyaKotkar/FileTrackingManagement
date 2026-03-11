from fastapi import APIRouter, Header, HTTPException

from app.database import create_user, fetch_all, get_user_by_login
from app.models.schemas import LoginRequest, UserCreate
from app.sql_loader import sql

router = APIRouter(prefix="/auth", tags=["Auth"])

# ----------------------------------------
# Master key for protected endpoints.
# Change this value before shipping.
# To load from environment instead:
#   import os
#   MASTER_KEY = os.environ.get("ADMIN_KEY", "changeme")
# ----------------------------------------
MASTER_KEY = "filetracker-admin-2025"


def require_admin(x_admin_key: str = Header(default=None)):
    if x_admin_key != MASTER_KEY:
        raise HTTPException(status_code=403, detail="Admin access required")


# ----------------------------------------
# POST /auth/login
# Body: { "login": "admin", "password": "Admin@123" }
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
        error = str(e)

        if "UNIQUE constraint failed: app_user.username" in error:
            raise HTTPException(status_code=409, detail="Username already exists")

        raise HTTPException(status_code=500, detail=f"Could not create user: {error}")


# ----------------------------------------
# GET /auth/users
# PROTECTED — requires X-Admin-Key header
# Returns all active users
# ----------------------------------------
@router.get("/users")
def list_users(x_admin_key: str = Header(default=None)):
    require_admin(x_admin_key)
    return fetch_all(sql.users.list_users)
