from fastapi import APIRouter, HTTPException

from app.database import create_user, fetch_all, get_user_by_login
from app.models.schemas import LoginRequest, UserCreate
from app.sql_loader import sql

router = APIRouter(prefix="/auth", tags=["Auth"])


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
# Body: UserCreate schema
# Returns: { "user_id": int }
# ----------------------------------------
@router.post("/register")
def register(data: UserCreate):
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

        # Catch duplicate username (SQLite UNIQUE constraint)
        if "UNIQUE constraint failed: app_user.username" in error:
            raise HTTPException(status_code=409, detail="Username already exists")

        raise HTTPException(status_code=500, detail=f"Could not create user: {error}")


# ----------------------------------------
# GET /auth/users
# Returns all active users (admin use)
# ----------------------------------------
@router.get("/users")
def list_users():
    return fetch_all(sql.users.list_users)
