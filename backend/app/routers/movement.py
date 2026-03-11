from fastapi import APIRouter

from app.database import fetch_all, move_document
from app.models.schemas import MovementCreate
from app.sql_loader import sql

router = APIRouter(prefix="/movement", tags=["Movement"])


@router.get("/{document_id}")
def get_movement_history(document_id: int):

    return fetch_all(sql.movement.get_movement_history, (document_id,))


@router.post("/")
def create_movement(data: MovementCreate):

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
