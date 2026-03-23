from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from app.database import get_conn, fetch_all, fetch_one
from app.deps import require_admin
from app.models.schemas import DepartmentCreate, DepartmentUpdate

router = APIRouter(prefix="/departments", tags=["Departments"])

try:
    with get_conn() as conn:
        conn.execute("ALTER TABLE department ADD COLUMN description TEXT")
        conn.execute("ALTER TABLE department ADD COLUMN created_by INTEGER")
except Exception:
    pass

def get_current_user_id(x_user_id: int = Header(default=0)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id req")
    return x_user_id

def get_current_user_role(x_user_role: str = Header(default="user")):
    return x_user_role

@router.get("/")
def get_departments(role: str = Depends(get_current_user_role), user_id: int = Depends(get_current_user_id)):
    if role == "admin":
        return fetch_all("SELECT id, name, description, created_by FROM department WHERE created_by = ?", (user_id,))
    return []

@router.post("/")
def create_department(data: DepartmentCreate, _ = Depends(require_admin), user_id: int = Depends(get_current_user_id)):
    with get_conn() as conn:
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO department (name, description, created_by) VALUES (?, ?, ?)", (data.name, data.description, user_id))
            return {"id": cur.lastrowid, "name": data.name, "description": data.description, "created_by": user_id}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

@router.put("/{dept_id}")
def update_department(dept_id: int, data: DepartmentUpdate, _ = Depends(require_admin)):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE department SET name = ? WHERE id = ?", (data.name, dept_id))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Department not found")
        return {"status": "updated"}

@router.delete("/{dept_id}")
def delete_department(dept_id: int, _ = Depends(require_admin)):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM department WHERE id = ?", (dept_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Department not found")
        return {"status": "deleted"}
