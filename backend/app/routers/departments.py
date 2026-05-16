from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from app.database import get_conn, fetch_all, fetch_one
from app.deps import require_admin
from app.models.schemas import DepartmentCreate, DepartmentUpdate

router = APIRouter(prefix="/departments", tags=["Departments"])

def get_current_user_id(x_user_id: int = Header(default=0)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id req")
    return x_user_id

def get_current_user_role(x_user_role: str = Header(default="user")):
    return x_user_role

@router.get("/all")
def get_all_departments(user_id: int = Depends(get_current_user_id)):
    """Return all departments (id + name) for any authenticated user (used in dropdowns)."""
    return fetch_all("SELECT id, name FROM department ORDER BY name")

@router.get("/")
def get_departments(role: str = Depends(get_current_user_role), user_id: int = Depends(get_current_user_id)):
    if role == "admin":
        return fetch_all("SELECT id, name, description, created_by FROM department WHERE created_by = %s", (user_id,))
    return []

@router.post("/")
def create_department(data: DepartmentCreate, _ = Depends(require_admin), user_id: int = Depends(get_current_user_id)):
    with get_conn() as conn:
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO department (name, description, created_by) VALUES (%s, %s, %s) RETURNING id", (data.name, data.description, user_id))
            new_id = cur.fetchone()[0]
            conn.commit()
            return {"id": new_id, "name": data.name, "description": data.description, "created_by": user_id}
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=400, detail=str(e))

@router.put("/{dept_id}")
def update_department(dept_id: int, data: DepartmentUpdate, _ = Depends(require_admin), user_id: int = Depends(get_current_user_id)):
    row = fetch_one("SELECT created_by FROM department WHERE id = %s", (dept_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Department not found")
    if row["created_by"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this department")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE department SET name = %s, description = %s WHERE id = %s", (data.name, data.description, dept_id))
        conn.commit()
        return {"id": dept_id, "name": data.name, "description": data.description, "created_by": user_id}

@router.delete("/{dept_id}")
def delete_department(dept_id: int, _ = Depends(require_admin), user_id: int = Depends(get_current_user_id)):
    row = fetch_one("SELECT created_by FROM department WHERE id = %s", (dept_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Department not found")
    if row["created_by"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this department")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM department WHERE id = %s", (dept_id,))
        conn.commit()
        return {"status": "deleted"}
