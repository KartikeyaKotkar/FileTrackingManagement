from fastapi import APIRouter
from app.database import fetch_all

router = APIRouter(prefix="/files", tags=["Files"])

@router.get("/{id}/history")
def get_file_history(id: int):
    return fetch_all("""
        SELECT e.action, e.timestamp, 
               u.username as performed_by, 
               d1.name as from_department, 
               d2.name as to_department
        FROM file_event e
        LEFT JOIN app_user u ON e.performed_by = u.id
        LEFT JOIN department d1 ON e.from_department = d1.id
        LEFT JOIN department d2 ON e.to_department = d2.id
        WHERE e.file_id = ?
        ORDER BY e.timestamp ASC
    """, (id,))
