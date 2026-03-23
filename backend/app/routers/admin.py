from fastapi import APIRouter, Depends
from app.database import fetch_all
from app.deps import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/logs")
def get_admin_logs(_=Depends(require_admin)):
    return fetch_all("""
        SELECT e.file_id, e.action, 
               d1.name as from_department, 
               d2.name as to_department, 
               u.username as performed_by, 
               e.timestamp
        FROM file_event e
        LEFT JOIN department d1 ON e.from_department = d1.id
        LEFT JOIN department d2 ON e.to_department = d2.id
        LEFT JOIN app_user u ON e.performed_by = u.id
        ORDER BY e.timestamp DESC
        LIMIT 50
    """)

@router.get("/dashboard")
def get_admin_dashboard(_=Depends(require_admin)):
    actions = fetch_all("SELECT action, COUNT(*) as count FROM file_event GROUP BY action")
    depts = fetch_all("""
        SELECT d.name as department, COUNT(*) as count 
        FROM file_event e
        JOIN department d ON e.to_department = d.id
        WHERE e.to_department IS NOT NULL
        GROUP BY e.to_department
    """)
    return {
        "movement_counts_by_action": actions,
        "movement_counts_by_department": depts
    }
