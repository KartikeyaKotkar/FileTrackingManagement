from fastapi import APIRouter

from app.database import fetch_all, fetch_one
from app.sql_loader import sql

router = APIRouter(prefix="/versions", tags=["Versions"])


@router.get("/{document_id}")
def get_versions(document_id: int):
    return fetch_all(sql.versions.get_versions, (document_id,))


@router.get("/{document_id}/current")
def get_current_version(document_id: int):
    return fetch_one(sql.versions.get_current_version, (document_id,))
