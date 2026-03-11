from fastapi import APIRouter

from app.database import fetch_all
from app.sql_loader import sql

router = APIRouter(prefix="/movement", tags=["Movement"])


@router.get("/{document_id}")
def get_movement_history(document_id: int):

    return fetch_all(sql.movement.get_movement_history, (document_id,))
