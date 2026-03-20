from fastapi import APIRouter

from app.database import add_version, fetch_all, fetch_one
from app.models.schemas import VersionCreate
from app.sql_loader import sql

router = APIRouter(prefix="/versions", tags=["Versions"])


@router.get("/{document_id}")
def get_versions(document_id: int):
    return fetch_all(sql.versions.get_versions, (document_id,))


@router.get("/{document_id}/current")
def get_current_version(document_id: int):
    return fetch_one(sql.versions.get_current_version, (document_id,))


@router.post("/")
def create_version(data: VersionCreate):

    version_id = add_version(
        data.document_id,
        data.version_no,
        data.file_name,
        data.file_path,
        data.file_hash,
        data.file_size,
        data.created_by,
    )

    return {"version_id": version_id}
