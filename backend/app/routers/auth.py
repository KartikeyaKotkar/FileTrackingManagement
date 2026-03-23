import os
from fastapi import APIRouter, Header, HTTPException, Depends

from app.database import create_user as db_create_user, fetch_all, get_user_by_login, get_conn, fetch_one
from app.errors import raise_for_write_error
from app.models.schemas import LoginRequest, UserCreate, UserUpdate
from app.sql_loader import sql
from app.deps import require_admin

router = APIRouter(prefix="/auth", tags=["Auth"])

# ----------------------------------------
# POST /auth/login
# ----------------------------------------
@router.post("/login")
def login(data: LoginRequest):
    user = get_user_by_login(data.login, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


# ----------------------------------------
# POST /auth/users
# PROTECTED — requires Admin
# ----------------------------------------
@router.post("/users")
def create_user(data: UserCreate, _ = Depends(require_admin)):
    role_id = 1 if data.role == "admin" else 3
    try:
        user_id = db_create_user(
            username=data.username,
            fullname=data.fullname,
            password=data.password,
            email=data.email,
            phone=data.phone,
            role_id=role_id,
            created_by=data.created_by,
        )
        return {"user_id": user_id}
    except Exception as e:
        raise_for_write_error(e, duplicate_detail="Username already exists")


# ----------------------------------------
# GET /auth/users
# PROTECTED — requires Admin
# ----------------------------------------
@router.get("/users")
def list_users(_ = Depends(require_admin)):
    return fetch_all(sql.users.list_users)


# ----------------------------------------
# PUT /auth/users/{user_id}
# PROTECTED — requires Admin
# ----------------------------------------
@router.put("/users/{user_id}")
def update_user(user_id: int, data: UserUpdate, _ = Depends(require_admin)):
    role_id = None
    if data.role:
        role_id = 1 if data.role == "admin" else 3
        
    with get_conn() as conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE app_user 
                SET fullname = COALESCE(?, fullname),
                    email = COALESCE(?, email),
                    role_id = COALESCE(?, role_id),
                    is_active = COALESCE(?, is_active)
                WHERE id = ?
            """, (data.fullname, data.email, role_id, data.is_active, user_id))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
            return {"status": "updated"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


# ----------------------------------------
# DELETE /auth/users/{user_id}
# PROTECTED — requires Admin
# ----------------------------------------
@router.delete("/users/{user_id}")
def delete_user(user_id: int, _ = Depends(require_admin)):
    with get_conn() as conn:
        cur = conn.cursor()
        # Soft delete logic
        cur.execute("UPDATE app_user SET is_deleted = 1, is_active = 0 WHERE id = ?", (user_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"status": "deleted"}
