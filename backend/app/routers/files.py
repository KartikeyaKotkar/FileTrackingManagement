from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.database import fetch_all, fetch_one, get_conn
from app.deps import get_current_user_role, get_current_user_dept, get_current_user_id, check_file_access

router = APIRouter(prefix="/files", tags=["Files"])

@router.get("/{id}/history")
def get_file_history(id: int, role: str = Depends(get_current_user_role), dept_id: int = Depends(get_current_user_dept)):
    document = fetch_one("SELECT department_id FROM document_holder WHERE id = %s", (id,))
    if document:
        check_file_access(role, dept_id, document["department_id"])

    return fetch_all("""
        SELECT e.action, e.timestamp, 
               u.username as performed_by, 
               a.username as approved_by,
               d1.name as from_department, 
               d2.name as to_department
        FROM file_event e
        LEFT JOIN app_user u ON e.performed_by = u.id
        LEFT JOIN app_user a ON e.approved_by = a.id
        LEFT JOIN department d1 ON e.from_department = d1.id
        LEFT JOIN department d2 ON e.to_department = d2.id
        WHERE e.file_id = %s
        ORDER BY e.timestamp ASC
    """, (id,))

@router.get("/{id}/transfer-status")
def get_transfer_status(id: int, role: str = Depends(get_current_user_role), dept_id: int = Depends(get_current_user_dept)):
    doc = fetch_one("SELECT department_id FROM document_holder WHERE id = %s", (id,))
    if not doc:
        raise HTTPException(status_code=404, detail="File not found")
        
    check_file_access(role, dept_id, doc["department_id"])    
    req = fetch_one("SELECT * FROM transfer_request WHERE file_id = %s AND status = 'pending' ORDER BY timestamp DESC LIMIT 1", (id,))
    return dict(req) if req else None


from typing import Optional

class TransferRequestCreate(BaseModel):
    to_department_id: int
    to_user_id: Optional[int] = None

@router.post("/{id}/request-transfer")
def request_transfer(id: int, data: TransferRequestCreate, role: str = Depends(get_current_user_role), dept_id: int = Depends(get_current_user_dept), user_id: int = Depends(get_current_user_id)):
    doc = fetch_one("SELECT department_id FROM document_holder WHERE id = %s", (id,))
    if not doc:
        raise HTTPException(status_code=404, detail="File not found")
        
    curr_dept = doc["department_id"]
    if role != "admin" and curr_dept != dept_id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only transfer files currently in your department")
        
    existing = fetch_one("SELECT id FROM transfer_request WHERE file_id = %s AND status = 'pending'", (id,))
    if existing:
        raise HTTPException(status_code=400, detail="A transfer request is already pending for this document.")
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO transfer_request (file_id, from_department_id, to_department_id, requested_by, to_user_id, status) VALUES (%s, %s, %s, %s, %s, %s)",
                (id, curr_dept, data.to_department_id, user_id, data.to_user_id, "pending")
            )
            conn.commit()
        
    from app.database import update_document_status
    update_document_status(id, "Pending Transfer")
    
    return {"status": "Request created successfully"}

@router.get("/department-logs")
def get_department_logs(dept_id: int = Depends(get_current_user_dept)):
    return fetch_all("""
        SELECT e.file_id, e.action, 
               d1.name as from_department, 
               d2.name as to_department, 
               u.username as performed_by, 
               a.username as approved_by,
               dh.title as file_name,
               e.timestamp
        FROM file_event e
        LEFT JOIN department d1 ON e.from_department = d1.id
        LEFT JOIN department d2 ON e.to_department = d2.id
        LEFT JOIN app_user u ON e.performed_by = u.id
        LEFT JOIN app_user a ON e.approved_by = a.id
        LEFT JOIN document_holder dh ON e.file_id = dh.id
        WHERE e.from_department = %s OR e.to_department = %s
        ORDER BY e.timestamp DESC
        LIMIT 50
    """, (dept_id, dept_id))
