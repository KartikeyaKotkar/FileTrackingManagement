from fastapi import APIRouter, Depends, HTTPException

from app.database import fetch_all, fetch_one, move_document
from app.errors import raise_for_write_error
from app.models.schemas import MovementCreate
from app.sql_loader import sql
from app.deps import get_current_user_role, get_current_user_dept, check_file_access

router = APIRouter(prefix="/movement", tags=["Movement"])


@router.get("/{document_id}")
def get_movement_history(document_id: int, role: str = Depends(get_current_user_role), dept_id: int = Depends(get_current_user_dept)):
    document = fetch_one("SELECT department_id FROM document_holder WHERE id = %s", (document_id,))
    if document:
        check_file_access(role, dept_id, document["department_id"])

    return fetch_all(sql.movement.get_movement_history, (document_id,))


@router.post("/")
def create_movement(data: MovementCreate, role: str = Depends(get_current_user_role), dept_id: int = Depends(get_current_user_dept)):
    document = fetch_one("SELECT department_id FROM document_holder WHERE id = %s", (data.document_id,))
    if document:
        check_file_access(role, dept_id, document["department_id"])

    if role != "admin" and data.from_dept != dept_id:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot transfer documents out of other departments")

    try:
        move_document(
            data.document_id,
            data.from_dept,
            data.to_dept,
            data.movement_type,
            data.approved_by,
            data.moved_by,
            data.remarks,
        )
        return {"status": "movement recorded"}
    except Exception as e:
        raise_for_write_error(e, duplicate_detail="Movement already exists")
