import os
from fastapi import APIRouter, Header, HTTPException, Depends

from app.database import create_user as db_create_user, fetch_all, get_user_by_login, get_conn, fetch_one
from app.errors import raise_for_write_error
from app.models.schemas import LoginRequest, UserCreate, UserUpdate
from app.sql_loader import sql
from pydantic import BaseModel
from app.deps import require_admin, get_current_user_id

router = APIRouter(prefix="/auth", tags=["Auth"])

# Table schema should be handled by migration scripts, not inline here.

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
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM role WHERE LOWER(role_name) = %s", (data.role.lower(),))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=400, detail=f"Role '{data.role}' not found")
            role_id = row[0]
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
def list_users():
    return fetch_all("""
        SELECT u.id, u.username, u.fullname, u.email, u.role_id, 
               u.department_id, d.name as department_name,
               u.is_active, u.is_deleted, r.role_name
        FROM app_user u 
        LEFT JOIN department d ON u.department_id = d.id
        LEFT JOIN role r ON u.role_id = r.id
        WHERE u.is_deleted = 0
        ORDER BY u.created_at DESC
    """)

class AssignDepartmentReq(BaseModel):
    department_id: int

# ----------------------------------------
# PUT /auth/users/{user_id}/assign-department
# PROTECTED — requires Admin
# ----------------------------------------
@router.put("/users/{user_id}/assign-department")
def assign_user_department(user_id: int, req: AssignDepartmentReq, _ = Depends(require_admin), admin_id: int = Depends(get_current_user_id)):
    with get_conn() as conn:
        cur = conn.cursor()
        
        dept = fetch_one("SELECT created_by FROM department WHERE id = %s", (req.department_id,))
        if not dept:
            raise HTTPException(status_code=404, detail="Department not found")
        if dept["created_by"] != admin_id:
            raise HTTPException(status_code=403, detail="Not authorized to assign to this department")
            
        user = fetch_one("SELECT id FROM app_user WHERE id = %s", (user_id,))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        cur.execute("UPDATE app_user SET department_id = %s WHERE id = %s", (req.department_id, user_id))
        conn.commit()
        return {"status": "success", "user_id": user_id, "department_id": req.department_id}

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
                SET fullname = COALESCE(%s, fullname),
                    email = COALESCE(%s, email),
                    role_id = COALESCE(%s, role_id),
                    is_active = COALESCE(%s, is_active)
                WHERE id = %s AND is_deleted = 0
            """, (data.fullname, data.email, role_id, data.is_active, user_id))
            conn.commit()
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
            return {"status": "updated"}
        except HTTPException:
            raise
        except Exception as e:
            conn.rollback()
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
        cur.execute("UPDATE app_user SET is_deleted = 1, is_active = 0 WHERE id = %s", (user_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"status": "deleted"}
